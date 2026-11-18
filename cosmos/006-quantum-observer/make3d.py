"""Original spatial explanatory reconstructions; no claim of direct observation or actual scale."""
import bpy,math,sys,pathlib,random
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parent;mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'lab_wide';pilot='--pilot' in sys.argv;family,view=mode.rsplit('_',1);random.seed(106)
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.render.engine='BLENDER_EEVEE_NEXT' if bpy.app.version>=(4,2,0) else 'BLENDER_EEVEE';s.eevee.taa_render_samples=32;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=50 if pilot else 100;s.render.fps=12;s.frame_start=1;s.frame_end=481;s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=95
s.world=bpy.data.worlds.new('Dark environment');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.009,.015,.026,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.28;s.view_settings.view_transform='AgX'
s.use_nodes=True;nt=s.node_tree;nt.nodes.clear();a=nt.nodes.new('CompositorNodeRLayers');g=nt.nodes.new('CompositorNodeGlare');g.glare_type='FOG_GLOW';g.threshold=2;g.quality='MEDIUM';g.size=7;c=nt.nodes.new('CompositorNodeComposite');nt.links.new(a.outputs['Image'],g.inputs['Image']);nt.links.new(g.outputs['Image'],c.inputs[0])
def mat(name,col,metal=0,rough=.3,em=0,alpha=1):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,alpha);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if em:p.inputs['Emission Color'].default_value=(*col,1);p.inputs['Emission Strength'].default_value=em
 if alpha<1:
  p.inputs['Alpha'].default_value=alpha
  if hasattr(m,'surface_render_method'):m.surface_render_method='DITHERED'
  else:m.blend_method='BLEND'
 return m
silver=mat('Brushed titanium',(.35,.4,.46),.85,.24);dark=mat('Charcoal ceramic',(.018,.025,.04),.6,.28);gold=mat('Warm photon',(.95,.47,.1),.3,.2,3);blue=mat('Cool coherent amplitude',(.13,.48,.8),.25,.25,2);white=mat('Neutral light',(.8,.88,1),0,.2,4);ceramic=mat('Porcelain',(.76,.8,.84),.2,.22);ghost=mat('Quantum alternative',(.17,.5,.85),.5,.2,0,.32);black=mat('Dark horizon',(.0001,.0001,.0001),0,1);copper=mat('Warm copper',(.42,.16,.055),.8,.28)
def smooth(o):
 if o.type=='MESH':
  for f in o.data.polygons:f.use_smooth=True
 return o
def ball(name,pos,rad,material):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=rad,location=pos);o=bpy.context.object;o.name=name;o.data.materials.append(material);return smooth(o)
def box(name,pos,scale,material,bevel=.08):
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos);o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material)
 if bevel:m=o.modifiers.new('Machined edges','BEVEL');m.width=bevel;m.segments=3;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o
def curve(name,points,material,r=.025):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=3;sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
 for p,xyz in zip(sp.points,points):p.co=(*xyz,1)
 o=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(o);o.data.materials.append(material);return o
def torus(name,pos,major,minor,material,rotation=(0,0,0)):
 bpy.ops.mesh.primitive_torus_add(major_segments=72,minor_segments=12,location=pos,major_radius=major,minor_radius=minor,rotation=rotation);o=bpy.context.object;o.name=name;o.data.materials.append(material);return smooth(o)
def animate(o,attr,start,end):
 setattr(o,attr,start);o.keyframe_insert(attr,frame=1);setattr(o,attr,end);o.keyframe_insert(attr,frame=481)
def area(pos,power,col,size):
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.color=col;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
area((1,-6,9),2300,(.72,.85,1),7);area((-6,3,7),2200,(1,.77,.5),6);area((5,5,4),2600,(.3,.55,1),5)
target=Vector((0,0,1));start=(9,-14,9);end=(5,-13,7)
if family=='lab':
 box('Optical isolation bench',(0,0,-.38),(15,10,.7),dark)
 for x in range(-6,7):
  for y in range(-4,5):ball('Bench mounting point',(x,y,-.01),.035,silver)
 # Two vacuum chamber flange rings and a transparent window around the trapped object.
 for y in [-1.6,1.6]:
  torus('Vacuum flange',(0,y,1.7),1.75,.23,silver,(math.pi/2,0,0))
  for j in range(12):
   t=2*math.pi*j/12;ball('Flange bolt',(1.75*math.cos(t),y-.18,1.7+1.75*math.sin(t)),.095,dark)
 for x in [-1.25,1.25]:box('Chamber support',(x,0,.75),(.3,3.1,1.5),silver)
 for x in [-4,4]:
  box('Optical module',(x,0,.7),(1.3,2.2,1.3),silver);torus('Lens holder',(x,0,1.45),.37,.09,dark,(0,math.pi/2,0));curve('Controlled optical field',[(x,0,1.45),(0,0,1.45)],blue,.018)
 ball('Isolated system',(0,0,1.45),.19,gold);target=Vector((0,0,1.5))
 start,end=((9,-13,8),(5,-12,6)) if view=='wide' else ((3,-6,3.8),(-2,-5.5,3.4))
