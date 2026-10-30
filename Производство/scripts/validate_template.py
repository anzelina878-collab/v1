#!/usr/bin/env python3
"""Check active channel settings, skill registration and local documentation links."""
import json,re,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2]
def main():
 errors=[];s=json.loads((R/'settings.json').read_text())
 if s.get('schema_version')!=3 or s.get('channel_id')!='chelovek-bez-litsa':errors.append('Wrong channel/schema')
 if s['languages']['primary']!='ru':errors.append('Default language must be ru')
 if sum(s['assets']['screen_time_targets_percent'].values())!=100:errors.append('Media duration targets must sum to 100')
 if not s['assets']['graphics_allowed'] or not s['assets']['ai_video_allowed']:errors.append('Missing requested visual types')
 if s['narration_input']['generation_enabled']:errors.append('Narration generation must stay disabled')
 if s['cleanup']['automatic_deletion']:errors.append('Inputs must not be deleted automatically')
 active=[R/'AGENTS.md',R/'README.md']+list((R/'Данные проекта').glob('*.md'))
 for key,rel in s['skills'].items():
  p=R/rel
  if not p.is_file():errors.append('Missing skill '+key);continue
  if not p.parent.name.startswith('faceless-'):errors.append('Old skill registration '+rel)
  active.append(p)
 for p in active:
  text=p.read_text()
  if re.search(r'retro-engineering|PASTWORKS|source=primary=uk|before TTS',text,re.I):errors.append('Obsolete active instruction '+str(p.relative_to(R)))
  for link in re.findall(r'\]\(([^)]+)\)',text):
   link=link.strip('<>').split('#',1)[0]
   if not link or '://' in link:continue
   if not (p.parent/link).exists():errors.append(f'Broken link {p.relative_to(R)}: {link}')
 print(json.dumps({'status':'failed' if errors else 'passed','active_skills':len(s['skills']),'checked_documents':len(active),'errors':errors,'scope':'template consistency; no film rendered, AI-video provider not tested'},ensure_ascii=False,indent=2))
 return bool(errors)
if __name__=='__main__':raise SystemExit(main())
