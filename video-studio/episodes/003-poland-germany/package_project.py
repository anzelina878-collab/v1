"""Self-contained source ZIP; no symlinks, caches or unrelated previous episodes."""
import argparse,json,zipfile,hashlib
from pathlib import Path
BASE=Path(__file__).resolve().parent;STUDIO=BASE.parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);ap.add_argument('--reports',type=Path,default=BASE/'output');args=ap.parse_args();args.output.parent.mkdir(parents=True,exist_ok=True)
 members={}
 def add(file,relative=None):
  if file.is_file():members[str(relative or Path('video-studio')/file.relative_to(STUDIO))]=file
 def tree(folder):
  for f in folder.rglob('*'):
   if f.is_file() and '__pycache__' not in f.parts and f.suffix not in ['.pyc','.log']:add(f)
 for name in ['studio','fonts']:tree(STUDIO/name)
 for name in ['README.md','LICENSE','requirements.txt']:add(STUDIO/name)
 for name in ['software_turntable.py','export_mesh.py','blender_turntable.py']:add(STUDIO/'tools'/name)
 for f in BASE.iterdir():
  if f.is_file() and f.suffix in ['.py','.json','.md','.txt']:add(f)
 for name in ['inputs','alignment','tools']:
  for f in (BASE/name).rglob('*'):
   if f.is_file() and not f.is_symlink() and '__pycache__' not in f.parts and f.suffix!='.pyc':add(f)
 add(BASE/'audio/voice.mp3');add(BASE/'assets/manifest.json');tree(BASE/'assets/maps')
 manifest=json.loads((BASE/'assets/manifest.json').read_text())
 for a in manifest:
  for field in ['photo','video']:
   if a.get(field):add(BASE/a[field])
  for folder in ['metadata','video-meta']:
   for f in (BASE/'assets'/folder).glob(a['id']+'.*'):add(f)
  if a.get('visual_origin')=='true_3d_render':tree(BASE/'assets/models'/a['id'].removeprefix('model-'))
 for f in args.reports.iterdir():
  if f.is_file() and f.suffix in ['.json','.jpg','.txt','.md','.progress','.log']:add(f,Path('video-studio/episodes')/BASE.name/'output'/f.name)
 with zipfile.ZipFile(args.output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3) as z:
  for arc,file in sorted(members.items()):z.write(file,arc)
 with zipfile.ZipFile(args.output) as z:
  assert z.testzip() is None
  for a in manifest:
   for field in ['photo','video']:
    if a.get(field):assert str(Path('video-studio/episodes')/BASE.name/a[field]) in z.namelist()
  voice=z.read(str(Path('video-studio/episodes')/BASE.name/'audio/voice.mp3'));assert hashlib.sha256(voice).digest()==hashlib.sha256((BASE/'audio/voice.mp3').read_bytes()).digest()
 print('ZIP_READY',args.output,len(members),args.output.stat().st_size,hashlib.sha256(args.output.read_bytes()).hexdigest(),flush=True)
if __name__=='__main__':main()
