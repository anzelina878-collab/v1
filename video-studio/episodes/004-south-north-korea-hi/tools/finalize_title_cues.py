"""Cue short visual headings at the spoken topic word, not an earlier preface."""
from pathlib import Path
import json,sys
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from align_audio import tokens
TARGETS={1:'वायु',2:'टैंकों',3:'मिसाइल',4:'पैदल',5:'तोपखाना',6:'ड्रोन',7:'वायु',8:'हेलीकॉप्टर',9:'नौसेना'}
TITLES={1:'वायु सेना',2:'टैंक',3:'मिसाइलें',4:'पैदल सेना',5:'तोपखाना',6:'ड्रोन',7:'वायु रक्षा',8:'हेलीकॉप्टर',9:'नौसेना',10:'निष्कर्ष',11:'आपकी राय'}
def main():
 rows=[r for r in json.load(open(BASE/'alignment/rows.hi.json')) if r['kind']=='narration'];audits=json.load(open(BASE/'alignment/chapter-cues.json'));headings=[]
 for c,title in TITLES.items():
  body=[r for r in rows if r['chapter']==c];cue=body[0]['start'];target=TARGETS.get(c)
  if target:
   matches=[t for r in body[:2] for x,t in zip(tokens(r['text']),r['times']) if x==tokens(target)[0]];assert matches,(c,target);cue=matches[0]
  headings.append({'kind':'heading','chapter':c,'text':title,'start':cue,'end':cue+1.8,'spoken':False,'method':'Short visual title cued to actual spoken topic word; summary/CTA to opening phrase'})
  a=next(a for a in audits if a['chapter']==c);a.update(block_opening_time=body[0]['start'],cue_time=cue,cue_word=target,cue_policy='First spoken category word, or opening phrase for summary/CTA');print('FINAL_TITLE_CUE',c,round(cue,3),flush=True)
 out=sorted(rows+headings,key=lambda r:(r['start'],0 if r['kind']=='heading' else 1));(BASE/'alignment/rows.hi.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');(BASE/'alignment/chapter-cues.json').write_text(json.dumps(audits,ensure_ascii=False,indent=2)+'\n');p=BASE/'alignment/report.json';r=json.load(open(p));r['chapter_transition_refinement']=audits;r['title_cue_policy']='Actual category word: do not let a short card finish during a preface before the topic is spoken';p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
