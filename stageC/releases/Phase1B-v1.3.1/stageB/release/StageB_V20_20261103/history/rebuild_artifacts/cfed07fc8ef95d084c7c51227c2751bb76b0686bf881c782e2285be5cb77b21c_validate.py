from build import *
import hashlib,copy,importlib.util,sys
from decimal import Decimal
sys.dont_write_bytecode=True
def nums(s):return {str(Decimal(x).normalize()) for x in re.findall(r'(?:\d+(?:\.\d+)?|\.\d+)',clean(s).replace(',',''))}
def checks(e,r,cl):
 out=[]
 def c(n,b,d=''):out.append(dict(Check=n,Passed=bool(b),Detail=d))
 base=read(O/'inputs/stageB_food_drug_interactions_v6.csv');old=read(O/'inputs/compound_registry.csv');eb={x['Evidence_ID']:x for x in e};rb={x['Compound_ID']:x for x in r};nr=[x for x in r if x['Origin']=='added_v7'];ne=[x for x in e if x['Release_Origin']=='v7_20261015_clean'];cm={x['Evidence_ID']:x for x in cl};rev=read(O/'outputs/all_record_review_audit.csv')
 c('Inherited 147 rows preserved in exact field order',e[:147]==base)
 c('Evidence IDs unique',len(eb)==len(e));c('Compound IDs unique',len(rb)==len(r));c('New IDs stable unrecycled sequential suffix',all(x['Evidence_ID']==f'SB-{148+i:04d}' for i,x in enumerate(ne)))
 c('Schema 36 fields unchanged',all(list(x)==list(base[0]) and len(x)==36 for x in e))
 c('Chemical keys and CIDs unique',len({x['InChIKey'] for x in r})==len(r) and len({x['PubChem_CID'] for x in r})==len(r))
 c('Canonical anchor names unique',len({x['Canonical_Name'].casefold().strip() for x in r})==len(r))
 c('Connectivity near-duplicates explicitly retain distinct stereo keys',all(a['InChIKey_A']!=a['InChIKey_B'] and a['Decision'].startswith('Distinct stereochemical') for a in read(O/'outputs/near_duplicate_identity_audit.csv')))
 c('Reference identities match actual PubChem snapshots',all(x['InChIKey']==load(O/'sources'/('identity_'+slug(x['Canonical_Name'])+'.json'))['PropertyTable']['Properties'][0]['InChIKey'] and x['InChI']==load(O/'sources'/('identity_'+slug(x['Canonical_Name'])+'.json'))['PropertyTable']['Properties'][0]['InChI'] for x in nr))
 c('Foreign keys and names valid',all(x['Compound_ID'] in rb and rb[x['Compound_ID']]['Canonical_Name']==x['Compound'] for x in e))
 c('No duplicate experimental contexts',len({tuple(x[k] for k in ['Study_ID','Compound_ID','Drug','Evidence_Type','Preparation','Co_Compounds']) for x in e})==len(e))
 c('Inherited registry changes restricted to evidence counts',all(all(rb[x['Compound_ID']][k]==v for k,v in x.items() if k!='Evidence_Records') for x in old))
 c('Registry evidence counts correct',all(int(x['Evidence_Records'])==sum(a['Compound_ID']==x['Compound_ID'] for a in e) for x in r))
 c('Selection provenance complete and current dates explicit',all(x['Selection_PMID'] and x['Selection_Rationale'] and x['Selection_URL'] and x['Date_Added']=='2026-10-15' for x in nr))
 c('Original-nine dates not fabricated',all(not x['Date_Added'] for x in r if x['Origin']=='original_nine'))
 c('Food context sources separate and locally available',all((O/x['Cache']).exists() and x['Domain'].startswith('Food association') for x in read(O/'outputs/food_context_source_audit.csv')))
 norm=lambda t:re.sub('[^a-z0-9]','',clean(str(t)).lower())
 c('New primary MED bibliography concordant',all(all(norm(x[k])==norm(primary(x['PMID']).get(v,'')) for k,v in [('Source_Title','title'),('Authors','authorString'),('Year','pubYear'),('DOI','doi')]) for x in ne))
 c('PMID DOI study formatting valid',all(re.fullmatch(r'\d{5,9}',x['PMID']) and x['Study_ID']=='PMID:'+x['PMID'] and (not x['DOI'] or re.fullmatch(r'10\.\d{4,9}/\S+',x['DOI'])) for x in e))
 c('Primary source cache paths valid',all(x['Source_Cache']==O.name+'/sources/pmid_'+x['PMID']+'.json' and (O/'sources'/('pmid_'+x['PMID']+'.json')).exists() for x in ne) and all((O/'inherited_sources'/x['Source_Cache']).exists() for x in base))
 upgraded={x['Evidence_ID'] for x in read(O/'outputs/evidence_change_log.csv') if x['Action']=='verification_upgrade'}
 c('Claim ledger covers new and upgraded contexts exactly',set(cm)=={x['Evidence_ID'] for x in ne}|upgraded and all(cm[x['Evidence_ID']]['Claim']==x['Quantitative_Outcome'] and cm[x['Evidence_ID']]['Qualitative_Claim']==x['Interaction_Effect'] for x in ne))
 bad=[]
 for x in cl:
  p=O/x['Source']
  if not p.exists():bad.append(x['Evidence_ID']);continue
  if p.suffix=='.xml':
   root=ET.parse(p).getroot();text=' '.join(root.itertext())
   if not any(a.get('pub-id-type')=='pmid' and a.text==x['PMID'] for a in root.findall('.//article-id')):bad.append(x['Evidence_ID'])
  else:
   hits=[a for a in load(p).get('resultList',{}).get('result',[]) if str(a.get('id'))==x['PMID']];text=hits[0].get('abstractText','') if hits else ''
  if not nums(x['Claim']).issubset(nums(text)):bad.append(x['Evidence_ID'])
 c('Numeric tokens trace to actual source passages',not bad,str(bad)+'; diagnostic only, manual endpoint/unit checks retained')
 c('Numerical outcomes retain units or dimensionless context',all(not x['Quantitative_Outcome'] or any(k in x['Quantitative_Outcome'] for k in ['micro','%',' h','four-fold','mm3']) for x in ne))
 c('Evidence classes permitted',all(x['Evidence_Type'] in ['Human pharmacokinetic','Controlled clinical','Animal','In vitro'] for x in e))
 c('Only randomized clinical studies labelled Controlled clinical',all(x['PMID'] in ['21482950','1828561'] and 'Randomized' in x['Study_Design'] for x in ne if x['Evidence_Type']=='Controlled clinical'))
 c('Human microsomes and cancer cells remain In vitro',all(x['Evidence_Type']=='In vitro' for x in ne if x['PMID'] in ['20877134','18191104','27529203','30976185','27058921']))
 c('Folic acid prevention and established-disease null separated',all(x['Outcome']==('reduced adverse-effect incidence' if x['PMID']=='21482950' else 'no significant clinical improvement') for x in ne if x['PMID'] in ['21482950','1828561']))
 c('Sesamin prior-study numerical result not attributed to current experiment',all('0.2' not in x['Quantitative_Outcome'] and '15.7' in x['Quantitative_Outcome'] for x in ne if x['Compound']=='Sesamin'))
 c('Lutein native suspension null not formulation-positive',all(x['Outcome']=='no exposure change detected' and 'Non-SNEDDS' in x['Preparation'] for x in ne if x['Compound']=='Lutein' and x['Drug']=='Warfarin'))
 c('Vitamin K1 not generalized to all vitamin K forms',all(x['Compound']=='Phylloquinone' and 'K1' in x['Preparation'] for x in ne if x['PMID']=='4091996'))
 c('Oleuropein unequal comparator dose remains explicit',all('1.5' in x['Dose'] and '2.5' in x['Dose'] and 'differs' in x['Limitations'] for x in ne if x['Compound']=='Oleuropein'))
 c('Processing rows preserved independently',read(O/'outputs/cooking_retention_evidence.csv')==read(O/'inputs/cooking_retention_evidence.csv'))
 c('New anchors have no imputed retention/master linkage',all(not x['Original_Molecular_Group'] and x['Retention_Status']=='No cooking-retention coefficient imported' for x in nr))
 c('Publication count distinct PMIDs not endpoints',{x['PMID'] for x in read(O/'outputs/study_registry.csv')}=={x['PMID'] for x in e})
 c('Food-only and unused generic vitamin-K sources not counted',not {x['PMID'] for x in e}.intersection({'34219099','30902268','35766779','17110451','17666020','32187570'}))
 c('All new contexts and upgrades change logged',{x['Evidence_ID'] for x in read(O/'outputs/evidence_change_log.csv') if x['Action']=='added'}=={x['Evidence_ID'] for x in ne})
 c('All 32 candidate decisions explicit',{x['Candidate'] for x in read(O/'outputs/candidate_selection.csv')}==set(CANDIDATES))
 c('Review status ledger complete and unique',len(rev)==len(e) and len({x['Evidence_ID'] for x in rev})==len(e) and {x['Evidence_ID'] for x in rev}==set(eb))
 c('Final anchor count computed from distinct entities',len(r)==len({x['Compound_ID'] for x in e}) and len(r)<=60 and len(nr)==len(FOODS))
 c('Drug registry exactly covers evidence labels',{x['Drug_Probe'] for x in read(O/'outputs/drug_probe_registry.csv')}=={x['Drug'] for x in e})
 c('No unresolved bibliographic mismatch',not any('requires review' in x['Verification'] for x in read(O/'outputs/study_registry.csv')))
 return out
