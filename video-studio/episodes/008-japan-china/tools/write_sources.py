"""Write human-readable attribution from the reviewed asset manifest."""
from pathlib import Path
import json
BASE=Path(__file__).resolve().parents[1]
def main():
 lines=['# Джерела та ліцензії','','Авторство та ліцензії сторонніх матеріалів збережено. Адаптовані зображення CC BY-SA поширюються за відповідною ліцензією оригіналу; геометрія F-35B — GPL-3.0. Оригінальні текст і голос належать їхньому правовласнику.','']
 for a in json.loads((BASE/'assets/manifest.json').read_text()):
  lines+=['## '+a['id'],'']
  for kind in ['photo','video']:
   if not a.get(kind):continue
   md=a.get(kind+'_metadata',{});lines += [f"- Файл: {a[kind]}",f"- Автор / ліцензія: {a.get(kind+'_credit','Original visualization')}",f"- Джерело: {a.get(kind+'_source','Original channel asset')}",f"- Ліцензія: {md.get('license_url',md.get('license','See model metadata or maps/SOURCES.md'))}",f"- Зміни: {md.get('changes','Original rendering / presentation')}",'']
 lines+=['## Карти','',(BASE/'assets/maps/SOURCES.md').read_text()]
 (BASE/'SOURCES.md').write_text('\n'.join(x.rstrip() for x in '\n'.join(lines).splitlines())+'\n')
if __name__=='__main__':main()
