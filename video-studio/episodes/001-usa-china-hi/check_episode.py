"""Episode-specific validation and encoded checks. No claim of continuous human review."""
from pathlib import Path
import json,hashlib,subprocess,argparse,re,sys,math
import numpy as np
BASE=Path(__file__).resolve().parent

def digest(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  while b:=f.read(1048576):h.update(b)
 return h.hexdigest()
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
def frame(p,t):
 b=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(t),'-i',str(p),'-frames:v','1','-vf','scale=320:180','-threads','1','-f','rawvideo','-pix_fmt','rgb24','-']);return np.frombuffer(b,np.uint8).reshape(180,320,3).astype(float)
def validate():
 p=json.load(open(BASE/'episode.json'));sc=p['scenes'];alignment=json.load(open(BASE/'alignment/report.json'));assert next(x for x in alignment['reports'] if x['language']=='hi')['exact_normalized_token_agreement']>.4
 assert next(x for x in alignment['reports'] if x['language']=='hi')['timing_refinement_windows']==8
 for rel,value in json.load(open(BASE/'alignment/timewarp.json'))['build_inputs_sha256'].items():assert digest(BASE/rel)==value,(rel,'Stale scene timing plan')
 last=json.loads((BASE/'alignment/transcript.jsonl').read_text().splitlines()[-1]);assert last['end']>p['original_audio_duration']-2,'Full Hindi alignment is incomplete'
 assert p['language']=='hi' and p['fps']==30 and p['width']==1920 and p['height']==1080
 original=json.load(open(BASE/'inputs/original-episode.v4.json'));original_ids={x['id'] for x in original['scenes']};adapted_ids={x for scene in sc for x in scene['original_scene_ids']};assert adapted_ids==original_ids,'An original visual beat was omitted'
 assert abs(sc[0]['start'])<.001
 for a,b in zip(sc,sc[1:]):assert abs(a['end']-b['start'])<.002
 assert abs(sc[-1]['end']-p['duration'])<.002
 assert sum(round(s['duration']*30) for s in sc)==round(p['duration']*30)
 for rel,r in json.load(open(BASE/'INPUTS.json')).items():assert digest(BASE/rel)==r['sha256'] and (BASE/rel).stat().st_size==r['bytes'],rel
 visible=[]
 def walk(x):
  if isinstance(x,list):
   for v in x:walk(v)
  elif isinstance(x,dict):
   for k,v in x.items():
    if k in ['title','subtitle','label','detail','eyebrow','text','note'] and isinstance(v,str):visible.append(v)
    elif k in ['sides','items','nodes','callouts']:walk(v)
    if k in ['image','video'] and v:assert (BASE/v).is_file(),v
 for s in sc:
  walk(s);assert s['entrance_once'] and not s['camera_motion'];assert round(s['duration']*30)>=1
  if s.get('motion_kind')=='true_3d':assert s['rotation_degrees_per_second']==15 and s['bank_duration']==24
 assert not re.search('[\u0400-\u04ff]','\n'.join(visible)),'Untranslated Cyrillic editorial text'
 ar={r['id']:r for r in json.load(open(BASE/'assets/archive-manifest.json'))};moving=held=0
 for s in sc:
  if s.get('archive_bank'):
   d=ar[s['archive_bank']]['duration'];moving+=min(s['duration'],d);held+=max(0,s['duration']-d)
 report={'status':'passed','scene_count':len(sc),'original_scene_coverage':len(original_ids),'duration':p['duration'],'frames':round(p['duration']*30),'first_90_seconds_shots':sum(s['start']<90 for s in sc),'exact_inputs_sha256':'passed','visible_editorial_text_no_cyrillic':'passed','all_referenced_media_present':'passed','real_archive_moving_seconds':round(moving,3),'archive_licensed_still_tail_seconds':round(held,3),'source_archive_windows':'Original episode #1 selections preserved at normal speed; no additional archive replay introduced. Original #1 is not subject to later episodes spacing rule.','native_3d_seconds':round(sum(s['duration'] for s in sc if s.get('motion_kind')=='true_3d'),3),'rotation_seconds_per_revolution':24,'continuous_human_watch_and_listen':'not performed; discrete semantic, storyboard, encoded-control and technical checks are separate'}
 return report

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--video',type=Path);ap.add_argument('--work',type=Path);ap.add_argument('--output',type=Path,default=BASE/'output/qa/verification.json');a=ap.parse_args();r=validate();print('PLAN_VALIDATED',json.dumps(r),flush=True)
 if a.video:
  info=probe(a.video);v=next(x for x in info['streams'] if x['codec_type']=='video');aud=next(x for x in info['streams'] if x['codec_type']=='audio');assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'30/1',r['frames']);source_audio=next(x for x in probe(BASE/'audio/voiceover.mp3')['streams'] if x['codec_type']=='audio');assert aud['codec_name']=='aac' and aud['sample_rate']==source_audio['sample_rate'] and aud['channels']==source_audio['channels'];assert abs(float(info['format']['duration'])-r['duration'])<.08
  subprocess.run(['ffmpeg','-v','error','-xerror','-threads','1','-i',str(a.video),'-map','0:v','-map','0:a','-f','null','-'],check=True);r['full_video_and_audio_decode']='passed'
  def waveform(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-ac','1','-ar','8000','-f','f32le','-']),np.float32)
  x=waveform(BASE/'audio/voiceover.mp3');y=waveform(a.video);n=min(len(x),len(y));cor=float(np.corrcoef(x[:n],y[:n])[0,1]);assert cor>.995,cor;r['audio_waveform_correlation_zero_lag']=cor
  if a.work:
   p=json.load(open(BASE/'episode.json'));checks=[]
   for s in p['scenes']:
    if s.get('video') or s['duration']<4:continue
    t=max(2,s.get('settle_after',1.2)+.35)
    if t+.5>=s['duration']-.1:continue
    f=a.work/s['id']/'scene.mp4';left=frame(f,t);right=frame(f,s['duration']-.1)
    if s.get('callouts'):left[15:29,204:307]=0;right[15:29,204:307]=0
    mae=float(np.abs(left-right).mean());assert mae<1.2,(s['id'],mae);checks.append({'scene':s['id'],'settled_frame_mae':mae,'intentional_fact_overlay_masked':bool(s.get('callouts'))})
   r['locked_photos_and_settled_cards']=checks
  r.update(sha256=digest(a.video),bytes=a.video.stat().st_size,video_stream=v,audio_stream=aud)
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print('CHECKS_PASSED',a.output,flush=True)
if __name__=='__main__':main()
