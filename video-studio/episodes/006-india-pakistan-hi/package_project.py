"""Portable source bundle: actual media bytes, model sources, licenses, fonts and frozen timing."""
from pathlib import Path
import json,zipfile,argparse,hashlib,os
BASE=Path(__file__).resolve().parent;STUDIO=BASE.parents[1]
def members():
 out={}
 def add(f,name):
  if f.is_file():out[name]=f.resolve()
 prefix='video-studio/episodes/'+BASE.name+'/'
 for f in BASE.rglob('*'):
  rel=f.relative_to(BASE)
  if any(x in rel.parts for x in ['__pycache__','work','library']):continue
  if f.is_symlink() or not f.is_file():continue
  if rel.parts[0]=='output' and (len(rel.parts)<2 or rel.parts[1]!='qa' or rel.name=='public-downloads.json'):continue
  add(f,prefix+rel.as_posix())
 add(BASE/'audio/voiceover.mp3',prefix+'audio/voiceover.mp3')
 for directory,dirs,files in os.walk(BASE/'assets',followlinks=True):
  dirs[:]=[d for d in dirs if d!='__pycache__']
  for name in files:
   f=Path(directory)/name
   if 'channel-ident' in name:continue
   add(f,prefix+f.relative_to(BASE).as_posix())
 for directory in ['studio','fonts','tests']:
  for f in (STUDIO/directory).rglob('*'):
   if f.is_file() and '__pycache__' not in f.parts:add(f,'video-studio/'+f.relative_to(STUDIO).as_posix())
 for name in ['render.py','README.md','FORMAT.md','requirements.txt','HINDI_VOICE_STYLE.md','HINDI_METADATA_GUIDE.md','HINDI_METADATA_EXAMPLES.json']:
  add(STUDIO/name,'video-studio/'+name)
 # Source geometry bank regeneration helpers; not needed for ordinary render.
 for name in ['software_turntable.py','export_mesh.py']:
  add(STUDIO/'tools'/name,'video-studio/tools/'+name)
 return out

def main():
 a=argparse.ArgumentParser();a.add_argument('output',type=Path);a.add_argument('--map',type=Path);args=a.parse_args();mapping=members();args.output.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(args.output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3) as z:
  for name,f in sorted(mapping.items()):z.write(f,name,compress_type=zipfile.ZIP_STORED if f.suffix.lower() in ['.mp4','.mp3','.png','.jpg','.jpeg','.npz','.zip'] else zipfile.ZIP_DEFLATED)
 with zipfile.ZipFile(args.output) as z:
  assert z.testzip() is None
  for name,r in json.load(open(BASE/'INPUTS.json')).items():assert hashlib.sha256(z.read('video-studio/episodes/'+BASE.name+'/'+name)).hexdigest()==r['sha256']
 if args.map:args.map.write_text(json.dumps({k:str(v) for k,v in mapping.items()},ensure_ascii=False,indent=2)+'\n')
 print('SOURCE_ZIP_READY',len(mapping),args.output.stat().st_size,flush=True)
if __name__=='__main__':main()
