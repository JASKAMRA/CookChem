exec(open(__file__.replace('exact.py','search.py'),encoding='utf8').read().split('with concurrent.futures')[0])
ids=['20716633','21943317']
queries=['EXT_ID:'+i+' AND SRC:MED' for i in ids]
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex: log=list(ex.map(fetch,enumerate(queries,43)))
(R/'outputs/probe_search_log.json').write_text(json.dumps(log,indent=2),encoding='utf8')
for i in range(43,45):
 for r in json.loads((C/f'search_{i:02}.json').read_text(encoding='utf8')).get('resultList',{}).get('result',[]):
  print(json.dumps({k:r.get(k) for k in ['id','title','doi','abstractText']},ensure_ascii=False))
  if r.get('pmcid') and r.get('isOpenAccess')=='Y':
   try:
    with urllib.request.urlopen('https://www.ebi.ac.uk/europepmc/webservices/rest/'+r['pmcid']+'/fullTextXML',timeout=60) as response:(C/(r['pmcid']+'.xml')).write_bytes(response.read())
   except Exception as e:print('Full-text unavailable',r['id'],str(e))
