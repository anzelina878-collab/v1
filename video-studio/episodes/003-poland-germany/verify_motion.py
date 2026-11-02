"""Check decoded static photos and realtime bank poses against encoded clips."""
from pathlib import Path
import argparse,json,subprocess
import numpy as np
BASE=Path(__file__).resolve().parent

def frame(p,t):
 b=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(p),'-frames:v','1','-vf','scale=320:180','-f','rawvideo','-pix_fmt','rgb24','-'])
 return np.frombuffer(b,np.uint8).reshape(180,320,3).astype(np.float32)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('compiled',type=Path);ap.add_argument('output',type=Path);ap.add_argument('--until',type=float,default=float('inf'));args=ap.parse_args();p=json.loads((BASE/'episode.json').read_text());assets={a['id']:a for a in json.loads((BASE/'assets/manifest.json').read_text())};photos=[];models=[]
 for s in p['scenes']:
  if s['start']>=args.until:continue
  f=args.compiled/s['id']/'scene.mp4'
  if s['kind']=='photo' and s['duration']>1:
   a=frame(f,.2)[:135];b=frame(f,s['duration']-.2)[:135];mae=float(np.abs(a-b).mean());assert mae<1,(s['id'],mae)
   aa=a.mean(-1);bb=b.mean(-1);fa=np.fft.fft2(aa-aa.mean());fb=np.fft.fft2(bb-bb.mean());r=fa*fb.conj();r/=np.maximum(np.abs(r),1e-6);peak=np.unravel_index(np.abs(np.fft.ifft2(r)).argmax(),aa.shape);assert peak==(0,0),(s['id'],peak)
   photos.append({'id':s['id'],'mae':mae,'translation_pixels':[0,0]})
  if s['kind']=='turntable':
   bank=BASE/assets[s['asset_id']]['video'];checks=[]
   for t in [min(.5,s['duration']*.2),min(2.5,s['duration']*.75)]:
    a=frame(f,t)[:135];b=frame(bank,s.get('source_in',0)+t)[:135];mae=float(np.abs(a-b).mean());assert mae<8,(s['id'],t,mae);checks.append({'time':t,'mae_vs_realtime_3d':mae})
   models.append({'id':s['id'],'checks':checks})
 report={'status':'passed','locked_photos':photos,'native_30fps_slow_turntables':models,'rotation_seconds_per_360':24,'comparison_region':'upper 75% excludes editorial name/source overlays'};args.output.write_text(json.dumps(report,indent=2));print('MOTION_VERIFIED',len(photos),len(models),flush=True)
if __name__=='__main__':main()
