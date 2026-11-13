"""Adapt the approved first edit through reviewed paragraph and spoken-word anchors.
Hindi timing hints are reference only. Original scenes/media stay untouched.
"""
from pathlib import Path
import json,math,re,copy,subprocess,hashlib
import numpy as np
from align_translation import tokens
from translations import tr
BASE=Path(__file__).resolve().parent;FPS=30

def main():
 old=json.load(open(BASE/'inputs/original-episode.v4.json'));uk={r['index']:r for r in json.load(open(BASE/'alignment/paragraphs.uk.json'))};hi={r['index']:r for r in json.load(open(BASE/'alignment/paragraphs.hi.json'))};links=json.load(open(BASE/'paragraph_translation_map.json'));points=[(0,0,100)];source_end=1063.1
 audio_duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(BASE/'audio/voiceover.mp3')]));end=math.ceil(audio_duration*30)/30
 def models(text,lang):
  out={}
  for m in re.finditer(r'\b(?:M\d+[A-Z0-9]*|Q[BJS][A-Z]*[- ]?\d+|HJ[- ]?\d+|ENVG[- ]?B)\b',text,re.I):
   key=re.sub('[^a-z0-9]','',m[0].lower());out.setdefault(key,[]).append(len(tokens(text[:m.start()],lang)))
  return out
 for link in links:
  a=uk[link['uk_index']];hs=[hi[i] for i in link['hi_indices']];b=hs[0];ht=[w for r in hs for w in r['tokens']];tt=[t for r in hs for t in r['times']];points.append((a['start'],b['start'],20));points.append((a['end'],hs[-1]['end'],10))
  om=models(a['text'],'uk');hm=models(link['hi_text'],'hi')
  for key in sorted(om.keys() & hm.keys()):
   for oi,ni in zip(om[key],hm[key]):
    if oi<len(a['times']) and ni<len(tt):points.append((a['times'][oi],tt[ni],30))
  os=[s for s in re.split(r'(?<=[.!?])\s+',a['text']) if s.strip()];ns=[s for s in re.split(r'(?<=[.!?।])\s+',link['hi_text']) if s.strip()]
  if len(os)==len(ns) and len(os)>1:
   oi=ni=0
   for x,y in zip(os,ns):
    if oi<len(a['times']) and ni<len(tt):points.append((a['times'][oi],tt[ni],5))
    oi+=len(tokens(x,'uk'));ni+=len(tokens(y,'hi'))
 points.append((source_end,end,100));chosen={}
 for x,y,weight in points:
  if 0<=x<=source_end and 0<=y<=end and (x not in chosen or weight>chosen[x][1]):chosen[x]=(y,weight)
 xx=np.array(sorted(chosen));yy=np.array([chosen[x][0] for x in xx]);fixed=np.maximum.accumulate(yy);max_adjust=float(np.max(abs(fixed-yy)));assert max_adjust<3,(max_adjust,'Review ambiguous bilingual timing anchor');yy=fixed
 def warp(t):return round(float(np.interp(t,xx,yy))*30)/30
 def translate(o):
  if isinstance(o,list):return [translate(x) for x in o]
  if isinstance(o,dict):
   out={}
   for k,v in o.items():
    if k in ['title','subtitle','label','detail','eyebrow','text','note'] and isinstance(v,str):out[k]=tr(v)
    elif k in ['sides','items','nodes','callouts']:out[k]=translate(v)
    else:out[k]=v
   for key in ['image','video']:
    if out.get(key,'').startswith('assets/prepared/'):out[key]=out[key].replace('assets/prepared/','assets/source_photos/')
   return out
  return o
 scenes=[]
 def add(s):
  if s['duration']<1/30-.001:return
  s['id']=f'hi-{len(scenes):03d}';s['end']=s['start']+s['duration'];s['eyebrow']='';s['camera_motion']=False;s['entrance_once']=True
  settle=max(1.2,(len(s.get('nodes',[]))-1)*.45+.1) if s['type']=='diagram' else 1.2;s['settle_after']=settle
  if scenes and s['type'] in ['diagram','compare','section','outro'] and all(scenes[-1].get(k)==s.get(k) for k in ['type','title','subtitle','sides','nodes','items','eyebrow']) and not(s.get('callouts') or scenes[-1].get('callouts')):
   scenes[-1]['duration']=s['end']-scenes[-1]['start'];scenes[-1]['end']=s['end'];scenes[-1]['original_scene_ids']+=s['original_scene_ids'];return
  scenes.append(s)
 opening=json.load(open(BASE/'inputs/original-opening.parts.v4.json'))['scenes'];ot=[0,2.3,4.6,6.8666666667,9.1666666667]
 for i,s in enumerate(old['scenes']):
  if i<2:
   if i==1:continue
   for j,part in enumerate(opening):
    a=warp(ot[j]);b=warp(ot[j+1]);s=translate(copy.deepcopy(part));s.update(start=a,duration=b-a,video=f'assets/archive/opening-{j}.mp4',archive_bank=f'opening-{j}',baked_captions=False,original_scene_ids=[old['scenes'][j//2]['id']]);add(s)
   continue
  a=warp(s['start']);b=warp(s['start']+s['duration']);s=translate(copy.deepcopy(s));s.update(start=a,duration=b-a,original_scene_ids=[s['id']]);s['narration_quote_asr_original']=s.pop('narration_quote_asr','')
  for call in s.get('callouts',[]):
   os=old['scenes'][i]['start'];call['start']=max(0,warp(os+call['start'])-a);call['end']=min(b-a,warp(os+call['end'])-a)
  if s['type']=='footage':s.update(video=f'assets/archive/source-{i:03d}.mp4',archive_bank=f'source-{i:03d}',baked_captions=False)
  if s['type']=='studio' and s.get('motion_kind')=='true_3d':
   key='m249' if 'm249' in s['video'].lower() else 'm4a1';s.update(video=f'assets/models/{key}/spin.mp4',bank_duration=24,source_in=0,rotation_degrees_per_second=15,loop=True)
  add(s)
 # Avoid restarting the exact same model when adjacent subshots only change labels.
 for i,s in enumerate(scenes):
  if s.get('motion_kind')=='true_3d' and i and scenes[i-1].get('video')==s.get('video') and scenes[i-1].get('motion_kind')=='true_3d':s['source_in']=(scenes[i-1].get('source_in',0)+scenes[i-1]['duration'])%24
 for a,b in zip(scenes,scenes[1:]):assert abs(a['end']-b['start'])<.002,(a['id'],b['id'])
 assert abs(scenes[-1]['end']-end)<.002 and sum(round(s['duration']*30) for s in scenes)==round(end*30)
 # Keep exact supplied Hindi paragraph context beside every visual beat for review/reuse.
 by_id={x['id']:x for x in old['scenes']};review_beats=[]
 for scene in scenes:
  originals=[by_id[x] for x in scene['original_scene_ids']];lo=min(x['start'] for x in originals);up=max(x['start']+x['duration'] for x in originals);indices=[]
  for link in links:
   paragraph=uk[link['uk_index']]
   if paragraph['start']<up and paragraph['end']>lo:indices.extend(link['hi_indices'])
  indices=sorted(set(indices));review_beats.append({'scene':scene['id'],'start':scene['start'],'end':scene['end'],'title':scene.get('title',''),'original_span':[lo,up],'hi_paragraph_indices':indices,'narration_hi_context':'\n'.join(hi[x]['text'] for x in indices)})
 chapters=json.load(open(BASE/'input/chapters.hi.json'));chapter_records=[]
 for c in chapters:
  first=hi[c['rows'][0]['index']];chapter_records.append({'start':0 if not chapter_records else round(first['start']*30)/30,'title':re.split(r'\s[—–]\s',c['heading'],maxsplit=1)[-1]})
 p={'schema':'arsenal.hindi-adaptation.v1','title':'USA vs China 2026: एक सैनिक क्या-क्या लेकर चलता है?','brand':'ARSENAL 360 / शस्त्र 360','language':'hi','style':'minimal','width':1920,'height':1080,'fps':30,'duration':end,'audio':'audio/voiceover.mp3','original_audio_duration':audio_duration,'original_source_episode':'001-usa-china-2026/episode.v4.json','original_source_duration':source_end,'motion_policy':{'photo_camera':'locked','card_entrance':'once then hold','rotation_seconds_per_revolution':24,'archive_speed':'unchanged; longer Hindi clause tails use a licensed still frame and are counted separately, never replayed'},'scenes':scenes,'chapters':chapter_records}
 (BASE/'editorial-alignment.json').write_text(json.dumps(review_beats,ensure_ascii=False,indent=2));(BASE/'episode.json').write_text(json.dumps(p,ensure_ascii=False,indent=2));(BASE/'chapters.hi.txt').write_text('\n'.join(f"{int(c['start'])//60:02d}:{int(c['start'])%60:02d} {c['title']}" for c in chapter_records)+'\n');(BASE/'alignment/timewarp.json').write_text(json.dumps({'build_inputs_sha256':{str(f.relative_to(BASE)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [BASE/'alignment/paragraphs.uk.json',BASE/'alignment/paragraphs.hi.json',BASE/'alignment/refinements.json',BASE/'paragraph_translation_map.json',BASE/'inputs/original-episode.v4.json',BASE/'translations.py',BASE/'build_episode.py']},'old_seconds':xx.tolist(),'hindi_seconds':yy.tolist(),'anchor_count':len(xx),'max_monotonic_adjustment':max_adjust,'reviewed_paragraph_correspondences':len(links)},indent=2));print('BUILT_HINDI',len(scenes),end,'anchors',len(xx),'max_adjust',max_adjust,flush=True)
if __name__=='__main__':main()
