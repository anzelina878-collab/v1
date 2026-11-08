from pathlib import Path
import urllib.request,json,re,sys
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'tools'));from convert_ac import convert
for key,repo,name in [('typhoon','Eurofighter','typhoon.ac'),('f35b','F-35B','F-35B.ac')]:
 p=B/'assets/models'/key;p.mkdir(exist_ok=True);root='https://raw.githubusercontent.com/FGMEMBERS/'+repo+'/master/'
 def get(s):return urllib.request.urlopen(root+s,timeout=60).read()
 try:
  raw=get('Models/'+name);(p/'model.ac').write_bytes(raw);mapping={};docs={}
  for i,t in enumerate(dict.fromkeys(re.findall(r'^texture "([^"]+)"',raw.decode(errors='replace'),re.M))):
   try:b=get('Models/'+t);n=f'texture-{i}'+Path(t).suffix;(p/n).write_bytes(b);mapping[t]=n
   except Exception as e:print('TEXTURE_FAIL',key,t,e,flush=True)
  for n in ['COPYING','COPYING.txt','License.txt','README','README.txt','Authors.txt']:
   try:b=get(n);(p/n).write_bytes(b);docs[n]=b.decode(errors='replace')
   except:pass
  if not any('GENERAL PUBLIC LICENSE' in v for v in docs.values()): (p/'COPYING').write_bytes((B/'assets/models/rafale/COPYING').read_bytes())
  source={'id':key,'repository':'https://github.com/FGMEMBERS/'+repo,'model_path':'Models/'+name,'texture_mapping':mapping,'documents':docs,'license':'GPL-3.0' if key=='f35b' else 'GPL-2.0','license_basis':'https://www.flightgear.org/about/policy/ ; upstream notices retained','modifications':'AC3D mesh conversion and studio display, simulator effects omitted'};(p/'source.json').write_text(json.dumps(source,indent=2));convert(p)
 except Exception as e:print('FAIL',key,e,flush=True)
