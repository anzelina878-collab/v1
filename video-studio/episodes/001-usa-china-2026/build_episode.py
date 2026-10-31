"""Episode-specific visual edit; timings are taken from the supplied audio ASR.
No text/voice generation. Shared scene templates remain in studio/.
"""
from pathlib import Path
import copy,json,math,hashlib,re
ROOT=Path(__file__).resolve().parent
FPS=30
DURATION=1063.08
VIDEO_END=math.ceil(DURATION*FPS)/FPS
rows=[json.loads(x) for x in (ROOT/'alignment/transcript.jsonl').read_text().splitlines()]
words=[w for r in rows for w in r['words']]
assets={r['id']:r for fn in ['downloaded_manifest.json','additional_manifest.json'] for r in json.loads((ROOT/'assets'/fn).read_text())}
blocks=[]

def image(key):
 path='assets/prepared/'+key+'.png'
 if not (ROOT/path).is_file():raise ValueError('Missing prepared asset '+key)
 return path

def obj(key,country,title,**kw):
 sourcekey={'M157_DETAIL':'M7','MSV_CUT':'MSV','IFAK_CUT':'IFAK','XINGKONG_CUT':'XINGKONG'}.get(key,key)
 return {'type':'studio','image':image(key),'country':country,'title':title,'motion_kind':'verified_static','asset_id':sourcekey,'source':assets[sourcekey]['source_url'],**kw}

def photo(key,country,title):return obj(key,country,title,full_bleed=True)

def mesh(title='M4A1'):
 return {'type':'studio','video':'assets/m4a1-turntable.mp4','country':'US','title':title,'motion_kind':'true_3d','asset_id':'M4A1_3D','source':'https://opengameart.org/content/m4a1-assault-rifle','in':0,'fit':'contain'}

def comparison(title,a,b):
 ka,ca,ta=a;kb,cb,tb=b
 return {'type':'compare','title':title,'eyebrow':'','sides':[{'label':'США' if ca=='US' else 'КИТАЙ','title':ta,'image':image(ka),'detail':''},{'label':'США' if cb=='US' else 'КИТАЙ','title':tb,'image':image(kb),'detail':''}],'asset_ids':[ka,kb]}

def diagram(title,*nodes):
 return {'type':'diagram','title':title,'eyebrow':'','nodes':[{'title':t,'detail':''} for t in nodes],'asset_id':'ORIGINAL_DIAGRAM','motion_kind':'motion_graphics'}

def block(a,b,purpose,data,callouts=None):
 blocks.append({'start':a,'end':b,'purpose':purpose,'data':data,'callouts_absolute':callouts or []})

