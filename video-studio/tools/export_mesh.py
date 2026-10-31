"""Blender importer -> neutral triangle archive for the CPU raster backend.
Usage: blender -b --disable-autoexec -P tools/export_mesh.py -- source.fbx mesh.npz
"""
import sys
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector

source,target=map(Path,sys.argv[sys.argv.index('--')+1:])
bpy.ops.wm.read_factory_settings(use_empty=True)
if source.suffix.lower()=='.fbx':
    bpy.ops.import_scene.fbx(filepath=str(source.resolve()),use_anim=False)
elif source.suffix.lower() in {'.gltf','.glb'}:
    bpy.ops.import_scene.gltf(filepath=str(source.resolve()))
elif source.suffix.lower()=='.obj':
    bpy.ops.wm.obj_import(filepath=str(source.resolve()))
else:raise ValueError('Use FBX, GLB, GLTF or OBJ')
positions=[];normals=[];uv=[]
for obj in bpy.context.scene.objects:
    if obj.type!='MESH' or obj.hide_render:continue
    mesh=obj.data;mesh.calc_loop_triangles()
    uv_layer=mesh.uv_layers.active
    normal_matrix=obj.matrix_world.to_3x3().inverted().transposed()
    for triangle in mesh.loop_triangles:
        positions.append([tuple(obj.matrix_world @ mesh.vertices[v].co) for v in triangle.vertices])
        normals.append([tuple((normal_matrix @ mesh.vertices[v].normal).normalized()) for v in triangle.vertices])
        uv.append([tuple(uv_layer.data[loop].uv) if uv_layer else (0,0) for loop in triangle.loops])
p=np.asarray(positions,dtype=np.float32)
n=np.asarray(normals,dtype=np.float32)
t=np.asarray(uv,dtype=np.float32)
if not len(p):raise ValueError('No mesh')
low=p.min(axis=(0,1));high=p.max(axis=(0,1));scale=3/np.max(high-low)
center=(low+high)/2;center[2]=low[2]
p=(p-center)*scale
target.parent.mkdir(parents=True,exist_ok=True)
np.savez_compressed(target,positions=p,normals=n,uv=t)
print('EXPORTED_TRIANGLES',len(p),target)
