"""Compile explicit semantic assignments against the unchanged voiceover word times."""
from pathlib import Path
import json,math,subprocess,re
from collections import Counter
from visual_map import SPANS
from tools.edit_rules import check_archive_spacing
BASE=Path(__file__).resolve().parent;FPS=30
FALLBACK={'rafale-indian-action':'rafale-india','rafale-action':'rafale','rafale-tlp':'rafale','yudh20':'sig716','yudh22':'sig716','m777-india':'m777','m777-joint':'m777','integrated':'akash','malabar':'kolkata','navy-shakti':'kolkata','sub-sindhuraj':'kalvari','falcon':'j10','brahmos-launch':'brahmos','brahmos-test':'brahmos','vikrant-video':'vikrant','m109-action':'m109','apache-demo':'model-apache','optics-training':'sig716','medevac-training':'sig716','austrahind':'sig716','infantry2019':'sig716','apache-indian-action':'model-apache','k4-launch':'arihant'}
# Content-reviewed bounds, not arbitrary whole-video offsets.
SOURCE_WINDOWS={'yudh20':[(0,17),(40,65),(66,86)],'yudh22':[(0,14),(15,34),(35,54),(55,74),(75,99)],'rafale-indian-action':[(11.5,29),(35,47)],'rafale-action':[(3,113)],'rafale-tlp':[(73.5,78),(102,108)],'m777-india':[(8,26),(38,54),(86,124)],'m777-joint':[(15,36)],'integrated':[(12,22)],'malabar':[(30,53),(70,112)],'navy-shakti':[(4,50)],'sub-sindhuraj':[(0,124)],'falcon':[(0,124)],'vikrant-video':[(26,35),(59,65),(100,110)],'brahmos-launch':[(0,10.8)],'brahmos-test':[(0,7.5)],'m109-action':[(8,110)],'apache-demo':[(8,110)],'optics-training':[(7,25),(37,49),(70,99),(101,115)],'medevac-training':[(8,57),(85,113)],'austrahind':[(3,13),(20,33),(35,55),(62,79)],'infantry2019':[(2,62)],'apache-indian-action':[(7,26),(32,65)],'k4-launch':[(0,25)]}
COMPARES={'aircraft':[('rafale-india','RAFALE','IN'),('j10','J-10 · РОДИНА','PK')],'tanks':[('bhishma','Т-90S BHISHMA','IN'),('vt4','VT-4','PK')],'drones':[('heron','HERON','IN'),('shahpar','SHAHPAR-II','PK')],'airdefense':[('s400','С-400 · РОДИНА','IN'),('hq9','HQ-9 · РОДИНА','PK')],'missiles':[('brahmos','BRAHMOS','IN'),('shaheen','SHAHEEN · РОДИНА','PK')],'navies':[('vikrant','INS VIKRANT','IN'),('agosta','AGOSTA · РОДИНА','PK')]}
NODES={'system':['Розвідка','Координація','Підготовка'],'claims':['Заяви сторін','Незалежні свідчення','Межі підтвердження'],'infantry-system':['Захист та оптика','Зв’язок','Підготовка'],'training':['Люди','Командування','Забезпечення'],'drone-system':['Управління','Захищений зв’язок','Протидія РЕБ'],'airdefense-system':['Радари','Командні пункти','Ракети та розрахунки'],'nuclear':['ІНДІЯ ≈ 190','ПАКИСТАН ≈ 170','Оцінка · січень 2026'],'escalation':['Обмежений конфлікт','Ризик ескалації','Ядерне стримування'],'sh15':['155 мм','Колісне шасі','Мобільність']}
def main():
 old=json.loads((BASE/'episode.json').read_text()).get('scenes',[]) if (BASE/'episode.json').exists() else []
 identity=lambda s:(round(s['start']*30),round(s['end']*30),s['kind'],s['asset_id'])
 previous_ids={identity(s):s['id'] for s in old}
 duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(BASE/'audio/voiceover.mp3')]));END=math.ceil(duration*30)/30
 pars={x['i']:x for x in json.loads((BASE/'alignment/paragraphs.json').read_text())};pt={i:x['start'] for i,x in pars.items()};words={x['i']:x for x in json.loads((BASE/'alignment/word_anchors.json').read_text())};assets={x['id']:x for x in json.loads((BASE/'assets/manifest.json').read_text())};scenes=[];history={};used={};decisions=[]
 def at(i,needle):
  n=re.findall(r'[a-zа-яіїєґ0-9]+',needle.lower());w=words[i]
  for j in range(len(w['tokens'])-len(n)+1):
   if w['tokens'][j:j+len(n)]==n:return w['times'][j]
  raise ValueError(('No scripted word onset',i,needle))
 def push(start,end,kind,key='original',title='',country='IN',**kw):
  start=round(start*30)/30;end=round(end*30)/30
  if end<=start:return
  s=dict(start=start,end=end,duration=end-start,kind=kind,asset_id=key,title=title or assets.get(key,{}).get('display_name',''),country=country,entrance_once=True,settle_after=1.2,note='',**kw)
  if kind=='archive':
   a=assets.get(key);url=a.get('video_source') if a else None;slot=None
   if a and a.get('video') and (url not in history or start-history[url]>60):
    for lo,hi in SOURCE_WINDOWS.get(key,[(0,a['duration']-.1)]):
     off=max(lo,kw.get('preferred_in',0));stop=min(hi,a['duration']-.1)
     for used_start,used_end in sorted(used.get(url,[])):
      if used_end<=off+.001:continue
      if used_start<=off+.001:off=used_end;continue
      stop=min(stop,used_start);break
     available=stop-off
     if available>=1:slot=(off,min(end-start,12 if start>=90 else 6.5,math.floor(available*30)/30));break
   if slot:
    off,length=slot;cut=round((start+length)*30)/30;s.update(end=cut,duration=cut-start,source_in=off);scenes.append(s);used.setdefault(url,[]).append((off,off+s['duration']));history[url]=cut
    if end-cut>.02:push(cut,end,'photo',FALLBACK[key],country=country,narration_quote=kw.get('narration_quote',''))
    return
   decisions.append({'time':start,'asset':key,'decision':'Corresponding photo: missing source, interval exhausted or >60 second cooldown'});return push(start,end,'photo',FALLBACK[key],country=country,narration_quote=kw.get('narration_quote',''))
  if kind=='photo' and key not in assets:
   if key=='sh15':s.update(kind='graphic',asset_id='original',nodes=NODES['sh15'],title='SH-15 · САМОХІДНА ГАУБИЦЯ')
   else:raise ValueError(('Missing actual subject photo',key))
  if kind=='graphic':s['nodes']=NODES[key]
  if kind=='question':s['nodes']=['Авіація','Ракети','Флот'] if 'ЗДИВУВАЛО' in title else ['Ваша думка','Ваш вибір країн','Коментарі']
  if kind=='compare':s['sides']=COMPARES[key]
  if kind=='turntable':
   s['note']='3D-візуалізація родини техніки';s['source_in']=kw.get('source_in',0);assert s['duration']+s['source_in']<=assets[key]['duration']+.01
  if kind=='map':s['source_in']=kw.get('source_in',0);assert s['duration']+s['source_in']<=assets[key]['duration']+.01
  scenes.append(s)
 # Intro: no title-only lead-in. Cuts use actual spoken phrases.
 push(0,3.5,'map','map-region')
 push(3.5,7.9,'archive','rafale-tlp','RAFALE · ФРАНЦІЯ, НАВЧАННЯ 2022')
 push(7.9,pt[2],'turntable','model-rafale','RAFALE · РОДИНА ЛІТАКІВ')
 push(pt[2],pt[3],'archive','rafale-indian-action','RAFALE · RED FLAG–ALASKA, 2024')
 cut=at(3,'далекобійні');push(pt[3],cut,'photo','j10','J-10 · РОДИНА ЛІТАКІВ','PK');push(cut,pt[4],'photo','pl15','PL-15 · РОДИНА РАКЕТ','PK')
 push(pt[4],pt[5],'photo','rafale-india','DASSAULT RAFALE')
 push(pt[5],pt[6],'photo','j10ce','J-10CE · ЕКСПОЗИЦІЯ, 2024','PK')
 push(pt[6],pt[7],'turntable','model-rafale','RAFALE · РОДИНА ЛІТАКІВ',source_in=8)
 push(pt[7],pt[8],'map','map-north')
 push(pt[8],pt[9],'compare','aircraft','RAFALE ТА J-10CE')
 push(pt[9],pt[10],'graphic','system','БОЙОВА СИСТЕМА')
 push(pt[10],pt[11],'turntable','model-mig29','МІГ-29 · РОДИНА ЛІТАКІВ')
 for i,group in [(11,[('танки','photo','bhishma','Т-90S BHISHMA','IN'),('надзвукові','photo','brahmos','BRAHMOS','IN'),('авіаносці','photo','vikrant','INS VIKRANT','IN')]),(12,[('винищувачі','photo','j10','J-10 · РОДИНА ЛІТАКІВ','PK'),('танки','photo','vt4','VT-4','PK'),('ракети','photo','shaheen','SHAHEEN · РОДИНА','PK'),('ППО','photo','hq9','HQ-9 · РОДИНА','PK')])]:
  ts=[pt[i]]+[at(i,g[0]) for g in group[1:]]+[pt[i+1]]
  for j,(_,kind,key,title,c) in enumerate(group):push(ts[j],ts[j+1],kind,key,title,c)
 push(pt[13],pt[14],'map','map-region')
 push(pt[14],pt[15],'compare','aircraft','ІНДІЯ ТА ПАКИСТАН')
 push(pt[15],pt[16],'archive','m777-india','M777 · НАВЧАННЯ, 2026')
 push(pt[16],pt[18],'turntable','model-apache','AH-64 APACHE · РОДИНА')
 push(pt[18],pt[22],'ident','channel-ident','АРСЕНАЛ 360°')
 for spec in SPANS:
  start=max(pt[spec['a']],scenes[-1]['end']);nexti=next((i for i in sorted(pt) if i>spec['b']),None);end=pt[nexti] if nexti is not None else END
  if end<=start:continue
  quote=' '.join(pars[i]['text'] for i in range(spec['a'],spec['b']+1) if i in pars);kind=spec['kind'];key=spec['asset_id'];title=spec['title'];c=spec['country']
  if kind=='section':
   cut=min(start+3.3,end);push(start,cut,kind,title=title,narration_quote=quote)
   if end-cut>.02:
    follow=next(x for x in SPANS if x['a']>spec['a']);fk=follow['asset_id'];pk={'model-rafale':'rafale-india','model-apache':'model-apache'}.get(fk,fk) if follow['kind']!='archive' else FALLBACK[fk];push(cut,end,'photo' if pk in assets else 'graphic',pk,country=follow['country'],title=follow['title'],narration_quote=quote)
   continue
  if spec['a']==114:
   cut=at(115,'медичного');push(start,cut,'archive','optics-training','ОПТИКА ТА ЗВ’ЯЗОК · НАВЧАННЯ, 2026',c,preferred_in=37,narration_quote=quote);push(cut,end,'archive','medevac-training','МЕДИЧНА ПІДГОТОВКА · НАВЧАННЯ, 2026',c,narration_quote=quote);continue
  if spec['a']==31:
   ts=[start,at(31,'МіГ'),at(31,'винищувачі'),end]
   # Exact full names can have punctuation; anchors are script-token based.
   for j,(k,asset,tit) in enumerate([('turntable','model-mirage','MIRAGE 2000 · РОДИНА'),('turntable','model-mig29','МІГ-29 · РОДИНА'),('photo','tejas','HAL TEJAS')]):push(ts[j],ts[j+1],k,asset,tit,c,narration_quote=quote)
   continue
  if kind=='ident':
   start=max(start,END-6)
   if scenes[-1]['end']<start:push(scenes[-1]['end'],start,'outro',title='АРСЕНАЛ 360°',subtitle='Світ військових технологій')
  preferred={43:35,68:66,73:7,108:35,116:15,119:2,121:40,128:38,185:12,195:16,198:5.5,208:32,241:1,272:75}.get(spec['a'],0)
  push(start,end,kind,key,title,c,narration_quote=quote,preferred_in=preferred)
 for i,s in enumerate(scenes):s['id']=previous_ids.get(identity(s),f'insert-{round(s["start"]*30):06d}');s['visual_purpose']=s.get('narration_quote') or 'Exact scripted equipment or geographic context at spoken word onset'
 for a,b in zip(scenes,scenes[1:]):assert abs(a['end']-b['start'])<.002,(a,b)
 assert abs(scenes[-1]['end']-END)<.001 and sum(round(s['duration']*30) for s in scenes)==round(END*30)
 check_archive_spacing(scenes)
 for s in scenes:
  for asset,_,_ in s.get('sides',[]):assert asset in assets,asset
 rows=json.loads((BASE/'inputs/paragraphs.json').read_text());chapters=[{'start':pt[r['i']+1],'title':r['text']} for r in rows if r['heading']]
 project=dict(schema='arsenal.semantic-edit.v1',title='Індія проти Пакистану: військові арсенали',width=1920,height=1080,fps=30,duration=END,audio='audio/voiceover.mp3',audio_original_duration=duration,audio_policy='Original supplied recording, unchanged words and tempo',motion_policy=dict(photo_camera='locked',rotation_seconds_per_revolution=24,native_3d_fps=30,card_entrance='once then hold',maps='continuous terrain mesh camera animation; source credits in SOURCES.md'),scenes=scenes,chapters=chapters)
 (BASE/'episode.json').write_text(json.dumps(project,ensure_ascii=False,indent=2));mix={k:round(sum(s['duration'] for s in scenes if s['kind']==k),3) for k in set(s['kind'] for s in scenes)};report=dict(seconds_by_kind=mix,archive_share=mix.get('archive',0)/END,scenes_by_kind=dict(Counter(s['kind'] for s in scenes)),source_decisions=decisions,first_90_seconds_shots=sum(s['start']<90 for s in scenes),three_d_quality_policy='Detailed actual mesh geometry, native 30fps, slow 15 degree/s rotation; no illustrative green tank meshes')
 (BASE/'media-mix.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));(BASE/'chapters.uk.txt').write_text('\n'.join(f"{int(c['start'])//60:02d}:{int(c['start'])%60:02d} {c['title']}" for c in chapters)+'\n');print('BUILT',len(scenes),END,report,flush=True)
if __name__=='__main__':main()
