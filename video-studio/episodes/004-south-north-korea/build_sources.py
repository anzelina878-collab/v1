"""Write a selected source library and human-readable attribution record."""
from pathlib import Path
import json,hashlib
BASE=Path(__file__).resolve().parent

def main():
 from build_episode import FALLBACK
 project=json.loads((BASE/'episode.json').read_text());rows=json.loads((BASE/'assets/manifest.json').read_text());used={s['asset_id'] for s in project['scenes']};used|={x[0] for s in project['scenes'] for x in s.get('sides',[])};used|={'kr-flag','kp-flag'};used|={FALLBACK[s['asset_id']] for s in project['scenes'] if s['kind']=='archive'};rows=[x for x in rows if x['id'] in used];(BASE/'assets/manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
 out=['# Джерела та атрибуції — випуск 004','','Повні дані джерел та авторства. Скорочені підписи у кадрі не замінюють ці дані. Голос і сценарій — незмінені матеріали користувача. Власна заставка — АРСЕНАЛ 360°.','', '## Карти','','Natural Earth — Public domain: https://www.naturalearthdata.com/about/terms-of-use/ . Дані: https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_admin_0_countries.geojson . Зміни: сферична/регіональна проєкція, світло, кольори країн, столиці та українські підписи.',''];audit=[]
 for a in rows:
  out+=['## '+a['id'],'']
  for kind in ['photo','video','model']:
   credit=a.get(kind+'_credit','');source=a.get(kind+'_source','');meta=a.get(kind+'_metadata',{})
   if not (credit or source or meta):continue
   out.append(kind+': '+credit)
   if source:out.append('Source: '+source)
   if meta:out+=['```json',json.dumps(meta,ensure_ascii=False,indent=2),'```']
  modifications='Studio camera, lighting and neutral display rendering; exterior geometry only' if a.get('visual_origin')=='true_3d_render' else 'Монтажний інтервал, масштабування, розміщення, назви й атрибуція; відділення фону/обрізка там, де зазначено в метаданих'
  out+=['','Зміни: '+modifications+'.',''];record={'id':a['id'],'used_in_film':a['id'] in {s['asset_id'] for s in project['scenes']} or any(a['id']==x[0] for s in project['scenes'] for x in s.get('sides',[])),'files':{}}
  for field in ['photo','video','original_photo']:
   if not a.get(field):continue
   f=BASE/a[field];assert f.is_file(),(a['id'],field,f);record['files'][a[field]]={'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
  audit.append(record)
 out+=['## Ліцензійні умови','','CC BY 3.0: https://creativecommons.org/licenses/by/3.0/','CC BY 4.0: https://creativecommons.org/licenses/by/4.0/','CC BY-SA 2.0: https://creativecommons.org/licenses/by-sa/2.0/','CC BY-SA 3.0: https://creativecommons.org/licenses/by-sa/3.0/','CC BY-SA 4.0: https://creativecommons.org/licenses/by-sa/4.0/','KOGL Type1: https://www.kogl.or.kr/info/licenseType1.do','DVIDS: https://www.dvidshub.net/about/copyright','GPL-2.0: локальні COPYING, .ac та вихідна геометрія включені в каталоги моделей.','', 'Зображення CC BY-SA та їх похідні зображення надаються під зазначеною версією CC BY-SA. Права на сторонні матеріали залишаються за авторами; LICENSE студії не замінює ліцензії медіа. Кожен DVIDS-матеріал перевірявся за його власною сторінкою Public Domain; сама назва платформи не є підставою для інших файлів.','']
 (BASE/'SOURCES.md').write_text('\n'.join(out));(BASE/'source-review.json').write_text(json.dumps({'source_assets':len(rows),'file_audit':audit,'scope':'Source metadata, selected intervals, photographic masks and storyboards reviewed; continuous full human playback is not claimed'},ensure_ascii=False,indent=2));print('SOURCE_LIBRARY',len(rows),flush=True)
if __name__=='__main__':main()
