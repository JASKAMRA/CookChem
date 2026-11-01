exec(open(__file__.replace('targeted.py','search.py'),encoding='utf8').read().split('with concurrent.futures')[0])
queries=[f'TITLE:{n} AND (TITLE:volunteers OR TITLE:human OR TITLE:interaction OR TITLE:drug) AND FIRST_PDATE:[1900-01-01 TO 2020-12-31]' for n in ['berberine','caffeine','curcumin','epigallocatechin','piperine','resveratrol','genistein','naringin','capsaicin']]
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex: log=list(ex.map(fetch,enumerate(queries,25)))
(R/'outputs/historical_search_log.json').write_text(json.dumps(log,indent=2),encoding='utf8')
for i in range(25,34):
 for r in json.loads((C/f'search_{i:02}.json').read_text(encoding='utf8')).get('resultList',{}).get('result',[]):print(r.get('id'),r.get('title'))
