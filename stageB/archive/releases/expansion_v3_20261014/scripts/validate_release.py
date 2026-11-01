"""Offline validation. Exit nonzero for errors; unresolved provenance remains visible."""
from pathlib import Path
import csv,json,re,hashlib,collections,html,sys
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[1];B=ROOT/'stageB'
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(evidence,registry,baseline):
    errors=[];warnings=[];checks=[]
    def check(name,ok,detail=''):
        checks.append({'check':name,'passed':bool(ok),'detail':detail})
        if not ok:errors.append({'check':name,'detail':detail})
    def warn(code,detail,ids=None):warnings.append({'code':code,'detail':detail,'ids':ids or []})
    check('schema_36_columns_preserved',all(list(r)==list(baseline[0]) for r in evidence) and len(evidence[0])==36)
    check('evidence_ids_unique',len({r['Evidence_ID'] for r in evidence})==len(evidence))
    check('evidence_id_format',all(re.fullmatch(r'SB-\d{4}',r['Evidence_ID']) for r in evidence))
    check('compound_ids_unique',len({r['Compound_ID'] for r in registry})==len(registry))
    check('canonical_names_unique',len({r['Canonical_Name'].casefold() for r in registry})==len(registry))
    check('standardized_identity_keys_unique',len({r['InChIKey'] for r in registry})==len(registry) and all(r['InChIKey'] for r in registry))
    reg={r['Compound_ID']:r for r in registry}
    check('compound_evidence_foreign_keys',all(r['Compound_ID'] in reg and reg[r['Compound_ID']]['Canonical_Name']==r['Compound'] for r in evidence))
    check('no_exact_context_duplicates',len({tuple(r[k] for k in ['Study_ID','Compound_ID','Drug','Evidence_Type','Preparation','Co_Compounds']) for r in evidence})==len(evidence))
    got={r['Evidence_ID']:r for r in evidence}
    check('baseline_64_rows_unchanged',len(baseline)==64 and all(got.get(r['Evidence_ID'])==r for r in baseline))
    check('primary_identifiers_format',all(re.fullmatch(r'\d{5,9}',r['PMID']) and (not r['DOI'] or re.fullmatch(r'10\.\d{4,9}/\S+',r['DOI'])) and r['Study_ID']=='PMID:'+r['PMID'] for r in evidence))
    check('classifications_present_valid',all(r['Evidence_Type'] in ['Human pharmacokinetic','Controlled clinical','Animal','In vitro'] and r['Evidence_Level'] and r['Outcome'] for r in evidence))
    check('primary_reference_fields_present',all(r['Source_Title'] and r['Authors'] and re.fullmatch(r'\d{4}',r['Year']) and r['Source_Locator'] and r['Source_URL'] for r in evidence))
    check('source_caches_exist',all((B/r['Source_Cache'].replace('\\','/')).exists() for r in evidence))
    sourceaudit=read(OUT/'outputs/interaction_evidence_source_audit.csv')
    check('all_primary_report_metadata_concordant',all(r['Source_Verification_Status']=='cached_primary_metadata_verified' for r in sourceaudit) and {r['PMID'] for r in sourceaudit}=={r['PMID'] for r in evidence})
    badunits=[]
    for r in evidence:
        q=r['Quantitative_Outcome'].lower()
        if q and not any(x in q for x in ['%','ratio','gmr','fold','ng','micro','µ','μ','um','mg','ml','min',' h','/h','hour','auc and clearance']):badunits.append(r['Evidence_ID'])
    check('quantitative_units_or_ratio_context_present',not badunits,str(badunits))
    ledger=read(OUT/'outputs/claim_support_ledger.csv');new=[r for r in evidence if r['Release_Origin']=='expansion_v3_20261014']
    check('new_claims_have_support_ledger',set(r['Evidence_ID'] for r in ledger)==set(r['Evidence_ID'] for r in new))
    newbyid={r['Evidence_ID']:r for r in new}
    check('ledger_matches_actual_claim_fields',all(r['Evidence_ID'] in newbyid and r['Claim']==newbyid[r['Evidence_ID']][r['Claim_Field']] for r in ledger))
    check('new_claim_quotes_and_numeric_tokens_supported',all(r['Excerpt_Present']=='True' and r['Numerical_Tokens_Supported']=='True' for r in ledger),'Manual comparison plus literal numeric/quote diagnostics; not automatic semantic proof')
    for r in new:
        if r['Quantitative_Outcome'] and 'no effect' in r['Direction'].lower():warn('quantitative_null_review',r['Quantitative_Outcome'],[r['Evidence_ID']])
    sels=read(OUT/'outputs/selection_sources.csv');newreg=[r for r in registry if r['Origin']=='added_v3']
    check('all_new_compounds_have_selection_sources',all(r['Selection_Rationale'] and r['Selection_PMID'] and r['Selection_URL'] and r['Date_Added']=='2026-10-14' and any(s['Compound_ID']==r['Compound_ID'] and s['Source_Role']=='primary_interaction_evidence_supporting_current_selection' for s in sels) for r in newreg))
    check('new_selection_primary_snapshots_exist',all((OUT/'sources'/f"pmid_{r['Selection_PMID']}.json").exists() for r in newreg))
    check('selection_identifiers_match_cached_primary',all((OUT/'sources'/f"pmid_{r['Selection_PMID']}.json").exists() and any(str(m.get('id'))==r['Selection_PMID'] and m.get('doi','').casefold()==r['Selection_DOI'].casefold() for m in json.loads((OUT/'sources'/f"pmid_{r['Selection_PMID']}.json").read_text(encoding='utf8')).get('resultList',{}).get('result',[])) for r in newreg))
    def metadata_matches(row):
        path=B/row['Source_Cache'].replace('\\','/')
        if not path.exists():return False
        matches=[m for m in json.loads(path.read_text(encoding='utf8')).get('resultList',{}).get('result',[]) if str(m.get('id'))==row['PMID'] and m.get('source')=='MED']
        if not matches:return False
        m=matches[0]
        return all(str(row[field]).strip().casefold()==str(m.get(key,'')).strip().casefold() for field,key in [('DOI','doi'),('Source_Title','title'),('Year','pubYear'),('Authors','authorString')])
    check('live_table_fields_match_cached_primary_metadata',all(metadata_matches(row) for row in evidence))
    q=[r for r in registry if r['Canonical_Name']=='Quercetin']
    check('quercetin_mixed_group_not_used_as_evidence_key',len(q)==1 and q[0]['Compound_ID']=='CHEM-PUBCHEM-5280343' and not any(r['Compound_ID']=='MOL-FDB10E6B0C4171D1' for r in evidence))
    check('registry_coverage_counts_match',all(int(r['Evidence_Records'])==sum(e['Compound_ID']==r['Compound_ID'] for e in evidence) for r in registry))
    for status in sorted({r['Provenance_Status'] for r in registry if r['Origin']=='original_nine'}):
        rr=[r for r in registry if r['Provenance_Status']==status]
        warn('historical_selection_provenance',status,[r['Canonical_Name'] for r in rr])
    missingdoi=sorted({r['PMID'] for r in evidence if not r['DOI']})
    if missingdoi:warn('DOI_not_supplied','Verified PMID remains primary reference',missingdoi)
    crossref=[r['PMID'] for r in sourceaudit if 'unavailable' in r['Crossref_Status']]
    if crossref:warn('Crossref_lookup_unavailable','MED identifiers and metadata verified; independent Crossref lookup unavailable for these reports',crossref)
    warn('inherited_outcome_scope','64 baseline rows retained exactly; all metadata rechecked but full-text numerical outcomes not independently re-extracted in this release')
    warn('unresolved_preparation','Apigenin/rutin abstract cannot establish separate versus combined groups; no isolated-apigenin magnitude assigned',['SB-0066'])
    warn('retention_link_unavailable','Standalone chemical evidence is eligible, but reliable compound-specific master linkage is not established',['Daidzein','Quercetin'])
    warn('source_reporting_ambiguity','Daidzein abstract baseline day and CI wording inconsistent; disputed CIs omitted',['SB-0069'])
    warn('bounded_review','First 100 results per broad query; unreviewed candidates explicitly retained; no exhaustive review or independent second-reviewer adjudication')
    return {'status':'PASS_WITH_WARNINGS' if not errors else 'FAIL','checks_passed':sum(c['passed'] for c in checks),'checks_total':len(checks),'errors':errors,'warnings':warnings,'checks':checks}
