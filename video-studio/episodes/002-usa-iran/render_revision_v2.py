"""Object-led revision: broad source/name bar matching episode 001, real 3D and fast hook."""
import sys,json,hashlib,subprocess,argparse
from pathlib import Path
from PIL import Image,ImageDraw
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE))
from render_episode import Renderer as OriginalRenderer
from studio.project import THEME

class Renderer(OriginalRenderer):
 def __init__(self,work):
  super().__init__(work);self.project=json.loads((BASE/'episode.v2.json').read_text());self.assets={x['id']:x for x in json.loads((BASE/'assets/manifest.v2.json').read_text())};self.painter.p['scenes']=self.project['scenes']
 def labels(self,s,archive=False):
  if not archive:
   im=super().labels(s,False)
   # Name and geometry status are kept distinct; no false photographic/3D claim.
   if s.get('note') and s['kind']=='turntable':pass
   return im
  im=Image.new('RGBA',(1920,1080));d=ImageDraw.Draw(im)
  d.rectangle((0,970,1920,1080),fill=(17,24,23,183))
  self.flag_at(im,s.get('country','US'),45,989,72,48)
  self.painter.text(im,s.get('title',''),(133,986,1725,64),46,'#FFFFFF',bold=True,min_size=28)
  self.painter.text(im,self.credit(s['asset_id'],'video'),(700,1051,1160,26),18,'#F8F8F4',align='right')
  return im
 def signature(self,s):
  if s['kind']=='ident':
   a=self.assets[s['asset_id']];f=BASE/a['video'];data=[s,a,str(f),f.stat().st_size,f.stat().st_mtime_ns]
   key=json.dumps(data,sort_keys=True)
  else:key=super().signature(s)
  return hashlib.sha256((key+Path(__file__).read_text()).encode()).hexdigest()
 def still(self,s,t=2):
  if s['kind']=='ident':
   import io
   a=self.assets[s['asset_id']];position=t/s['duration']*a['duration'];b=subprocess.check_output(['ffmpeg','-v','error','-ss',str(position),'-i',str(BASE/a['video']),'-frames:v','1','-vf','scale=1920:1080','-f','image2pipe','-vcodec','mjpeg','-']);return Image.open(io.BytesIO(b)).convert('RGB')
  return super().still(s,t)
 def long_model(self,s):
  directory=self.work/s['id'];directory.mkdir(exist_ok=True);out=directory/'scene.mp4';stamp=directory/'fingerprint.txt';fingerprint=self.signature(s)
  if out.exists() and stamp.exists() and stamp.read_text()==fingerprint:return out
  a=self.assets[s['asset_id']];frames=round(s['end']*30)-round(s['start']*30);duration=frames/30;labels=directory/'labels.png';self.labels(s).save(labels)
  filters=f'[0:v]fps=30,scale=1920:1080,tpad=stop_mode=clone:stop_duration={duration},setsar=1[base];[base][1:v]overlay=0:0,format=yuv420p[v]'
  subprocess.run(['ffmpeg','-y','-v','error','-threads','1','-i',str(BASE/a['video']),'-loop','1','-framerate','30','-i',str(labels),'-filter_complex',filters,'-filter_complex_threads','1','-map','[v]','-an','-frames:v',str(frames),'-r','30','-c:v','libx264','-preset','veryfast','-crf','22','-threads','2','-pix_fmt','yuv420p','-video_track_timescale','15360',str(out)],check=True)
  stamp.write_text(fingerprint);return out
 def scene(self,s):
  if s['kind']=='turntable' and s['duration']>self.assets[s['asset_id']]['duration']*1.1:return self.long_model(s)
  if s['kind']!='ident':return super().scene(s)
  directory=self.work/s['id'];directory.mkdir(exist_ok=True);out=directory/'scene.mp4';stamp=directory/'fingerprint.txt';fingerprint=self.signature(s)
  if out.exists() and stamp.exists() and stamp.read_text()==fingerprint:return out
  a=self.assets[s['asset_id']];frames=round(s['end']*30)-round(s['start']*30);duration=frames/30
  subprocess.run(['ffmpeg','-y','-v','error','-threads','1','-i',str(BASE/a['video']),'-an','-vf',f"setpts={duration/a['duration']}*PTS,fps=30,scale=1920:1080,tpad=stop_mode=clone:stop_duration=0.1,setsar=1",'-frames:v',str(frames),'-c:v','libx264','-preset','veryfast','-crf','22','-threads','2','-pix_fmt','yuv420p','-video_track_timescale','15360',str(out)],check=True);stamp.write_text(fingerprint);return out

def main():
 p=argparse.ArgumentParser();p.add_argument('--work',type=Path,default=BASE/'work-v2');p.add_argument('--output',type=Path,default=BASE/'output/final_video_v2.mp4');p.add_argument('--preview',action='store_true');p.add_argument('--pilot',type=float);a=p.parse_args();r=Renderer(a.work)
 if a.preview:r.preview()
 else:r.render(a.output,a.pilot)
if __name__=='__main__':main()
