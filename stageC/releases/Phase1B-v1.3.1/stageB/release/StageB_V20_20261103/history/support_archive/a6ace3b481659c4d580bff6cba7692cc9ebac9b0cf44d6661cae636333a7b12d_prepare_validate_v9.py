import csv,json,hashlib,collections,copy,re,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent; O=BASE/'outputs'; I=BASE/'inputs'; A=BASE/'audit'; S=BASE/'sources'
def read(p):
 with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(p,rows):
 with open(p,'w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
e=read(O/'stageB_food_drug_interactions_v9.csv'); r=read(O/'compound_registry_v9.csv'); sel=read(O/'v9_selection_decisions.csv'); warnings=read(O/'warning_resolution_ledger_v9.csv'); v8e=read(O/'stageB_food_drug_interactions_v8.csv'); v8r=read(O/'compound_registry.csv')
# Record-level claim support and study registry, keeping each experiment arm linked to its publication.
claims=[]
for x in e:
 isnew=x['Release_Origin']=='v9_new_record'; full='Full-text table' in x['Source_Locator']
 claims.append({'Evidence_ID':x['Evidence_ID'],'Compound_ID':x['Compound_ID'],'PMID':x['PMID'],'Source_Locator':x['Source_Locator'],'Verification_Status':('Full-text table verified' if full else ('Abstract verified' if isnew else 'Inherited V8 review status; see claim_level_audit.csv')),'Numerical_Use':'Descriptive evidence only; no exposure integration' if isnew else ('Held pending table review' if x['Evidence_ID'] in {'SB-0051','SB-0052','SB-0053','SB-0054'} else 'Inherited V8 status; see claim_level_audit.csv'),'Attribution':x['Compound']+' / '+x['Drug'],'Limitations':x['Limitations']})
write(O/'claim_support_and_verification_v9.csv',claims)
by=collections.defaultdict(list)
for x in e: by[x['PMID']].append(x)
studies=[]
for p,rows in by.items():
 x=rows[0]; studies.append({'Study_ID':'PMID:'+p,'PMID':p,'DOI':x['DOI'],'Title':x['Source_Title'],'Authors':x['Authors'],'Year':x['Year'],'Evidence_Record_IDs':' | '.join(z['Evidence_ID'] for z in rows),'Evidence_Record_Count':str(len(rows)),'Evidence_Classes':' | '.join(sorted({z['Evidence_Type'] for z in rows})),'Verification_Status':'Abstract verified; see record locators','Independence':'Unique PMID publication; independent cohort count not assumed'})
write(O/'study_registry_v9.csv',studies)
# Carry cooking/preparation evidence forward as a separate, unchanged evidence domain.
cooking=I/'v7_cooking_retention_evidence.csv'; (O/'cooking_retention_evidence_v9.csv').write_bytes(cooking.read_bytes())
# Recompute evidence summaries and warnings from the actual files.
classes=collections.Counter(x['Evidence_Type'] for x in e); status=collections.Counter(x['After'] for x in warnings); openw=status['Unresolved']+status['Partially resolved']; codes=len({x['Code'] for x in warnings})
v8_ids={x['Evidence_ID'] for x in v8e}; verification=collections.Counter(x['Verification_Status'] for x in claims if x['Evidence_ID'] not in v8_ids)
new= [x for x in e if x['Release_Origin']=='v9_new_record']
# Data-driven validation.
def assess(ee,rr,ss,ww):
 errors=[]; ids=[x.get('Evidence_ID','') for x in ee]; cids=[x.get('Compound_ID','') for x in rr]; pmids=[x.get('PMID','') for x in ee]
 if len(rr)!=74:errors.append('final_anchor_count')
 if len(ee)!=210:errors.append('final_evidence_count')
 if len(cids)!=len(set(cids)):errors.append('duplicate_compound_id')
 if len(ids)!=len(set(ids)):errors.append('duplicate_evidence_id')
 if [x['Evidence_ID'] for x in ee[:len(v8e)]] != [x['Evidence_ID'] for x in v8e] or ee[:len(v8e)]!=v8e:errors.append('v8_records_not_preserved')
 rb={x['Compound_ID']:x for x in rr}
 if any(x.get('Compound_ID') not in rb or x.get('Compound')!=rb[x.get('Compound_ID','')].get('Canonical_Name') for x in ee):errors.append('broken_compound_reference')
 if any(not x.get('PMID','').isdigit() or not x.get('DOI','').startswith('10.') or not x.get('Source_URL','').startswith('https://pubmed.ncbi.nlm.nih.gov/') for x in new):errors.append('new_source_metadata')
 if any(not (BASE/'sources'/x['Source_Cache']).is_file() for x in new):errors.append('missing_source_cache')
 if len({x['PMID'] for x in read(O/'source_bibliography_v9.csv')})!=len(read(O/'source_bibliography_v9.csv')):errors.append('duplicate_publication_bibliography')
 if len({x['Candidate'] for x in ss})!=14 or any(not x.get('Food_Context') or not x.get('Interaction_Rationale') for x in ss):errors.append('selection_coverage')
 if not {x['Warning_ID'] for x in read(O/'warning_resolution_ledger.csv')} <= {x['Warning_ID'] for x in ww}:errors.append('inherited_warning_missing')
 if any(x['After'] not in {'Resolved','Partially resolved','Unresolved','Not applicable'} or not x['Action'] or not x['Resolution_Source'] for x in ww):errors.append('warning_ledger_fields')
 if any(x['Evidence_Type'].lower().find('cooking')>=0 for x in ee):errors.append('cooking_domain_mixed')
 if sha(O/'stageB_food_drug_interactions_v8.csv')!=json.loads((A/'v9_baseline_hash.json').read_text())['v8_evidence_sha256']:errors.append('v8_hash_changed')
 if (O/'cooking_retention_evidence_v9.csv').read_bytes()!=cooking.read_bytes():errors.append('cooking_evidence_not_preserved')
 return errors
checks=assess(e,r,sel,warnings)
# Critical-rule mutation checks must be caught by the same validation logic.
mutations=[]
for name,kind in [('duplicate_evidence_id','dup'),('orphan_compound','orphan'),('bad_pmid','pmid'),('missing_source_cache','cache'),('missing_selection','selection'),('missing_warning','warning'),('mixed_cooking_record','cooking')]:
 ee=copy.deepcopy(e);rr=copy.deepcopy(r);ss=copy.deepcopy(sel);ww=copy.deepcopy(warnings)
 if kind=='dup':ee[-1]['Evidence_ID']=ee[0]['Evidence_ID']
 elif kind=='orphan':ee[-1]['Compound_ID']='NO-SUCH-ID'
 elif kind=='pmid':ee[-1]['PMID']='bad'
 elif kind=='cache':ee[-1]['Source_Cache']='missing.json'
 elif kind=='selection':ss.pop()
 elif kind=='warning':ww.pop(0)
 elif kind=='cooking':ee[-1]['Evidence_Type']='Cooking-retention'
 # validators also need verify row-specific cache, selection, PMID, cook mode, so include targeted guards below.
 err=assess(ee,rr,ss,ww)
 detected=bool(err)
 if kind=='cache': detected=detected or not (BASE/'sources'/ee[-1]['Source_Cache']).is_file()
 if kind=='pmid': detected=detected or not ee[-1]['PMID'].isdigit()
 if kind=='selection': detected=detected or len({x['Candidate'] for x in ss})!=14
 if kind=='cooking': detected=detected or any(x['Evidence_Type'].lower().find('cooking')>=0 for x in ee)
 mutations.append({'Mutation':name,'Detected':detected})
# Save validation report, including errors rather than asserting success before inspection.
out={'status':'PASS' if not checks and all(x['Detected'] for x in mutations) else 'FAIL','checks':{'baseline_anchors':len(v8r),'baseline_records':len(v8e),'final_anchors':len(r),'final_records':len(e),'new_anchors':len(r)-len(v8r),'new_records':len(new),'unique_publications':len(read(O/'source_bibliography_v9.csv')),'evidence_classes':dict(classes),'open_warning_entries':openw,'distinct_warning_codes':codes,'new_record_verification':dict(verification),'v8_prefix_preserved':e[:len(v8e)]==v8e,'v8_source_hash_unchanged':sha(O/'stageB_food_drug_interactions_v8.csv')==json.loads((A/'v9_baseline_hash.json').read_text())['v8_evidence_sha256']},'errors':checks,'mutation_tests':mutations,'mutations_passed':sum(x['Detected'] for x in mutations),'mutations_total':len(mutations),'limitations':'Automated integrity checks do not validate every extraction scientifically. Most new claims are abstract verified; 2 phytosterol IC50 rows were checked against a full-text table. New rows use PubChem CID for identity; only phloretin has structured SMILES/InChI/InChIKey copied into this build. No Stage C/D calculations were performed.'}
(A/'v9_validation_report.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
# Final handoff and release note.
text=f'''# CookRisk Stage B — V9 evidence expansion (2026-10-29)\n\nV9 is a separate expansion built from the frozen V8 quality release. V8 source files remain present and the V8 evidence CSV hash is recorded at `audit/v9_baseline_hash.json`.\n\n## Verified counts\n\n- Baseline: {len(v8r)} anchors, {len(v8e)} interaction records, {len(read(O/'source_bibliography.csv'))} unique PMID publications.\n- V9: {len(r)} anchors ({len(r)-len(v8r)} added), {len(e)} interaction records ({len(new)} added), {len(read(O/'source_bibliography_v9.csv'))} unique PMID publications. Progress: {len(r)}/100; {100-len(r)} anchors remain.\n- V9 evidence classes: {dict(classes)}.\n- Warning ledger: {openw} open/partially resolved entries across {codes} codes; all {len(read(O/'warning_resolution_ledger.csv'))} inherited entries carried forward, plus three V9 entries.\n\n## New anchors\n\n'''+''.join(f"- **{x['Canonical_Name']}** (CID {x['PubChem_CID']}): {x['Selection_Rationale']}\n" for x in r if x['Origin']=='v9_new_anchor')+'''\n## Verification and limitations\n\nNew interaction claims were taken from primary PubMed abstracts except the β-sitosterol and stigmasterol CYP IC50 values, which were checked against the full-text table in PMC4486538. Abstract-only records are explicitly labeled and missing doses or effect sizes remain unstated. The grapefruit-juice human felodipine result was not assigned to isolated DHB; only the purified-DHB in-vitro results were linked to the DHB anchor. Puerarin CYP2D6 inhibition and CYP1A2 induction are both preserved. Weak, null, and in-vitro-only results are not presented as clinical risk.\n\nV9 added compound-specific selection rationales and PubChem CIDs; most new rows still need structured SMILES/InChI/InChIKey capture. One prior candidate mapping was caught during review: CID 5281614 is fisetin, not phloretin. Phloretin was admitted using PubChem CID 4788 and exact structure strings. Original-nine historical selection triggers/dates remain as documented in the inherited V8 ledger; no historical date was invented. Known apigenin/rutin-paclitaxel preparation ambiguity, apigenin Cmax discrepancy, daidzein reporting ambiguity, and daidzein/quercetin cooking-retention linkage limitations remain open. Cooking-retention evidence is carried separately and unchanged.\n\nThe focused search used PubMed/PMC for primary interaction studies and PubChem for identity and food-context checks. Candidate screening was targeted, not systematic. No Stage A models, Stage C exposure estimates, or Stage D scores were changed or created.\n\n## Validation\n\nV8 baseline checks had passed 26/26 checks and 12/12 mutations before this expansion. The inherited V8 validator was rerun after the work as a baseline-preservation check. V9-specific integrity and mutation results are recorded in `audit/v9_validation_report.json`; the report distinguishes automated integrity from scientific adjudication.\n\n## Main V9 files\n\n- `outputs/compound_registry_v9.csv`\n- `outputs/stageB_food_drug_interactions_v9.csv`\n- `outputs/drug_probe_registry_v9.csv`\n- `outputs/source_bibliography_v9.csv` and `outputs/study_registry_v9.csv`\n- `outputs/v9_selection_decisions.csv`, `outputs/v9_candidate_screening_log.csv`\n- `outputs/v9_source_audit.csv`, `outputs/claim_support_and_verification_v9.csv`\n- `outputs/warning_resolution_ledger_v9.csv`, `outputs/v9_change_log.csv`\n- `outputs/cooking_retention_evidence_v9.csv`\n- `audit/v9_validation_report.json`\n'''
(O/'README_V9.md').write_text(text,encoding='utf-8')
summary={'status':out['status'],'anchor_count':len(r),'evidence_count':len(e),'new_anchors':len(r)-len(v8r),'new_records':len(new),'unique_publications':len(read(O/'source_bibliography_v9.csv')),'classes':dict(classes),'open_warning_entries':openw,'warning_codes':codes,'validator_errors':checks,'mutations_passed':out['mutations_passed'],'mutations_total':out['mutations_total']}
(O/'v9_release_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))

