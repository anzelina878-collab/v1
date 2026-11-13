"""Bundle a standalone visual project: selected media, licensed fonts, script, voice and runtime.
Raw M249 geometry is intentionally excluded; its rendered native 360 bank is included.
"""
from pathlib import Path
import argparse,zipfile,json
BASE=Path(__file__).resolve().parent;STUDIO=BASE.parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.parent.mkdir(parents=True,exist_ok=True);files={}
 def addtree(root,arc):
  for f in sorted(root.rglob('*')):
   if f.is_file() and '__pycache__' not in f.parts and '.git' not in f.parts:files[str(Path(arc)/f.relative_to(root))]=f
 prefix='video-studio/episodes/001-usa-china-hi'
 for f in sorted(BASE.iterdir()):
  if f.is_file() and f.suffix in ['.py','.json','.md','.txt']:files[f'{prefix}/{f.name}']=f
 for name in ['input','inputs','audio','fonts','alignment','tools']:addtree(BASE/name,f'{prefix}/{name}')
 # Path.rglob does not descend symlink directories: resolve these explicitly.
 for name in ['source_photos','archive','models']:addtree((BASE/'assets'/name).resolve(),f'{prefix}/assets/{name}')
 for f in sorted((BASE/'assets').iterdir()):
  if f.is_file():files[f'{prefix}/assets/{f.name}']=f
 original=BASE.parent/'001-usa-china-2026'
 addtree(original/'assets/metadata',f'{prefix}/assets/photo_provenance');addtree(BASE/'assets/photo_provenance',f'{prefix}/assets/photo_provenance')
 addtree(original/'assets/originals',f'{prefix}/assets/photo_originals')
 for name in ['studio','tests','fonts']:addtree(STUDIO/name,f'video-studio/{name}')
 for name in ['render.py','README.md','FORMAT.md','HINDI_METADATA_GUIDE.md','HINDI_METADATA_EXAMPLES.json']:
  files[f'video-studio/{name}']=STUDIO/name
 if (BASE/'output/qa').exists():addtree(BASE/'output/qa',f'{prefix}/output/qa')
 for name in ['metadata.json','metadata.hi.txt','README.md','EDITORIAL_REVIEW.md','SOURCES.md']:
  if (BASE/name).is_file():files[f'{prefix}/{name}']=BASE/name
 files['README-HINDI.md']=BASE/'README.md'
 with zipfile.ZipFile(a.output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True) as z:
  for name,f in sorted(files.items()):z.write(f,name)
 with zipfile.ZipFile(a.output) as z:
  assert z.testzip() is None
  assert all(not (i.external_attr>>16 & 0o170000)==0o120000 for i in z.infolist())
 print('SOURCE_ZIP_READY',a.output,a.output.stat().st_size,'files',len(files),flush=True)
if __name__=='__main__':main()
