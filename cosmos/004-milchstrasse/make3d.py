"""KOSMION original spatial illustrations. NASA spacecraft geometry; no narration."""
import bpy,math,random,sys,pathlib,json
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parent;args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];mode=args[0] if args else 'voyager_close';pilot='--pilot' in args
out=R/'3d'/mode;out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
try:s.render.engine='BLENDER_EEVEE_NEXT'
except:s.render.engine='BLENDER_EEVEE'
s.eevee.taa_render_samples=24
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=50 if pilot else 100;s.render.fps=12;s.frame_start=1;s.frame_end=289;s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=96
s.world=bpy.data.worlds.new('Space');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.003,.004,.008,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.13;s.view_settings.view_transform='AgX'
s.use_nodes=True;n=s.node_tree.nodes;n.clear();l=s.node_tree.links;rl=n.new('CompositorNodeRLayers');g=n.new('CompositorNodeGlare');g.glare_type='FOG_GLOW';g.quality='HIGH';g.threshold=1.1;g.size=7;l.new(rl.outputs['Image'],g.inputs['Image']);o=n.new('CompositorNodeComposite');l.new(g.outputs['Image'],o.inputs[0]);random.seed(94)
def em(name,c,p=1):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();e=n.new('ShaderNodeEmission');e.inputs[0].default_value=(*c,1);e.inputs[1].default_value=p;o=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],o.inputs[0]);return m
white=em('Cool stellar light',(.65,.79,1),3);warm=em('Warm stellar light',(1,.66,.33),3);line=em('Soft orbital guide',(.28,.43,.55),.65)
def sphere(name,loc,r,mat):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32,radius=r,location=loc);o=bpy.context.object;o.name=name;o.data.materials.append(mat)
 for p in o.data.polygons:p.use_smooth=True
 return o
def star_material(name,c):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();l=m.node_tree.links;o=n.new('ShaderNodeOutputMaterial');e=n.new('ShaderNodeEmission');e.inputs[1].default_value=7.5;t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=19;t.inputs['Detail'].default_value=5;r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.17;r.color_ramp.elements[0].color=(*[v*.16 for v in c],1);r.color_ramp.elements[1].position=.85;r.color_ramp.elements[1].color=(*c,1);l.new(t.outputs['Fac'],r.inputs[0]);l.new(r.outputs[0],e.inputs[0]);l.new(e.outputs[0],o.inputs[0]);return m
starmat=star_material('Photosphere granulation',(1,.64,.25));bluestar=star_material('Hot stellar photosphere',(.55,.76,1))
def curve(name,pts,r,mat):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=2;p=c.splines.new('POLY');p.points.add(len(pts)-1)
 for v,co in zip(p.points,pts):v.co=(*co,1)
 o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);o.data.materials.append(mat);return o
# Geometry nodes instance tiny stars from one mesh. Depth and parallax are real.
def points(name,coords,radius,mat):
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(coords,[],[]);obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);ng=bpy.data.node_groups.new(name,'GeometryNodeTree');ng.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');ng.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry');n=ng.nodes;l=ng.links;i=n.new('NodeGroupInput');o=n.new('NodeGroupOutput');ico=n.new('GeometryNodeMeshIcoSphere');ico.inputs['Radius'].default_value=radius;ico.inputs['Subdivisions'].default_value=1;sm=n.new('GeometryNodeSetMaterial');sm.inputs['Material'].default_value=mat;l.new(ico.outputs['Mesh'],sm.inputs['Geometry']);inst=n.new('GeometryNodeInstanceOnPoints');l.new(i.outputs['Geometry'],inst.inputs['Points']);l.new(sm.outputs['Geometry'],inst.inputs['Instance']);l.new(inst.outputs['Instances'],o.inputs['Geometry']);obj.modifiers.new(name,'NODES').node_group=ng;return obj
coords=[]
for i in range(1100):
 v=Vector((random.gauss(0,1),random.gauss(0,1),random.gauss(0,1))).normalized()*random.uniform(65,95);coords.append(tuple(v))
points('Distant stars',coords,.025,white)
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.lens=55

def camera(start,end,target=(0,0,0),lens=55):
 cam.data.lens=lens
 for f,loc in [(1,start),(289,end)]:
  cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.keyframe_insert('location',frame=f);cam.keyframe_insert('rotation_euler',frame=f)
