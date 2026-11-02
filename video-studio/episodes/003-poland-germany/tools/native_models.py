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
for key,nw in [('leopard-illustrative',7),('k2-illustrative',6),('pzh-illustrative',7)]:
 olive,dark,metal,glass=clear();length=6.7 if nw==7 else 6.1
 for y in [-1.16,1.16]:
  box('Track envelope',(0,y,.54),(length,.40,.82),dark,.18)
  for k in range(nw):
   x=-length*.39+k*length*.78/(nw-1);rod('Road wheel',(x,y-.23,.50),(x,y+.23,.50),.32,metal)
 box('Lower hull',(0,0,.87),(length,2.25,.74),olive,.12);box('Upper hull deck',(-.1,0,1.24),(length-.3,2.18,.38),olive,.07)
 if key=='pzh-illustrative':
  box('High howitzer turret',(.5,0,2.0),(3.1,2.05,1.40),olive,.1);rod('Display barrel',(-1.0,0,2.22),(-6.6,0,2.22),.10,olive);box('Muzzle brake',(-6.7,0,2.22),(.40,.30,.25),dark)
 else:
  box('Turret core',(-.2,0,1.84),(3.2 if nw==7 else 3.5,1.95,.84),olive,.12)
  wedge('Wedge turret face',[(-2.0,-.95,1.48),(-2.0,.95,1.48),(-1.3,.93,2.2),(-1.3,-.93,2.2),(-.1,-.93,2.2),(-.1,.93,2.2)],[(0,1,2,3),(3,2,5,4),(0,3,4),(1,5,2)],olive)
  rod('Display gun barrel',(-1.9,0,1.94),(-6.1,0,1.94),.09,olive);rod('Barrel sleeve',(-2.8,0,1.94),(-3.7,0,1.94),.14,olive);box('Turret bustle',(1.45,0,1.95),(1.0,1.9,.55),olive,.08)
  for y in [-.48,.48]:rod('Hatch',(.1,y,2.24),(.1,y,2.33),.30,olive)
  box('Optics housing',(-.4,-.7,2.37),(.38,.28,.25),olive);box('Optics front',(-.6,-.7,2.37),(.015,.22,.15),glass)
 rod('Display antenna',(1.3,.75,2.35),(1.3,.75,3.18),.012,dark)
 save(key,'https://en.wikipedia.org/wiki/'+{'leopard-illustrative':'Leopard_2','k2-illustrative':'K2_Black_Panther','pzh-illustrative':'Panzerhaubitze_2000'}[key])
olive,dark,metal,glass=clear();sphere('Pressure hull exterior',(0,0,.67),(3.8,.65,.65),dark);sphere('Upper casing',(-.15,0,1.1),(2.8,.45,.22),dark);box('Sail',(-.65,0,1.60),(1.15,.52,1.25),dark,.15)
for x,h in [(-.8,2.65),(-.5,2.48),(-.2,2.55)]:rod('Mast',(x,0,2.15),(x,0,h),.021,metal)
for angle in [45,135]:
 o=box('Schematic X stern rudder',(3.25,0,.67),(.6,1.8,.065),dark);o.rotation_euler.x=math.radians(angle)
rod('Stern shaft',(3.5,0,.67),(4.0,0,.67),.08,dark)
save('type212-illustrative','https://en.wikipedia.org/wiki/Type_212_submarine')
olive,dark,metal,glass=clear();sphere('TB2 fuselage',(-.3,0,.72),(2.0,.22,.24),metal);box('Straight wing',(-.30,0,.92),(.5,6.0,.08),metal);sphere('Sensor display',(-1.2,0,.43),(.2,.2,.2),dark)
for y in [-.8,.8]:rod('Tail boom',(.1,y,.68),(2.3,y,.68),.05,metal);o=box('V tail',(2.0,y,.96),(.65,.06,.85),metal);o.rotation_euler.x=.55 if y<0 else -.55
rod('Pusher axle',(1.3,0,.72),(1.65,0,.72),.08,dark);box('Propeller',(1.68,0,.72),(.04,1.2,.08),dark)
for x,y in [(-1.3,0),(.3,-.6),(.3,.6)]:rod('Display undercarriage',(x,y,.6),(x,y,.18),.025,dark);rod('Wheel',(x,y-.06,.14),(x,y+.06,.14),.14,dark)
save('tb2-illustrative','https://en.wikipedia.org/wiki/Bayraktar_TB2')
olive,dark,metal,glass=clear();box('Vehicle chassis',(0,0,.65),(4.7,1.7,.35),dark);box('Cab',(-1.6,0,1.46),(1.35,1.7,1.35),olive,.1);box('Windshield',(-2.3,0,1.75),(.03,1.45,.50),glass);box('Rear launcher pod',(.85,0,1.54),(2.65,1.55,1.03),olive,.07)
for x in [-1.65,.65,1.65]:
 for y in [-.92,.92]:rod('Tire',(x,y-.14,.48),(x,y+.14,.48),.44,dark);rod('Hub',(x,y-.15,.48),(x,y+.15,.48),.23,metal)
for y in [-.48,0,.48]:
 for z in [1.30,1.77]:rod('Nonfunctional tube face',(2.17,y,z),(2.24,y,z),.19,dark)
save('himars-illustrative','https://en.wikipedia.org/wiki/M142_HIMARS')
