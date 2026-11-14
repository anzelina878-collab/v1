"""Render silent, frame-accurate picture. Supplied narration never leaves the private workspace."""
import pathlib,json,subprocess,argparse,hashlib,concurrent.futures,os,time,urllib.request,http.cookiejar,zipfile,shutil
R=pathlib.Path(__file__).resolve().parent

def command(args,log):
 with open(log,'w') as f:p=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT)
 if p.returncode:raise RuntimeError(str(log)+'\n'+pathlib.Path(log).read_text()[-2200:])
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_streams','-show_format','-of','json',str(p)]))
def download(url,dest):
 for attempt in range(4):
  try:
   req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
   with urllib.request.urlopen(req,timeout=150) as source,open(dest.with_suffix('.download'),'wb') as out:
    while b:=source.read(1024*1024):out.write(b)
   dest.with_suffix('.download').replace(dest);return
  except Exception:
   if attempt==3:raise
   time.sleep(3*(attempt+1))
def prepare(plan,shots):
 assets={a['key']:a for a in plan['assets']};needed={s['asset'] for s in shots};(R/'assets').mkdir(exist_ok=True);(R/'logs').mkdir(exist_ok=True);stage=json.load(open(R/'transfer.json'))
 # This bundle contains fonts and public archival/illustration sources only.
 if not (R/'fonts/Lato-Bold.ttf').exists():
  jar=http.cookiejar.CookieJar();op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar));url=stage['source_url']
  with op.open(urllib.request.Request(url,headers={'Range':'bytes=0-31'}),timeout=90) as f:f.read(64)
  dest=R/'visual_sources.zip'
  with op.open(url,timeout=180) as source,open(dest,'wb') as out:
   while b:=source.read(1024*1024):out.write(b)
  assert hashlib.sha256(dest.read_bytes()).hexdigest()==stage['source_sha256']
  with zipfile.ZipFile(dest) as z:z.extractall(R)
  dest.unlink();print('Public visual sources verified.',flush=True)
 repo=os.environ.get('GH_REPO','anzelina878-collab/v1')
 def ensure(k):
  a=assets[k];dest=R/a['path']
  if dest.exists() and dest.stat().st_size>1000:return
  if a['kind']=='original3d':
   location=plan['scene_sources'][a['scene']];found=None
   for attempt in range(160):
    data=json.loads(subprocess.check_output(['gh','api',f'repos/{repo}/actions/runs/{location["run"]}/artifacts']));found=next((x for x in data['artifacts'] if x['name']==location['name']),None)
    if found:break
    time.sleep(10)
   if not found:raise RuntimeError('Missing 3D scene '+k)
   archive=R/(k+'.zip')
   with open(archive,'wb') as f:subprocess.run(['gh','api',f'repos/{repo}/actions/artifacts/{found["id"]}/zip'],stdout=f,check=True)
   folder=R/k
   with zipfile.ZipFile(archive) as z:z.extractall(folder)
   candidate=next(folder.rglob(a['scene']+'.mp4'),None)
   if candidate is None:raise RuntimeError('Incomplete original scene artifact '+k)
   shutil.copy(candidate,dest);archive.unlink()
  else:
   if 'source_in' in a:
    raw=dest.with_suffix('.source');download(a['url'],raw)
    command(['ffmpeg','-y','-v','warning','-ss',str(a['source_in']),'-i',str(raw),'-t',str(a['duration']),'-an','-c:v','libx264','-preset','veryfast','-crf','19','-threads','2',str(dest)],R/'logs'/(k+'-restore.log'));raw.unlink()
   else:download(a['url'],dest)
  if a['media']=='video':
   p=probe(dest);v=next(x for x in p['streams'] if x['codec_type']=='video');assert v['width']>=min(1280,a['width']);assert float(p['format']['duration'])>=a['duration']-.6
  print('SOURCE READY',k,flush=True)
 with concurrent.futures.ThreadPoolExecutor(3) as ex:list(ex.map(ensure,sorted(needed)))
 return assets

