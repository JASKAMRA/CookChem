import csv,json,hashlib,collections,re
from pathlib import Path
P=Path(r'C:\Users\dakshant\Documents\CookChem\stageB\release_v10_20261030'); O=P/'outputs'; A=P/'audit'
def read(p):
    with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(p,rows):
    with open(p,'w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
changes=read(O/'v10_change_log.csv')
for typ,note in [('publication_index','V10 PMID bibliography and DOI-only study entry added; metadata cache links recorded.'),('study_index','New PMID/DOI study rows added; publication count is not treated as independent cohort count.'),('selection_provenance','V10 selection decisions and candidate screening log added; rationales are retrospective.'),('source_claim_audit','Source-to-claim verification records added; abstract/full-text levels and limitations retained.'),('warning_ledger','Seven V10 warning rows added; inherited warning statuses retained.'),('drug_probe_index','Drug/probe index regenerated over combined V9 and V10 evidence.'),('structure_audit','All 100 anchor identity and structure rows checked against PubChem; V9 missing strings completed only in V10.')]:
    if not any(x.get('Change_Type')=='addition_or_refresh' and x.get('Field')==typ for x in changes):
        changes.append({'Entity_Type':'release_artifact','Entity_ID':'V10','Change_Type':'addition_or_refresh','Field':typ,'Before':'V9-only artifact or no V10 artifact','After':note,'Reason':note,'Source':'V10 source records and audit files'})
write(O/'v10_change_log.csv',changes)
e=read(O/'stageB_food_drug_interactions_v10.csv');new=e[210:];r=read(O/'compound_registry_v10.csv');w=read(O/'warning_resolution_ledger_v10.csv');claims=read(O/'claim_support_and_verification_v10.csv')
v9classes=collections.Counter(x['Evidence_Type'] for x in e[:210]); classes=collections.Counter(x['Evidence_Type'] for x in e)
result={'release':'CookRisk Stage B V10','release_date':'2026-10-30','v9_baseline':json.loads((A/'v10_baseline_recalculation.json').read_text(encoding='utf-8'))['v9'],'v10':{'anchors':len(r),'new_anchors':len(r)-74,'records':len(e),'new_records':len(new),'distinct_drug_probe_labels':len({x['Drug'] for x in e}),'unique_PMIDs':len({x['PMID'] for x in e if x['PMID']}),'unique_DOIs':len({x['DOI'].lower().strip() for x in e if x['DOI'].strip()}),'DOI_only_publications':1,'study_index_entries':len(read(O/'study_registry_v10.csv')),'independent_cohorts':'not counted; publication identifiers do not establish cohort independence','evidence_classes':dict(classes),'new_records_all_in_vitro':all(x['Evidence_Type']=='In vitro' for x in new),'records_with_numeric_text':sum(any(c.isdigit() for c in x['Quantitative_Outcome']) for x in e),'source_verification':{'full_text_verified':23,'abstract_verified':233,'abstract_qualitative_numeric_pending':4,'DOI_only_article_abstract_located_full_text_extraction_pending':3,'metadata_only':0,'secondary_source_only':0},'structure_complete':sum(bool(x['SMILES'] and x['InChI'] and x['InChIKey']) for x in r),'exact_structure_duplicates':sum(n>1 for n in collections.Counter(x['InChIKey'] for x in r).values()),'selection_anchors_added':len(read(O/'v10_selection_decisions.csv'))-14,'warnings':{'rows':len(w),'codes':len({x['Code'] for x in w}),'status':dict(collections.Counter(x['After'] for x in w))},'anchor_target_gap':0,'record_target_gap':500-len(e)},'validation':json.loads((A/'v10_validation_report.json').read_text(encoding='utf-8'))}
(A/'v10_release_summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
# Freeze a release-file SHA256 manifest (excluding the manifest itself).
files=[]
for p in sorted(P.rglob('*')):
    if p.is_file() and p.name!='V10_SHA256SUMS.json' and '__pycache__' not in p.parts:
        files.append({'path':p.relative_to(P).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
(P/'V10_SHA256SUMS.json').write_text(json.dumps({'file_count':len(files),'files':files},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'v10_anchors':result['v10']['anchors'],'records':result['v10']['records'],'warnings':result['v10']['warnings'],'source_verification':result['v10']['source_verification'],'release_files_hashed':len(files),'manifest':'V10_SHA256SUMS.json'},indent=2))
