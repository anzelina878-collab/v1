"""Restore source selections and render original 3D scenes. Requires ffmpeg and Blender."""
import pathlib,json,urllib.request,subprocess,urllib.parse
R=pathlib.Path(__file__).resolve().parent;plan=json.load(open(R/'plan.json'));(R/'assets').mkdir(exist_ok=True)
rendered=set()
for a in plan['assets']:
 target=R/'assets'/(a['key']+'.mp4')
 if target.exists():continue
 if a.get('kind')=='3d_explainer':
  mode=a['scene']
  if mode not in rendered:
   subprocess.run(['blender','-b','-t','4','-P',str(R/'make3d.py'),'--',mode],check=True);rendered.add(mode)
  subprocess.run(['ffmpeg','-y','-framerate','25/2','-i',str(R/'3d'/mode/'frame_%04d.jpg'),'-vf','minterpolate=fps=25:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1','-t','7.84','-an','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',str(target)],check=True)
 else:
  raw=target.with_suffix('.source');url=a['url']
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'CosmosVideoProduction/1.0'}),timeout=120) as response,open(raw,'wb') as output:
   while b:=response.read(1024*1024):output.write(b)
  if 'source_in' in a:
   subprocess.run(['ffmpeg','-y','-ss',str(a['source_in']),'-i',str(raw),'-t',str(a['duration']),'-an','-vf','scale=min(1920\\,iw):-2','-c:v','libx264','-preset','veryfast','-crf','22',str(target)],check=True);raw.unlink()
  else:raw.replace(target)
 a['path']=str(target)
(R/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