def render(plan,shots,assets,output,jobs):
 cache=R/'render';cache.mkdir(exist_ok=True);logs=R/'logs';logs.mkdir(exist_ok=True);fps=plan['fps'];bold=R/'fonts/Lato-Bold.ttf';regular=R/'fonts/Lato-Regular.ttf'
 def filename(s):return cache/(s['render_key']+'.mp4')
 def alpha(start,end,offset=0):
  t=f'(t+{offset:.5f})';return f"if(lt({t},{start}),0,if(lt({t},{start+.3}),({t}-{start})/0.3,if(lt({t},{end-.3}),1,if(lt({t},{end}),({end}-{t})/0.3,0))))"
 def draw(text,font,size,x,y,color,opacity,name):
  p=logs/(name+'.txt');p.write_text(text)
  return f"drawtext=fontfile='{font}':textfile='{p}':fontsize={size}:fontcolor={color}:x={x}:y={y}:borderw=1:bordercolor=black@0.45:shadowcolor=black@0.9:shadowx=2:shadowy=2:alpha='{opacity}'"
 def one(s):
  out=filename(s)
  if out.exists() and out.stat().st_size>1000:return
  a=assets[s['asset']];src=pathlib.Path(a['path']);src=src if src.is_absolute() else R/src;duration=s['frames']/fps;vf=[];cmd=['ffmpeg','-y','-hide_banner','-loglevel','warning','-threads','1']
  if a['media']=='image':
   cmd+=['-loop','1','-i',str(src)]
   if a['kind']=='archive_photo':
    vf+=['scale=1100:1000:force_original_aspect_ratio=decrease:flags=lanczos','pad=1920:1080:(ow-iw)*0.68:(oh-ih)/2:color=0x030710']
   else:vf+=['scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos','crop=1920:1080']
   vf+=[f"zoompan=z='min(1.04,1+on*0.00012)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={s['frames']}:s=1920x1080:fps={fps}"]
  else:
   cmd+=['-ss',str(s['in']),'-t',str(duration+.1),'-i',str(src)]
   vf+=['setpts=PTS-STARTPTS','scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos','crop=1920:1080',f'fps={fps}']
  vf+=['tpad=stop_mode=clone:stop_duration=1','setsar=1','eq=contrast=1.01:saturation=1.015']
  if s['fade_in']:vf.append(f"fade=t=in:st=0:d={s['fade_in']}")
  if s['fade_out']:vf.append(f"fade=t=out:st={max(0,duration-s['fade_out'])}:d={s['fade_out']}")
  for j,l in enumerate(s.get('labels',[])):
   op=alpha(l['global_start'],l['global_end'],s['start_frame']/25);labelid=s['render_key']+f'-label{j}';size=48 if len(l['title'])>25 else 54
   vf.append(draw(l['title'],bold,size,84,919,'white',op,labelid+'-title'))
   if l.get('subtitle'):vf.append(draw(l['subtitle'],regular,28,87,984,'white@0.92',op,labelid+'-sub'))
  if s.get('credit'):vf.append(draw(s['credit'],regular,14,42,1048,'white@0.72',alpha(0,duration),s['render_key']+'-credit'))
  cmd+=['-vf',','.join(vf),'-frames:v',str(s['frames']),'-an','-c:v','libx264','-preset','veryfast','-crf','20','-maxrate','6M','-bufsize','12M','-pix_fmt','yuv420p','-profile:v','high','-level','4.1','-g','50','-video_track_timescale','12800','-threads','1','-filter_threads','1',str(out)]
  command(cmd,logs/(s['render_key']+'.log'));assert int(next(x for x in probe(out)['streams'] if x['codec_type']=='video')['nb_frames'])==s['frames'];print('SHOT',s['id'],s['asset'],round(duration,2),flush=True)
 with concurrent.futures.ThreadPoolExecutor(jobs) as ex:list(ex.map(one,shots))
 listing=output.with_suffix('.concat.txt');listing.write_text(''.join("file '"+str(filename(s))+"'\n" for s in shots));command(['ffmpeg','-y','-v','warning','-f','concat','-safe','0','-i',str(listing),'-c:v','copy','-an','-movflags','+faststart',str(output)],logs/(output.stem+'-concat.log'))
 p=probe(output);v=next(x for x in p['streams'] if x['codec_type']=='video');assert int(v['nb_frames'])==sum(s['frames'] for s in shots);assert v['width']==1920 and v['height']==1080
 command(['ffmpeg','-v','error','-threads','2','-i',str(output),'-f','null','-'],logs/(output.stem+'-decode.log'));assert not (logs/(output.stem+'-decode.log')).read_text().strip();output.with_suffix('.verification.json').write_text(json.dumps(p,indent=2));print('VERIFIED',output.name,p['format']['duration'],output.stat().st_size,flush=True)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--part',type=int,required=True);ap.add_argument('--prepare',action='store_true');ap.add_argument('--upload',action='store_true');ap.add_argument('--jobs',type=int,default=2);a=ap.parse_args();p=json.load(open(R/'plan.json'));spec=p['parts'][a.part];shots=p['shots'][spec['first']:spec['last']];assets=prepare(p,shots) if a.prepare else {x['key']:x for x in p['assets']};output=R/f'picture_{a.part:02}.mp4';render(p,shots,assets,output,a.jobs)
 if a.upload:
  stage=json.load(open(R/'transfer.json'));response=output.with_suffix('.upload.json');command(['curl','--fail-with-body','--retry','3','-X','POST','-H','Content-Type: video/mp4','--data-binary','@'+str(output),stage['picture_base']+'/'+output.name,'-o',str(response)],R/'logs'/('upload-'+output.stem+'.log'));d=json.load(open(response));assert d['file']['bytes']==output.stat().st_size;print('TRANSFERRED',output.name,d['file']['sha256'],flush=True)
if __name__=='__main__':main()
