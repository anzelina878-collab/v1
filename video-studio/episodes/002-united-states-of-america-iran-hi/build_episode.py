"""Audio-led Hindi adaptation of the approved second edit. Archives never freeze/loop."""
from pathlib import Path
import json,copy,re,math,subprocess,hashlib
import numpy as np
from translations import tr
BASE=Path(__file__).resolve().parent;FPS=30

def main():
 old=json.load(open(BASE/'inputs/original-episode.v4.json'));rows=json.load(open(BASE/'alignment/rows.hi.json'));manifest=json.load(open(BASE/'assets/manifest.json'));assets={a['id']:a for a in manifest};duration=math.ceil(json.load(open(BASE/'alignment/report.json'))['audio_duration']*30)/30;body=[r for r in rows if r['kind']=='narration'];xx=[0]+[r['original_start'] for r in body[1:]]+[old['duration']];yy=[0]+[r['start'] for r in body[1:]]+[duration];assert all(b>=a for a,b in zip(yy,yy[1:]));warp=lambda t:round(float(np.interp(t,xx,yy))*30)/30
 def convert(s):
  s=copy.deepcopy(s)
  for k in ['title','subtitle','note']:
   if k in s:s[k]=tr(s[k])
  if 'nodes' in s:s['nodes']=[tr(x) for x in s['nodes']]
  if 'sides' in s:s['sides']=[[a,tr(t),c] for a,t,c in s['sides']]
  # Keep detailed real cutouts where two old illustrative meshes look crude.
  quality_replacements={'model-abrams':'product-abrams','model-shahed136-illustrative':'product-shahed136'}
  if s.get('asset_id') in quality_replacements and s['kind'] in ['photo','turntable']:
   s['asset_id']=quality_replacements[s['asset_id']];s['kind']='photo';s.pop('note',None);s.pop('visual_origin',None);s['quality_choice']='Real licensed cutout preferred to coarse illustrative geometry'
  if s.get('sides'):s['sides']=[[quality_replacements.get(a,a),t,c] for a,t,c in s['sides']]
  s.update(entrance_once=True,camera_motion=False,settle_after=max(1.2,(len(s.get('nodes',[]))-1)*.45+.12))
  for k in ['_base_id','_base_offset_frames','a','b','narration_quote']:s.pop(k,None)
  return s
 plans=[]
 for i,s in enumerate(old['scenes']):
  d=convert(s);d.update(start=warp(s['start']),end=warp(s['end']),original_scene_ids=[s['id']]);d['duration']=d['end']-d['start']
  if d['duration']<1/30:continue
  if d['kind']=='section':
   future=next((x for x in old['scenes'][i+1:] if x['kind'] in ['photo','turntable'] and assets[x['asset_id']].get('photo')),None)
   if future:d.update(kind='photo',asset_id={'model-abrams':'product-abrams','model-shahed136-illustrative':'product-shahed136'}.get(future['asset_id'],future['asset_id']),title=tr(future['title']),country=future.get('country','US'),role='original-section-reserve')
  plans.append(d)
 chapters=[{'start':0,'spoken_start':0,'title':'परिचय','display_start':0}];cards=[]
 for row in rows:
  if row['kind']!='heading':continue
  spoken=round(row['start']*30)/30;start=max(0,round((spoken-.70)*30)/30);end=round(min(start+5.5,max(start+2.5,row['end']+.5))*30)/30
  title=row['text'].split('।',1)[0].strip();cards.append({'kind':'section','title':title,'subtitle':'','start':start,'end':end,'duration':end-start,'original_scene_ids':[],'entrance_once':True,'settle_after':1.2,'camera_motion':False,'chapter':row['chapter'],'spoken_start':spoken});chapters.append({'start':spoken,'spoken_start':spoken,'spoken_end':row['end'],'display_start':start,'fully_visible_at':start+.65,'display_end':end,'title':title})
 boundaries=sorted({0,round(duration*30)}|{round(s[k]*30) for s in plans+cards for k in ['start','end']});out=[]
 for a,b in zip(boundaries,boundaries[1:]):
  t=a/30;c=next((s for s in cards if round(s['start']*30)<=a<round(s['end']*30)),None);base=c or next(s for s in plans if round(s['start']*30)<=a<round(s['end']*30));d=copy.deepcopy(base);d.update(start=a/30,end=b/30,duration=(b-a)/30)
  if d['kind']=='archive':d['source_in']=base.get('source_in',0)+(a/30-base['start'])
  if out and d['kind'] in ['photo','compare','graphic','section','question','outro','ident'] and all(d.get(k)==out[-1].get(k) for k in ['kind','asset_id','title','subtitle','note','nodes','sides','chapter']):
   out[-1]['end']=d['end'];out[-1]['duration']=out[-1]['end']-out[-1]['start'];out[-1]['original_scene_ids']=sorted(set(out[-1]['original_scene_ids']+d['original_scene_ids']));continue
  out.append(d)
 # Exhausted moving footage cuts to a deliberately composed matching object view.
 final=[];fallbacks=[]
 def photo_key(s):
  a=assets[s['asset_id']]
  if a.get('photo'):return a['id']
  key=a.get('fallback_photo');aliases={'ford-deck':'ford','ford-crew':'ford','iran-sam':'bavar','iran-missiles':'fateh','us-infantry':'m7'};key=key or aliases.get(a['id'])
  if key:
   match=next((k for k in assets if k.lower()==key.lower() and assets[k].get('photo')),None)
   if match:return match
  raise ValueError(('Choose a matching fallback explicitly',s))
 for s in out:
  if s['kind']=='archive':
   a=assets[s['asset_id']];info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(BASE/a['video'])]));bank=float(info['format']['duration']);available=max(0,int((bank-s.get('source_in',0))*30+.001));needed=round(s['duration']*30)
   if needed>available:
    moving=max(0,min(available,needed-75));moving=moving if moving>=45 else 0
    if moving:
     d=copy.deepcopy(s);d.update(end=s['start']+moving/30,duration=moving/30);final.append(d)
    d=copy.deepcopy(s);key=photo_key(s);d.update(kind='photo',asset_id=key,start=s['start']+moving/30,duration=(needed-moving)/30,title=tr(assets[key].get('display_name',s['title'])),role='intentional-matching-cutaway');d.pop('source_in',None);fallbacks.append({'original_scene':s.get('original_scene_ids'),'moving_seconds':moving/30,'cutaway_seconds':d['duration'],'matching_asset':key});final.append(d);continue
  final.append(s)
 for i,s in enumerate(final):
  s['id']=f'hi002-{i:03d}';s['settle_after']=max(1.2,(len(s.get('nodes',[]))-1)*.45+.12)
  if s['kind']=='turntable':
   s['source_in']=0
   if i and final[i-1]['kind']=='turntable' and final[i-1]['asset_id']==s['asset_id']:s['source_in']=(final[i-1]['source_in']+final[i-1]['duration'])%24
  context=[r['text'] for r in body if r['start']<s['end'] and r['end']>s['start']];s['narration_hi']='\n'.join(context)
 for a,b in zip(final,final[1:]):assert abs(a['end']-b['start'])<.002
 assert sum(round(s['duration']*30) for s in final)==round(duration*30)
 for c in chapters[1:]:
  s=next(s for s in final if s['kind']=='section' and s['start']<=c['spoken_start']<s['end']);assert s['start']+.65<=c['spoken_start']+.001
 p={'schema':'arsenal.hindi-episode002.v1','title':'संयुक्त राज्य अमेरिका बनाम ईरान: सैन्य शस्त्रागार की पूरी तुलना','language':'hi','brand':'ARSENAL 360 / शस्त्र 360','width':1920,'height':1080,'fps':30,'duration':duration,'audio':'audio/voiceover.mp3','scenes':final,'chapters':chapters,'motion_policy':{'archive':'Normal speed, no tpad or looping; extend available licensed material or cut to a matching deliberate still/3D','native_3d':'720 directly rendered poses / 24 seconds; no optical-flow interpolation','photos':'locked','cards':'one entrance then hold','chapter_titles':'Fully revealed by spoken heading start'}}
 (BASE/'episode.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n');(BASE/'chapters.hi.txt').write_text('\n'.join(f"{int(c['start'])//60:02d}:{int(c['start'])%60:02d} {c['title']}" for c in chapters)+'\n');(BASE/'archive-cutaways.json').write_text(json.dumps(fallbacks,ensure_ascii=False,indent=2)+'\n');(BASE/'alignment/timewarp.json').write_text(json.dumps({'original_seconds':xx,'hindi_seconds':yy,'source_paragraphs':242,'audio_based_chapter_overrides':chapters[1:],'input_hashes':{str(f.relative_to(BASE)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [BASE/'alignment/rows.hi.json',BASE/'inputs/original-episode.v4.json',BASE/'translations.py',Path(__file__)]}},ensure_ascii=False,indent=2)+'\n');print('HINDI_PLAN_READY',len(final),duration,'moving archive cutaways',len(fallbacks),flush=True)
if __name__=='__main__':main()
