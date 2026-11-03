"""Structural audit for CookRisk Stage B V17 (Python standard library only)."""
import csv, json, sys
from pathlib import Path

def table(root, rel):
    with (root/rel).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def inspect(root):
    root=Path(root); errors=[]; warnings=[]; checks=[]
    def err(code,record,detail):errors.append({'Code':code,'Record_ID':str(record),'Detail':detail})
    def warn(code,record,detail):warnings.append({'Code':code,'Record_ID':str(record),'Detail':detail})
    try:
        compounds=table(root,'data/compound_registry.csv'); evidence=table(root,'data/interaction_evidence.csv')
        drugs=table(root,'data/drug_probe_registry.csv'); studies=table(root,'data/study_registry.csv')
        pubs=table(root,'data/publication_bibliography.csv'); warnings_t=table(root,'data/warning_ledger.csv')
        identity=table(root,'identity/identity_structure_audit.csv')
        selections=table(root,'provenance/selection_decisions.csv'); sources=table(root,'provenance/source_audit.csv')
        claims=table(root,'provenance/claim_support_and_verification.csv')
        cooking=table(root,'data/cooking_retention_evidence.csv')
    except Exception as ex:
        return [{'Code':'FILE_READ','Record_ID':'','Detail':str(ex)}],[],[]
    def unique(rows,field,code,label):
        vals=[r.get(field,'').strip() for r in rows]
        dups=sorted(v for v in set(vals) if v and vals.count(v)>1)
        for v in dups:err(code,v,f'duplicate {label}: {v}')
        return set(v for v in vals if v)
    cids=unique(compounds,'Compound_ID','CMP_ID_DUP','compound ID')
    eids=unique(evidence,'Evidence_ID','EVI_ID_DUP','evidence ID')
    dlabels=unique(drugs,'Drug_Probe','DRUG_LABEL_DUP','drug/probe label')
    sids=unique(studies,'Study_ID','STUDY_ID_DUP','study ID')
    pmids=unique(pubs,'PMID','PUB_PMID_DUP','bibliography PMID')
    unique(warnings_t,'Warning_ID','WARNING_ID_DUP','warning ID')
    # V17 uses the full warning lifecycle vocabulary; preserve the legacy
    # values for historical rows while accepting the explicit V17 states.
    valid_warning_status={'Unresolved','Partially resolved','Resolved','Not applicable',
      'RESOLVED','PARTIALLY_RESOLVED','STILL_VALID','NEEDS_MANUAL_REVIEW','NOT_APPLICABLE'}
    for r in warnings_t:
        # V17's ``After`` is a narrative field for new warnings. Validate the
        # structured lifecycle status instead; keep legacy status checks too.
        after=r.get('After','')
        structured=r.get('Audit_Status','')
        if after not in valid_warning_status and structured not in valid_warning_status:
            err('WARNING_STATUS',r.get('Warning_ID',''),'unsupported warning status')
    for r in studies:
        if r.get('PMID','').strip() and r['PMID'].strip() not in pmids:err('STUDY_PUBLICATION',r.get('Study_ID',''),'study PMID does not resolve in bibliography')
    unique(identity,'Compound_ID','IDENTITY_ROW_DUP','identity compound ID')
    for r in compounds:
        cid=r.get('Compound_ID','')
        if not cid or not r.get('Canonical_Name','').strip():err('CMP_REQUIRED',cid,'missing stable ID or standardized name')
        if not r.get('Food_Context','').strip():warn('FOOD_CONTEXT_MISSING',cid,'food context is blank')
        if not r.get('Selection_Rationale','').strip():warn('SELECTION_MISSING',cid,'selection rationale is blank')
    for r in evidence:
        eid=r.get('Evidence_ID','')
        if r.get('Compound_ID','') not in cids:err('FK_COMPOUND',eid,'Compound_ID does not resolve')
        if r.get('Drug','') not in dlabels:err('FK_DRUG',eid,'Drug/probe label does not resolve')
        if not r.get('Study_ID','').strip() or r.get('Study_ID') not in sids:err('FK_STUDY',eid,'Study_ID missing or unresolved')
        if r.get('PMID','').strip() and not r['PMID'].strip().isdigit():err('PMID_FORMAT',eid,'PMID must contain digits only')
        if r.get('PMID','').strip() and r['PMID'].strip() not in pmids:err('FK_PUBLICATION',eid,'PMID does not resolve in bibliography')
        if r.get('DOI','').strip() and not r['DOI'].strip().lower().startswith('10.'):err('DOI_FORMAT',eid,'DOI does not begin with a DOI registrant prefix')
        if r.get('Evidence_Type','') not in {'Human pharmacokinetic','Controlled clinical','Other human clinical','Animal','In vitro'}:err('EVIDENCE_CLASS',eid,'unsupported evidence class')
        if not r.get('Source_URL','').strip() or not r.get('Source_Locator','').strip():warn('SOURCE_LOCATOR_MISSING',eid,'source URL or locator is blank')
        if not r.get('Quantitative_Outcome','').strip():warn('OUTCOME_MISSING',eid,'outcome description is blank')
        q=r.get('Quantitative_Outcome','')
        if any(ch.isdigit() for ch in q) and not any(u in q.lower() for u in ('μ','µ','mcg','mg','g/','/ml','%','fold','auc','cmax','p<','p =','ki','ic50','nm','mm','hours','days')):
            warn('NUMERIC_UNIT_REVIEW',eid,'numeric outcome text has no readily identifiable unit/statistic; review manually')
    claim_ids={r.get('Evidence_ID','') for r in claims if r.get('Evidence_ID','')}
    source_ids={r.get('Evidence_ID','') for r in sources if r.get('Evidence_ID','')}
    for r in evidence:
        eid=r.get('Evidence_ID','')
        if eid not in claim_ids:err('CLAIM_MISSING',eid,'no claim-support/verification row')
        if eid not in source_ids:warn('SOURCE_AUDIT_MISSING',eid,'no source-audit row')
    selection_names={r.get('Candidate','').strip().casefold() for r in selections if r.get('Candidate','').strip()}
    for r in compounds:
        if r.get('Origin','') in {'v12_controlled_expansion','v11_controlled_expansion','v10_controlled_expansion'} and r.get('Canonical_Name','').strip().casefold() not in selection_names:
            warn('SELECTION_ROW_MISSING',r.get('Compound_ID',''),'no selection decision matched the anchor name')
    keys=[r.get('Registry_InChIKey','').strip() for r in identity if r.get('Registry_InChIKey','').strip()]
    for key in sorted(set(k for k in keys if keys.count(k)>1)):warn('IDENTITY_DUP_KEY',key,'duplicate InChIKey; expert chemical adjudication required')
    contexts={}
    for r in evidence:
        key=(r.get('Compound_ID',''),r.get('Drug',''),r.get('Study_ID',''),r.get('Interaction_Effect',''),r.get('Quantitative_Outcome',''))
        if key in contexts:warn('DUPLICATE_CONTEXT',r.get('Evidence_ID',''),f'context overlaps {contexts[key]}; inspect source/arm before merging')
        else:contexts[key]=r.get('Evidence_ID','')
    cooking_ids={r.get('Evidence_ID','').strip() for r in cooking if r.get('Evidence_ID','').strip()}
    for eid in sorted(eids & cooking_ids):err('DOMAIN_ID_COLLISION',eid,'cooking-retention row shares an interaction evidence ID')
    metadata_path=root/'release_metadata.json'
    metadata=json.loads(metadata_path.read_text(encoding='utf-8')) if metadata_path.exists() else {'expected_compounds':119,'expected_evidence':286,'release':'StageB_Final'}
    if len(compounds)!=metadata['expected_compounds']:warn('EXPECTED_COMPOUND_COUNT','',f"anchor count is {len(compounds)}, release metadata expects {metadata['expected_compounds']}")
    if len(evidence)!=metadata['expected_evidence']:warn('EXPECTED_EVIDENCE_COUNT','',f"evidence count is {len(evidence)}, release metadata expects {metadata['expected_evidence']}")
    # Named assertions make results interpretable; warnings are not failures.
    checks=[('STRUCT-CMP-ID','Unique compound identifiers',not any(x['Code']=='CMP_ID_DUP' for x in errors)),
      ('STRUCT-EVI-ID','Unique evidence identifiers',not any(x['Code']=='EVI_ID_DUP' for x in errors)),
      ('REF-01','Compound foreign keys resolve',not any(x['Code']=='FK_COMPOUND' for x in errors)),
      ('REF-02','Drug/probe foreign keys resolve',not any(x['Code']=='FK_DRUG' for x in errors)),
      ('REF-03','Study foreign keys resolve',not any(x['Code']=='FK_STUDY' for x in errors)),
      ('PUB-01','PMID and DOI formatting/references',not any(x['Code'] in {'PMID_FORMAT','DOI_FORMAT','FK_PUBLICATION'} for x in errors)),
      ('EVI-CLASS','Evidence class values supported',not any(x['Code']=='EVIDENCE_CLASS' for x in errors)),
      ('CLAIM-01','Evidence has source-claim support',not any(x['Code']=='CLAIM_MISSING' for x in errors)),
      ('WARN-01','Warning IDs unique',not any(x['Code']=='WARNING_ID_DUP' for x in errors)),
      ('WARN-02','Warning status vocabulary valid',not any(x['Code']=='WARNING_STATUS' for x in errors)),
      ('PUB-02','Study publications resolve',not any(x['Code']=='STUDY_PUBLICATION' for x in errors)),
      ('DOMAIN-01','Cooking-retention IDs remain separate',not any(x['Code']=='DOMAIN_ID_COLLISION' for x in errors)),
      ('IDENT-01','Identity key uniqueness screen',not any(x['Code']=='IDENTITY_DUP_KEY' for x in warnings)),
      ('SEL-01','Selection rationale coverage screened',not any(x['Code']=='SELECTION_MISSING' for x in warnings)),
      ('DUP-01','Repeated evidence contexts surfaced',True),
      ('NUM-01','Numerical/unit review flags surfaced',True)]
    return errors,warnings,checks

def main(root):
    root=Path(root).resolve();errors,warnings,checks=inspect(root)
    metadata_path=root/'release_metadata.json'
    metadata=json.loads(metadata_path.read_text(encoding='utf-8')) if metadata_path.exists() else {'release':'StageB_Final'}
    report={'release':metadata.get('release','StageB_Final'),'status':'PASS_WITH_WARNINGS' if not errors else 'FAIL',
      'automated_checks':len(checks),'passed':sum(bool(x[2]) for x in checks),'failed':sum(not x[2] for x in checks),
      'errors':errors,'warnings':warnings,'checks':[{'Test_ID':a,'Purpose':b,'Status':'PASS' if ok else 'FAIL'} for a,b,ok in checks]}
    out=root/'validation/final_validation_results.json';out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    with (root/'validation/final_validation_results.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['Test_ID','Purpose','Status']);w.writeheader();w.writerows(report['checks'])
    print(json.dumps({'status':report['status'],'checks':len(checks),'passed':report['passed'],'failed':report['failed'],'errors':len(errors),'warnings':len(warnings)},indent=2))
    return 1 if errors else 0
if __name__=='__main__':raise SystemExit(main(sys.argv[1] if len(sys.argv)>1 else '.'))
