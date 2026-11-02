"""Compile the manually selected subjects against actual immutable voice timings."""
import json,math,copy,re
from pathlib import Path
from collections import Counter
from visual_map import SPANS
from tools.edit_rules import check_archive_spacing
BASE=Path(__file__).resolve().parent;FPS=30;DURATION=1288.128;END=math.ceil(DURATION*FPS)/FPS
FALLBACK={'pl-f16':'f16','de-ef':'eurofighter','pl-abrams':'abrams','pl-abrams-action':'abrams','pl-logistics':'abrams','de-leopard':'leopard','de-puma':'puma','de-boxer':'boxer','de-boxer-exact':'boxer','pl-krab':'krab','pl-krab-move':'krab','de-pzh':'pzh','pl-himars':'himars','pl-nato':'himars','de-g36':'g36','de-mg5':'mg5','pl-infantry':'grot','de-patriot':'patriot','de-patriot-setup-correct':'patriot','patriot-reload-type':'patriot','de-tiger-exact':'tiger','de-nh90':'nh90','pl-perry':'perry','de-k130-exact':'k130','de-frigate':'f124','pl-kormoran':'kormoran','allies-infantry':'grot','de-support':'leopard','f35-type':'f35','apache-type':'apache','uas-training':'flyeye'}
PREFERRED={'de-ef':18,'de-leopard':10,'de-puma':8,'de-frigate':18,'allies-infantry':5,'pl-perry':10,'pl-logistics':18,'heron-type':5,'patriot-reload-type':6,'pl-f16':6,'pl-nato':20,'uas-training':15}

