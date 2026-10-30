#!/usr/bin/env python3
"""Validate the new channel's plan contract, not the truth of pictures or sources."""
import argparse,json,re,math
from pathlib import Path
from urllib.parse import urlsplit

KINDS={'stock_video','ai_video','motion_graphics','real_photo','document','generated_image'}

def normalize(s):return ' '.join(re.findall(r'[a-zа-яё0-9]+',str(s).lower().replace('ё','е')))
def source_url(s):return urlsplit(str(s)).scheme in {'http','https'} and bool(urlsplit(str(s)).netloc)

def validate_plan(plan,manifest,claims=None,transcript=None,ready=False,asset_root=None):
 errors=[];warnings=[];ai_intervals=[];seconds={k:0.0 for k in KINDS};seen=set();assets={};claim_map={}
 def err(code,where):errors.append(f'{code}: {where}')
 if plan.get('schema_version')!=1:err('schema_version','expected 1')
 if plan.get('channel_id')!='chelovek-bez-litsa':err('channel_id','wrong channel')
 for a in manifest.get('assets',[]):
  aid=a.get('id')
  if not aid or aid in assets:err('asset_id','missing or duplicate')
  assets[aid]=a
  kind=a.get('kind')
  if kind not in KINDS:err('asset_kind',aid)
  if kind in {'stock_video','real_photo','document'} and (not source_url(a.get('source_url')) or not a.get('usage_basis')):err('source_and_basis',aid)
  if kind=='ai_video':
   err('ai_video_disabled',aid)
   suffix=Path(a.get('path') or '').suffix.lower()
   if a.get('generation_medium')!='video' or not a.get('generator') or suffix in {'.png','.jpg','.jpeg','.webp','.svg'}:err('photo_is_not_ai_video',aid)
  if kind=='generated_image' and a.get('verified_identity'):err('generated_portrait_not_evidence',aid)
  if kind in {'ai_video','generated_image'} and a.get('provenance')=='authentic_event_recording':err('synthetic_not_archive',aid)
  if kind=='real_photo' and a.get('person_id') and (a.get('verified_identity') is not True or not source_url(a.get('identity_source_url'))):err('portrait_identity',aid)
  if asset_root is not None and a.get('path') and not (asset_root/a['path']).is_file():err('missing_file',aid)
  if ready and not a.get('path'):err('ready_asset_missing_path',aid)
 for c in claims or []:
  cid=c.get('id')
  if not cid or cid in claim_map:err('claim_id','missing or duplicate')
  claim_map[cid]=c
 end=0.0
 shots=plan.get('shots',[])
 if not shots:err('empty_plan','no shots')
 for shot in shots:
  sid=shot.get('id')
  if not sid or sid in seen:err('shot_id','missing or duplicate')
  seen.add(sid)
  try:start=float(shot['start']);stop=float(shot['end'])
  except (ValueError,TypeError,KeyError):err('shot_time',sid);continue
  if not math.isfinite(start) or not math.isfinite(stop):err('nonfinite_time',sid);continue
  if start<0 or stop<=start:err('shot_duration',sid)
  if abs(start-end)>.001:err('timeline_gap_or_overlap',sid)
  end=stop
  a=assets.get(shot.get('asset_id'))
  if not a:err('unknown_asset',sid);continue
  kind=a.get('kind')
  if kind in seconds:seconds[kind]+=max(0,stop-start)
  def include_ai_photo(asset,left,right,motion):
   if asset.get('kind')!='generated_image':return
   ai_intervals.append((left,right))
   if ready:
    if not isinstance(motion,dict) or motion.get('type') not in {'pan','parallax','push_in','pull_out','document_reveal'} or motion.get('safe_crop_reviewed') is not True:err('ai_photo_motion_required',sid)
  include_ai_photo(a,start,stop,shot.get('motion'))
  for overlay in shot.get('overlays',[]):
   oa=assets.get(overlay.get('asset_id'))
   if not oa:err('unknown_overlay_asset',sid);continue
   try:left=float(overlay.get('start',start));right=float(overlay.get('end',stop))
   except (ValueError,TypeError):err('overlay_time',sid);continue
   if not math.isfinite(left) or not math.isfinite(right) or left<start or right>stop or right<=left:err('overlay_time',sid);continue
   include_ai_photo(oa,left,right,overlay.get('motion'))
  q=normalize(shot.get('narration_quote',''))
  if not q or not shot.get('visual_purpose'):err('semantic_binding_required',sid)
  if transcript is not None and q and q not in normalize(transcript):err('quote_not_in_narration',sid)
  if ready and shot.get('editorial_review')!='reviewed':err('editorial_review_required',sid)
  tags=set(a.get('tags',[]))
  negated=bool(re.search(r'\bне\s+(?:\w+\s+)?(?:пая|ремонт|восстан|solder|repair)',q))
  if 'soldering' in tags and (not re.search(r'па[яй]|припо|solder',q) or negated):err('irrelevant_soldering',sid)
  board=bool(re.search(r'плат[аыуе]|печатн|motherboard|circuit board',q))
  if 'pcb_repair' in tags and (not board or not re.search(r'ремонт|восстан|repair',q) or negated):err('irrelevant_pcb_repair',sid)
  if 'pcb_closeup' in tags and not (board or re.search(r'процессор|микросхем|чип|электрон',q)):err('irrelevant_pcb_closeup',sid)
  refs=list(dict.fromkeys(a.get('claim_ids',[])+shot.get('graphic_claim_ids',[])))
  if a.get('numeric_values') and not refs:err('numeric_graphic_without_claim',sid)
  for cid in refs:
   c=claim_map.get(cid)
   if not c or c.get('verified') is not True or not source_url(c.get('source_url')):err('unverified_graphic_claim',f'{sid}/{cid}')
 try:duration=float(plan['duration_seconds'])
 except (ValueError,TypeError,KeyError):duration=0;err('duration_seconds','missing or invalid')
 if not math.isfinite(duration) or duration<=0:err('duration_seconds','must be positive and finite');duration=0
 if duration<=0 or abs(end-duration)>.001:err('timeline_end',end)
 merged=[]
 for left,right in sorted(ai_intervals):
  left=max(0,left);right=min(duration,right)
  if right<=left:continue
  if merged and left<=merged[-1][1]:merged[-1]=(merged[-1][0],max(right,merged[-1][1]))
  else:merged.append((left,right))
 ai_seconds=sum(right-left for left,right in merged)
 ai_fraction=ai_seconds/duration if duration else 0
 if ai_fraction>.10+1e-9:err('ai_photo_screen_time_exceeds_10_percent',f'{ai_seconds:.3f}s / {duration:.3f}s')
 still=sum(seconds[k] for k in ['real_photo','document','generated_image'])
 if duration>0 and still/duration>.20:warnings.append('photo_heavy: review duration mix; camera movement does not change media kind')
 if not seconds['motion_graphics']:warnings.append('no_primary_graphics: verify whether overlays or explanatory graphics are planned')
 return {'errors':errors,'warnings':warnings,'seconds_by_primary_kind':seconds,'ai_photo_screen_seconds':ai_seconds,'ai_photo_screen_fraction':ai_fraction,'shot_count':len(shots),'validation_scope':'contract_and_known_regressions_only; visual/editorial/source review still required'}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('timeline',type=Path);p.add_argument('manifest',type=Path);p.add_argument('--claims',type=Path);p.add_argument('--transcript',type=Path);p.add_argument('--ready',action='store_true');p.add_argument('--require-files',action='store_true');a=p.parse_args()
 report=validate_plan(json.loads(a.timeline.read_text()),json.loads(a.manifest.read_text()),json.loads(a.claims.read_text()) if a.claims else [],a.transcript.read_text() if a.transcript else None,a.ready,a.manifest.parent if a.require_files else None)
 print(json.dumps(report,ensure_ascii=False,indent=2));return bool(report['errors'])

if __name__=='__main__':raise SystemExit(main())
