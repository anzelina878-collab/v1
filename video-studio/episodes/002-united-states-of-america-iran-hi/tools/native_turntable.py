"""Real UV-textured geometry, EGL/Mesa native poses; no optical flow or flat-photo warps."""
from pathlib import Path
import os,sys,argparse,json,math,subprocess,hashlib
os.environ.setdefault('LIBGL_ALWAYS_SOFTWARE','1');os.environ.setdefault('LP_NUM_THREADS','2')
import numpy as np
from PIL import Image
import moderngl

def unit(a):return a/np.linalg.norm(a)
def main():
 p=argparse.ArgumentParser();p.add_argument('--mesh',required=True);p.add_argument('--texture',required=True);p.add_argument('--output',required=True);p.add_argument('--duration',type=float,default=24);p.add_argument('--width',type=int,default=1280);p.add_argument('--height',type=int,default=720);p.add_argument('--fps',type=int,default=30);a=p.parse_args()
 d=dict(np.load(a.mesh));textures=np.load(a.texture)['textures'] if a.texture.endswith('.npz') else np.asarray(Image.open(a.texture).convert('RGB'))[None];positions=d['positions'].astype('f4');normals=d['normals'].astype('f4');uv=d['uv'].astype('f4');ids=d.get('material_ids',np.zeros(len(positions),np.int32));forward=unit(np.array([4,-8,2.5],np.float32));right=unit(np.cross([0,0,1],forward));up=unit(np.cross(forward,right));basis=np.stack([right,up,forward]).astype('f4')
 sample=positions.reshape(-1,3)[::max(1,len(positions)*3//3000)];lo=np.full(3,1e9);hi=-lo
 for angle in np.linspace(-45,315,72,endpoint=False):
  c,s=math.cos(math.radians(angle)),math.sin(math.radians(angle));r=np.array([[c,-s,0],[s,c,0],[0,0,1]],np.float32);q=sample@r.T@basis.T;lo=np.minimum(lo,q.min(0));hi=np.maximum(hi,q.max(0))
 scale=min(a.width*.80/(hi[0]-lo[0]),a.height*.62/(hi[1]-lo[1]));center=(lo+hi)/2
 ctx=moderngl.create_standalone_context(backend='egl');ctx.enable(moderngl.DEPTH_TEST);fbo=ctx.simple_framebuffer((a.width,a.height),components=3);fbo.use()
 vs='''#version 330
 in vec3 position;in vec3 normal;in vec2 uv;in float material;
 uniform mat3 basis;uniform float yaw;uniform vec3 center;uniform vec2 viewport;uniform float scale;uniform float depth_range;
 out vec3 N;out vec2 UV;flat out int MAT;
 void main(){float c=cos(yaw),s=sin(yaw);mat3 R=mat3(c,s,0,-s,c,0,0,0,1);vec3 world=R*position;vec3 q=basis*world;vec2 pix=vec2((q.x-center.x)*scale+viewport.x*.5,(q.y-center.y)*scale+viewport.y*.58);gl_Position=vec4(pix/viewport*2.-1.,-(q.z-center.z)/depth_range,1);N=R*normal;UV=vec2(fract(uv.x),1.-fract(uv.y));MAT=int(material+.1);}
 '''
 fs='''#version 330
 uniform sampler2DArray tex;in vec3 N;in vec2 UV;flat in int MAT;out vec4 color;
 void main(){vec3 n=normalize(N);vec3 base=texture(tex,vec3(UV,float(MAT))).rgb;float key=max(0.,dot(n,vec3(-.35,-.6,.72)));float fill=max(0.,dot(n,vec3(.7,.2,.4)));float spec=pow(max(0.,dot(n,vec3(.1,-.85,.52))),28.)*.10;vec3 lit=pow(pow(base,vec3(2.2))*(.60+key*.48+fill*.15)+vec3(spec),vec3(1./2.2));color=vec4(lit,1);}
 '''
 prog=ctx.program(vertex_shader=vs,fragment_shader=fs);verts=np.concatenate([positions.reshape(-1,3),normals.reshape(-1,3),uv.reshape(-1,2),np.repeat(ids,3)[:,None]],axis=1).astype('f4');vbo=ctx.buffer(verts.tobytes());vao=ctx.vertex_array(prog,[(vbo,'3f 3f 2f 1f','position','normal','uv','material')]);tex=ctx.texture_array((textures.shape[2],textures.shape[1],len(textures)),3,np.ascontiguousarray(textures[:,:,:,:3]).tobytes());tex.filter=(moderngl.LINEAR,moderngl.LINEAR);tex.use(0);prog['tex']=0;prog['basis'].write(basis.T.tobytes());prog['center'].value=tuple(center);prog['viewport'].value=(a.width,a.height);prog['scale']=scale;prog['depth_range']=float(max(hi[2]-lo[2],.1)*1.2)
 shadow=ctx.program(vertex_shader='''#version 330
 in vec2 p;void main(){gl_Position=vec4(p,0,1);}''',fragment_shader='''#version 330
 uniform vec2 center;uniform vec2 radii;out vec4 color;void main(){vec2 q=(gl_FragCoord.xy-center)/radii;float shade=exp(-2.8*dot(q,q))*.105;vec3 bg=vec3(242.,243.,240.)/255.;color=vec4(bg*(1.-shade),1);}''');quad=ctx.vertex_array(shadow,[(ctx.buffer(np.array([-1,-1,1,-1,-1,1,1,1],'f4').tobytes()),'2f','p')]);floor=sample.copy();floor[:,2]=positions[:,:,2].min()
 out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);frames=round(a.duration*a.fps);enc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{a.width}x{a.height}','-r',str(a.fps),'-i','pipe:0','-vf','vflip','-an','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],stdin=subprocess.PIPE)
 for i in range(frames):
  angle=math.radians(-45+360*i/frames);c,s=math.cos(angle),math.sin(angle);r=np.array([[c,-s,0],[s,c,0],[0,0,1]],np.float32);ground=floor@r.T@basis.T;mn=ground.min(0);mx=ground.max(0);sc=(mn+mx)/2;shadow['center'].value=((sc[0]-center[0])*scale+a.width*.5,(sc[1]-center[1])*scale+a.height*.58);shadow['radii'].value=(max(15.,(mx[0]-mn[0])*scale*.48),max(5.,(mx[1]-mn[1])*scale*.30));fbo.clear(242/255,243/255,240/255,depth=1);ctx.disable(moderngl.DEPTH_TEST);quad.render(moderngl.TRIANGLE_STRIP);ctx.enable(moderngl.DEPTH_TEST);prog['yaw']=angle;vao.render(moderngl.TRIANGLES);enc.stdin.write(fbo.read(components=3,alignment=1))
  if i%120==0:print('NATIVE_FRAME',i,frames,flush=True)
 enc.stdin.close();assert enc.wait()==0;out.with_suffix('.3d.json').write_text(json.dumps({'motion_kind':'true_3d','renderer':ctx.info['GL_RENDERER'],'native_frames':frames,'fps':a.fps,'duration':a.duration,'revolution_degrees':360,'rotation_degrees_per_second':360/a.duration,'mesh_sha256':hashlib.sha256(Path(a.mesh).read_bytes()).hexdigest(),'method':'Every pose rendered from actual licensed geometry; no temporal interpolation, tpad, or deformed photographs','loop_seam':'Endpoint excluded: constant angular step at cycle boundary'},indent=2));print('NATIVE_READY',out,flush=True)
if __name__=='__main__':main()
