"""Produce compact encoded control sheets for all shots used in final concatenation."""
from pathlib import Path
import argparse,json,subprocess,io
from PIL import Image,ImageDraw
BASE=Path(__file__).resolve().parent

def main():
 p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);p.add_argument('--output',type=Path,default=BASE/'output/qa/encoded-controls');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True);ss=json.load(open(BASE/'episode.json'))['scenes'];records=[]
 for off in range(0,len(ss),24):
  im=Image.new('RGB',(1280,1212),'#152026');d=ImageDraw.Draw(im)
  for j,s in enumerate(ss[off:off+24]):
   t=min(s['duration']-.06,max(.04,min(s['duration']*.55,s.get('settle_after',1.2)+.5)));f=a.work/s['id']/'scene.mp4'
   data=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(t),'-i',str(f),'-frames:v','1','-vf','scale=320:180','-threads','1','-f','image2pipe','-vcodec','png','-']);image=Image.open(io.BytesIO(data));im.paste(image,(j%4*320,j//4*202));d.text((j%4*320+3,j//4*202+181),f"{s['id']} {s['start']:.2f}s +{t:.2f}",fill='white');records.append({'scene':s['id'],'global_start':s['start'],'local_sample':t,'sheet':f'encoded-{off//24:02d}.jpg'})
  out=a.output/f'encoded-{off//24:02d}.jpg';im.save(out,quality=90);print('ENCODED_SHEET',out,flush=True)
 (a.output/'index.json').write_text(json.dumps({'scope':'Sampled encoded controls; one reference frame for every scene. Final assembly copies these encoded streams. Static-frame and native-bank motion checks are separate. Continuous human watch/listen not performed.','frames':records},ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
