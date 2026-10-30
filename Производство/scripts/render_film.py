#!/usr/bin/env python3
"""Render the reviewed phrase-aligned illustrative film through native FFmpeg."""
import argparse,concurrent.futures,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
E=ROOT/'Производство/episodes/001-chelovek-bez-litsa'

def main():
 ap=argparse.ArgumentParser(description='Historical episode 001 renderer; not the current channel engine')
 ap.add_argument('--render-legacy-episode-001',action='store_true',help='Explicitly opt in to rendering the historical episode')
 ap.add_argument('--limit',type=int);ap.add_argument('--workers',type=int,default=3);args=ap.parse_args()
 if not args.render_legacy_episode_001:ap.error('Historical episode renderer is disabled by default; editing the template must not rebuild delivered video.')
 timeline=json.loads((E/'timeline.json').read_text());manifest=json.loads((E/'assets/manifest.json').read_text());assets={a['id']:a for a in manifest['assets']};shots=timeline['shots'][:args.limit] if args.limit else timeline['shots']
 if not args.limit:
  audit=json.loads((E/'pre_render_audit.json').read_text())
  assert audit['status']=='passed_for_illustrative_cut'
  for name,path in [('timeline',E/'timeline.json'),('manifest',E/'assets/manifest.json')]:assert audit['hashes'][name]==hashlib.sha256(path.read_bytes()).hexdigest()
 parts=E/'render/parts';parts.mkdir(exist_ok=True)
 font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
 def run(shot):
  asset=assets[shot['asset_id']];src=E/'assets'/asset['path'];out=parts/(shot['id']+'.mp4');marker=out.with_suffix('.sha256');key=hashlib.sha256(json.dumps([shot,asset,timeline['color_treatment'],1920,1080,30,'render-v1'],sort_keys=True).encode()).hexdigest()
  if out.exists() and marker.exists() and marker.read_text()==key:return out
  cmd=['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-filter_threads','1','-threads','1'];vf=[]
  if asset['kind']=='video':cmd+=['-ss',str(shot['source_start'])]
  else:cmd+=['-loop','1','-framerate','30'];q=asset['quadrant'];vf += [f'crop=iw/2:ih/2:iw/2*{q%2}:ih/2*{q//2}']
  cmd+=['-i',str(src)]
  if asset.get('crop_top_fraction'):c=asset['crop_top_fraction'];vf +=[f'crop=iw:ih*{1-c}:0:ih*{c}']
  vf += ['scale=1920:1080:force_original_aspect_ratio=increase:flags=bicubic','crop=1920:1080','setsar=1','fps=30','format=yuv444p']
  if asset['kind']=='image':
   n=max(1,shot['frames']-1);p=f'0.016*on/{n}'
   vf += [f"perspective=x0='-W*{p}':y0='-H*{p}':x1='W+W*{p}':y1='-H*{p}':x2='-W*{p}':y2='H+H*{p}':x3='W+W*{p}':y3='H+H*{p}':interpolation=cubic:sense=destination:eval=frame"]
  vf += ['eq=saturation=0.82:contrast=1.025']
  if shot['id']=='shot_0001':
   vf += [f"drawtext=fontfile={font}:text='ЧЕЛОВЕК БЕЗ ЛИЦА':fontsize=64:fontcolor=white:x=95:y=795:shadowcolor=black:shadowx=2:shadowy=2",f"drawtext=fontfile={font}:text='Иллюстративная реконструкция':fontsize=30:fontcolor=white@0.85:x=98:y=880:shadowcolor=black:shadowx=2:shadowy=2"]
  if shot.get('fade_out_seconds'):
   d=shot['fade_out_seconds'];vf += [f'fade=t=out:st={shot["frames"]/30-d}:d={d}']
  vf += ['scale=1920:1080:out_color_matrix=bt709:out_range=tv','format=yuv420p']
  cmd+=['-an','-vf',','.join(vf),'-frames:v',str(shot['frames']),'-c:v','libx264','-preset','veryfast','-crf','23','-threads','1','-g','60','-keyint_min','30','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-video_track_timescale','30000','-y',str(out)]
  p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  if p.returncode:raise RuntimeError(shot['id']+' '+p.stderr[-3000:])
  count=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames','-of','json',str(out)],text=True))['streams'][0]['nb_frames']
  if int(count)!=shot['frames']:raise RuntimeError(f'Wrong frame count in {out}: {count}')
  marker.write_text(key);return out
 with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
  for i,path in enumerate(pool.map(run,shots),1):print(f'{i}/{len(shots)} {path.name}',flush=True)
 listing=E/'render/concat.txt';listing.write_text(''.join("file '"+str((parts/(s['id']+'.mp4')).resolve())+"'\nduration "+f"{s['frames']/30:.9f}"+"\n" for s in shots))
 if not args.limit:
  dest=ROOT/'Результаты/001-chelovek-bez-litsa';dest.mkdir(parents=True,exist_ok=True)
  cmd=['ffmpeg','-v','error','-nostdin','-f','concat','-safe','0','-i',str(listing),'-i',str(E/'render/narration-master.m4a'),'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart','-metadata','title=Человек без лица — история Алекса','-y',str(dest/'chelovek-bez-litsa-1080p.mp4')]
  subprocess.run(cmd,check=True)
  print('FILM',str(dest/'chelovek-bez-litsa-1080p.mp4'),flush=True)

if __name__=='__main__':main()
