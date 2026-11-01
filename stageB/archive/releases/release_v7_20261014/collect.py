from pathlib import Path
import json,csv,urllib.request,urllib.parse,concurrent.futures,sys
sys.dont_write_bytecode=True
if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf8')
O=Path(__file__).resolve().parent
for n in ['sources','outputs','inputs','reports','audit']:(O/n).mkdir(exist_ok=True)
CANDIDATES=['Diosmetin','Rutin','Pterostilbene','Ursolic acid','Oleanolic acid','Sesamin','Sesamolin','Theaflavin','Epicatechin gallate','Epigallocatechin','Gallocatechin','Catechin gallate',"6,7-Dihydroxybergamottin",'Bergaptol','Theobromine','Lycopene','Ascorbic acid','Phylloquinone','Folic acid','Astaxanthin','Lutein','Zeaxanthin','Beta-carotene','Nobiletin','Tangeretin','Chlorophyllin','Sulforaphene','Isothiocyanate','Vanillin','Hydroxytyrosol','Oleuropein','Allyl isothiocyanate']
def slug(n):return n.lower().replace(' ','_').replace(',','').replace('/','_')
def get(u,p):
 if p.exists():return json.loads(p.read_text(encoding='utf8'))
 try:
  with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'CookRiskStageB/7'}),timeout=45) as f:d=json.load(f)
 except Exception as ex:d={'retrieval_error':str(ex),'url':u}
 p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf8');return d
def search(arg):
 n,kind=arg
 q=f'TITLE:"{n}" AND (pharmacokinetic OR interaction OR coadministration OR metabolism OR synergistic) AND SRC:MED NOT PUB_TYPE:Review AND FIRST_PDATE:[1900-01-01 TO '+('2020-12-31]' if kind=='historical' else '2026-10-14]')
 u='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(dict(query=q,format='json',resultType='core',pageSize=100))
 p=O/'sources'/(kind+'_'+slug(n)+'.json');d=get(u,p)
 return dict(Candidate=n,Search=kind,Date='2026-10-14',Query=q,URL=u,Hits=d.get('hitCount',''),Retrieved=len(d.get('resultList',{}).get('result',[])),Cache=p.relative_to(O).as_posix(),Scope='Capped first 100 results; not fully screened')
def exact(pmid):
 u='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(dict(query=f'EXT_ID:{pmid} AND SRC:MED',format='json',resultType='core'))
 d=get(u,O/'sources'/('pmid_'+pmid+'.json'));hits=d.get('resultList',{}).get('result',[])
 if hits and hits[0].get('doi'):get('https://api.crossref.org/works/'+urllib.parse.quote(hits[0]['doi'],safe=''),O/'sources'/('crossref_'+pmid+'.json'))
 return d
def identity(n):
 return get('https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/'+urllib.parse.quote(n,safe='')+'/property/IUPACName,MolecularFormula,InChI,InChIKey,CanonicalSMILES/JSON',O/'sources'/('identity_'+slug(n)+'.json'))
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:rows=list(pool.map(search,[(n,k) for n in CANDIDATES for k in ['broad','historical']]));list(pool.map(identity,CANDIDATES))
 with (O/'outputs/search_log.csv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 print('Queries',len(rows),'occurrences',sum(x['Retrieved'] for x in rows))
