from pathlib import Path
import json,urllib.request,urllib.parse,concurrent.futures,hashlib,csv
O=Path(__file__).resolve().parent;R=O.parents[1]
for f in ['sources','outputs','audit','reports']:(O/f).mkdir(exist_ok=True)
def fetch(item):
    name,url=item;p=O/'sources'/name
    if p.exists():return
    try:
        with urllib.request.urlopen(url,timeout=40) as f:body=f.read()
        p.write_bytes(body)
    except Exception as e:(O/'sources'/(name+'.error.json')).write_text(json.dumps({'url':url,'error':str(e)}))
jobs=[(p+'.xml',f'https://www.ebi.ac.uk/europepmc/webservices/rest/{p}/fullTextXML') for p in ['PMC3863468','PMC3538144']]
jobs += [(p+'.xml',f'https://www.ebi.ac.uk/europepmc/webservices/rest/{p}/fullTextXML') for p in ['PMC11011382','PMC8151956']]
for pmid in ['22512082','18928093','24871039']:
    jobs.append((f'pmid_{pmid}.json','https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':f'EXT_ID:{pmid} AND SRC:MED','format':'json','resultType':'core'})))
V3=R/'stageB/expansion_v3_20261014'
warnings=json.loads((V3/'audit/validation_report.json').read_text())['warnings']
for warning in warnings:
    if warning['code']=='Crossref_lookup_unavailable':
        rows=list(csv.DictReader((V3/'outputs/study_registry.csv').open(encoding='utf-8-sig')))
        for row in rows:
            if row['PMID'] in warning['ids']:jobs.append((f"crossref_{row['PMID']}.json",'https://api.crossref.org/works/'+urllib.parse.quote(row['DOI'],safe='')))
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(fetch,jobs))
print('Retrieval attempts',len(jobs))
