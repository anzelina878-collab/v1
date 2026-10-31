"""Fetch prepared episode video files listed by path + SHA-256 in its manifest.
No accounts or keys needed. Existing verified files are reused; partial files
never replace a valid clip. Only writes inside the supplied episode directory.
"""
import argparse,hashlib,json,time,urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def fetch(config):
    base=config.resolve().parent;p=json.loads(config.read_text());manifest=json.loads((base/p['external_media_manifest']).read_text())
    def one(item):
        target=(base/item['path']).resolve()
        if base not in target.parents:raise ValueError('Unsafe media path')
        if target.exists() and target.stat().st_size==item['bytes'] and digest(target)==item['sha256']:return 'CACHED '+item['path']
        if not item['url'].startswith('https://'):raise ValueError('Expected HTTPS source')
        target.parent.mkdir(exist_ok=True,parents=True);partial=target.with_suffix(target.suffix+'.partial')
        for attempt in range(3):
            try:
                req=urllib.request.Request(item['url'],headers={'User-Agent':'VideoStudio-MediaFetcher/1.0'})
                with urllib.request.urlopen(req,timeout=90) as r,partial.open('wb') as out:
                    while block:=r.read(1024*1024):out.write(block)
                if partial.stat().st_size!=item['bytes'] or digest(partial)!=item['sha256']:raise ValueError('Media checksum mismatch: '+item['path'])
                partial.replace(target);return 'FETCHED '+item['path']
            except Exception:
                partial.unlink(missing_ok=True)
                if attempt==2:raise
                time.sleep(attempt+1)
    with ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(one,manifest['files']):print(result,flush=True)
    print('ALL_EPISODE_MEDIA_VERIFIED',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('episode',type=Path);a=parser.parse_args();fetch(a.episode)
