"""Original generic evidence-carrier geometry; no branded or case-specific device."""
from pathlib import Path
import sys,bpy,numpy as np
from mathutils import Matrix
out=Path(sys.argv[sys.argv.index('--')+1]);out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
colors=[(38,45,53),(12,19,27),(145,151,156),(73,84,100),(187,168,99),(20,23,28)]
mats=[]
for i,c in enumerate(colors):
 m=bpy.data.materials.new('original-material-'+str(i));m.diffuse_color=tuple(x/255 for x in c)+(1,);mats.append(m)
def cube(name,loc,size,mat,bevel=.02):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mats[mat])
 if bevel:
  b=o.modifiers.new('manufactured-rounded-edges','BEVEL');b.width=bevel;b.segments=4;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=b.name)
 return o
# Closed smartphone: dark screen, metal frame, separate cameras and buttons.
cube('phone-frame',(-.36,0,1.05),(.71,.075,1.43),2,.045)
cube('phone-front-glass',(-.36,-.043,1.05),(.665,.014,1.377),1,.035)
cube('phone-back',(-.36,.044,1.05),(.67,.018,1.38),0,.03)
cube('earpiece',(-.36,-.053,1.69),(.17,.012,.012),5,.005)
for z in [1.31,1.51]:
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.061,depth=.026,location=(-.59,.068,z),rotation=(1.5707963,0,0));bpy.context.object.data.materials.append(mats[1])
 cube('volume-button',(-.724,0,z),(.015,.032,.10),0,.006)
cube('power-button',(.003,0,1.35),(.016,.03,.15),0,.006)
# Closed external drive. Neutral original label, screws and connector.
cube('external-drive',(.35,.02,.60),(.62,.14,.91),0,.04)
cube('drive-front-label',(.35,-.057,.62),(.49,.009,.61),3,.012)
for x in [.12,.58]:
 for z in [.24,.97]:
  bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=.017,location=(x,-.078,z));bpy.context.object.scale.y=.2;bpy.context.object.data.materials.append(mats[2])
for i in range(4):cube('label-design',(.35,-.065,.78-i*.07),(.32-i*.03,.004,.012),2,0)
cube('USB-plug',(.35,0,1.10),(.17,.055,.14),2,.008)
cube('USB-recess',(.35,-.031,1.12),(.12,.005,.055),1,.003)
# Small flash carrier on its own plinth.
cube('USB-body',(.85,0,.27),(.19,.11,.40),3,.022)
cube('USB-metal',(.85,0,.54),(.16,.075,.17),2,.007)
for x in [.81,.88]:cube('contact', (x,-.039,.57),(.025,.006,.055),4,0)
# Display bases remain part of the real geometry throughout the orbit.
for x,w in [(-.36,.78),(.35,.67),(.85,.29)]:cube('exhibit-base',(x,0,.06),(w,.42,.12),2,.02)
positions=[];normals=[];uv=[];mid=[]
for obj in bpy.context.scene.objects:
 if obj.type!='MESH':continue
 me=obj.data;me.calc_loop_triangles();nm=obj.matrix_world.to_3x3().inverted().transposed();m=mats.index(me.materials[0])
 for t in me.loop_triangles:
  positions.append([tuple(obj.matrix_world@me.vertices[v].co) for v in t.vertices]);normals.append([tuple((nm@me.vertices[v].normal).normalized()) for v in t.vertices]);uv.append([(0,0)]*3);mid.append(m)
p=np.asarray(positions,np.float32);p[:,:,0]-=.08
np.savez_compressed(out/'mesh.npz',positions=p,normals=np.asarray(normals,np.float32),uv=np.asarray(uv,np.float32),material_ids=np.asarray(mid,np.int32))
tex=np.stack([np.full((8,8,3),c,np.uint8) for c in colors]);np.savez_compressed(out/'textures.npz',textures=tex)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'original-digital-carriers.blend'))
print('ORIGINAL_GEOMETRY',len(p))
