import json,urllib.request,urllib.parse,concurrent.futures,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[1]; C=R/'sources'
names=['berberine','caffeine','curcumin','epigallocatechin gallate','piperine','resveratrol','genistein','naringin','capsaicin']
queries=[f'({n}) AND (pharmacokinetics OR interaction) AND (human OR volunteers OR clinical)' for n in names]
queries += ['curcumin AND sulfasalazine','epigallocatechin AND rosuvastatin','resveratrol AND (buspirone OR carbamazepine OR diclofenac OR cytochrome)','genistein AND (midazolam OR talinolol OR pharmacokinetics)','naringin AND (talinolol OR fexofenadine OR pharmacokinetics)','piperine AND (diclofenac OR chlorzoxazone OR rifampicin OR pharmacokinetics)','caffeine AND (mexiletine OR norfloxacin OR enoxacin OR disulfiram OR theophylline) AND (human OR volunteers)']
def fetch(item):
 i,q=item;p=C/f'search_{i:02}.json'
 if not p.exists():
  u='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(dict(query=q,format='json',resultType='core',pageSize=100))
  with urllib.request.urlopen(u,timeout=60) as r:d=json.load(r)
  p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
 d=json.loads(p.read_text(encoding='utf-8'))
 return dict(query_id=i,query=q,date=datetime.date.today().isoformat(),database='Europe PMC',hit_count=d.get('hitCount'),retrieved=len(d.get('resultList',{}).get('result',[])),cache=str(p.relative_to(R)))
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex: log=list(ex.map(fetch,enumerate(queries)))
(R/'outputs/search_log.json').write_text(json.dumps(log,indent=2),encoding='utf-8')
seen=set();lines=[]
for p in sorted(C.glob('search*.json')):
 for r in json.loads(p.read_text(encoding='utf-8')).get('resultList',{}).get('result',[]):
  if r.get('id') in seen:continue
  seen.add(r.get('id'));lines.append(json.dumps({k:r.get(k) for k in ['id','title','authorString','pubYear','doi','pmcid','pubTypeList','abstractText']},ensure_ascii=False))
(R/'outputs/candidates.jsonl').write_text('\n'.join(lines),encoding='utf-8')
print('Queries',len(log),'unique candidates',len(seen))