# Intro. Model names are deliberately omitted until their first spoken mention.
block(0,4.6,'Title and the comparison question',{'type':'intro','eyebrow':'','title':'США ПРОТИ КИТАЮ','subtitle':'Що носить солдат у 2026 році?'})
block(4.6,9.16,'Two approaches, no claim about specific models',comparison('ДВА ПІДХОДИ',('M4A1','US',''),('QBZ191','CN','')))
block(9.16,16.52,'Contemporary US training context, not presented as Iraq/Afghanistan footage',photo('US_TRAINING','US','НАВЧАННЯ · США'))
block(16.52,24.32,'Chinese infantry training context; archival year shown',photo('CHINA_TRAINING','CN','НАВЧАННЯ · 2021'))
block(24.32,29.78,'Examples of the named equipment categories, not an exhaustive standard kit',{'type':'kit','title':'СПОРЯДЖЕННЯ','eyebrow':'','items':[{'label':'ЗБРОЯ','image':image('M4A1')},{'label':'ЗАХИСТ','image':image('MSV_CUT')},{'label':'ШОЛОМ','image':image('IHPS')}],'asset_ids':['M4A1','MSV','IHPS']})
block(29.78,34.88,'Visual comparison of details without announcing future model names',comparison('РІЗНИЦЯ В ДЕТАЛЯХ',('M7','US',''),('QBZ191','CN','')))
block(34.88,40.58,'The breadth of the forthcoming equipment comparison',mesh('ОСОБИСТА ЗБРОЯ'))
block(40.58,42.16,'Night vision mentioned in the introduction',photo('ENVGB','US','НІЧНЕ БАЧЕННЯ'))
block(42.16,43.82,'Small drone mentioned in the introduction',photo('BLACKHORNET','US','БЕЗПІЛОТНИК'))
block(43.82,44.88,'Field food mentioned in the introduction',obj('MRE','US','ХАРЧУВАННЯ'))
block(44.88,51.02,'The film asks about systems rather than declaring a winner',diagram('ЩО ВІДРІЗНЯЄ?','СПОРЯДЖЕННЯ','СИСТЕМА'))
# Rifle. The named shots begin at the actual word onset, not the script time hints.
block(51.02,56.26,'Rifle chapter opening',{'type':'section','eyebrow':'','title':'ОСОБИСТА ЗБРОЯ','subtitle':''})
block(56.26,61.16,'Rifle context before the first model-name word',mesh('КАРАБІН'))
block(61.16,68.18,'Verified M4A1 geometry and spoken 5.56 caliber',mesh(),[(65.48,67.7,'5,56 ММ')])
block(68.18,72.30,'The optic and accessories on the official M4 photograph',obj('M4A1','US','M4A1'))
block(72.30,80.12,'M4A1 history; real geometric turntable',mesh())
block(80.12,86.70,'The end of the old-generation context before M7 is named',obj('M4A1','US','M4A1'))
block(86.70,93.26,'M7 and its spoken new caliber',obj('M7','US','M7'),[(90.84,93.2,'6,8 ММ')])
block(93.26,99.64,'M7 in a real US training photograph, not a penetration test',photo('US_TRAINING','US','M7 · НАВЧАННЯ'))
block(99.64,105.84,'M7 weight and capacity trade-off',obj('M7','US','M7'))
block(105.84,107.30,'M7 magazine capacity at the spoken number',obj('M7','US','M7'),[(105.84,107.3,'20 НАБОЇВ')])
block(107.30,110.02,'M4 capacity at the corresponding spoken number',obj('M4A1','US','M4A1'),[(107.3,110.02,'30 НАБОЇВ')])
block(110.02,117.40,'Shorter variant context; do not announce M8 before it is spoken',obj('M7','US','НОВА ПЛАТФОРМА'))
block(117.40,118.88,'Actual new M8 image; not the unrelated HK XM8',obj('M8','US','M8'))
block(118.88,123.56,'Chinese rifle introduction before the name',photo('CHINA_QBZ','CN','КИТАЙ'))
block(123.56,128.40,'QBZ-95 identity and form',obj('QBZ95','CN','QBZ-95'))
block(128.40,134.20,'The magazine behind the grip visible in the real photo',obj('QBZ95','CN','QBZ-95'),[(132.96,134.2,'БУЛПАП')])
block(134.20,139.56,'Bullpup packaging, no invented dimensions',obj('QBZ95','CN','QBZ-95'))
block(139.56,145.88,'Change of platform, without prematurely naming its successor',obj('QBZ95','CN','ЗМІНА ПЛАТФОРМИ'))
block(145.88,154.70,'Actual QBZ-191 photo',obj('QBZ191','CN','QBZ-191'))
block(154.70,160.28,'China retains its 5.8 mm cartridge',obj('QBZ191','CN','QBZ-191'),[(157.74,160.28,'5,8 ММ')])
block(160.28,177.35,'The two approaches compared; no scaled size claim',comparison('РІЗНІ ПІДХОДИ',('M7','US','M7'),('QBZ191','CN','QBZ-191')))
# Optics.
block(177.35,181.78,'Optics chapter transition',{'type':'section','eyebrow':'','title':'ПРИЦІЛИ','subtitle':''})
block(181.78,187.86,'Optic on the established American platform',obj('M4A1','US','ОПТИКА'))
block(187.86,203.59,'M157 detail cropped from the official M7 photograph',obj('M157_DETAIL','US','M157'),[(193.66,196.86,'ДАЛЕКОМІР · ДАТЧИКИ')])
block(203.59,211.01,'Electronic capabilities have practical support needs',diagram('ЕЛЕКТРОНІКА','МАСА','ЖИВЛЕННЯ','НАВЧАННЯ'))
block(211.01,224.53,'A verified Chinese training photo with an optic; no universal issue claim',photo('CHINA_QBZ','CN','ОПТИКА · НАВЧАННЯ'))
block(224.53,238.63,'A photographed system is not proof of distribution',diagram('НЕ ОДНЕ Й ТЕ САМЕ','НАЯВНІСТЬ','ПОШИРЕННЯ'))
block(238.63,248.17,'Technical comparison without fabricated availability figures',comparison('ТЕХНОЛОГІЇ ТА ОСНАЩЕННЯ',('M7','US','США'),('QBZ191','CN','КИТАЙ')))
# Launchers.
block(248.17,256.75,'Grenade launcher chapter; model name held until the spoken onset',obj('M320','US','ГРАНАТОМЕТ'))
block(256.75,264.21,'M320 and the already mentioned caliber',obj('M320','US','M320'))
block(264.21,269.25,'Chinese category shown as a caliber comparison, not a mislabeled M320',diagram('РІЗНІ КАЛІБРИ','США · 40 ММ','КИТАЙ · 35 ММ'))
block(269.25,287.01,'Program complexity is not the same as mass adoption',diagram('ВІД ІДЕЇ ДО СЛУЖБИ','РОЗРОБКА','ВИПРОБУВАННЯ','ПОШИРЕННЯ'))
# Machine guns.
block(287.01,297.33,'Squad automatic-fire role before M249 is named',obj('M249','US','КУЛЕМЕТ'))
block(297.33,307.59,'The actual M249 and its feed/caliber',obj('M249','US','M249'),[(301.15,303.3,'5,56 ММ')])
block(307.59,316.71,'M250 is not substituted with M249',obj('M250','US','M250'),[(312.99,316.2,'6,8 ММ')])
block(316.71,323.63,'The shared US modernization program',comparison('НОВЕ ПОКОЛІННЯ',('M7','US','M7'),('M250','US','M250')))
block(323.63,328.21,'Chinese automatic-fire platform context',obj('QBB95','CN','КУЛЕМЕТ'))
block(328.21,336.65,'Correct QBB-95 photo with drum magazine',obj('QBB95','CN','QBB-95'))
block(336.65,341.59,'No licensed verified QJS-161 picture found: a clearly typographic feed concept, not a fake weapon',diagram('QJS-161','СТРІЧКОВЕ','ЖИВЛЕННЯ'))
block(341.59,357.53,'Effectiveness depends on a system, not isolated headline figures',diagram('ЕФЕКТИВНІСТЬ','НАДІЙНІСТЬ','ПІДГОТОВКА','ВЗАЄМОДІЯ'))
# Pistols.
block(357.53,369.33,'The limited role of the sidearm',obj('M17','US','ПІСТОЛЕТ'))
block(369.33,373.49,'US sidearm context before the spoken model name',obj('M17','US','ПІСТОЛЕТ'))
block(373.49,380.61,'Actual M17, not the shorter M18',obj('M17','US','M17'))
block(380.61,382.59,'Beretta M9 at its spoken mention',obj('M9','US','BERETTA M9'))
block(382.59,385.73,'Chinese sidearm context',obj('QSZ92','CN','ПІСТОЛЕТ'))
block(385.73,391.69,'QSZ-92',obj('QSZ92','CN','QSZ-92'))
block(391.69,394.63,'QSZ-193',obj('QSZ193','CN','QSZ-193'))
block(394.63,405.85,'Sidearm comparison without changing its importance',comparison('ДОПОМІЖНА ЗБРОЯ',('M17','US','M17'),('QSZ193','CN','QSZ-193')))
# Marksman.
block(405.85,416.03,'The marksman role, not a tactical firing tutorial',photo('M110A1','US','МАРКСМАН'))
block(416.03,419.27,'The US marksman before the model-name word',photo('M110A1','US','МАРКСМАНСЬКА ГВИНТІВКА'))
block(419.27,426.29,'Real M110A1 photograph, no HK417 substitution',photo('M110A1','US','M110A1'))
block(426.29,429.23,'Chinese marksman context',obj('QBU88','CN','МАРКСМАНСЬКА ГВИНТІВКА'))
block(429.23,435.81,'QBU-88',obj('QBU88','CN','QBU-88'))
block(435.81,438.47,'QBU-191 begins at the spoken QBU syllable',obj('QBU191','CN','QBU-191'))
block(438.47,454.27,'Family resemblance shown with the correctly identified two Chinese platforms',comparison('СПОРІДНЕНІ ПЛАТФОРМИ',('QBZ191','CN','QBZ-191'),('QBU191','CN','QBU-191')))
# Anti-armor.
block(454.27,464.95,'The category of portable anti-armor systems',{'type':'section','eyebrow':'','title':'ПРОТИТАНКОВІ СИСТЕМИ','subtitle':''})
block(464.95,471.75,'Javelin object photo',obj('JAVELIN','US','JAVELIN'))
block(471.75,477.31,'Carl Gustaf object photo',obj('CARLGUSTAF','US','CARL GUSTAF'))
block(477.31,481.29,'Chinese systems context, no name early',obj('HJ12','CN','ПРОТИТАНКОВА СИСТЕМА'))
block(481.29,487.99,'HJ-12 and its shared general role',obj('HJ12','CN','HJ-12'))
block(487.99,504.01,'No unsupported range or penetration numbers',diagram('ВАЖЛИВІ УМОВИ','ЗАЯВЛЕНЕ','ПЕРЕВІРЕНЕ'))
block(504.01,512.89,'Both armies include this class of system',comparison('СПІЛЬНЕ ПРИЗНАЧЕННЯ',('JAVELIN','US','JAVELIN'),('HJ12','CN','HJ-12')))
# Protection.
block(512.89,519.47,'Protection chapter',{'type':'section','eyebrow':'','title':'ЗАХИСТ СОЛДАТА','subtitle':''})
block(519.47,524.61,'Ballistic helmet context',obj('IHPS','US','ШОЛОМ'))
block(524.61,540.25,'Verified IHPS photo, then an attachment concept rather than invented numerical protection',obj('IHPS','US','IHPS'))
block(540.25,548.87,'Chinese helmet actually visible in the training photograph',photo('CHINA_TRAINING','CN','ШОЛОМ · НАВЧАННЯ'))
block(548.87,563.59,'An actual modular US vest with plates/pouches',obj('MSV_CUT','US','МОДУЛЬНИЙ ЗАХИСТ'))
block(563.59,568.93,'Chinese protection photographed in the field, no exact vest model invented',photo('CHINA_TRAINING','CN','ІНДИВІДУАЛЬНИЙ ЗАХИСТ'))
block(568.93,585.09,'Protection must work with the rest of the equipment',diagram('ЄДИНА СИСТЕМА','ЗАХИСТ','ЗВ’ЯЗОК','СПОРЯДЖЕННЯ'))
block(585.09,596.55,'The script explicitly rejects judging protection by appearance',obj('MSV_CUT','US','МАТЕРІАЛИ Й КОНФІГУРАЦІЯ'))
# Weight. No fabricated mass breakdown.
block(596.55,607.13,'The named equipment accumulates',{'type':'kit','title':'УСЕ ЦЕ ПОТРІБНО НЕСТИ','eyebrow':'','items':[{'label':'ЗБРОЯ','image':image('M4A1')},{'label':'ЗАХИСТ','image':image('MSV_CUT')},{'label':'АПТЕЧКА','image':image('IFAK_CUT')}],'asset_ids':['M4A1','MSV','IFAK']})
block(607.13,623.47,'The total load is qualitative; no invented kilograms',diagram('ЗАГАЛЬНЕ НАВАНТАЖЕННЯ','ЗАХИСТ','ОБЛАДНАННЯ','ЗАПАСИ'))
block(623.47,628.85,'US modular carriage',obj('MSV_CUT','US','РОЗМІЩЕННЯ СПОРЯДЖЕННЯ'))
block(628.85,635.11,'Chinese vest and pouches actually visible in the training image',photo('CHINA_TRAINING','CN','РОЗМІЩЕННЯ СПОРЯДЖЕННЯ'))
block(635.11,646.11,'Mobility trade-off',diagram('КОМПРОМІС','РУХЛИВІСТЬ','ЗАХИСТ'))
block(646.11,657.57,'Capability versus physical load',diagram('КОМПРОМІС','МОЖЛИВОСТІ','НАВАНТАЖЕННЯ'))
# Night vision.
block(657.57,667.59,'Night-vision context before naming ENVG-B',photo('ENVGB','US','НІЧНЕ БАЧЕННЯ'))
block(667.59,679.55,'Actual soldier with ENVG-B; no substituted civilian device',photo('ENVGB','US','ENVG-B'))
block(679.55,687.79,'Real product detail photographed at the military display',photo('NV','US','ENVG-B · ДЕТАЛІ'))
block(687.79,698.25,'Chinese technology category; no unsupported depiction of a specific NV model',diagram('НІЧНЕ СПОСТЕРЕЖЕННЯ','ПІДСИЛЕННЯ ЗОБРАЖЕННЯ','ТЕПЛОВІЗІЯ'))
block(698.25,714.17,'Availability is unknown: never invent a distribution percentage',diagram('МАСШТАБ ОСНАЩЕННЯ','ТЕХНОЛОГІЯ','ВІДКРИТІ ДАНІ'))
block(714.17,721.35,'What the public evidence can and cannot tell us',photo('ENVGB','US','ТЕХНОЛОГІЯ ≠ МАСОВІСТЬ'))
# Medical.
block(721.35,729.13,'The individual kit is named in the voice',obj('IFAK_CUT','US','ІНДИВІДУАЛЬНА АПТЕЧКА'))
block(729.13,743.61,'Actual photographed IFAK contents, no universal kit promise',obj('IFAK_CUT','US','АПТЕЧКА'))
block(743.61,750.25,'Chinese medical support discussed as a system, not a mislabeled US kit',diagram('МЕДИЧНЕ ЗАБЕЗПЕЧЕННЯ','КОМПЛЕКТ','ПІДГОТОВКА'))
block(750.25,766.63,'Medical outcomes depend on more than a pouch',diagram('ВАЖЛИВА ВСЯ СИСТЕМА','МАТЕРІАЛИ','НАВЧАННЯ','ДОПОМОГА'))
# Clothing.
block(766.63,786.03,'Climates mentioned in the narration, no made-up temperatures',diagram('РІЗНІ УМОВИ','ПУСТЕЛЯ','ГОРИ','ХОЛОД'))
block(786.03,789.51,'US clothing context before the pattern name',photo('OCP','US','КАМУФЛЯЖ'))
block(789.51,792.15,'Actual OCP swatch',photo('OCP','US','OCP'))
block(792.15,796.97,'The verified Type 19 blouse crop',obj('XINGKONG_CUT','CN','КАМУФЛЯЖ'))
block(796.97,808.03,'Xingkong at the spoken pattern-name onset',obj('XINGKONG_CUT','CN','XINGKONG'))
block(808.03,823.37,'Clothing must match environment, no universal winner',diagram('ВІДПОВІДНІСТЬ УМОВАМ','ХОЛОД','ВОЛОГА','СПЕКА'))
# Rations.
block(823.37,829.41,'Ration transition',{'type':'section','eyebrow':'','title':'ЇЖА В ПОЛЬОВИХ УМОВАХ','subtitle':''})
block(829.41,832.49,'Ration before its family name is spoken',obj('MRE','US','ПОЛЬОВИЙ РАЦІОН'))
block(832.49,835.57,'Actual MRE packages',obj('MRE','US','MRE'))
block(835.57,842.47,'Photographed MRE contents',obj('MRE2','US','СКЛАД РАЦІОНУ'))
block(842.47,853.83,'PLA ration overview; no single variant falsely asserted',obj('CHINA_RATION','CN','ПОЛЬОВІ РАЦІОНИ'))
block(853.83,861.17,'Heating is discussed without unsupported temperature numbers',obj('CHINA_RATION','CN','АВТОНОМНЕ ПІДІГРІВАННЯ'))
block(861.17,874.95,'The practical purpose of food and taste differences',comparison('ЕНЕРГІЯ В ПОЛЬОВИХ УМОВАХ',('MRE','US','MRE'),('CHINA_RATION','CN','ПОЛЬОВИЙ РАЦІОН')))
# Drones.
block(874.95,881.87,'Drones chapter transition',{'type':'section','eyebrow':'','title':'МАЛІ БЕЗПІЛОТНИКИ','subtitle':''})
block(881.87,890.17,'A small drone before its family name is spoken',photo('BLACKHORNET','US','МАЛИЙ БЕЗПІЛОТНИК'))
block(890.17,899.77,'The verified Black Hornet image; no invented size/performance',photo('BLACKHORNET','US','BLACK HORNET'))
block(899.77,908.51,'Chinese small-drone ecosystem rather than showing a US drone as Chinese',diagram('БЕЗПІЛОТНІ ТЕХНОЛОГІЇ','ВИРОБНИЦТВО','ЗАСТОСУВАННЯ'))
block(908.51,919.33,'The complete system around the airframe',diagram('НЕ ЛИШЕ АПАРАТ','ЗВ’ЯЗОК','ЖИВЛЕННЯ','ОПЕРАТОР'))
block(919.33,933.09,'Performance figures alone are insufficient',photo('BLACKHORNET','US','СИСТЕМА, А НЕ ЛИШЕ РОЗМІР'))
# Training.
block(933.09,946.93,'People matter more than a list of hardware',photo('US_TRAINING','US','ЛЮДИНА Й СПОРЯДЖЕННЯ'))
block(946.93,954.29,'US training, actual US training photograph',photo('US_TRAINING','US','ПІДГОТОВКА'))
block(954.29,961.45,'Chinese training, actual Chinese training photograph',photo('CHINA_TRAINING','CN','ПІДГОТОВКА · 2021'))
block(961.45,971.01,'No misleading week-count chart',diagram('ЯКІСТЬ ПІДГОТОВКИ','СПЕЦІАЛЬНІСТЬ','ПІДРОЗДІЛ'))
block(971.01,979.55,'The factors actually named by the narrator',diagram('НАВЧАННЯ ЯК СИСТЕМА','ІНСТРУКТОРИ','РЕГУЛЯРНІСТЬ','ВЗАЄМОДІЯ'))
# Conclusion.
block(979.55,993.75,'Return to the initial comparison, no new claims',comparison('СХОЖЕ СПОРЯДЖЕННЯ',('M7','US','M7'),('QBZ191','CN','QBZ-191')))
block(993.75,1005.13,'The US modernization approach',comparison('ОНОВЛЕННЯ СИСТЕМИ',('M7','US','M7'),('M250','US','M250')))
block(1005.13,1012.91,'Chinese generation transition',comparison('МОДЕРНІЗАЦІЯ',('QBZ95','CN','QBZ-95'),('QBZ191','CN','QBZ-191')))
block(1012.91,1021.09,'New model capabilities are not universal availability',diagram('НЕ ПЛУТАТИ','НОВИЙ ЗРАЗОК','ОСНАЩЕННЯ АРМІЇ'))
block(1021.09,1026.17,'A real optic photo does not establish universal issue',obj('M157_DETAIL','US','НАЯВНІСТЬ ≠ МАСОВІСТЬ'))
block(1026.17,1030.29,'Old models do not disappear immediately',mesh())
block(1030.29,1044.63,'Production, logistics and training are the concluding thesis',diagram('СПРАВЖНЯ РІЗНИЦЯ','ВИРОБНИЦТВО','ЛОГІСТИКА','ПІДГОТОВКА'))
block(1044.63,1052.69,'The actual audience question',diagram('ЩО ВАЖЛИВІШЕ?','ЗБРОЯ','ЗАХИСТ','ЕЛЕКТРОНІКА'))
block(1052.69,VIDEO_END,'The supplied closing call to comment/subscribe',{'type':'outro','eyebrow':'','title':'ВАША ДУМКА?','subtitle':'Зброя · захист · електроніка'})

