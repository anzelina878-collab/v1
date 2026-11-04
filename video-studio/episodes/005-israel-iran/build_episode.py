"""Build the new visual edit from user script, word timestamps and reviewed assets."""
from pathlib import Path
import json,math,re,subprocess
from collections import Counter
from visual_map import SPANS
from tools.edit_rules import check_archive_spacing
BASE=Path(__file__).resolve().parent;FPS=30
FALLBACK={'ua-shahed':'shahed136','f35i-action':'f35i','f35i-arrival':'f35i','f16i-action':'f16i','f35i-formation':'f35i','air-joint':'f35i','apache-action':'model-apache','apache-demo':'model-apache','iran-sub':'ghadir','israel-navy-action':'saar6','iron-intercepts':'irondome','iron-intercepts2':'irondome','iron-system':'irondome','arrow-test':'arrow','arrow3-test':'arrow','david-test':'davidsling','david-test2':'davidsling','iran-ballistic':'fateh','iran-ghader':'jamaran','iran-sam':'bavar','conflict2024':'irondome','conflict2024b':'arrow','conflict2025':'irondome','merkava-action':'merkava','merkava3-action':'merkava','idf-ready':'f35i','idf-ops':'irondome','idf-intercept':'irondome','idf-infantry':'x95','idf-field':'tavor','m109-action':'m109','iran-artillery':'raad2','idf-drone':'hermes900','israel-navy':'saar6','iran-boats-action':'iran-boats'}
PREFERRED={'arrow-test':40,'david-test':72,'david-test2':58,'iron-system':20,'iran-ghader':7,'iran-sam':5,'f35i-arrival':40,'f16i-action':45,'idf-infantry':19,'idf-field':12,'idf-ready':10,'iran-sub':8,'iran-boats-action':0,'israel-navy-action':0,'idf-drone':5.8};VALID_END={'f35i-action':36,'idf-drone':29.8,'iran-boats-action':8,'israel-navy-action':6}
def norm(s):return re.findall(r'[a-zа-яіїєґ0-9]+',s.lower())
def main():
 old=json.loads((BASE/'episode.json').read_text())['scenes'] if (BASE/'episode.json').exists() else []
 identity=lambda s:(round(s['start']*30),round(s['end']*30),s['kind'],s['asset_id'])
 previous_ids={identity(s):s['id'] for s in old}
 duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(BASE/'audio/voice.mp3')]));END=math.ceil(duration*30)/30
 rows=json.loads((BASE/'inputs/paragraphs.json').read_text());pars={x['i']:x for x in json.loads((BASE/'alignment/paragraphs.json').read_text())};pt={i:x['start'] for i,x in pars.items()};words={x['i']:x for x in json.loads((BASE/'alignment/word_anchors.json').read_text())};assets={a['id']:a for a in json.loads((BASE/'assets/manifest.json').read_text())};scenes=[];history={};used={};decisions=[]
 def at(i,needle):
  w=words[i];n=norm(needle)
  for j in range(len(w['tokens'])-len(n)+1):
   if w['tokens'][j:j+len(n)]==n:return w['times'][j]
  return pt[i]
 def push(start,end,kind,key='original',title='',country='IL',**kw):
  start=round(start*30)/30;end=round(end*30)/30
  if end<=start:return
  note=kw.pop('note','');s=dict(start=start,end=end,duration=end-start,kind=kind,asset_id=key,title=title or assets.get(key,{}).get('display_name',''),country=country,entrance_once=True,settle_after=1.2,note=note,**kw)
  if kind=='turntable':s['note']='3D-візуалізація родини техніки';assert key in assets
  if kind=='archive':
   if key not in assets or not assets[key].get('video'):
    replacement=FALLBACK[key];assert replacement in assets,(key,replacement)
    decisions.append(dict(time=start,source=key,decision='Use corresponding verified photo: documentary source unavailable'))
    s.update(kind='photo',asset_id=replacement,title=assets[replacement]['display_name']);scenes.append(s);return
   a=assets[key];url=a['video_source'];offset=max(PREFERRED.get(key,0),used.get(url,0),kw.get('source_in',0));available=min(a['duration']-.1,VALID_END.get(key,1e9))-offset
   if url in history and start-history[url]<=60:available=0
   length=min(end-start,kw.get('archive_cap',14),math.floor(available*30)/30)
   if length<.8:
    replacement=FALLBACK[key];s.update(kind='photo',asset_id=replacement,title=assets[replacement]['display_name']);decisions.append(dict(time=start,source=key,decision='Matching photo: exhausted interval or >60 second reuse cooldown'));scenes.append(s);return
   cut=round((start+length)*30)/30;s.update(end=cut,duration=cut-start,source_in=offset);scenes.append(s);history[url]=cut;used[url]=offset+s['duration']
   if end-cut>.02:push(cut,end,'photo',FALLBACK[key],country=country,narration_quote=kw.get('narration_quote',''))
   return
  if kind=='turntable':
   a=assets[key];s['source_in']=kw.get('source_in',0);assert end-start+s['source_in']<=a['duration']+.01
  if kind=='map':s['source_in']=kw.get('source_in',0);assert end-start+s['source_in']<=assets[key]['duration']+.01
  scenes.append(s)
 # Opening follows actual equipment-name onsets; no five-second text-only lead-in.
 push(0,min(pt[2],5.2),'map','map-region')
 if pt[2]>5.2:push(5.2,pt[2],'archive','conflict2024','ІЗРАЇЛЬ · КВІТЕНЬ 2024',archive_cap=6)
 choices={2:[('сучасну','archive','f35i-action','F-35I ADIR','IL'),('протиповітряну','archive','iron-intercepts','IRON DOME · 2023','IL')],3:[('Балістичні','archive','iran-ballistic','ІРАН · ВИПРОБУВАЛЬНІ ПУСКИ','IR'),('безпілотники','photo','shahed136','SHAHED-136','IR'),('сухопутні','photo','karrar','KARRAR','IR')],4:[('F-35','photo','f35i','F-35I ADIR','IL'),('танки','photo','merkava','MERKAVA MK.4','IL'),('Arrow','archive','arrow-test','ARROW · ВИПРОБУВАННЯ, 2020','IL')],5:[('Fateh','photo','fateh','FATEH-110','IR'),('Shahab','photo','shahab','SHAHAB','IR'),('Shahed','photo','shahed136','SHAHED-136','IR'),('артилерійські','photo','fajr5','FAJR-5','IR')]}
 for i,group in choices.items():
  times=[pt[i]]+[at(i,x[0]) for x in group[1:]]+[pt[i+1]]
  for j,(_,kind,key,title,c) in enumerate(group):push(times[j],times[j+1],kind,key,title,c,archive_cap=5,narration_quote=pars[i]['text'])
 push(pt[6],pt[7],'archive','conflict2024b','ІЗРАЇЛЬ · ЖОВТЕНЬ 2024',archive_cap=8)
 push(pt[7],pt[8],'map','map-region',source_in=6)
 push(pt[8],pt[8]+6,'archive','iron-system','IRON DOME · АРХІВ СИСТЕМИ',archive_cap=6)
 push(pt[8]+6,pt[9],'photo','f35i','F-35I ADIR')
 push(pt[9],pt[9]+4,'turntable','model-f14','F-14 · РОДИНА ЛІТАКІВ','IR')
 push(pt[9]+4,pt[10],'archive','iron-intercepts2','IRON DOME · ПЕРЕХОПЛЕННЯ, 2023',archive_cap=8)
 names=[('авіацію','turntable','model-f16','АВІАЦІЯ · F-16','IL'),('танки','photo','merkava','MERKAVA MK.4','IL'),('піхоту','photo','tavor','TAVOR','IL'),('артилерію','photo','atmos','ATMOS 2000','IL'),('ракети','photo','sejjil','SEJJIL','IR'),('безпілотники','photo','shahed136','SHAHED-136','IR'),('ППО','photo','irondome','IRON DOME','IL'),('вертольоти','turntable','model-apache','AH-64 · РОДИНА','IL'),('військово','photo','saar6','SA’AR 6','IL')]
 times=[pt[10]]+[at(10,x[0]) for x in names[1:]]+[pt[11]]
 for j,(_,kind,key,title,c) in enumerate(names):push(times[j],times[j+1],kind,key,title,c,narration_quote=pars[10]['text'])
 push(pt[11],pt[14],'ident','channel-ident','АРСЕНАЛ 360°')
 for spec in SPANS:
  start=max(pt[spec['a']],scenes[-1]['end']);nexti=next((i for i in sorted(pt) if i>spec['b']),None);end=pt[nexti] if nexti is not None else END
  if end<=start:continue
  quote=' '.join(pars[i]['text'] for i in range(spec['a'],spec['b']+1) if i in pars);kw={k:v for k,v in spec.items() if k not in ['a','b','kind','asset_id','title','country']};kw['narration_quote']=quote
  if spec['kind']=='section':
   cut=min(start+3.3,end);push(start,cut,'section',title=spec['title'],narration_quote=quote)
   if end-cut>.02:
    key={1:'f35i',2:'merkava',3:'fateh',4:'tavor',5:'m109',6:'hermes900',7:'irondome',8:'model-apache',9:'saar6',10:'f35i'}[pars[spec['a']]['chapter']];push(cut,end,'photo',key,country='IR' if key=='fateh' else 'IL',narration_quote=quote)
   continue
  splits={21:[('F-15','photo','f15i','F-15 · РОДИНА ЛІТАКІВ','IL'),('F-16','turntable','model-f16','F-16 · РОДИНА ЛІТАКІВ','IL')],29:[('МіГ-29','photo','model-mig29','МІГ-29 · РОДИНА ЛІТАКІВ','IR'),('F-4','photo','f4','F-4 PHANTOM · ІРАН','IR'),('Су-24','photo','su24','СУ-24 · ТИП ЛІТАКА','IR')],53:[('T-72','photo','t72','Т-72 · РОДИНА ТАНКІВ','IR'),('Zulfiqar','photo','zulfiqar','ZULFIQAR','IR')],136:[('Hermes 450','photo','hermes450','HERMES 450','IL'),('Hermes 900','photo','hermes900','HERMES 900','IL')],146:[('Mohajer-6','photo','mohajer6','MOHAJER-6','IR'),('Shahed-129','photo','shahed129','SHAHED-129','IR')],177:[('3rd Khordad','photo','khordad3','3RD KHORDAD','IR'),('С-300','photo','s300','С-300 · РОДИНА КОМПЛЕКСІВ','IR')],211:[('Alvand','photo','alvand','ALVAND · РОДИНА','IR'),('Jamaran','photo','jamaran','JAMARAN','IR')],212:[('Ghadir','archive','iran-sub','GHADIR · АРХІВ ФЛОТУ','IR'),('Fateh','photo','fatehsub','FATEH · ПІДВОДНИЙ ЧОВЕН','IR')],225:[('F-35','photo','f35i','F-35I ADIR','IL'),('F-15','photo','f15i','F-15 · РОДИНА','IL'),('F-16','turntable','model-f16','F-16 · РОДИНА','IL')],227:[('Tavor','photo','tavor','TAVOR','IL'),('Negev','photo','negev','NEGEV','IL'),('Spike','photo','spike','SPIKE','IL')],231:[('Fateh','photo','fateh','FATEH-110','IR'),('Shahab','photo','shahab','SHAHAB','IR'),('Sejjil','photo','sejjil','SEJJIL','IR'),('Shahed','photo','shahed136','SHAHED-136','IR')]}
  if spec['a'] in splits:
   group=splits[spec['a']];times=[start]+[min(end,max(start,at(spec['a'],x[0]))) for x in group[1:]]+[end]
   for j,(_,kind,key,title,c) in enumerate(group):push(times[j],times[j+1],kind,key,title,c,narration_quote=quote)
   continue
  if spec['kind']=='ident':start=max(scenes[-1]['start']+.1,END-6);scenes[-1]['end']=start;scenes[-1]['duration']=start-scenes[-1]['start']
  push(start,end,spec['kind'],spec['asset_id'],spec['title'],spec['country'],**kw)
 for i,s in enumerate(scenes):s['id']=previous_ids.get(identity(s),f'insert-{round(s["start"]*30):06d}' if old else f'shot-{i+1:03d}');s['visual_purpose']=s.get('narration_quote') or 'Equipment or geographic visual matched to the exact spoken onset'
 for a,b in zip(scenes,scenes[1:]):assert abs(a['end']-b['start'])<.002,(a['id'],b['id'],a['end'],b['start'])
 assert abs(scenes[-1]['end']-END)<.001 and sum(round(s['duration']*30) for s in scenes)==round(END*30)
 check_archive_spacing(scenes)
 for s in scenes:
  if s['kind'] in ['photo','archive','turntable','map','ident']:assert s['asset_id'] in assets,s
  for key,_,_ in s.get('sides',[]):assert key in assets,key
 chapters=[dict(start=pt[r['i']+1],title=re.sub(r'^\d\d:\d\d\s*—\s*','',r['text'])) for r in rows if r['heading']]
 project=dict(schema='arsenal.semantic-edit.v1',title='Ізраїль проти Ірану: військові арсенали',width=1920,height=1080,fps=30,duration=END,audio='audio/voice.mp3',audio_original_duration=duration,audio_policy='Original supplied recording, unchanged words and tempo',motion_policy=dict(photo_camera='locked',rotation_seconds_per_revolution=24,native_3d_fps=30,card_entrance='once then hold',maps='continuous genuine terrain-mesh camera animation'),scenes=scenes,chapters=chapters)
 (BASE/'episode.json').write_text(json.dumps(project,ensure_ascii=False,indent=2));mix={k:round(sum(s['duration'] for s in scenes if s['kind']==k),3) for k in set(s['kind'] for s in scenes)};report=dict(seconds_by_kind=mix,archive_share=mix.get('archive',0)/END,scenes_by_kind=dict(Counter(s['kind'] for s in scenes)),source_decisions=decisions,first_90_seconds_shots=sum(s['start']<90 for s in scenes),three_d_quality_policy='Only reviewed detailed aircraft/helicopter meshes; no schematic green tanks; real segmented equipment photos')
 (BASE/'media-mix.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));(BASE/'chapters.uk.txt').write_text('\n'.join(f"{int(c['start'])//60:02d}:{int(c['start'])%60:02d} {c['title']}" for c in chapters)+'\n');print('BUILT',len(scenes),END,report,flush=True)
if __name__=='__main__':main()
