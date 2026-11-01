from pathlib import Path
import sys
if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
import urllib.request,urllib.parse,json,csv,concurrent.futures
O=Path(__file__).resolve().parent
CANDIDATES=['(+)-Catechin','(-)-Epicatechin','Morin','Baicalein','Hesperetin','Rutin','6-Gingerol','Thymoquinone','Eugenol','Cinnamaldehyde','Carvacrol','Thymol','Pterostilbene','Ursolic acid','Oleanolic acid','Glycyrrhizin','Glycyrrhetinic acid','Diallyl sulfide','Diallyl disulfide','Diallyl trisulfide','Allicin','Bergapten','Diosmin','Hesperidin']
def slug(n):return n.lower().replace(' ','_').replace('/','_')
def get(u,p):
 if p.exists():return json.loads(p.read_text(encoding='utf8'))
 try:
  with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'CookRisk/6 evidence audit'}),timeout=40) as f:d=json.load(f)
 except Exception as ex:d={'retrieval_error':str(ex),'url':u}
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8');return d
def search(n):
 q=f'TITLE:"{n}" AND (drug OR pharmacokinetic OR interaction OR coadministration) AND FIRST_PDATE:[1900-01-01 TO 2026-10-14]'
 u='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(dict(query=q,format='json',resultType='core',pageSize=100))
 p=O/'sources'/('search_'+slug(n)+'.json');d=get(u,p)
 return dict(Candidate=n,Query=q,URL=u,Date='2026-10-14',Hits=d.get('hitCount',''),Retrieved=len(d.get('resultList',{}).get('result',[])),Cache=str(p.relative_to(O)),Scope='First 100 discovery records; not exhaustive')
def identity(n):
 return get('https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/'+urllib.parse.quote(n,safe='')+'/property/IUPACName,MolecularFormula,InChI,InChIKey,CanonicalSMILES/JSON',O/'sources'/('identity_'+slug(n)+'.json'))
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:rows=list(pool.map(search,CANDIDATES));list(pool.map(identity,CANDIDATES))
 with (O/'outputs/search_log.csv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 for n in CANDIDATES:
  hits=json.loads((O/'sources'/('search_'+slug(n)+'.json')).read_text(encoding='utf8')).get('resultList',{}).get('result',[])
  print('\n'+n)
  # Human priority, then earliest primary reports for manual screening.
  hits.sort(key=lambda x:('human' not in x.get('abstractText','').lower(),x.get('pubYear','')))
  for h in hits[:8]:print(h.get('id'),h.get('title'))
