"""Original spatial models for the Kardaschow documentary. No narration or private media."""
import bpy,math,random,sys,pathlib,urllib.request
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parent;mode=sys.argv[sys.argv.index('--')+1];pilot='--pilot' in sys.argv;out=R/'3d'/mode;out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
try:s.render.engine='BLENDER_EEVEE_NEXT'
except:s.render.engine='BLENDER_EEVEE'
s.eevee.taa_render_samples=8;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.fps=10;s.frame_start=1;s.frame_end=192;s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=95;s.render.film_transparent=False
s.world=bpy.data.worlds.new('Deep space');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.0015,.003,.008,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.06
s.view_settings.view_transform='AgX';random.seed(307)
def mat(name,c,metal=0,rough=.35,em=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=em;return m
def emiss(name,c,strength=1):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();e=n.new('ShaderNodeEmission');e.inputs['Color'].default_value=(*c,1);e.inputs['Strength'].default_value=strength;o=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],o.inputs[0]);return m
navy=mat('Photovoltaic blue',(.012,.065,.19),.55,.28);gold=mat('Gold thermal insulation',(.62,.32,.065),.65,.3);silver=mat('Spacecraft ceramic',(.55,.63,.73),.5,.25);dark=mat('Radiator carbon',(.008,.014,.025),.25,.5);hot=emiss('Warm radiator',(1,.16,.025),1.4);starwhite=emiss('Distant starlight',(.58,.73,1),2);amber=emiss('Distant warm starlight',(1,.6,.22),2)
def sphere(name,loc,r,material,segments=48):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=24,radius=r,location=loc);o=bpy.context.object;o.name=name;o.data.materials.append(material)
 for f in o.data.polygons:f.use_smooth=True
 return o
def box(name,loc,scale,material,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material)
 if bevel:
  b=o.modifiers.new('Soft manufactured edges','BEVEL');b.width=bevel;b.segments=2;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o
def curve(name,points,r,material):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=2;p=c.splines.new('POLY');p.points.add(len(points)-1)
 for q,co in zip(p.points,points):q.co=(*co,1)
 o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);o.data.materials.append(material);return o
def light(loc,energy,color=(1,.87,.66),size=5):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=energy;o.data.color=color;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler();return o
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.lens=42

def camera(start,end,target=(0,0,0),lens=42):
 cam.data.lens=lens
 for frame,loc in [(1,start),(192,end)]:
  cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.keyframe_insert('location',frame=frame);cam.keyframe_insert('rotation_euler',frame=frame)
def rotate(o,axis=2,angle=.5):
 o.keyframe_insert('rotation_euler',frame=1);o.rotation_euler[axis]+=angle;o.keyframe_insert('rotation_euler',frame=192)
def star_background(count=170):
 # Linked low-poly spheres occupy actual 3D positions, rather than a flat star card.
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.025,location=(0,0,80));proto=bpy.context.object;proto.name='Background star';proto.data.materials.append(starwhite)
 for i in range(count):
  o=bpy.data.objects.new('Far star',proto.data);bpy.context.collection.objects.link(o);o.location=(random.uniform(-35,35),random.uniform(10,45),random.uniform(-22,22));o.scale=(random.uniform(.4,1.8),)*3
star_background()

def texture(name,url):
 d=R/'textures';d.mkdir(exist_ok=True);p=d/name
 if not p.exists():p.write_bytes(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'KosmionRender/1.0'}),timeout=60).read())
 return bpy.data.images.load(str(p),check_existing=True)
def earth(night=False):
 m=mat('NASA Earth surface',(.04,.13,.3),.05,.46);n=m.node_tree.nodes;p=n.get('Principled BSDF');t=n.new('ShaderNodeTexImage')
 if night:
  t.image=texture('earth_night.jpg','https://www.solarsystemscope.com/textures/download/2k_earth_nightmap.jpg');m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color']);m.node_tree.links.new(t.outputs['Color'],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=.8
 else:
  t.image=texture('earth_day.png','https://svs.gsfc.nasa.gov/vis/a000000/a002900/a002915/bluemarble-2048.png');m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 o=sphere('Earth',(-.2,0,0),2,m,96);o.rotation_euler=(math.radians(78),0,.4);rotate(o,2,.55)
 # Restrained physical silhouette, no glow shell masking the map.
 light((-6,-4,4),1050 if night else 1700,(.65,.8,1),5);light((5,1,1),400,(.2,.4,1),4);camera((0,-9,2),(2,-10,2.7),(-.2,0,0),48)

def sun(radius=1.35):
 m=emiss('Stellar photosphere',(1,.38,.055),2);n=m.node_tree.nodes;e=next(x for x in n if x.type=='EMISSION');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=8;noise.inputs['Detail'].default_value=3;r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(.6,.035,.005,1);r.color_ramp.elements[1].color=(1,.73,.16,1);m.node_tree.links.new(noise.outputs['Fac'],r.inputs[0]);m.node_tree.links.new(r.outputs[0],e.inputs['Color']);return sphere('Star', (0,0,0),radius,m,64)

def collectors(dense=False):
 sun();light((0,-3,5),2200,(1,.65,.3),5);light((-5,-7,3),1200,(.4,.62,1),6)
 # Each ring is an independent orbital family; panels face the star radially.
 parent=bpy.data.objects.new('Orbital assembly',None);bpy.context.collection.objects.link(parent)
 template=None
 rings=10 if dense else 5;per=36 if dense else 18
 for ring in range(rings):
  incl=(ring/(rings-1)-.5)*math.pi*.85;radius=3.1+(ring%3)*.42
  for i in range(per):
   a=i/per*math.tau+ring*.21;loc=Vector((radius*math.cos(a),radius*math.sin(a)*math.cos(incl),radius*math.sin(a)*math.sin(incl)))
   if template is None:template=box('Collector',loc,(.28,.4,.022),navy);o=template
   else:o=bpy.data.objects.new('Collector',template.data);bpy.context.collection.objects.link(o);o.location=loc
   o.rotation_euler=loc.to_track_quat('Z','Y').to_euler();o.parent=parent
 rotate(parent,2,.34 if dense else .6);camera((0,-14,6),(3,-13,4),(0,0,0),43)

