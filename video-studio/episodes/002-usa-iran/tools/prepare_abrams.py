import bpy,numpy as np
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'assets/models/abrams';bpy.ops.wm.open_mainfile(filepath=str(p/'abrams.blend'),load_ui=False,use_scripts=False)
positions=[];normals=[];uv=[];ids=[];colors=[]
for obj in bpy.context.scene.objects:
 if obj.type!='MESH' or obj.hide_render or obj.name=='Cube.003':continue
 m=obj.data;m.calc_loop_triangles();nm=obj.matrix_world.to_3x3().inverted().transposed()
 slots=[]
 for mat in m.materials:
  color=(.48,.46,.35) if mat and mat.name.startswith('body') else (.1,.12,.1) if mat and mat.name in ['metal barrel','wheels','nukclearsign'] else tuple(mat.diffuse_color[:3]) if mat else (.42,.43,.28)
  slots.append(len(colors));colors.append(color)
 if not slots:slots=[len(colors)];colors.append((.42,.43,.28))
 for tri in m.loop_triangles:
  positions.append([tuple(obj.matrix_world@m.vertices[v].co) for v in tri.vertices]);normals.append([tuple((nm@m.vertices[v].normal).normalized()) for v in tri.vertices]);uv.append([(0,0)]*3);ids.append(slots[min(tri.material_index,len(slots)-1)])
a=np.asarray(positions,np.float32);n=np.asarray(normals,np.float32);lo=a.min((0,1));hi=a.max((0,1));c=(lo+hi)/2;c[2]=lo[2];a=(a-c)*3/max(hi-lo)
np.savez_compressed(p/'abrams.npz',positions=a,normals=n,uv=np.asarray(uv,np.float32),material_ids=np.asarray(ids,np.int32))
colors=np.asarray(colors);textures=np.tile((np.clip(colors,0,1)*255).astype(np.uint8)[:,None,None,:],(1,8,8,1));np.savez_compressed(p/'abrams-colors.npz',textures=textures)
print('EXPORTED',len(a),lo,hi,colors)
