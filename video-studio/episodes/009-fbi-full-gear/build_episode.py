"""Voice-aligned Ukrainian FBI edit. Assets are reviewed, not keyword selected."""
from pathlib import Path
import json,math,subprocess,hashlib
B=Path(__file__).resolve().parent;T=B/'inputs/research'
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
assets=json.load(open(T/'media-candidates.json'))
assets=[a for a in assets if not a.get('error')]
if (T/'extra-candidates.json').exists():assets += [a for a in json.load(open(T/'extra-candidates.json')) if not a.get('error')]
assets=[a for a in assets if (B/a.get('video',a.get('photo','missing'))).is_file()]
# Keep only assets that can actually be decoded; first-party footage is credited.
ids={a['id'] for a in assets}
for f in (B/'assets/video').glob('*.mp4'):
 if f.stem in ids or f.stat().st_size<1000:continue
 try:dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(f)]))
 except:continue
 key=f.stem;page=f'https://www.fbi.gov/video-repository/{key}/view'
 if (T/'firearms-source.json').exists() and key=='firearms-exhibit':a=json.load(open(T/'firearms-source.json'))
 else:a=dict(id=key,video='assets/video/'+f.name,duration=dur,source_url=page,credit='FBI · Public domain',license='17 USC 105 · first-party FBI production')
 if key=='operator-360':a.update(source_url='https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html',credit='3D: Adobe Mixamo · типове спорядження',license='Royalty-free rendered film. Raw model and derived geometry NOT redistributed.',motion_kind='true_3d',native_frames=720)
 if key=='digital-360':a.update(source_url='original:tools/build_digital_props.py',credit='АРСЕНАЛ 360° · оригінальна 3D-ілюстрація',license='Original project geometry; reusable',motion_kind='true_3d',native_frames=720)
 if key=='ar15-360':a.update(source_url='https://opengameart.org/content/m4a1-assault-rifle',credit='3D: nisu · CC0 · ілюстрація платформи AR-15',license='CC0',motion_kind='true_3d',native_frames=720)
 if key=='range-training':a.update(source_url='https://www.fbi.gov/video-repository/becoming-an-agent-series-firearms-training.mp4/view')
 assets.append(a);ids.add(key)
# Use official stills, never portraits as generic operators.
for f in (B/'assets/photos').glob('*'):
 if f.stem in ids:continue
 if any(z in f.stem for z in ['grogan','dove']):continue
 assets.append(dict(id=f.stem,photo='assets/photos/'+f.name,source_url='https://www.fbi.gov/image-repository/'+f.stem,credit='FBI · Public domain',license='17 USC 105 · first-party FBI photograph'));ids.add(f.stem)
for a in assets:
 a.setdefault('license','17 USC 105 · first-party FBI photograph')
 if 'video' in a:a['duration']=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(B/a['video'])]))

for a in assets:
 if a['id']=='fbi-glock-exhibit':a.update(source_url='https://www.fbi.gov/video-repository/fbi-experience-brief-firearms-john-fox-081525.mp4/view',credit='FBI · кадр експозиції, 2025 · Public domain',license='17 USC 105',original_video_time=50)

if (T/'dna-photos-source.json').exists():
 dna={a['id']:a for a in json.load(open(T/'dna-photos-source.json'))}
 assets=[dna.get(a['id'],a) for a in assets]
lookup={a['id']:a for a in assets}
scenes=[];cursor=0

def add(end,kind,title='',asset=None,source=0,nodes=None,note=''):
 global cursor
 start=round(cursor*30)/30;end=round(end*30)/30
 assert end>start,(start,end)
 s=dict(id=f'uk009-{len(scenes):03}',start=start,end=end,duration=(round(end*30)-round(start*30))/30,kind=kind,title=title,country='US',entrance_once=True,settle_after=.8,note=note,camera_motion=False)
 if asset:
  assert asset in lookup,(asset,title)
  s.update(asset_id=asset,source_in=source)
  if kind=='archive':assert source+s['duration']<=lookup[asset]['duration']+.02,(asset,source,s['duration'],lookup[asset]['duration'])
 if nodes:s['nodes']=nodes
 scenes.append(s);cursor=end

def A(e,key,title,src):add(e,'archive',title,key,src)
def P(e,key,title,note=''):add(e,'photo',title,key,note=note)
def R(e,key='operator-360',title='СПОРЯДЖЕННЯ СПЕЦПІДРОЗДІЛУ',src=0):add(e,'turntable',title,key,src,note='Типовий комплект · 3D-ілюстрація')
def G(e,title,*nodes):add(e,'graphic',title,nodes=list(nodes))
def H(cue,title):
 # Fully revealed by the first narrated phrase; one entrance, then a stable hold.
 assert abs(cursor-(cue-.8))<.04,(cursor,cue)
 add(cue+2.8,'section',title)
