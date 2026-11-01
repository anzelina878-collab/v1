"""Episode 002 renderer. Uses the existing studio typography and light visual theme.
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

class Renderer:
 def __init__(self,work):
  self.project=json.loads((BASE/'episode.json').read_text());self.assets={a['id']:a for a in json.loads((BASE/'assets/manifest.json').read_text())};self.work=work;work.mkdir(parents=True,exist_ok=True)
  theme={**THEME,'font':str(STUDIO/'fonts/DejaVuSansCondensed.ttf'),'font_bold':str(STUDIO/'fonts/DejaVuSansCondensed-Bold.ttf')}
  self.painter=Painter({'style':'minimal','theme':theme,'title_motion':True,'scenes':self.project['scenes'],'_frames':round(self.project['duration']*30),'fps':30});self.flag=Image.open(BASE/'assets/flag-IR.png').convert('RGBA')
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
  dependencies=[Path(__file__),STUDIO/'studio/visuals.py',STUDIO/'fonts/DejaVuSansCondensed.ttf',STUDIO/'fonts/DejaVuSansCondensed-Bold.ttf',BASE/'assets/flag-IR.png']
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
def main():
 p=argparse.ArgumentParser();p.add_argument('--work',type=Path,default=BASE/'work');p.add_argument('--output',type=Path,default=BASE/'output/final_video_v1.mp4');p.add_argument('--preview',action='store_true');p.add_argument('--pilot',type=float);a=p.parse_args();r=Renderer(a.work)
 if a.preview:r.preview()
 else:r.render(a.output,a.pilot)
if __name__=='__main__':main()
