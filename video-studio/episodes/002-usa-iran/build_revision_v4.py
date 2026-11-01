"""Chapter cards from episode 001's section template, aligned to recorded transitions."""
import json,copy
from pathlib import Path
BASE=Path(__file__).resolve().parent;FPS=30

def main():
 p=json.loads((BASE/'episode.v3.json').read_text());original=p['scenes'];duration=round(p['duration']*FPS)
 # Spoken bridge -> section title -> named equipment, without adding time to audio.
 specs=[('aviation',98.4,104.3666667,'АВІАЦІЯ'),('armor',320.5666667,326.1666667,'ТАНКИ ТА БРОНЕТЕХНІКА'),('missiles',469.1666667,475.4333333,'РАКЕТНЕ ОЗБРОЄННЯ'),('infantry',652.3666667,656.3666667,'ПІХОТНЕ ОЗБРОЄННЯ'),('artillery',712.5,717.0666667,'АРТИЛЕРІЯ'),('drones',798.3666667,803.3666667,'БЕЗПІЛОТНИКИ'),('air-defense',912.4333333,916.4333333,'ПРОТИПОВІТРЯНА ОБОРОНА'),('helicopters',1026.2333333,1029.2333333,'ВЕРТОЛЬОТИ'),('navy',1111.7666667,1115.7666667,'ВІЙСЬКОВО-МОРСЬКИЙ ФЛОТ'),('summary',1252.9666667,1258.5333333,'ПІДСУМОК')]
 inserts=[]
 for key,start,end,title in specs:inserts.append({'id':'v4-section-'+key,'kind':'section','start_frame':round(start*FPS),'end_frame':round(end*FPS),'title':title,'subtitle':'','settle_after':1.2})
 inserts+=[{'id':'v4-audience-question','kind':'question','start_frame':round(1377.22*FPS),'end_frame':round(1385.04*FPS),'title':'ЯКА КАТЕГОРІЯ НАЙЦІКАВІША?','nodes':['АВІАЦІЯ','РАКЕТИ','БЕЗПІЛОТНИКИ','ФЛОТ'],'settle_after':1.6},{'id':'v4-audience-comment','kind':'outro','start_frame':round(1385.04*FPS),'end_frame':round(1391.72*FPS),'title':'ВАША ДУМКА?','subtitle':'Арсенали яких країн порівняти далі?\nНапишіть у коментарях','settle_after':1.2}]
 boundaries=sorted({0,duration}|{round(s[k]*FPS) for s in original for k in ['start','end']}|{s[k] for s in inserts for k in ['start_frame','end_frame']});out=[]
 for start,end in zip(boundaries,boundaries[1:]):
  insert=next((s for s in inserts if s['start_frame']<=start<s['end_frame']),None)
  if insert:
   if out and out[-1]['id']==insert['id']:out[-1].update(end=end/FPS,duration=(end-round(out[-1]['start']*FPS))/FPS);continue
   s=copy.deepcopy(insert);s.pop('start_frame');s.pop('end_frame');s.update(start=start/FPS,end=end/FPS,duration=(end-start)/FPS,entrance_once=True)
  else:
   base=next(s for s in original if round(s['start']*FPS)<=start<round(s['end']*FPS));s=copy.deepcopy(base);s.update(start=start/FPS,end=end/FPS,duration=(end-start)/FPS,_base_id=base['id'],_base_offset_frames=start-round(base['start']*FPS));whole=start==round(base['start']*FPS) and end==round(base['end']*FPS)
   if not whole:s['id']=base['id']+'-v4-'+str(start)
   if s['kind']=='archive':s['source_in']=base.get('source_in',0)+s['_base_offset_frames']/FPS
  out.append(s)
 assert sum(round(s['duration']*FPS) for s in out)==duration
 assert len({s['id'] for s in out})==len(out)
 for a,b in zip(out,out[1:]):assert round(a['end']*FPS)==round(b['start']*FPS)
 for chapter,insert in zip(p['chapters'][1:],inserts):chapter['narration_start']=chapter['start'];chapter['start']=insert['start_frame']/FPS
 p.update(scenes=out,revision='v4-chapter-cards-and-audience-question',revision_notes='Episode 001 section/outro templates. Original narration, timing, slow 3D and locked photos preserved.');(BASE/'episode.v4.json').write_text(json.dumps(p,ensure_ascii=False,indent=2));print('V4_READY',len(out),'scenes',len(inserts),'title/question cards',flush=True)
 (BASE/'chapters.v4.uk.txt').write_text('\n'.join(f"{int(c['start'])//60:02d}:{int(c['start'])%60:02d} {c['title']}" for c in p['chapters'])+'\n')
if __name__=='__main__':main()
