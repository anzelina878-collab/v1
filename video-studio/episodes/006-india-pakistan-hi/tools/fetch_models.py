import os
from pathlib import Path
import urllib.request,json,re,shlex,sys
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'tools'));from convert_ac import convert
UA='Mozilla/5.0 (compatible; Arsenal360/1.0)'
def read(u):return urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':UA}),timeout=60).read()
for key,repo,model in [('rafale','RafaleB','RafaleB17.ac'),('mirage','Mirage-2000','m2000-5.ac')]:
 p=BASE/'assets/models'/key;p.mkdir(exist_ok=True);root='https://raw.githubusercontent.com/FGMEMBERS/'+repo+'/master/'
 try:
  raw=read(root+'Models/'+model);(p/'model.ac').write_bytes(raw);textures=list(dict.fromkeys(re.findall(r'^texture "([^"]+)"',raw.decode(errors='replace'),re.M)));mapping={};docs={}
  for n,name in enumerate(textures):
   try:
    b=read(root+'Models/'+name);local=f'texture-{n}'+Path(name).suffix;(p/local).write_bytes(b);mapping[name]=local
   except Exception as e:print('MISSING_TEXTURE',key,name,e,flush=True)
  for name in ['COPYING','COPYING.txt','README','README.txt','Authors.txt']:
   try:doc=read(root+name);(p/name).write_bytes(doc);docs[name]=doc.decode(errors='replace')
   except:pass
  if not any('GENERAL PUBLIC LICENSE' in d for d in docs.values()):
   # Preserve the exact GPL distribution policy and license rather than invent author notices.
   license=read('https://raw.githubusercontent.com/FGMEMBERS/MiG-29/master/COPYING.txt');(p/'COPYING').write_bytes(license)
  source={'id':key,'repository':'https://github.com/FGMEMBERS/'+repo,'model_path':'Models/'+model,'texture_mapping':mapping,'documents':docs,'license':'GPL-2.0-or-later','license_basis':'FlightGear model distribution policy https://www.flightgear.org/about/policy/ ; upstream notices retained','modifications':'UV triangle conversion, studio lighting; flight simulator helper effects excluded. Rafale B family display, not claimed an exact Indian national livery.'}
  (p/'source.json').write_text(json.dumps(source,ensure_ascii=False,indent=2));convert(p);print('CONVERTED',key,flush=True)
 except Exception as e:print('FAILED',key,repr(e),flush=True)
