from collect import *
PMIDS=['12920504','34836412','15885265','16002304','20877134','28051355','33149871','33074419','33319311','24276478','12136947','27690733','17708066','12698306','18449511','29908072','38958374','35690339','22139695','21535728','38411783','37492094']
def run(pmid):
 u='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(dict(query=f'EXT_ID:{pmid} AND SRC:MED',format='json',resultType='core'))
 d=get(u,O/'sources'/('pmid_'+pmid+'.json'));hits=d.get('resultList',{}).get('result',[])
 if hits and hits[0].get('doi'):get('https://api.crossref.org/works/'+urllib.parse.quote(hits[0]['doi'],safe=''),O/'sources'/('crossref_'+pmid+'.json'))
 return pmid
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:list(pool.map(run,PMIDS))
 for pmid in ['38958374','35690339','22139695','21535728','38411783','37492094','33319311','34836412']:
  h=json.loads((O/'sources'/('pmid_'+pmid+'.json')).read_text(encoding='utf8'))['resultList']['result'][0];print('\n',pmid,h['title'],'\n',h.get('abstractText',''))
