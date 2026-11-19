"""Phonetic Hindi phrase anchors, reviewed against unchanged word-timed narration."""
from pathlib import Path
import json,re,unicodedata,difflib,argparse
import numpy as np
B=Path(__file__).resolve().parent
COARSE=[(0,0),(111.7,101.98),(267.94,245.26),(399.38,370.4),(515.92,493.24),(631.7,614.54),(736.62,719.2),(837.88,826.1),(951.44,937.32),(1032.7,1023.44),(1146.58,1139.44),(1236.24,1223.04),(1368.7,1355.9),(1410,1391.5)]
FOLD=str.maketrans({'भ':'ब','ख':'क','घ':'ग','छ':'च','झ':'ज','ठ':'ट','ढ':'ड','ध':'द','थ':'त','फ':'प','ष':'स','श':'स','ण':'न'})
def norm(s):
 s=unicodedata.normalize('NFD',s.lower());s=''.join(c for c in s if not unicodedata.category(c).startswith('M'));s=s.translate(FOLD);return ''.join(re.findall('[a-z0-9\u0900-\u097f]',s))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--asr',type=Path,required=True);ap.add_argument('--signatures',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();old={r['i']:r for r in json.load(open(B/'inputs/original-paragraphs.json'))};rows=[json.loads(l) for l in args.asr.read_text().splitlines()];words=sorted([w for r in rows for w in r['words'] if norm(w['word'])],key=lambda w:w['start']);tokens=[norm(w['word']) for w in words];result=[]
 for line in args.signatures.read_text().splitlines():
  i,phrase=line.split('|',1);i=int(i);expected=float(np.interp(old[i]['start'],[p[0] for p in COARSE],[p[1] for p in COARSE]));key=norm(phrase);length=len(phrase.split());candidates=[]
  for j,w in enumerate(words):
   if abs(w['start']-expected)>18:continue
   score=0;bestn=0
   for n in range(max(2,length-2),length+4):
    value=''.join(tokens[j:j+n]);r=difflib.SequenceMatcher(None,key,value,autojunk=False).ratio()
    if r>score:score=r;bestn=n
   objective=score-.004*abs(w['start']-expected)
   candidates.append(dict(start=w['start'],score=score,objective=objective,recognized=''.join(x['word'] for x in words[j:j+bestn])))
  top=sorted(candidates,key=lambda x:x['objective'],reverse=True)[:3];a=top[0] if top else dict(start=expected,score=0,recognized='');result.append(dict(i=i,source_start=old[i]['start'],expected=expected,signature=phrase,**a,alternatives=top,source_text=old[i]['text']))
 result[0].update(start=0,score=1);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 for r in result:
  if r['score']<.68:print('LOW',r['i'],round(r['start'],2),round(r['score'],3),r['signature'],'=>',r['recognized'],flush=True)
 for a,b in zip(result,result[1:]):
  if b['start']<=a['start']:print('ORDER',a['i'],a['start'],b['i'],b['start'],flush=True)
 print('ANCHOR_CANDIDATES',len(result),flush=True)
if __name__=='__main__':main()
