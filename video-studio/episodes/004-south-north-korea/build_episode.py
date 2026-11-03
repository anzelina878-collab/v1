"""Compile authored equipment scenes against unchanged narration word times."""
import json,re,math,subprocess
from pathlib import Path
from collections import Counter
from visual_map import SPANS
from tools.edit_rules import check_archive_spacing
BASE=Path(__file__).resolve().parent;FPS=30
PREFERRED={'kr-air':8,'kr-infantry-field':8,'kr-navy':7,'kr-infantry':22,'kr-patriot-deploy':6,'kr-apache-rok':37,'kr-drone':1,'kr-navy-alt':6,'kr-k9-archive':2,'city-pyongyang-pan':0}
VALID_END={'kr-f15k':12,'kr-f35-flight':24.9,'kr-apache-rok':47,'kr-drone':11.5,'city-pyongyang-pan':18}
FALLBACK={'kr-kf21':'kf21','kr-infantry-field':'k2rifle','kr-navy-alt':'sejong','nk-parade':'type58','kr-f35-flight':'f35','kr-f15k':'f15k','kr-air':'f16','kr-k2-archive':'k2','kr-k2-maneuver':'k2','kr-k1':'k1','kr-k1-fire':'k1','kr-infantry':'k2rifle','kr-k9-archive':'k9','city-seoul':'seoul-photo','city-pyongyang':'pyongyang','city-pyongyang-pan':'pyongyang','kr-drone':'rq101','kr-patriot':'patriot','kr-patriot-deploy':'patriot','kr-apache':'apache','kr-apache-rok':'apache','kr-navy':'sejong'}
def norm(s):return re.findall(r'[a-zа-яіїєґ0-9]+',s.lower())
def main():
 duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(BASE/'audio/voice.mp3')]));END=math.ceil(duration*FPS)/FPS
 pars={x['i']:x for x in json.loads((BASE/'alignment/paragraphs.json').read_text())};pt={i:x['start'] for i,x in pars.items()};words={x['i']:x for x in json.loads((BASE/'alignment/word_anchors.json').read_text())};assets={a['id']:a for a in json.loads((BASE/'assets/manifest.json').read_text())};scenes=[];history={};used={};decisions=[]
 def at(i,needle):
  w=words[i];n=norm(needle)
  for j in range(len(w['tokens'])-len(n)+1):
   if w['tokens'][j:j+len(n)]==n:return w['times'][j]
  return pt[i]
 def push(start,end,kind,key='original',title='',country='KR',**kw):
  start=round(start*FPS)/FPS;end=round(end*FPS)/FPS
  if end<=start:return
  asset=assets.get(key,{});note=kw.pop('note','')
  if kind=='turntable':note='3D-візуалізація родини техніки'
  s=dict(start=start,end=end,duration=end-start,kind=kind,asset_id=key,title=title or asset.get('display_name',key.upper()),country=country,entrance_once=True,settle_after=1.2,note=note,**kw)
  if kind=='archive':
   asset=assets[key];source=asset['video_source'];offset=max(PREFERRED.get(key,0),used.get(source,0));available=min(asset['duration']-.1,VALID_END.get(key,1e9))-offset
   if source in history and start-history[source]<=60:
    decisions.append({'time':start,'source':key,'decision':'matching photograph: >60s archive cooldown'});s.update(kind='photo',asset_id=FALLBACK[key],title=assets[FALLBACK[key]]['display_name']);scenes.append(s);return
   count=min(round(s['duration']*FPS),round(kw.get('archive_cap',12)*FPS),math.floor(available*FPS));length=count/FPS
   if length<.8:
    s.update(kind='photo',asset_id=FALLBACK[key],title=assets[FALLBACK[key]]['display_name']);scenes.append(s);return
   cut=round((start+length)*FPS)/FPS
   if end-cut<.1 and end-start<=available:cut=end;length=end-start
   s.update(end=cut,duration=length,source_in=offset);scenes.append(s);history[source]=cut;used[source]=offset+length
   if end-cut>.02:push(cut,end,'photo',FALLBACK[key],country=country,note='Реальне фото · відповідний тип техніки',narration_quote=kw.get('narration_quote',''))
   return
  scenes.append(s)
 # Opening: fast equipment changes at the actual spoken names, with slow object rotations.
 push(0,pt[2],'map','map-globe','ОДИН ПІВОСТРІВ · ДВІ ДЕРЖАВИ')
 times=[pt[2],at(2,'танки'),at(2,'артилерія'),at(2,'сучасні'),pt[3]]
 for j,(kind,key,title) in enumerate([('archive','kr-f35-flight','F-35 · СПІЛЬНИЙ ПОЛІТ, 2025'),('photo','k2','K2 BLACK PANTHER'),('archive','kr-k9-archive','K9 THUNDER'),('archive','kr-navy','ROKS SEJONG THE GREAT')]):push(times[j],times[j+1],kind,key,title,archive_cap=3)
 p3=[pt[3],at(3,'тисячі'),at(3,'балістичні'),at(3,'ядерна'),pt[4]]
 for j,(key,title) in enumerate([('koksan','M1989 KOKSAN'),('m2020','M2020 / CHEONMA-2'),('hwasong17','HWASONG-17')]):push(p3[j],p3[j+1],'photo',key,title,'KP')
 push(p3[3],p3[4],'graphic',title='СТРАТЕГІЧНЕ СТРИМУВАННЯ',nodes=['РАКЕТНІ СИЛИ','ЯДЕРНИЙ АРСЕНАЛ'])
 push(pt[4],pt[4]+2.7,'turntable','model-f16','F-16 · РОДИНА ЛІТАКІВ');push(pt[4]+2.7,pt[5],'photo','kf21','KF-21 · ПРОГРАМА')
 push(pt[5],pt[5]+3,'archive','nk-parade','ПХЕНЬЯН · ПАРАДНА РЕПЕТИЦІЯ, 2011','KP',archive_cap=3);push(pt[5]+3,pt[6],'photo','hwasong17',country='KP')
 push(pt[6],pt[7],'compare',title='КІЛЬКІСТЬ ТА ТЕХНОЛОГІЇ',sides=[['f35','ПІВДЕННА КОРЕЯ','KR'],['mig29','КНДР · ТИП ЛІТАКА','KP']])
 push(pt[7],pt[7]+3.5,'photo','type58',country='KP');push(pt[7]+3.5,pt[8],'archive','city-pyongyang-pan','ПХЕНЬЯН · АРХІВ МІСТА','KP',archive_cap=5)
 names=[('авіацію','turntable','model-f16','АВІАЦІЯ · F-16'),('танки','photo','k2','ТАНКИ · K2'),('ракети','photo','hyunmoo','РАКЕТИ · HYUNMOO'),('артилерію','photo','k9','АРТИЛЕРІЯ · K9'),('безпілотники','photo','rq101','БЕЗПІЛОТНИКИ · RQ-101'),('протиповітряну','photo','kmsam','ПРОТИПОВІТРЯНА ОБОРОНА'),('військово','photo','sejong','ВІЙСЬКОВО-МОРСЬКІ СИЛИ')]
 ts=[pt[8]]+[at(8,x[0]) for x in names[1:]]+[pt[9]]
 for j,(_,kind,key,title) in enumerate(names):push(ts[j],ts[j+1],kind,key,title)
 push(pt[9],pt[9]+4,'map','map-korea','КОРЕЙСЬКИЙ ПІВОСТРІВ');push(pt[9]+4,pt[10],'archive','city-seoul','СЕУЛ · АРХІВ МІСТА',archive_cap=5);push(pt[10],pt[12],'ident','channel-ident','АРСЕНАЛ 360°')
 # Full script: manually authored semantic spans; no keyword-based random asset picker.
 for j,spec in enumerate(SPANS):
  nextspec=SPANS[j+1] if j+1<len(SPANS) else None;start=max(pt[spec['a']],scenes[-1]['end']);end=pt[nextspec['a']] if nextspec else END
  if end<=start:continue
  quote=' '.join(pars[i]['text'] for i in range(spec['a'],spec['b']+1) if i in pars);kw={k:v for k,v in spec.items() if k not in ['a','b','kind','asset_id','title','country']};kw['narration_quote']=quote
  if spec['kind']=='section':
   cut=min(end if end-start>=3 else END,start+3.3);push(start,cut,'section',title=spec['title'],narration_quote=quote)
   if end-cut>.1:
    chapter=pars[spec['a']]['chapter'];key={1:'f35',2:'k2',3:'hyunmoo',4:'k2rifle',5:'k9',6:'rq101',7:'patriot',8:'apache',9:'sejong',10:'k2'}[chapter];push(cut,end,'photo',key,narration_quote=quote)
   continue
  if spec['a'] in [17,21,71,139,168,171]:
   choices={17:[('f16','turntable','model-f16','F-16 · РОДИНА ЛІТАКІВ','KR'),('FA-50','photo','fa50','FA-50 · ТИП ЛІТАКА','KR')],21:[('МіГ-21','photo','mig21','МІГ-21 · ТИП ЛІТАКА','KP'),('МіГ-23','photo','mig23','МІГ-23 · ТИП ЛІТАКА','KP'),('Су-25','photo','su25','СУ-25 · ТИП ЛІТАКА','KP')],71:[('K3','photo','k3','K3','KR'),('K12','photo','k12','K12','KR'),('Raybolt','photo','raybolt','RAYBOLT','KR')],139:[('Мі-2','photo','mi2','МІ-2 · ТИП ВЕРТОЛЬОТА','KP'),('Мі-24','photo','mi24','МІ-24 · ТИП ВЕРТОЛЬОТА','KP')],168:[('F-35','photo','f35','F-35A · ТИП ЛІТАКА','KR'),('F-15K','photo','f15k','F-15K SLAM EAGLE','KR'),('K2','photo','k2','K2 BLACK PANTHER','KR'),('K9','photo','k9','K9 THUNDER','KR'),('есмінці','photo','sejong','SEJONG THE GREAT','KR')],171:[('сухопутні','photo','pokpung','БРОНЕТЕХНІКА КНДР','KP'),('артилерійські','photo','koksan','M1989 KOKSAN','KP'),('ракетну','photo','hwasong17','HWASONG-17','KP')]}[spec['a']]
   times=[start]+[max(start,min(end,at(spec['a'],x[0]))) for x in choices[1:]]+[end]
   for k,(_,kind,key,title,country) in enumerate(choices):push(times[k],times[k+1],kind,key,title,country,narration_quote=quote)
   continue
  if spec['kind']=='ident':start=min(start,END-6);scenes[-1]['end']=start;scenes[-1]['duration']=start-scenes[-1]['start']
  push(start,end,spec['kind'],spec['asset_id'],spec['title'],spec['country'],**kw)
 for i,s in enumerate(scenes):s['id']=f'shot-{i+1:03d}';s['visual_purpose']=s.get('narration_quote') or 'Opening country/equipment shot matched to spoken word onset'
 for a,b in zip(scenes,scenes[1:]):assert abs(a['end']-b['start'])<.002,(a,b)
 assert abs(scenes[-1]['end']-END)<.001 and sum(round(s['duration']*FPS) for s in scenes)==round(END*FPS)
 check_archive_spacing(scenes)
 for s in scenes:
  if s['kind'] in ['photo','archive','turntable','ident']:assert s['asset_id'] in assets,s
  for k,_,_ in s.get('sides',[]):assert k in assets,k
 chapters=[{'start':pt[r['i']+1],'title':re.sub(r'^\d\d:\d\d\s*—\s*','',r['text'])} for r in json.loads((BASE/'inputs/paragraphs.json').read_text()) if r['heading']]
 project={'schema':'arsenal.semantic-edit.v1','title':'Південна Корея проти КНДР: військові арсенали','width':1920,'height':1080,'fps':FPS,'duration':END,'audio':'audio/voice.mp3','audio_original_duration':duration,'audio_policy':'Original supplied recording, unchanged words and tempo','motion_policy':{'photo_camera':'locked','rotation_seconds_per_revolution':24,'native_3d_fps':30,'card_entrance':'once then hold'},'scenes':scenes,'chapters':chapters}
 (BASE/'episode.json').write_text(json.dumps(project,ensure_ascii=False,indent=2));mix={k:round(sum(s['duration'] for s in scenes if s['kind']==k),3) for k in set(s['kind'] for s in scenes)};report={'seconds_by_kind':mix,'archive_share':mix.get('archive',0)/END,'scenes_by_kind':dict(Counter(s['kind'] for s in scenes)),'source_decisions':decisions,'first_90_seconds_shots':sum(s['start']<90 for s in scenes),'3d_quality_policy':'Only approved detailed F16/Apache/Blackhawk meshes. All schematic green vehicle meshes excluded.'};(BASE/'media-mix.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));(BASE/'chapters.uk.txt').write_text('\n'.join(f"{int(c['start'])//60:02d}:{int(c['start'])%60:02d} {c['title']}" for c in chapters)+'\n');print('BUILT',len(scenes),END,report,flush=True)
if __name__=='__main__':main()
