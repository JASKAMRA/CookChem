"""Offline V8 build; reads immutable V7 and captured primary sources only."""
from pathlib import Path
import csv,json,hashlib,shutil,collections,sys
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;B=O.parent;V=B/'release_v7_20261015_clean'
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(name,rows):
 with (O/'outputs'/name).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def med(p):return next(x for x in json.loads((O/'sources'/f'pmid_{p}.json').read_text(encoding='utf8'))['resultList']['result'] if x['id']==p)
def main():
 old=read(V/'outputs/stageB_food_drug_interactions_v7.csv');e=[dict(x) for x in old];r=read(V/'outputs/compound_registry.csv');reviews={x['Evidence_ID']:dict(x) for x in read(V/'outputs/all_record_review_audit.csv')};changes=[]
 updates={
 'SB-0002':{'Quantitative_Outcome':'Cyclosporine C0 increased 26% and C2 increased 18% (both p<0.01); daily cyclosporine dose reduced 25-100 mg in 21 patients.','Limitations':'Open clinical transplant study; dose adjustment complicates causal attribution. Berberine dose not supplied in abstract; not inferred.'},
 'SB-0033':{'Quantitative_Outcome':'Caffeine half-life 5.2 +/- 1.2 to 8.2 +/- 2.5 h; AUC 16.3 +/- 6.6 to 25.9 +/- 7.8 microgram.h/mL; clearance 106 +/- 41.6 to 58.2 +/- 28.8 mL/min per 1.73 m2.','Limitations':'Small human study; clearance is normalized to 1.73 m2. Small reverse effect on ciprofloxacin AUC has no extracted magnitude.'},
 'SB-0046':{'Quantitative_Outcome':'Human sulfasalazine AUC0-24 increased 2.0-fold at the 100 microgram microdose and 3.2-fold at the 2 g therapeutic dose.','Limitations':'Eight healthy Japanese subjects; curcumin 2 g intervention is not a food-dose equivalence. Separate animal and in-vitro arms are not additional human cohorts.'},
 'SB-0012':{'Interaction_Effect':'Longer reported sedation and model-derived lower clearance; observed AUC0-5 difference was not significant.','Quantitative_Outcome':'Reported sedation duration 102 +/- 43 to 188 +/- 59 min (p<0.0001). Model-derived half-life 1.71 +/- 0.04 to 1.88 +/- 0.03 h and clearance 37.09 +/- 1.07 to 33.62 +/- 0.4 mL/min; observed AUC0-5 not significantly different.','Limitations':'Source sample-size wording inconsistent; Results reports 20 participants. Sparse three-sample one-compartment model; clearance prose conflicts with numerical direction. Abstract supplies units absent from Table 2 headers; Table 1 end-of-effect label versus Results duration wording is ambiguous. No robust observed AUC increase asserted.'},
 'SB-0037':{'Interaction_Effect':'Acute EGCG reduced rosuvastatin AUC; acute Cmax confidence interval includes no effect. Ten-day pretreatment comparisons were not significant.','Quantitative_Outcome':'Acute AUClast GMR 0.81 (90% CI 0.67-0.97), AUCinf 0.80 (0.66-0.96), Cmax 0.85 (0.70-1.04; not significant). After pretreatment: AUClast 0.89 (0.74-1.07), AUCinf 0.85 (0.71-1.02), Cmax 0.92 (0.75-1.12); all not significant.','Preparation':'Teavigo capsules containing 94% pure crystalline EGCG; 300 mg EGCG, one hour before rosuvastatin 20 mg.','Limitations':'Open-label fixed-sequence study of 13 volunteers (2 male, 11 female); Table 2 Cmax CI includes 1 despite abstract wording. No ordinary-tea equivalence or clinical outcome inferred.'}}
 for x in e:
  for k,val in updates.get(x['Evidence_ID'],{}).items():
   support={'SB-0012':'sources/PMC3904487.xml','SB-0037':'sources/PMC5431696.xml'}.get(x['Evidence_ID'],f'sources/pmid_{x["PMID"]}.json')
   changes.append(dict(Evidence_ID=x['Evidence_ID'],Field=k,Before=x[k],After=val,Reason='Primary-source re-extraction; uncertainty retained',PMID=x['PMID'],Source=support,Review_Date='2026-10-15'));x[k]=val
 pending={'SB-0051','SB-0052','SB-0053','SB-0054'}
 for x in e:
  q=reviews[x['Evidence_ID']]
  if q['Verification_Level']=='metadata_only_recent_audit':
   q.update(Verification_Level='abstract_qualitative_numeric_pending' if x['Evidence_ID'] in pending else 'abstract',Detail=f'sources/pmid_{x["PMID"]}.json; primary abstract manually compared with existing claims, design and intervention',Scope='V8 primary abstract review; absent details not inferred')
  if x['Evidence_ID'] in ['SB-0012','SB-0037']:
   q.update(Verification_Level='full_text_selected',Detail='sources/'+('PMC3904487.xml' if x['Evidence_ID']=='SB-0012' else 'PMC5431696.xml')+'; Methods, Results and outcome tables manually examined',Scope='V8 selected full-text outcome review; not whole-paper independent adjudication')
  if x['Evidence_ID'] in pending:q['Detail']+='; qualitative CYP direction supported, legacy GMR/CI require original full-text tables and are held from numerical integration'
 write('stageB_food_drug_interactions_v8.csv',e);write('compound_registry.csv',r);write('evidence_change_log.csv',changes);write('all_record_review_audit.csv',list(reviews.values()))
 # Snapshot full inherited source closure to keep unchanged source pointers auditable.
 inherited=O/'inherited_sources';inherited.mkdir(exist_ok=True)
 for folder in ['inherited_sources','inherited_audits']:
  if (V/folder).exists():shutil.copytree(V/folder,O/folder,dirs_exist_ok=True)
 shutil.copytree(V/'sources',inherited/V.name/'sources',dirs_exist_ok=True)
 for x in e:
  src=B/x['Source_Cache'];dst=inherited/x['Source_Cache'];dst.parent.mkdir(parents=True,exist_ok=True)
  if not dst.exists():shutil.copy2(src,dst)
 for name in ['selection_provenance_ledger.csv','food_context_source_audit.csv','interaction_evidence_source_audit.csv','near_duplicate_identity_audit.csv','processing_provenance_audit.csv','cooking_retention_evidence.csv','drug_probe_registry.csv','study_registry.csv','screening_log.csv','candidate_selection.csv','claim_support_and_outcome_audit.csv']:
  shutil.copy2(V/'outputs'/name,O/'inputs'/('v7_'+name))
 identity=[]
 for x in r:
  h=json.loads((O/'sources'/f'identity_{x["PubChem_CID"]}.json').read_text(encoding='utf8'))['PropertyTable']['Properties'][0]
  identity.append(dict(Compound_ID=x['Compound_ID'],Compound=x['Canonical_Name'],CID=x['PubChem_CID'],Expected_InChIKey=x['InChIKey'],Current_InChIKey=h['InChIKey'],Match=x['InChIKey']==h['InChIKey'],Food_Context=x['Food_Context'],Interaction_Rationale=x['Selection_Rationale'],Restriction=x['Link_Restriction'],Source=f'sources/identity_{x["PubChem_CID"]}.json'))
 write('identity_structure_audit.csv',identity)
 claims=[];bibliography=[]
 for x in e:
  h=med(x['PMID']);level=reviews[x['Evidence_ID']]['Verification_Level']
  claims.append(dict(Evidence_ID=x['Evidence_ID'],PMID=x['PMID'],Compound_ID=x['Compound_ID'],Verification_Level=level,Quantitative_Claim=x['Quantitative_Outcome'],Qualitative_Claim=x['Interaction_Effect'],Source=f'sources/pmid_{x["PMID"]}.json',Full_Text_Or_Inherited_Locator=reviews[x['Evidence_ID']]['Detail'],Numerical_Use='HOLD: original table re-verification pending' if x['Evidence_ID'] in pending else 'Literature lookup with study limitations; no exposure or clinical score',Attribution='PROVISIONAL: apigenin/rutin arms unresolved' if x['Evidence_ID']=='SB-0066' else 'Preserve stated preparation, perpetrator and affected entity',Study_Class=x['Evidence_Type'],Dose=x['Dose'],Population=x['Population'],Design=x['Study_Design'],Preparation=x['Preparation'],Limitations=x['Limitations']))
 for pm in sorted({x['PMID'] for x in e}):
  h=med(pm);bibliography.append(dict(PMID=pm,Title=h['title'],Authors=h['authorString'],Year=h['pubYear'],DOI=h.get('doi',''),PMCID=h.get('pmcid',''),Source=f'sources/pmid_{pm}.json',Count_Unit='Unique PMID-indexed publication; NOT independent cohort',DOI_Status='Supplied by MED' if h.get('doi') else 'Not supplied in current MED; not invented'))
 write('claim_level_audit.csv',claims);write('source_bibliography.csv',bibliography)
 provenance=[]
 first={'Berberine','Piperine','Curcumin','EGCG','Caffeine'}
 for x in r:
  if x['Origin']=='original_nine':
   initial=x['Canonical_Name'] in first
   provenance.append(dict(Compound=x['Canonical_Name'],Documented_Rationale='Initial five manually curated evidence anchors are listed, but no compound-specific contemporaneous choice rationale recovered.' if initial else 'V2 prioritization documented verified parent identity plus primary human interaction evidence; useful mechanistic bridges; frequency not sole criterion.',Historical_Rationale_Source='stageB/scripts/build_stageB.py; stageB/reports/stageB_methodology.md' if initial else 'stageB/expansion_v2/outputs/compound_prioritization.csv; stageB/expansion_v2/reports/literature_search_methodology.md',First_Documented_Search_Date='2026-10-06',Search_Date_Source='stageB/outputs/stageB_search_log.csv' if initial else 'stageB/expansion_v2/outputs/literature_search_log.csv',Original_Selection_Date='',Original_Primary_Selection_Trigger='',Status='Unresolved' if initial else 'Partially resolved',Review_Date='2026-10-15',Distinction='Interaction publications establish evidence, not proof of original historical selection event'))
 write('original_nine_selection_provenance.csv',provenance)
 warnings=read(V/'outputs/warning_resolution_ledger.csv')
 actions={
 'historical_selection_provenance':('Partially resolved','23 local source documents plus original search logs reviewed; search dates recovered, original selection dates and triggers remain unknown.','outputs/historical_document_search.csv; outputs/original_nine_selection_provenance.csv'),
 'inherited_outcome_scope':('Partially resolved','58 metadata-only records manually reviewed: 52 abstract, 2 selected-full-text upgrades; 4 resveratrol numerical table checks remain pending.','outputs/all_record_review_audit.csv; outputs/claim_level_audit.csv'),
 'unresolved_preparation':('Unresolved','Primary publisher abstract cannot distinguish separate versus combined apigenin/rutin arms; subscription full text unavailable; no isolated magnitude assigned.','https://link.springer.com/article/10.1007/s13318-014-0203-z'),
 'source_reporting_ambiguity':('Unresolved','Publisher abstract repeats day-3 methods versus day-1 results baseline and CI scale ambiguity; disputed CIs remain omitted.','https://link.springer.com/article/10.1007/s00228-003-0596-0'),
 'source_table_prose_discrepancy':('Unresolved','PMC3863468 Table 1 Cmax values increase for single doses whereas Results 3.3 says decrease; conflicting Cmax interpretation withheld.','sources/PMC3863468.xml; PMID 24369535'),
 'retention_link_unavailable':('Partially resolved','Re-examined soy assay hydrolysis and onion glycoside/weight-basis methods. These do not establish native free-aglycone master retention. No automatic link or coefficients imported.','inherited_sources/release_v4_20261014/sources/PMC11011382.xml; inherited_sources/release_v4_20261014/sources/PMC8151956.xml'),
 'parent_identity_scope':('Partially resolved','All 60 current reference InChIKeys match PubChem. This does not certify study formulation/isomer purity or repair master measurement provenance.','outputs/identity_structure_audit.csv'),
 'v6_reference_stereochemistry':('Partially resolved','Reference structures independently matched; primary tested stereochemical purity remains unestablished.','outputs/identity_structure_audit.csv'),
 'v7_identity_scope':('Partially resolved','Reference identities independently matched; ascorbate/folate analyte scope and tested-form restrictions retained.','outputs/identity_structure_audit.csv'),
 'possible_participant_overlap':('Unresolved','121 unique publications are explicitly not 121 independent cohorts. Possible shared genotype recruitment cannot be excluded.','inputs/v7_study_registry.csv; outputs/source_bibliography.csv')}
 for w in warnings:
  before=w['After'];status,act,src=actions.get(w['Code'],(before,'Fresh MED metadata checked for all 121 reports; existing scientific limitation retained. No new primary evidence supports closure.','outputs/source_bibliography.csv; inputs/v7_claim_support_and_outcome_audit.csv'))
  if w['Warning_ID']=='V3-W02':status='Unresolved';act='Original five documented as initial anchors; no original per-compound selection trigger or date recovered.'
  status={'Resolved with supporting source':'Resolved','Not applicable after inspection':'Not applicable'}.get(status,status)
  w.update(Before=before,Action=act,After=status,Resolution_Source=src,Review_Date='2026-10-15')
 warnings.append(dict(Warning_ID='V8-W24',Code='legacy_resveratrol_numerical_table_pending',Description='Four legacy GMR/CI outcomes not independently reverified against original full tables',Affected='SB-0051 | SB-0052 | SB-0053 | SB-0054',Classification='Numerical verification limitation',Before='Not explicitly separated in V7',Action='Primary abstract verifies qualitative enzyme directions only; preserved values explicitly held from numerical integration; public full-text requests failed.',After='Unresolved',Remaining_Limitations='Requires lawful full-text table access; not evidence that legacy values are wrong',Resolution_Source='sources/pmid_20716633.json; outputs/full_text_access_log.csv; outputs/alternative_full_text_access_log.csv',Review_Date='2026-10-15'))
 warnings.append(dict(Warning_ID='V8-W25',Code='piperine_midazolam_reporting',Description='Model-derived estimates, sample wording and clearance prose inconsistencies',Affected='SB-0012',Classification='Source reporting limitation',Before='Not separately coded in V7',Action='Re-extracted relevant full text; observed AUC null preserved; sedation separated from model PK; source contradictions retained.',After='Partially resolved',Remaining_Limitations='Author clarification needed for sample wording and prose; sparse model does not establish observed AUC increase',Resolution_Source='sources/PMC3904487.xml',Review_Date='2026-10-15'))
 write('warning_resolution_ledger.csv',warnings)
 deferred={x['Candidate']:x for x in read(V/'outputs/candidate_selection.csv') if x['Decision']=='deferred'}
 for x in read(V/'inherited_audits/v6/screening_log.csv'):
  # Older deferred candidates remain discoverable in inherited ledger; no blind admission.
  pass
 write('deferred_candidate_review.csv',[dict(Candidate=k,Decision='Remain deferred; no new admission',Scientific_Reason='Quality-focused release; no demonstrated evidence gap requires expansion. Prior substantive arm/identity/source review remains incomplete.',Prior_Reason=x['Reason'],Review_Scope='Triage only; no fresh candidate claim adjudication',Date='2026-10-15') for k,x in deferred.items()])
 summary=dict(version='V8',date='2026-10-15',anchors=len(r),records=len(e),publications=len(bibliography),drugs=len({x['Drug'] for x in e}),classes=dict(collections.Counter(x['Evidence_Type'] for x in e)),verification=dict(collections.Counter(x['Verification_Level'] for x in reviews.values())),changed_records=len({x['Evidence_ID'] for x in changes}),changed_fields=len(changes),numeric_fields_filled=sum(bool(x['Quantitative_Outcome']) for x in e),numeric_table_holds=4,warning_statuses=dict(collections.Counter(x['After'] for x in warnings)),open_warning_entries=sum(x['After'] in ['Unresolved','Partially resolved'] for x in warnings),deferred_triaged=len(deferred),new_anchors=0,new_records=0)
 (O/'outputs/release_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
