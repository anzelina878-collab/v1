from pathlib import Path
import os
os.environ['OMP_NUM_THREADS']='1';os.environ.setdefault('U2NET_HOME',str(Path.home()/'.u2net'))
from rembg import remove,new_session
from PIL import Image,ImageOps
from pathlib import Path
import numpy as np,json
root=Path(__file__).resolve().parents[1];session=new_session('isnet-general-use',providers=['CPUExecutionProvider'])
for key in ['rafale-india','rafale','j10','su30','jf17','arjun','vt4','shahpar','lch','type054','harop','apache-india','cobra-pak']:
 src=root/'assets/photos'/f'{key}.jpg';dst=root/'assets/prepared'/f'{key}.png'
 if not src.exists():continue
 im=Image.open(src).convert('RGB');im=ImageOps.contain(im,(1600,1200));out=remove(im,session=session);alpha=np.asarray(out.getchannel('A'));yy,xx=np.where(alpha>80)
 if not len(xx):continue
 out.crop((max(0,int(xx.min())-12),max(0,int(yy.min())-12),min(im.width,int(xx.max())+13),min(im.height,int(yy.max())+13))).save(dst)
 print('CUTOUT',key,flush=True)
