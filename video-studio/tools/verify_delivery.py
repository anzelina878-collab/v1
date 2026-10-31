"""Decode the complete deliverable and compare its audio with the supplied voice.
Usage: python tools/verify_delivery.py video.mp4 --audio voice.mp3 --report out.json
Requires numpy (requirements-3d.txt). No voice processing is performed.
"""
import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path
import numpy as np


def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))


def main():
    p=argparse.ArgumentParser()
    p.add_argument('video');p.add_argument('--audio',required=True);p.add_argument('--report',required=True)
    a=p.parse_args();video=Path(a.video).resolve();audio=Path(a.audio).resolve();report=Path(a.report).resolve()
    report.parent.mkdir(parents=True,exist_ok=True)
    media=probe(video);original=probe(audio)
    v=next(s for s in media['streams'] if s['codec_type']=='video')
    aud=next(s for s in media['streams'] if s['codec_type']=='audio')
    fps=int(round(eval_fraction(v['avg_frame_rate'])))
    duration=float(media['format']['duration']);audio_duration=float(original['format']['duration'])
    log=report.with_suffix('.decode.log');progress=report.with_suffix('.progress.txt')
    cmd=['ffmpeg','-v','info','-nostats','-threads','2','-i',str(video),'-vf','blackdetect=d=0.3:pix_th=0.02','-af','volumedetect','-filter_threads','1','-f','null','-progress',str(progress),'-']
    with log.open('w') as f:r=subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=f)
    logs=log.read_text();frames=[int(x) for x in re.findall(r'^frame=(\d+)$',progress.read_text(),re.M)]
    black=re.findall(r'black_start:([\d.]+) black_end:([\d.]+) black_duration:([\d.]+)',logs)
    def volume(name):
        match=re.search(name+r':\s*([-\d.]+) dB',logs)
        return float(match[1]) if match else None
    # Full-duration PCM comparisons in one fixed sample clock; no time stretching or inferred retiming.
    with tempfile.TemporaryDirectory(prefix='audio-compare-',dir=report.parent) as tmp:
        paths=[]
        for i,source in enumerate([audio,video]):
            out=Path(tmp)/f'{i}.f32'
            subprocess.run(['ffmpeg','-y','-v','error','-i',str(source),'-vn','-ac','1','-ar','16000','-f','f32le',str(out)],check=True)
            paths.append(out)
        x=np.fromfile(paths[0],dtype=np.float32);y=np.fromfile(paths[1],dtype=np.float32)
        n=min(len(x),len(y));xx=x[:n].astype(np.float64);yy=y[:n].astype(np.float64)
        denominator=float(np.sqrt(np.dot(xx,xx)*np.dot(yy,yy)))
        correlation=float(np.dot(xx,yy)/denominator) if denominator else 0
        # Check multiple windows to prevent an intact introduction hiding a broken later soundtrack.
        window_correlations=[]
        for start in range(0,n,60*16000):
            left=xx[start:min(n,start+60*16000)];right=yy[start:min(n,start+60*16000)]
            den=float(np.sqrt(np.dot(left,left)*np.dot(right,right)))
            if den>1e-6:window_correlations.append(float(np.dot(left,right)/den))
    result={
        'video':video.name,'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),
        'video_duration_seconds':duration,'original_audio_duration_seconds':audio_duration,
        'duration_difference_seconds':duration-audio_duration,'width':v['width'],'height':v['height'],
        'fps':v['avg_frame_rate'],'video_codec':v['codec_name'],'audio_codec':aud['codec_name'],
        'audio_sample_rate':aud['sample_rate'],'audio_channels':aud['channels'],
        'container_frame_count':int(v['nb_frames']),'decoded_frame_count':frames[-1] if frames else None,
        'complete_decode_exit_code':r.returncode,'black_intervals_over_0_3_seconds':black,
        'mean_volume_dbfs':volume('mean_volume'),'max_volume_dbfs':volume('max_volume'),
        'full_audio_waveform_correlation':correlation,
        'minimum_one_minute_audio_correlation':min(window_correlations) if window_correlations else None,
        'original_audio_sha256':hashlib.sha256(audio.read_bytes()).hexdigest(),
        'continuous_human_listening_performed':False,
        'continuous_human_video_playback_performed':False,
        'visual_review_method':'contact sheets for every scene plus selected encoded-frame checks',
    }
    checks={'resolution':(v['width'],v['height'])==(1920,1080),'fps':fps==30,'codecs':v['codec_name']=='h264' and aud['codec_name']=='aac','duration_within_one_video_frame':abs(duration-audio_duration)<=1/30+.002,'complete_decode':r.returncode==0,'all_frames_decoded':bool(frames) and frames[-1]==int(v['nb_frames']),'no_black_intervals':not black,'voice_preserved':correlation>.98 and min(window_correlations)>.97}
    result['automated_checks']=checks;result['all_automated_checks_passed']=all(checks.values())
    report.write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if not all(checks.values()):raise SystemExit(1)


def eval_fraction(value):
    numerator,denominator=value.split('/')
    return float(numerator)/float(denominator)


if __name__=='__main__':main()
