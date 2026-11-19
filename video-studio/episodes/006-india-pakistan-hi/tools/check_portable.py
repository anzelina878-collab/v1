from pathlib import Path
import zipfile,json,hashlib,argparse,sys,copy,subprocess
ap=argparse.ArgumentParser();ap.add_argument('zip',type=Path);ap.add_argument('--extract',type=Path,required=True);ap.add_argument('--report',type=Path,required=True);args=ap.parse_args();slug='006-india-pakistan-hi';prefix='video-studio/episodes/'+slug+'/'
with zipfile.ZipFile(args.zip) as z:
 names=z.namelist();assert len(set(names))==len(names);assert all(n.startswith('video-studio/') and '..' not in Path(n).parts and not n.startswith('/') for n in names)
 checks=json.loads(z.read(prefix+'assets-checksums.json'))
 for name,expected in checks.items():
  h=hashlib.sha256();count=0
  with z.open(prefix+name) as f:
   while b:=f.read(1048576):h.update(b);count+=len(b)
  assert count==expected['bytes'] and h.hexdigest()==expected['sha256'],name
 p=json.loads(z.read(prefix+'episode.json'));assets={a['id']:a for a in json.loads(z.read(prefix+'assets/manifest.json'))};scenes=[]
 for kind in ['turntable','archive','photo','compare','graphic','section','ident','question','map','outro']:
  candidates=[s for s in p['scenes'] if s['kind']==kind]
  if kind=='archive':candidates.sort(key=lambda s:checks[assets[s['asset_id']]['video']]['bytes'])
  s=copy.deepcopy(candidates[0]);s.update(id='portable-'+kind,start=0,end=1.1,duration=1.1)
  if kind in ['archive','map']:s['source_in']=0
  scenes.append(s)
 needed={prefix+'assets/maps/europe.geojson',prefix+'assets/manifest.json',prefix+'audio/voiceover.mp3'}
 needed|={prefix+'assets/flags/'+x+'-flag.png' for x in ['in','pk']}
 for s in scenes:
  keys=[x[0] for x in s['sides']] if s['kind']=='compare' else [s['asset_id']] if s['kind'] in ['turntable','photo','archive','map'] else []
  for key in keys:needed.add(prefix+assets[key]['video' if s['kind'] in ['turntable','archive','map'] else 'photo'])
 for n in names:
  rel=n[len(prefix):] if n.startswith(prefix) else ''
  shared=not n.startswith('video-studio/episodes/')
  code_or_metadata=rel and not rel.startswith(('assets/','audio/','output/'))
  if shared or code_or_metadata or n in needed:z.extract(n,args.extract)
B=args.extract/prefix;sys.path.insert(0,str(B));from render_episode import Renderer
r=Renderer(args.extract/'portable-smoke');samples=[]
for s in scenes:
 f=r.scene(s);v=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=width,height,nb_frames,r_frame_rate','-of','json',str(f)]))['streams'][0];assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'30/1',33);samples.append(dict(kind=s['kind'],frames=33,status='passed'));print('PORTABLE_RENDER',s['kind'],flush=True)
report=dict(status='passed',method='All ZIP media hashes verified by streaming; independent sparse extraction of code/fonts/voice and representative media; ten scene kinds rendered using only extracted files. Sparse extraction saves disk and does not skip any ZIP asset integrity check.',selected_asset_hashes_checked=len(checks),source_render_sha256=hashlib.sha256((B/'render_episode.py').read_bytes()).hexdigest(),samples=samples)
args.report.write_text(json.dumps(report,indent=2)+'\n');print('PORTABLE_PROJECT_PASSED',flush=True)
