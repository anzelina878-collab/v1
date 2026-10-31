"""Convert static GLB (including Draco) to rasterizer geometry + base-color material stack.

Requires numpy, Pillow and DracoPy. Preserves geometry and node transforms;
lighting/normal/metalness maps are not baked by this preview backend.
Use a PBR renderer when material fidelity is essential. Raw licensed models and
converted meshes must stay outside distributable projects unless licensed so.
"""
import argparse,io,json,math,struct
from pathlib import Path
import numpy as np
from PIL import Image


def matrix(node):
    if 'matrix' in node:return np.array(node['matrix']).reshape(4,4).T
    x,y,z,w=node.get('rotation',[0,0,0,1])
    r=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],
                [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],
                [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
    m=np.eye(4);m[:3,:3]=r@np.diag(node.get('scale',[1,1,1]));m[:3,3]=node.get('translation',[0,0,0]);return m


def main():
    import DracoPy
    p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('output');p.add_argument('--tile',type=int,default=512);a=p.parse_args()
    b=Path(a.source).read_bytes()
    if b[:4]!=b'glTF':raise ValueError('Expected GLB')
    length,kind=struct.unpack_from('<II',b,12);j=json.loads(b[20:20+length]);offset=20+length
    length,kind=struct.unpack_from('<II',b,offset);buf=b[offset+8:offset+8+length]
    def view(i):
        v=j['bufferViews'][i];start=v.get('byteOffset',0);return buf[start:start+v['byteLength']]
    def accessor(i):
        s=j['accessors'][i];v=j['bufferViews'][s['bufferView']]
        dtype={5120:'i1',5121:'u1',5122:'<i2',5123:'<u2',5125:'<u4',5126:'<f4'}[s['componentType']]
        cols={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[s['type']];dt=np.dtype(dtype)
        return np.ndarray((s['count'],cols),dtype=dt,buffer=buf,offset=v.get('byteOffset',0)+s.get('byteOffset',0),strides=(v.get('byteStride',dt.itemsize*cols),dt.itemsize))
    mats=j.get('materials',[]);side=math.ceil(math.sqrt(max(1,len(mats))))
    atlas=Image.new('RGB',(side*a.tile,side*a.tile),'#666666')
    for k,mat in enumerate(mats):
        pbr=mat.get('pbrMetallicRoughness',{});factor=np.array(pbr.get('baseColorFactor',[1,1,1,1])[:3])
        tex=pbr.get('baseColorTexture')
        if tex:
            image=j['images'][j['textures'][tex['index']]['source']]
            im=Image.open(io.BytesIO(view(image['bufferView']))).convert('RGB').resize((a.tile,a.tile))
            # glTF factors multiply in linear light.
            pixels=np.asarray(im)/255.;linear=np.where(pixels<=.04045,pixels/12.92,((pixels+.055)/1.055)**2.4)*factor
            pixels=np.where(linear<=.0031308,linear*12.92,1.055*linear**(1/2.4)-.055)
            im=Image.fromarray(np.uint8(np.clip(pixels,0,1)*255))
        else:
            srgb=np.where(factor<=.0031308,factor*12.92,1.055*factor**(1/2.4)-.055)
            im=Image.new('RGB',(a.tile,a.tile),tuple(np.uint8(np.clip(srgb,0,1)*255)))
        atlas.paste(im,((k%side)*a.tile,(k//side)*a.tile))
    pp=[];nn=[];tt=[];mm=[]
    # glTF Y-up -> rasterizer Z-up, preserving handedness.
    convert=np.array([[1,0,0],[0,0,-1],[0,1,0]])
    def visit(index,parent):
        node=j['nodes'][index];world=parent@matrix(node)
        if 'skin' in node:raise ValueError('Skinned models require posed export')
        if 'mesh' in node:
            for prim in j['meshes'][node['mesh']]['primitives']:
                if prim.get('mode',4)!=4:raise ValueError('Only triangle primitives supported')
                ext=prim.get('extensions',{}).get('KHR_draco_mesh_compression')
                if ext:
                    d=DracoPy.decode(view(ext['bufferView']));attrs={v['unique_id']:v['data'] for v in d.attributes};attrs={k:attrs[v] for k,v in ext['attributes'].items()};faces=d.faces
                else:
                    attrs={k:accessor(v) for k,v in prim['attributes'].items()};faces=accessor(prim['indices']).reshape(-1,3) if 'indices' in prim else np.arange(len(attrs['POSITION'])).reshape(-1,3)
                points=(attrs['POSITION']@world[:3,:3].T+world[:3,3])@convert.T
                normals=attrs['NORMAL']@np.linalg.inv(world[:3,:3])@convert.T;normals/=np.linalg.norm(normals,axis=1,keepdims=True)
                mi=prim.get('material',0);tex=mats[mi].get('pbrMetallicRoughness',{}).get('baseColorTexture',{})
                trans=tex.get('extensions',{}).get('KHR_texture_transform',{})
                uv=attrs.get('TEXCOORD_'+str(trans.get('texCoord',tex.get('texCoord',0))),np.zeros((len(points),2))).copy()
                uv*=trans.get('scale',[1,1]);ang=trans.get('rotation',0)
                uv=uv@np.array([[math.cos(ang),math.sin(ang)],[-math.sin(ang),math.cos(ang)]])+trans.get('offset',[0,0])
                uv[:,1]=1-uv[:,1]  # rasterizer uses bottom-left origin
                mm.append(np.full(len(faces),mi,dtype=np.int32))
                pp.append(points[faces]);nn.append(normals[faces]);tt.append(uv[faces])
        for child in node.get('children',[]):visit(child,world)
    for node in j['scenes'][j.get('scene',0)]['nodes']:visit(node,np.eye(4))
    points=np.concatenate(pp);low=points.min(axis=(0,1));high=points.max(axis=(0,1));center=(low+high)/2;center[2]=low[2]
    points=(points-center)*3/np.max(high-low)
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(out,positions=points.astype('f4'),normals=np.concatenate(nn).astype('f4'),uv=np.concatenate(tt).astype('f4'),material_ids=np.concatenate(mm))
    np.savez_compressed(out.with_suffix('.textures.npz'),textures=np.stack([np.asarray(atlas.crop(((k%side)*a.tile,(k//side)*a.tile,(k%side+1)*a.tile,(k//side+1)*a.tile))) for k in range(len(mats))]))
    atlas.save(out.with_suffix('.png'));print('EXPORTED',len(points),'triangles',len(mats),'materials')

if __name__=='__main__':main()
