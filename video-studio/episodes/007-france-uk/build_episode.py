"""Compile explicit semantic assignments against the unchanged voiceover word times."""
from pathlib import Path
import json,math,subprocess,re
from collections import Counter
from visual_map import SPANS
from tools.edit_rules import check_archive_spacing
BASE=Path(__file__).resolve().parent;FPS=30
FALLBACK={'rafale-action':'rafale','rafale-tlp':'rafale','leclerc-action':'leclerc','leclerc-fire':'leclerc','challenger-action':'challenger2','challenger-training':'challenger2','caesar-action':'caesar','caesar-night':'caesar','archer-action':'archer','typhoon-walk':'model-typhoon','typhoon-action':'model-typhoon','qe-embark':'qe','qe-operations':'qe','cdg-operations':'charles','tomahawk-launch':'tomahawk','tomahawk-action':'tomahawk','sub-launch':'tomahawk','french-infantry':'hk416','british-infantry':'l85a3','french-exercise':'hk416','apache-fire':'model-apache','apache-demo':'model-apache','trident-test':'trident'}
SOURCE_WINDOWS={}
COMPARES={'aircraft':[('rafale','RAFALE','FR'),('model-typhoon','TYPHOON','GB')],'tanks':[('leclerc','LECLERC','FR'),('challenger2','CHALLENGER 2','GB')],'carriers':[('charles','CHARLES DE GAULLE','FR'),('qe','HMS QUEEN ELIZABETH','GB')],'airdefense':[('sampt','SAMP/T','FR'),('skysabre','SKY SABRE','GB')],'french-deterrence':[('triomphant','TRIOMPHANT','FR'),('rafale','RAFALE','FR')]}
NODES={'survival':['Протидія дронам','Мінний захист','Взаємодія підрозділів'],'artillery':['Швидкість','Точність','Мобільність'],'drones':['Повітряна розвідка','Малі БПЛА та FPV','Протидія РЕБ'],'readiness':['Оголошені проєкти','Випробування','Реальна готовність'],'airdefense':['Радари','Зв’язок','Взаємодія з авіацією'],'helicopters':['Підтримка військ','Захист від ППО','Узгоджені дії'],'navy':['Готовність кораблів','Боєприпаси','Підготовка екіпажів'],'nuclear':['ФРАНЦІЯ ≈ 290','БРИТАНІЯ ≈ 225','Військові запаси · SIPRI 2026'],'future-sub':['Майбутня заміна Vanguard','Програма Dreadnought','Новий клас субмарин'],'deterrence':['Стратегічні ризики','Гуманітарні наслідки','Відповідальність'],'system':['Промисловість','Підготовка','Взаємодія сил']}
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
 def push(start,end,kind,key='original',title='',country='FR',**kw):
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
     if available>=1:slot=(off,min(end-start,12 if start>=90 else 5.5,math.floor(available*30)/30));break
   if slot:
    off,length=slot;cut=round((start+length)*30)/30;s.update(end=cut,duration=cut-start,source_in=off);scenes.append(s);used.setdefault(url,[]).append((off,off+s['duration']));history[url]=cut
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
 # Source ranges are populated only after shot-level content review.
 SOURCE_WINDOWS.update(json.loads((BASE/'source-windows.json').read_text()))
 # Six exact subject cuts follow the six spoken platform names.
 names=[('Rafale','turntable','model-rafale','RAFALE','FR'),('Eurofighter','turntable','model-typhoon','EUROFIGHTER TYPHOON','GB'),('Leclerc','archive','leclerc-action','LECLERC · НАВЧАННЯ, 2018','FR'),('Challenger','archive','challenger-training','CHALLENGER 2 · НАВЧАННЯ, 2017','GB'),('Charles','photo','charles','CHARLES DE GAULLE','FR'),('Queen','photo','qe','HMS QUEEN ELIZABETH','GB')]
 times=[0]+[at(1,x[0]) for x in names[1:]]+[pt[2]]
 for j,(_,kind,key,title,c) in enumerate(names):push(times[j],times[j+1],kind,key,title,c)
 def split(i,end,items):
  begin=pt[i];ts=[begin+(end-begin)*j/len(items) for j in range(len(items)+1)]
  for j,(kind,key,title,c) in enumerate(items):push(ts[j],ts[j+1],kind,key,title,c)
 split(2,pt[3],[('map','map-region','','FR'),('turntable','model-rafale','RAFALE · РОДИНА','FR'),('turntable','model-f35b','F-35B · РОДИНА','GB')])
 push(pt[3],pt[4],'compare','aircraft','ДВА ПІДХОДИ')
 split(4,pt[5],[('archive','rafale-action','RAFALE · ФРАНЦІЯ, 2019','FR'),('photo','leclerc','LECLERC','FR')])
 split(5,pt[6],[('archive','qe-embark','F-35B · HMS QUEEN ELIZABETH, 2020','GB'),('turntable','model-f35b','F-35B · РОДИНА','GB'),('photo','astute','ASTUTE · РОДИНА','GB')])
 split(6,pt[7],[('map','map-region','','FR'),('archive','typhoon-action','RAF TYPHOON · RED FLAG, 2026','GB')])
 split(7,pt[8],[('photo','l85a3','L85A3','GB'),('archive','caesar-action','CAESAR · DYNAMIC FRONT, 2026','FR')])
 push(pt[8],pt[9],'compare','carriers','ФРАНЦІЯ ТА ВЕЛИКА БРИТАНІЯ')
 push(pt[9],pt[12],'ident','channel-ident','АРСЕНАЛ 360°')
 heading_rows=[r for r in json.loads((BASE/'inputs/paragraphs.json').read_text()) if r['heading']]
 chapter_first={r['i']+1:r['text'].split('.')[0] for r in heading_rows if 0<r['chapter']<=11}
 # Alignment confirms paragraphs 54,55 and closing 169:171 are absent in audio.
 for spec in SPANS:
  if spec['a'] in [54]:continue
  start=max(pt[spec['a']],scenes[-1]['end']);nexti=next((i for i in sorted(pt) if i>spec['b'] and i not in [54,55,169,170,171]),None);end=pt[nexti] if nexti is not None else END
  if spec['b']==53:end=298.7666666667
  if spec['a']==57:start=scenes[-1]['end']
  if spec['a']==167:end=END
  if end<=start:continue
  quote=' '.join(pars[i]['text'] for i in range(spec['a'],spec['b']+1) if i in pars)
  if spec['a'] in chapter_first:
   cut=min(end,start+2.4);push(start,cut,'section',title=chapter_first[spec['a']],narration_quote=quote);start=cut
  k=spec['kind'];key=spec['asset_id'];c=spec['country'];title=spec['title']
  if spec['a']==32:
   items=[('photo','griffon','VBMR GRIFFON','FR'),('photo','jaguar','EBRC JAGUAR','FR'),('photo','serval','VBMR-L SERVAL','FR')];ts=[start,at(32,'Jaguar'),at(32,'Serval'),end]
  elif spec['a']==41:
   items=[('photo','boxer','BOXER · РОДИНА','GB'),('photo','ajax','AJAX','GB')];ts=[start,at(41,'Ajax'),end]
  elif spec['a']==50:
   items=[('photo','exocet','EXOCET','FR'),('photo','aasm','AASM','FR'),('photo','aster','ASTER · РОДИНА','FR')];ts=[start,at(50,'AASM'),at(50,'Aster'),end]
  elif spec['a']==51:
   items=[('photo','brimstone','BRIMSTONE','GB'),('archive','tomahawk-action','TOMAHAWK · АРХІВ ВМС США, 2014','GB'),('photo','type45','TYPE 45 · ASTER','GB')];ts=[start,at(51,'Tomahawk'),at(51,'Aster'),end]
  elif spec['a']==149:
   items=[('turntable','model-rafale','RAFALE · РОДИНА','FR'),('photo','leclerc','LECLERC','FR'),('photo','caesar','CAESAR','FR'),('photo','sampt','SAMP/T','FR'),('photo','charles','CHARLES DE GAULLE','FR')];ts=[start,at(149,'Leclerc'),at(149,'CAESAR'),at(149,'SAMP'),at(149,'Charles'),end]
  elif spec['a']==151:
   items=[('turntable','model-typhoon','TYPHOON · РОДИНА','GB'),('turntable','model-f35b','F-35B · РОДИНА','GB'),('photo','challenger2','CHALLENGER 2','GB'),('turntable','model-apache','APACHE · РОДИНА','GB'),('photo','qe','HMS QUEEN ELIZABETH','GB'),('photo','astute','ASTUTE · РОДИНА','GB')];ts=[start,at(151,'F'),at(151,'Challenger'),at(151,'Apache'),at(151,'авіаносці'),at(151,'Astute'),end]
  else:
   push(start,end,k,key,title,c,narration_quote=quote,preferred_in={16:79,118:90,130:73.5}.get(spec['a'],0));continue
  for j,(kind,asset,tit,country) in enumerate(items):push(max(start,ts[j]),ts[j+1],kind,asset,tit,country,narration_quote=quote)
 for i,s in enumerate(scenes):s['id']=previous_ids.get(identity(s),f'insert-{round(s["start"]*30):06d}');s['visual_purpose']=s.get('narration_quote') or 'Exact scripted equipment or geographic context at spoken word onset'
 for a,b in zip(scenes,scenes[1:]):assert abs(a['end']-b['start'])<.002,(a,b)
 assert abs(scenes[-1]['end']-END)<.001 and sum(round(s['duration']*30) for s in scenes)==round(END*30)
 check_archive_spacing(scenes)
 for s in scenes:
  for asset,_,_ in s.get('sides',[]):assert asset in assets,asset
 chapters=[{'start':0 if r['i']==0 else pt[r['i']+1],'title':r['text']} for r in heading_rows]
 project=dict(schema='arsenal.semantic-edit.v1',title='Франція проти Великої Британії: військові арсенали',width=1920,height=1080,fps=30,duration=END,audio='audio/voiceover.mp3',audio_original_duration=duration,audio_policy='Original supplied recording, unchanged words and tempo',motion_policy=dict(photo_camera='locked',rotation_seconds_per_revolution=24,native_3d_fps=30,card_entrance='once then hold',maps='continuous terrain mesh camera animation; source credits in SOURCES.md'),scenes=scenes,chapters=chapters)
 (BASE/'episode.json').write_text(json.dumps(project,ensure_ascii=False,indent=2));mix={k:round(sum(s['duration'] for s in scenes if s['kind']==k),3) for k in set(s['kind'] for s in scenes)};report=dict(seconds_by_kind=mix,archive_share=mix.get('archive',0)/END,scenes_by_kind=dict(Counter(s['kind'] for s in scenes)),source_decisions=decisions,first_90_seconds_shots=sum(s['start']<90 for s in scenes),three_d_quality_policy='Detailed actual mesh geometry, native 30fps, slow 15 degree/s rotation; no primitive green tank meshes')
 (BASE/'media-mix.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));(BASE/'chapters.uk.txt').write_text('\n'.join(f"{int(c['start'])//60:02d}:{int(c['start'])%60:02d} {c['title']}" for c in chapters)+'\n');print('BUILT',len(scenes),END,report,flush=True)
if __name__=='__main__':main()
