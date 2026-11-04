"""Align the unchanged supplied Ukrainian script to locally recognized word times."""
import json,re,difflib,math
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parent

def tokens(s):return re.findall(r'[a-zа-яіїєґ0-9]+',s.lower().replace('ё','е'))
def main():
 rows=json.loads((BASE/'inputs/paragraphs.json').read_text());asr=[json.loads(x) for x in (BASE/'alignment/transcript.jsonl').read_text().splitlines()];text=[];spoken=[];ats=[];starts={};counts={}
 for r in rows:
  if r['heading']:continue
  starts[r['i']]=len(text);t=tokens(r['text']);text+=t;counts[r['i']]=len(t)
 for r in asr:
  for w in r['words']:
   for t in tokens(w['word']):spoken.append(t);ats.append(w['start'])
 anchors={}
 for a,b,n in difflib.SequenceMatcher(None,text,spoken,autojunk=False).get_matching_blocks():
  for j in range(n):anchors[a+j]=ats[b+j]
 agreement=len(anchors)/len(text);assert agreement>.70,agreement
 keys=sorted(anchors);times=np.interp(np.arange(len(text)),keys,[anchors[k] for k in keys]);out=[]
 for r in rows:
  if r['heading']:continue
  i=r['i'];out.append({**r,'start':0 if i==1 else float(times[starts[i]]),'matched_words':sum(k in anchors for k in range(starts[i],starts[i]+counts[i])),'total_words':counts[i]})
 (BASE/'alignment/word_anchors.json').write_text(json.dumps([{'i':i,'tokens':text[starts[i]:starts[i]+counts[i]],'times':[float(x) for x in times[starts[i]:starts[i]+counts[i]]]} for i in starts],ensure_ascii=False))
 (BASE/'alignment/paragraphs.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));(BASE/'alignment/report.json').write_text(json.dumps({'exact_token_agreement':agreement,'script_tokens':len(text),'audio_words':len(spoken),'method':'SequenceMatcher word anchors with monotonic interpolation; chapter hints are not timing authority','source_audio_duration':1307.616},indent=2));print('ALIGNED',agreement,len(out))
 for r in out:
  if r['i'] in [12,35,66,89,103,121,138,159,179,195,219]:print(r['i'],r['start'],r['text'])
if __name__=='__main__':main()
