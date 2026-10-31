"""Assemble a full revision from validated prepared excerpts and unchanged base shots.

Avoids another lossy encode of already prepared archive footage. Reuses base
scene caches ONLY if scene data, renderer/assets fingerprint and global style
still match. Does not retime or rewrite user narration.
"""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from studio.project import ROOT,load_project,probe
from studio import fast


def fingerprint(project,scene,crf,preset):
    # Matches the scene compiler's recorded fingerprint; fail closed on changes.
    deps=[Path(fast.__file__),Path(fast.__file__).with_name('visuals.py'),Path(project['theme']['font']),Path(project['theme']['font_bold'])]
    for obj in [scene]+scene.get('sides',[])+scene.get('items',[]):
        deps += [Path(obj[k]) for k in ['_image','_video'] if obj.get(k)]
    return hashlib.sha256(json.dumps({'scene':scene,'theme':project['theme'],'style':project.get('style'),'title_motion':project.get('title_motion',False),'resolution':[project['width'],project['height'],project['fps']],'encoding':[crf,preset],'files':[(str(p),p.stat().st_size,p.stat().st_mtime_ns) for p in deps]},sort_keys=True).encode()).hexdigest()


def compatible_clip(path,project,frames):
    info=probe(path);v=next(s for s in info['streams'] if s['codec_type']=='video')
    numerator,denominator=map(float,v['avg_frame_rate'].split('/'))
    if (v['width'],v['height'],v['codec_name'],v.get('pix_fmt'))!=(project['width'],project['height'],'h264','yuv420p'):
        raise ValueError('Clip format mismatch: '+str(path))
    if abs(numerator/denominator-project['fps'])>.001 or int(v.get('nb_frames',-1))!=frames:
        raise ValueError('Clip frame count/fps mismatch: '+str(path))
    return info


def assemble(base_path,new_path,target,crf=25,preset='fast'):
    original=load_project(base_path);new=load_project(new_path)
    for key in ['width','height','fps','theme','style','title_motion','brand','footer']:
        if original.get(key)!=new.get(key):raise ValueError('Base global style changed: '+key)
    if original['_audio']!=new['_audio'] or original['_frames']!=new['_frames']:
        raise ValueError('This revision must preserve the full original audio and duration')
    base_sha=hashlib.sha256(Path(base_path).read_bytes()).hexdigest()[:16]
    old={s['id']:(i,s) for i,s in enumerate(original['scenes'])}
    clips=[];records=[]
    for s in new['scenes']:
        count=s['_end_frame']-s['_start_frame']
        if s.get('archive_edit') or s.get('archive_sequence'):
            clip=Path(s['_video']);compatible_clip(clip,new,count)
            records.append({'scene':s['id'],'origin':'prepared_actual_archive','path':s['video'],'frames':count})
        else:
            index,previous=old[s['id']]
            if s!=previous:raise ValueError('Unprepared scene changed: '+s['id'])
            folder=ROOT/'work'/'compiled'/base_sha/f'{index:04d}';clip=folder/'scene.mp4'
            if (folder/'cache.txt').read_text()!=fingerprint(original,previous,crf,preset):
                raise ValueError('Base scene/assets changed; rerender base first: '+s['id'])
            compatible_clip(clip,new,count)
            records.append({'scene':s['id'],'origin':'validated_unchanged_base_scene','frames':count})
        clips.append(clip)
    target=target.resolve();target.parent.mkdir(exist_ok=True,parents=True)
    if target.exists():raise ValueError('Preserve existing output; choose a new revision filename')
    work=ROOT/'work'/'revision-assembly'/target.stem;work.mkdir(exist_ok=True,parents=True)
    concat=work/'concat.txt';concat.write_text('\n'.join("file '"+str(p).replace("'","'\\''")+"'" for p in clips)+'\n')
    pending=target.with_name('.'+target.stem+'.pending.mp4')
    cmd=['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(concat),'-i',new['_audio'],'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-af','apad','-t',str(new['_frames']/new['fps']),'-movflags','+faststart',str(pending)]
    subprocess.run(cmd,check=True);pending.replace(target)
    result={'config':Path(new_path).name,'base_config':Path(base_path).name,'scenes':records,'frames':new['_frames'],'duration':new['_frames']/new['fps'],'original_audio_preserved':True,'video_encoding':'prepared H264 excerpts and unchanged cached shots copied without another lossy encode','sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
    target.with_suffix('.assembly.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print('FULL_REVISION_READY',target,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('base',type=Path);p.add_argument('revision',type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    assemble(a.base.resolve(),a.revision.resolve(),a.output)
