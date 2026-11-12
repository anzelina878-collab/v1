"""Restore source excerpts and render original 3D scenes. Requires ffmpeg and Blender 4.x."""
import pathlib,json,urllib.request,subprocess
R=pathlib.Path(__file__).resolve().parent;plan=json.load(open(R/'plan.json'));A=R/'assets';A.mkdir(exist_ok=True)
def ff(args):subprocess.run(['ffmpeg','-y','-v','warning']+args,check=True)
def generate(mode):
 target=A/('explain_'+mode+'.mp4')
 if target.exists():return target
 if mode=='crunch':
  original=generate('expansion');ff(['-i',str(original),'-vf','reverse','-an','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',str(target)]);return target
 subprocess.run(['blender','-b','-t','4','-P',str(R/'make3d.py'),'--',mode],check=True)
 ff(['-framerate','25/2','-i',str(R/'3d'/mode/'frame_%04d.jpg'),'-vf','framerate=fps=25','-t','7.84','-an','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',str(target)]);return target
for a in plan['assets']:
 target=A/(a['key']+'.mp4')
 if not target.exists():
  if a.get('kind')=='3d_explainer':generate(a['scene'])
  else:
   raw=target.with_suffix('.source')
   with urllib.request.urlopen(urllib.request.Request(a['url'],headers={'User-Agent':'CosmosVideoProduction/1.0'}),timeout=120) as response,open(raw,'wb') as output:
    while b:=response.read(1024*1024):output.write(b)
   if 'source_in' in a:
    ff(['-ss',str(a['source_in']),'-i',str(raw),'-t',str(a['duration']),'-an','-vf',r'scale=min(1920\,iw):-2','-c:v','libx264','-preset','veryfast','-crf','22',str(target)]);raw.unlink()
   else:raw.replace(target)
 a['path']=str(target)
(R/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
