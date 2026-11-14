"""Original exterior-only illustrative display geometry, not engineering CAD."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
import os
p=Path(os.environ.get('ARSENAL_MODEL_ROOT',str(Path(__file__).resolve().parents[2]/'assets/models-v2')))
def mat(name,c):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);return m
steel=mat('Dark hull',(.105,.14,.15));fin=mat('Satin gray',(.31,.34,.32));white=mat('Composite light',(.68,.69,.65));dark=mat('Propeller',(.09,.10,.095))
def sphere(name,location,scale,material):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=20,location=location);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(material);return o

def cube(name,loc,scale,material):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(material);bevel=o.modifiers.new('Soft plate edges','BEVEL');bevel.width=.045;bevel.segments=3;return o

def rod(name,a,b,r,material):
 d=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2);o=bpy.context.object;o.name=name;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(material);return o

def save(key,reference):
 d=p/key;d.mkdir(exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(d/'original.blend'));(d/'source.json').write_text(json.dumps({'id':key,'creator':'Original exterior visualization made for ARSENAL 360','license':'CC0','reference':reference,'fidelity':'Simplified exterior illustration; not an engineering-certified replica; no internal or functional details'},indent=2));
 positions=[];normals=[];mids=[];uv=[];colors=[]
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  deps=bpy.context.evaluated_depsgraph_get();obj=o.evaluated_get(deps);mesh=obj.to_mesh();mesh.calc_loop_triangles();nm=o.matrix_world.to_3x3().inverted().transposed();color=tuple(o.data.materials[0].diffuse_color[:3]);mi=len(colors);colors.append(color)
  for t in mesh.loop_triangles:
   positions.append([tuple(o.matrix_world@mesh.vertices[v].co) for v in t.vertices]);normals.append([tuple((nm@mesh.vertices[v].normal).normalized()) for v in t.vertices]);uv.append([(0,0)]*3);mids.append(mi)
  obj.to_mesh_clear()
 import numpy as np
 a=np.asarray(positions,np.float32);lo=a.min((0,1));hi=a.max((0,1));center=(lo+hi)/2;center[2]=lo[2];a=(a-center)*3/max(hi-lo)
 np.savez_compressed(d/'mesh.npz',positions=a,normals=np.asarray(normals,np.float32),uv=np.asarray(uv,np.float32),material_ids=np.asarray(mids,np.int32));textures=np.tile((np.asarray(colors)*255).astype(np.uint8)[:,None,None,:],(1,16,16,1));np.savez_compressed(d/'textures.npz',textures=textures)
 print('ORIGINAL_MODEL',key,len(a),flush=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
steel=mat('Dark hull',(.105,.14,.15));fin=mat('Satin gray',(.31,.34,.32));white=mat('Composite light',(.68,.69,.65));dark=mat('Propeller',(.09,.10,.095))
sphere('Ghadir hull exterior',(0,0,.58),(3.8,.46,.49),steel);sphere('Casing upper deck',(-.20,0,.96),(2.95,.33,.16),steel);cube('Sail',(-.95,0,1.22),(.77,.35,.8),steel);sphere('Sail rounded front',(-1.3,0,1.22),(.22,.18,.41),steel)
rod('Periscope',(-.95,0,1.60),(-.95,0,2.05),.022,fin);rod('Mast',(-.65,.03,1.60),(-.65,.03,1.89),.015,fin)
for x in [-2.9,2.8]:cube('Diving plane',(x,0,.68),(.33,1.5,.055),steel)
cube('Rudder',(3.30,0,.68),(.43,.06,1.1),steel);rod('Propeller axle',(3.7,0,.58),(4.0,0,.58),.045,dark)
for angle in range(0,360,72):
 o=cube('Propeller blade',(4.01,math.cos(math.radians(angle))*.17,.58+math.sin(math.radians(angle))*.17),(.04,.16,.35),dark);o.rotation_euler.x=math.radians(angle)
save('ghadir-illustrative','https://en.wikipedia.org/wiki/Ghadir-class_submarine')
bpy.ops.wm.read_factory_settings(use_empty=True)
steel=mat('Dark hull',(.105,.14,.15));fin=mat('Satin gray',(.31,.34,.32));white=mat('Composite light',(.68,.69,.65));dark=mat('Propeller',(.09,.10,.095))
sphere('Shahed exterior fuselage',(0,0,.24),(1.75,.14,.16),white);sphere('Nose',(-1.55,0,.24),(.38,.12,.13),white)
verts=[(-.92,0,.22),(1.28,-1.28,.22),(1.1,1.28,.22),(-.92,0,.29),(1.28,-1.28,.29),(1.1,1.28,.29)];faces=[(0,1,2),(3,5,4),(0,3,4,1),(1,4,5,2),(2,5,3,0)];mesh=bpy.data.meshes.new('Delta wing');mesh.from_pydata(verts,[],faces);o=bpy.data.objects.new('Delta wing',mesh);bpy.context.collection.objects.link(o);o.data.materials.append(white)
for y in [-1.24,1.24]:cube('Wingtip fin',(.98,y,.49),(.47,.035,.52),white)
rod('Rear propeller axle',(1.63,0,.24),(1.92,0,.24),.045,dark)
for angle in [20,200]:
 o=cube('Rear propeller',(1.94,math.cos(math.radians(angle))*.22,.24+math.sin(math.radians(angle))*.22),(.045,.09,.52),dark);o.rotation_euler.x=math.radians(angle)
save('shahed136-illustrative','https://en.wikipedia.org/wiki/Shahed_136')
bpy.ops.wm.read_factory_settings(use_empty=True)
steel=mat('Hull haze gray',(.31,.35,.37));fin=mat('Flight deck',(.085,.105,.12));white=mat('Deck markings',(.75,.75,.69));dark=mat('Windows',(.035,.07,.085))
# Original display silhouette of Ford's externally visible hull and flight deck.
verts=[(-4.3,-.08,.55),(-3.4,-.62,.55),(3.9,-.62,.55),(4.35,-.36,.55),(4.35,.36,.55),(3.8,.62,.55),(-3.45,.62,.55),(-4.3,.08,.55),(-3.6,-.25,.08),(3.9,-.3,.08),(3.9,.3,.08),(-3.6,.25,.08)]
faces=[(0,1,2,3,4,5,6,7),(0,8,9,3,2,1),(3,9,10,4),(4,10,11,7,6,5),(7,11,8,0),(8,11,10,9)]
mesh=bpy.data.meshes.new('Carrier hull');mesh.from_pydata(verts,[],faces);o=bpy.data.objects.new('Hull exterior',mesh);bpy.context.collection.objects.link(o);o.data.materials.append(steel)
outline=[(-4.32,-.12,.65),(-3.65,-.77,.65),(-.70,-.83,.65),(.15,-1.08,.65),(3.95,-.9,.65),(4.4,-.62,.65),(4.4,.70,.65),(2.4,.90,.65),(-.5,.78,.65),(-2.8,.70,.65),(-4.32,.20,.65)]
mesh=bpy.data.meshes.new('Flight deck');mesh.from_pydata(outline,[],[tuple(range(len(outline)))]);o=bpy.data.objects.new('Flight deck',mesh);bpy.context.collection.objects.link(o);o.data.materials.append(fin)
for k in range(13):cube('Landing centerline',(-2.9+k*.49,-.12,.666),(.25,.019,.005),white)
for x in [-2.8,-1.8]:cube('Forward launch track',(x,.32,.667),(1.6,.012,.005),white)
for x in [.8,1.5,2.2]:cube('Deck elevator',(x,.80,.57),(.65,.35,.12),steel)
cube('Island lower',(1.6,.65,.95),(.95,.45,.65),steel);cube('Island bridge',(1.4,.65,1.28),(.75,.48,.25),steel);cube('Bridge windows',(1.03,.65,1.29),(.015,.43,.12),dark);cube('Island upper',(1.76,.65,1.55),(.43,.28,.35),steel)
for x,z in [(1.6,2.1),(1.95,1.95)]:rod('Island mast',(x,.65,1.6),(x,.65,z),.012,steel)
for x in [-1.4,-.5,.4,2.7,3.3]:
 sphere('Parked aircraft fuselage',(x,.42,.74),(.29,.035,.035),steel);cube('Parked aircraft wings',(x+.03,.42,.745),(.10,.37,.018),steel);cube('Parked aircraft tail',(x+.2,.42,.78),(.065,.13,.07),steel)
save('ford-illustrative','https://www.navy.mil/Resources/Fact-Files/Display-FactFiles/Article/2169795/aircraft-carriers-cvn/')
