"""Hindi edition renderer using the original approved studio composition.
Devanagari uses Noto + RAQM shaping. Photos lock; cards enter once and hold.
"""
from pathlib import Path
import sys,json,hashlib,subprocess,argparse,io,math,re
from PIL import Image,ImageDraw,ImageOps,features
BASE=Path(__file__).resolve().parent;STUDIO=BASE.parents[1];sys.path.insert(0,str(STUDIO))
from studio.visuals import Painter,country_flag
from studio.project import THEME

class HindiPainter(Painter):
 def text(self,im,value,box,size=42,color='ink',bold=False,align='left',min_size=18):
  old=(self.c['font'],self.c['font_bold'])
  if not re.search('[\u0900-\u097f]',str(value)):
   self.c['font']=str(STUDIO/'fonts/DejaVuSansCondensed.ttf');self.c['font_bold']=str(STUDIO/'fonts/DejaVuSansCondensed-Bold.ttf')
  try:return super().text(im,value,box,size,color,bold,align,min_size)
  finally:self.c['font'],self.c['font_bold']=old

class Renderer:
 def __init__(self,work):
  assert features.check('raqm'),'A shaping-capable Pillow/RAQM build is required for Hindi'
  self.project=json.load(open(BASE/'episode.json'));self.work=Path(work);self.work.mkdir(exist_ok=True,parents=True)
  theme={**THEME,'font':str(BASE/'fonts/ArsenalHindi-Regular.ttf'),'font_bold':str(BASE/'fonts/ArsenalHindi-Bold.ttf'),'background':'#F2F3F0'}
  self.painter=HindiPainter({'theme':theme,'style':'minimal','title_motion':True,'scenes':self.project['scenes'],'_frames':round(self.project['duration']*30),'fps':30,'brand':'ARSENAL 360'})
  self.archives={r['id']:r for r in json.load(open(BASE/'assets/archive-manifest.json'))};self.rights=json.load(open(BASE/'assets/rights-manifest.json'));self.durations={}
 def duration(self,path):
  path=str(path)
  if path not in self.durations:self.durations[path]=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',path]))
  return self.durations[path]
 def prepared(self,s):
  d=dict(s)
  if s.get('image'):d['_image']=str(BASE/s['image'])
  for key in ['sides','items']:
   if key in s:d[key]=[{**x,'_image':str(BASE/x['image'])} if x.get('image') else dict(x) for x in s[key]]
  return d
 def credit(self,s):
  if s.get('archive_bank'):return self.archives[s['archive_bank']]['source']['credit'].replace('Архів','अभिलेख')
  if s.get('motion_kind')=='true_3d':return 'nisu · CC0 · 3D visualization' if 'm4a1' in s['video'] else 'NoBE Aubé · Blendkit Royalty Free · 3D visualization'
  key=s.get('asset_id','');a=self.rights.get(key,{})
  return (a.get('creator','')+' · '+a.get('license','')).strip(' ·') or s.get('source','')
 def labels(self,s,archive=False):
  im=Image.new('RGBA',(1920,1080));d=ImageDraw.Draw(im)
  if archive:
   d.rectangle((0,974,1920,1080),fill=(15,22,18,185));c=s.get('country',s.get('archive_edit',{}).get('country','US'));country_flag(im,c,44,991,64,43);self.painter.text(im,s.get('title',''),(132,984,1700,64),38,'#FFFFFF',True,min_size=22);self.painter.text(im,self.credit(s),(610,1045,1265,30),18,'#FFFFFF',align='right',min_size=12)
  else:
   country_flag(im,s.get('country','US'),90,855);self.painter.text(im,s.get('title',''),(90,917,1720,118),78,bold=True,min_size=30);self.painter.text(im,self.credit(s),(430,1040,1400,32),18,'muted',align='right',min_size=12)
  return im
 def facts(self,im,s,t):
  for c in s.get('callouts',[]):
   if c['start']<=t<c['end']:self.painter.tag(im,c['text'],1230,100,600)
  return im
 def plate(self,s,t):
  t=min(t,s.get('settle_after',1.2));im=self.painter.render(self.prepared(s),t,0,s['start']+t)
  if s['type']=='outro':self.painter.text(im,'ARSENAL 360  |  शस्त्र 360',(280,964,1360,60),28,'muted',align='center')
  if s['type']=='compare':
   for j,x in enumerate(s.get('sides',[])):
    name=Path(x.get('image','')).stem;name={'M157_DETAIL':'M7','IFAK_CUT':'IFAK','MSV_CUT':'MSV','XINGKONG_CUT':'XINGKONG'}.get(name,name);a=self.rights.get(name,{});credit=(a.get('creator','')+' · '+a.get('license','')).strip(' ·');self.painter.text(im,credit,(120+j*900,907,780,27),15,'muted',align='right',min_size=10)
  return im
 def still(self,s,t=2):
  if s['type']=='studio' and not s.get('video'):
   im=self.painter.render({**self.prepared(s),'_subject_only':True},2,0,s['start']+2);lay=self.labels(s);im.paste(lay,(0,0),lay);return self.facts(im,s,t)
  if s.get('video'):
   p=BASE/s['video'];position=(s.get('source_in',0)+t)%self.duration(p) if s.get('motion_kind')=='true_3d' else min(self.duration(p)-.05,s.get('source_in',0)+t)
   b=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(position),'-i',str(p),'-frames:v','1','-vf','scale=1920:1080','-threads','1','-f','image2pipe','-vcodec','png','-']);im=Image.open(io.BytesIO(b)).convert('RGB');lay=self.labels(s,s['type']=='footage');im.paste(lay,(0,0),lay);return self.facts(im,s,t)
  return self.plate(s,t)
 def signature(self,s):
  deps=[Path(__file__),STUDIO/'studio/visuals.py',BASE/'fonts/ArsenalHindi-Regular.ttf',BASE/'fonts/ArsenalHindi-Bold.ttf',BASE/'assets/rights-manifest.json']
  for o in [s]+s.get('sides',[])+s.get('items',[]):
   for k in ['image','video']:
    if o.get(k):deps.append(BASE/o[k])
  if s.get('archive_bank'):deps.append(BASE/'assets/archive-manifest.json')
  return hashlib.sha256(json.dumps([s,[(str(p),p.stat().st_size,p.stat().st_mtime_ns) for p in deps]],sort_keys=True).encode()).hexdigest()
 def scene(self,s):
  d=self.work/s['id'];d.mkdir(exist_ok=True);out=d/'scene.mp4';stamp=d/'fingerprint.txt';fingerprint=self.signature(s)
  if out.exists() and stamp.exists() and stamp.read_text()==fingerprint:return out
  frames=round(s['end']*30)-round(s['start']*30);duration=frames/30;cmd=['ffmpeg','-y','-v','error','-threads','1']
  if s['type']=='studio' and not s.get('video'):
   im=d/'locked.png';base=self.painter.render({**self.prepared(s),'_subject_only':True},2,0,s['start']+2);lay=self.labels(s);base.paste(lay,(0,0),lay);base.save(im);cmd+=['-loop','1','-framerate','30','-i',str(im)]
   filters=['[0:v]setsar=1[p0]'];last='p0'
   for j,c in enumerate([c for c in s.get('callouts',[]) if c['end']>c['start']]):
    lay=d/f'fact-{j}.png';overlay=Image.new('RGBA',(1920,1080));self.painter.tag(overlay,c['text'],1230,100,600);overlay.save(lay);cmd+=['-loop','1','-framerate','30','-i',str(lay)];filters.append(f"[{last}][{j+1}:v]overlay=0:0:enable='gte(t,{c['start']})*lt(t,{c['end']})'[p{j+1}]");last=f'p{j+1}'
   filters.append(f'[{last}]format=yuv420p[v]');cmd+=['-filter_complex',';'.join(filters),'-filter_complex_threads','1','-map','[v]']
  elif s.get('video'):
   bank=BASE/s['video'];model=s.get('motion_kind')=='true_3d';lay=d/'labels.png';self.labels(s,s['type']=='footage').save(lay)
   if model:cmd+=['-stream_loop','-1']
   cmd+=['-ss',str(s.get('source_in',0)),'-i',str(bank),'-loop','1','-framerate','30','-i',str(lay)]
   filters=[f'[0:v]fps=30,scale=1920:1080,tpad=stop_mode=clone:stop_duration={duration},setsar=1[base]','[base][1:v]overlay=0:0[p0]'];last='p0'
   for j,c in enumerate([c for c in s.get('callouts',[]) if c['end']>c['start']]):
    lay=d/f'fact-{j}.png';im=Image.new('RGBA',(1920,1080));self.painter.tag(im,c['text'],1230,100,600);im.save(lay);cmd+=['-loop','1','-framerate','30','-i',str(lay)];filters.append(f"[{last}][{j+2}:v]overlay=0:0:enable='gte(t,{c['start']})*lt(t,{c['end']})'[p{j+1}]");last=f'p{j+1}'
   filters.append(f'[{last}]format=yuv420p[v]');cmd+=['-filter_complex',';'.join(filters),'-filter_complex_threads','1','-map','[v]']
  else:
   entrance=min(frames,round(s.get('settle_after',1.2)*30)+1)
   for i in range(entrance):self.plate(s,i/30).save(d/f'entry-{i:03d}.png')
   cmd+=['-framerate','30','-i',str(d/'entry-%03d.png'),'-vf',f'tpad=stop_mode=clone:stop_duration={duration},setsar=1']
  cmd+=['-an','-frames:v',str(frames),'-r','30','-c:v','libx264','-preset','veryfast','-crf','22','-threads','2','-pix_fmt','yuv420p','-video_track_timescale','15360','-movflags','+faststart',str(out)]
  with (d/'ffmpeg.log').open('w') as log:subprocess.run(cmd,stderr=log,check=True)
  actual=int(json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames','-of','json',str(out)]))['streams'][0]['nb_frames']);assert actual==frames,(s['id'],actual,frames);stamp.write_text(fingerprint);return out
 def preview(self):
  for off in range(0,len(self.project['scenes']),24):
   sheet=Image.new('RGB',(1280,6*202),'#152026');d=ImageDraw.Draw(sheet)
   for j,s in enumerate(self.project['scenes'][off:off+24]):
    im=self.still(s,min(2,s['duration']*.5));sheet.paste(im.resize((320,180)),(j%4*320,j//4*202));d.text((j%4*320+3,j//4*202+181),f"{s['id']} {s['start']:.2f}s {s['type']}",fill='white')
   f=self.work/f'storyboard-{off//24:02d}.jpg';sheet.save(f,quality=90);print('STORYBOARD',f,flush=True)
 def render(self,target,limit=None):
  scenes=self.project['scenes'];clips=[]
  for i,original in enumerate(scenes):
   if limit is not None and original['start']>=limit:break
   s=dict(original)
   if limit is not None:s.update(end=min(s['end'],limit),duration=min(s['end'],limit)-s['start'])
   print('RENDER',i+1,len(scenes),s['id'],s['type'],round(s['duration'],2),flush=True);clips.append(self.scene(s))
  playlist=self.work/('pilot-concat.txt' if limit else 'concat.txt');playlist.write_text('\n'.join("file '"+str(p)+"'" for p in clips)+'\n');target=Path(target);target.parent.mkdir(exist_ok=True,parents=True);duration=limit or self.project['duration']
  subprocess.run(['ffmpeg','-y','-v','error','-xerror','-f','concat','-safe','0','-i',str(playlist),'-i',str(BASE/self.project['audio']),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-af','apad','-t',str(duration),'-movflags','+faststart',str(target)],check=True);print('READY',target,flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);p.add_argument('--output',type=Path,default=BASE/'output/final_video_hi_v1.mp4');p.add_argument('--preview',action='store_true');p.add_argument('--pilot',type=float);p.add_argument('--worker',type=int,choices=[0,1]);a=p.parse_args();r=Renderer(a.work)
 if a.preview:r.preview()
 elif a.worker is not None:
  for i,s in enumerate(r.project['scenes']):
   if i%2==a.worker:print('RENDER',i,s['id'],s['type'],round(s['duration'],2),flush=True);r.scene(s)
  print('WORKER_DONE',a.worker,flush=True)
 else:r.render(a.output,a.pilot)
if __name__=='__main__':main()
