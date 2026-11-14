"""Exact supplied speech, independent ASR followed by probability-audited forced alignment.
No speech changes. Actual spoken section headings are retained as timed rows.
"""
from pathlib import Path
import json,re,unicodedata,difflib,hashlib,subprocess,sys,os
import numpy as np
BASE=Path(__file__).resolve().parent

def tokens(text):
 s=unicodedata.normalize('NFKD',text).lower().replace('\u093c','').replace('\u200d','').replace('\u200c','').replace('ँ','').replace('ं','')
 return re.sub(r'[^a-z0-9\u0900-\u0963\u0966-\u097f]+',' ',s).split()
def main():
 from faster_whisper import WhisperModel
 from faster_whisper.tokenizer import Tokenizer
 from faster_whisper.audio import pad_or_trim
 lines=[x.strip() for x in (BASE/'inputs/script.hi.txt').read_text().splitlines() if x.strip()];rows=[];chapter=-1;spoken=0;reference=json.load(open(BASE/'inputs/translation_map.json'));refs=[x for x in reference if x['kind']=='narration'];old=json.load(open(BASE/'inputs/original-paragraphs.json'))
 for i,line in enumerate(lines):
  heading=bool(re.match(r'^\d\d:\d\d',line))
  if heading:chapter+=1;line=re.sub(r'^\d\d:\d\d\s*[—–-]\s*','',line)
  if heading and i==0:continue # Audio begins with Imagine two warships, not the intro heading.
  row={'index':i,'chapter':chapter,'kind':'heading' if heading else 'narration','text':line}
  if not heading:
   assert tokens(refs[spoken]['hi'])==tokens(line),(spoken,line);row.update(original_paragraph=old[spoken]['paragraph'],original_start=old[spoken]['start']);spoken+=1
  rows.append(row)
 assert spoken==242 and sum(r['kind']=='heading' for r in rows)==10
 script=[];offsets=[]
 for r in rows:offsets.append(len(script));script+=tokens(r['text'])
 asr=[];times=[]
 for line in (BASE/'alignment/transcript.jsonl').read_text().splitlines():
  s=json.loads(line)
  for w in s['words']:
   for x in tokens(w['word']):asr.append(x);times.append(w['start'])
 exact=difflib.SequenceMatcher(None,script,asr,autojunk=False).get_matching_blocks();ratio=sum(m.size for m in exact)/len(script);anchors={};glue=set('है की के मे और को का एक से भी यह इसके वह था ने जो हैं'.split())
 for m in exact:
  if m.size<2 or all(x in glue for x in script[m.a:m.a+m.size]):continue
  for j in range(m.size):anchors[m.a+j]=times[m.b+j]
 assert len(anchors)>len(script)*.18,(ratio,len(anchors)/len(script));kk=sorted(anchors);coarse=np.interp(np.arange(len(script)),kk,[anchors[k] for k in kk]);coarse=np.maximum.accumulate(coarse);coarse[0]=0
 duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(BASE/'audio/voiceover.mp3')]))
 for j,r in enumerate(rows):r.update(coarse_start=float(coarse[offsets[j]]),coarse_end=float(coarse[offsets[j+1]]) if j+1<len(rows) else duration)
 model_path='/workspace/work/usa-china/hf-cache/hub/models--Systran--faster-whisper-small/snapshots/536b0662742c02347bc0e980a01041f333bce120';model=WhisperModel(model_path,device='cpu',compute_type='int8',cpu_threads=2);tok=Tokenizer(model.hf_tokenizer,True,task='transcribe',language='hi');audio=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(BASE/'audio/voiceover.mp3'),'-ac','1','-ar','16000','-f','f32le','-']),np.float32);progress=BASE/'alignment/forced-progress.json';cache=json.load(open(progress)) if progress.exists() else {};groups=[];i=0
 while i<len(rows):
  j=i+1
  while j<len(rows):
   text=' '.join(r['text'] for r in rows[i:j+1]);enc=tok.encode(' '+re.sub(r'\s+',' ',re.sub(r'[।,;:!?\.]',' ',text)).strip());span=rows[j]['coarse_end']-rows[i]['coarse_start']
   if len(enc)>395 or span>23:break
   j+=1
  subset=rows[i:j];text=' '.join(r['text'] for r in subset);encoded=tok.encode(' '+re.sub(r'\s+',' ',re.sub(r'[।,;:!?\.]',' ',text)).strip());assert len(encoded)<=440
  start=max(0,subset[0]['coarse_start']-1);end=min(duration,subset[-1]['coarse_end']+1)
  if end-start<max(3,len(tokens(text))/4):end=min(duration,start+min(29.5,max(5,len(tokens(text))/2.7)))
  if end-start>30:start=max(0,end-30)
  fingerprint=hashlib.sha256(json.dumps([start,end,text]).encode()).hexdigest()
  if fingerprint in cache:result=cache[fingerprint]
  else:
   feat=model.feature_extractor(audio[round(start*16000):round(end*16000)]);words=model.find_alignment(tok,[encoded],model.encode(pad_or_trim(feat)),min(3000,feat.shape[-1]))[0];flat=[];tt=[];pp=[];ww=[]
   for w in words:
    ps=float(w['probability']);a=float(w['start'])+start;b=float(w['end'])+start;ww.append({'word':w['word'],'start':a,'end':b,'probability':ps})
    for x in tokens(w['word']):flat.append(x);tt.append(a);pp.append(ps)
   expected=[x for r in subset for x in tokens(r['text'])];assert flat==expected,('token split mismatch',i,flat,expected)
   median=float(np.median(pp));assert median>.38,('Review weak forced alignment window',i,start,end,median)
   result={'start':start,'end':end,'text':text,'times':tt,'probabilities':pp,'words':ww,'median_probability':median,'p10_probability':float(np.quantile(pp,.1))};cache[fingerprint]=result;progress.write_text(json.dumps(cache,ensure_ascii=False));print('ALIGNED_WINDOW',i,j,round(start,2),round(end,2),round(median,3),flush=True)
  # DTW pins the first target token to the padded audio-window boundary.
  # Bound that leading word by its phonetic duration instead of assigning it
  # the preceding chapter/paragraph's speech. Raw forced results stay intact.
  result=dict(result);result['times']=list(result['times']);first=result['words'][0];letters=sum(unicodedata.category(c).startswith('L') for c in first['word']);cap=min(.9,max(.24,letters*.12+.10))
  if i and first['end']-first['start']>cap:
   corrected=max(first['start'],first['end']-cap)
   for t in range(len(tokens(first['word']))):result['times'][t]=corrected
  cursor=0
  for r in subset:
   n=len(tokens(r['text']));r.update(start=result['times'][cursor],times=result['times'][cursor:cursor+n],probabilities=result['probabilities'][cursor:cursor+n],method='Teacher-forced cross-attention word alignment of exact supplied text');cursor+=n
  groups.append({k:result[k] for k in ['start','end','median_probability','p10_probability']});i=j
 rows[0]['start']=0;rows[0]['times'][0]=0
 # Remove only tiny overlap caused by padded neighboring alignment windows.
 for j,r in enumerate(rows):
  if j and r['start']<rows[j-1]['start']:raise ValueError(('Nonmonotonic narration boundary',r))
  r['end']=rows[j+1]['start'] if j+1<len(rows) else duration;r['times']=[float(np.clip(x,r['start'],r['end'])) for x in r['times']]
 (BASE/'alignment/rows.hi.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');(BASE/'alignment/report.json').write_text(json.dumps({'independent_asr_exact_normalized_token_match':ratio,'robust_anchor_token_fraction':len(anchors)/len(script),'forced_alignment_windows':groups,'forced_words_not_counted_as_independent_asr':True,'spoken_paragraphs':242,'spoken_section_headings':10,'audio_duration':duration,'voice_altered':False},indent=2)+'\n');print('ALL_ALIGNMENT_READY',len(rows),duration,flush=True)
if __name__=='__main__':main()
