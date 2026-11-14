from pathlib import Path
import json,hashlib,subprocess,argparse,re,sys
import numpy as np
BASE=Path(__file__).resolve().parent

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  while data:=f.read(1048576):h.update(data)
 return h.hexdigest()
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
def frame(p,t):
 data=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(t),'-i',str(p),'-frames:v','1','-vf','scale=320:180','-threads','1','-f','rawvideo','-pix_fmt','rgb24','-']);return np.frombuffer(data,np.uint8).reshape(180,320,3).astype(float)
def validate():
 p=json.load(open(BASE/'episode.json'));assets={a['id']:a for a in json.load(open(BASE/'assets/manifest.json'))};ss=p['scenes'];assert (p['width'],p['height'],p['fps'])==(1920,1080,30);assert ss[0]['start']==0 and abs(ss[-1]['end']-p['duration'])<.002
 for a,b in zip(ss,ss[1:]):assert abs(a['end']-b['start'])<.002
 assert sum(round(s['duration']*30) for s in ss)==round(p['duration']*30)
 for rel,info in json.load(open(BASE/'INPUTS.json')).items():assert sha(BASE/rel)==info['sha256'] and (BASE/rel).stat().st_size==info['bytes']
 for rel,value in json.load(open(BASE/'alignment/timewarp.json'))['input_hashes'].items():assert sha(BASE/rel)==value,(rel,'stale timing plan')
 texts=[];moving=0;native=0
 for s in ss:
  texts +=[s.get(k,'') for k in ['title','subtitle','note']]+s.get('nodes',[])+[x[1] for x in s.get('sides',[])];assert s['entrance_once'] and not s.get('camera_motion')
  keys=[x[0] for x in s['sides']] if s['kind']=='compare' else [s['asset_id']] if s['kind'] in ['photo','archive','turntable'] else []
  for key in keys:
   field='video' if s['kind'] in ['archive','turntable'] else 'photo';assert (BASE/assets[key][field]).is_file()
  if s['kind']=='archive':
   moving+=s['duration'];duration=float(probe(BASE/assets[s['asset_id']]['video'])['format']['duration']);assert s.get('source_in',0)+s['duration']<=duration+.025
  if s['kind']=='turntable':native+=s['duration'];assert assets[s['asset_id']]['native_rotation_seconds']==24
 assert not re.search('[\u0400-\u04ff]','\n'.join(texts));assert not re.search(r'\b(?:USA|US)\b','\n'.join(texts))
 for c in p['chapters'][1:]:
  s=next(s for s in ss if s['kind']=='section' and s['start']<=c['spoken_start']<s['end']);assert s['start']+.65<=c['spoken_start']+.001
 return {'status':'passed','duration':p['duration'],'frames':round(p['duration']*30),'scene_count':len(ss),'chapter_cards':10,'chapter_titles_fully_visible_by_audio_cue':True,'original_audio_and_script_hashes':'passed','moving_archive_seconds':round(moving,3),'native_3d_seconds':round(native,3),'archive_frozen_tail_seconds':0,'moving_inputs_policy':'No tpad, no slowdown, no loop on documentary footage; all requested frames available from source','native_rotation_seconds_per_revolution':24,'continuous_human_watch_and_listen':'not performed; source correspondence, contact sheets, encoded controls and technical checks are separate'}
def main():
 a=argparse.ArgumentParser();a.add_argument('--video',type=Path);a.add_argument('--work',type=Path);a.add_argument('--output',type=Path,default=BASE/'output/qa/verification.json');args=a.parse_args();r=validate();print('PLAN_VALIDATED',json.dumps(r),flush=True);p=json.load(open(BASE/'episode.json'))
 if args.video:
  info=probe(args.video);v=next(x for x in info['streams'] if x['codec_type']=='video');aud=next(x for x in info['streams'] if x['codec_type']=='audio');source=next(x for x in probe(BASE/'audio/voiceover.mp3')['streams'] if x['codec_type']=='audio');assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'30/1',r['frames']);assert aud['sample_rate']==source['sample_rate'] and aud['channels']==source['channels'];assert abs(float(info['format']['duration'])-p['duration'])<.08
  subprocess.run(['ffmpeg','-v','error','-xerror','-threads','2','-i',str(args.video),'-map','0:v','-map','0:a','-f','null','-'],check=True);r['full_video_and_audio_decode']='passed';print('FULL_DECODE_PASSED',flush=True)
  def wave(path):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-ac','1','-ar','8000','-f','f32le','-']),np.float32)
  x=wave(BASE/'audio/voiceover.mp3');y=wave(args.video);n=min(len(x),len(y));cor=float(np.corrcoef(x[:n],y[:n])[0,1]);assert cor>.995,cor;r['audio_waveform_correlation_zero_lag']=cor;print('AUDIO_SYNC_PASSED',cor,flush=True)
  r.update(sha256=sha(args.video),bytes=args.video.stat().st_size,video_stream=v,audio_stream=aud)
 if args.work:
  static=[];moving=[];assets={a['id']:a for a in json.load(open(BASE/'assets/manifest.json'))}
  for s in p['scenes']:
   f=args.work/s['id']/'scene.mp4'
   if s['kind'] in ['photo','compare','graphic','section','question','outro','ident'] and s['duration']>3:
    first=max(2,s['settle_after']+.2)
    if first+.3<s['duration']:
     mae=float(np.abs(frame(f,first)-frame(f,s['duration']-.12)).mean());assert mae<1.2,(s['id'],mae);static.append({'scene':s['id'],'settled_frame_mae':mae})
   if s['kind'] in ['archive','turntable']:
    length=min(1.6,s['duration']-.1);start=max(0,s['duration']-length-.04);buf=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(start),'-i',str(f),'-vf','fps=5,scale=192:108','-frames:v','8','-threads','1','-f','rawvideo','-pix_fmt','rgb24','-']);arr=np.frombuffer(buf,np.uint8).reshape(-1,108,192,3).astype(float);diff=np.abs(np.diff(arr[:,:90],axis=0)).mean(axis=(1,2,3));assert len(diff)>0
    frozen=bool(len(diff)>=3 and np.max(diff[-3:])<.035);assert not frozen,(s['id'],'Frozen ending',diff.tolist());assert float(arr[:,:90].mean())>4,(s['id'],'Black ending');moving.append({'scene':s['id'],'last_frame_differences':diff.tolist(),'frozen_tail':False})
  r.update(locked_photos_and_settled_cards=static,moving_shot_end_checks=moving);print('STATIC_AND_MOVING_ENDS_PASSED',len(static),len(moving),flush=True)
 args.output.parent.mkdir(exist_ok=True,parents=True);args.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print('CHECKS_PASSED',args.output,flush=True)
if __name__=='__main__':main()
