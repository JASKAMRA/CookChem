from collect import *
PMIDS=['20877134','18191104','31252064','30976185','30877660','30572191','27472952','26360766','32601017','32187570','27058921','27529203','24009877','27493101','28646810','26396928','15767232','688723','21482950','1828561','17110451','17666020']
def full(p):
 h=exact(p).get('resultList',{}).get('result',[])
 if not h:return
 pmc=h[0].get('pmcid')
 if not pmc:return
 path=O/'sources'/(pmc+'.xml')
 if path.exists():return
 u=f'https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextXML'
 try:
  with urllib.request.urlopen(u,timeout=45) as f:path.write_bytes(f.read())
 except Exception as ex:(O/'sources'/(pmc+'_access.json')).write_text(json.dumps(dict(URL=u,Error=str(ex))),encoding='utf8')
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:list(pool.map(full,PMIDS))
 for p in ['21482950','1828561','17110451','17666020']:
  h=exact(p)['resultList']['result'][0];print(p,h.get('pmcid'),h.get('abstractText',''))
