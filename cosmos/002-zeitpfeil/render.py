"""Frame-accurate silent-picture renderer; user narration is muxed privately afterwards."""
import pathlib,json,subprocess,argparse,hashlib,concurrent.futures,os,time,urllib.request,http.cookiejar,zipfile,shutil
R=pathlib.Path(__file__).resolve().parent

def command(args,log):
 with open(log,'w') as f:p=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT)
 if p.returncode:raise RuntimeError(str(log)+'\n'+pathlib.Path(log).read_text()[-2400:])

def get_json(path):return json.loads(subprocess.check_output(['gh','api',path]))

def prepare(plan,shots):
 assets={a['key']:a for a in plan['assets']};needed={s['asset'] for s in shots};(R/'assets').mkdir(exist_ok=True);(R/'logs').mkdir(exist_ok=True)
 if not all((R/str(assets[k]['path'])).exists() for k in needed if assets[k].get('kind')!='original3d' and not assets[k].get('derived_from')):
  stage=json.load(open(R/'transfer.json'));jar=http.cookiejar.CookieJar();op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar));url=stage['source_url']
  # First request establishes Filebin's ordinary download confirmation cookie.
  with op.open(urllib.request.Request(url,headers={'Range':'bytes=0-31'}),timeout=90) as f:f.read(64)
  dest=R/'visual_sources.zip'
  with op.open(url,timeout=180) as source,open(dest,'wb') as output:
   while data:=source.read(1024*1024):output.write(data)
  h=hashlib.sha256()
  with open(dest,'rb') as f:
   while b:=f.read(1024*1024):h.update(b)
  assert h.hexdigest()==stage['source_sha256'],'Visual source transfer does not match.'
  with zipfile.ZipFile(dest) as z:z.extractall(R)
  dest.unlink();print('Visual source bundle verified and restored.',flush=True)
 repo=os.environ.get('GH_REPO','anzelina878-collab/v1')
 def ensure(key):
  a=assets[key];dest=R/a['path']
  if dest.exists() and dest.stat().st_size>1000:return dest
  if a.get('derived_from'):
   base=ensure(a['derived_from']);command(['ffmpeg','-y','-v','warning','-threads','2','-i',str(base),'-vf','reverse','-an','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-threads','2','-filter_threads','2',str(dest)],R/'logs'/(key+'-reverse.log'));return dest
  if a.get('kind')!='original3d':
   if not a.get('url'):raise FileNotFoundError(dest)
   raw=dest.with_suffix('.source');req=urllib.request.Request(a['url'],headers={'User-Agent':'KosmionResearch/1.0'})
   with urllib.request.urlopen(req,timeout=120) as response,open(raw,'wb') as output:
    while b:=response.read(1024*1024):output.write(b)
   if 'source_in' in a:
    command(['ffmpeg','-y','-v','warning','-ss',str(a['source_in']),'-i',str(raw),'-t',str(a['duration']),'-an','-c:v','libx264','-preset','veryfast','-crf','21',str(dest)],R/'logs'/(key+'-restore.log'));raw.unlink()
   else:raw.replace(dest)
   return dest
  location=plan.get('scene_sources',{}).get(a['scene']);name=location['name'] if location else 'zeitpfeil-'+a['scene'];found=None
  for attempt in range(160):
   for run in ([location['run']] if location else plan['three_d_runs']):
    d=get_json(f'repos/{repo}/actions/runs/{run}/artifacts')
    found=next((x for x in d['artifacts'] if x['name']==name),None)
    if found:break
   if found:break
   if attempt%6==0:print('Waiting for completed 3D scene',name,flush=True)
   time.sleep(15)
  if not found:raise RuntimeError('3D scene not ready: '+name)
  archive=R/(name+'.zip')
  with open(archive,'wb') as out:subprocess.run(['gh','api',f'repos/{repo}/actions/artifacts/{found["id"]}/zip'],stdout=out,check=True)
  folder=R/name
  with zipfile.ZipFile(archive) as z:z.extractall(folder)
  candidate=next(folder.rglob(a['scene']+'.mp4'),None)
  if candidate is None:
   print('Recovering incomplete 3D render locally on this worker:',name,flush=True)
   subprocess.run(['sudo','apt-get','install','-y','-qq','blender'],check=True)
   fast=R/'make3d_recovery.py'
   command(['blender','-b','-t','2','-P',str(fast),'--',a['scene']],R/'logs'/(name+'-recovery.log'))
   command(['ffmpeg','-y','-v','warning','-framerate','25/2','-i',str(R/'3d'/a['scene']/'frame_%04d.jpg'),'-vf','framerate=fps=25','-t','7.84','-an','-c:v','libx264','-preset','veryfast','-crf','17','-threads','2','-filter_threads','2','-pix_fmt','yuv420p',str(dest)],R/'logs'/(name+'-recovery-encode.log'));return dest
  if a['scene']!='orbit':
   command(['ffmpeg','-y','-v','warning','-threads','2','-i',str(candidate),'-vf','nlmeans=s=8:p=5:r=9,hqdn3d=3:2:4:3','-an','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-filter_threads','2','-pix_fmt','yuv420p',str(dest)],R/'logs'/(name+'-clean.log'))
  else:shutil.copy(candidate,dest)
  archive.unlink();return dest
 for key in sorted(needed):ensure(key)
 return assets

