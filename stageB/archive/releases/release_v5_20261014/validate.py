from pathlib import Path
import sys,csv,json,hashlib,re,html,copy,importlib.util,xml.etree.ElementTree as ET
from decimal import Decimal
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1];B=R/'stageB';V4=B/'release_v4_20261014'
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def load(p):return json.loads(p.read_text(encoding='utf8'))
def norm(t):return re.sub('[^a-z0-9]','',html.unescape(re.sub(r'</?[A-Za-z][^>]*>','',t)).lower())
def nums(t):return {str(Decimal(x).normalize()) for x in re.findall(r'(?:\d+(?:\.\d+)?|\.\d+)',html.unescape(re.sub(r'</?[A-Za-z][^>]*>','',t)).replace(',',''))}
def sourceclaim(row,ledger):
    p=O/ledger['Source']
    if not p.exists():return False
    if p.suffix=='.xml':text=' '.join(ET.parse(p).getroot().itertext())
    else:
        d=load(p);hit=[m for m in d.get('resultList',{}).get('result',[]) if str(m.get('id'))==row['PMID']]
        if not hit:return False
        text=hit[0].get('abstractText','')
    return nums(row['Quantitative_Outcome']).issubset(nums(text))
def checks(e,reg,claims):
    out=[]
    def c(name,ok,detail=''):out.append(dict(Check=name,Passed=bool(ok),Detail=detail))
    base=read(V4/'outputs/stageB_food_drug_interactions_v4.csv');oldreg=read(V4/'outputs/compound_registry.csv');by={r['Evidence_ID']:r for r in e};rg={r['Compound_ID']:r for r in reg};new=[r for r in e if r['Release_Origin']=='v5_20261014'];newreg=[r for r in reg if r['Origin']=='added_v5'];cl={r['Evidence_ID']:r for r in claims}
    c('All 73 v4 rows preserved',all(by.get(r['Evidence_ID'])==r for r in base));c('Evidence IDs unique',len(by)==len(e));c('Compound IDs unique',len(rg)==len(reg))
    c('Schema and ordering unchanged',all(list(r)==list(base[0]) and len(r)==36 for r in e));c('Evidence ID syntax',all(re.fullmatch(r'SB-\d{4}',r['Evidence_ID']) for r in e))
    c('Compound foreign keys and canonical names',all(r['Compound_ID'] in rg and rg[r['Compound_ID']]['Canonical_Name']==r['Compound'] for r in e));c('Identity keys and canonical names unique',len({r['InChIKey'] for r in reg})==len(reg) and len({r['Canonical_Name'].casefold() for r in reg})==len(reg))
    c('Existing compound identities unchanged',all(all(r[k]==rg[r['Compound_ID']][k] for k in ['Canonical_Name','PubChem_CID','InChIKey','InChI','SMILES']) for r in oldreg))
    c('New selection sources and date present',all(r['Selection_PMID'] and r['Selection_DOI'] and r['Selection_URL'] and r['Selection_Rationale'] and r['Date_Added']=='2026-10-14' for r in newreg))
    c('No invented original-nine selection dates',all(not r['Date_Added'] for r in reg if r['Origin']=='original_nine'))
    c('Ambiguous parent measurement groups not linked',all(not r['Original_Molecular_Group'] for r in newreg if r['Canonical_Name'] in ['Myricetin','Naringenin']) and not any(r['Compound_ID'] in ['MOL-FDB10E6B0C4171D1','MOL-9CB93756EB0D9051','MOL-DAB1A78D5F57702F'] for r in e))
    c('Naringenin distinct from naringin and stereospecific CID',rg[next(r['Compound_ID'] for r in reg if r['Canonical_Name']=='Naringenin')]['PubChem_CID']=='932' and next(r['Compound_ID'] for r in reg if r['Canonical_Name']=='Naringenin')!=next(r['Compound_ID'] for r in reg if r['Canonical_Name']=='Naringin'))
    c('No duplicate experimental contexts',len({tuple(r[k] for k in ['Study_ID','Compound_ID','Drug','Evidence_Type','Preparation','Co_Compounds']) for r in e})==len(e))
    c('Classifications and source identifiers valid',all(r['Evidence_Type'] in ['Human pharmacokinetic','Controlled clinical','Animal','In vitro'] and re.fullmatch(r'\d{5,9}',r['PMID']) and r['Study_ID']=='PMID:'+r['PMID'] and (not r['DOI'] or re.fullmatch(r'10\.\d{4,9}/\S+',r['DOI'])) for r in e))
    metadata=True;bad=[]
    for r in new:
        p=B/r['Source_Cache'];hits=load(p).get('resultList',{}).get('result',[]) if p.exists() else [];hit=[m for m in hits if str(m.get('id'))==r['PMID'] and m.get('source')=='MED']
        ok=bool(hit) and all(norm(r[k])==norm(str(hit[0].get(v,''))) for k,v in [('Source_Title','title'),('DOI','doi'),('Authors','authorString'),('Year','pubYear')]);metadata &= ok
        if not ok:bad.append(r['Evidence_ID'])
    c('New primary metadata concordant with MED',metadata,str(bad))
    c('New claims have exact ledger matches',set(cl)=={r['Evidence_ID'] for r in new} and all(cl[r['Evidence_ID']]['Claim']==r['Quantitative_Outcome'] and cl[r['Evidence_ID']]['Qualitative_Claim']==r['Interaction_Effect'] and cl[r['Evidence_ID']]['Outcome']==r['Outcome'] for r in new))
    unsupported=[r['Evidence_ID'] for r in new if r['Evidence_ID'] not in cl or not sourceclaim(r,cl[r['Evidence_ID']])]
    c('New numerical tokens supported by actual sources',not unsupported,str(unsupported)+'; token check is a diagnostic, not endpoint-semantic proof')
    c('Numerical units or dimensionless context',all(not r['Quantitative_Outcome'] or any(t in r['Quantitative_Outcome'].lower() for t in ['%','ratio','fold','ng','micro','mg','min','gmr','ci=','auc and clearance','um']) for r in e))
    c('Null and no-synergy meanings preserved',all(r['Outcome']=='no synergy detected' and 'no interaction' not in r['Interaction_Effect'].lower() for r in new if r['Compound']=='Fisetin' and r['Drug'] in ['Methotrexate','Mitoxantrone']))
    c('Nonsignificant human talinolol result not overclaimed',all(r['Outcome']=='nonsignificant mean changes' and 'P>0.05' in r['Quantitative_Outcome'] for r in new if r['PMID']=='24472704'))
    c('Uncontrolled chrysin pilot not Controlled clinical',all(r['Evidence_Type']=='Human pharmacokinetic' and 'Uncontrolled' in r['Limitations'] for r in new if r['PMID']=='16003560'))
    c('Reverse interactions preserve affected entity',all(r['Affected_Entity']=='compound' and r['Perpetrator']=='drug' for r in new if (r['Compound'],r['Drug']) in [('Ferulic acid','Clopidogrel'),('Rosmarinic acid','Probenecid')]))
    studies=read(O/'outputs/study_registry.csv');c('Unique primary PMIDs counted correctly',len(studies)==len({r['PMID'] for r in e}) and {r['PMID'] for r in studies}=={r['PMID'] for r in e});c('Registry evidence counts correct',all(int(r['Evidence_Records'])==sum(x['Compound_ID']==r['Compound_ID'] for x in e) for r in reg))
    changes=read(O/'outputs/evidence_change_log.csv');c('Added IDs all documented without inherited edits',set(r['Evidence_ID'] for r in changes)=={r['Evidence_ID'] for r in new} and all(r['Action']=='added' for r in changes))
    c('Selection and processing publications not counted as interaction studies',not {r['PMID'] for r in studies}.intersection({'10794622','11032486','15309458'}))
    c('All candidate decisions explicit',len(read(O/'outputs/candidate_selection.csv'))==16 and all(r['Decision'] in ['selected','deferred','rejected'] for r in read(O/'outputs/candidate_selection.csv')))
    c('No unresolved Crossref title mismatches',all('requires review' not in r['Verification'] for r in studies))
    manifest=load(O/'audit/preservation_manifest.json');changed=[p for p,h in manifest.items() if not (R/p).exists() or hashlib.sha256((R/p).read_bytes()).hexdigest()!=h]
    c('All supplied files and v4 hashes unchanged',not changed,f'{len(manifest)} files checked; changed={changed}')
    return out
