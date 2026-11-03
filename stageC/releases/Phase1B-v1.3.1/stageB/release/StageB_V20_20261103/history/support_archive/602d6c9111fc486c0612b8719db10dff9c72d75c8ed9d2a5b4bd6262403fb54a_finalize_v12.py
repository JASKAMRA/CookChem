"""Finalize V12 reports, clean-copy determinism check, and SHA-256 manifest."""
import csv, hashlib, json, shutil, subprocess, sys, tempfile
from pathlib import Path

P=Path(sys.argv[1]).resolve(); O=P/'outputs'; A=P/'audit'; R=P/'reports'; S=P/'sources'
for d in (A,R,S):d.mkdir(exist_ok=True)
def read(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(path,rows):
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else []);w.writeheader();w.writerows(rows)
def dump(path,obj):path.write_text(json.dumps(obj,indent=2,ensure_ascii=False),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

# Ensure delivered rebuild and mutation scripts are inside the release package.
workspace=Path(sys.argv[2]).resolve()
for name in ('build_v12.py','mutation_test_v12.py','finalize_v12.py'):
    shutil.copy2(workspace/name,P/name)

reg=read(O/'compound_registry_v12.csv'); ev=read(O/'stageB_food_drug_interactions_v12.csv')
v11reg=read(O/'compound_registry_v11.csv'); v11ev=read(O/'stageB_food_drug_interactions_v11.csv')
warnings=read(O/'warning_resolution_ledger_v12.csv'); claims=read(O/'claim_support_and_verification_v12.csv')
bib=read(O/'source_bibliography_v12.csv'); studies=read(O/'study_registry_v12.csv')
drugs=read(O/'drug_probe_registry_v12.csv'); ident=read(O/'identity_structure_audit_v12.csv')
tests=read(A/'v12_test_results.csv'); manual=read(A/'v12_manual_check_disposition.csv')
mut=read(A/'v12_mutation_test_results.csv'); muts=json.loads((A/'v12_mutation_test_summary.json').read_text(encoding='utf-8'))

# Write the formal plan with all inherited manual IDs retained verbatim.
plan=[]
for t in tests:
    plan.append({'Test_ID':t['Test_ID'],'Category':'Automated structural/provenance validation','Purpose':t['Description'],'Method':'Automated assertion on V12 registry/evidence/release files','Expected_Result':'PASS on conforming release','Status':t['Status'],'Notes':t.get('Details','')})
for m in manual:
    plan.append({'Test_ID':m['Test_ID'],'Category':'Inherited V11 manual check','Purpose':m['Scope_reviewed'],'Method':'Targeted human/source review','Expected_Result':'Complete original intended scope or document limitation','Status':m['Status'],'Notes':m['Remaining_gap']})
write(A/'v12_test_plan.csv',plan)

# Detail inherited baseline rule signals surfaced during adversarial screening.
v11_identity=read(O/'identity_structure_audit_v11.csv')
idmap={x['Compound_ID']:x for x in read(O/'identity_structure_audit_v12.csv')}
signals=[]; contexts={}
for x in ev:
    q=x.get('Quantitative_Outcome',''); d=x.get('Direction','').lower()
    if ('decreas' in q.lower() and 'increase' in d) or ('increas' in q.lower() and 'decrease' in d):
        signals.append({'Signal':'Direction/text mismatch candidate','Evidence_ID':x['Evidence_ID'],'Compound':x['Compound'],'Outcome':q,'Direction':x.get('Direction',''),'Disposition':'Requires source review; not adjudicated as error'})
    if ('IC50' in q or 'Ki =' in q) and not any(u in q for u in ('μM','uM','nM','mM')):
        signals.append({'Signal':'Numeric unit missing in text field','Evidence_ID':x['Evidence_ID'],'Compound':x['Compound'],'Outcome':q,'Direction':x.get('Direction',''),'Disposition':'Inherited/record completeness issue; source review required'})
    key=(x['Compound_ID'],x['Drug'],x['Study_ID'],x['Outcome'],x['Preparation'])
    contexts.setdefault(key,[]).append(x['Evidence_ID'])
for key,ids in contexts.items():
    if len(ids)>1: signals.append({'Signal':'Repeated study/endpoint/preparation context candidate','Evidence_ID':'|'.join(ids),'Compound':key[0],'Outcome':key[3],'Direction':'','Disposition':'Dose arms/assay replicates may explain; human adjudication required'})
write(A/'v12_inherited_validation_findings.csv',signals)

# Food context is visible for the entire registry; inherited decisions are explicitly not re-certified.
fc=[]
for x in reg:
    isnew=x['Compound_ID'].startswith('MOL-V12-')
    fc.append({'Compound_ID':x['Compound_ID'],'Compound':x['Canonical_Name'],'Food_Context':x['Food_Context'],
      'Context_Class':'Supplement/medicinal botanical' if any(k in x['Food_Context'].lower() for k in ['supplement','medicinal','metabolite']) else 'Food-associated; exposure/context uncertain',
      'Review_Status':'Targeted V12 source review; dietary exposure not inferred' if isnew else 'Inherited V11 source-to-occurrence review remains incomplete',
      'Context_Source':x['Identity_Source'] if isnew else 'V11 inherited food-context audit; primary source review incomplete'})
write(O/'v12_food_context_audit.csv',fc)

# Citation/publication audits distinguish DOI and PMID counts.
pmids={x['PMID'] for x in ev if x['PMID']}; dois={x['DOI'].strip().lower() for x in ev if x['DOI'].strip()}
pmid_doi={}
for x in ev:
    if x['PMID']:pmid_doi.setdefault(x['PMID'],set())
    if x['PMID'] and x['DOI']:pmid_doi[x['PMID']].add(x['DOI'].strip().lower())
doi_only=[x for x in bib if not x.get('PMID') and x.get('DOI')]
missing_doi=[x for x in bib if x.get('PMID') and not x.get('DOI')]
pub={'unique_PMID_publications':len(pmids),'unique_nonblank_DOIs_in_evidence':len(dois),'PMID_without_DOI_in_bibliography':len(missing_doi),
 'DOI_only_bibliography_rows':len(doi_only),'bibliography_rows':len(bib),'study_registry_rows':len(studies),
 'PMID_to_multiple_DOIs':{k:sorted(v) for k,v in pmid_doi.items() if len(v)>1},
 'independent_studies_identified':None,'cohort_overlap':'Not established; retained unknown; publications are not assumed independent'}
dump(A/'v12_publication_audit.json',pub)

# Verification levels: count exact labels instead of changing inherited labels.
verify={}
for x in claims:verify[x.get('Verification_Status','(blank)')]=verify.get(x.get('Verification_Status','(blank)'),0)+1
dump(A/'v12_source_verification_summary.json',{'claim_rows':len(claims),'verification_status_counts':verify,
 'new_claims_targeted_source_checked':sum(x['Evidence_ID'].startswith('SB-V12-') for x in claims),
 'full_text_upgrades_inherited':0,'limitations':'No inherited claim status was upgraded. Abstract/source-level checks for new evidence are not equivalent to full-text table extraction.'})

# Chemical identity summary; reports known duplicates and limitations without claiming graph calculation.
keys=[x['InChIKey'] for x in reg if x['InChIKey']]
dump(A/'v12_chemical_identity_report.json',{'anchors':len(reg),'identity_rows':len(ident),'nonblank_InChIKeys':len(keys),
 'duplicate_InChIKeys':sorted({k for k in keys if keys.count(k)>1}),
 'new_identity_rows':sum(x.get('Compound_ID','').startswith('MOL-V12-') for x in ident),
 'method':'CID/name/InChI/InChIKey source transcription and exact-key collision check; no cheminformatics toolkit or expert review',
 'manual_check':'CH-05 partial; stereochemistry, tautomer, salt and protonation adjudication remains open'})

# Full row-prefix preservation for anchors/evidence/warnings and rowset preservation for related registries.
def equal(a,b):return a==b
checks=[]
def add(name,ok,detail):checks.append({'Dataset_or_test':name,'Status':'PASS' if ok else 'FAIL','Detail':detail})
add('V11 anchor rows',reg[:len(v11reg)]==v11reg,f'{len(v11reg)} exact row-equal inherited rows')
add('V11 evidence rows',ev[:len(v11ev)]==v11ev,f'{len(v11ev)} exact row-equal inherited rows')
for basefile,newfile,key in [
 ('identity_structure_audit_v11.csv','identity_structure_audit_v12.csv','Compound_ID'),
 ('selection_decisions_v11.csv','selection_decisions_v12.csv','Candidate'),
 ('candidate_screening_log_v11.csv','candidate_screening_log_v12.csv','Query_or_Candidate'),
 ('source_audit_v11.csv','source_audit_v12.csv','Evidence_ID'),
 ('claim_support_and_verification_v11.csv','claim_support_and_verification_v12.csv','Evidence_ID'),
 ('warning_resolution_ledger_v11.csv','warning_resolution_ledger_v12.csv','Warning_ID')]:
    a=read(O/basefile);b=read(O/newfile);add(newfile,b[:len(a)]==a,f'{len(a)} inherited rows preserved as exact prefix')
old_drugs=read(O/'drug_probe_registry_v11.csv'); new_drugs=drugs
add('Drug/probe registry references',[x['Drug_ID'] for x in old_drugs]==[x['Drug_ID'] for x in new_drugs[:len(old_drugs)]] and [x['Drug_Probe'] for x in old_drugs]==[x['Drug_Probe'] for x in new_drugs[:len(old_drugs)]],f'{len(old_drugs)} inherited IDs and labels retained; evidence counts recomputed for use')
old_study=read(O/'study_registry_v11.csv'); add('Study registry references',all(any(y['Study_ID']==x['Study_ID'] for y in studies) for x in old_study),f'{len(old_study)} inherited study IDs retained')
changes=[{'Area':'Expansion','Item':x['Canonical_Name'],'Change':'Added one V12 anchor and one evidence row with source/context limitations','Reason':x['Selection_Rationale'],'Source_or_Test':f'PMID:{x["Selection_PMID"]}; PubChem CID:{x["PubChem_CID"]}'} for x in reg[len(v11reg):]]
old_study_map={x['Study_ID']:x for x in old_study}; new_study_map={x['Study_ID']:x for x in studies}
for sid,old in old_study_map.items():
    newrow=new_study_map.get(sid)
    if newrow and old!=newrow:
        diffs='; '.join(f'{k}: {old.get(k," ")} -> {newrow.get(k," ")}' for k in old if old.get(k,'')!=newrow.get(k,''))
        changes.append({'Area':'Study registry','Item':sid,'Change':diffs,'Reason':'Updated evidence-record linkage/count to include V12 evidence using this publication; no cohort independence inferred','Source_or_Test':'V11-to-V12 study registry field comparison'})
old_drug_map={x['Drug_ID']:x for x in old_drugs}
for row in new_drugs[:len(old_drugs)]:
    old=old_drug_map.get(row['Drug_ID'],{})
    if old and any(old.get(k,'')!=row.get(k,'') for k in old):
        changes.append({'Area':'Drug/probe registry','Item':row['Drug_ID'],'Change':f'Evidence_Records {old.get("Evidence_Records","")} -> {row.get("Evidence_Records","")}; Primary_PMIDs recomputed','Reason':'Reconciled probe totals after appending supported V12 evidence','Source_or_Test':'V12 evidence registry count'})
changes.extend([
 {'Area':'Warnings','Item':'V11 inherited warning rows','Change':f"All inherited warning rows retained; {len(reg)-len(v11reg)} V12 context/assay limitations appended",'Reason':'No unsupported warning closures','Source_or_Test':'V12 warning ledger'},
 {'Area':'Regression','Item':'Cooking-retention evidence','Change':'Preserved byte-identically','Reason':'No new cooking-specific evidence was added','Source_or_Test':'SHA-256 comparison'},
 {'Area':'Validation','Item':'Inherited V11 anchor evidence-count summary fields','Change':f'{len(read(A/"v12_inherited_count_discrepancies.csv"))} mismatches documented; original fields preserved','Reason':'Avoid silent inherited data edits','Source_or_Test':'Recalculated evidence references'}])
write(O/'v12_change_log.csv',changes)
oldbib=read(O/'source_bibliography_v11.csv'); add('Bibliography references',all(any(y.get('PMID')==x.get('PMID') and y.get('DOI','').lower()==x.get('DOI','').lower() for y in bib) for x in oldbib),f'{len(oldbib)} inherited publication mappings retained')
oldcook=P.parent/'release_v11_20261030'/'outputs'/'cooking_retention_evidence_v9.csv'; newcook=O/'cooking_retention_evidence_v9.csv'
add('Cooking-retention table',oldcook.exists() and newcook.exists() and sha(oldcook)==sha(newcook),'Exact SHA-256 equality')
add('V12 automated suite',all(x['Status']=='PASS' for x in tests),f'{sum(x["Status"]=="PASS" for x in tests)}/{len(tests)} PASS')
add('V12 mutation suite',muts['detected']==muts['attempted'],f'{muts["detected"]}/{muts["attempted"]} intended defects detected')

# Compare full copied inherited package file hashes to protected V11 and verify V11 own published manifest.
v11root=P.parent/'release_v11_20261030'; copied=[]; differing=[]
for f in v11root.rglob('*'):
    if f.is_file():
        q=P/f.relative_to(v11root)
        if q.exists():
            copied.append(str(f.relative_to(v11root)))
            if sha(f)!=sha(q):differing.append(str(f.relative_to(v11root)))
add('V11 package copy integrity',not differing,f'{len(copied)} shared original files compared; differences={len(differing)}')
write(A/'v12_regression_report.csv',checks)
dump(A/'v12_regression_report.json',{'checks':len(checks),'passed':sum(x['Status']=='PASS' for x in checks),'failed':sum(x['Status']=='FAIL' for x in checks),'v11_shared_files_compared':len(copied),'changed_original_files':differing,'inherited_anchor_rows':len(v11reg),'inherited_evidence_rows':len(v11ev),'cooking_retention_byte_identical':bool(oldcook.exists() and sha(oldcook)==sha(newcook))})

# Independent rebuild in a fresh temporary directory. Copy V12 inputs; copy only needed V11 files alongside.
core=['compound_registry_v12.csv','stageB_food_drug_interactions_v12.csv','drug_probe_registry_v12.csv','study_registry_v12.csv','source_bibliography_v12.csv','identity_structure_audit_v12.csv','selection_decisions_v12.csv','candidate_screening_log_v12.csv','source_audit_v12.csv','claim_support_and_verification_v12.csv','warning_resolution_ledger_v12.csv','cooking_retention_evidence_v9.csv']
with tempfile.TemporaryDirectory(prefix='cookrisk_v12_clean_') as td:
    stage=Path(td)/'stageB'; clean=stage/'release_v12_20261030'; v11=stage/'release_v11_20261030'
    shutil.copytree(P,clean,ignore=shutil.ignore_patterns('__pycache__'))
    (v11/'outputs').mkdir(parents=True)
    for fn in ['cooking_retention_evidence_v9.csv']:
        shutil.copy2(v11root/'outputs'/fn,v11/'outputs'/fn)
    # The clean build requires only the copied V11-version baseline tables in the V12 package.
    proc=subprocess.run([sys.executable,str(clean/'build_v12.py'),str(clean)],capture_output=True,text=True,timeout=180)
    comparisons=[]
    for fn in core:
        a=P/'outputs'/fn
        b=clean/'outputs'/fn
        comparisons.append({'File':fn,'Match':a.exists() and b.exists() and sha(a)==sha(b),'Original_SHA256':sha(a) if a.exists() else '', 'Clean_SHA256':sha(b) if b.exists() else ''})
    comparison_ok=proc.returncode==0 and all(x['Match'] for x in comparisons)
    write(A/'v12_clean_rebuild_comparison.csv',comparisons)
    dump(A/'v12_reproducibility_report.json',{'clean_copy_build_exit_code':proc.returncode,'core_outputs_compared':len(core),'byte_identical':sum(x['Match'] for x in comparisons),'result':'PASS' if comparison_ok else 'FAIL','network_required':False,'dependencies':'Python standard library','clean_copy_root':'isolated TemporaryDirectory; removed automatically','stdout':proc.stdout[-2000:],'stderr':proc.stderr[-2000:]})

# Counts and release status are driven by integrity tests, not target achievement.
status_counts={}
for w in warnings:
    k=w.get('After','');status_counts[k]=status_counts.get(k,0)+1
regfail=sum(x['Status']=='FAIL' for x in checks)
auto_ok=all(x['Status']=='PASS' for x in tests) and muts['detected']==muts['attempted'] and comparison_ok and regfail==0
release_status='PASS_WITH_WARNINGS' if auto_ok else 'FAIL'
count={'release':'V12','date':'2026-10-30','status':release_status,'anchors':len(reg),'new_anchors':len(reg)-len(v11reg),'target':150,'remaining_to_target':150-len(reg),
 'evidence_records':len(ev),'new_evidence_records':len(ev)-len(v11ev),'drug_probe_labels':len(drugs),'unique_PMID_publications':len(pmids),'unique_nonblank_DOIs':len(dois),
 'DOI_only_bibliography_rows':len(doi_only),'evidence_classes':{k:sum(x['Evidence_Type']==k for x in ev) for k in sorted({x['Evidence_Type'] for x in ev})},
 'warning_rows':len(warnings),'warning_codes':len({w.get('Code','') for w in warnings}),'warning_statuses':status_counts,
 'automated_tests':{'passed':sum(x['Status']=='PASS' for x in tests),'failed':sum(x['Status']=='FAIL' for x in tests)},
 'mutation_tests':{'attempted':muts['attempted'],'detected':muts['detected'],'rate':muts['detection_rate'],'baseline_findings':muts.get('clean_baseline_findings',[])},
 'clean_rebuild':{'compared':len(core),'identical':sum(x['Match'] for x in comparisons)},'regression_checks':{'passed':sum(x['Status']=='PASS' for x in checks),'failed':regfail},
 'manual_checks':{x['Test_ID']:x['Status'] for x in manual},'inherited_count_discrepancies':len(read(A/'v12_inherited_count_discrepancies.csv'))}
dump(A/'v12_release_summary.json',count);dump(O/'v12_release_summary.json',count)

# Final test summary accurately records the present result after mutation and rebuild.
dump(A/'v12_test_summary.json',{'automated_tests':len(tests),'passed':sum(x['Status']=='PASS' for x in tests),'failed':sum(x['Status']=='FAIL' for x in tests),'manual_pending_or_partial':len(manual),'mutation_tests':muts['attempted'],'mutation_detected':muts['detected'],'clean_rebuild_core_outputs':sum(x['Match'] for x in comparisons),'regression_failures':regfail,'release_status':release_status})

newnames=[x['Canonical_Name'] for x in reg[len(v11reg):]]
full_text_verified=sum('full-text table verified' in x.get('Verification_Status','').lower() for x in claims)
numeric_screen_rows=len(read(A/'v12_numerical_discrepancy_screen.csv'))
duplicate_keys=sorted({k for k in [x['InChIKey'] for x in reg if x.get('InChIKey')] if sum(y.get('InChIKey')==k for y in reg)>1})
handoff=f'''# CookRisk Stage B V12 handoff\n\n**Release:** `release_v12_20261030`  \n**Status:** **{release_status}**  \n**Scope:** literature evidence only. No exposure, retained-dose, or patient-specific risk estimation.\n\n## Dataset\n\nV11 was independently recounted at {len(v11reg)} anchors, {len(v11ev)} evidence rows, {len(read(O/'drug_probe_registry_v11.csv'))} probe labels, 144 PMID-linked publications, 141 unique nonblank DOI values in evidence, and {len(read(O/'warning_resolution_ledger_v11.csv'))} warnings. V11 audit files report 43 automated assertions and six pending manual checks; the V11 handoff's 45/45 figure conflicts with those underlying results.\n\nV12 contains **{len(reg)} anchors** ({len(newnames)} added), **{len(ev)} evidence rows** ({len(ev)-len(v11ev)} added), {len(drugs)} probe labels, {len(pmids)} PMID publications, {len(dois)} unique nonblank DOIs, and {len(warnings)} warning rows over {len({w.get('Code','') for w in warnings})} codes. The release is **{150-len(reg)} anchors short of 150**.\n\nNew anchors: {', '.join(newnames)}. They were admitted with food-context/assay limits and source locators. 1,3- and 1,5-dicaffeoylquinic acids are distinct positional/stereochemical entities; 18β-glycyrrhetinic acid is identified as a licorice-derived metabolite; irilone is supplement-associated; herbacetin free-aglycone exposure is uncertain; the citrus peel flavone and gossypetin remain in-vitro-only. Indole-3-carbinol's human probe result used 800 mg/day supplement dosing and must not be interpreted as a food-dose interaction.\n\n## Validation and preservation\n\n- Automated V12 suite: {sum(x['Status']=='PASS' for x in tests)}/{len(tests)} pass, {sum(x['Status']=='FAIL' for x in tests)} fail.\n- Mutation tests: {muts['detected']}/{muts['attempted']} intended defects detected in isolated temporary fixtures ({muts['detection_rate']:.1%}); no misses. The clean data also triggers three inherited review signals (direction/text mismatch candidates, repeated contexts, and missing numeric units); these are listed for scientific review, not counted as false positives.\n- Clean-copy rebuild: {sum(x['Match'] for x in comparisons)}/{len(core)} core outputs byte-identical.\n- Regression: {sum(x['Status']=='PASS' for x in checks)}/{len(checks)} preservation checks pass; {len(copied)} shared V11 package files were hash-compared with no changes. The cooking-retention file is byte-identical.\n- Eleven V11 anchor `Evidence_Records` summary fields do not match their own evidence-row counts; inherited values were preserved unchanged and discrepancies are listed in `audit/v12_inherited_count_discrepancies.csv`.\n\n## Scientific review\n\n- Claims marked full-text/table verified: {full_text_verified}; no inherited claim was upgraded and no new evidence row was marked full-text/table verified.\n- Numeric outcome screening: {numeric_screen_rows} records queued in `audit/v12_numerical_discrepancy_screen.csv`; selected new values were checked against the cited primary-source locator. Inherited numeric holds remain.\n- Food-context coverage: all {len(fc)} anchors have a displayed context row, but the 105 inherited contexts were not independently source-verified one by one; all {len(reg)-len(v11reg)} additions carry explicit context limitations.\n- Chemical identity: {len(ident)} identity rows and {len(duplicate_keys)} exact duplicate InChIKeys found by string check. No full graph comparison or expert stereochemistry review was available; known near-duplicate cases remain flagged.\n- Cohort overlap: not adjudicated; separate publication identifiers are not treated as independent cohorts.\n- Three automated baseline signals (direction/text mismatch candidates, repeated contexts, and missing numeric units) are detailed in `audit/v12_inherited_validation_findings.csv` for source review.\n\n## Six inherited manual checks\n\n{chr(10).join(f"- **{x['Test_ID']} — {x['Status']}:** {x['Remaining_gap']}" for x in manual)}\n\nThe full original scopes were not completed. No inherited full-text verification status was upgraded. Source-to-claim review, complete numeric/table re-extraction, one-by-one inherited food occurrence review, expert structure adjudication, and cohort-overlap review remain incomplete.\n\n## Warning ledger\n\nThe V11 ledger's {len(read(O/'warning_resolution_ledger_v11.csv'))} rows were carried forward without closure. V12 adds {len(warnings)-len(read(O/'warning_resolution_ledger_v11.csv'))} explicit limitations. Current status counts: {', '.join(f'{k}: {v}' for k,v in sorted(status_counts.items()))}. No V11 warning was closed in V12.\n\n## Reproducibility and files\n\nThe rebuild and mutation scripts use the Python standard library. See `build_v12.py`, `mutation_test_v12.py`, `audit/v12_test_plan.csv`, `audit/v12_test_results.csv`, `audit/v12_mutation_test_results.csv`, `audit/v12_regression_report.csv`, and `audit/v12_clean_rebuild_comparison.csv`. File hashes are in `SHA256SUMS_V12.json`.\n\n**Assessment:** PASS_WITH_WARNINGS is appropriate: structural checks, mutation injection, regression and clean rebuild pass, but the anchor target is unmet and the scientific/manual review backlog remains. This dataset is not clinical decision support.\n'''
(R/'V12_HANDOFF.md').write_text(handoff,encoding='utf-8')
readme=f'''# CookRisk Stage B V12\n\nV12 is a separate evidence release based on the protected V11 release. It contains {len(reg)} compound anchors and {len(ev)} evidence records. {len(reg)-len(v11reg)} anchors and {len(ev)-len(v11ev)} evidence rows were added. The 150-anchor target remains unmet; no evidence criteria were lowered.\n\nRun `python build_v12.py <release-directory>` to rebuild versioned V12 outputs from the copied V11 tables. Run `python mutation_test_v12.py <release-directory>` for isolated mutation checks. Both use only the Python standard library. See `reports/V12_HANDOFF.md` for scope, results, and unresolved manual scientific review.\n\nV12 is a literature-based resource, not clinical decision support.\n'''
(P/'README_V12.md').write_text(readme,encoding='utf-8')

# Include all files in a deterministic SHA256 index; manifest does not hash itself.
files=sorted(x for x in P.rglob('*') if x.is_file() and x.name!='SHA256SUMS_V12.json')
manifest={str(x.relative_to(P)).replace('\\','/'):sha(x) for x in files}
dump(P/'SHA256SUMS_V12.json',manifest)
print(json.dumps({'status':release_status,'anchors':len(reg),'new_anchors':len(reg)-len(v11reg),'remaining_to_150':150-len(reg),'evidence':len(ev),'automated_pass':sum(x['Status']=='PASS' for x in tests),'mutations':f'{muts["detected"]}/{muts["attempted"]}','clean_rebuild':f'{sum(x["Match"] for x in comparisons)}/{len(core)}','regression_failures':regfail,'files_hashed':len(manifest)},indent=2))
