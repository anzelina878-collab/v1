"""Prepare timed real-video excerpts, with small source credits and factual overlays.
Raw sources stay in a local library; episode JSON contains a reviewed selection.
Usage: python tools/prepare_archive.py EPISODE --library DIRECTORY
"""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PIL import Image,ImageDraw
from studio.project import ROOT,THEME,probe
from studio.visuals import Painter,country_flag


def prepare(config,library,only=None):
    base=config.parent;p=json.loads(config.read_text());sources=json.loads((base/p['archive_sources']).read_text())['sources']
    theme={**THEME,**p.get('theme',{})}
    for key in ['font','font_bold']:
        path=Path(theme[key]);theme[key]=str(path if path.is_absolute() else ROOT/path)
    painter=Painter({'theme':theme,'style':'minimal'})
    work=ROOT/'work'/'archive-preparation';work.mkdir(exist_ok=True)
    for scene in p['scenes']:
        edit=scene.get('archive_edit')
        if not edit or (only and scene['id'] not in only):continue
        source=sources[edit['source']];raw=(library/source['local_file']).resolve()
        info=probe(raw);vid=next(s for s in info['streams'] if s['codec_type']=='video')
        duration=float(info['format'].get('duration',0));start=edit['in'];frames=round(scene['duration']*p['fps'])
        if duration<=0 or start<0 or start+frames/p['fps']>duration+.01:raise ValueError('Source interval invalid: '+scene['id'])
        target=base/scene['video'];target.parent.mkdir(exist_ok=True,parents=True)
        fingerprint=hashlib.sha256(json.dumps({'edit':edit,'scene':scene,'source':source,'raw':(raw.stat().st_size,raw.stat().st_mtime_ns),'tool':Path(__file__).read_text()},sort_keys=True).encode()).hexdigest()
        stamp=target.with_suffix('.archive.json')
        if target.exists() and stamp.exists() and json.loads(stamp.read_text()).get('preparation_sha256')==fingerprint:
            print('ARCHIVE_CACHE',scene['id'],flush=True);continue
        layer=Image.new('RGBA',(1920,1080));draw=ImageDraw.Draw(layer)
        # Compact lower strip, rather than the older quarter-frame label panel.
        draw.rectangle((0,974,1920,1080),fill=(15,22,18,155))
        country_flag(layer,edit['country'],44,991,width=64,height=43)
        painter.text(layer,scene.get('title',''),(132,987,1500,60),38,color='#FFFFFF',bold=True)
        painter.text(layer,source['credit'],(610,1047,1265,29),18,color='#FFFFFF',align='right')
        caption=work/(scene['id']+'.png');layer.save(caption,compress_level=1)
        cmd=['ffmpeg','-y','-v','error','-threads','1','-ss',str(start),'-i',str(raw),'-loop','1','-framerate',str(p['fps']),'-i',str(caption)]
        filters=[f'[0:v]fps={p["fps"]},scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1[base]',
                 '[1:v]format=rgba,fade=t=in:st=0:d=0.35:alpha=1[label]', '[base][label]overlay=0:0[p0]']
        last='p0'
        for i,c in enumerate(scene.get('callouts',[])):
            overlay=Image.new('RGBA',(1920,1080));painter.tag(overlay,c['text'],1230,100,600)
            file=work/(scene['id']+f'-fact-{i}.png');overlay.save(file,compress_level=1)
            cmd+=['-loop','1','-framerate',str(p['fps']),'-i',str(file)]
            filters.append(f'[{last}][{i+2}:v]overlay=0:0:enable=\'gte(t,{c["start"]})*lt(t,{c["end"]})\'[p{i+1}]');last=f'p{i+1}'
        filters.append(f'[{last}]format=yuv420p[final]')
        cmd+=['-filter_complex',';'.join(filters),'-filter_complex_threads','1','-map','[final]','-an','-frames:v',str(frames),'-r',str(p['fps']),'-c:v','libx264','-preset','veryfast','-crf','23','-threads','2','-video_track_timescale','15360','-movflags','+faststart',str(target)]
        print('PREPARE',scene['id'],edit['source'],start,frames,flush=True)
        subprocess.run(cmd,check=True)
        record={'kind':'actual_archive_video','source':edit['source'],'source_url':source['page_url'],'source_in':start,'duration':frames/p['fps'],'frames':frames,'fps':p['fps'],'source_width':vid['width'],'source_height':vid['height'],'archive_audio_removed':True,'credits_burned_in':True,'preparation_sha256':fingerprint,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'rights_basis':source['rights_basis']}
        stamp.write_text(json.dumps(record,ensure_ascii=False,indent=2))
    print('ARCHIVE_PREPARATION_READY',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('episode',type=Path);parser.add_argument('--library',required=True,type=Path);parser.add_argument('--only',nargs='*');a=parser.parse_args()
    prepare(a.episode.resolve(),a.library.resolve(),a.only)