def main():
    e=read(OUT/'outputs/stageB_food_drug_interactions_v3.csv');r=read(OUT/'outputs/compound_registry.csv');b=read(B/'expansion_v2/outputs/stageB_food_drug_interactions_expanded.csv')
    report=validate(e,r,b)
    manifest=json.loads((OUT/'audit/supplied_file_manifest.json').read_text())
    changed=[p for p,h in manifest.items() if not (ROOT/p).exists() or digest(ROOT/p)!=h]
    report['checks'].append({'check':'all_supplied_file_hashes_unchanged','passed':not changed,'detail':f'{len(manifest)} preserved files checked'})
    report['checks_total']+=1;report['checks_passed']+=not changed
    if changed:report['errors'].append({'check':'all_supplied_file_hashes_unchanged','detail':changed});report['status']='FAIL'
    report['scope']='Stage B only; validation does not clinically validate interaction risk or resolve original selection history'
    (OUT/'audit/validation_report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    outcomeaudit=[]
    ledger={r['Evidence_ID']:r for r in read(OUT/'outputs/claim_support_ledger.csv')}
    for row in e:
        l=ledger.get(row['Evidence_ID']);outcomeaudit.append({'Evidence_ID':row['Evidence_ID'],'PMID':row['PMID'],'Quantitative_Outcome':row['Quantitative_Outcome'],'Unit_Status':'endpoint units or dimensionless ratio context checked' if row['Quantitative_Outcome'] else 'no numerical effect size extracted; not zero','Claim_Review_Status':'manual new abstract extraction and support ledger' if l else 'inherited extraction not independently re-extracted','Unsupported_Claim_Flag':'none identified in reviewed new extraction' if l else 'not independently adjudicated in v3','Limitation':row['Limitations']})
    with (OUT/'outputs/outcome_validation_audit.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(outcomeaudit[0]));w.writeheader();w.writerows(outcomeaudit)
    print(json.dumps({'status':report['status'],'checks_passed':report['checks_passed'],'checks_total':report['checks_total'],'errors':report['errors'],'warnings':len(report['warnings']),'supplied_files_preserved':len(manifest)},indent=2))
    return report
if __name__=='__main__':sys.exit(0 if not main()['errors'] else 1)
