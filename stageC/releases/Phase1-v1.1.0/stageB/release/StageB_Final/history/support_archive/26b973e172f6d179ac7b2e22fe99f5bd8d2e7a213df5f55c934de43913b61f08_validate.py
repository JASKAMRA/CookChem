from pathlib import Path
import sys,json,hashlib,copy,re,html,collections
sys.dont_write_bytecode=True
import build
O=build.O;V=build.V
def norm(s):return re.sub('[^a-z0-9]','',html.unescape(re.sub('<[^>]+>','',s)).lower())
def assess(e,r,claims):
 checks={};old=build.read(V/'outputs/stageB_food_drug_interactions_v7.csv');by={x['Evidence_ID']:x for x in old};reg={x['Compound_ID']:x for x in r};ids=[x['Evidence_ID'] for x in e]
 checks['counts']=len(e)==189 and len(r)==60
 checks['unique_ids']=len(ids)==len(set(ids))
 checks['original_ids_preserved']=set(ids)==set(by)
 checks['schema_preserved']=list(e[0])==list(old[0])
 checks['unique_identity']=len({x['InChIKey'] for x in r})==60 and len(reg)==60
 checks['mapping']=all(x['Compound_ID'] in reg and x['Compound']==reg[x['Compound_ID']]['Canonical_Name'] for x in e)
 checks['references']=all(x['PMID'].isdigit() and norm(x['Source_Title'])==norm(build.med(x['PMID'])['title']) and x['DOI']==build.med(x['PMID']).get('doi','') and x['Year']==build.med(x['PMID'])['pubYear'] and norm(x['Authors'])==norm(build.med(x['PMID'])['authorString']) for x in e)
 checks['source_cache']=all((O/'inherited_sources'/x['Source_Cache']).is_file() for x in e)
 checks['study_classes']=collections.Counter(x['Evidence_Type'] for x in e)==collections.Counter(x['Evidence_Type'] for x in old)
 checks['claim_coverage']=len(claims)==189 and {x['Evidence_ID'] for x in claims}==set(ids)
 checks['four_numeric_holds']={x['Evidence_ID'] for x in claims if x['Numerical_Use'].startswith('HOLD')}=={'SB-0051','SB-0052','SB-0053','SB-0054'}
 checks['provisional_apigenin']=next(x for x in claims if x['Evidence_ID']=='SB-0066')['Attribution'].startswith('PROVISIONAL')
 checks['no_historical_date_invention']=all(not x['Date_Added'] and not x['Earliest_Verified_Selection_Date'] for x in r if x['Origin']=='original_nine')
 checks['registered_food_context']=all(x['Food_Context'] and x['Selection_Rationale'] and x['Identity_Source'] for x in r)
 checks['only_logged_changes']=all(x[k]==by[x['Evidence_ID']][k] or (x['Evidence_ID'],k) in {(c['Evidence_ID'],c['Field']) for c in build.read(O/'outputs/evidence_change_log.csv')} for x in e for k in x)
 checks['five_changed_records']={x['Evidence_ID'] for x in e if x!=by[x['Evidence_ID']]}=={'SB-0002','SB-0012','SB-0033','SB-0037','SB-0046'}
 checks['nulls_preserved']=all(x['Interaction_Effect']==by[x['Evidence_ID']]['Interaction_Effect'] and x['Quantitative_Outcome']==by[x['Evidence_ID']]['Quantitative_Outcome'] for x in e if x['Evidence_ID'] not in ['SB-0002','SB-0012','SB-0033','SB-0037','SB-0046'])
 checks['egcg_cmax_nonsignificant']='not significant' in next(x for x in e if x['Evidence_ID']=='SB-0037')['Quantitative_Outcome']
 checks['piperine_observed_auc_null']='not significantly different' in next(x for x in e if x['Evidence_ID']=='SB-0012')['Quantitative_Outcome']
 return checks
def main():
 e=build.read(O/'outputs/stageB_food_drug_interactions_v8.csv');r=build.read(O/'outputs/compound_registry.csv');c=build.read(O/'outputs/claim_level_audit.csv');checks=assess(e,r,c)
 ident=build.read(O/'outputs/identity_structure_audit.csv');checks['fresh_identity_matches']=len(ident)==60 and all(x['Match']=='True' for x in ident)
 warnings=build.read(O/'outputs/warning_resolution_ledger.csv');checks['original_warning_coverage']={x['Warning_ID'] for x in build.read(V/'outputs/warning_resolution_ledger.csv')} <= {x['Warning_ID'] for x in warnings}
 checks['warning_status_source']=all(x['After'] in ['Resolved','Partially resolved','Unresolved','Not applicable'] and x['Resolution_Source'] and x['Action'] for x in warnings)
 checks['publication_count']=len(build.read(O/'outputs/source_bibliography.csv'))==121
 checks['deferred_count']=len(build.read(O/'outputs/deferred_candidate_review.csv'))==14
 checks['historical_nine']=len(build.read(O/'outputs/original_nine_selection_provenance.csv'))==9
 manifest=json.loads((O/'audit/preservation_manifest.json').read_text());bad=[p for p,h in manifest.items() if not (O.parent.parent/p).is_file() or hashlib.sha256((O.parent.parent/p).read_bytes()).hexdigest()!=h]
 checks['prior_8087_files_unchanged']=len(manifest)==8087 and not bad
 tests=[]
 for name,kind,field,value in [('duplicate_evidence','e','Evidence_ID',e[1]['Evidence_ID']),('bad_mapping','e','Compound_ID','invalid'),('bad_pmid','e','PMID','0'),('bad_title','e','Source_Title','invented'),('bad_doi','e','DOI','10.fake/invalid'),('wrong_class','e','Evidence_Type','Human clinical risk'),('unlogged_number','e','Quantitative_Outcome','Invented 9999%'),('missing_cache','e','Source_Cache','not_there.json'),('identity_collision','r','InChIKey',r[1]['InChIKey']),('invented_history','r','Date_Added','2020-01-01')]:
  ee=copy.deepcopy(e);rr=copy.deepcopy(r);cc=copy.deepcopy(c);(ee if kind=='e' else rr)[0][field]=value
  try:result=assess(ee,rr,cc);caught=not all(result.values())
  except (KeyError,StopIteration,FileNotFoundError):caught=True
  tests.append(dict(Mutation=name,Detected=caught))
 cc=copy.deepcopy(c);next(x for x in cc if x['Evidence_ID']=='SB-0051')['Numerical_Use']='Approved';tests.append(dict(Mutation='remove_numeric_hold',Detected=not all(assess(e,r,cc).values())))
 cc=copy.deepcopy(c);next(x for x in cc if x['Evidence_ID']=='SB-0066')['Attribution']='Isolated apigenin';tests.append(dict(Mutation='erase_provisional_attribution',Detected=not all(assess(e,r,cc).values())))
 out=dict(checks=checks,passed=sum(checks.values()),total=len(checks),prior_files_checked=len(manifest),preservation_mismatches=bad,mutations=tests,mutations_passed=sum(x['Detected'] for x in tests),mutations_total=len(tests),Scientific_Limit='Structural checks do not resolve primary-publication ambiguity or independently validate every scientific number.')
 (O/'audit/validation_report.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out,indent=2));assert all(checks.values()) and all(x['Detected'] for x in tests)
if __name__=='__main__':main()
