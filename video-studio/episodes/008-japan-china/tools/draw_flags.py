"""Original national-flag drawings used by the episode renderer."""
from pathlib import Path
from PIL import Image,ImageDraw
import math
ROOT=Path(__file__).resolve().parents[1]/'assets/flags';ROOT.mkdir(parents=True,exist_ok=True)
im=Image.new('RGBA',(450,300),'white');d=ImageDraw.Draw(im);d.ellipse((135,60,315,240),fill='#BC002D');im.save(ROOT/'jp-flag.png')
im=Image.new('RGBA',(450,300),'#DE2910');d=ImageDraw.Draw(im)
def star(cx,cy,r,angle):
 pts=[]
 for i in range(10):
  a=angle+i*math.pi/5;rr=r if i%2==0 else r*.382;pts.append((cx+rr*math.cos(a),cy+rr*math.sin(a)))
 d.polygon(pts,fill='#FFDE00')
star(75,75,45,-math.pi/2)
for x,y in [(150,30),(180,60),(180,105),(150,135)]:star(x,y,15,math.atan2(75-y,75-x))
im.save(ROOT/'cn-flag.png')
