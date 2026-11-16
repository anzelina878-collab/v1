"""Written headings are not narrated. Cue short titles at actual chapter-opening phrases."""
from pathlib import Path
import json,re,subprocess,unicodedata
import numpy as np
from align_audio import tokens
BASE=Path(__file__).resolve().parent
TITLES={1:'वायु सेना',2:'टैंक',3:'मिसाइलें',4:'पैदल सेना',5:'तोपखाना',6:'ड्रोन',7:'वायु रक्षा',8:'हेलीकॉप्टर',9:'नौसेना',10:'निष्कर्ष',11:'आपकी राय'}
def main():
 from faster_whisper import WhisperModel
 from faster_whisper.tokenizer import Tokenizer
 from faster_whisper.audio import pad_or_trim
 rows=[r for r in json.load(open(BASE/'alignment/rows.hi.json')) if r['kind']=='narration'];model=WhisperModel('/workspace/work/usa-china/hf-cache/hub/models--Systran--faster-whisper-small/snapshots/536b0662742c02347bc0e980a01041f333bce120',device='cpu',compute_type='int8',cpu_threads=2);tok=Tokenizer(model.hf_tokenizer,True,task='transcribe',language='hi');audio=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(BASE/'audio/voiceover.mp3'),'-ac','1','-ar','16000','-f','f32le','-']),np.float32);audits=[]
 for chapter,title in TITLES.items():
  i=next(i for i,r in enumerate(rows) if r['chapter']==chapter);subset=rows[i-1:i+2];start=max(0,subset[0]['start']-.5);end=min(len(audio)/16000,subset[-1]['end']+.5)
  if end-start>29.5:end=start+29.5
  text=' '.join(r['text'] for r in subset);encoded=tok.encode(' '+re.sub(r'\s+',' ',re.sub(r'[।,;:!?\.]',' ',text)).strip());assert len(encoded)<440;feat=model.feature_extractor(audio[round(start*16000):round(end*16000)]);ww=model.find_alignment(tok,[encoded],model.encode(pad_or_trim(feat)),min(3000,feat.shape[-1]))[0];flat=[];tt=[];pp=[]
  for w in ww:
   for x in tokens(w['word']):flat.append(x);tt.append(float(w['start'])+start);pp.append(float(w['probability']))
  expected=[x for r in subset for x in tokens(r['text'])];assert flat==expected;assert np.median(pp)>.4,(chapter,np.median(pp));cursor=0
  for j,r in enumerate(subset):
   n=len(tokens(r['text']));times=tt[cursor:cursor+n]
   if j==0:
    first=ww[0];letters=sum(unicodedata.category(c).startswith('L') for c in first['word']);cap=min(.9,max(.24,letters*.12+.1));new=max(times[0],float(first['end'])+start-cap)
    for k in range(len(tokens(first['word']))):times[k]=new
   r.update(start=times[0],times=times,probabilities=pp[cursor:cursor+n],method='Contextual forced alignment around actual block-opening phrase');cursor+=n
  audits.append({'chapter':chapter,'title':title,'spoken_heading':False,'cue_time':rows[i]['start'],'actual_phrase':rows[i]['text'],'median_probability':float(np.median(pp)),'window':[start,end]});print('CHAPTER_CUE',chapter,round(rows[i]['start'],3),flush=True)
 for i,r in enumerate(rows):
  assert not i or r['start']>=rows[i-1]['start'],('Nonmonotonic',r)
  r['end']=rows[i+1]['start'] if i+1<len(rows) else len(audio)/16000;r['times']=[float(np.clip(x,r['start'],r['end'])) for x in r['times']]
 out=[]
 for r in rows:
  if r['chapter'] and not any(x['kind']=='heading' and x['chapter']==r['chapter'] for x in out):out.append({'kind':'heading','chapter':r['chapter'],'text':TITLES[r['chapter']],'start':r['start'],'end':r['start']+1.8,'spoken':False,'method':'Visual title cued to actual first phrase of the block; written heading not read'})
  out.append(r)
 (BASE/'alignment/rows.hi.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');(BASE/'alignment/chapter-cues.json').write_text(json.dumps(audits,ensure_ascii=False,indent=2)+'\n');p=BASE/'alignment/report.json';report=json.load(open(p));report.update(spoken_section_headings=0,visual_section_titles=11,written_heading_policy='Headings not narrated: use actual spoken chapter-opening phrases, not old timestamp hints',chapter_transition_refinement=audits);p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('CHAPTER_CUES_READY',flush=True)
if __name__=='__main__':main()
