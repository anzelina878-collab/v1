#!/usr/bin/env python3
"""Prepare a phrase-aligned illustrative cut from a reviewed source selection."""
import json,re,difflib,math,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
E=ROOT/'Производство/episodes/001-chelovek-bez-litsa'
A=E/'assets'
FPS=30

def tokens(text):
 return [(m.group().lower().replace('ё','е'),m.start(),m.end()) for m in re.finditer(r'[a-zа-яё0-9]+',text,re.I)]

def main():
 script=(E/'inputs/script.txt').read_text(); st=tokens(script)
 rec=json.loads((E/'alignment/recognition.json').read_text())
 wt=[]
 for seg in rec['segments']:
  for w in seg['words']:
   for token,_,_ in tokens(w['word']):wt.append({'token':token,'start':w['start'],'end':w['end']})
 seq=difflib.SequenceMatcher(None,[v[0] for v in st],[v['token'] for v in wt],autojunk=False)
 mapping={i+k:j+k for i,j,n in seq.get_matching_blocks() for k in range(n)}
 coverage=len(mapping)/len(st)
 if coverage<.86:raise RuntimeError(f'Alignment coverage only {coverage:.1%}; manual investigation needed')
 unmatched=[]
 for tag,i,j,k,l in seq.get_opcodes():
  if tag!='equal':unmatched.append({'kind':tag,'script':' '.join(x[0] for x in st[i:j]),'recognition':' '.join(x['token'] for x in wt[k:l]),'near_seconds':wt[min(k,len(wt)-1)]['start']})
 (E/'alignment/comparison.json').write_text(json.dumps({'matched_token_fraction':coverage,'note':'Machine comparison, not human listening or fact verification','differences':unmatched},ensure_ascii=False,indent=2)+'\n')
 duration=json.loads((E/'audio_probe.json').read_text())['format']['duration']; total=round(float(duration)*FPS)
 blocks=json.loads((E/'scene_blocks.json').read_text()); pos=0
 for b in blocks:
  at=script.find(b['anchor_text'],pos)
  if at<0:raise ValueError(b['id'])
  pos=at+len(b['anchor_text']); ti=next(i for i,(_,a,z) in enumerate(st) if z>at)
  near=next((i for i in range(ti,min(ti+12,len(st))) if i in mapping),None)
  if near is None:
   b['skip_reason']='No corresponding speech in supplied audio; preserve authored script separately';continue
  b['start_frame']=round(wt[mapping[near]]['start']*FPS);b['alignment_anchor_tokens']=near-ti
 skipped=[b for b in blocks if 'start_frame' not in b]
 if skipped:(E/'alignment/skipped_text_blocks.json').write_text(json.dumps(skipped,ensure_ascii=False,indent=2)+'\n')
 blocks=[b for b in blocks if 'start_frame' in b]
 blocks[0]['start_frame']=0
 for i,b in enumerate(blocks):
  b['end_frame']=blocks[i+1]['start_frame'] if i+1<len(blocks) else total
  assert b['end_frame']>b['start_frame'],b
  b['start_seconds']=b['start_frame']/FPS;b['end_seconds']=b['end_frame']/FPS;b['timing_status']='aligned_to_recognized_words_reviewed_anchors'
 assets=json.loads((A/'downloaded_manifest.json').read_text())
 # These thumbnails were rejected after review; facial identities and wrong contexts are excluded.
 rejected={8,10,11,27,29,42,51,89,138,147,148,149,152,223,261,263,264,265,267,271,272,300,321,41}
 assets=[a for a in assets if a['contact_index'] not in rejected]
 for a in assets:
  a['kind']='video';a['used_seconds']=.25;a['last_used']=-1000;a['uses']=0
  a['crop_top_fraction']=.25 if a['contact_index'] in {8,52,157,162,168,174,275,283,307,309,311,312,313,314,317,320,321,322,323,325} else 0
  if a['category'] in {'code','coding','email'}:a['group']='code'
  elif a['category']=='research':a['group']='documents'
  elif a['category'] in {'travel','travel2'}:a['group']='travel'
  elif a['category']=='casino2':a['group']='casino'
  elif a['category']=='money':a['group']='money_pl' if a['contact_index'] in {101,106,107,108,110} else 'money'
  else:a['group']=a['category']
  a['usage_status']='approved_illustrative_stock'
 # All quadrants were visually inspected. They are separate artistic stills, not archival evidence.
 gen_map={'01.02':(1,0),'01.01':(1,1),'02.01':(1,2),'02.04':(1,3),'01.04':(2,0),'04.03':(2,1),'06.01':(2,2),'07.04':(2,3),'06.03':(3,0),'08.03':(3,1),'08.04':(3,2),'10.04':(3,3),'04.04':(4,0),'04.02':(4,1),'01.03':(4,2),'05.01':(4,3),'03.01':(5,0),'03.02':(5,1),'03.04':(5,2),'02.02':(5,3),'09.01':(6,0),'10.05':(6,1),'11.03':(6,2),'11.05':(6,3)}
 for block,(sheet,q) in gen_map.items():
  path=A/'generated'/('opening-sheet.png' if sheet==1 else f'sheet-{sheet}.png')
  assets.append({'id':f'gen_{sheet}_{q}','kind':'image','path':str(path.relative_to(A)),'quadrant':q,'block':block,'group':'reconstruction','visual_role':'artistic_reconstruction','author':'OpenAI image generation','license':'Generated for this production','source_url':None,'usage_status':'approved_artistic_reconstruction','sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'uses':0})
 pref={
 1:[['casino','night','phone'],['phone','casino'],['casino','money','phone'],['documents','surveillance','code']],
 2:[['anonymous','petersburg','code'],['code','documents','money','petersburg'],['petersburg','casino','electronics'],['electronics','code']],
 3:[['electronics','code'],['code','server','electronics'],['electronics','code','server'],['documents','code','electronics']],
 4:[['casino','night'],['phone','casino','surveillance'],['code','phone','night'],['casino','phone','money']],
 5:[['surveillance','night','phone'],['code','phone'],['phone','code','casino'],['server','phone','anonymous']],
 6:[['coffee','petersburg','phone'],['phone','coffee','money'],['travel','warsaw','phone'],['warsaw','server','phone','money']],
 7:[['travel','server','city'],['travel','warsaw','chicago','petersburg'],['money','phone','server'],['server','anonymous','phone']],
 8:[['surveillance','documents','police'],['surveillance','documents','night'],['chicago','travel','phone'],['police','phone','surveillance'],['documents','police'],['anonymous','server','phone']],
 9:[['code','documents','anonymous'],['money','documents','code'],['code','documents'],['code','phone','anonymous']],
 10:[['documents','code'],['code','anonymous'],['phone','code','server'],['anonymous','petersburg','code'],['phone','anonymous','night']],
 11:[['police','documents','petersburg'],['documents','code','anonymous'],['electronics','code','server'],['phone','anonymous','petersburg'],['petersburg','night','city']]
 }
 byid={a['id']:a for a in assets};shots=[];wordends=sorted(set(round(w['end']*FPS) for w in wt))
 def pick(groups,frame,length,last):
  eligible=[a for a in assets if a['kind']=='video' and a['id']!=last and a['actual_duration']-a['used_seconds']>=length+.08 and frame/FPS-a['last_used']>=90]
  if not eligible:raise RuntimeError('No remaining unlooped source footage')
  ranked=[(groups.index(a['group']) if a['group'] in groups else 99,a['uses'],(int(a['id'].split('_')[1])%53),a) for a in eligible]
  ranked.sort(key=lambda x:x[:3]);a=ranked[0][-1]
  if ranked[0][0]==99:raise RuntimeError(f'Coverage gap at {frame/FPS}: {groups}')
  return a
 for b in blocks:
  cat,idx=map(int,b['id'].split('.'));groups=pref[cat][idx-1];start=b['start_frame'];end=b['end_frame'];bounds=[start]
  while end-bounds[-1]>210:
   cur=bounds[-1];ideal=cur+180
   if end-cur<300:ideal=cur+(end-cur)//2
   opts=[x for x in wordends if cur+110<=x<=min(cur+210,end-100)]
   boundary=min(opts,key=lambda x:abs(x-ideal)) if opts else ideal
   bounds.append(boundary)
  bounds.append(end)
  gen_index=0
  if b['id']=='01.01':gen_index=1
  if b['id']=='02.02':gen_index=max(0,len(bounds)-3)
  if b['id']=='04.04':gen_index=min(4,len(bounds)-2)
  if b['id']=='05.01':gen_index=min(3,len(bounds)-2)
  if b['id']=='08.04':gen_index=min(6,len(bounds)-2)
  for j,(f0,f1) in enumerate(zip(bounds,bounds[1:])):
   secs=(f1-f0)/FPS;gen=None
   if b['id'] in gen_map and j==gen_index:
    sheet,q=gen_map[b['id']];gen=byid[f'gen_{sheet}_{q}']
   if b['id']=='11.05' and f1!=end:gen=None
   if b['id']=='11.05' and f1==end:
    sheet,q=gen_map[b['id']];gen=byid[f'gen_{sheet}_{q}']
   spoken=' '.join(w['token'] for w in wt if w['end']>f0/FPS and w['start']<f1/FPS)
   dynamic=groups[j%len(groups):]+groups[:j%len(groups)]
   def boost(cats):
    nonlocal dynamic
    dynamic=cats+[c for c in dynamic if c not in cats]
   if re.search('петербург|санкт|нева',spoken):boost(['petersburg'])
   if re.search('варшав|евро',spoken):boost(['warsaw','phone'])
   if re.search('чикаго|о хара',spoken):boost(['chicago','travel'])
   if re.search('корпус|плат[уыа]|микросх|оборудован',spoken):boost(['electronics','code'])
   if re.search('формул|математ|алгоритм|псевдослуч|вычисл|программ|код',spoken):boost(['code','electronics','server'])
   if re.search('сервер|криптовалют|загруз|защищенн|сеть',spoken):boost(['server','code','phone'])
   if re.search('доллар|выигрыш|заработ|деньг|миллион|тысяч',spoken):boost(['money','phone'])
   if re.search('автомат|барабан|кнопк|вращени|казино|казин',spoken):boost(['casino','phone','electronics'])
   if re.search('телефон|айфон|смартфон|приложен|таймер|вибр|сообщени',spoken):boost(['phone','code'])
   if re.search('письм|журналист|стать|интернет|публику|вайард|читает',spoken):boost(['code','documents'])
   if re.search('охрана|охран[уы]|камера|камер[уы]|наблюден',spoken):boost(['surveillance','phone'])
   if re.search('отчет|журнал операций|таблиц|провер|документ|сертифик|патент|судим|приговор',spoken):boost(['documents','code'])
   if re.search('фбр|полици|наруч|арест|тюрьм|депортац|тактическ|внедорожник',spoken):boost(['police','documents'])
   if re.search('перелет|прилет|лететь|билет|аэропорт|самолет',spoken):boost(['travel','phone'])
   a=gen or pick(dynamic,f0,secs,shots[-1]['asset_id'] if shots else None)
   shot={'id':f'shot_{len(shots)+1:04}','block_id':b['id'],'start':f0/FPS,'end':f1/FPS,'start_frame':f0,'end_frame':f1,'frames':f1-f0,'asset_id':a['id'],'scene_text':spoken,'visual_brief':b['visual_brief'],'visual_role':a['visual_role'],'motion':'subpixel_zoom' if gen else 'none'}
   if a['kind']=='video':shot['source_start']=round(a['used_seconds'],4);a['used_seconds']+=secs+.12;a['last_used']=f0/FPS
   a['uses']+=1;shots.append(shot)
 used=[a for a in assets if a['uses']]
 for a in used:
  for field in ['used_seconds','last_used']:a.pop(field,None)
 manifest={'status':'selected_for_illustrative_cut','license_snapshot':'pages/pexels-license.html','assets':used}
 timeline={'channel_id':'chelovek-bez-litsa','format':'long','width':1920,'height':1080,'fps':FPS,'audio_language':'ru','audio_path':'inputs/narration.mp3','total_frames':total,'duration_seconds':total/FPS,'color_treatment':{'saturation':.82,'contrast':1.025},'editorial_role':'Illustrative visual reconstruction, not archival documentation; existing authored narration unchanged','alignment_matched_fraction':coverage,'shots':shots}
 (E/'timeline.json').write_text(json.dumps(timeline,ensure_ascii=False,indent=2)+'\n');(A/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');(E/'scene_blocks.json').write_text(json.dumps(blocks,ensure_ascii=False,indent=2)+'\n')
 print('ALIGNMENT',coverage,'SHOTS',len(shots),'SOURCES',len(used),'IMAGES',sum(a['kind']=='image' for a in used))
 assert all(shots[i]['end_frame']==shots[i+1]['start_frame'] for i in range(len(shots)-1))
 assert shots[-1]['end_frame']==total

if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser(description='Historical episode 001 builder; not the current channel template')
 parser.add_argument('--rebuild-legacy-episode-001',action='store_true',help='Explicitly opt in to rebuilding the historical first-episode plan')
 args=parser.parse_args()
 if not args.rebuild_legacy_episode_001:
  parser.error('Legacy episode 001 selector is disabled by default. Use the new channel contract; do not rebuild an existing episode while editing the template.')
 main()
