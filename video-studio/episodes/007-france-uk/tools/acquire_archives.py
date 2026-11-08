import urllib.request,urllib.parse,re,json,subprocess,concurrent.futures,html,time
from pathlib import Path
import os
B=Path(__file__).resolve().parents[1];T=Path(os.environ.get('ARSENAL_PREP_CACHE','/tmp/arsenal-007'));T.mkdir(exist_ok=True,parents=True)
S=[('leclerc-action', 605309, 'strong-europe-tank-challenge-cbrn-with-french-soldiers'), ('leclerc-fire', 605359, 'strong-europe-tank-challenge-offensive-operations-with-french-and-austrian-soldiers'), ('challenger-action', 604974, 'uk-offensive-operations-lane-strong-europe-tank-challenge-2018'), ('challenger-training', 551992, 'b-roll-challenger-tanks-royal-wessex-yeomanry'), ('caesar-action', 995708, 'dynamic-front-26-french-caesar-howitzer-live-fire-b-roll'), ('caesar-night', 877800, 'b-roll-french-soldiers-fire-caesar-into-night-during-dynamic-front-23'), ('archer-action', 944113, 'archer-fires-during-dynamic-front'), ('typhoon-walk', 996501, 'us-uk-eurofighter-typhoon-walkthrough'), ('typhoon-action', 995683, 'red-flag-nellis-26-1-b-roll'), ('qe-embark', 768700, 'f-35bs-embark-aboard-hms-queen-elizabeth'), ('cdg-operations', 922927, 'nato-ally-france-joins-neptune-strike-2024'), ('tomahawk-action', 362338, 'tomahawk-launch'), ('french-infantry', 839488, 'nato-response-force-nrf-soldiers-train-romania'), ('british-infantry', 607683, 'us-soldiers-fire-british-weapon'), ('trident-test', 1009153, 'uss-rhode-island-successfully-tests-trident-ii-d5-missile'), ('french-exercise', 976767, 'exercise-delayen-3rd-anglico-live-fire-range-tahiti'), ('apache-demo', 834686, 'apache-demo')]
def get(u):
 return urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Arsenal360-video-production/1.0'}),timeout=90).read()
def run(row):
 key,id,slug=row;cache=T/(key+'.record.json')
 if cache.exists():return json.loads(cache.read_text())
 try:
  url=f'https://www.dvidshub.net/video/{id}/{slug}';page=get(url).decode();(B/'assets/video-meta'/f'{key}.html').write_text(page)
  if 'Asset contains copyrighted material' in page or not re.search(r'PUBLIC\s+DOMAIN',page):raise ValueError('No explicit public domain notice')
  master=get(f'https://www.dvidshub.net/video/{id}.m3u8').decode();variants=[x for x in master.splitlines() if x.startswith('http')];u=next((x for x in variants if '1280x720' in x),variants[-1]);pl=get(u).decode();segments=[urllib.parse.urljoin(u,x) for x in pl.splitlines() if x and not x.startswith('#')];durations=[float(x.split(':')[1].split(',')[0]) for x in pl.splitlines() if x.startswith('#EXTINF')];total=0;ts=T/f'{key}.ts'
  with ts.open('wb') as f:
   for n,s in enumerate(segments):
    if total>=125:break
    f.write(get(s));total+=durations[n]
  out=B/'assets/video'/f'{key}.mp4';subprocess.run(['ffmpeg','-y','-v','error','-xerror','-i',str(ts),'-t','125','-an','-vf','scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,fps=30,setsar=1','-c:v','libx264','-preset','veryfast','-crf','21','-threads','1','-filter_threads','1','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],check=True);ts.unlink()
  duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(out)]));m=re.search(r'<meta[^>]+name="author"[^>]+content="([^"]+)',page);author=html.unescape(m.group(1)) if m else 'DVIDS / source credit retained';r=dict(id=key,video=f'assets/video/{key}.mp4',duration=duration,video_source=url,video_credit=f'{author} · Public domain',video_metadata={'license':'Public domain','author':author,'source':url,'changes':'Muted 720p normalized excerpt; editorial cuts; no playback speed changes'});cache.write_text(json.dumps(r,indent=2));print('OK',key,duration,flush=True);return r
 except Exception as e:print('FAILED',key,repr(e),flush=True);return None
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:r=list(ex.map(run,S))
(T/'archive-records.json').write_text(json.dumps([x for x in r if x],indent=2))