def main():
 rows=json.loads((BASE/'inputs/paragraphs.json').read_text());pars={r['i']:r for r in json.loads((BASE/'alignment/paragraphs.json').read_text())};pt={i:r['start'] for i,r in pars.items()};words={r['i']:r for r in json.loads((BASE/'alignment/word_anchors.json').read_text())};assets={a['id']:a for a in json.loads((BASE/'assets/manifest.json').read_text())};scenes=[];used={};history={};decisions=[]
 def push(start,end,kind,key,title='',country='PL',**kw):
  start=round(start*FPS)/FPS;end=round(end*FPS)/FPS
  if end<=start:return
  a=assets.get(key,{});note=kw.pop('note','')
  if kind=='turntable':note='Схематична 3D-візуалізація' if a.get('schematic') else '3D-візуалізація родини техніки'
  s={'start':start,'end':end,'duration':end-start,'kind':kind,'asset_id':key,'title':title or a.get('display_name',key.upper()),'country':country,'entrance_once':True,'settle_after':1.2,'note':note,**kw}
  if kind=='archive':
   a=assets[key];canonical=a['video_source'];offset=max(PREFERRED.get(key,0),used.get(canonical,0));available=a['duration']-offset-.1
   if canonical in history and start-history[canonical]<=60:
    decisions.append({'time':start,'asset':key,'reason':'Archive source cooldown >60s enforced; matching photograph used'});s.update(kind='photo',asset_id=FALLBACK[key],title=assets[FALLBACK[key]].get('display_name',title));scenes.append(s);return
   cap=kw.get('archive_cap',10);cap+=4 if cap>=10 else 0
   length=min(s['duration'],cap,available);length=math.floor(length*FPS)/FPS
   if length<1:
    s.update(kind='photo',asset_id=FALLBACK[key],title=assets[FALLBACK[key]].get('display_name',title));scenes.append(s);return
   cut=round((start+length)*FPS)/FPS
   if end-cut<.05 and end-start<=available:cut=end;length=end-start
   s.update(end=cut,duration=length,source_in=offset);scenes.append(s);history[canonical]=cut;used[canonical]=offset+length
   if end-cut>.02:push(cut,end,'photo',FALLBACK[key],assets[FALLBACK[key]].get('display_name',title),country,narration_quote=kw.get('narration_quote',''),note='Реальна фотографія · відповідний тип техніки')
   return
  scenes.append(s)
 def at(i,needle):
  tokens=re.findall(r'[a-zа-яіїєґ0-9]+',needle.lower());w=words[i]
  for j in range(len(w['tokens'])-len(tokens)+1):
   if w['tokens'][j:j+len(tokens)]==tokens:return w['times'][j]
  return pt[i]
 # Opening geography is animated, followed by source-bound equipment shots.
 push(0,4,'map','map-europe','ПОЛЬЩА ТА НІМЕЧЧИНА')
 push(4,6.5,'turntable','model-abrams','M1 ABRAMS')
 push(6.5,pt[2],'archive','de-leopard','LEOPARD 2 · НАВЧАННЯ НАТО','DE',archive_cap=3)
 p2=[pt[2],at(2,'південнокорейські'),at(2,'реактивна'),at(2,'новітні'),pt[3]]
 for j,(kind,key,title) in enumerate([('archive','pl-abrams-action','M1 ABRAMS · НАВЧАННЯ НАТО'),('photo','k2','K2 BLACK PANTHER'),('turntable','model-himars-illustrative','M142 HIMARS'),('archive','f35-type','F-35A · ТИП ЛІТАКА')]):push(p2[j],p2[j+1],kind,key,title)
 p3=[pt[3],at(3,'бойові'),at(3,'бронетранспортери'),at(3,'та сучасні'),pt[4]]
 for j,(kind,key,title) in enumerate([('turntable','model-leopard-illustrative','LEOPARD 2'),('photo','puma','PUMA'),('photo','boxer','BOXER'),('photo','iris','IRIS-T SLM')]):push(p3[j],p3[j+1],kind,key,title,'DE')
 push(pt[4],pt[5]+3,'compare','original','ДВА ПІДХОДИ',sides=[['k2','ПОЛЬЩА','PL'],['leopard','НІМЕЧЧИНА','DE']])
 push(pt[5]+3,pt[5]+6.5,'turntable','model-f16','F-16 · РОДИНА ЛІТАКІВ');push(pt[5]+6.5,pt[6],'turntable','model-eurofighter','EUROFIGHTER TYPHOON','DE')
 push(pt[6],pt[6]+3,'graphic','original','КІЛЬКІСТЬ · ТЕХНОЛОГІЇ · ЗАБЕЗПЕЧЕННЯ',nodes=['ТЕХНІКА','ПРОМИСЛОВІСТЬ','ПОСТАЧАННЯ'])
 push(pt[6]+3,pt[7],'archive','pl-logistics','ЛОГІСТИКА · СПІЛЬНІ НАВЧАННЯ',archive_cap=8)
 push(pt[7],pt[7]+3,'map','map-europe','ПОЛЬЩА ТА НІМЕЧЧИНА');push(pt[7]+3,pt[8],'compare','original','АРСЕНАЛ 360°',sides=[['f16','ПОЛЬЩА','PL'],['eurofighter','НІМЕЧЧИНА','DE']])
 names=[('винищувачі','model-f16','ВИНИЩУВАЧІ · F-16','turntable','PL'),('танки','model-abrams','ТАНКИ · M1 ABRAMS','turntable','PL'),('ракети','himars','РАКЕТИ · HIMARS','photo','PL'),('піхотне','grot','ПІХОТНЕ ОЗБРОЄННЯ · GROT','photo','PL'),('артилерія','pl-krab','АРТИЛЕРІЯ · KRAB','archive','PL'),('безпілотники','bayraktar','БЕЗПІЛОТНИКИ · TB2','photo','PL'),('протиповітряна','iris','ПРОТИПОВІТРЯНА ОБОРОНА','photo','DE'),('вертольоти','model-apache','ВЕРТОЛЬОТИ · AH-64','turntable','PL'),('військово','f124','ВІЙСЬКОВО-МОРСЬКИЙ ФЛОТ','photo','DE')]
 times=[at(8,n[0]) for n in names]+[pt[9]]
 for j,(_,key,title,kind,country) in enumerate(names):push(times[j],times[j+1],kind,key,title,country,archive_cap=2)
 push(pt[9],pt[9]+3.5,'turntable','model-leopard-illustrative','LEOPARD 2','DE');push(pt[9]+3.5,pt[10],'photo','k2','K2 BLACK PANTHER');push(pt[10],pt[12],'ident','channel-ident','АРСЕНАЛ 360°')
 # Body: the authored equipment/claim span determines each visual.
 for index,spec in enumerate(SPANS[1:]):
  nextspec=SPANS[index+2] if index+2<len(SPANS) else None;start=max(pt[spec['a']],scenes[-1]['end']);end=pt[nextspec['a']] if nextspec else END
  if end<=start:continue
  x={k:v for k,v in spec.items() if k not in ['a','b','kind','asset_id','title','country']};x['narration_quote']=' '.join(pars[i]['text'] for i in range(spec['a'],spec['b']+1) if i in pars)
  if spec['kind']=='section':
   length=max(3,min(4.5,end-start)) if end-start>5.5 or end-start<3 else end-start;cut=min(END,start+length);push(start,cut,'section','original',spec['title'],**x)
   if end-cut>.05:
    chapter=pars[spec['a']]['chapter'];key={1:'f16',2:'abrams',3:'himars',4:'grot',5:'krab',6:'bayraktar',7:'patriot',8:'apache',9:'f124',10:'leopard'}[chapter];push(cut,end,'photo',key,assets[key].get('display_name',key.upper()),'DE' if chapter in [9,10] else 'PL',narration_quote=x['narration_quote'])
   continue
  if spec['a']==183:
   cut=start+(end-start)*.45
   push(start,cut,'compare','original',spec['title'],sides=spec['sides'])
   push(cut,end,'archive','pl-kormoran','ORP ALBATROS · KORMORAN II',archive_cap=8)
   continue
  if spec['a']==167:
   cut1=max(start+2,min(end-4,at(167,'AW149')));cut2=max(cut1+2,min(end-2,at(167,'AW101')))
   push(start,cut1,'turntable','model-blackhawk','BLACK HAWK · РОДИНА ВЕРТОЛЬОТІВ')
   push(cut1,cut2,'photo','aw149','AW149 · ТИП ВЕРТОЛЬОТА')
   push(cut2,end,'photo','aw101','AW101 · РОДИНА ВЕРТОЛЬОТІВ',note='Ілюстрація спорідненої версії')
   continue
  if spec['kind']=='ident':start=max(start,END-6)
  push(start,end,spec['kind'],spec['asset_id'],spec['title'],spec['country'],**x)
 # Extend the last brand ident to six seconds, taking the end of its preceding outro.
 if scenes[-1]['kind']=='ident' and scenes[-1]['duration']<6:
  newstart=END-6;scenes[-2]['end']=newstart;scenes[-2]['duration']=newstart-scenes[-2]['start'];scenes[-1].update(start=newstart,duration=6)
 # Keep scene IDs stable when one source interval replaces a short fallback.
 prior=json.loads((BASE/'episode.json').read_text()).get('scenes',[]) if (BASE/'episode.json').exists() else []
 existing={(round(s['start']*FPS),s['kind'],s.get('asset_id')):s['id'] for s in prior}
 counter=max([int(s['id'].split('-')[-1]) for s in prior if re.match(r'^shot-\d+$',s['id'])]+[0])
 for j,s in enumerate(scenes):
  key=(round(s['start']*FPS),s['kind'],s['asset_id'])
  if key in existing:s['id']=existing[key]
  else:counter+=1;s['id']=f'shot-{counter:03d}'
  s['visual_purpose']=s.get('narration_quote') or 'Opening visual explicitly tied to the spoken country/equipment overview'
 for a,b in zip(scenes,scenes[1:]):assert abs(a['end']-b['start'])<.002,(a['id'],b['id'],a['end'],b['start'])
 assert abs(scenes[-1]['end']-END)<.001
 check_archive_spacing(scenes)
 chapters=[]
 for row in rows:
  if row['heading']:
   title=re.sub(r'^\d\d:\d\d\s*—\s*','',row['text']);chapters.append({'title':title,'start':round(pt[row['i']+1]*FPS)/FPS})
 project={'schema':'arsenal.semantic-edit.v1','title':'Польща проти Німеччини: порівняння військових арсеналів','width':1920,'height':1080,'fps':30,'duration':END,'audio':'audio/voice.mp3','audio_original_duration':DURATION,'audio_policy':'Preserve the immutable supplied recording and tempo','motion_policy':{'photo_camera':'locked','rotation_seconds_per_revolution':24,'native_3d_fps':30,'card_entrance':'once then hold'},'scenes':scenes,'chapters':chapters,'asr_exact_token_match_ratio':json.loads((BASE/'alignment/report.json').read_text())['exact_token_agreement']}
 for s in scenes:
  if s['kind'] in ['photo','turntable','archive','ident']:assert s['asset_id'] in assets,(s['id'],s['asset_id'])
  for k,_,_ in s.get('sides',[]):assert k in assets,k
 (BASE/'episode.json').write_text(json.dumps(project,ensure_ascii=False,indent=2));mix={k:round(sum(s['duration'] for s in scenes if s['kind']==k),3) for k in set(s['kind'] for s in scenes)};baseline=0.23561683045510923;report={'seconds_by_kind':mix,'archive_share':mix.get('archive',0)/END,'previous_episode_archive_share':baseline,'archive_relative_share_increase':mix.get('archive',0)/END/baseline-1,'scenes_by_kind':dict(Counter(s['kind'] for s in scenes)),'source_decisions':decisions,'first_90_seconds_shots':sum(s['start']<90 for s in scenes)};(BASE/'media-mix.json').write_text(json.dumps(report,indent=2));(BASE/'chapters.uk.txt').write_text('\n'.join(f"{int(c['start'])//60:02d}:{int(c['start'])%60:02d} {c['title']}" for c in chapters)+'\n');print('BUILT',len(scenes),'scenes',END,'sec',report,flush=True)
if __name__=='__main__':main()
