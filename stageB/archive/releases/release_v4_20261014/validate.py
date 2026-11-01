from pathlib import Path
import csv,json,re,hashlib,xml.etree.ElementTree as E,html,importlib.util,copy,sys
from decimal import Decimal
O=Path(__file__).resolve().parent;R=O.parents[1];B=R/'stageB';V3=B/'expansion_v3_20261014'
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def norm(t):return re.sub('[^a-z0-9]','',html.unescape(re.sub(r'</?[A-Za-z][^>]*>','',t)).lower())
def nums(t):return {str(Decimal(x).normalize()) for x in re.findall(r'(?:\d+(?:\.\d+)?|\.\d+)',html.unescape(re.sub(r'</?[A-Za-z][^>]*>','',t)).replace(',',''))}
def source_text(p):
    if p.suffix=='.xml':return ' '.join(E.parse(p).getroot().itertext())
    return json.loads(p.read_text(encoding='utf8'))
def run(e,reg):
    checks=[]
    def c(name,ok,detail=''):checks.append(dict(Check=name,Passed=bool(ok),Detail=detail))
    base=read(V3/'outputs/stageB_food_drug_interactions_v3.csv');by={r['Evidence_ID']:r for r in e};rg={r['Compound_ID']:r for r in reg}
    c('Evidence IDs unique',len(by)==len(e));c('Compound IDs unique',len(rg)==len(reg))
    c('Names and structure keys unique',len({r['Canonical_Name'].lower() for r in reg})==len(reg) and len({r['InChIKey'] for r in reg})==len(reg))
    c('Exact schema preserved',all(list(r)==list(base[0]) for r in e));c('All compound references valid',all(r['Compound_ID'] in rg and rg[r['Compound_ID']]['Canonical_Name']==r['Compound'] for r in e))
    c('Original 64 unchanged',all(by.get(r['Evidence_ID'])==r for r in base[:64]))
    changes=read(O/'outputs/evidence_change_log.csv');actual={(r['Evidence_ID'],k) for r in e for k in r if r[k]!=next(x for x in base if x['Evidence_ID']==r['Evidence_ID'])[k]}
    documented={(r['Evidence_ID'],r['Field']) for r in changes}
    c('Every changed field documented',actual==documented and all(by[r['Evidence_ID']][r['Field']]==r['After'] and next(x for x in base if x['Evidence_ID']==r['Evidence_ID'])[r['Field']]==r['Before'] for r in changes))
    c('No records added or removed',set(by)=={r['Evidence_ID'] for r in base});c('Duplicate contexts absent',len({tuple(r[k] for k in ['Study_ID','Compound_ID','Drug','Evidence_Type','Preparation','Co_Compounds']) for r in e})==len(e))
    c('ID and DOI syntax',all(re.fullmatch(r'SB-\d{4}',r['Evidence_ID']) and re.fullmatch(r'\d{5,9}',r['PMID']) and (not r['DOI'] or re.fullmatch(r'10\.\d{4,9}/\S+',r['DOI'])) and r['Study_ID']=='PMID:'+r['PMID'] for r in e))
    c('Classification and endpoint context',all(r['Evidence_Type'] in ['Human pharmacokinetic','Controlled clinical','Animal','In vitro'] and r['Direction'] and r['Outcome'] and r['Source_Locator'] for r in e))
    c('Outcome units or ratio present',all(not r['Quantitative_Outcome'] or any(x in r['Quantitative_Outcome'].lower() for x in ['%','ratio','gmr','fold','ng','micro','um','µ','μ','mg','ml','min',' h','/h','auc and clearance']) for r in e))
    metadata=True
    for r in e:
        p=B/r['Source_Cache'].replace('\\','/')
        if not p.exists():metadata=False;continue
        hits=[m for m in json.loads(p.read_text(encoding='utf8')).get('resultList',{}).get('result',[]) if str(m.get('id'))==r['PMID']]
        if not hits:metadata=False;continue
        m=hits[0];metadata &= all(norm(r[k])==norm(str(m.get(v,''))) for k,v in [('Source_Title','title'),('DOI','doi'),('Authors','authorString'),('Year','pubYear')])
    c('All cached primary metadata concordant',metadata)
    audits=read(O/'outputs/claim_support_and_outcome_audit.csv');c('Claim ledger matches actual outcomes',all(a['Evidence_ID'] in by and a['Claim']==by[a['Evidence_ID']]['Quantitative_Outcome'] for a in audits) and len(audits)==len(e))
    supported=True
    for a in audits:
        if a['Verification_Level']=='cached_primary_metadata_rechecked':continue
        p=R/a['Source'];r=by[a['Evidence_ID']]
        if not p.exists():supported=False;continue
        text=source_text(p)
        if isinstance(text,dict):text=next(m.get('abstractText','') for m in text['resultList']['result'] if str(m['id'])==r['PMID'])
        supported &= nums(r['Quantitative_Outcome']).issubset(nums(text))
    c('Reviewed numerical values present in actual sources',supported,'Numeric diagnostics plus manual endpoint review; not an automatic scientific proof')
    c('Quercetin nonsignificant interval interpretation preserved','nonsignificant' in by['SB-0073']['Direction'] and '0.61-1.10' in by['SB-0073']['Quantitative_Outcome'])
    c('New selection sources present',all(r['Selection_PMID'] and r['Selection_DOI'] and r['Selection_Rationale'] and r['Date_Added']=='2026-10-14' for r in reg if r['Origin']=='added_v3'))
    c('Unknown original dates not invented',all(not r['Date_Added'] and not r['Earliest_Verified_Selection_Date'] for r in reg if r['Origin']=='original_nine'))
    c('Glycoside and mixed group links prohibited',rg['CHEM-PUBCHEM-5280343']['Original_Molecular_Group']!='MOL-FDB10E6B0C4171D1' and not any(r['Compound_ID']=='MOL-FDB10E6B0C4171D1' for r in e) and 'CHEM-PUBCHEM-5281708' in rg)
    c('Registry and primary counts match',len({r['PMID'] for r in e})==len(read(O/'outputs/study_registry.csv')) and all(int(r['Evidence_Records'])==sum(x['Compound_ID']==r['Compound_ID'] for x in e) for r in reg))
    primary=read(O/'outputs/study_registry.csv');c('Previously unavailable Crossref titles resolved',all(r['Crossref_Verification']=='v4 Crossref title concordant' for r in primary if (O/'sources'/f"crossref_{r['PMID']}.json").exists()))
    c('Recovered Crossref DOI identifiers concordant',all(json.loads((O/'sources'/f"crossref_{r['PMID']}.json").read_text(encoding='utf8')).get('message',{}).get('DOI','').casefold()==r['DOI'].casefold() for r in primary if (O/'sources'/f"crossref_{r['PMID']}.json").exists()))
    manifest=json.loads((O/'audit/preservation_manifest.json').read_text());changed=[p for p,h in manifest.items() if not (R/p).exists() or hashlib.sha256((R/p).read_bytes()).hexdigest()!=h]
    c('All supplied and v3 file hashes preserved',not changed,f'{len(manifest)} files; changes={changed}')
    old=json.loads((V3/'audit/supplied_file_manifest.json').read_text());c('Original v3 input manifest still valid',all((R/p).exists() and hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in old.items()))
    return checks
