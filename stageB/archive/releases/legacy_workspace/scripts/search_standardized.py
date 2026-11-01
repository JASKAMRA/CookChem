import csv,json,urllib.request,urllib.parse,concurrent.futures
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((ROOT/'outputs/stageB_compound_mapping.csv').open(encoding='utf-8')))
def work(r):
    key=r['Canonical_Molecular_ID']; name=r['standardized_compound_name']
    query=f'TITLE_ABS:"{name}" AND (TITLE_ABS:drug OR TITLE_ABS:pharmacokinetic OR TITLE_ABS:pharmacodynamic OR TITLE_ABS:absorption OR TITLE_ABS:metabolism OR TITLE_ABS:transporter) AND FIRST_PDATE:[* TO 2026-10-06]'
    url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':query,'format':'json','resultType':'core','pageSize':25})
    p=ROOT/'sources'/(key.replace(':','_')+'_standardized_search.json')
    if not p.exists():
        try:
            with urllib.request.urlopen(url,timeout=35) as response: x=json.load(response)
        except Exception as e:x={'retrieval_error':str(e)}
        p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
    x=json.loads(p.read_text(encoding='utf-8'))
    return {'Canonical_Molecular_ID':key,'standardized_compound_name':name,'query':query,'source_url':url,'search_date':'2026-10-06','hit_count':x.get('hitCount',''),'retrieval_status':'error' if 'retrieval_error' in x else 'retrieved','screening_status':'not_exhaustively_screened','cache':p.relative_to(ROOT).as_posix()}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool: log=list(pool.map(work,[r for r in rows if r['standardized_compound_name']]))
with (ROOT/'outputs/stageB_standardized_search_log.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(log[0]));w.writeheader();w.writerows(log)
print('Standardized searches',len(log),'errors',sum(r['retrieval_status']=='error' for r in log))
