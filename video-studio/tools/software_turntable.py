"""True 3D CPU triangle rasterizer for constrained, headless environments.

It projects actual imported mesh geometry and UV textures for each angle.
It never rotates/warps a flat photograph. Lighting is an editorial studio
approximation, not a physically based Cycles render.
Requires numpy + numba + Pillow; the final encode uses FFmpeg.
"""
import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path
import numpy as np
from numba import njit
from PIL import Image,ImageFilter


@njit(cache=True)
def raster(projected, normals, uv, textures, material_ids, width, height):
    output=np.zeros((height,width,4),np.uint8)
    depth=np.full((height,width),-1e20,np.float32)
    for k in range(len(projected)):
        texture=textures[material_ids[k]]
        p=projected[k]
        x0,y0,z0=p[0];x1,y1,z1=p[1];x2,y2,z2=p[2]
        den=(y1-y2)*(x0-x2)+(x2-x1)*(y0-y2)
        if abs(den)<1e-6:continue
        xmin=max(0,int(math.floor(min(x0,x1,x2))));xmax=min(width-1,int(math.ceil(max(x0,x1,x2))))
        ymin=max(0,int(math.floor(min(y0,y1,y2))));ymax=min(height-1,int(math.ceil(max(y0,y1,y2))))
        for y in range(ymin,ymax+1):
            for x in range(xmin,xmax+1):
                a=((y1-y2)*(x+.5-x2)+(x2-x1)*(y+.5-y2))/den
                b=((y2-y0)*(x+.5-x2)+(x0-x2)*(y+.5-y2))/den
                c=1-a-b
                if a<0 or b<0 or c<0:continue
                z=a*z0+b*z1+c*z2
                if z<=depth[y,x]:continue
                depth[y,x]=z
                u=a*uv[k,0,0]+b*uv[k,1,0]+c*uv[k,2,0]
                v=a*uv[k,0,1]+b*uv[k,1,1]+c*uv[k,2,1]
                u=u%1.0;v=v%1.0
                tx=min(texture.shape[1]-1,max(0,int(u*(texture.shape[1]-1))))
                ty=min(texture.shape[0]-1,max(0,int((1-v)*(texture.shape[0]-1))))
                nx=a*normals[k,0,0]+b*normals[k,1,0]+c*normals[k,2,0]
                ny=a*normals[k,0,1]+b*normals[k,1,1]+c*normals[k,2,1]
                nz=a*normals[k,0,2]+b*normals[k,1,2]+c*normals[k,2,2]
                length=math.sqrt(nx*nx+ny*ny+nz*nz)+1e-8
                nx/=length;ny/=length;nz/=length
                key=max(0,nx*-.35+ny*-.6+nz*.72)
                fill=max(0,nx*.7+ny*.2+nz*.4)
                spec=max(0,nx*.1+ny*-.85+nz*.52)**28*.16
                shade=.58+key*.5+fill*.16
                for channel in range(3):
                    color=texture[ty,tx,channel]/255
                    output[y,x,channel]=min(255,int((color**2.2*shade+spec)**(1/2.2)*255))
                output[y,x,3]=255
    return output


def unit(v):return v/np.linalg.norm(v)


