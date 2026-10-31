"""Reusable real-geometry turntable renderer; run inside Blender 4.x.

blender --background --disable-autoexec -t 3 --python tools/blender_turntable.py --
  --model assets/model.glb --output output/model.mp4 --duration 6 --fps 30

The importer does not certify model identity. Verify identity and license in the
episode asset manifest before using the output in a documentary.
"""
import argparse
import hashlib
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def empty(name):
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    return obj


def point_at(obj, target):
    direction = Vector(target)-obj.location
    obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


def material(name, color, metallic=0, roughness=.45):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    return mat


def bounds(objects):
    points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    low = Vector([min(v[i] for v in points) for i in range(3)])
    high = Vector([max(v[i] for v in points) for i in range(3)])
    return low, high


def import_model(path):
    ext = path.suffix.lower()
    if ext in {'.glb', '.gltf'}:
        bpy.ops.import_scene.gltf(filepath=str(path))
    elif ext == '.obj':
        bpy.ops.wm.obj_import(filepath=str(path))
    elif ext == '.fbx':
        bpy.ops.import_scene.fbx(filepath=str(path), use_anim=False)
    elif ext == '.blend':
        with bpy.data.libraries.load(str(path), link=False) as (source, destination):
            destination.objects = source.objects
        for obj in destination.objects:
            if obj is not None:
                bpy.context.collection.objects.link(obj)
    else:
        raise ValueError('Supported model formats: GLB, GLTF, OBJ, FBX, BLEND')


