from exact import *
if __name__=='__main__':
 for n in ['6-Gingerol','Carvacrol','Thymoquinone']:
  p=O/'sources'/('identity_'+slug(n)+'.json')
  if not json.loads(p.read_text(encoding='utf8')).get('PropertyTable'):p.unlink();identity(n)
 for p in ['38148345','20582416','10755708','29937536']:run(p)
 for pmid in ['38148345','20582416']:
  h=json.loads((O/'sources'/('pmid_'+pmid+'.json')).read_text(encoding='utf8'))['resultList']['result'][0];print(pmid,h['title'],h.get('abstractText',''))
 # Source XML is archived for access and correction review; not automatically a full-text verification claim.
 for pmid in ['33319311','33074419','38958374','37492094','34836412','29908072']:
  h=json.loads((O/'sources'/('pmid_'+pmid+'.json')).read_text(encoding='utf8'))['resultList']['result'][0]
  pmc=h.get('pmcid');print(pmid,pmc)
  if pmc:
   u=f'https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextXML';p=O/'sources'/(pmc+'.xml')
   try:
    with urllib.request.urlopen(u,timeout=40) as f:p.write_bytes(f.read())
   except Exception as ex:(O/'sources'/(pmc+'_access.json')).write_text(json.dumps(dict(url=u,error=str(ex))),encoding='utf8')
