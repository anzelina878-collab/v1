import bpy, math, random,sys,pathlib
from mathutils import Vector
mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'fusion'
R=pathlib.Path(__file__).resolve().parent;out=R/'3d'/mode;out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=2;s.cycles.use_denoising=False;s.cycles.max_bounces=2;s.cycles.diffuse_bounces=1;s.cycles.glossy_bounces=1;s.cycles.transmission_bounces=0
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.fps=25;s.render.fps_base=2;s.frame_start=1;s.frame_end=100
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.003,.006,.015,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.3
s.view_settings.view_transform='AgX'
def mat(name,col,em=.0,noise=False):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;bs=n.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*col,1);bs.inputs['Metallic'].default_value=.25;bs.inputs['Roughness'].default_value=.3;bs.inputs['Emission Color'].default_value=(*col,1);bs.inputs['Emission Strength'].default_value=em
 if noise:
  t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=6;t.inputs['Detail'].default_value=4;r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(*(v*.18 for v in col),1);r.color_ramp.elements[1].color=(*col,1);m.node_tree.links.new(t.outputs['Fac'],r.inputs[0]);m.node_tree.links.new(r.outputs[0],bs.inputs['Base Color']);m.node_tree.links.new(r.outputs[0],bs.inputs['Emission Color'])
 return m
red=mat('Hot hydrogen',(1,.12,.025),.5,True);blue=mat('Neutron / cool',(.03,.35,1),.3,True);gold=mat('Starlight',(1,.54,.12),2);cyan=mat('Spiral arms',(.12,.44,1),1.5);core=mat('Galactic core',(1,.65,.25),2.5);cold=mat('Cold',(.015,.11,.5),.3,True)
def ball(loc,r,ma,name=''):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=r,location=loc);o=bpy.context.object;o.name=name or ma.name;o.data.materials.append(ma)
 for p in o.data.polygons:p.use_smooth=True
 return o
