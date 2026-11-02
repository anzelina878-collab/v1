"""CC0, simplified exterior display illustrations; not engineering replicas."""
import bpy,math,json,os
from pathlib import Path
from mathutils import Vector
import numpy as np
ROOT=Path(os.environ.get('ARSENAL_MODEL_ROOT',str(Path(__file__).resolve().parents[1]/'assets/models')));ROOT.mkdir(parents=True,exist_ok=True)
def clear():
 bpy.ops.wm.read_factory_settings(use_empty=True)
 def m(name,c):
  a=bpy.data.materials.new(name);a.diffuse_color=(*c,1);return a
 return m('Olive',(.24,.29,.20)),m('Tracks',(.055,.065,.06)),m('Metal',(.39,.43,.40)),m('Glass',(.035,.065,.08))
def box(name,loc,size,material,bevel=.04):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.scale=size;o.data.materials.append(material)
 if bevel:
  mod=o.modifiers.new('Edge chamfer','BEVEL');mod.width=bevel;mod.segments=2
 return o
def sphere(name,loc,size,material):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=loc);o=bpy.context.object;o.name=name;o.scale=size;o.data.materials.append(material);return o
def rod(name,a,b,r,material,vertices=20):
 v=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=v.length,location=(Vector(a)+Vector(b))/2);o=bpy.context.object;o.name=name;o.rotation_euler=v.to_track_quat('Z','Y').to_euler();o.data.materials.append(material);return o
def wedge(name,verts,faces,material):
 m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o);o.data.materials.append(material);return o
def save(key,reference):
 d=ROOT/key;d.mkdir(exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(d/'original.blend'));pp=[];nn=[];uu=[];mi=[];colors=[]
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  ob=o.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ob.to_mesh();mesh.calc_loop_triangles();nm=o.matrix_world.to_3x3().inverted().transposed();i=len(colors);colors.append(tuple(o.data.materials[0].diffuse_color[:3]))
  for t in mesh.loop_triangles:pp.append([tuple(o.matrix_world@mesh.vertices[v].co) for v in t.vertices]);nn.append([tuple((nm@mesh.vertices[v].normal).normalized()) for v in t.vertices]);uu.append([(0,0)]*3);mi.append(i)
  ob.to_mesh_clear()
 pp=np.asarray(pp,np.float32);lo=pp.min((0,1));hi=pp.max((0,1));c=(lo+hi)/2;c[2]=lo[2];pp=(pp-c)*3/max(hi-lo)
 np.savez_compressed(d/'mesh.npz',positions=pp,normals=np.asarray(nn,np.float32),uv=np.asarray(uu,np.float32),material_ids=np.asarray(mi,np.int32));tex=np.tile((np.asarray(colors)*255).astype(np.uint8)[:,None,None,:],(1,32,32,1));np.savez_compressed(d/'textures.npz',textures=tex);(d/'source.json').write_text(json.dumps({'id':key,'creator':'Original ARSENAL 360 exterior display illustration','license':'CC0','reference':reference,'fidelity':'Simplified schematic exterior; not an exact model/version or engineering design; no internal functional details'},indent=2));print('SCHEMATIC_READY',key,len(pp),flush=True)

olive,dark,metal,glass=clear()
verts=[(-4.4,0,.85),(-3.0,-.70,.85),(4.1,-.70,.85),(4.1,.70,.85),(-3.0,.70,.85),(-3.9,0,.10),(3.8,-.45,.10),(3.8,.45,.10)]
wedge('Schematic frigate hull',verts,[(0,1,2,3,4),(0,5,6,2,1),(0,4,3,7,5),(2,6,7,3),(5,7,6)],metal)
box('Forward deck',(-2.0,0,.86),(3.2,1.25,.08),metal);box('Helicopter deck',(2.8,0,.86),(2.2,1.3,.08),dark)
box('Bridge',(-.9,0,1.35),(1.4,1.05,.95),metal);box('Bridge windows',(-1.62,0,1.60),(.025,.86,.20),glass);box('Hangar',(.9,0,1.28),(1.5,1.1,.83),metal)
for x,z in [(-.1,2.6),(.6,2.25)]:rod('Sensor mast',(x,0,1.7),(x,0,z),.045,metal)
box('Radar display',(-.1,0,2.58),(.38,.65,.20),dark);rod('Generic display bow mount',(-3.0,0,1.1),(-3.5,0,1.18),.045,dark)
for x in [2.1,2.5,2.9,3.3]:box('Helipad marking',(x,0,.92),(.15,.025,.005),metal)
save('miecznik-illustrative','https://en.wikipedia.org/wiki/Wicher-class_frigate')
