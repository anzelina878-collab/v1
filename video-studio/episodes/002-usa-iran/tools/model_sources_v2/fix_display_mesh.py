import numpy as np,json,math
from pathlib import Path
import os
p=Path(os.environ.get('ARSENAL_MODEL_ROOT',str(Path(__file__).resolve().parents[2]/'assets/models-v2')))
for key in ['blackhawk','apache']:
 root=p/key;body=dict(np.load(root/'mesh-airframe.npz'));texture=np.load(root/'textures-airframe.npz')['textures'];conv=json.loads((root/'conversion.json').read_text());lo,hi=np.array(conv['bounds_original']);center=(lo+hi)/2;center[2]=lo[2];bp=body['positions']*(hi-lo).max()/3+center
 # Display-pose blades complement the licensed airframe; no aerodynamic CAD is claimed.
 cx,cz,radius=(-3.047,1.65,8.0) if key=='blackhawk' else (-1.3,2.60,7.30)
 pp=[]
 for angle in [0,90,180,270]:
  a=math.radians(angle+20);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1.]])
  v=np.array([[.6,-.12,-.02],[radius,-.10,-.02],[radius,.16,-.02],[.6,.20,-.02],[.6,-.12,.02],[radius,-.10,.02],[radius,.16,.02],[.6,.20,.02]])@R.T+[cx,0,cz]
  for f in [(0,1,2),(0,2,3),(4,6,5),(4,7,6),(0,4,5),(0,5,1),(1,5,6),(1,6,2),(2,6,7),(2,7,3)]:pp.append(v[list(f)])
 rp=np.array(pp);rn=np.cross(rp[:,1]-rp[:,0],rp[:,2]-rp[:,0]);rn/=np.maximum(np.linalg.norm(rn,axis=1)[:,None],1e-8);rn=np.repeat(rn[:,None,:],3,axis=1)
 pos=np.concatenate([bp,rp]);lo=pos.min((0,1));hi=pos.max((0,1));c=(lo+hi)/2;c[2]=lo[2];pos=(pos-c)*3/(hi-lo).max();np.savez_compressed(root/'mesh.npz',positions=pos.astype(np.float32),normals=np.concatenate([body['normals'],rn]).astype(np.float32),uv=np.concatenate([body['uv'],np.zeros((len(rp),3,2),np.float32)]),material_ids=np.concatenate([body['material_ids'],np.full(len(rp),len(texture),np.int32)]));np.savez_compressed(root/'textures.npz',textures=np.concatenate([texture,np.tile(np.uint8([27,30,28]),(1,512,512,1))]));print('DISPLAY_ROTOR_FIXED',key)
# Neutral studio paint avoids implying that a generic Tomcat carries an Iranian or US livery.
root=p/'f14';a=np.load(root/'textures.npz')['textures'];means=a.mean((1,2));colors=np.where((means.max(1)>.18*255)[:,None],np.array([136,144,146]),np.array([24,30,33]));a[:]=colors[:,None,None,:].astype(np.uint8);np.savez_compressed(root/'textures.npz',textures=a)
