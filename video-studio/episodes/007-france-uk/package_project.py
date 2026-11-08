"""Portable source ZIP, with prepared assets, original inputs and native model data."""
from pathlib import Path
import argparse,json,zipfile,hashlib,stat
BASE=Path(__file__).resolve().parent;STUDIO=BASE.parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1048576):h.update(b)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);ap.add_argument('--reports',type=Path,default=BASE/'output/qa');args=ap.parse_args();members={}
 def add(p,arc=None):
  if p.is_file():members[str(arc or Path('video-studio')/p.relative_to(STUDIO))]=p
 def tree(folder):
  for p in folder.rglob('*'):
   if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.pyc','.nbc','.nbi']:add(p)
 for name in ['studio','fonts','tests']:tree(STUDIO/name)
 for name in ['README.md','LICENSE','requirements.txt','FORMAT.md','render.py']:add(STUDIO/name)
 for name in ['software_turntable.py','export_mesh.py','blender_turntable.py']:add(STUDIO/'tools'/name)
 for p in BASE.iterdir():
  if p.is_file() and p.suffix in ['.py','.md','.json','.txt']:add(p)
 for folder in ['input','inputs','alignment','tools','assets/metadata','assets/maps','assets/flags']:tree(BASE/folder)
 add(BASE/'audio/voiceover.mp3');add(BASE/'assets/manifest.json')
 manifest=json.loads((BASE/'assets/manifest.json').read_text())
 for a in manifest:
  for field in ['photo','video','original_photo']:
   if a.get(field):
    p=BASE/a[field];assert p.is_file(),p;add(p)
  if a['id'].startswith('model-'):tree(BASE/'assets/models'/a['id'].removeprefix('model-'))
  for folder in ['metadata','video-meta']:
   for p in (BASE/'assets'/folder).glob(a['id']+'.*'):add(p)
 if args.reports.exists():
  for p in args.reports.rglob('*'):
   if p.is_file() and p.suffix in ['.json','.jpg','.md','.txt','.log','.progress']:add(p,Path('video-studio/episodes')/BASE.name/'output/qa'/p.relative_to(args.reports))
 args.output.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(args.output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True) as z:
  for arc,p in sorted(members.items()):z.write(p,arc,compress_type=zipfile.ZIP_STORED if p.suffix.lower() in ['.mp4','.webm','.mp3','.jpg','.jpeg','.png','.npz','.zip'] else zipfile.ZIP_DEFLATED)
 with zipfile.ZipFile(args.output) as z:
  assert z.testzip() is None
  assert all(not stat.S_ISLNK(i.external_attr>>16) for i in z.infolist())
  names=set(z.namelist());prefix=Path('video-studio/episodes')/BASE.name
  for a in manifest:
   for field in ['photo','video','original_photo']:
    if a.get(field):assert str(prefix/a[field]) in names
  assert hashlib.sha256(z.read(str(prefix/'audio/voiceover.mp3'))).hexdigest()==sha(BASE/'audio/voiceover.mp3')
  assert hashlib.sha256(z.read(str(prefix/'input/script.uk.txt'))).hexdigest()==sha(BASE/'input/script.uk.txt')
 print('ZIP_READY',len(members),args.output.stat().st_size,sha(args.output),flush=True)
if __name__=='__main__':main()
