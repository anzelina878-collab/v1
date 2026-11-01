"""Align immutable supplied script to ASR and compile the reviewed visual map.
Run once after alignment/transcript.jsonl and assets/manifest.json exist.
"""
import json,re,difflib,math
from pathlib import Path
import numpy as np
from visual_map import SPANS
from tools.edit_rules import archive_allowed,check_archive_spacing
BASE=Path(__file__).resolve().parent
FPS=30;DURATION=1397.448;END=math.ceil(DURATION*FPS)/FPS

def tokens(s):return re.findall(r"[a-zа-яіїєґ0-9]+",s.lower().replace('ё','е'))

def main():
 paras=[s.strip() for s in (BASE/'inputs/script.uk.md').read_text().split('\n\n') if s.strip()]
 rows=[json.loads(s) for s in (BASE/'alignment/transcript.jsonl').read_text().splitlines()]
 audio=[];ats=[]
 for r in rows:
  for w in r.get('words',[]):
   for token in tokens(w['word']):audio.append(token);ats.append(w['start'])
 text=[];starts={};counts={}
 for i,p in enumerate(paras):
  if p.startswith('#'):continue
  starts[i]=len(text);t=tokens(p);counts[i]=len(t);text+=t
 match=difflib.SequenceMatcher(None,text,audio,autojunk=False)
 anchors={}
 for a,b,n in match.get_matching_blocks():
  for j in range(n):anchors[a+j]=ats[b+j]
 if len(anchors)/len(text)<.55:raise ValueError('ASR/script agreement too low; inspect input mismatch')
 keys=sorted(anchors);times=np.interp(np.arange(len(text)),keys,[anchors[k] for k in keys]);pt={i:float(times[a]) for i,a in starts.items()};pt[2]=0
 (BASE/'alignment/paragraphs.json').write_text(json.dumps([{'paragraph':i,'start':pt[i],'text':paras[i],'matched_words':sum(j in anchors for j in range(starts[i],starts[i]+counts[i])),'total_words':counts[i]} for i in starts],ensure_ascii=False,indent=2))
 assets={a['id']:a for a in json.loads((BASE/'assets/manifest.json').read_text())}
 spans=sorted(SPANS,key=lambda s:s['a']);scenes=[];history={};used={}
 def push(spec,start,end):
  if end-start<1/FPS:return
  scene=dict(spec);scene.update(start=start,end=end,duration=end-start,id=f'shot-{len(scenes)+1:03d}')
  scene['narration_quote']=' '.join(paras[i] for i in range(spec['a'],spec['b']+1) if not paras[i].startswith('#'))
  scene['visual_purpose']=f"{spec['kind']}: {spec['title'] or spec['asset_id']}; exact subject of the supplied narration"
  scene['entrance_once']=True;scene['settle_after']=1.2
  scenes.append(scene)
 for j,spec in enumerate(spans):
  start=round(pt[spec['a']]*FPS)/FPS if j else 0;end=round(pt[spans[j+1]['a']]*FPS)/FPS if j+1<len(spans) else END
  if spec['kind']=='archive':
   asset=assets[spec['asset_id']];duration=asset['duration'];fallback=asset['fallback_photo'];available=duration-1.0
   # A different quote or a later source offset never bypasses the source cooldown.
   if not archive_allowed(history,spec['asset_id'],start):
    push({**spec,'kind':'photo','asset_id':fallback,'title':asset['display_name']},start,end);continue
   source_in=asset.get('preferred_in',0)
   length=min(end-start,available-source_in)
   if length<2:push({**spec,'kind':'photo','asset_id':fallback,'title':asset['display_name']},start,end);continue
   # Reuse, when separated by >60 seconds, uses an unshown part if long enough.
   previous=used.get(spec['asset_id'],0)
   if previous+length+1<duration:source_in=max(source_in,previous)
   cut=round((start+length)*FPS)/FPS
   push({**spec,'source_in':source_in},start,cut);history[spec['asset_id']]=cut;used[spec['asset_id']]=source_in+length
   if end-cut>=1/FPS:push({**spec,'kind':'photo','asset_id':fallback,'title':asset['display_name']},cut,end)
  else:push(spec,start,end)
 check_archive_spacing(scenes)
 for s in scenes:
  if s['kind'] in ['archive','photo','turntable'] and s['asset_id'] not in assets:raise ValueError('Missing '+s['asset_id'])
  if s['kind']=='compare':
   for key,_,_ in s['sides']:
    if key not in assets:raise ValueError('Missing comparison photo '+key)
 for a,b in zip(scenes,scenes[1:]):assert abs(a['end']-b['start'])<.001
 chapters=[]
 for i,p in enumerate(paras):
  if p.startswith('## '):
   nxt=next(k for k in starts if k>i);chapters.append({'title':re.sub(r'^##\s*\d+:\d+\s*—\s*','',p),'start':round(pt[nxt]*FPS)/FPS})
 project={'schema':'arsenal.semantic-edit.v1','title':'США проти ІРАНУ: Повне порівняння військового арсеналу','width':1920,'height':1080,'fps':FPS,'duration':END,'audio':'audio/voice.mp3','audio_original_duration':DURATION,'audio_policy':'preserve tempo and all spoken content; frame-rounded tail only','scenes':scenes,'chapters':chapters,'asr_exact_token_match_ratio':len(anchors)/len(text),'review':'semantic map manually authored; ASR alignment requires control-frame review'}
 (BASE/'episode.json').write_text(json.dumps(project,ensure_ascii=False,indent=2));print('BUILT',len(scenes),'scenes',END,'seconds; token agreement',len(anchors)/len(text))
if __name__=='__main__':main()