def render(plan,shots,assets,output,jobs):
 fps=plan['fps'];cache=R/'render';cache.mkdir(exist_ok=True);logs=R/'logs';logs.mkdir(exist_ok=True)
 bold=R/'fonts/Lato-Bold.ttf';regular=R/'fonts/Lato-Regular.ttf'
 if not bold.exists():bold=pathlib.Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
 if not regular.exists():regular=pathlib.Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
 def filename(s):return cache/(s['render_key']+'.mp4')
 def alpha(start,end,offset=0):
  t=f'(t+{offset:.5f})';return f"if(lt({t},{start}),0,if(lt({t},{start+.35}),({t}-{start})/0.35,if(lt({t},{end-.35}),1,if(lt({t},{end}),({end}-{t})/0.35,0))))"
 def draw(text,font,size,x,y,color,opacity,fileid):
  p=logs/(fileid+'.txt');p.write_text(text)
  return f"drawtext=fontfile='{font}':textfile='{p}':fontsize={size}:fontcolor={color}:x={x}:y={y}:shadowcolor=black@0.85:shadowx=2:shadowy=2:alpha='{opacity}'"
 def one(s):
  out=filename(s)
  if out.exists() and out.stat().st_size>1000:return out
  a=assets[s['asset']];src=pathlib.Path(a['path']);src=src if src.is_absolute() else R/src;duration=s['frames']/fps;vf=[];cmd=['ffmpeg','-y','-hide_banner','-loglevel','warning','-threads','1']
  if a.get('media')=='image':
   cmd+=['-loop','1','-i',str(src)]
   if a.get('focus_crop'):x,y,w,h=a['focus_crop'];vf.append(f'crop={w}:{h}:{x}:{y}')
   vf += ['scale=1100:1000:force_original_aspect_ratio=decrease:flags=lanczos','pad=1920:1080:(ow-iw)*0.64:(oh-ih)/2:color=0x040910',f"zoompan=z='min(1.05,1+on*0.00015)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={s['frames']}:s=1920x1080:fps={fps}"]
  else:
   cmd+=['-ss',str(s['in']),'-t',str(duration*s.get('rate',1)+.08),'-i',str(src)]
   vf += [f"setpts=(PTS-STARTPTS)/{s.get('rate',1)}",'scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos','crop=1920:1080']
   if s.get('zoom',1)>1.001:
    z=s['zoom'];w=round(1920*z/2)*2;h=round(1080*z/2)*2;vf += [f'scale={w}:{h}:flags=lanczos','crop=1920:1080']
   vf += [f'fps={fps}']
  vf+=['setsar=1','eq=contrast=1.015:saturation=1.02']
  if a.get('kind')=='original3d':vf.append('hqdn3d=2:1.5:3:2')
  if s['fade_in']:vf.append(f"fade=t=in:st=0:d={s['fade_in']}")
  if s['fade_out']:vf.append(f"fade=t=out:st={max(0,duration-s['fade_out'])}:d={s['fade_out']}")
  for j,l in enumerate(s.get('labels',[])):
   opacity=alpha(l['global_start'],l['global_end'],s['start_frame']/fps);labelid=s['render_key']+f'-label{j}';size=58 if len(l['title'])>28 else 64
   vf.append(draw(l['eyebrow'],regular,24,96,851,'0xE7C880',opacity,labelid+'-small'))
   vf.append(draw(l['title'],bold,size,92,896,'white',opacity,labelid+'-title'))
   if l.get('subtitle'):vf.append(draw(l['subtitle'],regular,29,96,979,'white@0.92',opacity,labelid+'-sub'))
  if s.get('credit'):vf.append(draw(s['credit'],regular,20,64,1034,'white@0.82',alpha(0,duration),s['render_key']+'-credit'))
  cmd+=['-vf',','.join(vf),'-frames:v',str(s['frames']),'-an','-c:v','libx264','-preset','veryfast','-crf','19','-maxrate','10M','-bufsize','20M','-pix_fmt','yuv420p','-profile:v','high','-level','4.1','-g','50','-video_track_timescale','12800','-threads','1','-filter_threads','1',str(out)]
  command(cmd,logs/(s['render_key']+'.log'));print('SHOT',s['id'],s['asset'],round(duration,2),flush=True);return out
 specs={s['render_key']:s for s in shots}
 with concurrent.futures.ThreadPoolExecutor(jobs) as ex:list(ex.map(one,specs.values()))
 concat=output.with_suffix('.concat.txt');concat.write_text(''.join("file '"+str(filename(s))+"'\n" for s in shots))
 command(['ffmpeg','-y','-v','warning','-f','concat','-safe','0','-i',str(concat),'-c:v','copy','-an','-movflags','+faststart',str(output)],logs/(output.stem+'-concat.log'))
 probe=json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_streams','-show_format','-of','json',str(output)]));v=next(s for s in probe['streams'] if s['codec_type']=='video');assert int(v['nb_frames'])==sum(s['frames'] for s in shots);assert v['width']==1920 and v['height']==1080
 command(['ffmpeg','-v','error','-threads','2','-i',str(output),'-f','null','-'],logs/(output.stem+'-decode.log'));assert not (logs/(output.stem+'-decode.log')).read_text().strip()
 output.with_suffix('.verification.json').write_text(json.dumps(probe,indent=2));print('VERIFIED',output.name,probe['format']['duration'],output.stat().st_size,flush=True)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--part',type=int,default=-1);ap.add_argument('--jobs',type=int,default=2);ap.add_argument('--prepare',action='store_true');ap.add_argument('--upload',action='store_true');ap.add_argument('--preview',type=float,default=0);args=ap.parse_args();p=json.load(open(R/'plan.json'));shots=p['shots']
 if args.part>=0:
  spec=p['parts'][args.part];shots=shots[spec['first']:spec['last']]
 if args.preview:shots=[s for s in shots if (s['start_frame']+s['frames'])/p['fps']<=args.preview]
 assets=prepare(p,shots) if args.prepare else {a['key']:a for a in p['assets']}
 out=R/(f'picture_{args.part:02}.mp4' if args.part>=0 else 'picture_preview.mp4');render(p,shots,assets,out,args.jobs)
 if args.upload:
  stage=json.load(open(R/'transfer.json'));u=stage['picture_base']+'/'+out.name
  command(['curl','--fail-with-body','--retry','3','-X','POST','-H','Content-Type: video/mp4','--data-binary','@'+str(out),u,'-o',str(out.with_suffix('.upload.json'))],R/'logs'/('upload-'+out.stem+'.log'));r=json.load(open(out.with_suffix('.upload.json')));assert r['file']['bytes']==out.stat().st_size;print('TRANSFERRED',out.name,r['file']['sha256'],flush=True)
if __name__=='__main__':main()
