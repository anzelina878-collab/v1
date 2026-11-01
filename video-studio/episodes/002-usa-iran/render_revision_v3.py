"""Calm revision: locked photographs; consistent 24-second revolutions, smooth 30fps."""
import sys,json,hashlib,subprocess,argparse,copy
from pathlib import Path
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE))
from render_revision_v2 import Renderer as PreviousRenderer

class Renderer(PreviousRenderer):
 def __init__(self,work,reuse=None):
  super().__init__(work);self.project=json.loads((BASE/'episode.v3.json').read_text());self.painter.p['scenes']=self.project['scenes'];self.reuse=reuse
 def signature(self,s):
  key=super().signature(s)
  if s['kind'] in ['photo','turntable']:key=hashlib.sha256((key+Path(__file__).read_text()).encode()).hexdigest()
  return key
 def scene(self,s):
  if s['kind'] not in ['photo','turntable']:
   if self.reuse:
    f=self.reuse/s['id']/'scene.mp4';stamp=f.parent/'fingerprint.txt'
    if f.exists() and stamp.exists() and stamp.read_text()==self.signature(s):return f
   return super().scene(s)
  directory=self.work/s['id'];directory.mkdir(exist_ok=True);out=directory/'scene.mp4';stamp=directory/'fingerprint.txt';fingerprint=self.signature(s)
  if out.exists() and stamp.exists() and stamp.read_text()==fingerprint:return out
  frames=round(s['end']*30)-round(s['start']*30);duration=frames/30
  if s['kind']=='photo':
   # Bake the subject and labels once. No moving camera, integer crop or zoompan.
   still=directory/'locked.png';self.still(s,2).save(still)
   cmd=['ffmpeg','-y','-v','error','-loop','1','-framerate','30','-i',str(still),'-vf','setsar=1']
  else:
   a=self.assets[s['asset_id']];rate=24/a['duration'];source_time=min(a['duration'],duration/rate+.2);labels=directory/'labels.png';self.labels(s).save(labels)
   # Real geometry supplies the source views. Motion-compensated intermediate
   # frames retain smooth playback when slowing the existing rendered revolution.
   filt=f'[0:v]setpts={rate}*PTS,tpad=stop_mode=clone:stop_duration=0.25,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,tpad=stop_mode=clone:stop_duration={duration},scale=1920:1080,setsar=1[base];[base][1:v]overlay=0:0,format=yuv420p[v]'
   cmd=['ffmpeg','-y','-v','error','-threads','1','-t',str(source_time),'-i',str(BASE/a['video']),'-loop','1','-framerate','30','-i',str(labels),'-filter_complex',filt,'-filter_complex_threads','1','-map','[v]']
  cmd+=['-an','-frames:v',str(frames),'-r','30','-c:v','libx264','-preset','veryfast','-crf','22','-threads','2','-pix_fmt','yuv420p','-video_track_timescale','15360','-movflags','+faststart',str(out)]
  with (directory/'ffmpeg.log').open('w') as log:subprocess.run(cmd,stderr=log,check=True)
  n=int(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames','-of','csv=p=0',str(out)]));assert n==frames,(s['id'],n,frames)
  stamp.write_text(fingerprint);return out

def main():
 p=argparse.ArgumentParser();p.add_argument('--work',type=Path,default=BASE/'work-v3');p.add_argument('--reuse',type=Path);p.add_argument('--output',type=Path,default=BASE/'output/final_video_v3.mp4');p.add_argument('--preview',action='store_true');p.add_argument('--pilot',type=float);a=p.parse_args();r=Renderer(a.work,a.reuse)
 if a.preview:r.preview()
 else:r.render(a.output,a.pilot)
if __name__=='__main__':main()
