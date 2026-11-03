"""Geographic globe and regional maps using Natural Earth public-domain polygons."""
import math
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
BG='#F2F3F0';COLORS={'South Korea':'#28608C','North Korea':'#B1353D'}
def render_map(r,s,t):
 return globe(r,s,t) if s['asset_id']=='map-globe' else region(r,s,t)
def footer(r,im):r.painter.text(im,'Картографія: Natural Earth · Public domain',(800,1043,1030,28),18,'muted',align='right')
def rings(r):
 for f in r.geo['features']:
  g=f['geometry'];ps=g['coordinates'] if g['type']=='MultiPolygon' else[g['coordinates']]
  for p in ps:yield f['properties'].get('ADMIN',''),np.asarray(p[0],float)
def region(r,s,t):
 im=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im);x0,x1,y0,y1=117,136,31,44;scale=min(1470/((x1-x0)*.8),720/(y1-y0));cx=(x0+x1)/2;cy=(y0+y1)/2
 def proj(v):return(960+(v[0]-cx)*.8*scale,560-(v[1]-cy)*scale)
 for country,ring in rings(r):
  if not np.any((ring[:,0]>x0-4)&(ring[:,0]<x1+4)&(ring[:,1]>y0-4)&(ring[:,1]<y1+4)):continue
  color=COLORS.get(country,'#D9DFD9');d.polygon([proj(v) for v in ring],fill=color,outline=BG,width=3)
 r.painter.text(im,s.get('title','КОРЕЙСЬКИЙ ПІВОСТРІВ'),(90,72,1740,100),62,bold=True)
 for title,xy,country,box in [('КНДР',(126.4,40.0),'KP',(190,260,650,85)),('ПІВДЕННА КОРЕЯ',(127.6,35.8),'KR',(1160,750,680,120))]:
  p=proj(xy);d.line((p[0],p[1],box[0]+(530 if country=='KP' else 30),box[1]+45),fill=COLORS['North Korea' if country=='KP' else 'South Korea'],width=3);r.flag_at(im,country,box[0],box[1],90,60);r.painter.text(im,title,(box[0]+115,box[1]-2,box[2]-115,box[3]),38,bold=True)
 for label,v,offset in [('Пхеньян',(125.7625,39.0392),(-260,-64)),('Сеул',(126.9780,37.5665),(30,5))]:
  x,y=proj(v);d.ellipse((x-7,y-7,x+7,y+7),fill='white',outline='#26342C',width=2);d.rounded_rectangle((x+offset[0]-8,y+offset[1],x+offset[0]+190,y+offset[1]+53),radius=8,fill=BG);r.painter.text(im,label,(x+offset[0],y+offset[1],240,60),32,bold=True)
 r.painter.text(im,'КИТАЙ',(170,200,400,65),30,'muted');r.painter.text(im,'ЯПОНІЯ',(1470,380,300,65),30,'muted');footer(r,im);return im

def globe(r,s,t):
 progress=max(0,min(1,t/1.2));lon0=math.radians(113+12*(1-(1-progress)**3));lat0=math.radians(25);R=370;cx,cy=650,555
 if not hasattr(r,'_globe_base'):
  im=Image.new('RGB',(1920,1080),BG);shadow=Image.new('RGBA',im.size);sd=ImageDraw.Draw(shadow);sd.ellipse((cx-R+35,cy+R-18,cx+R+60,cy+R+44),fill=(25,39,32,45));shadow=shadow.filter(ImageFilter.GaussianBlur(26));im.paste(shadow,(0,0),shadow)
  yy,xx=np.mgrid[-R:R+1,-R:R+1];X=xx/R;Y=-yy/R;z=np.sqrt(np.maximum(0,1-X*X-Y*Y));mask=X*X+Y*Y<=1;shade=np.clip(.67+.26*z-.12*X+.13*Y,.35,1.1);color=np.clip(np.array([185,205,217])[None,None,:]*shade[:,:,None],0,255).astype(np.uint8);rgba=np.concatenate([color,(mask*255).astype(np.uint8)[:,:,None]],axis=2);disc=Image.fromarray(rgba);im.paste(disc,(cx-R,cy-R),disc);r._globe_base=im
 im=r._globe_base.copy();d=ImageDraw.Draw(im)
 def xyz(ring):
  lon=np.radians(ring[:,0])-lon0;lat=np.radians(ring[:,1]);c=np.cos(lat);return np.stack([c*np.sin(lon),np.cos(lat0)*np.sin(lat)-np.sin(lat0)*c*np.cos(lon),np.sin(lat0)*np.sin(lat)+np.cos(lat0)*c*np.cos(lon)],axis=1)
 def clip(points):
  out=[]
  for j,b in enumerate(points):
   a=points[j-1];inside_a=a[2]>=0;inside_b=b[2]>=0
   if inside_a!=inside_b:
    u=a[2]/(a[2]-b[2]);out.append(a+(b-a)*u)
   if inside_b:out.append(b)
  return np.asarray(out)
 for country,ring in rings(r):
  v=xyz(ring)
  if v[:,2].max()<0:continue
  v=clip(v)
  if len(v)<3:continue
  shade=np.clip(.68+.25*np.mean(v[:,2])-.08*np.mean(v[:,0])+.1*np.mean(v[:,1]),.5,1.1);base=COLORS.get(country,'#D6DDD5');rgb=tuple(int(base.lstrip('#')[i:i+2],16) for i in (0,2,4));color=tuple(min(255,int(q*shade)) for q in rgb);d.polygon([(cx+R*q[0],cy-R*q[1]) for q in v],fill=color,outline='#B3C3BB',width=1)
 r.painter.text(im,s.get('title','ОДИН ПІВОСТРІВ · ДВІ ДЕРЖАВИ'),(90,70,1740,104),60,bold=True)
 for country,coord,label,y in [('KP',(126.4,40),'КНДР',370),('KR',(127.5,36),'ПІВДЕННА\nКОРЕЯ',650)]:
  q=xyz(np.asarray([coord]))[0];x,yy=cx+R*q[0],cy-R*q[1];color=COLORS['North Korea' if country=='KP' else 'South Korea'];d.ellipse((x-5,yy-5,x+5,yy+5),fill='white',outline=color,width=2);d.line((x+8,yy,1100,y+35),fill=color,width=3);r.flag_at(im,country,1120,y,105,70);r.painter.text(im,label,(1260,y-6,570,160),50,bold=True)
 r.painter.text(im,'СХІДНА АЗІЯ',(300,976,700,55),27,'muted',align='center');footer(r,im);return im
