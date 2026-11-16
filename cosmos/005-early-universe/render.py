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
 assets={a['key']:a for a in plan['assets']};needed={s['asset'] for s in shots};(R/'assets').mkdir(exist_ok=True);(R/'logs').mkdir(exist_ok=True);
 # Source media is fetched from its original public publisher; no anonymous bundle links.
 (R/'fonts').mkdir(exist_ok=True)
 for name in ['Lato-Regular.ttf','Lato-Bold.ttf']:
  dest=R/'fonts'/name
  if not dest.exists():download('https://raw.githubusercontent.com/google/fonts/main/ofl/lato/'+name,dest)
 repo=os.environ.get('GH_REPO','anzelina878-collab/v1')
 def ensure(k):
  a=assets[k];dest=R/a['path']
  if dest.exists() and dest.stat().st_size>1000:return
  if a['kind']=='original3d':
   found=None
   for attempt in range(420):
    
    try:
     runs=json.loads(subprocess.check_output(['gh','api',f'repos/{repo}/actions/workflows/render-early-universe-3d.yml/runs?branch=cosmos-005-early-universe&per_page=5']))['workflow_runs']
     for run in runs:
      if run['conclusion']!='success':continue
      data=json.loads(subprocess.check_output(['gh','api',f"repos/{repo}/actions/runs/{run['id']}/artifacts"]));found=next((x for x in data['artifacts'] if x['name'].endswith('-'+a['scene']) and not x['expired']),None)
      if found:break
    except subprocess.CalledProcessError:
     time.sleep(min(20,2+attempt));continue
    if found:break
    time.sleep(10)
   if not found:raise RuntimeError('Missing 3D scene '+k)
   archive=R/(k+'.zip')
   for retry in range(5):
    try:
     with open(archive,'wb') as f:subprocess.run(['gh','api',f'repos/{repo}/actions/artifacts/{found["id"]}/zip'],stdout=f,check=True)
     if found.get('digest'):assert 'sha256:'+hashlib.sha256(archive.read_bytes()).hexdigest()==found['digest']
     break
    except (subprocess.CalledProcessError,AssertionError):
     if retry==4:raise
     time.sleep(3*(retry+1))
   folder=R/k
   with zipfile.ZipFile(archive) as z:z.extractall(folder)
   candidate=next(folder.rglob(a['scene']+'.mp4'),None)
   if candidate is None:raise RuntimeError('Incomplete original scene artifact '+k)
   shutil.copy(candidate,dest);archive.unlink()
  else:
   if 'source_in' in a:
    raw=dest.with_suffix('.source');download(a['url'],raw)
    command(['ffmpeg','-y','-v','warning','-ss',str(a['source_in']),'-i',str(raw),'-t',str(a['duration']),'-an','-map_metadata','-1','-c:v','libx264','-preset','veryfast','-crf','19','-threads','2',str(dest)],R/'logs'/(k+'-restore.log'));raw.unlink()
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
  a=assets[s['asset']];src=pathlib.Path(a['path']);src=src if src.is_absolute() else R/src;rawframes=s['frames']+s.get('handle',0);duration=rawframes/fps;vf=[];cmd=['ffmpeg','-y','-hide_banner','-loglevel','warning','-threads','1']
  if a['media']=='image':
   cmd+=['-loop','1','-i',str(src)]
   if a['width']/a['height']<1.5:
    vf+=['scale=1800:1000:force_original_aspect_ratio=decrease:flags=lanczos','pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0x030710']
   else:vf+=([f"crop={a['crop']}"] if a.get('crop') else [])+['scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos','crop=1920:1080']
   vf+=[f"zoompan=z='min({1.055+s.get('photo_variant',0)*.16},{1+s.get('photo_variant',0)*.16}+on*0.00012)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={rawframes}:s=1920x1080:fps={fps}"]
  else:
   cmd+=['-ss',str(s['in']),'-t',str(duration*s.get('rate',1)+.1),'-i',str(src)]
   vf+=([f"crop={a['crop']}"] if a.get('crop') else [])
   vf+=[f"setpts=(PTS-STARTPTS)/{s.get('rate',1)}"]+(['scale=1920:1080:force_original_aspect_ratio=decrease:flags=lanczos','pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black'] if a.get('contain') else ['scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos','crop=1920:1080'])+[f'fps={fps}']
  vf+=['tpad=stop_mode=clone:stop_duration=1','setsar=1','eq=contrast=1.01:saturation=1.015']
  if s['fade_in']:vf.append(f"fade=t=in:st=0:d={s['fade_in']}")
  if s['fade_out']:vf.append(f"fade=t=out:st={max(0,duration-s['fade_out'])}:d={s['fade_out']}")
  for j,l in enumerate(s.get('labels',[])):
   op=alpha(l['global_start'],l['global_end'],s['start_frame']/25);labelid=s['render_key']+f'-label{j}';size=l.get('size',48 if len(l['title'])>25 else 54)
   vf.append(draw(l['title'],regular,size,l.get('x',84),l.get('y',919),'0xF2F0E9',op,labelid+'-title'))
   if l.get('subtitle'):vf.append(draw(l['subtitle'],regular,28,87,984,'white@0.92',op,labelid+'-sub'))
  if s.get('credit'):vf.append(draw(s['credit'],regular,14,42,1048,'white@0.72',alpha(0,duration),s['render_key']+'-credit'))
  cmd+=['-vf',','.join(vf),'-frames:v',str(rawframes),'-an','-map_metadata','-1','-c:v','libx264','-preset','veryfast','-crf','20','-maxrate','6M','-bufsize','12M','-pix_fmt','yuv420p','-profile:v','high','-level','4.1','-g','50','-video_track_timescale','12800','-threads','1','-filter_threads','1',str(out)]
  command(cmd,logs/(s['render_key']+'.log'));assert int(next(x for x in probe(out)['streams'] if x['codec_type']=='video')['nb_frames'])==rawframes;print('SHOT',s['id'],s['asset'],round(duration,2),flush=True)
 with concurrent.futures.ThreadPoolExecutor(jobs) as ex:list(ex.map(one,shots))
 segments=[]
 for i,spec in enumerate(shots):
  raw=filename(spec);d=int(spec.get('dissolve',0)) if i else 0
  if d:
   prev=shots[i-1];join=cache/(spec['render_key']+'-dissolve.mp4')
   if not join.exists() or join.stat().st_size<1000:
    command(['ffmpeg','-y','-v','warning','-threads','1','-ss',str(prev['frames']/fps),'-i',str(filename(prev)),'-threads','1','-i',str(raw),'-filter_complex',f"[0:v]settb=1/25,setpts=PTS-STARTPTS,fps=25[a];[1:v]settb=1/25,setpts=PTS-STARTPTS,fps=25[b];[a][b]xfade=transition=fade:duration={(d-1)/fps}:offset=0,format=yuv420p[v]",'-map','[v]','-frames:v',str(d),'-an','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-filter_complex_threads','1','-video_track_timescale','12800',str(join)],logs/(join.stem+'.log'))
   assert int(probe(join)['streams'][0]['nb_frames'])==d;segments.append(join)
  if d or spec.get('handle',0):
   body=cache/(spec['render_key']+'-body.mp4')
   if not body.exists():
    command(['ffmpeg','-y','-v','warning','-threads','1','-ss',str(d/fps),'-i',str(raw),'-frames:v',str(spec['frames']-d),'-vf','setpts=PTS-STARTPTS','-an','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-filter_threads','1','-video_track_timescale','12800','-pix_fmt','yuv420p',str(body)],logs/(body.stem+'.log'))
   assert int(probe(body)['streams'][0]['nb_frames'])==spec['frames']-d;segments.append(body)
  else:segments.append(raw)
 listing=output.with_suffix('.concat.txt');listing.write_text(''.join("file '"+str(f)+"'\nduration "+str(int(probe(f)['streams'][0]['nb_frames'])/fps)+"\n" for f in segments));command(['ffmpeg','-y','-v','warning','-f','concat','-safe','0','-i',str(listing),'-map','0:v:0','-map_metadata','-1','-c:v','copy','-an','-movflags','+faststart',str(output)],logs/(output.stem+'-concat.log'))
 p=probe(output);v=next(x for x in p['streams'] if x['codec_type']=='video');assert int(v['nb_frames'])==sum(s['frames'] for s in shots);assert v['width']==1920 and v['height']==1080
 command(['ffmpeg','-v','error','-threads','2','-i',str(output),'-f','null','-'],logs/(output.stem+'-decode.log'));assert not (logs/(output.stem+'-decode.log')).read_text().strip();output.with_suffix('.verification.json').write_text(json.dumps(p,indent=2));print('VERIFIED',output.name,p['format']['duration'],output.stat().st_size,flush=True)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--part',type=int,required=True);ap.add_argument('--prepare',action='store_true');ap.add_argument('--jobs',type=int,default=2);a=ap.parse_args();p=json.load(open(R/'plan.json'));spec=p['parts'][a.part];shots=p['shots'][spec['first']:spec['last']];assets=prepare(p,shots) if a.prepare else {x['key']:x for x in p['assets']};output=R/f'picture_{a.part:02}.mp4';render(p,shots,assets,output,a.jobs)
if __name__=='__main__':main()
