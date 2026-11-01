"""Check actual encoded motion: locked photos, partial angles and no position jumps."""
import argparse,json,subprocess,sys
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from render_revision_v3 import Renderer

def frame(f,t):
 return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(t),'-i',str(f),'-frames:v','1','-vf','scale=320:180','-pix_fmt','rgb24','-f','rawvideo','-']),np.uint8).reshape(180,320,3)
def main():
 p=argparse.ArgumentParser();p.add_argument('--compiled',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();r=Renderer(a.compiled);photos=[];models=[]
 for s in r.project['scenes']:
  f=a.compiled/s['id']/'scene.mp4'
  if s['kind']=='photo':
   x=frame(f,.1).astype(float);y=frame(f,max(.1,s['duration']-.1)).astype(float);diff=float(np.abs(x-y).mean());assert diff<1.0,(s['id'],diff)
   # Static H264 I/P frames can differ by quantization. Check geometric
   # translation separately instead of mistaking tiny codec noise for motion.
   f1=np.fft.fft2(x[:135].mean(-1));f2=np.fft.fft2(y[:135].mean(-1));cross=f1*np.conj(f2);cross/=np.maximum(np.abs(cross),1e-9);phase=np.fft.ifft2(cross).real;peak=np.unravel_index(np.argmax(phase),phase.shape);assert peak==(0,0),(s['id'],peak)
   photos.append({'id':s['id'],'encoded_mae':diff,'encoded_translation_peak_yx':[int(v) for v in peak]})
  elif s['kind']=='turntable':
   asset=r.assets[s['asset_id']];t=min(2.0,s['duration']-.15);actual=frame(f,t);expected=frame(BASE/asset['video'],min(asset['duration']-.1,t*asset['duration']/24));diff=float(np.abs(actual[:135].astype(float)-expected[:135]).mean());assert diff<8,(s['id'],diff)
   raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-i',str(f),'-t',str(min(3,s['duration'])),'-vf','scale=320:180','-pix_fmt','rgb24','-f','rawvideo','-']);arr=np.frombuffer(raw,np.uint8).reshape(-1,180,320,3)[:,:135];mask=(np.abs(arr.astype(np.int16)-np.array([242,243,240])).max(-1)>45).astype(float);weights=mask.sum((1,2));assert np.all(weights>0)
   xx=np.arange(320)[None,None,:];yy=np.arange(135)[None,:,None];centers=np.stack([(mask*xx).sum((1,2))/weights,(mask*yy).sum((1,2))/weights],1);steps=np.linalg.norm(np.diff(centers,axis=0),axis=1);maximum=float(steps.max());assert maximum<3,(s['id'],maximum)
   models.append({'id':s['id'],'expected_source_pose_mae':diff,'max_subject_centroid_step_at_320px':maximum,'degrees_per_second':15,'one_revolution_seconds':24})
 report={'status':'passed','locked_photo_checks':photos,'rotating_model_checks':models,'review_scope':'Encoded measurements and sampled frame sequences; no claim of uninterrupted human playback'};a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2));print('MOTION_VERIFIED',len(photos),'photos',len(models),'3D plans',flush=True)
if __name__=='__main__':main()
