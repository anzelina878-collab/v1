"""FFmpeg scene compiler using the existing Painter for typography/composition.

Preserves genuine 3D/video motion, uses gentle camera motion for declared static
photos, and renders short frame sequences for diagrams. No fake 3D transforms.
"""
import hashlib
import json
import math
import subprocess
from pathlib import Path

from PIL import Image

from .project import ROOT
from .visuals import Painter,country_flag,output_size
from .cli import safe_output,video_filter


def execute(cmd, log):
    with open(log,'w') as err:
        p=subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=err)
    if p.returncode:
        raise ValueError(f"FFmpeg: {Path(log).read_text()[-1800:]}")


def caption(painter,scene,path):
    im=Image.new('RGBA',(1920,1080))
    if scene.get('full_bleed'):
        im.paste(Image.new('RGBA',(1920,250),(242,243,240,235)),(0,830))
    country_flag(im,scene['country'],90,855)
    painter.text(im,scene.get('title',''),(90,930,1720,115),78,bold=True)
    if scene.get('show_source'):
        painter.text(im,scene.get('source',''),(850,1034,980,30),18,'muted',align='right')
    im.save(path)


def render_fast(project,target,preset='fast',crf=22):
    target=safe_output(project,target)
    if target.suffix.lower()!='.mp4':raise ValueError('Output must be MP4')
    if project.get('_frames')!=round(project['_duration']*project['fps']):
        raise ValueError('Fast compiler requires a complete timeline matching the supplied audio. Use strict audio_policy')
    painter=Painter(project)
    width,height,fps=project['width'],project['height'],project['fps']
    identity=hashlib.sha256(Path(project['_path']).read_bytes()).hexdigest()[:16]
    cache=ROOT/'work'/'compiled'/identity;cache.mkdir(parents=True,exist_ok=True)
    clips=[]
    for index,scene in enumerate(project['scenes']):
        frames=scene['_end_frame']-scene['_start_frame']
        duration=frames/fps
        directory=cache/f'{index:04d}';directory.mkdir(exist_ok=True)
        out=directory/'scene.mp4'
        # Include media stats, fonts, theme and renderer implementation in the cache key.
        dependencies=[Path(__file__),Path(__file__).with_name('visuals.py'),Path(project['theme']['font']),Path(project['theme']['font_bold'])]
        for obj in [scene]+scene.get('sides',[])+scene.get('items',[]):
            dependencies += [Path(obj[k]) for k in ('_image','_video') if obj.get(k)]
        fingerprint=hashlib.sha256(json.dumps({'scene':scene,'theme':project['theme'],'style':project.get('style'),'title_motion':project.get('title_motion',False),'resolution':[width,height,fps],'encoding':[crf,preset],'files':[(str(p),p.stat().st_size,p.stat().st_mtime_ns) for p in dependencies]},sort_keys=True).encode()).hexdigest()
        stamp=directory/'cache.txt'
        clips.append(out)
        if out.exists() and stamp.exists() and stamp.read_text()==fingerprint:
            print(f'CACHE {index+1}/{len(project["scenes"])} {scene["id"]}',flush=True);continue
        print(f'COMPILE {index+1}/{len(project["scenes"])} {scene["id"]} {duration:.2f}s',flush=True)
        cmd=['ffmpeg','-y','-v','error','-threads','1']
        filters=[]
        if scene['type']=='studio':
            if scene.get('_video'):
                if scene.get('loop'):cmd += ['-stream_loop','-1']
                cmd += ['-ss',str(scene.get('in',0)),'-i',scene['_video']]
                filters.append(f'[0:v]fps={fps},'+video_filter(width,height,scene.get('fit','contain'))+',setsar=1[base]')
            else:
                base=directory/'subject.png'
                im=painter.render({**scene,'_subject_only':True},2,index,scene['start']+2)
                output_size(im,width,height).save(base)
                cmd += ['-loop','1','-framerate',str(fps),'-i',str(base)]
                if scene.get('camera_motion',True):
                    # This is explicitly a camera move over a static photo, never labelled 3D.
                    filters.append(f"[0:v]zoompan=z='1+0.018*on/{frames}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={width}x{height}:fps={fps},setsar=1[base]")
                else:filters.append('[0:v]setsar=1[base]')
            labels=directory/'labels.png';caption(painter,scene,labels)
            cmd += ['-loop','1','-framerate',str(fps),'-i',str(labels)]
            start=float(scene.get('label_start',0))
            animated=project.get('title_motion') and scene.get('animate_title',True)
            if animated:
                filters.append(f'[1:v]scale={width}:{height},format=rgba,fade=t=in:st={start}:d=0.45:alpha=1[caption]')
                dy=24*height/1080
                expression=f"{dy}*pow(1-min(1,max(0,(t-{start})/0.55)),3)"
                filters.append(f"[base][caption]overlay=x=0:y='{expression}':enable='gte(t,{start})'[p0]")
            else:
                filters.append(f'[1:v]scale={width}:{height}[caption]')
                filters.append(f"[base][caption]overlay=0:0:enable='gte(t,{start})'[p0]")
            last='p0'
            for j,c in enumerate(scene.get('callouts',[])):
                overlay=Image.new('RGBA',(1920,1080))
                painter.tag(overlay,c['text'],1230,100,600)
                file=directory/f'callout-{j}.png';overlay.save(file)
                cmd += ['-loop','1','-framerate',str(fps),'-i',str(file)]
                filters.append(f'[{j+2}:v]scale={width}:{height}[c{j}]')
                filters.append(f"[{last}][c{j}]overlay=0:0:enable='gte(t,{c['start']})*lt(t,{c['end']})'[p{j+1}]")
                last=f'p{j+1}'
            filters.append(f'[{last}]format=yuv420p[final]')
            cmd += ['-filter_complex',';'.join(filters),'-map','[final]','-filter_complex_threads','1']
        elif scene['type']=='footage':
            if scene.get('loop'):cmd += ['-stream_loop','-1']
            cmd += ['-ss',str(scene.get('in',0)),'-i',scene['_video'],'-vf',f'fps={fps},'+video_filter(width,height,scene.get('fit','cover'))+',setsar=1']
        else:
            if scene['type'] in {'diagram','bars','intro','section','outro'} or project.get('title_motion'):
                animation_frames=min(frames,max(1,round((1.8 if scene['type'] in {'diagram','bars'} else 1.2 if project.get('title_motion') else .8)*fps)))
                for f in range(animation_frames):
                    im=painter.render(scene,f/fps,index,scene['start']+f/fps)
                    output_size(im,width,height).save(directory/f'anim-{f:04d}.png')
                cmd += ['-framerate',str(fps),'-i',str(directory/'anim-%04d.png'),'-vf',f'tpad=stop_mode=clone:stop_duration={duration},setsar=1']
            else:
                plate=directory/'plate.png'
                im=painter.render(scene,min(2,max(0,duration-1/fps)),index,scene['start']+min(2,duration))
                output_size(im,width,height).save(plate)
                cmd += ['-loop','1','-framerate',str(fps),'-i',str(plate),'-vf','setsar=1']
        cmd += ['-an','-frames:v',str(frames),'-r',str(fps),'-c:v','libx264','-preset',preset,'-crf',str(crf),'-pix_fmt','yuv420p','-threads','2','-video_track_timescale','15360','-movflags','+faststart',str(out)]
        execute(cmd,directory/'ffmpeg.log')
        stamp.write_text(fingerprint)
    concat=cache/'concat.txt'
    concat.write_text('\n'.join("file '"+str(p).replace("'","'\\''")+"'" for p in clips)+'\n')
    pending=target.with_name('.'+target.stem+'.pending.mp4')
    cmd=['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(concat)]
    if project.get('_audio'):
        cmd += ['-i',project['_audio'],'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-af','apad']
    else:cmd += ['-map','0:v:0','-c:v','copy','-an']
    cmd += ['-t',str(project['_frames']/fps),'-movflags','+faststart',str(pending)]
    try:
        execute(cmd,cache/'concat.log');pending.replace(target)
    finally:pending.unlink(missing_ok=True)
    manifest={'renderer':'FFmpeg scene compiler + existing Pillow templates','config_sha256':identity,'width':width,'height':height,'fps':fps,'frames':project['_frames'],'duration':project['_frames']/fps,'audio_included':bool(project.get('_audio')),'scenes':len(project['scenes'])}
    target.with_suffix('.render.json').write_text(json.dumps(manifest,indent=2))
    print('FINAL_READY',target,flush=True)