def geometry(data,angle,basis):
    c,s=math.cos(angle),math.sin(angle)
    rot=np.array([[c,-s,0],[s,c,0],[0,0,1]],np.float32)
    points=data['positions']@rot.T
    normals=data['normals']@rot.T
    return points,points@basis.T,normals


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--mesh',required=True);p.add_argument('--texture',required=True)
    p.add_argument('--output',required=True);p.add_argument('--duration',type=float,default=8)
    p.add_argument('--width',type=int,default=1920);p.add_argument('--height',type=int,default=1080)
    p.add_argument('--fps',type=int,default=30)
    p.add_argument('--yaw-start',type=float,default=-25);p.add_argument('--yaw-end',type=float,default=25)
    a=p.parse_args()
    if a.duration<=0 or not math.isfinite(a.duration):raise ValueError('Invalid duration')
    with np.load(a.mesh,allow_pickle=False) as archive:
        data={key:archive[key] for key in archive.files}
    if Path(a.texture).suffix=='.npz':textures=np.load(a.texture,allow_pickle=False)['textures']
    else:textures=np.asarray(Image.open(a.texture).convert('RGB'))[None]
    material_ids=data['material_ids'] if 'material_ids' in data else np.zeros(len(data['positions']),np.int32)
    output=Path(a.output).resolve();output.parent.mkdir(parents=True,exist_ok=True)
    forward=unit(np.array([4,-8,2.5],np.float32))
    right=unit(np.cross(np.array([0,0,1],np.float32),forward))
    up=unit(np.cross(forward,right))
    basis=np.stack([right,up,forward])
    low=np.full(3,1e8);high=-low
    for yaw in np.linspace(a.yaw_start,a.yaw_end,30):
        _,q,_=geometry(data,math.radians(yaw),basis)
        low=np.minimum(low,q.min(axis=(0,1)));high=np.maximum(high,q.max(axis=(0,1)))
    scale=min(a.width*.82/(high[0]-low[0]),a.height*.63/(high[1]-low[1]))
    center=(low+high)/2
    frames=round(a.duration*a.fps)
    cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{a.width}x{a.height}','-r',str(a.fps),'-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','18','-threads','2','-pix_fmt','yuv420p','-movflags','+faststart',str(output)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    for i in range(frames):
        yaw=math.radians(a.yaw_start+(a.yaw_end-a.yaw_start)*i/max(1,frames-1))
        world,q,n=geometry(data,yaw,basis)
        q[:,:,0]=(q[:,:,0]-center[0])*scale+a.width/2
        q[:,:,1]=-(q[:,:,1]-center[1])*scale+a.height*.42
        rgba=raster(q,n,data['uv'],textures,material_ids,a.width,a.height)
        im=Image.new('RGB',(a.width,a.height),'#F2F3F0')
        # Soft floor contact silhouette, computed from the rotated geometry.
        floor=world.copy();floor[:,:,2]=0
        projected=floor@basis.T
        projected[:,:,0]=(projected[:,:,0]-center[0])*scale+a.width/2
        projected[:,:,1]=-(projected[:,:,1]-center[1])*scale+a.height*.42
        from PIL import ImageDraw
        mask=Image.new('L',(a.width,a.height));draw=ImageDraw.Draw(mask)
        # A soft studio ground shadow; avoid a Python polygon per mesh triangle.
        # Convex silhouette is deliberately approximate, as is the studio lighting.
        sample=projected.reshape(-1,3)[::max(1,len(projected)*3//4000),:2]
        points=sorted(set(map(tuple,sample)))
        def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
        lower=[];upper=[]
        for point in points:
            while len(lower)>=2 and cross(lower[-2],lower[-1],point)<=0:lower.pop()
            lower.append(point)
        for point in reversed(points):
            while len(upper)>=2 and cross(upper[-2],upper[-1],point)<=0:upper.pop()
            upper.append(point)
        hull=lower[:-1]+upper[:-1]
        if len(hull)>=3:draw.polygon(hull,fill=40)
        mask=mask.filter(ImageFilter.GaussianBlur(a.width/100))
        im.paste(Image.new('RGB',im.size,'#4E554B'),(0,0),mask)
        object_image=Image.fromarray(rgba,'RGBA')
        im.paste(object_image,(0,0),object_image)
        proc.stdin.write(im.tobytes())
        if i%a.fps==0:print('3D_FRAME',i,'/',frames,flush=True)
    proc.stdin.close()
    if proc.wait():raise RuntimeError('FFmpeg failed')
    metadata={'motion_kind':'true_3d','renderer':'CPU UV-textured mesh rasterizer','lighting':'studio approximation','mesh_sha256':hashlib.sha256(Path(a.mesh).read_bytes()).hexdigest(),'frames':frames,'fps':a.fps,'yaw_start':a.yaw_start,'yaw_end':a.yaw_end,'width':a.width,'height':a.height,'identity_verified_by_renderer':False}
    output.with_suffix('.3d.json').write_text(json.dumps(metadata,indent=2))
    print('READY',output)


if __name__=='__main__':main()
