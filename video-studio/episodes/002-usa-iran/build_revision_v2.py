"""Restore the first film's object-led visual balance, preserving supplied audio.
The first 90 seconds are a manually authored, speech-bound fast montage.
"""
import json,copy,math
from pathlib import Path
B=Path(__file__).resolve().parent;FPS=30

def main():
 project=json.loads((B/'episode.json').read_text());assets={a['id']:a for a in json.loads((B/'assets/manifest.v2.json').read_text())};paragraphs={x['paragraph']:x['start'] for x in json.loads((B/'alignment/paragraphs.json').read_text())};out=[]
 def add(start,end,kind,key,title='',country='US',**kw):
  start=round(start*FPS)/FPS;end=round(end*FPS)/FPS
  if end<=start:return
  s={'start':start,'end':end,'duration':end-start,'kind':kind,'asset_id':key,'title':title or assets.get(key,{}).get('display_name',key.upper()),'country':country,'entrance_once':True,'settle_after':1.2,**kw}
  if kind=='turntable':s['note']='Схематична 3D-візуалізація' if assets[key].get('schematic') else '3D-візуалізація';s['visual_origin']='true_3d_render'
  if kind=='photo' and assets.get(key,{}).get('visual_origin')=='true_3d_render':s['visual_origin']='true_3d_render';s['note']='Схематична 3D-візуалізація' if assets[key].get('schematic') else '3D-візуалізація · статичний ракурс'
  out.append(s)
 def pair(start,end,title,left,right):add(start,end,'compare','original-comparison',title,sides=[list(left),list(right)])
 def model(s,key,title=None,spin=True,country=None):add(s['start'],s['end'],'turntable' if spin else 'photo',key,title or assets[key]['display_name'],country or s.get('country') or ('IR' if key in ['model-f14','model-mig29','model-shahed136-illustrative','model-ghadir-illustrative'] else 'US'),a=s.get('a'),b=s.get('b'),narration_quote=s.get('narration_quote',''))
 # Hook. Short shots are tied to the actual recorded words; no extra intro delays the voice.
 add(0,2.5,'archive','ford','USS GERALD R. FORD · CVN-78',source_in=0)
 add(2.5,5.4,'turntable','model-ford-illustrative')
 add(5.4,8.2,'photo','ford','USS GERALD R. FORD · CVN-78',camera_motion='detail')
 add(8.2,11.5,'archive','ford-deck','ПАЛУБА USS GERALD R. FORD',source_in=8)
 add(11.5,14.733333,'archive','ford-crew','ЕКІПАЖ USS GERALD R. FORD',source_in=50)
 add(14.733333,17.4,'turntable','model-ghadir-illustrative','GHADIR','IR')
 add(17.4,20,'photo','ghadir','GHADIR','IR')
 add(20,21.766667,'photo','model-ghadir-illustrative','GHADIR','IR')
 pair(21.766667,24.8,'ДВА КОРАБЛІ · РІЗНІ ЗАВДАННЯ',('ford','USS GERALD R. FORD','US'),('model-ghadir-illustrative','GHADIR','IR'))
 add(24.8,27.933333,'photo','ford','USS GERALD R. FORD')
 add(27.933333,31,'archive','f35','F-35 LIGHTNING II',source_in=0)
 add(31,34.2,'photo','product-f35','F-35 LIGHTNING II')
 add(34.2,37.5,'photo','f35','F-35 LIGHTNING II')
 add(37.5,41.333333,'photo','product-f35','F-35 · СЕНСОРИ ТА ОБМІН ДАНИМИ')
 add(41.333333,44.4,'turntable','model-f14','F-14 TOMCAT','IR')
 add(44.4,47.2,'photo','f14','F-14 TOMCAT','IR')
 add(47.2,49.166667,'photo','model-f14','F-14 TOMCAT','IR')
 add(49.166667,51.8,'turntable','model-f22')
 add(51.8,53.533333,'photo','ford','АВІАНОСНА ГРУПА · США')
 add(53.533333,57.133333,'archive','iran-missiles','РАКЕТНІ СИЛИ ІРАНУ','IR',source_in=0)
 add(57.133333,58.6,'turntable','model-shahed136-illustrative','SHAHED-136','IR')
 add(58.6,60.266667,'archive','iran-boats','ШВИДКІСНІ КАТЕРИ · ІРАН','IR',source_in=1)
 add(60.266667,64.166667,'turntable','model-f22')
 add(64.166667,66.833333,'photo','model-abrams','M1 ABRAMS')
 add(66.833333,70.766667,'ident','channel-ident','АРСЕНАЛ 360°')
 pair(70.766667,74.566667,'США ПРОТИ ІРАНУ',('model-f22','F-22 RAPTOR','US'),('model-f14','F-14 TOMCAT','IR'))
 add(74.566667,76.1,'photo','model-f22','АВІАЦІЯ · F-22')
 add(76.1,77.4,'photo','model-abrams','БРОНЕТЕХНІКА · M1 ABRAMS')
 add(77.4,78.633333,'photo','product-fateh','РАКЕТИ · FATEH-110','IR')
 add(78.633333,80,'photo','model-shahed136-illustrative','БЕЗПІЛОТНИКИ · SHAHED-136','IR')
 add(80,81.366667,'photo','patriot','ПРОТИПОВІТРЯНА ОБОРОНА · PATRIOT')
 add(81.366667,82.5,'photo','model-apache','ВЕРТОЛЬОТИ · AH-64')
 add(82.5,84.2,'photo','model-ford-illustrative','ФЛОТ · USS GERALD R. FORD')
 add(84.2,87.2,'turntable','model-m4','M4A1')
 add(87.2,90,'photo','model-f22','ТЕХНОЛОГІЇ · МОЖЛИВОСТІ · ОБМЕЖЕННЯ')
 # After the hook, keep real photographs and licensed video; replace empty text screens with objects.
 spin_map={(15,16):'model-f22',(18,19):'model-f22',(41,41):'model-f14',(52,53):'model-abrams',(59,62):'model-abrams',(150,151):'model-shahed136-illustrative',(160,161):'model-shahed136-illustrative',(212,212):'model-ford-illustrative',(224,226):'model-ghadir-illustrative',(231,231):'model-f22'}
 still_map={(22,23):'product-f35',(45,45):'model-f14',(83,83):'product-fateh',(104,105):'product-sejjil',(107,108):'product-fateh',(109,110):'sejjil',(115,115):'model-m4',(120,120):'product-m7',(140,140):'product-m777',(141,141):'m777',(162,163):'model-shahed136-illustrative',(184,184):'product-bavar',(193,194):'model-chinook',(198,198):'bell214',(243,244):'model-abrams'}
 model_photos={'f14':'model-f14','kowsar':None,'m7':None,'ghadir':'model-ghadir-illustrative'}
 for old in project['scenes']:
  if old['end']<=90:continue
  s=copy.deepcopy(old);s['start']=max(90,s['start']);s['duration']=s['end']-s['start'];span=(s.get('a'),s.get('b'))
  # Direct model names on video, rather than narration quotes or an empty lower third.
  if span==(13,14):
   add(s['start'],s['end'],'photo','model-f22','F-22 RAPTOR');continue
  if s['kind']=='archive':
   s['title']=assets[s['asset_id']].get('display_name',s['asset_id'].upper())
   explicit={'ford':'USS GERALD R. FORD · CVN-78','f35':'F-35 LIGHTNING II','f22':'F-22 RAPTOR','f15ex':'F-15EX EAGLE II','b2':'B-2 SPIRIT','b21':'B-21 RAIDER','kc46':'KC-46 PEGASUS','abrams':'M1 ABRAMS','tomahawk':'TOMAHAWK','paladin':'M109A7 PALADIN','m777':'M777','himars':'M142 HIMARS','mq9':'MQ-9 REAPER','rq4':'RQ-4 GLOBAL HAWK','patriot':'PATRIOT','thaad':'THAAD · ВИПРОБУВАННЯ','apache':'AH-64 APACHE','blackhawk':'UH-60 BLACK HAWK','chinook':'CH-47 CHINOOK','destroyer':'USS HARVEY C. BARNUM JR. · ARLEIGH BURKE','iran-boats':'ШВИДКІСНІ КАТЕРИ · ІРАН'}
   s['title']=explicit.get(s['asset_id'],s['title']);out.append(s);continue
  if s['kind']=='turntable':
   s['asset_id']={'m4-360':'model-m4','abrams-360':'model-abrams'}.get(s['asset_id'],s['asset_id']);model(s,s['asset_id']);continue
  if span in spin_map:model(s,spin_map[span]);continue
  if span in still_map:
   key=still_map[span];add(s['start'],s['end'],'photo',key,assets[key]['display_name'],s.get('country','IR' if key in ['product-fateh','product-sejjil','model-ghadir-illustrative','model-shahed136-illustrative','model-f14'] else 'US'),a=s.get('a'),b=s.get('b'));continue
  if s['kind']=='graphic':
   if span==(77,79):pair(s['start'],s['end'],'БРОНЕТЕХНІКА · ДВА ПІДХОДИ',('model-abrams','M1 ABRAMS','US'),('karrar','KARRAR','IR'));continue
   if span==(98,99):add(s['start'],s['end'],'archive','iran-missiles','РАКЕТНІ СИЛИ ІРАНУ','IR',source_in=8);continue
   if span==(124,126):add(s['start'],s['end'],'archive','us-infantry','ПІХОТА · США','US',source_in=0);continue
   if span==(136,137):pair(s['start'],s['end'],'АРТИЛЕРІЯ ІРАНУ',('raad2','RAAD-2','IR'),('fajr5','FAJR-5','IR'));continue
   if span==(175,177):
    cut=round(paragraphs[177]*FPS)/FPS;add(s['start'],cut,'photo','patriot','PATRIOT');add(cut,s['end'],'archive','iran-sam','ППО ІРАНУ · НАВЧАННЯ','IR',source_in=2);continue
   if span==(178,178):pair(s['start'],s['end'],'СИСТЕМИ ППО ІРАНУ',('s300','С-300ПМУ-2 · ТИП','IR'),('bavar','BAVAR-373','IR'));continue
   if span==(182,183):add(s['start'],s['end'],'photo','bavar','BAVAR-373','IR');continue
   if span==(206,207):pair(s['start'],s['end'],'АВІАНОСНА ГРУПА',('ford','USS GERALD R. FORD','US'),('destroyer','ARLEIGH BURKE','US'));continue
   if span in [(227,229),(241,242)]:pair(s['start'],s['end'],'ДВІ МОРСЬКІ СТРАТЕГІЇ',('model-ford-illustrative','USS GERALD R. FORD','US'),('model-ghadir-illustrative','GHADIR','IR'));continue
   if span==(239,240):pair(s['start'],s['end'],'РІЗНІ АРСЕНАЛИ',('model-f22','F-22 RAPTOR','US'),('model-shahed136-illustrative','SHAHED-136','IR'));continue
   if span==(247,248):add(s['start'],s['end'],'archive','us-infantry','ПІДГОТОВКА ТА ЗАБЕЗПЕЧЕННЯ','US',source_in=0);continue
   if span==(249,251):
    cut1=s['start']+s['duration']/3;cut2=s['start']+s['duration']*2/3
    add(s['start'],cut1,'turntable','model-f22','F-22 RAPTOR');add(cut1,cut2,'turntable','model-shahed136-illustrative','SHAHED-136','IR');add(cut2,s['end'],'turntable','model-ford-illustrative','USS GERALD R. FORD');continue
   if span==(252,253):add(s['start'],s['end'],'ident','channel-ident','АРСЕНАЛ 360°');continue
  if s['kind']=='photo' and s['asset_id'] in model_photos and model_photos[s['asset_id']]:
   # Keep the real Tomcat and Ghadir photos as context; only selected longer shots become true geometry.
   if s.get('a') in [42,219]:model(s,model_photos[s['asset_id']],country=s.get('country','IR'));continue
  if s['kind']=='compare':
   for side in s['sides']:
    key=side[0]
    replacements={'f22':'model-f22','f14':'model-f14','mig29':'model-mig29','chinook':'model-chinook','ghadir':'model-ghadir-illustrative','shahed136':'model-shahed136-illustrative','abrams':'model-abrams'}
    if key in replacements:side[0]=replacements[key]
    elif 'product-'+key in assets:side[0]='product-'+key
  out.append(s)
 # Merge continued cards/images instead of making the same object appear again.
 merged=[]
 for s in out:
  if merged and s['kind'] in ['photo','turntable'] and merged[-1]['kind']==s['kind'] and s['asset_id']==merged[-1]['asset_id'] and abs(s['start']-merged[-1]['end'])<.001:
   merged[-1]['end']=s['end'];merged[-1]['duration']=s['end']-merged[-1]['start'];continue
  merged.append(s)
 ir={'f14','mig29','su24','kowsar','karrar','t72','bmp2','safir','fateh','zolfaghar','shahab','sejjil','soumar','g3','raad2','fajr5','shahed129','mohajer6','shahed136','s300','bavar','bell214','jamaran','kilo','ghadir','iran-sam','iran-missiles','iran-boats'}
 for i,s in enumerate(merged):
  s['id']=f'v2-shot-{i+1:03d}'
  if s['kind'] not in ['graphic','compare','ident']:
   k=s['asset_id'].removeprefix('product-').removeprefix('model-').removesuffix('-illustrative')
   if k in ir:s['country']='IR'
 for a,b in zip(merged,merged[1:]):assert abs(a['end']-b['start'])<.001,(a['id'],b['id'],a['end'],b['start'])
 history={}
 for s in merged:
  if s['kind']=='archive':
   key=s['asset_id'];a=assets[key]
   if key in history and s['start']-history[key]<=60:raise ValueError(('Archive repeated too soon',s['id'],key))
   history[key]=s['end'];assert s.get('source_in',0)+s['duration']<=a['duration']+.04,(s['id'],key,s['duration'],a['duration'])
 # Add a genuine moving model alongside the archive for every newly available platform.
 expanded=[]
 swap={'b2':'model-b2','apache':'model-apache','blackhawk':'model-blackhawk','chinook':'model-chinook'}
 for scene in merged:
  if scene['kind']=='archive' and scene['asset_id'] in swap and scene['start']>=90:
   mid=round((scene['start']+scene['duration']*.5)*FPS)/FPS
   live=copy.deepcopy(scene);live.update(id=scene['id']+'-a',end=mid,duration=mid-scene['start']);expanded.append(live)
   cg=copy.deepcopy(scene);cg.update(id=scene['id']+'-b',start=mid,duration=scene['end']-mid,kind='turntable',asset_id=swap[scene['asset_id']],note='3D-візуалізація',visual_origin='true_3d_render');cg.pop('source_in',None);expanded.append(cg)
  elif scene['kind']=='compare' and scene['title']=='РАДЯНСЬКІ ПЛАТФОРМИ':
   mid=round((scene['start']+scene['duration']*.5)*FPS)/FPS
   for suffix,start,end,kind,key,title in [('a',scene['start'],mid,'turntable','model-mig29','МіГ-29'),('b',mid,scene['end'],'photo','su24','СУ-24 · ТИП')]:
    item=copy.deepcopy(scene);item.update(id=scene['id']+'-'+suffix,start=start,end=end,duration=end-start,kind=kind,asset_id=key,title=title,country='IR');item.pop('sides',None)
    if kind=='turntable':item.update(note='3D-візуалізація',visual_origin='true_3d_render')
    expanded.append(item)
  else:expanded.append(scene)
 for item in expanded:
  if item.get('asset_id')=='product-bavar':item['asset_id']='bavar'
  for side in item.get('sides',[]):
   if side[0]=='product-bavar':side[0]='bavar'
 merged=expanded
 project['scenes']=merged;project['revision']='v2-object-led';project['notes']='Real photos + licensed archive + true geometry; one entrance then still information plates; first 90s fast hook';(B/'episode.v2.json').write_text(json.dumps(project,ensure_ascii=False,indent=2));print('REVISION_READY',len(merged),'scenes; hook shots',sum(s['start']<90 for s in merged))
if __name__=='__main__':main()