def main():
    e=read(O/'outputs/stageB_food_drug_interactions_v4.csv');r=read(O/'outputs/compound_registry.csv');checks=run(e,r)
    ledger=read(O/'outputs/warning_resolution_ledger.csv');remaining=[w for w in ledger if not w['After'].startswith('resolved')]
    report=dict(version='v4',status='PASS_WITH_WARNINGS' if all(c['Passed'] for c in checks) else 'FAIL',checks_passed=sum(c['Passed'] for c in checks),checks_total=len(checks),errors=[c for c in checks if not c['Passed']],remaining_warning_entries=len(remaining),remaining_distinct_warning_codes=len({w['Code'] for w in remaining}),warnings=remaining,checks=checks)
    (O/'audit/validation_report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    # Invoke the existing v3 validation function read-only; do not invoke its writing main routine.
    sys.dont_write_bytecode=True
    spec=importlib.util.spec_from_file_location('v3_validation',V3/'scripts/validate_release.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    be=read(V3/'outputs/stageB_food_drug_interactions_v3.csv');br=read(V3/'outputs/compound_registry.csv');b64=read(B/'expansion_v2/outputs/stageB_food_drug_interactions_expanded.csv')
    tests=[]
    cases=[('duplicate ID',lambda ee,rr:ee[-1].update(Evidence_ID=ee[0]['Evidence_ID']),'evidence_ids_unique'),('broken reference',lambda ee,rr:ee[-1].update(Compound_ID='MISSING'),'compound_evidence_foreign_keys'),('numerical mutation',lambda ee,rr:ee[-1].update(Quantitative_Outcome='AUC GMR 99.99'),'ledger_matches_actual_claim_fields'),('bibliographic corruption',lambda ee,rr:ee[-1].update(Source_Title='Wrong title'),'live_table_fields_match_cached_primary_metadata'),('baseline alteration',lambda ee,rr:ee[0].update(Interaction_Effect='Changed'),'baseline_64_rows_unchanged'),('missing selection',lambda ee,rr:rr[-1].update(Selection_PMID=''),'all_new_compounds_have_selection_sources')]
    for name,mutate,expected in cases:
        ee,rr=copy.deepcopy(be),copy.deepcopy(br);mutate(ee,rr);codes={x['check'] for x in mod.validate(ee,rr,b64)['errors']};tests.append(dict(Test='v3 '+name,Passed=expected in codes))
    for name,field,value,expected in [('corrected claim tamper','Quantitative_Outcome','AUC 9999 mg.h/L','Reviewed numerical values present in actual sources'),('significance overclaim','Direction','established exposure reduction','Quercetin nonsignificant interval interpretation preserved')]:
        ee=copy.deepcopy(e);next(x for x in ee if x['Evidence_ID']==('SB-0067' if field=='Quantitative_Outcome' else 'SB-0073'))[field]=value
        tests.append(dict(Test='v4 '+name,Passed=any(x['Check']==expected and not x['Passed'] for x in run(ee,r))))
    (O/'audit/mutation_tests.json').write_text(json.dumps(dict(tests=tests,passed=sum(t['Passed'] for t in tests),total=len(tests)),indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in report.items() if k not in ['warnings','checks']},indent=2));print('Mutation tests',sum(t['Passed'] for t in tests),'/',len(tests))
    assert not report['errors'] and all(t['Passed'] for t in tests)
if __name__=='__main__':main()
