import collect,csv,json,concurrent.futures,urllib.parse
O=collect.O
def search(name):
    q=f'TITLE:"{name}" AND (TITLE:pharmacokinetic OR TITLE:interaction OR TITLE:bioavailability OR TITLE:disposition) AND FIRST_PDATE:[1900-01-01 TO 2020-12-31]'
    url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':q,'format':'json','resultType':'core','pageSize':100})
    p=O/'sources'/('historical_'+name.lower().replace(' ','_')+'.json');d=collect.get(url,p)
    return dict(Candidate=name,Query=q,Date='2026-10-14',Database='Europe PMC',URL=url,Limit=100,Hits=d.get('hitCount',''),Retrieved=len(d.get('resultList',{}).get('result',[])),Cache=p.relative_to(O).as_posix(),Scope='Historical title-focused follow-up; not exhaustive screening')
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:logs=list(pool.map(search,collect.CANDIDATES))
with (O/'outputs/search_log.csv').open(encoding='utf-8-sig',newline='') as f:old=list(csv.DictReader(f))
with (O/'outputs/search_log.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(logs[0]));w.writeheader();w.writerows(old+logs)
print('Historical queries',len(logs))
