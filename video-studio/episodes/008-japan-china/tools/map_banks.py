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
 tex=np.asarray(texture).astype(float);tex=np.uint8(np.clip(tex*np.array([.79,.86,.91])+np.array([3,7,12]),0,255))
 dem=np.zeros((768,1024,3),np.float32)
 for x in range(4):
  for y in range(3):dem[y*256:(y+1)*256,x*256:(x+1)*256]=np.asarray(Image.open(ROOT/f'dem/4-{x+11}-{y+5}.png').convert('RGB'))
 dem=dem[:,:,0]*256+dem[:,:,1]+dem[:,:,2]/256-32768
 def height(lon,lat):
  xx=(np.asarray(lon)+180)/360*16*256-11*256;yy=(1-np.arcsinh(np.tan(np.radians(lat)))/np.pi)/2*16*256-5*256
  return dem[np.clip(yy.astype(int),0,767),np.clip(xx.astype(int),0,1023)]
 lon,lat=np.meshgrid(np.linspace(75,153,236),np.linspace(15,55,201));X=(lon-114)*.82;Y=lat-35;z=np.maximum(0,height(lon,lat))/111000*20-(X*X+Y*Y)/700
 points=np.stack([X,Y,z],axis=-1);dx=np.gradient(z,axis=1)/(78/235*.82);dy=np.gradient(z,axis=0)/(40/200);norm=np.stack([-dx,-dy,np.ones_like(z)],axis=-1);norm/=np.linalg.norm(norm,axis=-1)[:,:,None]
 uv=np.stack([(lon-75)/78,(lat-15)/40],axis=-1);idx=np.arange(points.shape[0]*points.shape[1]).reshape(points.shape[:2]);tris=np.concatenate([np.stack([idx[:-1,:-1],idx[:-1,1:],idx[1:,:-1]],-1).reshape(-1,3),np.stack([idx[:-1,1:],idx[1:,1:],idx[1:,:-1]],-1).reshape(-1,3)])
 pos=points.reshape(-1,3)[tris].astype(np.float32);nr=norm.reshape(-1,3)[tris].astype(np.float32);uv=uv.reshape(-1,2)[tris].astype(np.float32)
 geo=json.loads((ROOT/'europe.geojson').read_text());polys=[]
 for f in geo['features']:
  country=f['properties'].get('ADMIN');g=f['geometry'];p=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
  if country not in ['China','Japan','Taiwan','South Korea','North Korea','Russia','Mongolia','Vietnam','Philippines']:continue
  for poly in p:
   r=np.asarray(poly[0]);r=r[(r[:,0]>75)&(r[:,0]<153)&(r[:,1]>15)&(r[:,1]<55)]
   if len(r)>2:
    x=(r[:,0]-114)*.82;y=r[:,1]-35;zz=np.maximum(0,height(r[:,0],r[:,1]))/111000*20-(x*x+y*y)/700+.04;polys.append((country,np.stack([x,y,zz],-1)))

 return pos,nr,uv,tex[None],polys,height

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--kind',choices=['region','north','navy'],default='region');ap.add_argument('--duration',type=float,default=24);ap.add_argument('--preview',action='store_true');a=ap.parse_args();pos,nr,uv,tex,polys,height=load();out=ROOT/f'map-{a.kind}.mp4';temporary=ROOT/f'map-{a.kind}.rendering.mp4'
 focuses={'region':(119,35,63),'north':(127,32,35),'navy':(127,32,35)};lon0,lat0,span=focuses[a.kind];center=np.array([(lon0-114)*.82,lat0-35,0],np.float32)
 bg=Image.new('RGB',(W,H),'#081722');d=ImageDraw.Draw(bg)
 for y in range(0,H,90):d.line((0,y,W,y),fill='#0C202C')
 for x in range(0,W,90):d.line((x,0,x,H),fill='#0C202C')
 count=1 if a.preview else round(a.duration*30)
 if not a.preview:p=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','19','-threads','1','-pix_fmt','yuv420p','-movflags','+faststart',str(temporary)],stdin=subprocess.PIPE)
 font=ImageFont.truetype(str(FONT),27);small=ImageFont.truetype(str(FONT),15)
 for i in range(count):
  t=.5 if a.preview else i/max(1,count-1);angle=math.radians(-18+30*(t*t*(3-2*t)));elev=math.radians(49+5*math.sin(t*math.pi));forward=unit(np.array([math.sin(angle)*math.cos(elev),-math.cos(angle)*math.cos(elev),math.sin(elev)],np.float32));right=unit(np.cross([0,0,1],forward));up=unit(np.cross(forward,right));basis=np.stack([right,up,forward]).astype(np.float32);scale=W/span*(1+.08*math.sin(t*math.pi));cx,cy=W*.5,H*.49
  def project(v):
   q=(v-center)@basis.T;q[...,0]=q[...,0]*scale+cx;q[...,1]=-q[...,1]*scale+cy;return q
  q=project(pos);n=nr@basis.T;rgba=raster(q,n,uv,tex,np.zeros(len(pos),np.int32),W,H);im=bg.copy();im.paste(Image.fromarray(rgba),(0,0),Image.fromarray(rgba[:,:,3]));overlay=Image.new('RGBA',(W,H));od=ImageDraw.Draw(overlay)
  for country,r in polys:
   q=project(r);coords=[tuple(x[:2]) for x in q]
   if country in ['Japan','China']:
    color=(48,196,255,240) if country=='Japan' else (247,179,74,240);od.polygon(coords,fill=(*color[:3],30));
    od.line(coords+[coords[0]],fill=color,width=3)
   else:od.line(coords,fill=(225,235,229,65),width=1)
  glow=overlay.filter(ImageFilter.GaussianBlur(6));im=Image.alpha_composite(im.convert('RGBA'),glow);im=Image.alpha_composite(im,overlay);d=ImageDraw.Draw(im)
  labels=[('КИТАЙ',109,34,'#F7B34A',(-50,-15)),('ЯПОНІЯ',138,37,'#30C4FF',(10,-20))]
  if a.kind in ['north','navy']:labels=[('КИТАЙ',118,30,'#F7B34A',(-70,-25)),('ЯПОНІЯ',136,35,'#30C4FF',(15,-15)),('СЕНКАКУ / ДЯОЮЙДАО',123.47,25.75,'#E7EAE7',(-90,25))]
  for label,lon,lat,col,off in labels:
   x=(lon-114)*.82;y=lat-35;z=max(0,float(height(np.asarray(lon),np.asarray(lat))))/111000*20-(x*x+y*y)/700+.1;q=project(np.array([x,y,z]));xx,yy=q[:2]
   if not (30<xx<W-30 and 60<yy<H-70):continue
   bx=xx+off[0];by=yy+off[1];textfont=small if ('МОРЕ' in label or 'ОКЕАН' in label or label=='СЕНКАКУ / ДЯОЮЙДАО') else font;bounds=d.textbbox((0,0),label,font=textfont);ww=bounds[2]+20;hh=bounds[3]+14;d.line((xx,yy,bx+ww/2,by-20),fill=col,width=2);d.ellipse((xx-4,yy-4,xx+4,yy+5),fill=col);d.rounded_rectangle((bx,by-25,bx+ww,by-25+hh),radius=5,fill='#081722');d.text((bx+11,by-23),label,font=textfont,fill=col)

  if a.preview:im.convert('RGB').save(ROOT/f'preview-{a.kind}.jpg',quality=94)
  else:p.stdin.write(im.convert('RGB').tobytes())
  if i%90==0:print(a.kind,i,count,flush=True)
 if not a.preview:
  p.stdin.close();assert p.wait()==0;temporary.replace(out);(ROOT/f'map-{a.kind}.3d.json').write_text(json.dumps(dict(kind='true_3d_terrain',fps=30,frames=count,camera='continuous smooth 30 degree eased orbit with camera tilt and real East Asian relief',elevation_exaggeration=20,source='Mapzen terrain / NASA-USGS and Natural Earth texture',no_military_positions=True),indent=2))
if __name__=='__main__':main()
