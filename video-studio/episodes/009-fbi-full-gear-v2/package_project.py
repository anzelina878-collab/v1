"""Portable sources: selected actual media, original voice, fonts, code and QA.
Adobe Mixamo raw/derived geometry is deliberately never included; rendered film banks are licensed.
"""
from pathlib import Path
import json,zipfile,argparse,hashlib,os
BASE=Path(__file__).resolve().parent;STUDIO=BASE.parents[1]
def members():
 out={};prefix='video-studio/episodes/'+BASE.name+'/'
 def add(f,name):
  if f.is_file():out[name]=f.resolve()
 for f in BASE.rglob('*'):
  rel=f.relative_to(BASE)
  if any(x in rel.parts for x in ['__pycache__','work','library','assets','fonts','audio','alignment']):continue
  if f.is_symlink() or not f.is_file():continue
  if rel.parts[0]=='output' and (len(rel.parts)<2 or rel.parts[1]!='qa' or rel.name=='public-downloads.json'):continue
  add(f,prefix+rel.as_posix())
 for rel in ['audio/voiceover.mp3','alignment/transcript.jsonl']:
  add(BASE/rel,prefix+rel)
 for f in (BASE/'fonts').glob('*.ttf'):add(f,prefix+'fonts/'+f.name)
 add(BASE/'assets/manifest.json',prefix+'assets/manifest.json')
 for a in json.load(open(BASE/'assets/manifest.json')):
  for field in ['video','photo']:
   if field in a:
    f=BASE/a[field];add(f,prefix+a[field])
    if f.with_suffix('.3d.json').is_file():add(f.with_suffix('.3d.json'),prefix+str(Path(a[field]).with_suffix('.3d.json')))
 for model in ['digital-carriers','m4a1']:
  for root,dirs,files in os.walk(BASE/'assets/models'/model,followlinks=True):
   for name in files:
    f=Path(root)/name
    if f.suffix=='.blend1':continue
    add(f,prefix+f.relative_to(BASE).as_posix())
 for folder in ['studio','fonts','tests']:
  for f in (STUDIO/folder).rglob('*'):
   if f.is_file() and '__pycache__' not in f.parts:add(f,'video-studio/'+f.relative_to(STUDIO).as_posix())
 for name in ['README.md','FORMAT.md','requirements.txt']:
  add(STUDIO/name,'video-studio/'+name)
 for name in ['software_turntable.py','export_mesh.py']:add(STUDIO/'tools'/name,'video-studio/tools/'+name)
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);ap.add_argument('--map',type=Path);args=ap.parse_args();mapping=members();args.output.parent.mkdir(parents=True,exist_ok=True)
 assert not any('restricted-model' in str(p) or 'Swat.glb' in str(p) or 'operator-mesh' in str(p) or 'operator-textures' in str(p) for p in mapping.values())
 with zipfile.ZipFile(args.output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3) as z:
  for name,f in sorted(mapping.items()):z.write(f,name,compress_type=zipfile.ZIP_STORED if f.suffix.lower() in ['.mp4','.mp3','.png','.jpg','.jpeg','.npz','.zip'] else zipfile.ZIP_DEFLATED)
 with zipfile.ZipFile(args.output) as z:
  assert z.testzip() is None
  for name,r in json.load(open(BASE/'INPUTS.json')).items():assert hashlib.sha256(z.read('video-studio/episodes/'+BASE.name+'/'+name)).hexdigest()==r['sha256']
 if args.map:args.map.write_text(json.dumps({k:str(v) for k,v in mapping.items()},ensure_ascii=False,indent=2)+'\n')
 print('SOURCE_ZIP_READY',len(mapping),args.output.stat().st_size,flush=True)
if __name__=='__main__':main()