# Audio-derived cut points: use segment/word boundaries, never proportional script timing.
scene_list=[]
for block_index,b in enumerate(blocks):
 if block_index and abs(b['start']-blocks[block_index-1]['end'])>.001:raise ValueError('Gap in visual edit')
 a,end=b['start'],b['end'];cuts=[a]
 while end-cuts[-1]>10:
  t=cuts[-1]
  candidates=[r['start'] for r in rows if t+3<=r['start']<=min(t+8,end-2)]
  if not candidates:candidates=[w['start'] for w in words if t+4<=w['start']<=min(t+7,end-2)]
  if not candidates:break
  cuts.append(candidates[-1])
 cuts.append(end)
 for j,(start,finish) in enumerate(zip(cuts,cuts[1:])):
  sf=round(start*FPS);ef=round(finish*FPS)
  if ef<=sf:continue
  scene=copy.deepcopy(b['data']);scene['id']=f'shot-{len(scene_list)+1:03d}'
  scene['start']=sf/FPS;scene['duration']=(ef-sf)/FPS
  scene['visual_purpose']=b['purpose']
  scene['narration_quote_asr']=''.join(w['word'] for w in words if start<=w['start']<finish).strip()
  scene['alignment_basis']='actual supplied audio word/segment timestamps'
  if scene['type']=='studio' and scene.get('_video'):scene.pop('_video',None)
  calls=[]
  for ca,cb,text in b['callouts_absolute']:
   ca=max(start,ca);cb=min(finish,cb)
   if cb>ca:calls.append({'start':max(0,ca-start),'end':min(scene['duration'],cb-start),'text':text})
  scene['callouts']=calls
  if scene.get('video'):
   # Each genuine turntable shot is shorter than its source, so no looping jump is introduced.
   scene['in']=min((start-b['start'])%3,max(0,10-scene['duration']))
  scene_list.append(scene)
