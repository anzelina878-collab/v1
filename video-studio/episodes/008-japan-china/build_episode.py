"""Compile explicit semantic assignments against the unchanged voiceover word times."""
from pathlib import Path
import json,math,subprocess,re
from collections import Counter
from visual_map import SPANS
from tools.edit_rules import check_archive_spacing
BASE=Path(__file__).resolve().parent;FPS=30
FALLBACK={'japan-armor':'type10','rq4-action':'rq4','ah1s-action':'ah1s','japan-antitank':'type89','jasdf-f35':'f35a','jasdf-arrival':'f35a','j20-airshow':'j20','j20-anniversary':'j20','kaga-trials':'kaga','izumo-trials':'izumo','japan-infantry':'type89','japan-pac3':'patriot','japan-sm3':'maya','sm3-cooperative':'maya','tomahawk-action':'type12-base','jinan-video':'type055','soryu-video':'soryu','taigei-launch':'taigei','china-helos':'z10'}
SOURCE_WINDOWS={}
COMPARES={'aircraft':[('f35a','F-35A · РОДИНА','JP'),('j20','J-20','CN')],'tanks':[('type10','TYPE 10','JP'),('type99a','TYPE 99A','CN')],'carriers':[('izumo','JS IZUMO','JP'),('fujian','FUJIAN','CN')],'rifles':[('type20','HOWA TYPE 20','JP'),('qbz191','QBZ-191','CN')],'missiles':[('type12-base','TYPE 12','JP'),('df26','DF-26 · РОДИНА','CN')],'drones':[('rq4','RQ-4 · РОДИНА','JP'),('wingloong2','WING LOONG II','CN')]}
NODES={'drones-research':['Швидкісна розвідка','Взаємодія з літаками','Експериментальні системи'],'sensors':['AN/APG-81','Сучасні сенсори','Обмін інформацією'],'air-system':['Підготовка пілотів','Раннє попередження','Ракети та союзники'],'mobility':['Маса машини','Інфраструктура','Мобільність'],'land-scale':['Танковий парк','Сухопутні сили','Масштаб операцій'],'uncertainty':['Відкриті джерела','Випробування','Закриті характеристики'],'infantry-system':['Зв’язок','Розвідка та підтримка','Підготовка'],'pcl181':['155 мм','Колісне шасі','Підтримка військ'],'artillery-system':['Розвідка','Боєприпаси','Передача координат'],'maritime-drones':['Спостереження','Морські завдання','Оборона островів'],'readiness':['Демонстратор','Випробування','Серійна система'],'airdefense-system':['Радари','Кораблі','Винищувачі'],'future-helo':['Пілотовані платформи','Нові завдання','Безпілотні системи'],'japan-deterrence':['Власної зброї немає','Союз зі США','Розширене стримування'],'nuclear-estimates':['Сотні боєголовок','Відкриті оцінки','Точні дані закриті'],'nuclear-risk':['Стримування','Ризик ескалації','Гуманітарні наслідки'],'comparison-scope':['Національні арсенали','Підтримка союзників','Географія та готовність'],'logistics':['Перекидання сил','Забезпечення','Контроль повітря']}
def main():
 old=json.loads((BASE/'episode.json').read_text()).get('scenes',[]) if (BASE/'episode.json').exists() else []
 identity=lambda s:(round(s['start']*30),round(s['end']*30),s['kind'],s['asset_id'])
 previous_ids={identity(s):s['id'] for s in old if all(k in s for k in ['start','end','kind','asset_id'])}
 duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(BASE/'audio/voiceover.mp3')]));END=math.ceil(duration*30)/30
 pars={x['i']:x for x in json.loads((BASE/'alignment/paragraphs.json').read_text())};pt={i:x['start'] for i,x in pars.items()};words={x['i']:x for x in json.loads((BASE/'alignment/word_anchors.json').read_text())};assets={x['id']:x for x in json.loads((BASE/'assets/manifest.json').read_text())};scenes=[];history={};used={};decisions=[]
 def at(i,needle):
  n=re.findall(r'[a-zа-яіїєґ0-9]+',needle.lower());w=words[i]
  for j in range(len(w['tokens'])-len(n)+1):
   if w['tokens'][j:j+len(n)]==n:return w['times'][j]
  raise ValueError(('No scripted word onset',i,needle))
 def push(start,end,kind,key='original',title='',country='JP',**kw):
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
     if available>=1:slot=(off,min(end-start,16 if start>=90 else 5.5,math.floor(available*30)/30));break
   if slot:
    off,length=slot
    if start>=90 and .02<end-start-length<1:length=end-start-1
    cut=round((start+length)*30)/30;s.update(end=cut,duration=cut-start,source_in=off);scenes.append(s);used.setdefault(url,[]).append((off,off+s['duration']));history[url]=cut
    if end-cut>.02:push(cut,end,'photo',FALLBACK[key],country=country,narration_quote=kw.get('narration_quote',''))
    return
   decisions.append({'time':start,'asset':key,'decision':'Corresponding photo: missing source, interval exhausted or >60 second cooldown'});return push(start,end,'photo',FALLBACK[key],country=country,narration_quote=kw.get('narration_quote',''))
  if kind=='photo' and key not in assets:
   if key=='sh15':s.update(kind='graphic',asset_id='original',nodes=NODES['sh15'],title='SH-15 · САМОХІДНА ГАУБИЦЯ')
   else:raise ValueError(('Missing actual subject photo',key))
  if kind=='graphic':s['nodes']=NODES[key]
  if kind=='question':s['nodes']=['Авіація','Бронетехніка','Флот'] if 'ВРАЗИЛО' in title else ['Оберіть категорію','Напишіть коментар','Запропонуйте країни']
  if kind=='compare':s['sides']=COMPARES[key]
  if kind=='turntable':
   s['note']='3D-візуалізація родини техніки';s['source_in']=kw.get('source_in',0);assert s['duration']+s['source_in']<=assets[key]['duration']+.01
  if kind=='map':s['source_in']=kw.get('source_in',0);assert s['duration']+s['source_in']<=assets[key]['duration']+.01
  scenes.append(s)
 SOURCE_WINDOWS.update(json.loads((BASE/'source-windows.json').read_text()))
 def piece(start,end,kind,key,title='',country='JP',**kw):
  if end-start<.04:return
  push(start,end,kind,key,title,country,**kw)
 def script_cuts(i,items):
  end=pt[next(j for j in sorted(pt) if j>i)];ts=[pt[i]]+[at(i,item[0]) for item in items[1:]]+[end]
  # Very fast spoken lists become short explicit cuts, never inferred random assets.
  for j,(_,kind,key,title,c) in enumerate(items):piece(ts[j],ts[j+1],kind,key,title,c)
 def two(i,kind1,key1,title1,kind2,key2,title2,needle,c1='JP',c2='CN'):
  end=pt[next(j for j in sorted(pt) if j>i)];cut=at(i,needle);piece(pt[i],cut,kind1,key1,title1,c1);piece(cut,end,kind2,key2,title2,c2)
 two(1,'turntable','model-f35b','F-35 · РОДИНА ЛІТАКІВ','archive','j20-airshow','J-20 · ЧЖУХАЙ, 2018','китайського')
 two(2,'photo','type10','TYPE 10','photo','type99a','TYPE 99A','проти')
 two(3,'photo','maya','MAYA · AEGIS','photo','type055','TYPE 055 · NANCHANG','китайських')
 two(4,'photo','taigei','TAIGEI · РОДИНА СУБМАРИН','photo','type094','TYPE 094 · РОДИНА','китайські')
 piece(pt[5],pt[5]+4,'map','map-region');piece(pt[5]+4,pt[6],'compare','aircraft','ВИСОКІ ТЕХНОЛОГІЇ · ДВА ПІДХОДИ')
 script_cuts(6,[('', 'photo','type99a','TYPE 99A','CN'),('ракетною','photo','df26','DF-26','CN'),('винищувачами','archive','j20-anniversary','J-20 · АРХІВ КНР','CN'),('ядерною','photo','df41','DF-41','CN')])
 script_cuts(7,[('', 'photo','f35a','F-35A · РОДИНА','JP'),('радари','photo','maya','MAYA · AEGIS','JP'),('протичовнові','photo','soryu','SORYU','JP'),('союз','archive','kaga-trials','JS KAGA · ВИПРОБУВАННЯ, 2024','JP')])
 piece(pt[8],pt[9],'map','map-navy')
 # Fast opening inventory is timed to each actual named category.
 script_cuts(9,[('', 'archive','jasdf-arrival','F-35A JASDF · АРХІВ, 2017','JP'),('танки','photo','type10','TYPE 10','JP'),('ракети','photo','type12-base','TYPE 12','JP'),('піхотне','photo','type20','HOWA TYPE 20','JP'),('артилерію','photo','type19','TYPE 19','JP'),('безпілотники','photo','rq4','RQ-4 GLOBAL HAWK · РОДИНА','JP'),('протиповітряну','archive','japan-pac3','PATRIOT PAC-3 · НАВЧАННЯ, 2017','JP'),('вертольоти','photo','z10','Z-10','CN'),('флот','archive','izumo-trials','JS IZUMO · ВИПРОБУВАННЯ, 2021','JP'),('ядерні','photo','df41','DF-41','CN')])
 piece(pt[10],pt[10]+4,'compare','aircraft','МАСШТАБ ТА ТЕХНОЛОГІЇ');piece(pt[10]+4,pt[11],'turntable','model-f35b','F-35 · РОДИНА ЛІТАКІВ')
 piece(pt[11],pt[15],'ident','channel-ident','АРСЕНАЛ 360°')
 for spec in SPANS:
  start=max(pt[spec['a']],scenes[-1]['end']);nexti=next((i for i in sorted(pt) if i>spec['b']),None);end=pt[nexti] if nexti is not None else END
  if end<=start:continue
  quote=' '.join(pars[i]['text'] for i in range(spec['a'],spec['b']+1) if i in pars);kind=spec['kind'];key=spec['asset_id'];c=spec['country'];title=spec['title']
  if kind=='section':
   # A chapter appears once, then settles. Do not insert a subsecond object flash.
   cut=min(start+2.6,end)
   if end-cut<1:cut=end
   piece(start,cut,'section','original',title,c,narration_quote=quote)
   if end-cut>.03:
    nxt=next(x for x in SPANS if x['a']>spec['a']);nk=nxt['asset_id'];pk=FALLBACK[nk] if nxt['kind']=='archive' else nk
    if nxt['kind']=='compare':piece(cut,end,'compare',nk,nxt['title'],nxt['country'],narration_quote=quote)
    elif nk in assets and assets[nk].get('photo'):piece(cut,end,'photo',nk,assets[nk].get('display_name',nxt['title']),nxt['country'],narration_quote=quote)
    elif pk in assets:piece(cut,end,'photo',pk,assets[pk].get('display_name',pk),nxt['country'],narration_quote=quote)
    else:piece(cut,end,'graphic',nk,nxt['title'],nxt['country'],narration_quote=quote)
   continue
  if spec['a']==22:
   cut=at(22,'F-2');piece(start,cut,'photo','f15j','F-15J','JP',narration_quote=quote);piece(cut,end,'photo','f2','MITSUBISHI F-2','JP',narration_quote=quote);continue
  if spec['a']==28:
   cut=at(28,'J-10C');piece(start,cut,'photo','j16','SHENYANG J-16','CN',narration_quote=quote);piece(cut,end,'photo','j10c-exact','CHENGDU J-10C','CN',narration_quote=quote);continue
  if spec['a']==59:
   cut=at(60,'DF-26');piece(start,cut,'photo','df21','DF-21 · РОДИНА','CN',narration_quote=quote);piece(cut,end,'photo','df26','DF-26 · РОДИНА','CN',narration_quote=quote);continue
  if spec['a']==106:
   cut=at(106,'CH-4');piece(start,cut,'photo','wingloong2','WING LOONG II · ВИСТАВКА','CN',narration_quote=quote);piece(cut,end,'photo','ch4','CH-4 · ВИСТАВКОВИЙ ЗРАЗОК','CN',narration_quote=quote);continue
  if spec['a']==144:
   cut=at(144,'Taigei');piece(start,cut,'archive','soryu-video','SORYU · ЯПОНСЬКА СУБМАРИНА','JP',narration_quote=quote);piece(cut,end,'archive','taigei-launch','TAIGEI · СПУСК СУБМАРИНИ JINGEI, 2022','JP',narration_quote=quote);continue
  if spec['a']==151:
   ts=[start,at(151,'Shandong'),at(151,'Fujian'),end]
   for j,(k,t) in enumerate([('liaoning','LIAONING'),('shandong','SHANDONG'),('fujian','FUJIAN')]):piece(ts[j],ts[j+1],'photo',k,t,'CN',narration_quote=quote)
   continue
  if spec['a']==180:
   ts=[start,at(180,'Aegis'),at(180,'підводними'),at(180,'протиракетною'),end];items=[('turntable','model-f35b','F-35 · РОДИНА'),('photo','maya','MAYA · AEGIS'),('photo','soryu','SORYU'),('archive','japan-pac3','PATRIOT PAC-3 · НАВЧАННЯ, 2017')]
   for j,(k,asset,t) in enumerate(items):piece(ts[j],ts[j+1],k,asset,t,'JP',narration_quote=quote)
   continue
  if kind=='turntable' and end-start>24:
   cut=start+24;piece(start,cut,kind,key,title,c,narration_quote=quote);piece(cut,end,'photo','f35a','F-35A · РОДИНА',c,narration_quote=quote);continue
  piece(start,end,kind,key,title,c,narration_quote=quote,subtitle='Світ військових технологій' if kind=='outro' else '')
 # Adjacent instances of the same settled card are one shot, with one entrance.
 merged=[]
 for scene in scenes:
  if merged and scene['kind'] in ['graphic','compare'] and all(merged[-1].get(k)==scene.get(k) for k in ['kind','asset_id','title','country']):
   prev=merged[-1];prev.update(end=scene['end'],duration=scene['end']-prev['start']);prev['narration_quote']=prev.get('narration_quote','')+' '+scene.get('narration_quote','')
  else:merged.append(scene)
 scenes=merged
 for s in scenes:s['id']=previous_ids.get(identity(s),f'insert-{round(s["start"]*30):06d}');s['visual_purpose']=s.get('narration_quote') or 'Exact scripted subject at spoken word onset'
 for a,b in zip(scenes,scenes[1:]):assert abs(a['end']-b['start'])<.002,(a,b)
 assert abs(scenes[-1]['end']-END)<.001 and sum(round(s['duration']*30) for s in scenes)==round(END*30)
 check_archive_spacing(scenes)
 for s in scenes:
  for k,_,_ in s.get('sides',[]):assert k in assets,k
 headings=[r for r in json.loads((BASE/'inputs/paragraphs.json').read_text()) if r['heading']];chapters=[{'start':0 if r['i']==0 else pt[r['i']+1],'title':r['text']} for r in headings]
 project=dict(schema='arsenal.semantic-edit.v1',title='Японія проти Китаю: військові арсенали',width=1920,height=1080,fps=30,duration=END,audio='audio/voiceover.mp3',audio_original_duration=duration,audio_policy='Original supplied voice, unchanged words and tempo',motion_policy=dict(photo_camera='locked',rotation_seconds_per_revolution=24,native_3d_fps=30,card_entrance='once then hold',maps='true geographic terrain mesh; source attribution outside picture'),scenes=scenes,chapters=chapters)
 (BASE/'episode.json').write_text(json.dumps(project,ensure_ascii=False,indent=2));mix={k:round(sum(s['duration'] for s in scenes if s['kind']==k),3) for k in set(s['kind'] for s in scenes)};report=dict(seconds_by_kind=mix,archive_share=mix.get('archive',0)/END,scenes_by_kind=dict(Counter(s['kind'] for s in scenes)),source_decisions=decisions,first_90_seconds_shots=sum(s['start']<90 for s in scenes),three_d_quality_policy='Detailed true meshes only; rejected unsuitable OH1 geometry; native slow F35B family display; real photo cutouts for other subjects')
 (BASE/'media-mix.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));(BASE/'chapters.uk.txt').write_text('\n'.join(f"{int(c['start'])//60:02d}:{int(c['start'])%60:02d} {c['title']}" for c in chapters)+'\n');print('BUILT',len(scenes),END,report,flush=True)
if __name__=='__main__':main()
