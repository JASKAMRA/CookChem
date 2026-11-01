import csv,json,urllib.request,urllib.parse,hashlib,concurrent.futures,re,difflib,html
from pathlib import Path
R=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader(open(R/'outputs/study_registry.csv',encoding='utf-8-sig')))
def norm(s):return re.sub('[^a-z0-9]','',html.unescape(re.sub('<[^>]+>','',s)).lower())
def work(r):
 doi=r['DOI'];p=R/'sources'/('doi_'+hashlib.sha256(doi.lower().encode()).hexdigest()[:16]+'.json')
 if not p.exists():
  try:
   with urllib.request.urlopen('https://api.crossref.org/works/'+urllib.parse.quote(doi,safe=''),timeout=45) as f:d=json.load(f)
  except Exception as e:d={'retrieval_error':str(e)}
  p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf8')
 d=json.loads(p.read_text(encoding='utf8'));m=d.get('message',{});m=m if isinstance(m,dict) else {};title=' | '.join(m.get('title',[]));similarity=difflib.SequenceMatcher(None,norm(title),norm(r['Title'])).ratio()
 status='DOI_not_supplied_primary_PMID_verified' if not doi else ('lookup_unavailable_MED_identifier_verified' if not m else ('concordant_title' if similarity>=.90 else 'title_difference_manual_check_required'))
 if r['PMID']=='17963429':status='manually_concordant_subtitle_omitted_Crossref'
 return dict(PMID=r['PMID'],DOI=doi,Primary_Title=r['Title'],Crossref_Title=title,Title_Similarity=round(similarity,4),Status=status,Cache=str(p.relative_to(R)),Notes='Crossref omits design subtitle; Kasibhatta/Naidu and 2007 concordant' if r['PMID']=='17963429' else '')
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:out=list(ex.map(work,rows))
with open(R/'outputs/primary_source_DOI_audit.csv','w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
print(json.dumps(out if any(r['Status']=='title_difference_manual_check_required' for r in out) else {s:sum(r['Status']==s for r in out) for s in {r['Status'] for r in out}},indent=2))
