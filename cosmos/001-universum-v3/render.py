"""Portable cinematic stock renderer. No 2D charts or technical overlays."""
import argparse,pathlib,json,subprocess,concurrent.futures,hashlib,os,shutil,csv,time
def run(cmd,log):
 with open(log,'w') as f:
  p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
 if p.returncode:raise RuntimeError(str(log)+'\n'+pathlib.Path(log).read_text()[-1800:])
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--project',default='.');ap.add_argument('--audio',required=True);ap.add_argument('--output',default='Universum_V2_1080p.mp4');ap.add_argument('--preview',type=float,default=0);ap.add_argument('--cache-only',action='store_true');ap.add_argument('--skip-missing',action='store_true');ap.add_argument('--jobs',type=int,default=2);args=ap.parse_args()
 root=pathlib.Path(args.project).resolve();plan=json.loads((root/'plan.json').read_text());fps=plan['fps'];width=plan['width'];height=plan['height']
 audio=pathlib.Path(args.audio).resolve();output=pathlib.Path(args.output).resolve()
 assert audio.exists()
 if plan.get('audio_sha256') and hashlib.sha256(audio.read_bytes()).hexdigest()!=plan['audio_sha256']:raise ValueError('The audio does not match the supplied original narration.')
 cache=root/'render';cache.mkdir(exist_ok=True);logdir=root/'logs';logdir.mkdir(exist_ok=True);assets={a['key']:a for a in plan['assets']}
 shots=[]
 for s0 in plan['shots']:
  s=dict(s0)
  if args.preview and s['start_frame']>=round(args.preview*fps):break
  if args.preview:s['frames']=min(s['frames'],round(args.preview*fps)-s['start_frame'])
  shots.append(s)
 unique={s['render_key']+('_preview' if args.preview and s['frames']!=s0['frames'] else ''):s for s in shots}
 # The final path is determined by the actual content specification, including frame count.
 def path_for(s):
  content={k:s[k] for k in ['asset','in','frames','crop_top','effect','labels','fade_in','fade_out']}
  return cache/(hashlib.sha256(json.dumps(content,sort_keys=True).encode()).hexdigest()[:20]+'.mp4')
 font=root/'fonts'/'DejaVuSans.ttf';font=font if font.exists() else pathlib.Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
 def render_shot(s):
  out=path_for(s)
  if out.exists() and out.stat().st_size>1000:return out
  a=assets[s['asset']];p=pathlib.Path(a['path']);p=p if p.exists() else root/'assets'/(s['asset']+'.mp4')
  if not p.exists():raise FileNotFoundError(p)
  dur=s['frames']/fps;vf=[]
  if s['crop_top']:vf.append(f'crop=iw:ih-{s["crop_top"]}:0:{s["crop_top"]}')
  vf += [f'scale={width}:{height}:force_original_aspect_ratio=increase:flags=lanczos',f'crop={width}:{height}','setsar=1',f'fps={fps}','eq=contrast=1.025:saturation=1.015']
  if s['effect']=='dim':vf.append(f'fade=t=out:st=0:d={dur}')
  if s['fade_in']:vf.append(f'fade=t=in:st=0:d={s["fade_in"]}')
  if s['fade_out']:vf.append(f'fade=t=out:st={max(0,dur-s["fade_out"])}:d={s["fade_out"]}')
  for j,l in enumerate(s['labels']):
   textfile=logdir/(out.stem+f'-label{j}.txt');textfile.write_text(l['text'])
   st,en=l['start'],min(l['end'],dur);alpha=f"if(lt(t,{st}),0,if(lt(t,{st+.3}),(t-{st})/0.3,if(lt(t,{en-.3}),1,if(lt(t,{en}),({en}-t)/0.3,0))))"
   vf.append(f"drawtext=fontfile='{font}':textfile='{textfile}':fontsize=46:fontcolor=white:x=100:y=h-145:shadowcolor=black@0.8:shadowx=2:shadowy=3:alpha='{alpha}'")
  cmd=['ffmpeg','-y','-hide_banner','-loglevel','warning','-threads','1','-ss',str(s['in']),'-i',str(p),'-vf',','.join(vf),'-frames:v',str(s['frames']),'-an','-c:v','libx264','-preset','veryfast','-crf','19','-maxrate','10M','-bufsize','20M','-profile:v','high','-level','4.1','-pix_fmt','yuv420p','-threads','1','-filter_threads','1','-g',str(fps*2),'-video_track_timescale','12800',str(out)]
  run(cmd,logdir/(out.stem+'.log'));print('SHOT',s['id'],s['asset'],round(dur,2),flush=True);return out
 specs={str(path_for(s)):s for s in shots}
 if args.skip_missing:
  specs={k:s for k,s in specs.items() if pathlib.Path(assets[s['asset']]['path']).exists() and assets[s['asset']].get('kind')!='3d_explainer'}
 with concurrent.futures.ThreadPoolExecutor(args.jobs) as ex:list(ex.map(render_shot,specs.values()))
 if args.cache_only:
  print('CACHE COMPLETE',len(specs),flush=True);return
 concat=root/('concat-preview.txt' if args.preview else 'concat-v2.txt')
 concat.write_text(''.join("file '"+str(path_for(s))+"'\n" for s in shots))
 duration=sum(s['frames'] for s in shots)/fps
 cmd=['ffmpeg','-y','-hide_banner','-loglevel','warning','-f','concat','-safe','0','-i',str(concat),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-t',str(duration),'-c:v','copy','-c:a','aac','-b:a','192k','-metadata','title='+plan['title'],'-movflags','+faststart',str(output)]
 run(cmd,logdir/('preview-mux.log' if args.preview else 'final-mux.log'))
 probe=json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_entries','format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate','-of','json',str(output)]))
 assert abs(float(probe['format']['duration'])-duration)<.12
 v=next(s for s in probe['streams'] if s['codec_type']=='video');assert (v['width'],v['height'])==(1920,1080)
 assert any(s['codec_type']=='audio' for s in probe['streams'])
 output.with_suffix('.verification.json').write_text(json.dumps(probe,indent=2))
 print('DONE',str(output),json.dumps(probe),flush=True)
if __name__=='__main__':main()
