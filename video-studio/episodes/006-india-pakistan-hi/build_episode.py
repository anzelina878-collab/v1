"""Hindi edition, independently reviewed speech anchors and preserved Ukrainian edit.
Unanchored interior scene boundaries interpolate only between nearby semantic anchors.
"""
from pathlib import Path
import json,copy,math,hashlib,subprocess,re
import numpy as np
from translations import tr
BASE=Path(__file__).resolve().parent
FALLBACK={'apache-demo': 'model-apache', 'apache-indian-action': 'model-apache', 'austrahind': 'sig716', 'brahmos-launch': 'brahmos', 'brahmos-test': 'brahmos', 'infantry2019': 'sig716', 'integrated': 'bhishma', 'k4-launch': 'arihant', 'm109-action': 'm109', 'm777-india': 'm777', 'm777-joint': 'm777', 'malabar': 'kolkata', 'navy-shakti': 'kolkata', 'optics-training': 'sig716', 'rafale-action': 'rafale-india', 'rafale-indian-action': 'rafale-india', 'rafale-tlp': 'rafale-india', 'vikrant-video': 'vikrant', 'yudh20': 'bhishma', 'yudh22': 'sig716', 'medevac-training': 'sig716'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 old=json.load(open(BASE/'inputs/original-episode.json'));paras=json.load(open(BASE/'inputs/original-paragraphs.json'));anchors=json.load(open(BASE/'alignment/anchors.json'));am={int(k):v for k,v in anchors.items()};assets={a['id']:a for a in json.load(open(BASE/'assets/manifest.json'))};duration=math.ceil(float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(BASE/'audio/voiceover.mp3')]))*30)/30
 pairs=sorted([(r['start'],am[r['i']]) for r in paras if r['i'] in am]);assert all(b[1]>a[1] for a,b in zip(pairs,pairs[1:])),pairs
 xx=[x for x,y in pairs]+[old['duration']];yy=[y for x,y in pairs]+[duration]
 warp=lambda t:round(float(np.interp(t,xx,yy))*30)/30
 plans=[]
 for i,s in enumerate(old['scenes']):
  d=copy.deepcopy(s)
  for k in ['title','subtitle','note']:
   if k in d:d[k]=tr(d[k])
  if 'nodes'in d:d['nodes']=[tr(v) for v in d['nodes']]
  if 'sides'in d:d['sides']=[[a,tr(t),c] for a,t,c in d['sides']]
  for k in ['narration_quote','visual_purpose','a','b']:d.pop(k,None)
  if d['kind']=='section':
   future=next(x for x in old['scenes'][i+1:] if x['kind'] in ['photo','turntable'] and assets[x['asset_id']].get('photo'))
   d.update(kind='photo',asset_id=future['asset_id'],title=tr(future['title']),country=future.get('country','IN'),role='original-section-reserve')
  if d['kind']=='ident':d.pop('asset_id',None);d.update(title='ARSENAL 360',subtitle='शस्त्र 360')
  d.pop('asset_id',None) if d['kind']=='compare' else None
  d.update(start=warp(s['start']),end=warp(s['end']),original_scene_ids=[s['id']],entrance_once=True,camera_motion=False)
  d['duration']=d['end']-d['start']
  if d['duration']>=1/30:plans.append(d)
 cues=json.load(open(BASE/'alignment/chapter-cues.json'));cards=[];chapters=[dict(start=0,spoken_start=0,title='परिचय',display_start=0)]
 for c in cues:
  cue=round(c['spoken_start']*30)/30;start=round(max(0,cue-.7)*30)/30;end=round((cue+2.8)*30)/30
  cards.append(dict(kind='section',title=c['title'],subtitle='',start=start,end=end,duration=end-start,chapter=c['chapter'],spoken_start=cue,original_scene_ids=[],entrance_once=True,camera_motion=False))
  chapters.append(dict(start=cue,spoken_start=cue,display_start=start,fully_visible_at=start+.65,display_end=end,title=c['title']))
 boundaries=sorted({0,round(duration*30)}|{round(s[k]*30) for s in plans+cards for k in ['start','end']});out=[]
 for a,b in zip(boundaries,boundaries[1:]):
  base=next((s for s in cards if round(s['start']*30)<=a<round(s['end']*30)),None) or next(s for s in plans if round(s['start']*30)<=a<round(s['end']*30));d=copy.deepcopy(base);d.update(start=a/30,end=b/30,duration=(b-a)/30)
  if d['kind'] in ['archive','map']:d['source_in']=base.get('source_in',0)+a/30-base['start']
  if out and d['kind'] in ['photo','compare','graphic','section','question','outro','ident'] and all(d.get(k)==out[-1].get(k) for k in ['kind','asset_id','title','subtitle','note','nodes','sides','chapter','country']):
   out[-1].update(end=d['end'],duration=d['end']-out[-1]['start']);out[-1]['original_scene_ids']=sorted(set(out[-1]['original_scene_ids']+d['original_scene_ids']));continue
  out.append(d)
 i=0
 while i<len(out):
  s=out[i]
  if s['kind']!='section' and (s['duration']<.8 or (s.get('role')=='original-section-reserve' and s['duration']<1.2)):
   if i+1<len(out) and out[i+1]['kind']=='section':out[i+1].update(start=s['start'],duration=out[i+1]['end']-s['start']);out.pop(i);continue
   if i and out[i-1]['kind']=='section':out[i-1].update(end=s['end'],duration=s['end']-out[i-1]['start']);out.pop(i);continue
  i+=1
 final=[];fallbacks=[];history={}
 def cutaway(s,reason):
  key=FALLBACK[s['asset_id']];assert assets[key].get('photo'),key;d=copy.deepcopy(s);d.update(kind='photo',asset_id=key,title=assets[key].get('display_name',s['title']),note='',role=reason);d.pop('source_in',None);fallbacks.append(dict(original_asset=s['asset_id'],matching_asset=key,start=s['start'],end=s['end'],reason=reason));return d
 for s in out:
  if s['kind']=='archive':
   key=s['asset_id'];bank=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(BASE/assets[key]['video'])]));needed=round(s['duration']*30);available=max(0,math.floor((bank-s.get('source_in',0))*30+.001))
   if key in history and s['start']-history[key]<=60:s=cutaway(s,'matching-cutaway-for-reuse-spacing')
   elif needed>available:
    moving=max(0,min(available,needed-75));moving=moving if moving>=45 else 0
    if moving:d=copy.deepcopy(s);d.update(end=s['start']+moving/30,duration=moving/30);final.append(d);history[key]=d['end']
    s=copy.deepcopy(s);s.update(start=s['start']+moving/30,duration=(needed-moving)/30);s=cutaway(s,'source-exhausted-matching-cutaway')
   else:history[key]=s['end']
  final.append(s)
 if len(final)>1 and final[-1]['kind']=='ident' and final[-2].get('title')=='ARSENAL 360':
  tail=final.pop();final[-1].update(kind='ident',title='ARSENAL 360',subtitle='शस्त्र 360',end=tail['end'],duration=tail['end']-final[-1]['start'])
 # Eliminate accidental sub-second flashes from language retiming.
 i=0
 while i<len(final):
  s=final[i]
  if s['duration']<.8 and i and final[i-1]['kind']!='section':
   prev=final[i-1];extend=True
   if prev['kind'] in ['archive','map']:
    bank=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(BASE/assets[prev['asset_id']]['video'])]));extend=prev.get('source_in',0)+(s['end']-prev['start'])<=bank+.001
   if extend:prev.update(end=s['end'],duration=s['end']-prev['start']);prev['original_scene_ids']=sorted(set(prev['original_scene_ids']+s['original_scene_ids']));final.pop(i);continue
  i+=1
 for i,s in enumerate(final):
  s['id']=f'hi006-{i:03d}';s['settle_after']=max(1.2,(len(s.get('nodes',[]))-1)*.45+.12)
  if s['kind']=='turntable':
   s['source_in']=0
   if i and final[i-1]['kind']=='turntable' and final[i-1]['asset_id']==s['asset_id']:s['source_in']=(final[i-1]['source_in']+final[i-1]['duration'])%24
  if s['kind']=='map':s['source_in']=min(s.get('source_in',0),max(0,assets[s['asset_id']]['duration']-s['duration']));assert s['duration']<=assets[s['asset_id']]['duration']
 for a,b in zip(final,final[1:]):assert abs(a['end']-b['start'])<.002
 p=dict(schema='arsenal.hindi-episode006.v1',title='भारत बनाम पाकिस्तान 2026: किसका सैन्य शस्त्रागार अधिक शक्तिशाली है?',language='hi',brand='ARSENAL 360 / शस्त्र 360',width=1920,height=1080,fps=30,duration=duration,audio='audio/voiceover.mp3',scenes=final,chapters=chapters,motion_policy={'archive':'Normal speed with matching cutaway if source exhausted; no loops or frozen tails','native_3d':'720 native frames, smooth 24-second full revolution, fixed camera','cards':'One entrance and hold','photos':'locked','maps':'True 3D elevation mesh with animated camera and Hindi labels'})
 (BASE/'episode.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n');(BASE/'chapters.hi.txt').write_text('\n'.join(f"{int(c['start'])//60:02d}:{int(c['start'])%60:02d} {c['title']}" for c in chapters)+'\n');(BASE/'archive-cutaways.json').write_text(json.dumps(fallbacks,ensure_ascii=False,indent=2)+'\n')
 deps=['alignment/anchors.json','alignment/chapter-cues.json','inputs/original-episode.json','inputs/original-paragraphs.json','translations.py','build_episode.py'];(BASE/'alignment/timewarp.json').write_text(json.dumps(dict(original_seconds=xx,hindi_seconds=yy,reviewed_semantic_anchors=len(pairs),method='Reviewed Hindi word-timed speech anchors mapped to original Ukrainian semantic paragraphs; interior shot boundaries interpolate between anchors',input_hashes={rel:sha(BASE/rel) for rel in deps}),ensure_ascii=False,indent=2)+'\n');print('HINDI_PLAN_READY',len(final),duration,'cutaways',len(fallbacks),flush=True)
if __name__=='__main__':main()
