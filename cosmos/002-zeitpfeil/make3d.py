"""Original spatial explanatory animations for Kosmion's arrow-of-time film."""
import bpy,math,random,sys,pathlib
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parent;mode=sys.argv[sys.argv.index('--')+1];out=R/'3d'/mode;out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.cycles.max_bounces=4;s.cycles.diffuse_bounces=2;s.cycles.glossy_bounces=2;s.cycles.transmission_bounces=2
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.fps=25;s.render.fps_base=2;s.frame_start=1;s.frame_end=100;s.view_settings.view_transform='AgX'
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.008,.015,.028,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.22
detail=(mode=='gas_detail')
if detail:mode='gas'
random.seed(47 if detail else 23)
def material(name,color,metal=0,em=0,rough=.3,texture=False):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;b=n.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=rough;b.inputs['Emission Color'].default_value=(*color,1);b.inputs['Emission Strength'].default_value=em
 if texture:
  t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=5;t.inputs['Detail'].default_value=5;r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(*(v*.15 for v in color),1);r.color_ramp.elements[1].color=(*color,1);m.node_tree.links.new(t.outputs['Fac'],r.inputs[0]);m.node_tree.links.new(r.outputs[0],b.inputs['Base Color']);m.node_tree.links.new(r.outputs[0],b.inputs['Emission Color'])
 return m
navy=material('Midnight ceramic',(.015,.027,.055),.35,rough=.25);gold=material('Champagne gold',(.78,.45,.13),.72,rough=.25);glow=material('Amber light',(1,.39,.035),.15,em=2);white=material('Ivory',(.78,.84,.92),.35,rough=.24);blue=material('Glacier blue',(.025,.27,.65),.45,rough=.2);dark=material('Slate',(.012,.022,.036),.3,rough=.38)
def smooth(o):
 for p in o.data.polygons:p.use_smooth=True
 return o
def sphere(loc,r,mat):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=20,radius=r,location=loc);o=bpy.context.object;o.data.materials.append(mat);return smooth(o)
def cube(loc,scale,mat,bevel=.1):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
 if bevel:mod=o.modifiers.new('Soft manufactured edges','BEVEL');mod.width=bevel;mod.segments=3;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o
def cylinder(loc,r,depth,mat):
 bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=r,depth=depth,location=loc);o=bpy.context.object;o.data.materials.append(mat);smooth(o);b=o.modifiers.new('Polished edge','BEVEL');b.width=.025;b.segments=3;o.modifiers.new('Normals','WEIGHTED_NORMAL');return o