def curve(pts,r,ma,parent=None):
 c=bpy.data.curves.new('Orbital structure','CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=2;sp=c.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,co in zip(sp.points,pts):p.co=(*co,1)
 o=bpy.data.objects.new('Spatial path',c);bpy.context.collection.objects.link(o);o.data.materials.append(ma);o.parent=parent;return o
def key(o,prop,frame,val):
 setattr(o,prop,val);o.keyframe_insert(data_path=prop,frame=frame)
def galaxy(loc,scale=1):
 root=bpy.data.objects.new('Bound spiral galaxy',None);bpy.context.collection.objects.link(root);root.location=loc;root.rotation_euler=(.2,.15,random.random()*6)
 o=ball((0,0,0),.3,core);o.scale=(1,1,.6);o.parent=root
 # Thousands of lit star surfaces occupy real three-dimensional spiral arms.
 verts=[];faces=[]
 for j in range(1800):
  arm=j%3;t=random.random();r=.15+1.5*t;ang=t*5.8+arm*math.tau/3+random.gauss(0,.16)
  x=r*math.cos(ang);y=r*math.sin(ang);z=random.gauss(0,.045*(1-t)+.01);sz=random.uniform(.006,.018)*(1.4-t*.5)
  base=len(verts);verts.extend([(x+sz,y,z),(x-sz,y,z),(x,y+sz,z),(x,y-sz,z),(x,y,z+sz),(x,y,z-sz)])
  faces.extend([tuple(base+k for k in f) for f in [(0,2,4),(2,1,4),(1,3,4),(3,0,4),(2,0,5),(1,2,5),(3,1,5),(0,3,5)]])
 mesh=bpy.data.meshes.new('Volumetric stellar population');mesh.from_pydata(verts,[],faces);ob=bpy.data.objects.new('Spiral stellar population',mesh);bpy.context.collection.objects.link(ob);ob.data.materials.append(cyan);ob.parent=root
 disk=ball((0,0,0),1,mat('Galactic haze',(.025,.055,.12),.28,True));disk.scale=(1.45,1.45,.022);disk.parent=root
 root.scale=(scale,)*3;return root
# Real volumetric objects, no flat dot plots or HUD.
if mode=='fusion':
 for j,pos in enumerate([(-2.8,-.6,.6),(2.6,.4,-.4),(-.4,2.6,.3),(.5,-2.6,-.3)]):
  o=ball(pos,.48,red,'Atomic nucleus');dest=[(-.36,-.3,.2),(.36,.3,.2),(-.28,.3,-.2),(.3,-.3,-.2)][j]
  key(o,'location',1,pos);key(o,'location',65,dest);key(o,'location',100,dest)
 # Ejected light is explicitly energy, not an extra nucleus.
 for j in range(12):
  ang=j*math.tau/12;o=ball((0,0,0),.035,gold,'Released energy');key(o,'scale',1,(0,0,0));key(o,'scale',62,(0,0,0));key(o,'scale',68,(1,1,1));key(o,'location',64,(0,0,0));key(o,'location',100,(4*math.cos(ang),4*math.sin(ang),.6*math.sin(ang*2)))
 target=(0,0,0);cam=(4,-10,5);end=(3,-9,4)
elif mode in ['expansion','crunch','rip']:
 random.seed(7)
 for j,pos in enumerate([(-3,-1.8,.2),(2.5,1.6,-.1),(-2.6,2,.7),(2.7,-2,-.6)]):
  o=galaxy(pos,.67)
  if mode=='expansion':factor1,factor2=.7,1.42
  elif mode=='crunch':factor1,factor2=1.5,.35
  else:factor1,factor2=.7,1.7
  key(o,'location',1,tuple(v*factor1 for v in pos));key(o,'location',100,tuple(v*factor2 for v in pos))
  if mode=='rip':key(o,'scale',1,(.67,.67,.67));key(o,'scale',100,(1.25,.3,.3))
 target=(0,0,0);cam=(3,-13,10);end=(4,-13,11)
elif mode=='entropy':
 hot=ball((-2,0,0),1.15,red,'Hot reservoir');cool=ball((2,0,0),1.15,cold,'Cold reservoir')
 # Separate materials converge toward the same temperature color.
 for obj,start in [(hot,(1,.12,.025,1)),(cool,(.015,.11,.5,1))]:
  bs=obj.data.materials[0].node_tree.nodes.get('Principled BSDF')
  for link in list(obj.data.materials[0].node_tree.links):
   if link.to_socket in [bs.inputs['Emission Color'],bs.inputs['Base Color']]: obj.data.materials[0].node_tree.links.remove(link)
  # The radiative colors converge; textured surfaces retain spatial depth.
  bs.inputs['Base Color'].default_value=start;bs.inputs['Base Color'].keyframe_insert('default_value',frame=1);bs.inputs['Base Color'].default_value=(.38,.15,.35,1);bs.inputs['Base Color'].keyframe_insert('default_value',frame=100)
  bs.inputs['Emission Color'].default_value=start;bs.inputs['Emission Color'].keyframe_insert('default_value',frame=1);bs.inputs['Emission Color'].default_value=(.38,.15,.35,1);bs.inputs['Emission Color'].keyframe_insert('default_value',frame=100)
 for j in range(22):
  phase=j/22;z=.65*math.sin(j*2.4);y=.55*math.cos(j*2.4);o=ball((-1,y,z),.04,gold,'Heat transfer')
  key(o,'location',1,(-1+phase*2,y,z));key(o,'location',75,(1,y,z));key(o,'scale',1,(1,1,1));key(o,'scale',80,(1,1,1));key(o,'scale',100,(0,0,0))
 target=(0,0,0);cam=(2,-11,3.6);end=(1,-10,4)
else:raise ValueError(mode)
# Soft studio illumination and a restrained rim; no arbitrary UI decoration.
for loc,energy,color,size in [((1,-5,6),900,(.6,.75,1),5),((-5,2,4),1100,(1,.35,.1),4)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=energy;o.data.color=color;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=cam);c=bpy.context.object;s.camera=c;c.data.lens=45
for f,loc in [(1,cam),(100,end)]:
 key(c,'location',f,loc);key(c,'rotation_euler',f,(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler())
for obj in bpy.data.objects:
 if obj.animation_data and obj.animation_data.action:
  for fc in obj.animation_data.action.fcurves:
   for p in fc.keyframe_points:p.interpolation='LINEAR'
s.use_nodes=True;tree=s.node_tree;tree.nodes.clear();rl=tree.nodes.new('CompositorNodeRLayers');gl=tree.nodes.new('CompositorNodeGlare');gl.glare_type='FOG_GLOW';gl.quality='LOW';gl.threshold=1.4;gl.size=7;co=tree.nodes.new('CompositorNodeComposite');tree.links.new(rl.outputs['Image'],gl.inputs[0]);tree.links.new(gl.outputs[0],co.inputs[0])
s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=90;s.render.filepath=str(out/'frame_')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'))
if '--pilot' in sys.argv:
 s.frame_set(45);s.render.filepath=str(out/'pilot.jpg');bpy.ops.render.render(write_still=True)
else:bpy.ops.render.render(animation=True)
