"""Collect public snapshots; never write outside this versioned release."""
from pathlib import Path
import csv,json,urllib.request,urllib.parse,hashlib,concurrent.futures,re
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parents[1]
DATE='2026-10-14'
for part in ['sources','outputs','reports','audit']:(OUT/part).mkdir(exist_ok=True,parents=True)
PMIDS=['23153560','24871039','24369535','18338336','12756512','19221726','21680781','25988261','22471240','11285356']
def fetch(url,path):
    if path.exists():return json.loads(path.read_text(encoding='utf8'))
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'CookRiskAcademicEvidenceAudit/3'})
        with urllib.request.urlopen(req,timeout=50) as f:data=json.load(f)
    except Exception as e:data={'retrieval_error':str(e),'url':url}
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf8');return data
def paper(pmid):
    url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':f'EXT_ID:{pmid} AND SRC:MED','format':'json','resultType':'core'})
    return pmid,fetch(url,OUT/'sources'/f'pmid_{pmid}.json')
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    papers=dict(pool.map(paper,PMIDS))
def doi(item):
    pmid,data=item;hits=data.get('resultList',{}).get('result',[])
    if not hits:return pmid,'missing_MED_record'
    d=hits[0].get('doi','')
    if not d:return pmid,'no_DOI'
    data=fetch('https://api.crossref.org/works/'+urllib.parse.quote(d,safe=''),OUT/'sources'/f'crossref_{pmid}.json')
    return pmid,'retrieved' if 'message' in data else 'lookup_unavailable'
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:print(dict(pool.map(doi,papers.items())))
for cid in ['5280343','5281708']:
    fetch(f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/IUPACName,MolecularFormula,InChI,InChIKey,CanonicalSMILES/JSON',OUT/'sources'/f'pubchem_{cid}.json')
    fetch(f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/synonyms/JSON',OUT/'sources'/f'pubchem_synonyms_{cid}.json')
queries=[]
for compound in ['sulforaphane','apigenin','kaempferol','daidzein','quercetin']:
    queries.append((compound,f'TITLE:{compound} AND (pharmacokinetic OR interaction OR CYP OR transporter) AND FIRST_PDATE:[1900-01-01 TO {DATE}]'))
def search(item):
    name,q=item;p=OUT/'sources'/f'search_{name}.json'
    url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':q,'format':'json','resultType':'core','pageSize':100})
    d=fetch(url,p);return {'Compound':name,'Query':q,'Database':'Europe PMC','Search_Date':DATE,'Hit_Count':d.get('hitCount',''),'Retrieved':len(d.get('resultList',{}).get('result',[])),'Cap':100,'Source_Cache':str(p.relative_to(OUT)),'Scope':'First page only; candidate retrieval not exhaustive screening'}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:logs=list(pool.map(search,queries))
for pmid,data in papers.items():logs.append({'Compound':'exact source verification','Query':f'EXT_ID:{pmid} AND SRC:MED','Database':'Europe PMC','Search_Date':DATE,'Hit_Count':data.get('hitCount',''),'Retrieved':len(data.get('resultList',{}).get('result',[])),'Cap':1,'Source_Cache':f'sources/pmid_{pmid}.json','Scope':'Targeted primary verification; two sources support selection or processing only'})
with (OUT/'outputs/literature_search_log.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(logs[0]));w.writeheader();w.writerows(logs)
print('Primary snapshots',len(papers),'and logged queries',len(logs))