def light(loc,power,color=(1,.84,.65),size=5):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.color=color;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
def galaxy():
 # Layered spatial illustration derived from NASA's unlabelled Milky Way artist concept.
 # Texture carries fine dust structure, while separated planes and central stellar light add depth.
 image=bpy.data.images.load(str(R/'models/galaxy-concept.png'))
 m=bpy.data.materials.new('NASA galactic stellar disk');m.use_nodes=True
 try:m.surface_render_method='DITHERED'
 except:m.blend_method='HASHED'
 n=m.node_tree.nodes;n.clear();l=m.node_tree.links;o=n.new('ShaderNodeOutputMaterial');tex=n.new('ShaderNodeTexImage');tex.image=image;emission=n.new('ShaderNodeEmission');emission.inputs[1].default_value=1.5;l.new(tex.outputs['Color'],emission.inputs[0]);bw=n.new('ShaderNodeRGBToBW');l.new(tex.outputs['Color'],bw.inputs[0]);threshold=n.new('ShaderNodeMath');threshold.operation='GREATER_THAN';threshold.inputs[1].default_value=.008;l.new(bw.outputs[0],threshold.inputs[0]);opacity=n.new('ShaderNodeMath');opacity.operation='MULTIPLY';opacity.inputs[1].default_value=.15;l.new(threshold.outputs[0],opacity.inputs[0]);mix=n.new('ShaderNodeMixShader');transparent=n.new('ShaderNodeBsdfTransparent');l.new(opacity.outputs[0],mix.inputs[0]);l.new(transparent.outputs[0],mix.inputs[1]);l.new(emission.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],o.inputs[0])
 for j in range(13):
  bpy.ops.mesh.primitive_plane_add(size=24,location=(0,0,(j-6)*.035));o=bpy.context.object;o.name='Stellar disk depth layer';o.scale=(1-abs(j-6)*.004,1-abs(j-6)*.004,1);o.data.materials.append(m)
 sphere('Central stellar light',(0,0,0),.15,em('Warm central starlight',(1,.62,.33),2))

def animate_path(obj,pts):
 for i,p in enumerate(pts):obj.location=p;obj.keyframe_insert('location',frame=1+i*288/(len(pts)-1))
if mode.startswith('voyager') or mode.startswith('parker'):
 model='parker' if mode.startswith('parker') else 'voyager';bpy.ops.import_scene.gltf(filepath=str(R/'models'/(model+'-plain.glb')));objects=[o for o in s.objects if o.type=='MESH' and o.name!='Distant stars'];bounds=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box];low=Vector(tuple(min(v[i] for v in bounds) for i in range(3)));high=Vector(tuple(max(v[i] for v in bounds) for i in range(3)));center=(high+low)/2;scale=9/max(high-low)
 root=bpy.data.objects.new('NASA spacecraft',None);bpy.context.collection.objects.link(root)
 tops=[o for o in s.objects if o!=root and o.type!='CAMERA' and o.name!='Distant stars' and o.parent is None]
 for o in tops:o.parent=root
 root.scale=(scale,)*3;root.location=-center*scale
 light((5,-8,10),2100);light((-8,4,3),1000,(.46,.64,1),7)
 if mode.endswith('close'):camera((11,-13,6),(8,-11,4),lens=60)
 elif mode.endswith('wide'):camera((17,-21,11),(22,-27,14),lens=55)
 else:camera((-9,-13,5),(-12,-7,7),lens=63)
 if model=='parker':sphere('Sun',(-13,9,0),6,starmat);camera((10,-18,7),(12,-16,5),(-3,1,0),48)
elif mode.startswith('star'):
 o=sphere('Escaping star',(0,0,0),.95 if mode=='star_hot' else 1.7,bluestar)
 if mode=='star_close':camera((4,-6,1),(3,-5,1.8),lens=63)
 elif mode=='star_wide':camera((8,-14,5),(12,-18,7),lens=55)
 elif mode=='star_limb':camera((3.8,-4.5,.2),(3,-4,.8),lens=70)
 elif mode=='star_depart':camera((9,-24,0),(10,-30,1),lens=55)
 elif mode=='star_profile':camera((-7,-8,.2),(-4,-6,2),lens=55)
 elif mode=='star_hot':camera((3,-6,1),(5,-7,2),lens=65)
 else:camera((-5,-8,2),(6,-9,3),lens=55)
 o.keyframe_insert('rotation_euler',frame=1);o.rotation_euler[2]=.25;o.keyframe_insert('rotation_euler',frame=289)
