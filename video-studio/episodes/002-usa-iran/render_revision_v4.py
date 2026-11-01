"""Episode 001 chapter/question styling over the approved calm-motion edit."""
import sys,json,hashlib,subprocess,argparse
from pathlib import Path
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE))
from render_revision_v3 import Renderer as PreviousRenderer
CARD_KINDS={'section','question','outro'}

class Renderer(PreviousRenderer):
 def __init__(self,work,reuse_dirs=()):
  super().__init__(work);self.base_scenes={s['id']:s for s in self.project['scenes']};self.project=json.loads((BASE/'episode.v4.json').read_text());self.painter.p['scenes']=self.project['scenes'];self.reuse_dirs=[Path(x) for x in reuse_dirs]
 def signature(self,s):
  if s['kind'] in CARD_KINDS:key=json.dumps([s,self.painter.c],sort_keys=True)
  elif s.get('_base_id'):key=json.dumps(s,sort_keys=True)+PreviousRenderer.signature(self,self.base_scenes[s['_base_id']])
  else:return PreviousRenderer.signature(self,s)
  return hashlib.sha256((key+Path(__file__).read_text()).encode()).hexdigest()
 def source_clip(self,base):
  expected=PreviousRenderer.signature(self,base)
  for directory in self.reuse_dirs:
   f=directory/base['id']/'scene.mp4';stamp=f.parent/'fingerprint.txt'
   if f.exists() and stamp.exists() and stamp.read_text()==expected:return f
  return PreviousRenderer.scene(self,base)
 def card(self,s,t):
  t=min(t,s.get('settle_after',1.2));kind=s['kind'];q={'type':'diagram' if kind=='question' else kind,'eyebrow':'','title':s['title'],'subtitle':s.get('subtitle',''),'animate_title':True}
  if kind=='question':q['nodes']=[{'title':'','detail':''} for text in s['nodes']]
  im=self.painter.render(q,t,0,s['start']+t)
  if kind=='question':
   # Parallel audience choices do not imply a causal chain.
   from PIL import ImageDraw
   for j,text in enumerate(s['nodes']):
    if t>=j*.45:self.painter.text(im,text,(125+j*1740/len(s['nodes']),545,1740/len(s['nodes'])-95,160),40,bold=True)
   for j in range(len(s['nodes'])-1):
    ax=100+(j+1)*1740/len(s['nodes'])-35;ImageDraw.Draw(im).rectangle((ax-52,606,ax+14,632),fill=self.painter.c['background'])
  return im
 def still(self,s,t=2):
  if s['kind'] in CARD_KINDS:return self.card(s,t)
  base=self.base_scenes[s.get('_base_id',s['id'])];offset=s.get('_base_offset_frames',0)/30
  if self.reuse_dirs:
   import io
   f=self.source_clip(base);buf=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(offset+min(t,max(.01,s['duration']-.1))),'-i',str(f),'-frames:v','1','-f','image2pipe','-vcodec','mjpeg','-']);from PIL import Image;return Image.open(io.BytesIO(buf)).convert('RGB')
  if base['kind']=='turntable':
   a=self.assets[base['asset_id']];return PreviousRenderer.still(self,dict(base,source_in=0),min(a['duration']-.1,(offset+t)*a['duration']/24))
  return PreviousRenderer.still(self,base,offset+t)
 def scene(self,s):
  if s['kind'] not in CARD_KINDS and not s.get('_base_id'):return PreviousRenderer.scene(self,s)
  if s.get('_base_id'):
   base=self.base_scenes[s['_base_id']];source=self.source_clip(base);count=round(s['end']*30)-round(s['start']*30)
   if s.get('_base_offset_frames',0)==0 and count==round(base['end']*30)-round(base['start']*30):return source
  directory=self.work/s['id'];directory.mkdir(exist_ok=True);out=directory/'scene.mp4';stamp=directory/'fingerprint.txt';key=self.signature(s)
  if out.exists() and stamp.exists() and stamp.read_text()==key:return out
  count=round(s['end']*30)-round(s['start']*30);duration=count/30;cmd=['ffmpeg','-y','-v','error','-threads','1']
  if s['kind'] in CARD_KINDS:
   entrance=min(count,round(s.get('settle_after',1.2)*30)+1)
   for frame in range(entrance):self.card(s,frame/30).save(directory/f'entry-{frame:03d}.png')
   cmd+=['-framerate','30','-i',str(directory/'entry-%03d.png'),'-vf',f'tpad=stop_mode=clone:stop_duration={duration},setsar=1']
  else:cmd+=['-ss',str(s.get('_base_offset_frames',0)/30),'-i',str(source),'-vf','setsar=1']
  cmd+=['-an','-frames:v',str(count),'-r','30','-c:v','libx264','-preset','veryfast','-crf','22','-threads','2','-pix_fmt','yuv420p','-video_track_timescale','15360','-movflags','+faststart',str(out)]
  with (directory/'ffmpeg.log').open('w') as log:subprocess.run(cmd,stderr=log,check=True)
  actual=int(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames','-of','csv=p=0',str(out)]));assert actual==count,(s['id'],actual,count);stamp.write_text(key);return out

def main():
 p=argparse.ArgumentParser();p.add_argument('--work',type=Path,default=BASE/'work-v4');p.add_argument('--reuse',action='append',type=Path,default=[]);p.add_argument('--output',type=Path,default=BASE/'output/final_video_v4.mp4');p.add_argument('--preview',action='store_true');a=p.parse_args();r=Renderer(a.work,a.reuse)
 if a.preview:r.preview()
 else:r.render(a.output)
if __name__=='__main__':main()
