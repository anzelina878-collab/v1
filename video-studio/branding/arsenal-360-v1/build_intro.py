"""Reusable six-second military mosaic ident. Original typography/animation.
Only the channel name, timing, grid and source folder are configured in JSON.
Dependencies: Pillow + numpy; FFmpeg/FFprobe on PATH. No online service needed.
"""
import argparse,hashlib,json,math,subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageEnhance,ImageChops


def smooth(x):
    x=max(0.,min(1.,x));return x*x*(3-2*x)


def layout(columns,rows,seed,source_count):
    rng=np.random.default_rng(seed);occupied=np.zeros((rows,columns),bool);tiles=[]
    for y in range(rows):
        for x in range(columns):
            if occupied[y,x]:continue
            size=int(rng.choice([1,2,3],p=[.82,.16,.02]))
            while size>1 and (x+size>columns or y+size>rows or occupied[y:y+size,x:x+size].any()):size-=1
            occupied[y:y+size,x:x+size]=True
            # Balanced source use; phases differ across the wall.
            source=(len(tiles)*7+int(rng.integers(source_count)))%source_count
            tiles.append({'x':x,'y':y,'size':size,'source':source,'phase':int(rng.integers(96))})
    return tiles


class Ident:
    def __init__(self,config):
        self.path=config.resolve();self.base=self.path.parent;self.p=json.loads(config.read_text())
        self.w,self.h=self.p['width'],self.p['height'];self.fps=self.p['fps'];self.duration=self.p['duration']
        if (self.w,self.h)!=(1920,1080):raise ValueError('This ident master is 1920x1080; scale only the encoded export')
        if self.duration!=6 or self.fps!=30:raise ValueError('Keep the requested 6 seconds / 30 fps')
        self.files=sorted((self.base/self.p['assets']).glob('*.mp4'))
        if len(self.files)<4:raise ValueError('At least four reviewed video sources required')
        self.tile_w=self.w//self.p['columns'];self.tile_h=self.h//self.p['rows']
        if self.w%self.p['columns'] or self.h%self.p['rows']:raise ValueError('Grid must divide master dimensions')
        self.tiles=layout(self.p['columns'],self.p['rows'],self.p['seed'],len(self.files))
        self.frames=[]
        for file in self.files:
            data=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-i',str(file),'-t','8','-vf','fps=12,scale=240:136','-an','-f','rawvideo','-pix_fmt','rgb24','-threads','1','pipe:1'])
            n=len(data)//(240*136*3)
            if n<36:raise ValueError('Source too short: '+str(file))
            frames=[]
            for i in range(n):
                im=Image.frombytes('RGB',(240,136),data[i*240*136*3:(i+1)*240*136*3])
                im=ImageEnhance.Color(im).enhance(.66);im=ImageEnhance.Contrast(im).enhance(1.12)
                frames.append(im)
            self.frames.append(frames)
            print('DECODED',file.name,n,flush=True)
        # All three tile sizes cached; no per-frame large-source resizing.
        self.cache={}
        for source,frames in enumerate(self.frames):
            for size in [1,2,3]:
                self.cache[source,size]=[im.resize((self.tile_w*size-2,self.tile_h*size-2),Image.Resampling.LANCZOS) for im in frames]
        self.make_title()
        yy,xx=np.mgrid[0:self.h,0:self.w];self.xx=xx.astype(np.float32);self.yy=yy.astype(np.float32)
        radius=((self.xx-self.w/2)/(self.w*.72))**2+((self.yy-self.h/2)/(self.h*.88))**2
        self.vignette=np.clip(1-.30*radius,.55,1).astype(np.float32)
        self.central=np.exp(-(((self.xx-self.w/2)/(self.w*.52))**2+((self.yy-self.h/2)/(self.h*.37))**2)*1.8).astype(np.float32)
        rng=np.random.default_rng(self.p['seed']+2);self.grain=rng.normal(0,1.8,(self.h,self.w)).astype(np.float32)

    def make_title(self):
        font_path=self.base/self.p['font'];size=300
        while True:
            font=ImageFont.truetype(str(font_path),size);box=font.getbbox(self.p['title'],stroke_width=1)
            if box[2]-box[0]<=1800:break
            size-=1
        mask=Image.new('L',(self.w,self.h));d=ImageDraw.Draw(mask)
        x=(self.w-(box[2]-box[0]))/2-box[0];y=(self.h-(box[3]-box[1]))/2-box[1]+5
        d.text((x,y),self.p['title'],font=font,fill=255,stroke_width=1)
        self.title_mask=np.asarray(mask).astype(np.float32)/255
        self.glow=np.asarray(mask.filter(ImageFilter.GaussianBlur(11))).astype(np.float32)/255
        self.edge=np.asarray(mask.filter(ImageFilter.MaxFilter(7))).astype(np.float32)/255
        self.shadow=np.asarray(mask.filter(ImageFilter.GaussianBlur(20))).astype(np.float32)/255
        self.font_size=size;self.title_box=mask.getbbox()
        clean=Image.new('RGBA',(self.w,self.h),(255,255,255,0));clean.putalpha(mask)
        clean.save(self.base/'output/logo_white.png')

    def frame(self,t):
        mosaic=Image.new('RGB',(self.w,self.h),'#070D12')
        for tile in self.tiles:
            source=tile['source'];seq=self.cache[source,tile['size']]
            index=(int(t*12)+tile['phase'])%len(seq)
            mosaic.paste(seq[index],(tile['x']*self.tile_w+1,tile['y']*self.tile_h+1))
        # Slow dolly out across the whole wall, with safe overscan at every time.
        progress=smooth(t/3.8);zoom=1.12-.093*progress
        dx=8*math.sin(t*.57);dy=4*math.cos(t*.4)
        matrix=(1/zoom,0,(self.w-self.w/zoom)/2+dx,0,1/zoom,(self.h-self.h/zoom)/2+dy)
        mosaic=mosaic.transform((self.w,self.h),Image.Transform.AFFINE,matrix,Image.Resampling.BICUBIC)
        a=np.asarray(mosaic).astype(np.float32)
        dark=smooth((t-.55)/2.0)
        light=self.vignette*(.89-.13*dark-.10*dark*self.central)
        a*=light[:,:,None];a[:,:,0]*=1.035;a[:,:,2]*=.985
        # Diagonal cut, staggered in fine horizontal bands, reveals the real font.
        reveal=smooth((t-self.p['reveal_start'])/(self.p['reveal_end']-self.p['reveal_start']))
        cut=-300+reveal*(self.w+600)+(self.yy-self.h/2)*.26
        band=(np.floor(self.yy/23)%4-1.5)*8*(1-reveal)
        gate=np.clip((cut+band-self.xx)/8+.5,0,1)
        if reveal>=.9999:gate=np.ones_like(gate)
        alpha=self.title_mask*gate
        shadow=self.shadow*gate*.74
        a*=1-shadow[:,:,None]
        glow=self.glow*gate*(.90-.35*smooth((t-2.7)/.8))
        a+=glow[:,:,None]*np.array([190,76,10],np.float32)
        # Hot cutting edge only during reveal; no full-screen flashes.
        hot=np.clip(1-np.abs(self.xx-cut-band)/11,0,1)*self.edge*(1 if .02<reveal<.99 else 0)
        a+=hot[:,:,None]*np.array([150,65,8],np.float32)
        etched=((self.xx.astype(np.int32)%80<1)|(self.yy.astype(np.int32)%45<1)).astype(np.float32)*10
        white=np.clip(251+self.grain-etched,228,255)
        a=a*(1-alpha[:,:,None])+white[:,:,None]*alpha[:,:,None]
        a=np.clip(a,0,255).astype(np.uint8);im=Image.fromarray(a)
        if .03<reveal<.97:
            draw=ImageDraw.Draw(im);rng=np.random.default_rng(self.p['seed']+int(t*30))
            for _ in range(12):
                sy=int(rng.integers(400,690));sx=int(cut[sy,0]+band[sy,0]+rng.normal(0,22))
                if 0<sx<self.w and self.edge[sy,sx]>.02:
                    draw.line((sx,sy,sx+int(rng.integers(4,18)),sy-int(rng.integers(2,11))),fill=(255,173,65),width=1)
        return im


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,default=Path(__file__).with_name('intro.json'));p.add_argument('--preview-only',action='store_true');a=p.parse_args()
    out=a.config.resolve().parent/'output';out.mkdir(exist_ok=True)
    ident=Ident(a.config);times=[0,.75,1.25,1.75,2.3,2.9,4.2,5.9667]
    sheet=Image.new('RGB',(1280,4*382),'#10161B');d=ImageDraw.Draw(sheet)
    for i,t in enumerate(times):
        im=ident.frame(t);im.resize((640,360),Image.Resampling.LANCZOS)
        sheet.paste(im.resize((640,360),Image.Resampling.LANCZOS),(i%2*640,i//2*382));d.text((i%2*640+8,i//2*382+364),f'{t:.2f}s',fill='white')
        if t in [1.75,2.9,5.9667]:im.save(out/f'frame-{t:.2f}.jpg',quality=95)
    sheet.save(out/'storyboard.jpg',quality=92)
    if a.preview_only:return
    target=ident.base/ident.p['output'];frames=round(ident.duration*ident.fps)
    cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','18','-threads','2','-pix_fmt','yuv420p','-movflags','+faststart',str(target)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    for f in range(frames):
        proc.stdin.write(ident.frame(f/ident.fps).tobytes())
        if f%30==0:print('FRAME',f,'/',frames,flush=True)
    proc.stdin.close()
    if proc.wait():raise RuntimeError('Encode failed')
    meta={'title':ident.p['title'],'duration':ident.duration,'frames':frames,'fps':ident.fps,'width':ident.w,'height':ident.h,'mosaic_windows':len(ident.tiles),'unique_video_sources':len(ident.files),'background':'actual moving video excerpts, repeated at different time offsets','audio':'none, visual ident only','font_size':ident.font_size,'title_box':ident.title_box,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'configuration':ident.p,'layout':ident.tiles}
    (out/'render.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2));print('INTRO_READY',target,flush=True)

if __name__=='__main__':main()
