from pathlib import Path
import json,sys,subprocess,io,hashlib
import numpy as np
from PIL import Image,ImageDraw
import argparse
args=argparse.ArgumentParser();args.add_argument('--workspace',type=Path,required=True);args=args.parse_args()
B=Path(__file__).resolve().parents[1];T=args.workspace;Q=B/'output/qa';sys.path.insert(0,str(B));from render_episode import Renderer
from check_episode import frame,probe
p=json.load(open(B/'episode.json'));assets={a['id']:a for a in json.load(open(B/'assets/manifest.json'))};r=Renderer(T/'compiled');native=[];chapters=[]
for s in p['scenes']:
 if s['kind']!='turntable':continue
 bank=B/assets[s['asset_id']]['video'];v=next(x for x in probe(bank)['streams'] if x['codec_type']=='video');assert int(v['nb_frames'])==720 and v['r_frame_rate']=='30/1';samples=[]
 for t in [min(.4,s['duration']*.15),s['duration']*.5,s['duration']*.85]:
  ref=(s['source_in']+t)%24;mae=float(np.abs(frame(T/'compiled'/s['id']/'scene.mp4',t)[:135]-frame(bank,ref)[:135]).mean());assert mae<3,(s['id'],t,mae);samples.append({'local_time':t,'bank_time':ref,'model_area_mae':mae})
 native.append({'scene':s['id'],'native_frames':720,'revolution_seconds':24,'samples':samples});print('NATIVE_ENCODED',s['id'],flush=True)
(Q/'native-3d-motion.json').write_text(json.dumps({'status':'passed','method':'Three encoded poses per 3D scene compared to exact 720-frame / 24-second native bank at normal speed. Footer excluded. Actual licensed geometry, no optical-flow interpolation.','scenes':native},indent=2)+'\n')
for c in p['chapters'][1:]:
 s=next(s for s in p['scenes'] if s['kind']=='section' and s['start']<=c['spoken_start']<s['end']);local=c['spoken_start']-s['start'];actual=frame(T/'final_video_hi_v1.mp4',c['spoken_start']);ref=np.asarray(r.plate(s,2).resize((320,180))).astype(float);mae=float(np.abs(actual[58:108,25:295]-ref[58:108,25:295]).mean());assert mae<3,(s['id'],mae);chapters.append({'title':c['title'],'spoken_start':c['spoken_start'],'card_start':s['start'],'reveal_lead_seconds':round(local-.65,6),'fully_visible_title_area_mae':mae});print('CHAPTER_ENCODED',s['id'],flush=True)
(Q/'chapter-onsets.json').write_text(json.dumps({'status':'passed','method':'At each audio cue, decoded final movie title region compared to fully revealed intended title plate; cue from contextual forced word alignment. Summary written heading not spoken, so cue is first actual summary phrase.','chapters':chapters},ensure_ascii=False,indent=2)+'\n')
for off in range(0,len(p['scenes']),24):
 im=Image.new('RGB',(1280,1212),'#152026');draw=ImageDraw.Draw(im)
 for j,s in enumerate(p['scenes'][off:off+24]):
  t=s['start']+min(2,s['duration']*.55);raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(t),'-i',str(T/'final_video_hi_v1.mp4'),'-frames:v','1','-vf','scale=320:180','-threads','1','-f','image2pipe','-vcodec','png','-']);im.paste(Image.open(io.BytesIO(raw)),(j%4*320,j//4*202));draw.text((j%4*320+3,j//4*202+182),f"{s['id']} {t:.2f}s {s['kind']}",fill='white')
 f=Q/f'encoded-{off//24:02d}.jpg';im.save(f,quality=90);print('ENCODED_SHEET',f.name,flush=True)
print('ENCODED_CONTROLS_READY',flush=True)
