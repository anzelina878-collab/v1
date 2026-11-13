import urllib.request,zipfile,json,os
from pathlib import Path
from PIL import Image
BASE=Path(__file__).resolve().parents[1]
CACHE=Path(os.environ.get('ARSENAL_PREP_CACHE','/tmp/arsenal-008'));CACHE.mkdir(parents=True,exist_ok=True)
p=BASE/'assets/maps';(p/'dem').mkdir(parents=True,exist_ok=True)
def get(u,f):
 if f.exists():return
 with urllib.request.urlopen(u,timeout=120) as r,f.open('wb') as w:
  while b:=r.read(1048576):w.write(b)
 print(f.name,flush=True)
get('https://naciscdn.org/naturalearth/50m/raster/NE2_50M_SR_W.zip',CACHE/'naturalearth.zip')
with zipfile.ZipFile(CACHE/'naturalearth.zip') as z:
 name=next(n for n in z.namelist() if n.endswith('.tif'));dst=CACHE/'surface.tif'
 if not dst.exists():
  with z.open(name) as r,dst.open('wb') as w:
   while b:=r.read(1048576):w.write(b)
 im=Image.open(dst);w,h=im.size
 im.crop(((75+180)/360*w,(90-55)/180*h,(153+180)/360*w,(90-15)/180*h)).resize((3120,1600)).save(p/'surface-region.png')
for x in range(11,15):
 for y in range(5,8):get(f'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/4/{x}/{y}.png',p/'dem'/f'4-{x}-{y}.png')
get('https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson',p/'europe.geojson')
get('https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_boundary_lines_disputed_areas.geojson',p/'disputed.geojson')
(p/'SOURCES.md').write_text('Natural Earth shaded relief NE2 1:50m and country/disputed-boundary vectors: public domain, https://www.naturalearthdata.com/about/terms-of-use/ .\nTerrain Terrarium tiles: https://registry.opendata.aws/terrain-tiles/ . Mapzen attribution: https://github.com/tilezen/joerd/blob/master/docs/attribution.md . Source terrain uses NASA/USGS/NOAA public datasets; elevations exaggerated for legibility.\nDisputed boundaries are an overview, not a statement of territorial sovereignty. No downloaded map video or third-party software watermark is used. Map animation rendered from actual elevation mesh in this project.\n')