def curve(pts,r,mat):
 c=bpy.data.curves.new('Spatial path','CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=2;sp=c.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,v in zip(sp.points,pts):p.co=(*v,1)
 o=bpy.data.objects.new('Spatial path',c);bpy.context.collection.objects.link(o);o.data.materials.append(mat);return o
def key(o,prop,f,val):setattr(o,prop,val);o.keyframe_insert(data_path=prop,frame=f)
def floor():cube((0,0,-1.8),(200,200,.1),dark,.02)
if mode=='orbit':
 sun=material('Stellar surface',(1,.28,.02),em=2.4,texture=True);o=sphere((-1.25,0,0),1.15,sun)
 planet=material('Planetary surface',(.1,.35,.65),.1,rough=.42,texture=True);p=sphere((2,0,0),.38,planet)
 pts=[(-1.25+3.1*math.cos(j*math.tau/200),3.1*math.sin(j*math.tau/200),0) for j in range(201)];curve(pts,.008,navy)
 for f in range(1,101):
  a=(f-1)*math.tau/100;key(p,'location',f,(-1.25+3.1*math.cos(a),3.1*math.sin(a),0));key(p,'rotation_euler',f,(.2,.1,a))
 target=(-.2,0,0);camera=(6,-10,6);end=(5.2,-10.5,5.4)
elif mode=='gas':
 # Elastic reflections inside a volume. The central barrier is lifted after the initial frames.
 for x in [-3,3]:
  for y in [-1.5,1.5]:curve([(x,y,-1.3),(x,y,1.3)],.025,gold)
 for z in [-1.3,1.3]:
  for y in [-1.5,1.5]:curve([(-3,y,z),(3,y,z)],.025,gold)
  for x in [-3,3]:curve([(x,-1.5,z),(x,1.5,z)],.025,gold)
 barrier=cube((0,0,0),(.025,3,2.6),blue,.01);key(barrier,'location',1,(0,0,0));key(barrier,'location',12,(0,0,0));key(barrier,'location',25,(0,0,4.2));key(barrier,'scale',25,(1,1,1));key(barrier,'scale',30,(0,0,0))
 objs=[];pos=[];vel=[]
 for j in range(60 if detail else 105):
  p=Vector((random.uniform(-2.8,-.15),random.uniform(-1.3,1.3),random.uniform(-1.1,1.1)));v=Vector(tuple(random.uniform(-.12,.12) for _ in range(3)));pos.append(p);vel.append(v);objs.append(sphere(p,.075 if detail else .055,glow if j%4==0 else gold))
 for f in range(1,101):
  for j,o in enumerate(objs):
   p=pos[j];v=vel[j];p+=v
   for k,(lo,hi) in enumerate([(-2.9,-.08 if f<18 else 2.9),(-1.4,1.4),(-1.2,1.2)]):
    if p[k]<lo:p[k]=2*lo-p[k];v[k]*=-1
    if p[k]>hi:p[k]=2*hi-p[k];v[k]*=-1
   key(o,'location',f,p)
  for i in range(len(objs)):
   for j in range(i):
    delta=pos[i]-pos[j];d=delta.length
    if 0<d<.11:
     normal=delta/d;relative=(vel[i]-vel[j]).dot(normal)
     if relative<0:vel[i]-=normal*relative;vel[j]+=normal*relative
 floor();target=(0,0,0);camera=((-5,-8,3.2) if detail else (6,-10,4.6));end=((-4,-8.5,3.0) if detail else (5.4,-10.4,4.2))
elif mode=='coins':
 floor()
 for row in range(4):
  for col in range(5):
   root=bpy.data.objects.new('One coin',None);bpy.context.collection.objects.link(root);x=(col-2)*1.06;y=(row-1.5)*1.06;root.location=(x,y,-1.68)
   o=cylinder((0,0,0),.42,.065,gold);o.parent=root
   # Different physical reliefs make the two sides recognisable without any lettering.
   o=cylinder((0,0,.043),.18,.025,white);o.parent=root
   for k in range(5):
    a=k*math.tau/5;o=sphere((.23*math.cos(a),.23*math.sin(a),.052),.038,gold);o.parent=root
   o=cylinder((0,0,-.044),.24,.025,blue);o.parent=root
   for f,z,rot in [(1,-1.68,0),(22,-.3,math.pi*2),(55,-1.68,math.pi*(4+(row+col)%2)),(100,-1.68,math.pi*(4+(row+col)%2))]:key(root,'location',f,(x,y,z));key(root,'rotation_euler',f,(rot,0,.06*(row-col)))
 target=(0,0,-1.68);camera=(5,-7,7);end=(3.8,-7,7.5)
elif mode=='heat':
 floor();mats=[]
 for x,color in [(-1.5,(1,.18,.025)),(1.5,(.025,.2,.8))]:
  m=material('Thermal reservoir',color,.55,em=.3,rough=.23);mats.append(m);cube((x,0,-.7),(2.2,2.2,2.0),m,.14)
  bs=m.node_tree.nodes.get('Principled BSDF')
  for prop in ['Base Color','Emission Color']:
   bs.inputs[prop].default_value=(*color,1);bs.inputs[prop].keyframe_insert('default_value',frame=1);bs.inputs[prop].default_value=(.42,.26,.35,1);bs.inputs[prop].keyframe_insert('default_value',frame=100)
 for j in range(24):
  o=sphere((-.3,random.uniform(-.75,.75),random.uniform(-1.3,.1)),.025,glow)
  y=o.location.y;z=o.location.z;key(o,'location',1,(-.3+random.random()*.6,y,z));key(o,'location',80,(.3,y,z));key(o,'scale',80,(1,1,1));key(o,'scale',100,(0,0,0))
 target=(0,0,-.6);camera=(5,-9,4);end=(4,-9.5,4.2)
elif mode=='chess':
 floor();wood=material('Walnut',(.12,.048,.018),.15,rough=.3,texture=True)
 cube((0,0,-1.65),(5.15,5.15,.15),wood,.06)
 for row in range(8):
  for col in range(8):cube(((col-3.5)*.6,(row-3.5)*.6,-1.55),(.595,.595,.045),white if (row+col)%2==0 else navy,.008)
 for side,ma in [(-1,white),(1,navy)]:
  for row in [0,1]:
   for col in range(8):
    root=bpy.data.objects.new('Chess piece',None);bpy.context.collection.objects.link(root);x=(col-3.5)*.6;y=side*(2.1-row*.6);root.location=(x,y,-1.48)
    o=cylinder((0,0,.05),.19,.1,ma);o.parent=root;o=cylinder((0,0,.24),.085,.32 if row else .45,ma);o.parent=root;o=sphere((0,0,.43 if row else .57),.12 if row else .15,ma);o.parent=root
    if side==-1 and row==1 and col==3:
     key(root,'location',1,(x,y,-1.48));key(root,'location',25,(x,y,-1.48));key(root,'location',60,(x,y+1.2,-1.48));key(root,'location',100,(x,y+1.2,-1.48))
 target=(0,0,-1);camera=(5,-7,6);end=(4.3,-7.5,6.4)
elif mode=='clock':
 floor();root=bpy.data.objects.new('Clock',None);bpy.context.collection.objects.link(root)
 cylinder((0,0,-.8),2.0,.2,gold);cylinder((0,0,-.68),1.83,.1,navy)
 for j in range(60):
  a=j*math.tau/60;r=1.62;o=cube((r*math.sin(a),r*math.cos(a),-.6),(.035,.19 if j%5==0 else .08,.025),white,.008);o.rotation_euler.z=-a
 def hand(length,width,mat,z):
  pivot=bpy.data.objects.new('Clock hand',None);bpy.context.collection.objects.link(pivot);pivot.location=(0,0,z);o=cube((0,length/2,0),(width,length,.025),mat,.015);o.parent=pivot;return pivot
 h=hand(.85,.09,gold,-.51);h.rotation_euler.z=-.7;m=hand(1.3,.055,white,-.47);m.rotation_euler.z=-2.5;sec=hand(1.52,.025,glow,-.43);key(sec,'rotation_euler',1,(0,0,0));key(sec,'rotation_euler',100,(0,0,-math.tau));sphere((0,0,-.4),.09,gold)
 target=(0,0,-.7);camera=(3,-5,6.7);end=(2.2,-5.2,7.2)
elif mode=='pendulum':
 floor();pivot=bpy.data.objects.new('Pendulum pivot',None);bpy.context.collection.objects.link(pivot);pivot.location=(0,0,1.1);o=cylinder((0,0,-1.2),.035,2.4,white);o.parent=pivot;o=sphere((0,0,-2.4),.43,gold);o.parent=pivot
 for f in range(1,101):key(pivot,'rotation_euler',f,(0,.52*math.cos((f-1)*math.tau/50),0))
 curve([(-2.2,0,-1.7),(-2.2,0,1.3),(2.2,0,1.3),(2.2,0,-1.7)],.045,navy)
 target=(0,0,-.1);camera=(4,-9,2.4);end=(3.3,-9.3,2.7)
else:raise ValueError(mode)
for loc,power,color,size in [((1,-5,7),1200,(.65,.8,1),5),((-6,1,3),1500,(1,.55,.2),4),((3,5,4),1300,(.25,.5,1),4)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.color=color;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=camera);c=bpy.context.object;s.camera=c;c.data.lens=47
for f,loc in [(1,camera),(100,end)]:key(c,'location',f,loc);key(c,'rotation_euler',f,(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler())
for obj in bpy.data.objects:
 if obj.animation_data and obj.animation_data.action:
  for fc in obj.animation_data.action.fcurves:
   for p in fc.keyframe_points:p.interpolation='LINEAR'
s.use_nodes=True;t=s.node_tree;t.nodes.clear();rl=t.nodes.new('CompositorNodeRLayers');gl=t.nodes.new('CompositorNodeGlare');gl.glare_type='FOG_GLOW';gl.quality='MEDIUM';gl.threshold=1.5;gl.size=7;co=t.nodes.new('CompositorNodeComposite');t.links.new(rl.outputs['Image'],gl.inputs[0]);t.links.new(gl.outputs[0],co.inputs[0])
s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=95;s.render.filepath=str(out/'frame_');bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'))
if '--pilot' in sys.argv:s.frame_set(55);s.render.filepath=str(out/'pilot.jpg')
try:bpy.ops.render.render(write_still=True) if '--pilot' in sys.argv else bpy.ops.render.render(animation=True)
except RuntimeError as e:
 if 'denois' not in str(e).lower():raise
 s.cycles.use_denoising=False;s.cycles.samples=24
 bpy.ops.render.render(write_still=True) if '--pilot' in sys.argv else bpy.ops.render.render(animation=True)
