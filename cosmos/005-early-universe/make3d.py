"""Original spatial illustrations of light wavelength and light nuclei, not direct observations."""
import bpy,math,sys,pathlib,random
from mathutils import Vector
r=pathlib.Path(__file__).resolve().parent;mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'nuclei';pilot='--pilot' in sys.argv
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=32;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=50 if pilot else 100;s.render.fps=25;s.frame_start=1;s.frame_end=501;s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=96
s.world=bpy.data.worlds.new('Dark studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.004,.008,.018,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.25;s.view_settings.view_transform='AgX';s.use_nodes=True;n=s.node_tree.nodes;n.clear();l=s.node_tree.links;rl=n.new('CompositorNodeRLayers');g=n.new('CompositorNodeGlare');g.glare_type='FOG_GLOW';g.threshold=2;g.quality='HIGH';g.size=7;l.new(rl.outputs['Image'],g.inputs['Image']);o=n.new('CompositorNodeComposite');l.new(g.outputs['Image'],o.inputs[0])
def mat(name,c,metal=.35):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=.27;return m
def emit(name,c,power):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=power;return m
p=mat('Warm proton',(.72,.26,.08));n=mat('Cool neutron',(.12,.36,.55));light=emit('Wavelength light',(1,.24,.035),4)
def sphere(name,xyz,rad,m,parent=None):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,radius=rad,location=xyz);o=bpy.context.object;o.name=name;o.data.materials.append(m);o.parent=parent
 for face in o.data.polygons:face.use_smooth=True
 return o
def area(xyz,power,color,size):
 bpy.ops.object.light_add(type='AREA',location=xyz);o=bpy.context.object;o.data.energy=power;o.data.color=color;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
area((2,-6,8),1800,(1,.83,.61),7);area((-6,2,4),2400,(.42,.66,1),6);area((3,6,-1),1600,(1,.45,.19),5)
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.lens=52
if mode in ['nuclei','helium','lithium']:
 configs=[('Hydrogen',(-4.6,0,0),[(0,0,0)],1),('Helium',(0,0,0),[(-.38,-.38,-.3),(.38,.38,-.3),(-.38,.38,.3),(.38,-.38,.3)],2),('Lithium',(4.6,0,0),[(0,0,.65),(0,0,-.65),(.62,0,.16),(-.5,.37,.16),(-.5,-.37,.16),(.19,.59,-.35),(.19,-.59,-.35)],3)]
 if mode=='helium':configs=[configs[1]]
 if mode=='lithium':configs=[configs[2]]
 if mode!='nuclei':configs=[(x[0],(0,0,0),x[2],x[3]) for x in configs]
 for name,loc,coords,np in configs:
  root=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(root);root.location=loc
  for i,xyz in enumerate(coords):sphere(name+str(i),xyz,.51,p if i<np else n,root)
  root.rotation_euler=(0,.15,-.4);root.keyframe_insert('rotation_euler',frame=1);root.rotation_euler=(.15,.5,1.0);root.keyframe_insert('rotation_euler',frame=501)
 start=(1,-20,9) if mode=='nuclei' else (3,-9,4);end=(-1,-18,7) if mode=='nuclei' else (-2,-8,3)
else:
 # A wave rendered as a tube in real 3D; its increasing spatial wavelength explains cosmological redshift.
 curve=bpy.data.curves.new('Light wave','CURVE');curve.dimensions='3D';curve.bevel_depth=.045;curve.bevel_resolution=4;sp=curve.splines.new('POLY');sp.points.add(500)
 for i,v in enumerate(sp.points):
  x=-9+i*18/500;y=.75*math.sin(2*math.pi*(x+9)/(1.2+.10*(x+9)));v.co=(x,y,0,1)
 ob=bpy.data.objects.new('Travelling electromagnetic wave illustration',curve);bpy.context.collection.objects.link(ob);ob.data.materials.append(light)
 for f,sc in [(1,(.72,1,1)),(501,(1.12,1,1))]:ob.scale=sc;ob.keyframe_insert('scale',frame=f)
 start=(1,-16,11);end=(-2,-16,7)
for f,loc in [(1,start),(501,end)]:cam.location=loc;cam.rotation_euler=(-cam.location).to_track_quat('-Z','Y').to_euler();cam.keyframe_insert('location',frame=f);cam.keyframe_insert('rotation_euler',frame=f)
for ob in s.objects:
 if ob.animation_data and ob.animation_data.action:
  for fc in ob.animation_data.action.fcurves:
   for k in fc.keyframe_points:k.interpolation='LINEAR'
out=r/'3d'/mode;out.mkdir(parents=True,exist_ok=True);s.render.filepath=str(out/'frame-')
if pilot:s.frame_set(210);s.render.filepath=str(r/(mode+'-pilot.jpg'));bpy.ops.render.render(write_still=True)
else:bpy.ops.render.render(animation=True)