elif mode.startswith('galaxy') or mode.startswith('escape') or mode=='halo' or mode=='fountain' or mode=='magnetic':
 galaxy();camera((18,-24,17),(21,-21,12),lens=48)
 if mode=='halo':
  m=bpy.data.materials.new('Diffuse unseen mass illustration');m.use_nodes=True;n=m.node_tree.nodes;n.clear();o=n.new('ShaderNodeOutputMaterial');v=n.new('ShaderNodeVolumePrincipled');v.inputs['Density'].default_value=.009;v.inputs['Color'].default_value=(.15,.22,.34,1);m.node_tree.links.new(v.outputs['Volume'],o.inputs['Volume']);sphere('Diffuse halo',(0,0,0),17,m);camera((32,-44,27),(38,-36,25),lens=48)
 if mode=='galaxy_edge':camera((21,-27,5),(25,-23,8),lens=58)
 if mode=='galaxy_above':camera((5,-12,29),(11,-6,31),lens=50)
 if mode.startswith('escape'):
  pts=[(8*math.cos(t),8*math.sin(t),math.sin(t)*1.2) for t in [i*4.4/120 for i in range(121)]] if mode=='escape_bound' else [(5+19*t,-3+8*t,1+10*t) for t in [i/120 for i in range(121)]]
  curve('Trajectory',pts,.018,line);o=sphere('Travelling star',pts[0],.14,warm);animate_path(o,pts);camera((28,-37,23),(32,-28,26),(5,0,2),48)
 if mode=='fountain':
  for j in range(8):
   a=j*math.pi/4;r=3+random.random()*3;pts=[(r*math.cos(a)+t*2,r*math.sin(a),8*math.sin(math.pi*t)) for t in [i/100 for i in range(101)]];curve('Galactic fountain gas',pts,.025,em('Hot diffuse gas'+str(j),(.46,.65,1),.5));o=sphere('Gas parcel',pts[0],.065,white);animate_path(o,pts)
  camera((15,-24,12),(20,-20,9),lens=46)
 if mode=='magnetic':
  for j in range(5):
   pts=[((3+j*.7)*math.cos(t), (3+j*.7)*math.sin(t),-4+8*t/(math.pi*6)) for t in [i*math.pi*6/200 for i in range(201)]];curve('Field-guided charged particle path',pts,.012,line);o=sphere('Charged particle',pts[0],.075,white);animate_path(o,pts)
  camera((13,-20,11),(18,-15,9),lens=53)
elif mode.startswith('hills'):
 data=json.load(open(R/'hills-trajectories.json'));pts1=data['a'][:112];pts2=data['b'][:112];dark=em('Black hole silhouette',(.0001,.0001,.0001),1);sphere('Central black hole',(0,0,0),.45,dark)
 # A faint ring identifies the dark central mass; trajectories use a numerical restricted three-body calculation.
 curve('Faint ambient central emission',[(.56*math.cos(t),.56*math.sin(t),0) for t in [i*2*math.pi/160 for i in range(161)]],.012,em('Faint warm ring',(.65,.35,.15),.7))
 a=sphere('Escaping component',pts1[0],.23,bluestar);b=sphere('Captured component',pts2[0],.21,starmat);animate_path(a,pts1);animate_path(b,pts2)
 if mode=='hills_close':camera((8,-13,11),(12,-9,10),(0,0,0),48)
 elif mode=='hills_wide':camera((19,-29,24),(27,-23,21),(0,0,0),48)
 else:camera((0,-2,27),(5,2,29),(0,0,0),48)
else:raise ValueError(mode)
# Camera and orbital motion use linear interpolation; no artificial acceleration at cut boundaries.
for o in s.objects:
 if o.animation_data and o.animation_data.action:
  for fc in o.animation_data.action.fcurves:
   for k in fc.keyframe_points:k.interpolation='LINEAR'
if pilot:
 s.frame_set(145);s.render.filepath=str(out/'pilot.jpg');bpy.ops.render.render(write_still=True)
else:
 s.render.filepath=str(out/'frame-');bpy.ops.render.render(animation=True)
