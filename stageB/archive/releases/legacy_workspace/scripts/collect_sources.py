"""Read-only public database retrieval; caches every response for offline audit."""
import csv, json, urllib.request, urllib.parse, time, concurrent.futures
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'sources'; CACHE.mkdir(parents=True,exist_ok=True)
DATA=Path('C:/Users/dakshant/Downloads/cookchem_master_expanded_round11.csv')
rows=list(csv.DictReader(DATA.open(encoding='utf-8-sig')))
groups={}
for r in rows: groups.setdefault(r['Canonical_Molecular_ID'],[]).append(r)
def get(url,path):
    if path.exists(): return json.loads(path.read_text(encoding='utf-8'))
    for attempt in range(3):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'CookRisk-academic-evidence-mapping/1.0'})
            with urllib.request.urlopen(req,timeout=35) as response: result=json.load(response)
            path.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8'); return result
        except Exception as e:
            if attempt==2: return {'retrieval_error':str(e),'url':url}
            time.sleep(1+attempt)
def work(item):
    key,rs=item; name=next((r['Canonical_Compound_Name'] for r in rs if r['Canonical_Compound_Name']),rs[0]['Compound_Name'])
    # No name-based merging. Search all CookRisk groups, including unresolved groups.
    query='TITLE_ABS:"'+name.replace('"','')+'" AND (TITLE_ABS:"drug interaction" OR TITLE_ABS:pharmacokinetic OR TITLE_ABS:cytochrome OR TITLE_ABS:transporter OR TITLE_ABS:"enzyme inhibition" OR TITLE_ABS:"drug absorption")'
    url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':query,'format':'json','resultType':'core','pageSize':25})
    payload=get(url,CACHE/(key.replace(':','_')+'_search.json'))
    cids=sorted({r[c].split('.')[0] for r in rs for c in ['Resolved_PubChem_CID','PubChem_CID_Resolved','PubChem_CID'] if r[c]})
    for cid in cids:
        u=f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/Title,MolecularFormula,InChI,InChIKey,ConnectivitySMILES,SMILES/JSON'
        p=CACHE/('pubchem_'+cid+'.json'); result=get(u,p)
        if 'retrieval_error' in result: p.write_text(json.dumps(result),encoding='utf-8')
    return {'Canonical_Molecular_ID':key,'search_name':name,'query':query,'source_url':url,'search_date':'2026-10-06','hit_count':payload.get('hitCount',''),'retrieval_status':'error' if 'retrieval_error' in payload else 'retrieved','screening_status':'awaiting_manual_screening'}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool: log=list(pool.map(work,groups.items()))
with (ROOT/'sources/search_log.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(log[0])); w.writeheader(); w.writerows(log)
print('Retrieved searches:',len(log),'errors:',sum(r['retrieval_status']=='error' for r in log))
