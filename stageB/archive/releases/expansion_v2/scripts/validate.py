import csv,json,hashlib,collections,zipfile,html,re
from pathlib import Path
R=Path(__file__).resolve().parents[1];B=R.parent
def read(p):
 with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
r=read(R/'outputs/stageB_food_drug_interactions_expanded.csv');s=json.loads((R/'outputs/evidence_summary.json').read_text());m=read(R/'outputs/qc_identity.csv');mi={x['Compound_ID']:x for x in m};old=read(B/'outputs/stageB_food_drug_interactions.csv')
checks={}
checks['record_count_matches_summary']=len(r)==s['evidence_records']==64
checks['unique_evidence_ids']=len({x['Evidence_ID'] for x in r})==len(r)
checks['initial_identifiers_preserved']=all(any(x['Evidence_ID']==o['interaction_id'] and x['Compound']==o['compound_name'] and x['Drug']==o['drug_name'] and x['PMID']==o['source_id'] for x in r) for o in old)
checks['no_excluded_identity_assigned']=all(mi[x['Compound_ID']]['Status'].startswith('verified') for x in r)
checks['complete_priorities']=len(read(R/'outputs/compound_prioritization.csv'))==198
checks['evidence_categories_sum']=sum(s[x] for x in ['human_PK_records','clinical_records','animal_records','in_vitro_records'])==len(r)
checks['primary_report_count']=len({x['PMID'] for x in r})==s['primary_reports']==45
checks['required_fields_present']=all(all(x[k] for k in ['Compound','Compound_ID','Drug','Interaction_Effect','Evidence_Type','Study_Design','Source_Title','Authors','Year','PMID','Limitations','Confidence','Source_Locator']) for x in r)
checks['source_cache_PMID_title_DOI_concordance']=True
for x in r:
 p=B/x['Source_Cache'];d=json.loads(p.read_text(encoding='utf8'));match=[t for t in d.get('resultList',{}).get('result',[]) if t.get('id')==x['PMID'] and t.get('source')=='MED']
 norm=lambda t:re.sub('[^a-z0-9]','',html.unescape(t).lower())
 if not match or match[0].get('doi','').lower()!=x['DOI'].lower() or norm(match[0]['title'])!=norm(x['Source_Title']):checks['source_cache_PMID_title_DOI_concordance']=False
checks['no_source_after_search_date']=all(int(x['Year'])<=2026 for x in r)
checks['conflict_records_refer_to_existing_ids']=all(all(t.strip() in {x['Evidence_ID'] for x in r} for t in c['Evidence_IDs'].split('|')) for c in read(R/'outputs/conflict_synthesis.csv'))
checks['all_search_caches_present']=all((R/x['cache']).exists() for x in read(R/'outputs/literature_search_log.csv'))
audit=read(R/'outputs/primary_source_DOI_audit.csv');checks['no_unreviewed_Crossref_title_mismatches']=all(x['Status']!='title_difference_manual_check_required' for x in audit)
(R/'outputs/validation_results.json').write_text(json.dumps(checks,indent=2),encoding='utf8')
assert all(checks.values()),checks
hashes={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in R.rglob('*') if p.is_file() and '__pycache__' not in str(p) and p.name!='manifest_sha256.json'}
(R/'manifest_sha256.json').write_text(json.dumps(hashes,indent=2),encoding='utf8')
archive=B.parent/'CookRisk_StageB_Expanded_v2.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(R.rglob('*')):
  if p.is_file() and '__pycache__' not in str(p):z.write(p,p.relative_to(B.parent))
 needed={B/x['Source_Cache'] for x in r if not x['Source_Cache'].replace('\\','/').startswith('expansion_v2/')}
 for sub in ['outputs','reports','audit']:
  needed.update(p for p in (B/sub).glob('*') if p.is_file())
 for cid in ['2353','2519','969516','65064','638024','445154','5280961','442428','1548943']:
  needed.update(p for p in [B/'sources'/('pubchem_'+cid+'.json'),B/'sources'/('synonyms_'+cid+'.json')] if p.exists())
 for p in sorted(needed):z.write(p,p.relative_to(B.parent))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(json.dumps(checks,indent=2));print('Archive:',archive)