chapters=[(0,'ВСТУП'),(68.94,'СПОРЯДЖЕННЯ АГЕНТА'),(130.38,'ПІСТОЛЕТИ ФБР'),(201.8,'ПЕРЕСТРІЛКА В МАЯМІ'),(264.58,'ДОВГОСТВОЛЬНА ЗБРОЯ'),(336.26,'БРОНЕЗАХИСТ'),(402.36,'SWAT ФБР'),(474.78,'СПЕЦПІДРОЗДІЛ HRT'),(548.54,'ТРАНСПОРТ ФБР'),(620.14,'ВИБУХОТЕХНІКИ'),(687.22,'КРИМІНАЛІСТИ'),(755.39,'ЛАБОРАТОРІЯ ФБР'),(815.33,'ЦИФРОВІ ДОКАЗИ'),(889.39,'ПІДГОТОВКА В КВАНТІКО'),(958.01,'АРСЕНАЛ ФБР'),(1001.65,'ВАША ДУМКА')]
# Opening: three distinct roles, then a fast, relevant equipment montage.
R(3.07,title='ФБР · ТРИ РІЗНІ РОЛІ',src=0)
A(9.73,'field-training','АГЕНТИ ФБР · НАВЧАННЯ',4.2)
A(16.43,'ert2021','КРИМІНАЛІСТИ · ERT',29)
R(22.3,src=6)
G(27.6,'FBI','АГЕНТ','КРИМІНАЛІСТ','СПЕЦПІДРОЗДІЛ')
A(33.73,'field-training','РОБОТА КОМАНДИ · НАВЧАННЯ',42)
A(38.4,'firearms-exhibit','СЛУЖБОВИЙ ПІСТОЛЕТ · ЕКСПОЗИЦІЯ ФБР',49)
R(42.47,'ar15-360','ПЛАТФОРМА AR-15',3)
A(48.37,'hrt2013','HRT · ТРЕНУВАННЯ',52)
A(52.1,'bombtraining2025','ВИБУХОТЕХНІЧНИЙ РОБОТ',1)
A(55.3,'hrt-water','СПІЛЬНІ НАВЧАННЯ HRT',11.5)
R(60.27,title='ВІД АГЕНТА ДО СПЕЦПІДРОЗДІЛУ',src=12)
A(64.47,'ert2021','ФІКСАЦІЯ ДОКАЗІВ · НАВЧАННЯ',91.5)
add(68.14,'ident');H(68.94,'СПОРЯДЖЕННЯ АГЕНТА')
A(76.0,'classroom','АГЕНТИ ТА АНАЛІТИКИ · КВАНТІКО',2)
G(82.3,'РІЗНІ ЗАВДАННЯ — РІЗНЕ СПОРЯДЖЕННЯ','РОЗСЛІДУВАННЯ','ТАКТИЧНІ ОПЕРАЦІЇ','КРИМІНАЛІСТИКА')
A(90.0,'field-training','БАЗОВА ПІДГОТОВКА АГЕНТІВ',110)
G(97.1,'БАЗОВИЙ КОМПЛЕКТ','ПОСВІДЧЕННЯ','ПІСТОЛЕТ','ЗВ’ЯЗОК')
P(104.5,'stolen-wfo-motorola-radio-apx-7000-jpg','MOTOROLA APX-7000','Документований приклад · ФБР, 2016')
A(113.4,'field-training','ЗВИЧАЙНИЙ ОДЯГ · НАВЧАЛЬНА ОПЕРАЦІЯ',134)
R(122.1,title='ЗАХИСТ ДЛЯ КОНКРЕТНОГО ЗАВДАННЯ',src=17)
G(129.58,'КОМПЛЕКТ ВИЗНАЧАЄ ЗАВДАННЯ','БЕЗПЕКА','МОБІЛЬНІСТЬ','ПІДГОТОВКА');H(130.38,'ПІСТОЛЕТИ ФБР')
P(139.7,'fbi-glock-exhibit','СЛУЖБОВИЙ ПІСТОЛЕТ · ЕКСПОЗИЦІЯ ФБР')
G(151.13,'GLOCK 19M / GLOCK 17M','9 ММ','ДОКУМЕНТ ФБР · 2021')
P(159.97,'fbi-glock-exhibit','GLOCK · ЕКСПОЗИЦІЯ ФБР','Службова конфігурація на виставці · 2025')
A(171.2,'range-training','ВОГНЕВА ПІДГОТОВКА АГЕНТІВ',29)
G(182.37,'СЛУЖБОВИЙ ПІСТОЛЕТ','КОНТРОЛЬ','НАДІЙНІСТЬ','РЕГУЛЯРНІ ТРЕНУВАННЯ')
P(191.8,'fbi-glock-exhibit','КОЛІМАТОР І ЛІХТАР','Експонат ФБР · не універсальна комплектація')
R(201.0,title='ІНДИВІДУАЛЬНИЙ КОМПЛЕКТ СПОРЯДЖЕННЯ',src=7);H(201.8,'ПЕРЕСТРІЛКА В МАЯМІ')
G(212.07,'11 КВІТНЯ 1986','МАЯМІ','ПЕРЕСТРІЛКА ФБР')
P(223.07,'wall-of-honor','БЕН ГРОГАН І ДЖЕРРІ ДАВ','Агенти, які загинули в Маямі · 1986')
R(233.7,title='ОЗБРОЄННЯ · ЗАХИСТ · ПІДГОТОВКА',src=0)
A(245.03,'range-training','ВОГНЕВА ПІДГОТОВКА · КВАНТІКО',3)
R(254.9,title='СПОРЯДЖЕННЯ ПРАЦЮЄ ЯК СИСТЕМА',src=3)
G(263.78,'БЕЗПЕКА — ЦЕ СИСТЕМА','ЗАХИСТ','ЗВ’ЯЗОК','НАВИЧКИ');H(264.58,'ДОВГОСТВОЛЬНА ЗБРОЯ')
R(276.8,'ar15-360','КАРАБІН ПЛАТФОРМИ AR-15',0)
P(288.6,'stolen-wfo-rock-river-arms-rifle-jpg','ROCK RIVER ARMS LAR-15','Офіційна публікація ФБР · 2016')
A(300.87,'range-training','КАРАБІНИ · НАВЧАЛЬНІ СТРІЛЬБИ',88)
P(306.47,'stolen-wfo-gun-lock-box-jpg','АВТОМОБІЛЬНИЙ СЕЙФ','Документований приклад · ФБР, 2016')
G(316.0,'HECKLER & KOCH MP5','10 ММ','ІСТОРИЧНО ДОКУМЕНТОВАНО · 2017')
R(325.0,'ar15-360','ПЛАТФОРМА AR-15 · 3D-ІЛЮСТРАЦІЯ',12)
G(335.46,'ЗБРОЯ ЗАЛЕЖИТЬ ВІД ОПЕРАЦІЇ','СЕРЕДОВИЩЕ','ЗАВДАННЯ','ПІДГОТОВКА');H(336.26,'БРОНЕЗАХИСТ')
R(349.2,title='БРОНЕЖИЛЕТ І РОЗВАНТАЖЕННЯ',src=0)
G(360.7,'РІЗНІ ЗАГРОЗИ — РІЗНИЙ ЗАХИСТ','М’ЯКА БРОНЯ','ЖОРСТКІ ПЛИТИ')
P(369.9,'swat-operator-female-png','СПОРЯДЖЕННЯ SWAT ФБР','Реальна фотографія ФБР')
R(381.8,title='ШОЛОМ · ЗАХИСТ · ЗВ’ЯЗОК',src=11)
G(391.1,'ЗАХИСТ МАЄ ОБМЕЖЕННЯ','КЛАС І МОДЕЛЬ','МАСА','РУХЛИВІСТЬ')
A(401.56,'field-training','ПЕРЕСУВАННЯ В ЗАХИСТІ · НАВЧАННЯ',50);H(402.36,'SWAT ФБР')
P(415.9,'swat-pr-training-2021-jpg','SWAT ФБР · НАВЧАННЯ','Пуерто-Рико · 2021')
R(429.3,title='ТАКТИЧНИЙ КОМПЛЕКТ SWAT',src=5)
G(441.8,'СПЕЦІАЛЬНЕ СПОРЯДЖЕННЯ','ЗАХИСНІ ЩИТИ','ЗВ’ЯЗОК','СПОСТЕРЕЖЕННЯ')
A(449.1,'fbi-expo','НІЧНЕ СПОРЯДЖЕННЯ ФБР · ДЕМОНСТРАЦІЯ',.1)
P(463.1,'swat-operator-hands-doors-blur-jpg','SWAT · КОМАНДНА РОБОТА')
P(473.98,'swat-weapon-la-png','SWAT ФБР · СПОРЯДЖЕННЯ ГРУПИ');H(474.78,'СПЕЦПІДРОЗДІЛ HRT')
G(491.5,'HRT · СТВОРЕНО 1983 РОКУ','HOSTAGE RESCUE TEAM','ЗВІЛЬНЕННЯ ЗАРУЧНИКІВ')
A(501.87,'hrt-water','HRT · ВОДНО-РЯТУВАЛЬНА ПІДГОТОВКА',36)
R(515.5,title='HRT · ІЛЮСТРАЦІЯ СПОРЯДЖЕННЯ',src=15)
P(526.0,'hrt-training-fast-rope-080519','HRT · ВИСАДКА З ГЕЛІКОПТЕРА')
A(538.5,'hrt-water','HRT · ВОДНО-РЯТУВАЛЬНІ НАВЧАННЯ',54)
G(547.74,'МОБІЛЬНІСТЬ HRT','СУХОДІЛ','ВОДА','ПОВІТРЯ');H(548.54,'ТРАНСПОРТ ФБР')
A(563.0,'field-training','СЛУЖБОВІ АВТОМОБІЛІ · НАВЧАННЯ',137)
P(576.9,'swat-operator-truck-blur-jpg','БРОНЬОВАНИЙ ТРАНСПОРТ SWAT')
A(588.4,'hrt-water','HRT · ГЕЛІКОПТЕР І КАТЕР',7.5)
P(599.6,'zodiac-surf-jump','HRT · ШВИДКІСНІ ЧОВНИ')
P(608.4,'hrt-mobility-team-diver','HRT · ВОДОЛАЗНА ПІДГОТОВКА')
G(619.34,'ТРАНСПОРТ ПІД ЗАВДАННЯ','ЗАХИСТ ЛЮДЕЙ','ДОСТАВКА ГРУПИ','ЕВАКУАЦІЯ');H(620.14,'ВИБУХОТЕХНІКИ')
A(633.97,'bombtraining2025','РОБОТ · КАМЕРА І МАНІПУЛЯТОР',30)
A(641.5,'hds2018','ДИСТАНЦІЙНИЙ ОГЛЯД · HDS',33)
A(649.9,'bombtraining2025','РЕНТГЕНІВСЬКИЙ КОНТРОЛЬ · НАВЧАННЯ',44)
A(656.5,'bombsuit2025','ЗАХИСНИЙ КОСТЮМ ВИБУХОТЕХНІКА',18)
G(669.6,'HAZARDOUS DEVICES SCHOOL','ГАНТСВІЛЛ','ПРАЦЮЄ З 1971 РОКУ')
A(678.9,'hds2018','HDS · ТРЕНУВАННЯ ВИБУХОТЕХНІКІВ',50)
A(686.42,'hds2018','ПРАКТИЧНА ПІДГОТОВКА ВИБУХОТЕХНІКІВ',96);H(687.22,'КРИМІНАЛІСТИ')
A(704.87,'ert2021','ERT · ФІКСАЦІЯ МІСЦЯ ПОДІЇ',36)
G(715.43,'КОМПЛЕКТ КРИМІНАЛІСТА','ФОТОКАМЕРА','МАРКЕРИ','ПАКУВАННЯ')
A(728.03,'ert2021','МАРКУВАННЯ ТА ПАКУВАННЯ · НАВЧАННЯ',88)
G(739.0,'ЛАНЦЮГ ЗБЕРЕЖЕННЯ ДОКАЗІВ','ВИЯВЛЕННЯ','ФІКСАЦІЯ','ПЕРЕДАЧА')
A(747.7,'ert2021','КРИМІНАЛІСТИ · НАВЧАЛЬНИЙ МАЙДАНЧИК',125)
A(754.59,'ert2021','МАРКУВАННЯ ДОКАЗІВ · НАВЧАННЯ',140);H(755.39,'ЛАБОРАТОРІЯ ФБР')
G(765.0,'ЛАБОРАТОРІЯ ФБР','ЗАСНОВАНА 1932 РОКУ','НАУКОВА ЕКСПЕРТИЗА')
P(776.0,'dna-lab-1','ЗРАЗОК ДЛЯ ДНК-АНАЛІЗУ','Приклад із публікації ФБР · 2026')
A(786.4,'lab-scenes','ЛАБОРАТОРІЯ · 3D-РЕКОНСТРУКЦІЯ МІСЦЬ ПОДІЙ',13)
P(796.3,'dna-lab-2','ЛАБОРАТОРНЕ ОБЛАДНАННЯ ФБР','Федеральний підрозділ бази ДНК · 2026')
A(805.8,'lab-scenes','ЛАБОРАТОРІЯ · ПРОСТОРОВЕ МОДЕЛЮВАННЯ',87)
P(814.53,'dna-lab-3','ДОСЛІДЖЕННЯ ЗРАЗКІВ','Реальна лабораторія ФБР · 2026');H(815.33,'ЦИФРОВІ ДОКАЗИ')
R(828.5,'digital-360','НОСІЇ ЦИФРОВИХ ДОКАЗІВ',0)
G(838.5,'ЗБЕРЕГТИ ОРИГІНАЛ','ВИЛУЧЕННЯ','ДОКУМЕНТУВАННЯ','КОПІЯ ДЛЯ АНАЛІЗУ')
G(849.5,'БЛОКУВАЛЬНИК ЗАПИСУ','ЗАХИСТ ВІД ЗМІН','КОНТРОЛЬ ЦІЛІСНОСТІ')
R(860.8,'digital-360','ДАНІ · ШИФРУВАННЯ · ТЕХНІЧНІ МЕЖІ',12)
G(873.7,'CODIS','ПОРІВНЯННЯ ДНК-ПРОФІЛІВ','НАПРЯМОК ДЛЯ ПЕРЕВІРКИ')
G(888.59,'ЗБІГ — ПРИВІД ДЛЯ ПЕРЕВІРКИ','ДОДАТКОВІ ДОКАЗИ','КОНТЕКСТ','ПЕРЕВІРКА');H(889.39,'ПІДГОТОВКА В КВАНТІКО')
G(905.1,'БАЗОВА ПІДГОТОВКА','ПРИБЛИЗНО 18 ТИЖНІВ','АКАДЕМІЯ ФБР · КВАНТІКО')
A(919.43,'classroom','НАВЧАННЯ АГЕНТІВ І АНАЛІТИКІВ',116.5)
P(929.67,'hogans-alley-corner','HOGAN’S ALLEY','Навчальне містечко ФБР')
G(938.7,'HOGAN’S ALLEY','ПРАЦЮЄ З 1987 РОКУ','НАВЧАЛЬНІ СИТУАЦІЇ')
A(948.4,'field-training','HOGAN’S ALLEY · НАВЧАЛЬНА ОПЕРАЦІЯ',24)
R(957.21,title='ГОЛОВНИЙ ІНСТРУМЕНТ — ПІДГОТОВЛЕНА ЛЮДИНА',src=8);H(958.01,'АРСЕНАЛ ФБР')
A(969.4,'range-training','ЗБРОЯ ТА ПІДГОТОВКА',100)
R(980.0,title='ЗАХИСТ · ЗВ’ЯЗОК · КОМАНДА',src=14)
A(989.5,'bombtraining2025','ТЕХНІКА ДЛЯ ЗБЕРЕЖЕННЯ ЖИТТЯ',54)
A(1000.83,'ert2021','ДОКАЗИ ТА КРИМІНАЛІСТИКА',51)
add(1019.6,'question','ЩО ВАС ЗДИВУВАЛО НАЙБІЛЬШЕ?',nodes=['ЗБРОЯ ТА ЗАХИСТ','СПЕЦПІДРОЗДІЛИ','КРИМІНАЛІСТИКА'])
R(1024.07,title='НАПИШІТЬ СВОЮ ДУМКУ В КОМЕНТАРЯХ',src=3)
# Final invitation enters once, then brand remains through the final spoken line.
add(1033.37,'section','ПІДПИШІТЬСЯ НА КАНАЛ')
add(math.ceil(1039.224*30)/30,'ident')
project=dict(schema='arsenal.uk-fbi-009.v1',title='ФБР: повне спорядження агентів і спецпідрозділів',language='uk',brand='АРСЕНАЛ 360°',width=1920,height=1080,fps=30,duration=cursor,audio='audio/voiceover.mp3',scenes=scenes,chapters=[dict(cue=t,title=v) for t,v in chapters])
# Only selected assets enter portable sources. Raw licensed operator geometry is excluded.
selected={s['asset_id'] for s in scenes if 'asset_id' in s};write(B/'assets/manifest.json',[lookup[k] for k in sorted(selected)]);write(B/'episode.json',project)
write(B/'visual-plan.json',dict(scene_count=len(scenes),ai_video_seconds=0,ai_photo_seconds=0,voice_unchanged=True,scene_alignment='Hand-edited to actual word-timed Ukrainian narration',scenes=scenes))
(B/'chapters.uk.txt').write_text('\n'.join(f'{int(t)//60:02}:{int(t)%60:02} {v}' for t,v in chapters)+'\n')
print('READY',len(scenes),cursor)
