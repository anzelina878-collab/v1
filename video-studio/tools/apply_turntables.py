"""Bind verified turntable clips to studio shots for any episode.

Usage: python tools/apply_turntables.py episode.json turntables.json output.json
Default is strict: any unbound object prevents writing a misleading final config.
Use --draft only to inspect partial preparation; it is marked incomplete.
"""
import argparse,copy,json
from pathlib import Path


def apply(data,registry,base):
    data=copy.deepcopy(data);missing=[];bound=[]
    entries=registry['objects'];previous=None
    for scene in data['scenes']:
        signature=(scene['type'],scene.get('title'),scene.get('country'))
        scene['animate_title']=signature!=previous;previous=signature
        if scene['type']!='studio':continue
        name=scene.get('object_id') or Path(scene.get('image',scene.get('video',''))).stem.replace('-turntable','')
        name=name.upper()
        entry=entries.get(name)
        if entry and entry.get('status')=='archive_context_not_product_turntable':continue
        if not entry or entry.get('status')!='ready':
            missing.append({'scene':scene['id'],'object_id':name});continue
        clip=(base/entry['video']).resolve()
        if not clip.is_file():raise ValueError(f'Missing prepared turntable: {clip}')
        meta=json.loads(clip.with_suffix('.3d.json').read_text())
        if meta.get('motion_kind')!='true_3d':raise ValueError(f'Not a real mesh render: {name}')
        if abs(meta['yaw_end']-meta['yaw_start'])<359:raise ValueError(f'Not a full revolution: {name}')
        if not entry.get('source_url') or not entry.get('license'):raise ValueError(f'Missing license/source: {name}')
        scene.pop('image',None);scene.update(video=entry['video'],motion_kind='true_3d',loop=True,fit='contain',source=entry['source_url'],object_id=name)
        bound.append(scene['id'])
    data['title_motion']=True
    # Comparisons and kit collages still require individual animated panels.
    for scene in data['scenes']:
        for obj in scene.get('sides',[])+scene.get('items',[]):
            if obj.get('image'):missing.append({'scene':scene['id'],'object_id':Path(obj['image']).stem,'context':'comparison/kit panel'})
    for name,entry in entries.items():
        if entry.get('status')!='ready':
            for sid in entry.get('required_scenes',[]):
                if any(s['id']==sid for s in data['scenes']):missing.append({'scene':sid,'object_id':name,'context':'required model, currently typographic'})
    data['production_status']='all_object_turntables_ready' if not missing else 'incomplete_3d_draft'
    return data,{'bound_scenes':bound,'unresolved':missing,'all_objects_animated':not missing}


def main():
    p=argparse.ArgumentParser();p.add_argument('episode');p.add_argument('registry');p.add_argument('output');p.add_argument('--draft',action='store_true');a=p.parse_args()
    source=Path(a.episode).resolve();target=Path(a.output).resolve()
    if source==target or target.exists():raise ValueError('Use a new output filename')
    if source.parent!=target.parent:raise ValueError('Keep revised config in the episode folder to preserve relative paths')
    data,report=apply(json.loads(source.read_text()),json.loads(Path(a.registry).read_text()),source.parent)
    target.with_suffix('.coverage.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    if not report['all_objects_animated'] and not a.draft:raise SystemExit('Missing models/panels: see coverage report. No final config written.')
    target.write_text(json.dumps(data,ensure_ascii=False,indent=2));print(target)

if __name__=='__main__':main()
