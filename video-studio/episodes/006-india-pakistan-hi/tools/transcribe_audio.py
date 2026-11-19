"""Word times for visual editing; never changes or generates the supplied voice."""
import argparse,json,subprocess
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,default=BASE/'audio/voice.mp3');p.add_argument('--output',type=Path,default=BASE/'alignment/transcript.jsonl');p.add_argument('--model',default='small',help='Model name or an existing local faster-whisper model directory');p.add_argument('--language',default='uk');p.add_argument('--threads',type=int,default=2);p.add_argument('--prompt',default='Військові технології.');a=p.parse_args()
 import numpy as np
 from faster_whisper import WhisperModel
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(a.input),'-ac','1','-ar','16000','-f','f32le','-']);audio=np.frombuffer(raw,dtype=np.float32)
 model=WhisperModel(a.model,device='cpu',compute_type='int8',cpu_threads=a.threads)
 segments,info=model.transcribe(audio,language=a.language,beam_size=3,word_timestamps=True,vad_filter=True,initial_prompt=a.prompt);a.output.parent.mkdir(parents=True,exist_ok=True)
 with a.output.open('w',encoding='utf-8') as out:
  for s in segments:
   out.write(json.dumps(dict(start=s.start,end=s.end,text=s.text,words=[dict(start=w.start,end=w.end,word=w.word,probability=w.probability) for w in s.words or []]),ensure_ascii=False)+'\n');out.flush();print(f'{s.end:.2f}s',flush=True)
if __name__=='__main__':main()