def galaxy():
 mats=[emiss('Blue stellar population',(.28,.5,1),2),emiss('Warm stellar population',(1,.55,.18),2),emiss('Bright stellar population',(.75,.85,1),2)]
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.04);proto=bpy.context.object;proto.name='Spiral star';proto.data.materials.append(mats[0]);parent=bpy.data.objects.new('Rotating galactic disk',None);bpy.context.collection.objects.link(parent);proto.parent=parent
 for i in range(1700):
  r=7*math.sqrt(random.random());arm=i%4;a=arm*math.pi/2+r*.52+random.gauss(0,.18);o=bpy.data.objects.new('Galactic star',proto.data.copy() if i<3 else proto.data);bpy.context.collection.objects.link(o);o.location=(r*math.cos(a),r*math.sin(a),random.gauss(0,.12+.025*r));o.scale=(random.uniform(.35,1.35),)*3;o.parent=parent
 for i in range(130):
  r=random.random()**.6*1.2;a=random.random()*math.tau;o=sphere('Central bulge star',(r*math.cos(a),r*math.sin(a),random.gauss(0,.28)),.035,mats[1],8);o.parent=parent
 rotate(parent,2,.18);camera((1,-16,10),(5,-15,8),(0,0,0),38)

def satellite():
 body=box('Insulated spacecraft',(0,0,0),(1.3,1,1.2),gold,.09)
 for x in [-1,1]:
  box('Solar array',(x*2.6,0,0),(3,.07,2),navy,.02)
  for k in range(6):box('Panel bus',(x*2.6-1.35+k*.54,-.045,0),(.018,.015,1.97),silver)
 box('Radiator',(0,.6,0),(.96,.07,.94),dark,.02)
 for z in [-.36,-.12,.12,.36]:box('Radiator channel',(0,-.57,z),(1.03,.03,.022),hot,.005)
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=.45,location=(0,0,.85));bpy.context.object.scale=(1,1,.25);bpy.context.object.data.materials.append(silver)
 light((-5,-6,6),1500,(1,.83,.6),4);light((4,2,2),1200,(.3,.55,1),5);camera((6,-11,6),(8,-9,4),(0,0,0),45)

def dust():
 sun(1.5);light((-3,-5,5),1800,(1,.6,.25),5);warm=mat('Dust grains',(.22,.11,.045),0,.9);p=bpy.data.objects.new('Dust stream',None);bpy.context.collection.objects.link(p);proto=None
 for i in range(230):
  loc=(random.gauss(0,2.3),random.gauss(-2,.35),random.gauss(0,.65))
  if proto is None:proto=sphere('Dust grain',loc,.05,warm,8);o=proto
  else:o=bpy.data.objects.new('Dust grain',proto.data);bpy.context.collection.objects.link(o);o.location=loc;o.scale=(random.uniform(.25,1.3),)*3
  o.parent=p
 p.location=(-2,0,0);p.keyframe_insert('location',frame=1);p.location=(2,0,0);p.keyframe_insert('location',frame=192);camera((0,-11,3),(1,-11,2),(0,0,0),47)

def background():
 # Near star and an extended far background source, placed at different depths.
 near=emiss('Foreground star',(.6,.78,1),2.5);sphere('Nearby foreground star',(-1,-2,.15),.22,near,32)
 far=emiss('Background dusty galaxy',(1,.35,.1),1.1)
 for i in range(320):
  r=random.random()**.5*2.2;a=random.random()*math.tau;sphere('Background galactic light',(r*math.cos(a)+.15,7+random.gauss(0,.35),r*math.sin(a)*.35),.025,far,8)
 camera((0,-13,2),(2.1,-13,2),(-.1,2,0),47)

if mode=='planet_day':earth(False)
elif mode=='planet_night':earth(True)
elif mode=='dyson':collectors(False)
elif mode=='dyson_dense':collectors(True)
elif mode=='galaxy':galaxy()
elif mode=='radiator':satellite()
elif mode=='dust':dust()
elif mode=='background':background()
else:raise ValueError(mode)
# Linear motion avoids camera acceleration at repeated edit boundaries.
for o in bpy.data.objects:
 if o.animation_data and o.animation_data.action:
  for fc in o.animation_data.action.fcurves:
   for k in fc.keyframe_points:k.interpolation='LINEAR'
s.use_nodes=True;n=s.node_tree.nodes;n.clear();rl=n.new('CompositorNodeRLayers');g=n.new('CompositorNodeGlare');g.glare_type='FOG_GLOW';g.quality='MEDIUM';g.threshold=1.3;g.size=7;g.mix=-.8;comp=n.new('CompositorNodeComposite');s.node_tree.links.new(rl.outputs['Image'],g.inputs['Image']);s.node_tree.links.new(g.outputs['Image'],comp.inputs['Image'])
if pilot:
 s.frame_set(96);s.render.filepath=str(out/'pilot.jpg');bpy.ops.render.render(write_still=True)
else:
 for frame in range(1,193):
  s.frame_set(frame);s.render.filepath=str(out/f'frame_{frame:04}.jpg');bpy.ops.render.render(write_still=True)
print('ORIGINAL SCENE COMPLETE',mode,flush=True)
