"""Present portrait archive footage over a blurred copy of the same frames."""
import argparse,subprocess
from pathlib import Path
def main():
 p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('output',type=Path);p.add_argument('--start',type=float,default=0);p.add_argument('--duration',type=float,default=12);a=p.parse_args();a.output.parent.mkdir(parents=True,exist_ok=True)
 filt='[0:v]split[back][front];[back]scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,boxblur=30:2[back];[front]scale=-2:720[front];[back][front]overlay=(W-w)/2:0,setsar=1,fps=30[v]'
 subprocess.run(['ffmpeg','-y','-v','error','-xerror','-threads','1','-ss',str(a.start),'-i',str(a.input),'-t',str(a.duration),'-filter_complex',filt,'-filter_complex_threads','1','-map','[v]','-an','-c:v','libx264','-preset','veryfast','-crf','21','-threads','2','-pix_fmt','yuv420p','-movflags','+faststart',str(a.output)],check=True)
if __name__=='__main__':main()
