"""Align each category between its neighboring full phrases, not a window edge.
Summary's written heading is not spoken: cue its card from the recorded summary opening.
"""
from pathlib import Path
import json,re,sys,subprocess,unicodedata
import numpy as np
from align_audio import tokens
BASE=Path(__file__).resolve().parent

def main():
 from faster_whisper import WhisperModel
 from faster_whisper.tokenizer import Tokenizer
 from faster_whisper.audio import pad_or_trim
 rows=json.load(open(BASE/'alignment/rows.hi.json'));model=WhisperModel('/workspace/work/usa-china/hf-cache/hub/models--Systran--faster-whisper-small/snapshots/536b0662742c02347bc0e980a01041f333bce120',device='cpu',compute_type='int8',cpu_threads=2);tok=Tokenizer(model.hf_tokenizer,True,task='transcribe',language='hi');audio=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(BASE/'audio/voiceover.mp3'),'-ac','1','-ar','16000','-f','f32le','-']),np.float32);audits=[]
 for i,h in enumerate(rows):
  if h['kind']!='heading':continue
  spoken=h['chapter']!=10;subset=[rows[i-1]]+([h] if spoken else [])+[rows[i+1]];start=max(0,subset[0]['start']-.5);end=min(len(audio)/16000,subset[-1]['end']+.5);assert end-start<30,(h,start,end);text=' '.join(r['text'] for r in subset);encoded=tok.encode(' '+re.sub(r'\s+',' ',re.sub(r'[।,;:!?\.]',' ',text)).strip());assert len(encoded)<440;feat=model.feature_extractor(audio[round(start*16000):round(end*16000)]);ww=model.find_alignment(tok,[encoded],model.encode(pad_or_trim(feat)),min(3000,feat.shape[-1]))[0];flat=[];tt=[];pp=[]
  for w in ww:
   for x in tokens(w['word']):flat.append(x);tt.append(float(w['start'])+start);pp.append(float(w['probability']))
  expected=[x for r in subset for x in tokens(r['text'])];assert flat==expected;cursor=0
  for j,r in enumerate(subset):
   n=len(tokens(r['text']));times=tt[cursor:cursor+n]
   if j==0:
    first=ww[0];letters=sum(unicodedata.category(c).startswith('L') for c in first['word']);cap=min(.9,max(.24,letters*.12+.1));new=max(times[0],float(first['end'])+start-cap)
    for k in range(len(tokens(first['word']))):times[k]=new
   r.update(start=times[0],times=times,probabilities=pp[cursor:cursor+n],method='Neighbor-context forced word alignment around actual chapter transition');cursor+=n
  if not spoken:h.update(start=rows[i+1]['start'],times=[],probabilities=[],spoken=False,method='Written summary heading not spoken; card cued by actual तो हमने क्या देखा phrase')
  else:h['spoken']=True
  audits.append({'title':h['text'],'spoken_heading':spoken,'cue_time':h['start'],'median_probability':float(np.median(pp)),'window':[start,end],'heading_word_times':h['times']});print('CHAPTER_CUE',h['text'],round(h['start'],3),'spoken',spoken,flush=True)
 for i,r in enumerate(rows):
  if i and r['start']<rows[i-1]['start']:raise ValueError(('Nonmonotonic refined cue',r))
  r['end']=rows[i+1]['start'] if i+1<len(rows) else len(audio)/16000;r['times']=[float(np.clip(x,r['start'],r['end'])) for x in r['times']]
 (BASE/'alignment/rows.hi.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');(BASE/'alignment/chapter-cues.json').write_text(json.dumps(audits,ensure_ascii=False,indent=2)+'\n');p=BASE/'alignment/report.json';report=json.load(open(p));report.update(spoken_section_headings=9,visual_section_titles=10,summary_heading='Not spoken verbatim; actual summary-opening phrase is the synchronization cue',chapter_transition_refinement=audits);p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('CHAPTER_CUES_READY',flush=True)
if __name__=='__main__':main()
