"""DOI metadata audit only; does not certify source measurements or alter inputs."""
import csv,json,urllib.request,urllib.parse,hashlib,concurrent.futures,re,unicodedata
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1]; C=ROOT/'sources'
data=list(csv.DictReader(open('C:/Users/dakshant/Downloads/cookchem_master_expanded_round11.csv',encoding='utf-8-sig')))
g=defaultdict(list)
for r in data:
    if r['DOI']: g[r['DOI'].strip().lower()].append(r)
def norm(s): return re.sub('[^a-z0-9]','',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())
def work(item):
    doi,rs=item; p=C/('crossref_'+hashlib.sha256(doi.encode()).hexdigest()[:16]+'.json')
    if not p.exists():
        try:
            with urllib.request.urlopen('https://api.crossref.org/works/'+urllib.parse.quote(doi,safe=''),timeout=40) as response: x=json.load(response)
        except Exception as e: x={'retrieval_error':str(e)}
        p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
    x=json.loads(p.read_text(encoding='utf-8')); m=x.get('message',{}) if isinstance(x.get('message',{}),dict) else {}
    supplied_auth=sorted({r['Authors'] for r in rs}); supplied_year=sorted({r['Year'] for r in rs}); pubyears=sorted({str(m[k]['date-parts'][0][0]) for k in ['published','published-print','published-online','issued'] if k in m and m[k].get('date-parts')})
    authors='; '.join(' '.join([a.get('given',''),a.get('family','')]).strip() for a in m.get('author',[]))
    family=[norm(a.get('family','')) for a in m.get('author',[]) if a.get('family')]
    authorok=all(any(f in norm(a) for f in family) for a in supplied_auth) if family else False
    yearok=all(y in pubyears for y in supplied_year)
    return {'DOI':doi,'record_count':len(rs),'Record_IDs':' | '.join(r['Record_ID'] for r in rs),'supplied_authors':' | '.join(supplied_auth),'supplied_years':' | '.join(supplied_year),'retrieved_title':' | '.join(m.get('title',[])),'retrieved_authors':authors,'retrieved_years':' | '.join(pubyears),'author_metadata_concordant':str(authorok).lower(),'year_metadata_concordant':str(yearok).lower(),'status':'retrieval_unavailable' if not m else ('metadata_concordant_measurements_unverified' if authorok and yearok else 'metadata_mismatch_source_verification_required'),'source_url':'https://doi.org/'+doi,'cache':p.relative_to(ROOT).as_posix(),'interpretation':'Metadata matching does not verify food, compound, conditions or measured values.'}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool: out=list(pool.map(work,g.items()))
with (ROOT/'outputs/stageB_dataset_source_audit.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
print('DOIs audited',len(out),'metadata mismatch',sum(r['status']=='metadata_mismatch_source_verification_required' for r in out),'retrieval unavailable',sum(r['status']=='retrieval_unavailable' for r in out))
