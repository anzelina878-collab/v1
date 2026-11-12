"""Download the source media named by a portable plan, without paid services."""
import pathlib,json,urllib.request,urllib.error,concurrent.futures,time,subprocess,argparse
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--project',default='.');args=ap.parse_args();root=pathlib.Path(args.project).resolve()
 plan=json.loads((root/'plan.json').read_text());(root/'assets').mkdir(exist_ok=True)
 def get(a):
  dest=root/'assets'/(a['key']+'.mp4')
  if dest.exists() and dest.stat().st_size>1000:
   try:
    subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(dest)],stderr=subprocess.STDOUT)
    print('READY',a['key'],flush=True);return
   except subprocess.CalledProcessError:pass
  for attempt in range(4):
   try:
    req=urllib.request.Request(a['url'],headers={'User-Agent':'Mozilla/5.0'})
    tmp=dest.with_suffix('.download')
    with urllib.request.urlopen(req,timeout=90) as r,open(tmp,'wb') as f:
     while b:=r.read(1024*1024):f.write(b)
    subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(tmp)],stderr=subprocess.STDOUT)
    tmp.replace(dest);print('DOWNLOADED',a['key'],flush=True);return
   except Exception as e:
    if attempt==3:raise
    delay=int(e.headers.get('Retry-After','10')) if isinstance(e,urllib.error.HTTPError) and e.code==429 else 3*(attempt+1)
    print('RETRY',a['key'],type(e).__name__,flush=True);time.sleep(delay)
 with concurrent.futures.ThreadPoolExecutor(3) as ex:list(ex.map(get,plan['assets']))
if __name__=='__main__':main()
