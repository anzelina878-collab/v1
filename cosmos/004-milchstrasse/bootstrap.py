import pathlib,json,urllib.request,http.cookiejar,zipfile,hashlib
R=pathlib.Path(__file__).resolve().parent
if not (R/'fonts/Lato-Bold.ttf').exists():
 cfg=json.load(open(R/'transfer.json'));u=cfg['source_url'];jar=http.cookiejar.CookieJar();op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
 with op.open(urllib.request.Request(u,headers={'Range':'bytes=0-31'}),timeout=60) as f:f.read(64)
 p=R/'visual_sources.zip'
 with op.open(u,timeout=180) as f,open(p,'wb') as out:
  while b:=f.read(1024*1024):out.write(b)
 assert hashlib.sha256(p.read_bytes()).hexdigest()==cfg['source_sha256']
 with zipfile.ZipFile(p) as z:z.extractall(R)
 p.unlink()
print('Public visual inputs verified')
