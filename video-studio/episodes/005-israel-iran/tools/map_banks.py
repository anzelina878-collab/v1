"""Real 3D geographic terrain: public elevation mesh, texture and animated camera.
No strike trajectories, readiness values or fictional military positions.
"""
from pathlib import Path
import sys,json,math,subprocess,argparse
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
BASE=Path(__file__).resolve().parents[1];STUDIO=BASE.parents[1];sys.path.insert(0,str(STUDIO/'tools'))
from software_turntable import raster,unit
W,H=1280,720;ROOT=BASE/'assets/maps';FONT=STUDIO/'fonts/DejaVuSansCondensed-Bold.ttf'
def load():
 texture=Image.open(ROOT/'surface-region.png').convert('RGB')
 tex=np.asarray(texture).astype(float);tex=np.uint8(np.clip(tex*np.array([.68,.76,.77])+np.array([7,10,15]),0,255))
 dem=np.zeros((768,512,3),np.float32)
 for x in range(2):
  for y in range(3):dem[y*256:(y+1)*256,x*256:(x+1)*256]=np.asarray(Image.open(ROOT/f'dem/4-{x+9}-{y+5}.png').convert('RGB'))
 dem=dem[:,:,0]*256+dem[:,:,1]+dem[:,:,2]/256-32768
 def height(lon,lat):
  xx=(np.asarray(lon)+180)/360*16*256-9*256;yy=(1-np.arcsinh(np.tan(np.radians(lat)))/np.pi)/2*16*256-5*256
  return dem[np.clip(yy.astype(int),0,767),np.clip(xx.astype(int),0,511)]
 lon,lat=np.meshgrid(np.linspace(24,68,221),np.linspace(10,45,176));X=(lon-46)*.84;Y=lat-27.5;z=np.maximum(0,height(lon,lat))/111000*8-(X*X+Y*Y)/250
 points=np.stack([X,Y,z],axis=-1);dx=np.gradient(z,axis=1)/((68-24)/220*.84);dy=np.gradient(z,axis=0)/((45-10)/175);norm=np.stack([-dx,-dy,np.ones_like(z)],axis=-1);norm/=np.linalg.norm(norm,axis=-1)[:,:,None]
 uv=np.stack([(lon-24)/44,(lat-10)/35],axis=-1);idx=np.arange(points.shape[0]*points.shape[1]).reshape(points.shape[:2]);tris=np.concatenate([np.stack([idx[:-1,:-1],idx[:-1,1:],idx[1:,:-1]],-1).reshape(-1,3),np.stack([idx[:-1,1:],idx[1:,1:],idx[1:,:-1]],-1).reshape(-1,3)])
 pos=points.reshape(-1,3)[tris].astype(np.float32);nr=norm.reshape(-1,3)[tris].astype(np.float32);uv=uv.reshape(-1,2)[tris].astype(np.float32)
 geo=json.loads((ROOT/'europe.geojson').read_text());polys=[]
 for f in geo['features']:
  country=f['properties'].get('ADMIN');g=f['geometry'];p=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
  if country not in ['Israel','Iran','Iraq','Saudi Arabia','Jordan','Syria','Turkey','United Arab Emirates','Oman','Egypt','Lebanon']:continue
  for poly in p:
   r=np.asarray(poly[0]);r=r[(r[:,0]>24)&(r[:,0]<68)&(r[:,1]>10)&(r[:,1]<45)]
   if len(r)>2:
    x=(r[:,0]-46)*.84;y=r[:,1]-27.5;zz=np.maximum(0,height(r[:,0],r[:,1]))/111000*8-(x*x+y*y)/250+.04;polys.append((country,np.stack([x,y,zz],-1)))
 return pos,nr,uv,tex[None],polys,height

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--kind',choices=['region','israel','iran','navy'],default='region');ap.add_argument('--duration',type=float,default=24);ap.add_argument('--preview',action='store_true');a=ap.parse_args();pos,nr,uv,tex,polys,height=load();out=ROOT/f'map-{a.kind}.mp4'
 focuses={'region':(45,31,31),'israel':(36,31.5,15),'iran':(53,32,23),'navy':(50,24.5,24)};lon0,lat0,span=focuses[a.kind];center=np.array([(lon0-46)*.84,lat0-27.5,0],np.float32)
 bg=Image.new('RGB',(W,H),'#0C1720');d=ImageDraw.Draw(bg)
 for y in range(0,H,36):d.line((0,y,W,y),fill='#14232D')
 for x in range(0,W,36):d.line((x,0,x,H),fill='#14232D')
 count=1 if a.preview else round(a.duration*30)
 if not a.preview:p=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','19','-threads','1','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],stdin=subprocess.PIPE)
 font=ImageFont.truetype(str(FONT),27);small=ImageFont.truetype(str(FONT),15)
 for i in range(count):
  t=.5 if a.preview else i/max(1,count-1);angle=math.radians(-12+24*t);elev=math.radians(54+3*math.sin(t*math.pi));forward=unit(np.array([math.sin(angle)*math.cos(elev),-math.cos(angle)*math.cos(elev),math.sin(elev)],np.float32));right=unit(np.cross([0,0,1],forward));up=unit(np.cross(forward,right));basis=np.stack([right,up,forward]).astype(np.float32);scale=W/span*(1+.035*math.sin(t*math.pi));cx,cy=W*.5,H*.54
  def project(v):
   q=(v-center)@basis.T;q[...,0]=q[...,0]*scale+cx;q[...,1]=-q[...,1]*scale+cy;return q
  q=project(pos);n=nr@basis.T;rgba=raster(q,n,uv,tex,np.zeros(len(pos),np.int32),W,H);im=bg.copy();im.paste(Image.fromarray(rgba),(0,0),Image.fromarray(rgba[:,:,3]));overlay=Image.new('RGBA',(W,H));od=ImageDraw.Draw(overlay)
  for country,r in polys:
   q=project(r);coords=[tuple(x[:2]) for x in q]
   if country in ['Israel','Iran']:
    color=(48,196,255,240) if country=='Israel' else (247,179,74,240);od.polygon(coords,fill=(*color[:3],30));od.line(coords+[coords[0]],fill=color,width=3)
   else:od.line(coords,fill=(225,235,229,65),width=1)
  glow=overlay.filter(ImageFilter.GaussianBlur(6));im=Image.alpha_composite(im.convert('RGBA'),glow);im=Image.alpha_composite(im,overlay);d=ImageDraw.Draw(im)
  labels=[('ІЗРАЇЛЬ',35.05,31.45,'#30C4FF',(-100,0)),('ІРАН',54.1,32.6,'#F7B34A',(20,-4))]
  if a.kind=='navy':labels+=[('ПЕРСЬКА ЗАТОКА',51.5,26.5,'#D4E4EC',(-155,40)),('ОМАНСЬКА ЗАТОКА',58.5,24.0,'#D4E4EC',(-40,70))]
  for label,lon,lat,col,off in labels:
   x=(lon-46)*.84;y=lat-27.5;z=max(0,float(height(np.asarray(lon),np.asarray(lat))))/111000*8-(x*x+y*y)/250+.1;q=project(np.array([x,y,z]));xx,yy=q[:2]
   if not (30<xx<W-30 and 60<yy<H-70):continue
   bx=xx+off[0];by=yy+off[1];textfont=small if 'ЗАТОКА' in label else font;bounds=d.textbbox((0,0),label,font=textfont);ww=bounds[2]+20;hh=bounds[3]+14;d.line((xx,yy,bx+ww/2,by-20),fill=col,width=2);d.ellipse((xx-4,yy-4,xx+4,yy+4),fill=col);d.rounded_rectangle((bx,by-25,bx+ww,by-25+hh),radius=5,fill='#0C1720');d.text((bx+10,by-23),label,font=textfont,fill=col)
  d.text((36,30),'БЛИЗЬКИЙ СХІД' if a.kind!='navy' else 'ГЕОГРАФІЯ МОРСЬКИХ СИЛ',font=font,fill='#F3F4EF');d.text((36,H-30),'3D-рельєф · висота перебільшена для наочності',font=small,fill='#AEC0C8');d.text((625,H-30),'Natural Earth / Mapzen / NASA–USGS · Public domain',font=small,fill='#AEC0C8')
  if a.preview:im.convert('RGB').save(ROOT/f'preview-{a.kind}.jpg',quality=94)
  else:p.stdin.write(im.convert('RGB').tobytes())
  if i%90==0:print(a.kind,i,count,flush=True)
 if not a.preview:
  p.stdin.close();assert p.wait()==0;(ROOT/f'map-{a.kind}.3d.json').write_text(json.dumps(dict(kind='true_3d_terrain',fps=30,frames=count,camera='continuous smooth 24 degree orbit',elevation_exaggeration=8,source='Mapzen terrain / NASA-USGS and Natural Earth texture',no_military_positions=True),indent=2))
if __name__=='__main__':main()
