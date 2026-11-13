"""Word anchors for immutable scripts and a reviewed bilingual paragraph correspondence.
No machine translation, speech replacement, or timestamp-hint timing.
"""
from pathlib import Path
import json,re,unicodedata,difflib,subprocess
import numpy as np
BASE=Path(__file__).resolve().parent

def tokens(s,lang):
 s=unicodedata.normalize('NFKD',s).lower().replace('\u093c','').replace('\u200d','').replace('\u200c','')
 if lang=='hi':
  s=s.replace('ँ','').replace('ं','');s=re.sub(r'[^a-z0-9\u0900-\u0963\u0966-\u097f]+',' ',s)
  for a,b in [('आमेरिका','अमेरिका'),('उपकरन','उपकरण'),('दुन्या','दुनिया'),('सैन्ने','सैन्य'),('चाहिये','चाहिए')]:s=s.replace(a,b)
  return s.split()
 return re.findall(r'[a-zа-яіїєґ0-9]+',unicodedata.normalize('NFC',s))

def align(chapters,transcript,lang,duration):
 rows=[r for c in chapters for r in c['rows']];text=[];starts={};spoken=[];times=[]
 for r in rows:starts[r['index']]=len(text);text+=tokens(r['text'],lang)
 for line in Path(transcript).read_text().splitlines():
  seg=json.loads(line)
  for word in seg.get('words',[]):
   for t in tokens(word['word'],lang):spoken.append(t);times.append(word['start'])
 anchors={}
 for a,b,n in difflib.SequenceMatcher(None,text,spoken,autojunk=False).get_matching_blocks():
  for j in range(n):anchors[a+j]=times[b+j]
 assert len(anchors)>len(text)*.4,(lang,len(anchors)/len(text))
 keys=sorted(anchors);t=np.interp(np.arange(len(text)),keys,[anchors[k] for k in keys]);t=np.maximum.accumulate(t);t[0]=0
 out=[]
 for j,r in enumerate(rows):
  a=starts[r['index']];end=starts[rows[j+1]['index']] if j+1<len(rows) else len(text);out.append({**r,'start':float(t[a]),'end':float(t[end]) if end<len(t) else duration,'tokens':text[a:end],'times':[float(x) for x in t[a:end]],'matched':sum(k in anchors for k in range(a,end)),'total_tokens':end-a})
 return out,{'language':lang,'exact_normalized_token_agreement':len(anchors)/len(text),'script_tokens':len(text),'asr_tokens':len(spoken),'method':'Normalized script/ASR token anchors with monotonic interpolation; bilingual paragraphs reviewed separately; original timing hints ignored'}
def main():
 old=BASE.parent/'001-usa-china-2026';hi=json.load(open(BASE/'input/chapters.hi.json'));uk=json.load(open(BASE/'input/chapters.uk.reference.json'));duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(BASE/'audio/voiceover.mp3')]))
 reports=[]
 for lang,chapters,asr,d in [('uk',uk,BASE/'inputs/original-transcript.uk.jsonl',1063.1),('hi',hi,BASE/'alignment/transcript.jsonl',duration)]:
  out,r=align(chapters,asr,lang,d)
  if lang=='hi' and (BASE/'alignment/refinements.json').exists():
   refinements=json.load(open(BASE/'alignment/refinements.json'));by_index={x['index']:x for x in out}
   for window in refinements:
    for row in window['rows']:
     target=by_index[row['index']];assert len(row['times'])==target['total_tokens'];target.update(start=row['start'],end=row['end'],times=row['times'],timing_refinement='Teacher-forced supplied-text cross-attention alignment inside reviewed audio window',forced_token_probabilities=row['forced_token_probabilities'])
   # Window ends are independently recognized starts of the next clause.
   forced_indices={row['index'] for window in refinements for row in window['rows']}
   for window in refinements:
    last=window['rows'][-1]['index'];following=next((row for row in out if row['index']>last),None)
    if following and following['index'] not in forced_indices:following['start']=window['window']['end']
   for i,row in enumerate(out):
    row['end']=out[i+1]['start'] if i+1<len(out) else d;assert row['end']>=row['start'],row
    row['times']=[float(np.clip(t,row['start'],row['end'])) for t in row['times']]
   r['timing_refinement_windows']=len(refinements);r['timing_refinement_rows']=sum(len(x['rows']) for x in refinements);r['timing_refinement_probability_medians']=[x['median_token_probability'] for x in refinements];r['agreement_scope']='Exact token agreement is from independent ASR before teacher-forced refinement; supplied forced words do not inflate this metric.'
  (BASE/'alignment'/f'paragraphs.{lang}.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));reports.append(r);print('ALIGNED',lang,r['exact_normalized_token_agreement'],flush=True)
 (BASE/'alignment/report.json').write_text(json.dumps({'reports':reports,'audio_duration':duration,'original_files_unchanged':True},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
