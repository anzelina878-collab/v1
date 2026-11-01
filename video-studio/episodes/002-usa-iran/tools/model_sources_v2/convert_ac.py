"""AC3D -> actual world-space triangles and material textures; no photo warping."""
import json,re,shlex,sys,math
from pathlib import Path
import numpy as np
from PIL import Image

def convert(directory):
 directory=Path(directory);source=json.loads((directory/'source.json').read_text());text=(directory/'model.ac').read_text(errors='replace');lines=text.splitlines();materials=[]
 for line in lines:
  if line.startswith('MATERIAL '):
   a=shlex.split(line);i=a.index('rgb');j=a.index('trans');materials.append((a[1],list(map(float,a[i+1:i+4])),float(a[j+1])))
 i=next(n for n,l in enumerate(lines) if l.startswith('OBJECT '));nodes=[]
 def parse():
  nonlocal i
  node={'name':'','loc':np.zeros(3),'rot':np.eye(3),'texture':None,'verts':np.empty((0,3)),'faces':[],'kids':[]};i+=1
  while i<len(lines):
   line=lines[i].strip();i+=1
   if not line:continue
   a=shlex.split(line)
   if a[0]=='name':node['name']=a[1]
   elif a[0]=='loc':node['loc']=np.array(list(map(float,a[1:4])))
   elif a[0]=='rot':node['rot']=np.array(list(map(float,a[1:10]))).reshape(3,3)
   elif a[0]=='texture':node['texture']=a[1]
   elif a[0]=='numvert':
    n=int(a[1]);node['verts']=np.array([list(map(float,x.split()[:3])) for x in lines[i:i+n]]);i+=n
   elif a[0]=='numsurf':
    for _ in range(int(a[1])):
     mat=0;flags=0
     while i<len(lines):
      b=lines[i].strip().split();i+=1
      if not b:continue
      if b[0]=='SURF':flags=int(b[1],0)
      elif b[0]=='mat':mat=int(b[1])
      elif b[0]=='refs':
       n=int(b[1]);refs=[list(map(float,x.split()[:3])) for x in lines[i:i+n]];i+=n
       if flags&0xF==0 and n>=3:node['faces'].append((mat,refs))
       break
   elif a[0]=='kids':
    node['kids']=[parse() for _ in range(int(a[1]))];return node
  return node
 root=parse();positions=[];normals=[];uv=[];mids=[];texids={};textures=[];names=[]
 def texture(material,name):
  key=(material,name)
  if key in texids:return texids[key]
  matname,color,trans=materials[material] if material<len(materials) else ('default',[.5,.5,.5],0)
  filepath=source['texture_mapping'].get(name)
  if filepath and directory.name!='b2':
   im=Image.open(directory/filepath).convert('RGB').resize((512,512));arr=np.asarray(im).astype(np.float32)*np.array(color)
  else:
   color=np.array(color)
   if color.max()>.9:color=np.array([.30,.33,.35]) if directory.name in ['f14','f22','b2'] else np.array([.20,.25,.16])
   if directory.name=='b2':color=np.array([.16,.18,.20]) if color.max()>.1 else np.array([.035,.045,.05])
   if trans>.4:color=np.array([.045,.075,.09])
   arr=np.tile(color*255,(512,512,1))
  arr=np.uint8(np.clip(arr,0,255));texids[key]=len(textures);textures.append(arr);return len(textures)-1
 C=np.array([[1,0,0],[0,0,-1],[0,1,0]],float)
 def visit(node,parent):
  local=np.eye(4);local[:3,:3]=node['rot'];local[:3,3]=node['loc'];world=parent@local
  name=node['name'].lower()
  # Exclude visible FX meshes and simulation-only fixture helpers, never airframe parts.
  skip=any(w in name for w in ['afterburn','flame','flack','vapor','vapour','shadow','collision','bounding','halo','lgt-','strobe','convexhull','shockwave','vortex','reheat','gear-indexer'])
  if len(node['verts']) and not skip:
   verts=(node['verts']@world[:3,:3].T+world[:3,3])@C.T
   if directory.name=='f14' and np.max(np.abs(verts))>60:
    print('EXCLUDED_F14_SIMULATION_OBJECT',node['name'],verts.min(0),verts.max(0),flush=True)
    for kid in node['kids']:visit(kid,world)
    return
   names.append(node['name']);faces=[];uvs=[];ids=[]
   for mat,refs in node['faces']:
    if mat<len(materials) and materials[mat][2]>=.999:continue
    for k in range(1,len(refs)-1):
     ids.append(texture(mat,node['texture']));faces.append([int(refs[j][0]) for j in [0,k,k+1]]);uvs.append([refs[j][1:3] for j in [0,k,k+1]])
   if faces:
    f=np.asarray(faces,np.int32);pos=verts[f];normal=np.cross(pos[:,1]-pos[:,0],pos[:,2]-pos[:,0]);length=np.linalg.norm(normal,axis=1);normal/=np.maximum(length[:,None],1e-9);averaged=np.zeros_like(verts)
    for j in range(3):np.add.at(averaged,f[:,j],normal)
    averaged/=np.maximum(np.linalg.norm(averaged,axis=1)[:,None],1e-9)
    positions.append(pos);normals.append(averaged[f]);uv.append(np.asarray(uvs));mids.append(np.array(ids))
  for kid in node['kids']:visit(kid,world)
 visit(root,np.eye(4));pos=np.concatenate(positions).astype(np.float32);norm=np.concatenate(normals).astype(np.float32);lo=pos.min((0,1));hi=pos.max((0,1));center=(lo+hi)/2;center[2]=lo[2];pos=(pos-center)*3/max(hi-lo)
 np.savez_compressed(directory/'mesh.npz',positions=pos,normals=norm,uv=np.concatenate(uv).astype(np.float32),material_ids=np.concatenate(mids).astype(np.int32));np.savez_compressed(directory/'textures.npz',textures=np.array(textures))
 (directory/'conversion.json').write_text(json.dumps({'triangles':len(pos),'bounds_original':[lo.tolist(),hi.tolist()],'objects':names,'materials':len(textures),'coordinate_conversion':'AC3D Y-up to Z-up','modifications':'Omitted simulation FX; studio material approximation; source geometry and node transforms retained'},indent=2));print(directory.name,len(pos),len(textures),lo,hi,flush=True)
if __name__=='__main__':
 import os
 for d in Path(os.environ.get('ARSENAL_MODEL_ROOT',str(Path(__file__).resolve().parents[2]/'assets/models-v2'))).glob('*'):
  if (d/'source.json').exists():
   try:convert(d)
   except Exception as e:print('ERROR',d.name,repr(e),flush=True)