elif family in ['slits','detector']:
 box('Optical table',(0,0,-.35),(17,11,.5),dark)
 # The wall is built from three solid sections, leaving two genuine narrow openings.
 for y,dy in [(-3.85,4.3),(0,2),(3.85,4.3)]:box('Double slit barrier',(0,y,1.6),(.18,dy,3.2),silver,.025)
 box('Detection screen',(6,0,1.6),(.16,10,3.2),dark)
 ball('Electron source',(-6,0,1.5),.21,ceramic)
 for x in [-5,-4,-3,-2,-1]:
  o=curve('Incoming coherent wavefront',[(x,y/12,1.5) for y in range(-48,49)],blue,.014);animate(o,'location',(0,0,0),(.7,0,0))
 if family=='slits':
  for center in [-1.35,1.35]:
   for rad in [.7,1.4,2.1,2.8,3.5,4.2,4.9,5.6]:
    pts=[(rad*math.cos(t),center+rad*math.sin(t),1.5) for t in [(-.95+1.9*j/70) for j in range(71)]];o=curve('Spreading quantum amplitude',pts,blue,.018)
  for j in range(900):
   y=random.uniform(-4.8,4.8)
   if random.random()<(.5+.5*math.cos(y*4))**2:
    z=random.uniform(.3,2.9);o=ball('Discrete detection event',(5.89,y,z),.025,white);f=random.randint(1,430);o.hide_render=True;o.keyframe_insert('hide_render',frame=max(1,f-1));o.hide_render=False;o.keyframe_insert('hide_render',frame=f)
 else:
  for y in [-1.35,1.35]:
   box('Path-sensitive coupling',(.5,y,2.7),(.7,.65,.5),dark);ball('Detector record',(.45,y,2.38),.12,gold)
   for j in range(100):ball('Distinguishable detection event',(5.89,random.gauss(y,.44),random.uniform(.3,2.9)),.025,white)
 target=Vector((1,0,1));start,end=((-8,-16,13),(-5,-14,11)) if view=='wide' else ((3,-10,8),(2,-8,7))
elif family in ['decoherence','field','thermal']:
 box('Laboratory base',(0,0,-1.15),(13,10,.3),dark)
 for x in [-1.25,1.25]:
  o=ball('Alternative position',(x,0,.8),.65,ghost if x<0 else ceramic);animate(o,'rotation_euler',(0,0,0),(0,0,1))
 if family=='decoherence':
  for j in range(38):
   theta=random.uniform(0,math.tau);z=random.uniform(-.5,3);origin=Vector((1.25,0,.8));direction=Vector((math.cos(theta),math.sin(theta),z-.8)).normalized();o=ball('Scattered environmental light',origin+direction*.9,.045,gold if j%2 else blue);animate(o,'location',origin+direction*.9,origin+direction*random.uniform(5,8))
  for j in range(16):
   x=random.uniform(-6,6);y=random.uniform(-5,5);o=ball('Environmental molecule',(x,y,2.4),.09,silver);animate(o,'location',(x,y,2.4),(x+.6,y-1,2.1))
 elif family=='field':
  for j in range(16):
   t=j*math.tau/16
   for x,material in [(-1.25,blue),(1.25,gold)]:curve('Extended field correlation',[(x+math.cos(t)*r,math.sin(t)*r,.8+.15*r*r*math.sin(t)) for r in [k*.12 for k in range(55)]],material,.012)
 else:
  box('Thermal environment',(4,0,1.4),(.4,9,5),copper)
  for j in range(35):
   y=random.uniform(-4,4);z=random.uniform(-.5,3.4);o=ball('Thermal photon',(3.7,y,z),.035,gold);animate(o,'location',(3.7,y,z),(-4,y*.7,z*.8))
 target=Vector((.5,0,.7));start,end=((8,-12,8),(3,-11,7)) if view=='wide' else ((4,-6,3.5),(-3,-6,3))
