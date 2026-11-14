"""Hindi light-studio visual edit. Moving inputs never freeze, slow, or interpolate.
Cards enter once and settle; photos are intentionally locked composition shots.
"""
from pathlib import Path
import sys,json,re,hashlib,subprocess,argparse,io,copy
from PIL import Image,ImageDraw,features
BASE=Path(__file__).resolve().parent;STUDIO=BASE.parents[1];sys.path.insert(0,str(STUDIO))
from studio.visuals import Painter,country_flag
from studio.project import THEME

class HindiPainter(Painter):
 def text(self,im,value,box,size=42,color='ink',bold=False,align='left',min_size=18):
  old=self.c['font'],self.c['font_bold']
  if not re.search('[\u0900-\u097f]',str(value)):self.c['font']=str(STUDIO/'fonts/DejaVuSansCondensed.ttf');self.c['font_bold']=str(STUDIO/'fonts/DejaVuSansCondensed-Bold.ttf')
  try:return super().text(im,value,box,size,color,bold,align,min_size)
  finally:self.c['font'],self.c['font_bold']=old

class Renderer:
 def __init__(self,work):
  assert features.check('raqm');self.project=json.load(open(BASE/'episode.json'));self.assets={a['id']:a for a in json.load(open(BASE/'assets/manifest.json'))};self.work=Path(work);self.work.mkdir(exist_ok=True,parents=True);self.flag=Image.open(BASE/'assets/flag-IR.png').convert('RGBA');theme={**THEME,'background':'#F2F3F0','font':str(BASE/'fonts/ArsenalHindi-Regular.ttf'),'font_bold':str(BASE/'fonts/ArsenalHindi-Bold.ttf')};self.painter=HindiPainter({'theme':theme,'style':'minimal','title_motion':True,'scenes':self.project['scenes'],'_frames':round(self.project['duration']*30),'fps':30});self.duration_cache={}
 def duration(self,path):
  path=str(path)
  if path not in self.duration_cache:self.duration_cache[path]=float(json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','json',path]))['format']['duration'])
  return self.duration_cache[path]
 def flag_at(self,im,country,x,y,w=90,h=60):
  if country=='IR':f=self.flag.resize((w,h),Image.Resampling.LANCZOS);im.paste(f,(x,y),f)
  else:country_flag(im,'US',x,y,w,h)
 def credit(self,key,kind='photo'):
  a=self.assets.get(key,{});return a.get(kind+'_credit',a.get('credit',''))
 def labels(self,s):
  im=Image.new('RGBA',(1920,1080));d=ImageDraw.Draw(im);archive=s['kind']=='archive';a=self.assets[s['asset_id']]
  if archive:
   d.rectangle((0,970,1920,1080),fill=(17,24,23,183));self.flag_at(im,s.get('country','US'),45,986,72,48);self.painter.text(im,s.get('title',''),(133,984,1725,65),44,'#FFFFFF',True,min_size=24);self.painter.text(im,self.credit(s['asset_id'],'video'),(470,1043,1390,31),18,'#FFFFFF',align='right',min_size=10)
  else:
   self.flag_at(im,s.get('country','US'),90,855);self.painter.text(im,s.get('title',''),(90,915,1720,118),76,bold=True,min_size=28);self.painter.text(im,self.credit(s['asset_id'],'photo' if s['kind']=='photo' else 'video'),(430,1040,1400,32),18,'muted',align='right',min_size=10)
   if s.get('note'):self.painter.text(im,s['note'],(220,865,1550,48),24,'muted',min_size=16)
  return im
 def plate(self,s,t):
  t=min(t,s.get('settle_after',1.2));kind=s['kind'];p=self.painter
  if kind in ['graphic','question']:
   q={'type':'diagram','eyebrow':'','title':s['title'],'nodes':[{'title':v,'detail':''} for v in s['nodes']]};im=p.render(q,t,0,s['start']+t)
   for j in range(len(s['nodes'])-1):ax=100+(j+1)*1740/len(s['nodes'])-35;ImageDraw.Draw(im).rectangle((ax-54,604,ax+16,634),fill=p.c['background'])
   if any('1987' in v or '2019' in v or '500' in v for v in s['nodes']):p.text(im,'United States of America Department of State · INF Treaty',(90,1030,1730,32),18,'muted',align='right')
   return im
  if kind=='compare':
   im=Image.new('RGB',(1920,1080),p.c['background']);p.motion_text(im,s['title'],(90,150,1740,160),t,66,bold=True)
   for j,(key,title,country) in enumerate(s['sides']):
    x=90+j*900;ImageDraw.Draw(im).rounded_rectangle((x,355,x+840,955),radius=12,fill='white');p.picture(im,{'_image':str(BASE/self.assets[key]['photo'])},(x+35,390,770,380),t-j*.15)
    if t>.15+j*.15:self.flag_at(im,country,x+35,805,75,50);p.text(im,title,(x+135,797,670,105),38,bold=True);p.text(im,self.credit(key),(x+30,916,780,30),16,'muted',align='right',min_size=10)
   return im
  if kind=='ident':
   return p.render({'type':'section','eyebrow':'','title':'ARSENAL 360','subtitle':'शस्त्र 360'},t,0,s['start']+t)
  im=p.render({'type':kind,'eyebrow':'','title':s.get('title',''),'subtitle':s.get('subtitle','')},t,0,s['start']+t)
  if kind=='outro':p.text(im,'ARSENAL 360  |  शस्त्र 360',(280,975,1360,55),26,'muted',align='center')
  return im
 def still(self,s,t=2):
  if s['kind']=='photo':
   im=self.painter.render({'type':'studio','_image':str(BASE/self.assets[s['asset_id']]['photo']),'_subject_only':True},2,0,s['start']+2);labels=self.labels(s);im.paste(labels,(0,0),labels);return im
  if s['kind'] in ['archive','turntable']:
   a=self.assets[s['asset_id']];path=BASE/a['video'];pos=(s.get('source_in',0)+t)%24 if s['kind']=='turntable' else min(self.duration(path)-.05,s.get('source_in',0)+t);data=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(pos),'-i',str(path),'-frames:v','1','-vf','scale=1920:1080','-threads','1','-f','image2pipe','-vcodec','png','-']);im=Image.open(io.BytesIO(data)).convert('RGB');labels=self.labels(s);im.paste(labels,(0,0),labels);return im
  return self.plate(s,t)
 def signature(self,s):
  keys=[a[0] for a in s['sides']] if s['kind']=='compare' else [s['asset_id']] if s['kind'] in ['photo','archive','turntable'] else [];deps=[Path(__file__),STUDIO/'studio/visuals.py',BASE/'fonts/ArsenalHindi-Regular.ttf',BASE/'fonts/ArsenalHindi-Bold.ttf',BASE/'assets/flag-IR.png']
  for key in keys:
   field='video' if s['kind'] in ['archive','turntable'] else 'photo';deps.append(BASE/self.assets[key][field])
  return hashlib.sha256(json.dumps([s,[self.assets[k] for k in keys],[(str(p),p.stat().st_size,p.stat().st_mtime_ns) for p in deps]],sort_keys=True).encode()).hexdigest()
 def scene(self,s):
  d=self.work/s['id'];d.mkdir(exist_ok=True);out=d/'scene.mp4';stamp=d/'fingerprint.txt';key=self.signature(s)
  if out.exists() and stamp.exists() and stamp.read_text()==key:return out
  frames=round(s['end']*30)-round(s['start']*30);duration=frames/30;cmd=['ffmpeg','-y','-v','error','-threads','1'];pipe=False
  if s['kind'] in ['archive','turntable']:
   a=self.assets[s['asset_id']];path=BASE/a['video'];labels=d/'labels.png';self.labels(s).save(labels)
   if s['kind']=='turntable':cmd+=['-stream_loop','-1']
   else:assert s.get('source_in',0)+duration<=self.duration(path)+.025,(s['id'],'Not enough moving material')
   cmd+=['-ss',str(s.get('source_in',0)),'-i',str(path),'-loop','1','-framerate','30','-i',str(labels),'-filter_complex','[0:v]fps=30,scale=1920:1080,setsar=1[b];[b][1:v]overlay=0:0,format=yuv420p[v]','-filter_complex_threads','1','-map','[v]']
  elif s['kind']=='photo':
   image=d/'locked.png';self.still(s).save(image);cmd+=['-loop','1','-framerate','30','-i',str(image),'-vf','setsar=1']
  else:
   pipe=True;entrance=min(frames,round(s.get('settle_after',1.2)*30)+1);cmd+=['-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','pipe:0','-vf',f'tpad=stop_mode=clone:stop_duration={duration},setsar=1']
  cmd+=['-an','-frames:v',str(frames),'-r','30','-c:v','libx264','-preset','veryfast','-crf','22','-threads','2','-pix_fmt','yuv420p','-video_track_timescale','15360','-movflags','+faststart',str(out)]
  with (d/'ffmpeg.log').open('w') as log:
   if pipe:
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
    for f in range(entrance):proc.stdin.write(self.plate(s,f/30).convert('RGB').tobytes())
    proc.stdin.close();assert proc.wait()==0,(s['id'],(d/'ffmpeg.log').read_text())
   else:subprocess.run(cmd,stderr=log,check=True)
  actual=int(json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames','-of','json',str(out)]))['streams'][0]['nb_frames']);assert actual==frames,(s['id'],actual,frames);stamp.write_text(key);return out
 def preview(self):
  for off in range(0,len(self.project['scenes']),24):
   im=Image.new('RGB',(1280,1212),'#152026');draw=ImageDraw.Draw(im)
   for j,s in enumerate(self.project['scenes'][off:off+24]):im.paste(self.still(s,min(2,s['duration']*.55)).resize((320,180)),(j%4*320,j//4*202));draw.text((j%4*320+3,j//4*202+181),f"{s['id']} {s['start']:.2f}s {s['kind']}",fill='white')
   f=self.work/f'storyboard-{off//24:02d}.jpg';im.save(f,quality=90);print('STORYBOARD',f,flush=True)
 def render(self,target,limit=None):
  clips=[]
  for s in self.project['scenes']:
   if limit is not None and s['start']>=limit:break
   s=copy.deepcopy(s)
   if limit is not None:s.update(end=min(s['end'],limit),duration=min(s['end'],limit)-s['start'])
   print('RENDER',s['id'],s['kind'],round(s['duration'],2),flush=True);clips.append(self.scene(s))
  playlist=self.work/('pilot-concat.txt' if limit else 'concat.txt');playlist.write_text('\n'.join("file '"+str(p)+"'" for p in clips)+'\n');target=Path(target);target.parent.mkdir(exist_ok=True,parents=True);duration=limit or self.project['duration'];subprocess.run(['ffmpeg','-y','-v','error','-xerror','-f','concat','-safe','0','-i',str(playlist),'-i',str(BASE/self.project['audio']),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-af','apad','-t',str(duration),'-movflags','+faststart',str(target)],check=True);print('READY',target,flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);p.add_argument('--output',type=Path,default=BASE/'output/final_video_hi_v1.mp4');p.add_argument('--preview',action='store_true');p.add_argument('--pilot',type=float);p.add_argument('--worker',type=int,choices=[0,1]);a=p.parse_args();r=Renderer(a.work)
 if a.preview:r.preview()
 elif a.worker is not None:
  for i,s in enumerate(r.project['scenes']):
   if i%2==a.worker:print('RENDER',i,s['id'],s['kind'],round(s['duration'],2),flush=True);r.scene(s)
  print('WORKER_DONE',a.worker,flush=True)
 else:r.render(a.output,a.pilot)
if __name__=='__main__':main()
