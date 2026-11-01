from collect import *
import xml.etree.ElementTree as ET
def retry(r):
 p=O/'sources'/('identity_'+r['PubChem_CID']+'.json');d=json.loads(p.read_text(encoding='utf8'))
 if d.get('PropertyTable'):return
 p.unlink();get('https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/'+r['PubChem_CID']+'/property/InChI,InChIKey/JSON',p)
def bioc(pmc):
 u=f'https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/{pmc}/unicode';p=O/'sources'/(pmc+'.bioc.xml')
 try:
  with urllib.request.urlopen(u,timeout=35) as f:raw=f.read()
  root=ET.fromstring(raw)
  if root.tag!='collection':raise ValueError('Response is not a BioC article collection')
  p.write_bytes(raw);state='Public BioC XML retrieved; manual verification pending'
 except Exception as ex:state=str(ex)
 return dict(PMCID=pmc,URL=u,Status=state)
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(retry,read(V/'outputs/compound_registry.csv')))
 ids=['PMC4898966','PMC3579260','PMC2014893','PMC1884944','PMC172463','PMC3402804','PMC2933312','PMC3538144','PMC3403202','PMC3090066','PMC1400816']
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(bioc,ids))
 with (O/'outputs/alternative_full_text_access_log.csv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 print(rows)
