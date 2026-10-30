#!/usr/bin/env python3
"""Decode the finished MP4 and measure its actual encoded audio."""
import json,re,subprocess,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];E=ROOT/'Производство/episodes/001-chelovek-bez-litsa';R=ROOT/'Результаты/001-chelovek-bez-litsa';p=R/'chelovek-bez-litsa-1080p.mp4'
t=json.loads((E/'timeline.json').read_text())
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(p)],text=True));v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'],v['codec_name'],v['r_frame_rate'])==(1920,1080,'h264','30/1')
assert a['codec_name']=='aac' and int(a['sample_rate'])==48000
assert int(v['nb_frames'])==t['total_frames']
assert abs(float(v['duration'])-float(a['duration']))<=1/30+.001
log=E/'render/final-decode-check.log';progress=E/'render/final-decode-progress.txt'
with log.open('w') as f:
 result=subprocess.run(['ffmpeg','-hide_banner','-nostats','-xerror','-threads','4','-filter_threads','1','-i',str(p),'-map','0:v:0','-map','0:a:0','-af','ebur128=peak=true:framelog=verbose','-progress',str(progress),'-stats_period','5','-f','null','-'],stdout=f,stderr=f)
assert result.returncode==0,'Full decoding failed; inspect log'
frames=[int(x) for x in re.findall(r'(?m)^frame=(\d+)',progress.read_text())];assert frames[-1]==t['total_frames']
s=log.read_text();lufs=float(re.findall(r'I:\s*([-\d.]+) LUFS',s)[-1]);peak=float(re.findall(r'Peak:\s*([-\d.]+) dBFS',s)[-1]);assert peak<=-1.0,(lufs,peak)
assert -15<=lufs<=-13,(lufs,peak)
report={'status':'technical_checks_passed','path':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'video_duration':float(v['duration']),'audio_duration':float(a['duration']),'frames':frames[-1],'width':v['width'],'height':v['height'],'fps':30,'integrated_lufs':lufs,'true_peak_dbtp':peak,'full_decode_exit_code':result.returncode,'full_human_playback':False,'audio_text_differences':'Retained from original; see sources-and-notes.txt','probe':probe}
(R/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:value for k,value in report.items() if k!='probe'},ensure_ascii=False),flush=True)
