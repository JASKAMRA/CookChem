from build import *
import hashlib,copy,re
from decimal import Decimal
def nums(s):return {str(Decimal(x).normalize()) for x in re.findall(r'(?:\d+(?:\.\d+)?|\.\d+)',clean(s).replace(',',''))}
def checks(e,reg,claims):
 out=[]
 def c(n,v,d=''):out.append(dict(Check=n,Passed=bool(v),Detail=d))
 base=read(O/'inputs/stageB_food_drug_interactions_v5.csv');br=read(O/'inputs/compound_registry.csv');eb={x['Evidence_ID']:x for x in e};rb={x['Compound_ID']:x for x in reg};new=[x for x in e if x['Release_Origin']=='v6_20261014'];newreg=[x for x in reg if x['Origin']=='added_v6'];cl={x['Evidence_ID']:x for x in claims}
 c('V5 evidence field values and order preserved',e[:len(base)]==base)
 c('Evidence IDs unique',len(eb)==len(e));c('Evidence IDs stable sequential new suffix',all(x['Evidence_ID']==f'SB-{119+i:04d}' for i,x in enumerate(new)))
 c('Compound IDs unique',len(rb)==len(reg));c('Distinct chemical entities',len({x['InChIKey'] for x in reg})==len(reg) and len({x['PubChem_CID'] for x in reg})==len(reg))
 c('Schema remains 36 columns',all(list(x)==list(base[0]) and len(x)==36 for x in e))
 c('Compound foreign keys and names',all(x['Compound_ID'] in rb and rb[x['Compound_ID']]['Canonical_Name']==x['Compound'] for x in e))
 c('V5 registry unchanged',all(rb[x['Compound_ID']]==x for x in br))
 c('No duplicate study experimental contexts',len({tuple(x[k] for k in ['Study_ID','Compound_ID','Drug','Evidence_Type','Preparation','Co_Compounds']) for x in e})==len(e))
 c('PMID DOI and study identifiers valid',all(re.fullmatch(r'\d{5,9}',x['PMID']) and x['Study_ID']=='PMID:'+x['PMID'] and (not x['DOI'] or re.fullmatch(r'10\.\d{4,9}/\S+',x['DOI'])) for x in e))
 c('Permitted evidence classes',all(x['Evidence_Type'] in ['Human pharmacokinetic','Controlled clinical','Animal','In vitro'] for x in e))
 c('Claims ledger exactly matches new rows',set(cl)=={x['Evidence_ID'] for x in new} and all(cl[x['Evidence_ID']]['Claim']==x['Quantitative_Outcome'] and cl[x['Evidence_ID']]['Qualitative_Claim']==x['Interaction_Effect'] and cl[x['Evidence_ID']]['Outcome']==x['Outcome'] for x in new))
 c('Numerical tokens present in actual primary abstract',all(nums(x['Quantitative_Outcome']).issubset(nums(primary(x['PMID']).get('abstractText',''))) for x in new),'Diagnostic token check; manual endpoint/unit context remains necessary')
 c('Numerical outcomes have units or dimensionless measures',all(not x['Quantitative_Outcome'] or any(k in x['Quantitative_Outcome'] for k in ['%','micro','FICI=','fold','ng/mL']) for x in new))
 norm=lambda t:re.sub('[^a-z0-9]','',clean(str(t)).lower())
 c('Primary bibliography matches exact MED snapshot',all(all(norm(x[k])==norm(primary(x['PMID']).get(v,'')) for k,v in [('Source_Title','title'),('Authors','authorString'),('Year','pubYear'),('DOI','doi')]) for x in new))
 c('Source cache paths resolve and match new primary IDs',all(x['Source_Cache']==f'release_v6_20261014/sources/pmid_{x["PMID"]}.json' and (O/'sources'/('pmid_'+x['PMID']+'.json')).exists() for x in new) and all((B/x['Source_Cache']).exists() or (O/'inherited_sources'/x['Source_Cache']).exists() for x in base))
 c('Selection sources rationale and date complete',all(x['Selection_PMID'] and x['Selection_URL'] and x['Selection_Rationale'] and x['Date_Added']=='2026-10-14' for x in newreg))
 c('Historical dates not invented',all(not x['Date_Added'] for x in reg if x['Origin']=='original_nine'))
 c('Identity metadata matches cached reference',all(x['InChIKey']==load(O/'sources'/('identity_'+slug(x['Canonical_Name'])+'.json'))['PropertyTable']['Properties'][0]['InChIKey'] and x['InChI']==load(O/'sources'/('identity_'+slug(x['Canonical_Name'])+'.json'))['PropertyTable']['Properties'][0]['InChI'] for x in newreg))
 c('Reference stereochemistry not asserted as tested purity',all('stereochemistry not certified' in x['Identity_Status'] for x in newreg if x['Canonical_Name'] in ['Hesperetin','Hesperidin','6-Gingerol','Cinnamaldehyde']))
 c('Human cells not classified as human PK',all(x['Evidence_Type']=='In vitro' for x in new if x['Compound'] in ['(+)-Catechin','(-)-Epicatechin','Eugenol','Carvacrol','Thymol']))
 c('Diosmin uncontrolled studies classified as human PK',all(x['Evidence_Type']=='Human pharmacokinetic' for x in new if x['Compound']=='Diosmin'))
 c('Null thymoquinone finding retained',any(x['Compound']=='Thymoquinone' and x['PMID']=='33149871' and x['Outcome']=='no significant viability change' for x in new))
 c('Thymol partial synergy distinguished',all(x['Outcome']=='partial synergy detected' for x in new if x['Compound']=='Thymol'))
 c('Reverse glycyrrhizin interaction direction retained',all(x['Affected_Entity']=='compound' and x['Perpetrator']=='drug' for x in new if x['Compound']=='Glycyrrhizin'))
 c('No retention coefficient inferred for new anchors',all(not x['Original_Molecular_Group'] and x['Retention_Status']=='No compound-specific cooking retention imported' for x in newreg))
 c('Registry evidence counts correct',all(int(x['Evidence_Records'])==sum(a['Compound_ID']==x['Compound_ID'] for a in e) for x in reg))
 c('No retrospective clinical scoring',all(x['Clinical_Extrapolation']=='No clinical risk classification or food-exposure equivalence' for x in new))
 c('Primary publication count matches unique PMIDs',{x['PMID'] for x in read(O/'outputs/study_registry.csv')}=={x['PMID'] for x in e})
 c('Selection-only food reports not interaction publications',not {x['PMID'] for x in e}.intersection({'34836412','10812937','17875310','12972089','15351063'}))
 c('No unresolved Crossref title mismatch',not any('requires review' in x['Verification'] for x in read(O/'outputs/study_registry.csv')))
 c('Changes document all additions',{x['Evidence_ID'] for x in read(O/'outputs/evidence_change_log.csv')}=={x['Evidence_ID'] for x in new})
 statuses={'Resolved with supporting source','Partially resolved','Unresolved','Not applicable after inspection'}
 c('Issue statuses use requested vocabulary',all(x['After'] in statuses for x in read(O/'outputs/warning_resolution_ledger.csv')))
 c('Processing rows preserved separately',read(O/'outputs/cooking_retention_evidence.csv')==read(O/'inputs/stageB_processing_evidence.csv'))
 c('Candidate decisions complete',{x['Candidate'] for x in read(O/'outputs/candidate_selection.csv')}==set(CANDIDATES) and all(x['Decision'] in ['selected','deferred','rejected'] for x in read(O/'outputs/candidate_selection.csv')))
 return out
