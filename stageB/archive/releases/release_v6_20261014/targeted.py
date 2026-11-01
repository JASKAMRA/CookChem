from collect import *
def run(n):
 q=f'TITLE:"{n}" AND (TITLE:pharmacokinetic OR TITLE:interaction OR TITLE:bioavailability OR TITLE:metabolism) AND FIRST_PDATE:[1900-01-01 TO 2020-12-31] AND SRC:MED NOT PUB_TYPE:Review'
 u='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(dict(query=q,format='json',resultType='core',pageSize=100))
 p=O/'sources'/('target_'+slug(n)+'.json');d=get(u,p)
 return dict(Candidate=n,Query=q,URL=u,Date='2026-10-14',Hits=d.get('hitCount',''),Retrieved=len(d.get('resultList',{}).get('result',[])),Cache=str(p.relative_to(O)),Scope='Historical primary title search; cap 100')
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:rows=list(pool.map(run,CANDIDATES))
 with (O/'outputs/targeted_search_log.csv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 for n in CANDIDATES:
  print('\n'+n)
  for h in json.loads((O/'sources'/('target_'+slug(n)+'.json')).read_text(encoding='utf8')).get('resultList',{}).get('result',[]):print(h.get('id'),h.get('title'))
