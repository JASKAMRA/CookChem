from pathlib import Path
import json,csv,urllib.request,urllib.parse,concurrent.futures
O=Path(__file__).resolve().parent
for name in ['sources','outputs','audit','reports']:(O/name).mkdir(exist_ok=True)
CANDIDATES=['Myricetin','Luteolin','Ellagic acid','Gallic acid','Ferulic acid','Caffeic acid','Chlorogenic acid','Rosmarinic acid','Naringenin','Hesperetin','Bergamottin','Chrysin','Baicalein','Fisetin','Theobromine','Lycopene']
def get(url,p):
    if p.exists():return json.loads(p.read_text(encoding='utf8'))
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'CookRiskEvidenceResearch/5'}),timeout=50) as f:d=json.load(f)
    except Exception as e:d={'retrieval_error':str(e),'url':url}
    p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf8');return d
def search(name):
    q=f'TITLE:"{name}" AND (pharmacokinetic OR interaction OR coadministration OR bioavailability) AND FIRST_PDATE:[1900-01-01 TO 2026-10-14]'
    url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':q,'format':'json','resultType':'core','pageSize':100})
    p=O/'sources'/('search_'+name.lower().replace(' ','_')+'.json');d=get(url,p)
    return dict(Candidate=name,Query=q,Date='2026-10-14',Database='Europe PMC',URL=url,Limit=100,Hits=d.get('hitCount',''),Retrieved=len(d.get('resultList',{}).get('result',[])),Cache=p.relative_to(O).as_posix(),Scope='Capped first-page discovery; not exhaustive screening')
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:logs=list(pool.map(search,CANDIDATES))
with (O/'outputs/search_log.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(logs[0]));w.writeheader();w.writerows(logs)
def identity(name):
    p=O/'sources'/('identity_'+name.lower().replace(' ','_')+'.json')
    d=get('https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/'+urllib.parse.quote(name,safe='')+'/property/IUPACName,MolecularFormula,InChI,InChIKey,CanonicalSMILES/JSON',p)
    hits=d.get('PropertyTable',{}).get('Properties',[])
    if hits:
        cid=hits[0]['CID'];get(f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/synonyms/JSON',O/'sources'/('synonyms_'+name.lower().replace(' ','_')+'.json'))
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(identity,CANDIDATES))
print('Candidate queries',len(logs),'retrieved',sum(r['Retrieved'] for r in logs))
