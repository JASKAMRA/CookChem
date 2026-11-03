from pathlib import Path
import csv,json,urllib.request,urllib.parse,concurrent.futures,sys
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;B=O.parent;V=B/'release_v7_20261015_clean'
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def get(u,p):
 if p.exists():return json.loads(p.read_text(encoding='utf8'))
 try:
  with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'CookRiskStageBQuality/8'}),timeout=45) as f:d=json.load(f)
 except Exception as ex:d={'retrieval_error':str(ex),'url':u}
 p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf8');return d
def primary(p):
 u='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(dict(query=f'EXT_ID:{p} AND SRC:MED',format='json',resultType='core'))
 return get(u,O/'sources'/('pmid_'+p+'.json'))
def identity(r):
 cid=r['PubChem_CID'];return get(f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/InChI,InChIKey,MolecularFormula,CanonicalSMILES/JSON',O/'sources'/('identity_'+cid+'.json'))
def full(p):
 h=primary(p).get('resultList',{}).get('result',[])
 if not h or not h[0].get('pmcid'):return dict(PMID=p,PMCID='',Status='No PMC identifier in current MED metadata')
 pmc=h[0]['pmcid'];path=O/'sources'/(pmc+'.xml');u=f'https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextXML'
 if path.exists():return dict(PMID=p,PMCID=pmc,Status='Retrieved public XML; verification requires manual review')
 try:
  with urllib.request.urlopen(u,timeout=45) as f:path.write_bytes(f.read())
  state='Retrieved public XML; verification requires manual review'
 except Exception as ex:state=str(ex)
 return dict(PMID=p,PMCID=pmc,Status=state)
if __name__=='__main__':
 e=read(V/'outputs/stageB_food_drug_interactions_v7.csv');r=read(V/'outputs/compound_registry.csv')
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:list(pool.map(primary,sorted({x['PMID'] for x in e})));list(pool.map(identity,r))
 priority=['21870106','24398010','22725836','10606838','16236038','2729942','28533679','22300367','20716633','23153560','22114872','21482950','4091996','24369535','12756512','24871039','23883365','21704146','16133554','26396928']
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:logs=list(pool.map(full,priority))
 with (O/'outputs/full_text_access_log.csv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(logs[0]));w.writeheader();w.writerows(logs)
 for x in logs:print(x)
