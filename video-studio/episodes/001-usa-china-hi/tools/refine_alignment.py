"""Teacher-forced word alignment of supplied text inside reviewed audio gaps.
Does not change speech or count forced text as independently recognized ASR.
Optional production preparation tool; completed results ship with the project.
"""
from pathlib import Path
import argparse,json,subprocess,time,sys,re
import numpy as np
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from align_translation import tokens

def main():
 p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--threads',type=int,default=2);a=p.parse_args()
 from faster_whisper import WhisperModel
 from faster_whisper.tokenizer import Tokenizer
 from faster_whisper.audio import pad_or_trim
 rows={r['index']:r for c in json.load(open(BASE/'input/chapters.hi.json')) for r in c['rows']};windows=json.load(open(BASE/'alignment/refinement-windows.json'));raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(BASE/'audio/voiceover.mp3'),'-ac','1','-ar','16000','-f','f32le','-']);audio=np.frombuffer(raw,np.float32);model=WhisperModel(a.model,device='cpu',compute_type='int8',cpu_threads=a.threads);tok=Tokenizer(model.hf_tokenizer,model.model.is_multilingual,task='transcribe',language='hi');results=[]
 for w in windows:
  text=' '.join(rows[i]['text'] for i in w['rows']);encoded=tok.encode(' '+re.sub(r'\s+',' ',re.sub(r'[।,;:!?\.]',' ',text)).strip());assert len(encoded)<=440,(w,len(encoded));features=model.feature_extractor(audio[round(w['start']*16000):round(w['end']*16000)]);assert w['end']-w['start']<30.01
  print('FORCE_WINDOW',w['start'],w['end'],'tokens',len(encoded),flush=True);words=model.find_alignment(tok,[encoded],model.encode(pad_or_trim(features)),min(3000,features.shape[-1]))[0];flat=[];tt=[];prob=[];ww=[]
  for word in words:
   start=float(word['start'])+w['start'];end=float(word['end'])+w['start'];ps=float(word['probability']);ww.append({'word':word['word'],'start':start,'end':end,'probability':ps})
   for x in tokens(word['word'],'hi'):flat.append(x);tt.append(start);prob.append(ps)
  expected=[x for i in w['rows'] for x in tokens(rows[i]['text'],'hi')];assert flat==expected,(w,flat,expected)
  cursor=0;rr=[]
  for i in w['rows']:
   n=len(tokens(rows[i]['text'],'hi'));rr.append({'index':i,'start':tt[cursor],'end':tt[cursor+n] if cursor+n<len(tt) else w['end'],'times':tt[cursor:cursor+n],'forced_token_probabilities':prob[cursor:cursor+n]});cursor+=n
  med=float(np.median(prob));low=float(np.quantile(prob,.1));assert med>.3,(w,med,low);results.append({'window':w,'method':'Whisper cross-attention teacher-forced alignment of exact supplied text; not ASR transcription','median_token_probability':med,'p10_token_probability':low,'rows':rr,'words':ww});print('FORCED_OK',w['start'],med,low,flush=True)
 (BASE/'alignment/refinements.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n');print('REFINEMENTS_READY',len(results),flush=True)
if __name__=='__main__':main()
