"""Segment a real photo; requires visual review before selecting its output."""
import argparse,os
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('output',type=Path);p.add_argument('--model-dir',type=Path);a=p.parse_args()
 if a.model_dir:os.environ['U2NET_HOME']=str(a.model_dir)
 os.environ.setdefault('OMP_NUM_THREADS','2')
 from PIL import Image
 import numpy as np
 from rembg import remove,new_session
 im=Image.open(a.input).convert('RGB');out=remove(im,session=new_session('isnet-general-use',providers=['CPUExecutionProvider']));alpha=np.asarray(out.getchannel('A'));yy,xx=np.where(alpha>50)
 if not len(xx):raise ValueError('No foreground found; keep the intact source photo')
 margin=18;box=(max(0,int(xx.min())-margin),max(0,int(yy.min())-margin),min(out.width,int(xx.max())+margin+1),min(out.height,int(yy.max())+margin+1));a.output.parent.mkdir(parents=True,exist_ok=True);out.crop(box).save(a.output)
 print('Review the mask: vehicle shape, barrel, tracks, rotor blades and unwanted background. Reject inaccurate cutouts.')
if __name__=='__main__':main()
