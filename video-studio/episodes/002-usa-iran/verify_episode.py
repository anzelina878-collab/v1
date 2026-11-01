"""Technical verification; does not claim continuous human editorial playback."""
import argparse,json,subprocess,hashlib,sys,io
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE));from tools.edit_rules import check_archive_spacing

def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(p)]))
def audio(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-vn','-ar','8000','-ac','1','-f','f32le','-']),np.float32)
def frame(p,t,scale='320:180'):
 return subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(p),'-frames:v','1','-vf','scale='+scale,'-pix_fmt','rgb24','-f','rawvideo','-'])
def main():
 p=argparse.ArgumentParser();p.add_argument('video',type=Path);p.add_argument('--compiled',type=Path);p.add_argument('--output',type=Path,default=BASE/'output');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
 project=json.loads((BASE/'episode.json').read_text());x=probe(a.video);video=next(s for s in x['streams'] if s['codec_type']=='video');sound=next(s for s in x['streams'] if s['codec_type']=='audio');expected=round(project['duration']*30)
 assert (video['width'],video['height'],video['r_frame_rate'],int(video['nb_frames']))==(1920,1080,'30/1',expected)
 assert abs(float(x['format']['duration'])-project['duration'])<.06
 source=probe(BASE/project['audio']);original_sound=next(s for s in source['streams'] if s['codec_type']=='audio');assert sound['channels']==original_sound['channels']
 log=a.output/'full_decode.log';progress=a.output/'full_decode.progress'
 with log.open('w') as e:
  r=subprocess.run(['ffmpeg','-v','error','-i',str(a.video),'-map','0:v:0','-map','0:a:0','-progress',str(progress),'-f','null','-'],stderr=e)
 assert r.returncode==0 and not log.read_text().strip(),log.read_text()[-1000:]
 assert 'progress=end' in progress.read_text()
 original=audio(BASE/project['audio']);encoded=audio(a.video);n=min(len(original),len(encoded));correlation=float(np.corrcoef(original[:n],encoded[:n])[0,1]);assert correlation>.995,correlation
 check_archive_spacing(project['scenes'])
 frozen=[]
 if a.compiled:
  for s in project['scenes']:
   if s['kind'] not in ['graphic','compare'] or s['duration']<3:continue
   f=a.compiled/s['id']/'scene.mp4';first=np.frombuffer(frame(f,1.7),np.uint8).astype(np.float32);last=np.frombuffer(frame(f,s['duration']-.2),np.uint8).astype(np.float32);difference=float(np.abs(first-last).mean());assert difference<.4,(s['id'],difference);frozen.append({'id':s['id'],'mean_pixel_difference':difference})
 times=sorted(set([0,1,project['duration']-.15]+[s['start']+min(2,s['duration']*.5) for s in project['scenes']]))
 for offset in range(0,len(times),24):
  sheet=Image.new('RGB',(1280,6*202),'#111820');d=ImageDraw.Draw(sheet)
  for j,t in enumerate(times[offset:offset+24]):
   b=frame(a.video,t);im=Image.frombytes('RGB',(320,180),b);sheet.paste(im,(j%4*320,j//4*202));d.text((j%4*320+3,j//4*202+182),f'{int(t)//60:02d}:{t%60:05.2f}',fill='white')
  sheet.save(a.output/f'encoded-contact-{offset//24:02d}.jpg',quality=90)
 report={'status':'technically_verified','video':str(a.video),'sha256':hashlib.sha256(a.video.read_bytes()).hexdigest(),'duration':float(x['format']['duration']),'width':1920,'height':1080,'fps':30,'frames':expected,'audio_codec':sound['codec_name'],'audio_channels':sound['channels'],'audio_sample_rate':sound['sample_rate'],'original_audio_sha256':hashlib.sha256((BASE/project['audio']).read_bytes()).hexdigest(),'audio_waveform_correlation_zero_lag':correlation,'full_video_and_audio_decode':'passed','archive_spacing':'passed >60 seconds from previous use end','encoded_information_card_freeze_checks':frozen,'control_frames':len(times),'continuous_human_watch_and_listen':'not performed; source sheets, storyboard and encoded controls are separately reviewed'}
 (a.output/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('VERIFIED',report['sha256'],correlation,flush=True)
if __name__=='__main__':main()
