"""Original national-flag drawings used by the episode renderer."""
from pathlib import Path
from PIL import Image,ImageDraw
import math
ROOT=Path(__file__).resolve().parents[1]/'assets/flags';ROOT.mkdir(parents=True,exist_ok=True)
im=Image.new('RGBA',(450,300),'white');d=ImageDraw.Draw(im);d.rectangle((0,0,450,99),fill='#FF9933');d.rectangle((0,200,450,300),fill='#138808');cx,cy,r=225,150,42;d.ellipse((cx-r,cy-r,cx+r,cy+r),outline='#000080',width=4);d.ellipse((cx-5,cy-5,cx+5,cy+5),fill='#000080')
for i in range(24):
 a=i*math.pi/12;d.line((cx,cy,cx+r*math.cos(a),cy+r*math.sin(a)),fill='#000080',width=2)
im.save(ROOT/'in-flag.png')
im=Image.new('RGBA',(450,300),'#01411C');d=ImageDraw.Draw(im);d.rectangle((0,0,111,300),fill='white');d.ellipse((184,70,344,230),fill='white');d.ellipse((211,48,365,202),fill='#01411C');pts=[]
for i in range(10):
 a=-math.pi/2+i*math.pi/5;rr=35 if i%2==0 else 14;pts.append((315+rr*math.cos(a),112+rr*math.sin(a)))
d.polygon(pts,fill='white');im.save(ROOT/'pk-flag.png')