elif family=='horizon':
 ball('Black hole causal boundary',(3,0,0),2.5,black)
 for j in range(12):
  t=math.tau*j/12;pts=[]
  for i in range(95):
   x=-6+i*.115;y=(.4+1.4*i/95)*math.cos(t);z=(.4+1.4*i/95)*math.sin(t);pts.append((x,y,z))
  curve('Field coupling to horizon',pts,blue if j%2 else gold,.012)
 for x in [-4.8,-3.6]:ball('External quantum alternatives',(x,0,0),.2,ghost if x<-4 else ceramic)
 for rad in [2.56,2.64]:torus('Gravitational lensing edge',(3,0,0),rad,.014,blue,(math.pi/2,0,0))
 for j in range(24):
  t=random.uniform(0,math.tau);o=ball('Soft field excitation',(-3,math.cos(t)*.6,math.sin(t)*.6),.035,gold);animate(o,'location',(-3,math.cos(t)*.6,math.sin(t)*.6),(2.2,math.cos(t),math.sin(t)))
 target=Vector((-.3,0,0));start,end=((1,-16,8),(-3,-14,5)) if view=='wide' else ((-5,-8,3),(-6,-7,2))
elif family=='branches':
 for branch,y in enumerate([-2.5,2.5]):
  box('Independent laboratory record',(0,y,-.3),(11,3.5,.4),dark)
  for x in [-3,0,3]:torus('Recorded state',(x,y,.6),.65,.07,silver,(math.pi/2,0,0))
  for x in [-3,0,3]:ball('Correlated state',(x,y,.6),.3,blue if branch==0 else gold)
  o=curve('Separation of alternatives',[(-6,0,.6),(-4,y,.6),(4,y,.6)],blue if branch==0 else gold,.025)
 target=Vector((0,0,.5));start,end=((9,-13,12),(6,-11,10)) if view=='wide' else ((3,-9,7),(-2,-8,6))
elif family=='signal':
 for x in [-4,4]:ball('Local physical system',(x,0,0),.55,silver)
 curve('Light-signal path',[(-3.5,0,0),(3.5,0,0)],blue,.012)
 o=ball('Finite-speed light pulse',(-3.5,0,0),.14,gold);animate(o,'location',(-3.5,0,0),(3.5,0,0))
 for j in range(7):
  o=torus('Propagating field front',(-3.5+j,0,0),.4+j*.13,.015,blue,(0,math.pi/2,0))
 target=Vector((0,0,0));start,end=((4,-13,6),(-3,-12,4)) if view=='wide' else ((0,-8,3),(2,-8,2))
elif family in ['cosmos','acceleration']:
 for j in range(180):
  theta=random.uniform(0,math.tau);v=random.uniform(-1,1);rr=random.uniform(2,10);xyz=Vector((rr*math.sqrt(1-v*v)*math.cos(theta),rr*math.sqrt(1-v*v)*math.sin(theta),rr*v));o=ball('Distant luminous galaxy',xyz,random.uniform(.025,.065),white if j%3 else gold);animate(o,'location',xyz,xyz*1.12)
 if family=='cosmos':
  for z in [-4,-2,0,2,4]:
   rr=math.sqrt(36-z*z);curve('Causal horizon cross-section',[(rr*math.cos(t),rr*math.sin(t),z) for t in [j*math.tau/128 for j in range(129)]],blue,.008)
  ball('Observer location',(0,0,0),.1,white)
 else:
  box('Accelerating laboratory',(0,0,0),(1.6,3,.8),silver);ball('Laboratory window',(0,-1.3,.1),.25,blue)
  for x in [-8,-5,-2]:curve('Causal light trajectory',[(x+.025*j*j,-5+j*.13,-2+j*.055) for j in range(65)],gold,.018)
 target=Vector((0,0,0));start,end=((10,-18,11),(6,-16,8)) if view=='wide' else ((4,-10,5),(-2,-9,4))
else:raise RuntimeError(mode)
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.lens=48
for frame,pos in [(1,start),(481,end)]:cam.location=pos;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.keyframe_insert('location',frame=frame);cam.keyframe_insert('rotation_euler',frame=frame)
for ob in s.objects:
 if ob.animation_data and ob.animation_data.action:
  for fc in ob.animation_data.action.fcurves:
   for key in fc.keyframe_points:key.interpolation='LINEAR' if fc.data_path!='hide_render' else 'CONSTANT'
out=R/'3d'/mode;out.mkdir(parents=True,exist_ok=True);s.render.filepath=str(out/'frame-')
if pilot:s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.cycles.device='CPU';s.frame_set(170);s.render.filepath=str(R/(mode+'-pilot.jpg'));bpy.ops.render.render(write_still=True)
else:bpy.ops.render.render(animation=True)