def main():
    e=read(O/'outputs/stageB_food_drug_interactions_v5.csv');r=read(O/'outputs/compound_registry.csv');cl=read(O/'outputs/claim_support_and_outcome_audit.csv');own=checks(e,r,cl)
    spec=importlib.util.spec_from_file_location('v4_validator',V4/'validate.py');v4=importlib.util.module_from_spec(spec);spec.loader.exec_module(v4)
    base=read(V4/'outputs/stageB_food_drug_interactions_v4.csv');br=read(V4/'outputs/compound_registry.csv');compat=v4.run(base,br)
    allchecks=[dict(c,Check='Inherited v4: '+c['Check']) for c in compat]+own
    ledger=read(O/'outputs/warning_resolution_ledger.csv');warn=[r for r in ledger if not r['After'].startswith('resolved')]
    report=dict(version='v5',status='PASS_WITH_WARNINGS' if all(c['Passed'] for c in allchecks) else 'FAIL',checks_passed=sum(c['Passed'] for c in allchecks),checks_total=len(allchecks),inherited_checks=len(compat),v5_checks=len(own),errors=[c for c in allchecks if not c['Passed']],warning_entries=len(warn),distinct_warning_codes=len({r['Code'] for r in warn}),warnings=warn,checks=allchecks)
    (O/'audit/validation_report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    tests=[]
    v3path=B/'expansion_v3_20261014';sp=importlib.util.spec_from_file_location('v3_validator',v3path/'scripts/validate_release.py');v3=importlib.util.module_from_spec(sp);sp.loader.exec_module(v3);be=read(v3path/'outputs/stageB_food_drug_interactions_expanded.csv') if (v3path/'outputs/stageB_food_drug_interactions_expanded.csv').exists() else read(v3path/'outputs/stageB_food_drug_interactions_v3.csv');breg=read(v3path/'outputs/compound_registry.csv');b64=read(B/'expansion_v2/outputs/stageB_food_drug_interactions_expanded.csv')
    for name,mut,expected in [('duplicate ID',lambda x,y:x[-1].update(Evidence_ID=x[0]['Evidence_ID']),'evidence_ids_unique'),('broken FK',lambda x,y:x[-1].update(Compound_ID='MISSING'),'compound_evidence_foreign_keys'),('numeric claim',lambda x,y:x[-1].update(Quantitative_Outcome='AUC 9999'),'ledger_matches_actual_claim_fields'),('wrong bibliography',lambda x,y:x[-1].update(Source_Title='wrong'),'live_table_fields_match_cached_primary_metadata'),('baseline changed',lambda x,y:x[0].update(Interaction_Effect='wrong'),'baseline_64_rows_unchanged'),('missing selection',lambda x,y:y[-1].update(Selection_PMID=''),'all_new_compounds_have_selection_sources')]:
        ee,rr=copy.deepcopy(be),copy.deepcopy(breg);mut(ee,rr);tests.append(dict(Test='Existing v3 '+name,Passed=expected in {a['check'] for a in v3.validate(ee,rr,b64)['errors']}))
    for name,eid,field,value,expect in [('corrected claim tamper','SB-0067','Quantitative_Outcome','AUC 9999999 mg.h/L','Reviewed numerical values present in actual sources'),('significance overclaim','SB-0073','Direction','significant established reduction','Quercetin nonsignificant interval interpretation preserved')]:
        ee=copy.deepcopy(base);next(x for x in ee if x['Evidence_ID']==eid)[field]=value;tests.append(dict(Test='Existing v4 '+name,Passed=any(c['Check']==expect and not c['Passed'] for c in v4.run(ee,br))))
    for name,predicate,field,value,expect in [('false new quantity',lambda x:x['Release_Origin']=='v5_20261014' and bool(x['Quantitative_Outcome']),'Quantitative_Outcome','AUC 9999999 ng.h/mL','New numerical tokens supported by actual sources'),('no synergy relabelled no interaction',lambda x:x['Compound']=='Fisetin' and x['Drug']=='Methotrexate','Outcome','no interaction','Null and no-synergy meanings preserved'),('reverse interaction flipped',lambda x:x['Compound']=='Ferulic acid','Affected_Entity','drug/probe','Reverse interactions preserve affected entity')]:
        ee=copy.deepcopy(e);next(x for x in ee if predicate(x))[field]=value;tests.append(dict(Test='New v5 '+name,Passed=any(c['Check']==expect and not c['Passed'] for c in checks(ee,r,cl))))
    (O/'audit/mutation_tests.json').write_text(json.dumps(dict(passed=sum(x['Passed'] for x in tests),total=len(tests),tests=tests),indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in report.items() if k not in ['warnings','checks']},indent=2));print('Mutation tests',sum(x['Passed'] for x in tests),'/',len(tests));assert not report['errors'] and all(x['Passed'] for x in tests)
if __name__=='__main__':main()