for i,s in enumerate(scene_list):
 expected=scene_list[i-1]['start']+scene_list[i-1]['duration'] if i else 0
 if abs(s['start']-expected)>.0001:raise ValueError('Frame gap')
project={'version':1,'brand':'','title':'США проти Китаю: що носить солдат у 2026 році?','style':'minimal','width':1920,'height':1080,'fps':30,'audio':'audio/voice.mp3','audio_policy':'strict','footer':'','theme':{'font':'fonts/DejaVuSansCondensed.ttf','font_bold':'fonts/DejaVuSansCondensed-Bold.ttf','background':'#F2F3F0'},'scenes':scene_list}
# Fonts resolve from studio root; asset paths resolve from this episode.
(ROOT/'episode.json').write_text(json.dumps(project,ensure_ascii=False,indent=2))
hints=json.loads((ROOT/'timeline.draft.json').read_text())['chapters']
starts=[0,51.02,177.35,248.17,287.01,357.53,405.85,454.27,512.89,596.55,657.57,721.35,766.63,823.37,874.95,933.09,979.55,DURATION]
chapters=[{'id':h['id'],'title':h['title'],'start':starts[i],'end':starts[i+1],'script_time_hint':h['script_time_hint']} for i,h in enumerate(hints)]
(ROOT/'timeline.json').write_text(json.dumps({'status':'audio_aligned_visual_edit','duration_seconds':DURATION,'fps':FPS,'chapters':chapters,'scenes':scene_list,'source_script_sha256':hashlib.sha256((ROOT/'inputs/script.uk.txt').read_bytes()).hexdigest(),'audio_sha256':hashlib.sha256((ROOT/'audio/voice.mp3').read_bytes()).hexdigest()},ensure_ascii=False,indent=2))
# A genuine 90-second pilot, clipped only for technical review. Final keeps the entire input.
pilot=copy.deepcopy(project);pilot['audio']='alignment/pilot.wav';pilot_scenes=[]
for s in scene_list:
 if s['start']>=90:break
 s=copy.deepcopy(s);s['duration']=min(s['duration'],90-s['start'])
 s['callouts']=[dict(c,end=min(c['end'],s['duration'])) for c in s.get('callouts',[]) if c['start']<s['duration']]
 pilot_scenes.append(s)
pilot['scenes']=pilot_scenes
(ROOT/'pilot.json').write_text(json.dumps(pilot,ensure_ascii=False,indent=2))
print('EPISODE',len(scene_list),'shots',len(chapters),'chapters',scene_list[-1]['start']+scene_list[-1]['duration'],'seconds')
print('PILOT',len(pilot_scenes),'shots')
