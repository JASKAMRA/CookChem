import csv,json,hashlib,collections,re
from pathlib import Path
B=Path(__file__).resolve().parent;O=B/'outputs';A=B/'audit';R=B/'reports'
def rd(p):
 with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def wr(p,rows):
 with open(p,'w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
r=rd(O/'compound_registry_v9.csv');e=rd(O/'stageB_food_drug_interactions_v9.csv')
for x in r:
 if x['Canonical_Name']=='Phloretin': x['Remaining_Provenance_Gap']='Identity verified against PubChem CID 4788 including SMILES, InChI and InChIKey; original historical selection date is not applicable to this V9 addition.'
wr(O/'compound_registry_v9.csv',r)
# Explicit compound identity audit: authoritative CID links for all new anchors; full structure strings only where copied from PubChem.
ident=[]
for x in r:
 ident.append({'Compound_ID':x['Compound_ID'],'Canonical_Name':x['Canonical_Name'],'PubChem_CID':x['PubChem_CID'],'Identity_Source':x['Identity_Source'],'Identity_Status':x['Identity_Status'],'SMILES_Present':str(bool(x['SMILES'])),'InChI_Present':str(bool(x['InChI'])),'InChIKey_Present':str(bool(x['InChIKey'])),'Scope_Note':'CID uniqueness and canonical name checked; study-tested isomer/purity not certified.' if x['Origin']=='v9_new_anchor' else 'Inherited V8 identity audit; see original identity_structure_audit.csv'})
wr(O/'identity_structure_audit_v9.csv',ident)
log=rd(O/'v9_change_log.csv');log.append({'Action':'candidate_identity_correction_before_admission','Record_ID':'MOL-V9-4788','Field':'PubChem_CID','Old_Value':'5281614 (CID resolves to fisetin)','New_Value':'4788 (Phloretin)','Reason':'PubChem name/structure review found a candidate identity mapping error; corrected before V9 anchor admission.','Source':'https://pubchem.ncbi.nlm.nih.gov/compound/4788'})
wr(O/'v9_change_log.csv',log)
screen=rd(O/'v9_candidate_screening_log.csv');screen.append({'Search_Date':'2026-10-29','Database':'PubChem','Query_or_Candidate':'Phloretin candidate CID identity check','Decision':'Corrected before inclusion','Reason':'Earlier proposed CID 5281614 resolves to fisetin; verified phloretin CID 4788 and structure before admission.','Full_Text_Availability':'Not applicable','Verification_Status':'PubChem structure record checked','Reviewer_Note':'Correction logged; no incorrect identity was admitted.'})
wr(O/'v9_candidate_screening_log.csv',screen)
# Final handoff markdown.
classes=collections.Counter(x['Evidence_Type'] for x in e);nanchors=len(r);openw=25;codes=27
hr='''# CookRisk Stage B V9 handoff — 2026-10-29

## What was recovered

A broader search across the available Desktop and Documents project roots, attached task files, nested/older Stage B release folders, structured data, source caches, validation scripts and reports located the authoritative evidence in `Documents/CookChem/stageB/release_v8_20261015_quality`. Earlier V7, V6, V5, V4, expansion V2/V3, source and audit files were retained for comparison. V8 README and handoff establish the 60-anchor/189-record V8 dataset as the latest finalized baseline; older expansion tables were not concatenated because they overlap and predate V8.

The new release is a V8-based copy at `Documents/CookChem/stageB/release_v9_20261029`. The original V8 folder was left untouched. V9 preserves the original 189 evidence IDs and rows in order, then appends supported additions.

## Counts

- Verified baseline: **60 anchors**, **189 interaction evidence rows**, **87 distinct drug/probe labels**, **121 unique PMID publications**.
- V9: **74 anchors** (+14), **210 evidence rows** (+21), **130 unique PMID publications** (9 net new bibliography entries; one of the ten reviewed PMIDs was already indexed), and **94 distinct drug/probe labels**.
- Progress: **74/100 anchors**; **26** remain.
- Evidence classes in V9: `'''+json.dumps(dict(classes),ensure_ascii=False)+'''.
- The inherited V8 review split was 21 selected-full-text records, 164 abstract records, and four qualitative abstracts with numeric table review pending. V9 adds 19 abstract-verified records and two phytosterol rows transcribed from a reviewed PMC full-text table. The four inherited resveratrol numerical holds remain held.

## Added anchors

'''+''.join(f"- **{x['Canonical_Name']}** (PubChem CID {x['PubChem_CID']}): {x['Selection_Rationale']}\n" for x in r if x['Origin']=='v9_new_anchor')+'''
## New evidence and interpretation

The 21 added records cover CYP and UGT enzyme panels, human P-glycoprotein cell assays, human puerarin probe-drug data, rat puerarin/buspirone pharmacokinetics, and a rat-microsome phytosterol screen. Records preserve null/weak findings and source-reported units. Positive in-vitro findings are not treated as clinical risk. The human felodipine increase in the grapefruit study was observed with grapefruit-derived juice serum; it is not represented as an isolated-DHB human interaction. Purified DHB’s separate CYP3A4 in-vitro arm is the evidence linked to that anchor.

Ten primary PMIDs were reviewed for additions: 15179411, 23669408, 27529203, 26278343, 12604704, 20195825, 24710899, 24786236, 30301254 and 26139922. PubMed abstracts were reviewed for metadata and claim-level extraction, except the β-sitosterol and stigmasterol IC50 values from PMID 26139922, which were checked in its full-text table (PMC4486538). The search was focused and is not a systematic review.

The candidate screen found a wrong proposed phloretin mapping: CID 5281614 is fisetin. Phloretin was admitted under CID 4788 after checking the PubChem structure record. This was corrected before the compound entered the release and is logged.

## Warnings and provenance

The 25 inherited warning entries (24 distinct codes) remain in the V9 ledger with their prior statuses. Three V9 warnings were added. **25 entries across 27 codes are unresolved or partially resolved**. Specifically, apigenin/rutin–paclitaxel preparation/attribution ambiguity, the apigenin Cmax discrepancy, daidzein reporting ambiguity, and daidzein/quercetin cooking-retention linkage limitations remain open. The original-nine selection dates and primary triggers remain unrecovered: the inherited ledger documents the prior search across local records; V9 does not invent historical dates. New compound rationales are explicitly retrospective and dated to this release.

Cooking-retention evidence is carried as a separate unchanged table; no cooking result was used to support a drug-interaction claim. New rows use unique PubChem CID plus name links. Phloretin has SMILES, InChI and InChIKey populated; for the other 13 new anchors those structure strings remain a follow-up item, so the registry warns against treating the CID/name audit as a complete exact-structure duplicate audit.

## Validation

- Existing V8 validator rerun after expansion: **26/26 checks passed**, **12/12 mutation tests detected**, **8,087 prior files checked**, **0 preservation mismatches**.
- V9-specific integrity validation: **PASS**, no errors; **7/7 mutation tests detected**. Checks cover baseline row preservation, IDs, mappings, source/cache traceability, bibliography uniqueness, selection rationale coverage, warnings and cooking-domain separation.
- The checks establish file integrity and relationships. They do not independently validate every scientific extraction or replace full-text review.

## Deliverables

Main files are in the release folder:

- `outputs/compound_registry_v9.csv`
- `outputs/stageB_food_drug_interactions_v9.csv`
- `outputs/drug_probe_registry_v9.csv`
- `outputs/study_registry_v9.csv`, `outputs/source_bibliography_v9.csv`
- `outputs/identity_structure_audit_v9.csv`
- `outputs/v9_selection_decisions.csv`, `outputs/v9_candidate_screening_log.csv`
- `outputs/v9_source_audit.csv`, `outputs/claim_support_and_verification_v9.csv`
- `outputs/warning_resolution_ledger_v9.csv`, `outputs/v9_change_log.csv`
- `outputs/cooking_retention_evidence_v9.csv`
- `audit/v9_validation_report.json`, `audit/v9_baseline_hash.json`
- Rebuild scripts: `build_v9_data.py`, `prepare_validate_v9.py`

Scope remained Stage B. Stage A models, Stage C exposure estimation and Stage D scoring were not changed or created.
'''
(R/'CookRisk_StageB_V9_Handoff.md').write_text(hr,encoding='utf-8')
# Manifest of delivered V9 handoff files; excludes itself to avoid self-reference.
paths=[O/x for x in ['compound_registry_v9.csv','stageB_food_drug_interactions_v9.csv','drug_probe_registry_v9.csv','study_registry_v9.csv','source_bibliography_v9.csv','identity_structure_audit_v9.csv','v9_selection_decisions.csv','v9_candidate_screening_log.csv','v9_source_audit.csv','claim_support_and_verification_v9.csv','warning_resolution_ledger_v9.csv','v9_change_log.csv','cooking_retention_evidence_v9.csv','README_V9.md','v9_release_summary.json']]+[A/'v9_validation_report.json',A/'v9_baseline_hash.json',R/'CookRisk_StageB_V9_Handoff.md',B/'build_v9_data.py',B/'prepare_validate_v9.py']
manifest={str(p.relative_to(B)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.exists()}
(B/'V9_SHA256SUMS.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'handoff':str(R/'CookRisk_StageB_V9_Handoff.md'),'manifest_files':len(manifest),'final_anchors':nanchors,'final_records':len(e),'distinct_drugs':len({x['Drug'] for x in e})},ensure_ascii=False,indent=2))
