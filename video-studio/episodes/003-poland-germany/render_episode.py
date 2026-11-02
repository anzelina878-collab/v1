"""Episode 003 renderer. Uses the existing studio typography and light visual theme.
Video excerpts are never looped. Information plates have one entrance then freeze.
"""
import argparse,json,subprocess,sys,hashlib,io
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps
BASE=Path(__file__).resolve().parent
STUDIO=BASE.parents[1];sys.path.insert(0,str(STUDIO));sys.path.insert(0,str(BASE))
from studio.visuals import Painter,country_flag,ease
from studio.project import THEME
from tools.edit_rules import check_archive_spacing,entrance_time

class BaseRenderer:
 def __init__(self,work):
  self.project=json.loads((BASE/'episode.json').read_text());self.assets={a['id']:a for a in json.loads((BASE/'assets/manifest.json').read_text())};self.work=work;work.mkdir(parents=True,exist_ok=True)
  theme={**THEME,'font':str(STUDIO/'fonts/DejaVuSansCondensed.ttf'),'font_bold':str(STUDIO/'fonts/DejaVuSansCondensed-Bold.ttf')}
  self.painter=Painter({'style':'minimal','theme':theme,'title_motion':True,'scenes':self.project['scenes'],'_frames':round(self.project['duration']*30),'fps':30});self.flag=None
  check_archive_spacing(self.project['scenes'])
 def flag_at(self,im,country,x,y,w=90,h=60):
  if country=='IR':im.paste(self.flag.resize((w,h),Image.Resampling.LANCZOS),(x,y),self.flag.resize((w,h)).getchannel('A'))
  else:country_flag(im,country,x,y,w,h)
 def photo(self,key):return str(BASE/self.assets[key]['photo'])
 def credit(self,key,kind='photo'):
  a=self.assets[key];return a.get(kind+'_credit',a.get('credit',''))
 def labels(self,s,archive=False):
  im=Image.new('RGBA',(1920,1080));d=ImageDraw.Draw(im)
  if archive:
   d.rectangle((0,1008,1920,1080),fill=(12,18,21,170));self.flag_at(im,s.get('country','US'),55,1023,66,44)
   self.painter.text(im,self.credit(s['asset_id'],'video'),(160,1027,1700,35),22,'#FFFFFF',align='right')
  else:
   self.flag_at(im,s.get('country','US'),90,855)
   self.painter.text(im,s['title'],(90,930,1720,104),78,bold=True)
   credit=self.credit(s['asset_id'],'photo' if s['kind']=='photo' else 'video')
   self.painter.text(im,credit,(430,1042,1400,30),18,'muted',align='right')
   if s.get('note'):self.painter.text(im,s['note'],(220,864,1550,50),24,'muted')
  return im
 def plate(self,s,t):
  t=entrance_time(t)
  if s['kind']=='graphic':
   q={'type':'diagram','eyebrow':'','title':s['title'],'nodes':[{'title':v,'detail':''} for v in s['nodes']]}
   im=self.painter.render(q,t,0,s['start']+t)
   # Decorative connectors removed: parallel factors do not imply a causal chain.
   for j in range(len(s['nodes'])-1):
    ax=100+(j+1)*1740/len(s['nodes'])-35
    ImageDraw.Draw(im).rectangle((ax-52,606,ax+14,632),fill=THEME['background'])
   if any('1987' in v or '2019' in v or '500' in v for v in s['nodes']):self.painter.text(im,'Джерело: U.S. Department of State · INF Treaty',(90,1032,1730,32),20,'muted',align='right')
   return im
  if s['kind']=='compare':
   im=Image.new('RGB',(1920,1080),THEME['background']);self.painter.motion_text(im,s['title'],(90,150,1740,160),t,66,bold=True)
   for j,(key,title,country) in enumerate(s['sides']):
    x=90+j*900;d=ImageDraw.Draw(im);d.rounded_rectangle((x,355,x+840,955),radius=12,fill='white')
    self.painter.picture(im,{'_image':self.photo(key)},(x+35,390,770,380),t-j*.15)
    if t>.15+j*.15:
     self.flag_at(im,country,x+35,805,75,50);self.painter.text(im,title,(x+135,797,670,105),38,bold=True)
     self.painter.text(im,self.credit(key),(x+30,916,780,30),16,'muted',align='right',min_size=12)
   return im
  raise ValueError(s['kind'])
 def still(self,s,t=2):
  if s['kind'] in ['graphic','compare']:return self.plate(s,t)
  if s['kind']=='photo':
   im=self.painter.render({'type':'studio','country':'US','_image':self.photo(s['asset_id']),'_subject_only':True},2,0,s['start']+2);labels=self.labels(s);im.paste(labels,(0,0),labels);return im
  a=self.assets[s['asset_id']];position=s.get('source_in',0)+min(t,max(0,a['duration']-s.get('source_in',0)-.1))
  b=subprocess.check_output(['ffmpeg','-v','error','-ss',str(position),'-i',str(BASE/a['video']),'-frames:v','1','-vf','scale=1920:1080','-f','image2pipe','-vcodec','mjpeg','-']);im=Image.open(io.BytesIO(b)).convert('RGB');labels=self.labels(s,s['kind']=='archive');im.paste(labels,(0,0),labels);return im
 def preview(self):
  scenes=self.project['scenes'];sheets=[]
  for offset in range(0,len(scenes),24):
   sheet=Image.new('RGB',(1280,6*202),'#152026');d=ImageDraw.Draw(sheet)
   for j,s in enumerate(scenes[offset:offset+24]):
    im=self.still(s,min(2,s['duration']*.5));sheet.paste(im.resize((320,180)),(j%4*320,j//4*202));d.text((j%4*320+4,j//4*202+182),f"{s['id']} {s['start']:.1f}s {s['kind']}",fill='white')
   f=self.work/f'storyboard-{offset//24:02d}.jpg';sheet.save(f,quality=88);sheets.append(str(f));print('STORYBOARD',f,flush=True)
  return sheets
 def signature(self,s):
  keys=[side[0] for side in s['sides']] if s['kind']=='compare' else [s['asset_id']] if s['kind'] in ['photo','archive','turntable'] else []
  records=[self.assets[key] for key in keys]
  dependencies=[Path(__file__),STUDIO/'studio/visuals.py',STUDIO/'fonts/DejaVuSansCondensed.ttf',STUDIO/'fonts/DejaVuSansCondensed-Bold.ttf']
  for key in keys:
   a=self.assets[key];field='video' if s['kind'] in ['archive','turntable'] else 'photo'
   if a.get(field):dependencies.append(BASE/a[field])
  data={'scene':s,'assets':records,'media':[(str(f),f.stat().st_size,f.stat().st_mtime_ns) for f in dependencies],'renderer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'resolution':[1920,1080,30],'encoding':['libx264','veryfast',22]}
  return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
 def scene(self,s):
  directory=self.work/s['id'];directory.mkdir(exist_ok=True);out=directory/'scene.mp4';stamp=directory/'fingerprint.txt'
  fingerprint=self.signature(s)
  if out.exists() and stamp.exists() and stamp.read_text()==fingerprint:return out
  frames=round(s['end']*30)-round(s['start']*30);duration=frames/30;cmd=['ffmpeg','-y','-v','error','-threads','1'];filt=[]
  if s['kind'] in ['archive','turntable']:
   a=self.assets[s['asset_id']];cmd+=['-ss',str(s.get('source_in',0)),'-i',str(BASE/a['video'])]
   if s['kind']=='turntable':
    # Retiming covers the complete geometric revolution once, never a partial spin.
    rate=duration/a['duration'];filt.append(f'[0:v]setpts={rate}*PTS,fps=30,scale=1920:1080,setsar=1[base]')
   else:filt.append('[0:v]fps=30,scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1[base]')
   overlay=directory/'labels.png';self.labels(s,s['kind']=='archive').save(overlay);cmd+=['-loop','1','-framerate','30','-i',str(overlay)];filt.append('[base][1:v]overlay=0:0,format=yuv420p[v]');cmd+=['-filter_complex',';'.join(filt),'-filter_complex_threads','1','-map','[v]']
  elif s['kind']=='photo':
   base=directory/'subject.png';self.painter.render({'type':'studio','country':'US','_image':self.photo(s['asset_id']),'_subject_only':True},2,0,s['start']+2).save(base)
   labels=directory/'labels.png';self.labels(s).save(labels);cmd+=['-loop','1','-framerate','30','-i',str(base),'-loop','1','-framerate','30','-i',str(labels)]
   filt=[f"[0:v]zoompan=z='1+0.025*on/{max(1,frames-1)}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=1920x1080:fps=30[base]",'[base][1:v]overlay=0:0,format=yuv420p[v]'];cmd+=['-filter_complex',';'.join(filt),'-filter_complex_threads','1','-map','[v]']
  else:
   entrance=min(frames,37)
   # Only these initial frames are animated; tpad clones the settled final image.
   for f in range(entrance):self.plate(s,f/30).save(directory/f'entry-{f:03d}.png')
   cmd+=['-framerate','30','-i',str(directory/'entry-%03d.png'),'-vf',f'tpad=stop_mode=clone:stop_duration={duration},setsar=1']
  cmd+=['-an','-frames:v',str(frames),'-r','30','-c:v','libx264','-preset','veryfast','-crf','22','-threads','2','-pix_fmt','yuv420p','-video_track_timescale','15360','-movflags','+faststart',str(out)]
  with (directory/'ffmpeg.log').open('w') as log:
   r=subprocess.run(cmd,stderr=log)
  if r.returncode:raise RuntimeError((directory/'ffmpeg.log').read_text()[-1500:])
  n=int(json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames','-of','json',str(out)]))['streams'][0]['nb_frames'])
  if n!=frames:raise ValueError(f"Short scene {s['id']}: {n} != {frames}; do not loop/freeze documentary footage")
  stamp.write_text(fingerprint);return out
 def render(self,target,limit=None):
  scenes=self.project['scenes']
  if limit is not None:
   scenes=[dict(s,end=min(s['end'],limit),duration=min(s['end'],limit)-s['start']) for s in scenes if s['start']<limit]
  clips=[]
  for i,s in enumerate(scenes):print('RENDER',i+1,'/',len(scenes),s['id'],s['kind'],round(s['duration'],2),flush=True);clips.append(self.scene(s))
  playlist=self.work/('pilot-concat.txt' if limit else 'concat.txt');playlist.write_text('\n'.join("file '"+str(f)+"'" for f in clips)+'\n');duration=limit or self.project['duration'];target.parent.mkdir(parents=True,exist_ok=True)
  subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(playlist),'-i',str(BASE/self.project['audio']),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-af','apad','-t',str(duration),'-movflags','+faststart',str(target)],check=True);print('READY',target,flush=True)
class Renderer(BaseRenderer):
 def __init__(self,work):
  super().__init__(work)
  self.geo=json.loads((BASE/'assets/maps/europe.geojson').read_text())
 def flag_at(self,im,country,x,y,w=90,h=60):
  d=ImageDraw.Draw(im)
  if country=='DE':
   for j,color in enumerate(['#111111','#DD0000','#FFCE00']):d.rectangle((x,y+j*h/3,x+w,y+(j+1)*h/3),fill=color)
  elif country=='PL':
   d.rectangle((x,y,x+w,y+h),fill='#DC143C');d.rectangle((x,y,x+w,y+h/2),fill='white');d.rectangle((x,y,x+w,y+h),outline='#CAD0CA',width=1)
  else:super().flag_at(im,country,x,y,w,h)
 def credit(self,key,kind='photo'):
  a=self.assets[key];s=a.get(kind+'_credit',a.get('credit','')).replace('\n',' ').strip()
  return s if len(s)<145 else s[:105]+'… · '+a.get(kind+'_metadata',{}).get('license','')
 def labels(self,s,archive=False):
  if not archive:return super().labels(s,False)
  im=Image.new('RGBA',(1920,1080));d=ImageDraw.Draw(im);d.rectangle((0,970,1920,1080),fill=(17,24,23,183));self.flag_at(im,s.get('country','PL'),45,989,72,48);self.painter.text(im,s.get('title',''),(133,986,1725,64),46,'#FFFFFF',bold=True,min_size=28);self.painter.text(im,self.credit(s['asset_id'],'video'),(700,1051,1160,26),18,'#FFFFFF',align='right',min_size=12);return im
 def map_frame(self,s,t):
  import numpy as np
  from studio.visuals import ease
  im=Image.new('RGB',(1920,1080),THEME['background']);d=ImageDraw.Draw(im);baltic=s['asset_id']=='map-baltic';bounds=(-7,37,43,61) if not baltic else(3,31,50,61);x0,x1,y0,y1=bounds;scale=min(1500/((x1-x0)*.6),700/(y1-y0));cx=(x0+x1)/2;cy=(y0+y1)/2
  def project(point):return(960+(point[0]-cx)*.6*scale,550-(point[1]-cy)*scale)
  for f in self.geo['features']:
   country=f['properties'].get('ADMIN','');geom=f['geometry'];polys=geom['coordinates'] if geom['type']=='MultiPolygon' else[geom['coordinates']];color='#D7DDD7'
   if country=='Germany':color=tuple(round(a+(b-a)*ease(t/.65)) for a,b in zip([215,221,215],[40,96,140]))
   if country=='Poland':color=tuple(round(a+(b-a)*ease((t-.3)/.65)) for a,b in zip([215,221,215],[177,53,61]))
   for poly in polys:
    ring=poly[0]
    if not any(x0-2<pt[0]<x1+2 and y0-2<pt[1]<y1+2 for pt in ring):continue
    d.polygon([project(v) for v in ring],fill=color,outline='#F2F3F0',width=3)
  self.painter.text(im,s.get('title','ПОЛЬЩА ТА НІМЕЧЧИНА'),(90,75,1740,110),64,bold=True)
  for name,capital,coord,country in [('НІМЕЧЧИНА','Берлін',(13.405,52.52),'DE'),('ПОЛЬЩА','Варшава',(21.012,52.23),'PL')]:
   x,y=project(coord);d.ellipse((x-7,y-7,x+7,y+7),fill='#FFFFFF',outline='#202923',width=2);self.painter.text(im,capital,(x-120,y+17,270,50),27,'#FFFFFF',align='center');lx=430 if country=='DE' else 1130;self.flag_at(im,country,lx,880,72,48);self.painter.text(im,name,(lx+95,880,480,60),40,bold=True)
  if baltic:self.painter.text(im,'БАЛТІЙСЬКЕ МОРЕ',(1000,260,740,90),44,'blue',align='center')
  self.painter.text(im,'Картографія: Natural Earth · Public domain',(810,1044,1020,28),18,'muted',align='right');return im
 def plate(self,s,t):
  t=min(t,s.get('settle_after',1.2))
  if s['kind']=='map':return self.map_frame(s,t)
  if s['kind'] in ['section','outro']:return self.painter.render({'type':s['kind'],'eyebrow':'','title':s['title'],'subtitle':s.get('subtitle',''),'animate_title':True},t,0,s['start']+t)
  if s['kind']=='question':
   q={'type':'diagram','eyebrow':'','title':s['title'],'nodes':[{'title':v,'detail':''} for v in s['nodes']]};im=self.painter.render(q,t,0,s['start']+t)
   for j in range(len(s['nodes'])-1):
    ax=100+(j+1)*1740/len(s['nodes'])-35;ImageDraw.Draw(im).rectangle((ax-52,606,ax+14,632),fill=THEME['background'])
   return im
  return super().plate(s,t)
 def still(self,s,t=2):
  if s['kind'] in ['section','outro','question','map']:return self.plate(s,t)
  if s['kind']=='ident':
   import io
   a=self.assets[s['asset_id']];b=subprocess.check_output(['ffmpeg','-v','error','-ss',str(min(a['duration']-.1,t/s['duration']*a['duration'])),'-i',str(BASE/a['video']),'-frames:v','1','-vf','scale=1920:1080','-f','image2pipe','-vcodec','mjpeg','-']);return Image.open(io.BytesIO(b)).convert('RGB')
  return super().still(s,t)
 def signature(self,s):
  if s['kind'] in ['section','outro','question','map','ident']:
   deps=[Path(__file__),BASE/'assets/maps/europe.geojson']
   if s['kind']=='ident':deps.append(BASE/self.assets[s['asset_id']]['video'])
   return hashlib.sha256(json.dumps([s,self.painter.c,[(str(f),f.stat().st_size,f.stat().st_mtime_ns) for f in deps]],sort_keys=True).encode()).hexdigest()
  return super().signature(s)
 def render(self,target,limit=None):
  target.parent.mkdir(parents=True,exist_ok=True)
  try:import fcntl
  except ImportError:return super().render(target,limit)
  with target.with_suffix(target.suffix+'.lock').open('a+b') as lock:
   fcntl.flock(lock,fcntl.LOCK_EX)
   return super().render(target,limit)
 def scene(self,s):
  directory=self.work/s['id'];directory.mkdir(exist_ok=True)
  try:import fcntl
  except ImportError:return self._scene_locked(s)
  with (directory/'.render.lock').open('a+b') as lock:
   fcntl.flock(lock,fcntl.LOCK_EX)
   return self._scene_locked(s)
 def _scene_locked(self,s):
  if s['kind'] not in ['photo','turntable','ident']:return super().scene(s)
  directory=self.work/s['id'];directory.mkdir(exist_ok=True);out=directory/'scene.mp4';stamp=directory/'fingerprint.txt';key=self.signature(s)
  if out.exists() and stamp.exists() and stamp.read_text()==key:return out
  frames=round(s['end']*30)-round(s['start']*30);duration=frames/30;cmd=['ffmpeg','-y','-v','error','-threads','1']
  if s['kind']=='photo':
   f=directory/'locked.png';self.still(s,2).save(f);cmd+=['-loop','1','-framerate','30','-i',str(f),'-vf','setsar=1']
  elif s['kind']=='ident':
   a=self.assets[s['asset_id']];cmd+=['-i',str(BASE/a['video']),'-vf',f"setpts={duration/a['duration']}*PTS,fps=30,tpad=stop_mode=clone:stop_duration=0.1,setsar=1"]
  else:
   a=self.assets[s['asset_id']];f=directory/'labels.png';self.labels(s).save(f);cmd+=['-ss',str(s.get('source_in',0)),'-i',str(BASE/a['video']),'-loop','1','-framerate','30','-i',str(f),'-filter_complex',f'[0:v]fps=30,scale=1920:1080,tpad=stop_mode=clone:stop_duration={duration},setsar=1[base];[base][1:v]overlay=0:0,format=yuv420p[v]','-filter_complex_threads','1','-map','[v]']
  cmd+=['-an','-frames:v',str(frames),'-r','30','-c:v','libx264','-preset','veryfast','-crf','22','-threads','2','-pix_fmt','yuv420p','-video_track_timescale','15360','-movflags','+faststart',str(out)]
  with (directory/'ffmpeg.log').open('w') as log:subprocess.run(cmd,stderr=log,check=True)
  n=int(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames','-of','csv=p=0',str(out)]));assert n==frames,(s['id'],n,frames);stamp.write_text(key);return out

def main():
 p=argparse.ArgumentParser();p.add_argument('--work',type=Path,default=BASE/'work');p.add_argument('--output',type=Path,default=BASE/'output/final_video_v1.mp4');p.add_argument('--preview',action='store_true');p.add_argument('--pilot',type=float);a=p.parse_args();r=Renderer(a.work)
 if a.preview:r.preview()
 else:r.render(a.output,a.pilot)
if __name__=='__main__':main()
