"""Prepare optional masks from immutable source photographs; review before selecting."""
from pathlib import Path
import os,json,argparse
os.environ.setdefault('OMP_NUM_THREADS','1')
from rembg import remove,new_session
from PIL import Image,ImageOps
import numpy as np
BASE=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('asset_ids',nargs='+');a=ap.parse_args();m={r['id']:r for r in json.loads((BASE/'assets/manifest.json').read_text())};session=new_session('isnet-general-use',providers=['CPUExecutionProvider'])
 for key in a.asset_ids:
  r=m[key];src=BASE/r.get('original_photo',r['photo']);im=ImageOps.contain(Image.open(src).convert('RGB'),(1400,1000));out=remove(im,session=session);alpha=np.asarray(out.getchannel('A'));yy,xx=np.where(alpha>70)
  if not len(xx):raise ValueError('No foreground: '+key)
  box=(max(0,int(xx.min())-12),max(0,int(yy.min())-12),min(im.width,int(xx.max())+13),min(im.height,int(yy.max())+13));dst=BASE/'assets/prepared'/f'{key}.png';dst.parent.mkdir(exist_ok=True,parents=True);out.crop(box).save(dst);print('Candidate only; inspect mask before using:',dst)
if __name__=='__main__':main()