def main():
 e=read(O/'outputs/stageB_food_drug_interactions_v6.csv');r=read(O/'outputs/compound_registry.csv');cl=read(O/'outputs/claim_support_and_outcome_audit.csv');out=checks(e,r,cl)
 manifest=load(O/'audit/preservation_manifest.json');changed=[p for p,h in manifest.items() if not (O.parents[1]/p).exists() or hashlib.sha256((O.parents[1]/p).read_bytes()).hexdigest()!=h]
 out.append(dict(Check='All prior workspace files including V5 preserved',Passed=not changed,Detail=f'{len(manifest)} hashes; changed: {changed}'))
 before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (O/'outputs').glob('*')};mainbuild=__import__('build').main;mainbuild();after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (O/'outputs').glob('*')}
 out.append(dict(Check='Offline deterministic rebuild',Passed=before==after,Detail=f'{len(before)} output files byte compared'))
 (O/'audit/rebuild_verification.json').write_text(json.dumps(dict(passed=before==after,files=len(before)),indent=2),encoding='utf8')
 cases=[('duplicate evidence',lambda x,y:x[-1].update(Evidence_ID=x[0]['Evidence_ID']),'Evidence IDs unique'),('broken foreign key',lambda x,y:x[-1].update(Compound_ID='MISSING'),'Compound foreign keys and names'),('false number',lambda x,y:x[-1].update(Quantitative_Outcome='AUC 999999999 ng/mL'),'Numerical tokens present in actual primary abstract'),('wrong bibliography',lambda x,y:x[-1].update(Source_Title='wrong'),'Primary bibliography matches exact MED snapshot'),('inherited change',lambda x,y:x[0].update(Drug='wrong'),'V5 evidence field values and order preserved'),('missing selection',lambda x,y:y[-1].update(Selection_PMID=''),'Selection sources rationale and date complete'),('reverse direction',lambda x,y:x[-1].update(Affected_Entity='drug'),'Reverse glycyrrhizin interaction direction retained'),('duplicate chemical',lambda x,y:y[-1].update(InChIKey=y[0]['InChIKey']),'Distinct chemical entities')]
 tests=[]
 cases.append(('broken source cache',lambda x,y:x[-1].update(Source_Cache='missing.json'),'Source cache paths resolve and match new primary IDs'))
 for n,m,expect in cases:
  ee,rr=copy.deepcopy(e),copy.deepcopy(r);m(ee,rr);tests.append(dict(Test=n,Passed=any(x['Check']==expect and not x['Passed'] for x in checks(ee,rr,cl))))
 baseline=load(O/'audit/baseline_v5_validation_report.json');bm=load(O/'audit/baseline_v5_mutation_tests.json');total=baseline['checks_total']+len(out);passed=baseline['checks_passed']+sum(x['Passed'] for x in out);errors=[x for x in out if not x['Passed']];summary=load(O/'outputs/release_summary.json')
 result=dict(status='FAIL' if errors or not all(x['Passed'] for x in tests) else 'PASS_WITH_WARNINGS',checks_passed=passed,checks_total=total,inherited_v5_checks=baseline['checks_total'],v6_checks=len(out),errors=errors,warning_entries=summary['warning_entries'],distinct_warning_codes=summary['distinct_warning_codes'],checks=out)
 (O/'audit/validation_report.json').write_text(json.dumps(result,indent=2),encoding='utf8');(O/'audit/mutation_tests.json').write_text(json.dumps(dict(passed=bm['passed']+sum(x['Passed'] for x in tests),total=bm['total']+len(tests),inherited_tests=bm,new_tests=tests),indent=2),encoding='utf8');print(result['status'],passed,'/',total,'errors',errors);assert not errors and all(x['Passed'] for x in tests)
if __name__=='__main__':main()
