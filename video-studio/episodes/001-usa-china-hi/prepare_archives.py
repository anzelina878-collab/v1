"""Recreate the original approved documentary selections without baked Ukrainian labels.
Exact original source windows; actual speed; source audio removed. Never loops.
"""
from pathlib import Path
import argparse,json,subprocess,hashlib,concurrent.futures,os
BASE=Path(__file__).resolve().parent

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--library',type=Path,required=True);ap.add_argument('--jobs',type=int,default=1);args=ap.parse_args()
 old=json.load(open(BASE/'inputs/original-episode.v4.json'));sources=json.load(open(BASE/'inputs/original-archive_sources.v4.json'))['sources'];opening=json.load(open(BASE/'inputs/original-opening.parts.v4.json'))['scenes'];jobs=[]
 for i,s in enumerate(old['scenes']):
  if s.get('archive_edit'):jobs.append((f'source-{i:03d}',s,s['duration']))
 for i,s in enumerate(opening):jobs.append((f'opening-{i}',s,s['duration']+.65))
 def one(row):
  key,s,duration=row;e=s['archive_edit'];meta=sources[e['source']];raw=args.library/meta['local_file'];out=BASE/'assets/archive'/(key+'.mp4');frames=round(duration*30)
  assert raw.is_file();stamp=out.with_suffix('.source.json');fingerprint=hashlib.sha256(json.dumps([key,e,frames,raw.stat().st_size,'clean720crf18-v1'],sort_keys=True).encode()).hexdigest()
  if out.exists() and stamp.exists() and json.load(open(stamp)).get('fingerprint')==fingerprint:return json.load(open(stamp))
  subprocess.run(['ffmpeg','-y','-v','error','-xerror','-threads','1','-ss',str(e['in']),'-i',str(raw),'-an','-frames:v',str(frames),'-vf','fps=30,scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,setsar=1','-c:v','libx264','-preset','veryfast','-crf','18','-threads','1','-filter_threads','1','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],check=True)
  actual=int(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames','-of','csv=p=0',str(out)]));assert actual==frames,(key,actual,frames)
  record={'id':key,'video':str(out.relative_to(BASE)),'duration':frames/30,'source_key':e['source'],'source_in':e['in'],'country':e['country'],'source':meta,'fingerprint':fingerprint,'changes':'Original approved excerpt re-encoded clean at 720p30; no archive audio, editorial labels or speed changes'};stamp.write_text(json.dumps(record,ensure_ascii=False,indent=2));print('ARCHIVE',key,frames/30,flush=True);return record
 with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as ex:r=list(ex.map(one,jobs))
 (BASE/'assets/archive-manifest.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print('ARCHIVES_READY',len(r),flush=True)
if __name__=='__main__':main()