def calibration_model():
    """Asymmetric fixture for pipeline checks; never a real equipment model."""
    steel = material('Calibration steel', (.12, .2, .23), .75, .32)
    brass = material('Calibration brass', (.6, .38, .12), .7, .3)
    for location, scale, mat in [((0,0,.4),(1.5,.5,.4),steel), ((-.8,0,1),(.25,.4,.35),brass), ((.5,.15,.85),(.55,.2,.1),brass)]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=location)
        obj = bpy.context.object
        obj.scale = scale
        obj.data.materials.append(mat)
        bevel = obj.modifiers.new('Rounded edges', 'BEVEL')
        bevel.width = .06
        bevel.segments = 3
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model')
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--output', required=True)
    parser.add_argument('--duration', type=float, default=6)
    parser.add_argument('--fps', type=int, default=30)
    parser.add_argument('--width', type=int, default=1920)
    parser.add_argument('--height', type=int, default=1080)
    parser.add_argument('--yaw-start', type=float, default=-30)
    parser.add_argument('--yaw-end', type=float, default=30)
    parser.add_argument('--model-rotation', type=float, nargs=3, default=(0,0,0))
    parser.add_argument('--samples', type=int, default=32)
    parser.add_argument('--engine', choices=['CYCLES', 'BLENDER_EEVEE_NEXT'], default='CYCLES')
    parser.add_argument('--texture-prefix', help='Optional PBR atlas prefix, e.g. /path/M4A1')
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    if bool(args.model) == bool(args.self_test):
        raise ValueError('Choose a model OR --self-test')
    if not math.isfinite(args.duration) or args.duration <= 0 or not 1 <= args.fps <= 60:
        raise ValueError('Invalid duration or fps')
    if min(args.width,args.height) < 64 or args.width % 2 or args.height % 2:
        raise ValueError('Resolution must be positive and even')
    if not all(math.isfinite(v) for v in [args.yaw_start,args.yaw_end,*args.model_rotation]):
        raise ValueError('Angles must be finite')
    output = Path(args.output).resolve()
    if output.exists() and not args.overwrite:
        raise ValueError('Output exists; use a new version or --overwrite')
    output.parent.mkdir(parents=True,exist_ok=True)
    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        raise ValueError('FFmpeg is required')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if args.self_test:
        calibration_model()
    else:
        source = Path(args.model).resolve()
        if not source.is_file():
            raise ValueError('Model file is missing')
        import_model(source)
    imported = list(bpy.context.scene.objects)
    meshes = [o for o in imported if o.type == 'MESH' and not o.hide_render]
    if not meshes:
        raise ValueError('No renderable mesh in model')
    if args.texture_prefix:
        mat=material('Source PBR atlas',(.18,.19,.18),.2,.45)
        nodes,links=mat.node_tree.nodes,mat.node_tree.links
        bsdf=nodes.get('Principled BSDF')
        for suffix,socket in [('Base_Color','Base Color'),('Metallic','Metallic'),('Roughness','Roughness'),('Normal','Normal')]:
            path=Path(args.texture_prefix+'_'+suffix+'.png').resolve()
            if not path.is_file():
                raise ValueError('Missing source texture: '+str(path))
            image=bpy.data.images.load(str(path))
            image.pack()
            if suffix!='Base_Color':image.colorspace_settings.name='Non-Color'
            tex=nodes.new('ShaderNodeTexImage');tex.image=image
            if suffix=='Normal':
                normal=nodes.new('ShaderNodeNormalMap')
                links.new(tex.outputs['Color'],normal.inputs['Color'])
                links.new(normal.outputs['Normal'],bsdf.inputs['Normal'])
            else:links.new(tex.outputs['Color'],bsdf.inputs[socket])
        for obj in meshes:
            obj.data.materials.clear();obj.data.materials.append(mat)
    # Remove arbitrary imported animation, cameras and lighting.
    for obj in imported:
        obj.animation_data_clear()
        if obj.type in {'CAMERA','LIGHT'}:
            bpy.data.objects.remove(obj, do_unlink=True)
    imported = [o for o in bpy.context.scene.objects]
    orient = empty('Model orientation')
    for obj in imported:
        if obj.parent is None:
            world = obj.matrix_world.copy()
            obj.parent = orient
            obj.matrix_world = world
    orient.rotation_euler = tuple(math.radians(v) for v in args.model_rotation)
    bpy.context.view_layer.update()
    low, high = bounds(meshes)
    extent = high-low
    if max(extent) <= 0:
        raise ValueError('Degenerate geometry')
    normal = empty('Normalized model')
    orient.parent = normal
    scale = 3/max(extent)
    normal.scale = (scale,)*3
    normal.location = (-(low.x+high.x)/2*scale, -(low.y+high.y)/2*scale, -low.z*scale+.025)
    rig = empty('Turntable yaw')
    normal.parent = rig
    bpy.context.view_layer.update()
    low,high = bounds(meshes)
    center = Vector((0,0,(low.z+high.z)/2))
    bpy.ops.object.camera_add(location=(4,-7,3.1+center.z))
    camera = bpy.context.object
    camera.name = 'Studio camera'
    point_at(camera,center)
    camera.data.type = 'ORTHO'
    camera.data.shift_y = -.07
    bpy.context.scene.camera = camera
    # Fit the object over the entire yaw interval, not just the first frame.
    max_x,max_y = 0,0
    inverse = camera.rotation_euler.to_matrix().transposed()
    for i in range(25):
        rig.rotation_euler.z = math.radians(args.yaw_start+(args.yaw_end-args.yaw_start)*i/24)
        bpy.context.view_layer.update()
        for obj in meshes:
            for corner in obj.bound_box:
                point = inverse @ (obj.matrix_world @ Vector(corner)-camera.location)
                max_x=max(max_x,abs(point.x));max_y=max(max_y,abs(point.y))
    aspect=args.width/args.height
    # Blender's landscape camera ortho_scale is the horizontal span.
    camera.data.ortho_scale=max(max_x*2,max_y*2*aspect)*1.4
    frames=max(2,round(args.duration*args.fps))
    for frame,angle in [(1,args.yaw_start),(frames,args.yaw_end)]:
        rig.rotation_euler.z=math.radians(angle)
        rig.keyframe_insert(data_path='rotation_euler',frame=frame)
    for curve in rig.animation_data.action.fcurves:
        for key in curve.keyframe_points:
            key.interpolation='LINEAR'
    floor=material('Neutral studio floor',(.88,.89,.87),0,.75)
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,0))
    bpy.context.object.data.materials.append(floor)
    for name,location,energy,size in [('Key',(-3,-4,6),650,5),('Fill',(4,-1,4),400,4),('Rim',(1,4,5),550,4)]:
        bpy.ops.object.light_add(type='AREA',location=location)
        light=bpy.context.object;light.name=name
        light.data.energy=energy;light.data.shape='DISK';light.data.size=size
        point_at(light,center)
    scene=bpy.context.scene
    scene.world=bpy.data.worlds.new('Studio world')
    scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.82,.84,.81,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value=.35
    scene.render.engine=args.engine
    scene.cycles.device='CPU';scene.cycles.samples=args.samples
    # Some headless builds omit OpenImageDenoise; never fail a render for that optional feature.
    scene.cycles.use_denoising=bool(getattr(bpy.app.build_options, 'openimagedenoise', False))
    scene.render.resolution_x=args.width;scene.render.resolution_y=args.height
    scene.render.resolution_percentage=100;scene.render.fps=args.fps
    scene.frame_start=1;scene.frame_end=frames
    scene.render.image_settings.file_format='PNG'
    scene.view_settings.view_transform='AgX'
    scene.render.film_transparent=False
    frames_dir=output.parent/(output.stem+'_frames')
    frames_dir.mkdir(exist_ok=True)
    scene.render.filepath=str(frames_dir/'frame_')
    bpy.ops.wm.save_as_mainfile(filepath=str(output.with_suffix('.blend')))
    bpy.ops.render.render(animation=True)
    cmd=[ffmpeg,'-y','-v','error','-framerate',str(args.fps),'-i',str(frames_dir/'frame_%04d.png'),'-frames:v',str(frames),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(output)]
    subprocess.run(cmd,check=True)
    metadata={'motion_kind':'true_3d','self_test_only':args.self_test,'model':str(Path(args.model).resolve()) if args.model else None,'model_sha256':hashlib.sha256(Path(args.model).read_bytes()).hexdigest() if args.model else None,'yaw_start':args.yaw_start,'yaw_end':args.yaw_end,'frames':frames,'fps':args.fps,'width':args.width,'height':args.height,'engine':args.engine,'identity_verified_by_renderer':False,'license_verified_by_renderer':False}
    output.with_suffix('.3d.json').write_text(json.dumps(metadata,indent=2))
    print('TURNTABLE_READY',output)


if __name__=='__main__':
    main()
