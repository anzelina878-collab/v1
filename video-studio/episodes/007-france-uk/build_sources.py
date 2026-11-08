"""Write full attribution and integrity evidence for the selected episode assets."""
import json,hashlib
from pathlib import Path
from build_episode import FALLBACK
BASE=Path(__file__).resolve().parent

def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1048576):h.update(b)
 return h.hexdigest()
def main():
 project=json.loads((BASE/'episode.json').read_text());all={a['id']:a for a in json.loads((BASE/'assets/manifest.json').read_text())};keys={'fr-flag','gb-flag'}
 for s in project['scenes']:
  if s['kind'] in ['photo','archive','turntable','map','ident']:keys.add(s['asset_id'])
  for key,_,_ in s.get('sides',[]):keys.add(key)
  if s['kind']=='archive':keys.add(FALLBACK[s['asset_id']])
 assets=[all[key] for key in sorted(keys)];(BASE/'assets/manifest.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2))
 lines=['# Джерела випуску 007 — Франція проти Великої Британії','','Прапор позначає країну порівняння. Підписи «родина»/«тип» означають сімейство техніки, не конкретну національну модифікацію. Інший оператор, виставковий зразок, навчання чи випробування названі окремо. Навчання не видаються за бойову зйомку.','','Карти створені в цьому проєкті зі справжньої сітки висот. Natural Earth NE2 1:50m та кордони — public domain: https://www.naturalearthdata.com/about/terms-of-use/ . Terrarium: https://registry.opendata.aws/terrain-tiles/ ; Mapzen/NASA/USGS/NOAA, атрибуції https://github.com/tilezen/joerd/blob/master/docs/attribution.md . Висоти перебільшені у 20 разів. Атрибуції карт розміщені тут, без написів поверх карти.','','Сценарій і озвучка користувача збережені без змін. Немає AI-фото або AI-відео; сегментація лише відділяє реальний предмет від фону. 3D створене з геометрії та UV-текстур, не з деформації фото.','','## Матеріали'];review=[]
 for a in assets:
  lines+=['',f"### {a['id']} — {a.get('display_name','Original graphic')}"]
  for field in ['photo','video']:
   if not a.get(field):continue
   m=a.get(field+'_metadata',{});source=a.get(field+'_source','Original channel/project graphic')
   lines += [f'- {field}: {a[field]}',f'- Джерело: {source}',f"- Автор: {m.get('author',a.get(field+'_credit','Project'))}",f"- Ліцензія: {m.get('license',a.get('model_metadata',{}).get('license','Original project graphic; see source notices'))}"]
   for key,label in [('license_url','Умови'),('changes','Зміни'),('description','Опис джерела'),('date_taken','Дата зйомки')]:
    if m.get(key):lines.append(f'- {label}: '+str(m[key]).replace('\n',' ')[:1800])
  files=[]
  for field in ['photo','video','original_photo']:
   if a.get(field):
    f=BASE/a[field];assert f.is_file(),f;files.append({'field':field,'path':a[field],'bytes':f.stat().st_size,'sha256':digest(f)})
  review.append({'id':a['id'],'files':files,'license_review':'Source metadata/public-domain notices and upstream model licenses retained','visual_review':'Source sheets and scene control frames reviewed separately from full decode'})
 lines+=['','## Моделі','','Rafale B та Apache: вихідні моделі FlightGear, notices і GPL-2.0-or-later включені. Typhoon: Maverick Alex, upstream README — GPLv2; F-35B: upstream License.txt — GPLv3. Вихідна геометрія, текстури, конвертер і notices включені до assets/models. Освітлення студійне; лівреї не заявляються як точні бойові модифікації ВПС порівнюваних країн.','','## Факти в графіці','','SIPRI Yearbook 2026, Summary, друкована сторінка 11 (PDF page 13), таблиця World nuclear forces, January 2026: military stockpile France 290, UK 225. Це оцінка військових запасів, без списаних боєголовок; total inventory France 370, UK 225. https://www.sipri.org/sites/default/files/2026-06/yb26_summary_en_1.pdf . У графіці підписано саме військові запаси. Інші обмеження — claims.json.','','Комерційно сумісні CC BY/CC BY-SA/OGL/Etalab фотографії мають повні відомості авторства та умов у manifest.json. Зміни: масштабування й, для вибраних фото, відділення фону. Оригінальні завантажені версії включені.']
 (BASE/'SOURCES.md').write_text('\n'.join(lines)+'\n');(BASE/'source-review.json').write_text(json.dumps({'assets':review,'map_source_credits':'assets/maps/SOURCES.md','continuous_human_playback':'not performed; source sheets and encoded scene controls separately reviewed'},ensure_ascii=False,indent=2));print('SOURCES',len(assets))
if __name__=='__main__':main()
