"""Write complete attribution and file-integrity evidence for selected material."""
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
 project=json.loads((BASE/'episode.json').read_text());all={a['id']:a for a in json.loads((BASE/'assets/manifest.json').read_text())};keys={'in-flag','pk-flag'}
 for s in project['scenes']:
  if s['kind'] in ['photo','archive','turntable','map','ident']:keys.add(s['asset_id'])
  for key,_,_ in s.get('sides',[]):keys.add(key)
  if s['kind']=='archive':keys.add(FALLBACK[s['asset_id']])
 assets=[all[key] for key in sorted(keys)];(BASE/'assets/manifest.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2))
 lines=['# Джерела випуску 006 — Індія проти Пакистану','','Прапор позначає країну порівняння. Підпис «родина»/«тип» означає вигляд сімейства, а не гарантію конкретної національної модифікації чи лівреї. Інші оператори та навчання у відео названі окремо. Жодна вставка навчань не видається за зйомку конфлікту травня 2025 року.','','Карти створені в цьому проєкті зі справжньої сітки висот. Natural Earth NE2 1:50m, кордони та спірні лінії — public domain: https://www.naturalearthdata.com/about/terms-of-use/ . Terrarium terrain: https://registry.opendata.aws/terrain-tiles/ ; Mapzen/NASA/USGS/NOAA, атрибуції https://github.com/tilezen/joerd/blob/master/docs/attribution.md . Висоти перебільшені у 20 разів для читабельності. Спірні ділянки позначаються пунктиром; карта не є заявою про суверенітет. Джерела та інструменти не написані поверх карт на прохання користувача.','','Пошук та відхилені кандидати описані в claims.json. Оригінальну озвучку та сценарій надав користувач; текст і темп не змінювалися. ML-сегментація лише прибирає фон фотографій. AI-фотографії й AI-відео не використані.','','## Матеріали'];review=[]
 for a in assets:
  lines+=['',f"### {a['id']} — {a.get('display_name','АРСЕНАЛ 360°')}"]
  for field in ['photo','video']:
   if not a.get(field):continue
   m=a.get(field+'_metadata',{});source=a.get(field+'_source','Original channel graphic / existing series project')
   lines += [f'- {field}: {a[field]}',f'- Джерело: {source}',f"- Автор: {m.get('author',a.get(field+'_credit',a.get('credit','Original channel graphic')))}",f"- Ліцензія: {m.get('license','See original asset source and model notices')}"]
   if m.get('license_url'):lines.append('- Умови: '+m['license_url'])
   if m.get('changes'):lines.append('- Зміни: '+m['changes'])
   if m.get('description'):lines.append('- Опис джерела: '+m['description'].replace('\n',' ')[:1800])
  files=[]
  for field in ['photo','video','original_photo']:
   if a.get(field):
    f=BASE/a[field];assert f.is_file(),f;files.append({'field':field,'path':a[field],'bytes':f.stat().st_size,'sha256':digest(f)})
  review.append({'id':a['id'],'files':files,'license_review':'Source metadata / public-domain notices retained','visual_review':'Selected source sheets and scene control frames reviewed'})
 lines+=['','## Ліцензії моделей','','3D Rafale B: FGMEMBERS/RafaleB; Mirage 2000-5: Emmanuel Baranger та Fabien Barbier, FGMEMBERS/Mirage-2000; МиГ-29 та Apache: відповідні вихідні проєкти FlightGear. Оригінальні notices, геометрія, UV-текстури, конвертація та GPL-2.0-or-later включені в assets/models. Кольори й освітлення є студійною апроксимацією. Відкинуто лише симуляційні FX, а не елементи планера.','','Для GFDL-1.2 фотографії JF-17 включено повний текст assets/metadata/GFDL-1.2.txt. Повні відомості автора й походження містить manifest.json; вихідне фото збережене поряд із обробленою версією.','','## Факти в графіці','','SIPRI Yearbook 2026, оцінки станом на січень 2026: Індія приблизно 190, Пакистан приблизно 170 ядерних боєголовок. https://www.sipri.org/sites/default/files/2026-06/yb26_summary_en_1.pdf . Це оцінки дослідників. Інші посилання та межі фактчеку — claims.json.']
 (BASE/'SOURCES.md').write_text('\n'.join(lines)+'\n');(BASE/'source-review.json').write_text(json.dumps({'assets':review,'map_source_credits':'assets/maps/SOURCES.md','watermarks':'No downloaded-site overlays on maps; source credits retained on archive. Original source photos remain intact alongside selected cutouts.','continuous_human_playback':'not performed; source/scene frame reviews separate from full decode'},ensure_ascii=False,indent=2));print('SOURCES',len(assets),flush=True)
if __name__=='__main__':main()