def main():
 e=read(O/'outputs/stageB_food_drug_interactions_v7.csv');r=read(O/'outputs/compound_registry.csv');cl=read(O/'outputs/claim_support_and_outcome_audit.csv');out=checks(e,r,cl)
 mf=load(O/'audit/preservation_manifest.json');bad=[p for p,h in mf.items() if not (O.parents[1]/p).exists() or hashlib.sha256((O.parents[1]/p).read_bytes()).hexdigest()!=h];out.append(dict(Check='All frozen prior files including V6 preserved',Passed=not bad,Detail=f'{len(mf)} files; changed={bad}'))
 before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (O/'outputs').glob('*')};__import__('build').main();after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (O/'outputs').glob('*')};out.append(dict(Check='Offline deterministic rebuild byte-identical',Passed=before==after,Detail=f'{len(before)} files compared'))
 tests=[]
 cases=[('duplicate evidence',lambda x,y:x[-1].update(Evidence_ID=x[0]['Evidence_ID']),'Evidence IDs unique'),('foreign key',lambda x,y:x[-1].update(Compound_ID='missing'),'Foreign keys and names valid'),('wrong bibliography',lambda x,y:x[-1].update(Source_Title='wrong'),'New primary MED bibliography concordant'),('broken source',lambda x,y:x[-1].update(Source_Cache='missing'),'Primary source cache paths valid'),('inherited edit',lambda x,y:x[0].update(Drug='wrong'),'Inherited 147 rows preserved in exact field order'),('missing selection',lambda x,y:y[-1].update(Selection_PMID=''),'Selection provenance complete and current dates explicit'),('duplicate chemistry',lambda x,y:y[-1].update(InChIKey=y[0]['InChIKey']),'Chemical keys and CIDs unique'),('false human class',lambda x,y:next(a for a in x if a['Release_Origin']=='v7_20261015_clean' and a['PMID']=='27529203').update(Evidence_Type='Human pharmacokinetic'),'Human microsomes and cancer cells remain In vitro'),('null converted to benefit',lambda x,y:next(a for a in x if a['PMID']=='1828561').update(Outcome='benefit'),'Folic acid prevention and established-disease null separated')]
 for n,mut,expected in cases:
  ee,rr=copy.deepcopy(e),copy.deepcopy(r);mut(ee,rr);tests.append(dict(Test=n,Passed=any(x['Check']==expected and not x['Passed'] for x in checks(ee,rr,cl))))
 cc=copy.deepcopy(cl);cc[-1]['Claim']='999999999 microM';tests.append(dict(Test='Invented numerical claim in supporting ledger',Passed=any(x['Check']=='Numeric tokens trace to actual source passages' and not x['Passed'] for x in checks(e,r,cc))))
 errors=[x for x in out if not x['Passed']];s=load(O/'outputs/release_summary.json');result=dict(status='FAIL' if errors or not all(x['Passed'] for x in tests) else 'PASS_WITH_WARNINGS' if s['warning_entries'] else 'PASS',checks_passed=sum(x['Passed'] for x in out),checks_total=len(out),errors=errors,warning_entries=s['warning_entries'],distinct_warning_codes=s['distinct_warning_codes'],checks=out,baseline_suite_before=load(O/'audit/baseline_v6_validation_before.json')['status'],baseline_suite_after=load(O/'audit/baseline_v6_validation_after.json')['status'])
 (O/'audit/validation_report.json').write_text(json.dumps(result,indent=2),encoding='utf8');(O/'audit/mutation_tests.json').write_text(json.dumps(dict(passed=sum(x['Passed'] for x in tests),total=len(tests),tests=tests,scope='Fresh V7 tests; separate V6 before/after mutation results retained, not double-counted'),indent=2),encoding='utf8');(O/'audit/rebuild_verification.json').write_text(json.dumps(dict(passed=before==after,files=len(before)),indent=2),encoding='utf8');print(result['status'],result['checks_passed'],'/',len(out),'mutations',sum(x['Passed'] for x in tests),'/',len(tests),errors);assert not errors and all(x['Passed'] for x in tests)
if __name__=='__main__':main()
