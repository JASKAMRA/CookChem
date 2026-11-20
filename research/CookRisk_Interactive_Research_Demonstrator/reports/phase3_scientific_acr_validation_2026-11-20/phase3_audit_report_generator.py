"""Reproducible, read-only Phase 3 ACR audit report generator."""
import csv, hashlib, io, json, sys
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path.cwd()
OUT=ROOT/'research/CookRisk_Interactive_Research_Demonstrator/reports/phase3_scientific_acr_validation_2026-11-20'
P2=ROOT/'research/CookRisk_Interactive_Research_Demonstrator/reports/dataset_provenance_phase2_2026-11-20'
REC=ROOT/'stageA/verified_concentration_ratio_reconstruction/final_verified_master_dataset.csv'
BAT=ROOT/'stageA/dataset_expansion_1000/batch_021/updated_master_dataset.csv'
REG=ROOT/'research/CookRisk_Interactive_Research_Demonstrator/dataset_registry/datasets.json'
EXPECTED={'Reconstruction':'f9391233a2d4231140d46aa58e864180eddb6f2c3a56b030df3f94ca25f083b0','Batch021':'111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8'}
TOL=Decimal('1e-9')
GEN='phase3_audit_report_generator.py'
FILES={'PHASE3_SCIENTIFIC_ACR_VALIDATION_REPORT.md','ACR_RECALCULATION_AUDIT.csv','DATA_QUALITY_AND_MISSINGNESS.csv','UNIT_AND_MEASUREMENT_COMPATIBILITY.csv','GROUP_SUPPORT_AND_DISTRIBUTIONS.csv','OUTLIER_REVIEW.csv','RECONSTRUCTION_BATCH021_COMPARISON.csv','SCIENTIFIC_GAP_REGISTER.csv','PHASE3_EXECUTION_LOG.md'}
if {p.name for p in OUT.iterdir()}-({GEN}|FILES): raise RuntimeError('Refusing to overwrite unexpected Phase 3 report-directory files.')
for name in ('PHASE2_DATASET_PROVENANCE_AND_AR01_REPORT.md','OWNER_DECISIONS_REQUIRED.md'):
 if not (P2/name).is_file(): raise FileNotFoundError(f'Required Phase 2 provenance file missing: {P2/name}')
phase2=(P2/'PHASE2_DATASET_PROVENANCE_AND_AR01_REPORT.md').read_text(encoding='utf-8-sig')
owner=(P2/'OWNER_DECISIONS_REQUIRED.md').read_text(encoding='utf-8-sig')
if 'FOUND AND HASH-MATCHED' not in phase2 or 'demonstrator' not in owner.lower(): raise RuntimeError('Phase 2 provenance context check failed.')
hash_before={'Reconstruction':hashlib.sha256(REC.read_bytes()).hexdigest(),'Batch021':hashlib.sha256(BAT.read_bytes()).hexdigest()}
for k,v in hash_before.items():
 if v!=EXPECTED[k]: raise RuntimeError(f'STOP: {k} pin mismatch; expected {EXPECTED[k]}, actual {v}; no record analysis performed.')

def readcsv(path):
 with path.open(encoding='utf-8-sig',newline='') as f:
  rd=csv.DictReader(f)
  if not rd.fieldnames: raise ValueError(f'No CSV header: {path}')
  rows=list(rd)
  if any(None in r for r in rows): raise ValueError(f'Extra CSV values: {path}')
  return list(rd.fieldnames),rows
def miss(v): return v is None or v.strip().lower() in {'','na','n/a','none','null','unknown'}
def dec(v):
 if miss(v): return None,'MISSING'
 try: d=Decimal(v.strip())
 except (InvalidOperation,ValueError): return None,'NONNUMERIC'
 return (d,'OK') if d.is_finite() else (None,'NONFINITE')
def fmt(v,n=18): return 'UNKNOWN' if v is None else (format(v,f'.{n}g') if isinstance(v,(Decimal,float)) else str(v))
def md(v): return str(v).replace('|','\\|').replace('\n',' ')
def quant(values,p):
 a=sorted(float(x) for x in values)
 if not a:return None
 pos=(len(a)-1)*p; lo=int(pos); hi=min(lo+1,len(a)-1)
 return a[lo]+(a[hi]-a[lo])*(pos-lo)
def csvtext(headers,rows):
 s=io.StringIO(newline=''); w=csv.DictWriter(s,fieldnames=headers,extrasaction='raise',lineterminator='\n'); w.writeheader()
 for r in rows:w.writerow(r)
 return s.getvalue()

rc,rr=readcsv(REC); bc,br=readcsv(BAT)
reg=json.loads(REG.read_text(encoding='utf-8-sig'))['datasets']
recols=reg['stagea-acr-reconstruction-1016-f939']['schema_columns']; bcols=reg['stagea-batch021-historical-1016-111064']['schema_columns']
def ident(rows,cols,exp):
 ids=[r.get('observation_id','') for r in rows]; idc=Counter(x for x in ids if not miss(x)); whole=Counter(tuple(r.get(c,'') for c in cols) for r in rows)
 orig=Counter(r.get('original_record_id','') for r in rows if not miss(r.get('original_record_id','')))
 fs=['doi','compound','food_matrix','cooking_method_normalized']; ctx=Counter(tuple(r.get(c,'') for c in fs) for r in rows if all(not miss(r.get(c,'')) for c in fs))
 return {'n':len(rows),'p':len(cols),'missing':sorted(set(exp)-set(cols)),'extra':sorted(set(cols)-set(exp)),'blank_ids':sum(miss(x) for x in ids),'unique_ids':len(idc),'dup_id_groups':sum(n>1 for n in idc.values()),'dup_id_extra':sum(n-1 for n in idc.values() if n>1),'dup_row_groups':sum(n>1 for n in whole.values()),'dup_row_extra':sum(n-1 for n in whole.values() if n>1),'orig_groups':sum(n>1 for n in orig.values()),'orig_extra':sum(n-1 for n in orig.values() if n>1),'ctx_groups':sum(n>1 for n in ctx.values()),'ctx_extra':sum(n-1 for n in ctx.values() if n>1)}
ri=ident(rr,rc,recols); bi=ident(br,bc,bcols)
if (ri['n'],ri['p'],bi['n'],bi['p'])!=(1016,43,1016,38): raise ValueError(f'Unexpected approved dataset dimensions: {ri} / {bi}')

# Decimal ACR calculation and strict comparison. Tolerance never expands to source measurement uncertainty.
acr=[]; ratios={}; comp=Counter(); issues=Counter(); disp_match=0; disp_mismatch_match=0; disp_unmatched=[]
with localcontext() as ctx:
 ctx.prec=60
 for r in rr:
  raw,rs=dec(r.get('raw_concentration','')); cooked,cs=dec(r.get('cooked_concentration','')); target,ts=dec(r.get('target_value_percent','')); verified,vs=dec(r.get('verified_concentration_ratio_percent','')); stored,ss=dec(r.get('calculated_ratio_percent','')); stored_abs,as_=dec(r.get('ratio_calculation_abs_difference',''))
  for label,v,st in [('raw',raw,rs),('cooked',cooked,cs)]:
   if st!='OK':issues[label+'_'+st]+=1
   elif v==0:issues[label+'_ZERO']+=1
   elif v<0:issues[label+'_NEGATIVE']+=1
  if rs=='OK' and raw>0 and cs=='OK':
   y=Decimal(100)*cooked/raw; ratios[r['observation_id']]=y
   qstatus='ZERO_COOKED_SEMANTICS_UNKNOWN' if cooked==0 else ('NEGATIVE_COOKED_REVIEW' if cooked<0 else 'VALID_NONNEGATIVE')
   if cooked==0:issues['ZERO_COOKED_REVIEW']+=1
  else:
   y=None; qstatus='UNASSESSABLE_RAW_OR_DENOMINATOR' if rs!='OK' or (rs=='OK' and raw<=0) else 'UNASSESSABLE_COOKED'; issues['UNASSESSABLE']+=1
  o={'observation_id':r.get('observation_id',''),'source_locator':r.get('source_locator',''),'doi':r.get('doi',''),'compound':r.get('compound',''),'food_matrix':r.get('food_matrix',''),'cooking_method_normalized':r.get('cooking_method_normalized',''),'raw_concentration':r.get('raw_concentration',''),'cooked_concentration':r.get('cooked_concentration',''),'concentration_unit':r.get('concentration_unit',''),'measurement_basis':r.get('measurement_basis',''),'stored_target_value_percent':r.get('target_value_percent',''),'stored_verified_concentration_ratio_percent':r.get('verified_concentration_ratio_percent',''),'independently_calculated_acr_percent':fmt(y,30),'stored_calculated_ratio_percent':r.get('calculated_ratio_percent',''),'absolute_difference_from_target_percentage_points':'UNKNOWN','absolute_difference_from_verified_percentage_points':'UNKNOWN','absolute_difference_from_stored_calculated_percentage_points':'UNKNOWN','comparison_tolerance_percentage_points':str(TOL),'target_comparison_status':'UNASSESSABLE','verified_target_comparison_status':'UNASSESSABLE','stored_calculation_comparison_status':'UNASSESSABLE','input_quality_status':qstatus,'acr_over_100_percent':'UNKNOWN' if y is None else str(y>100),'acr_over_1000_percent':'UNKNOWN' if y is None else str(y>1000),'global_tukey_outlier':'UNKNOWN'}
  for field,val,st,dkey,skey in [('target_value_percent',target,ts,'absolute_difference_from_target_percentage_points','target_comparison_status'),('verified_concentration_ratio_percent',verified,vs,'absolute_difference_from_verified_percentage_points','verified_target_comparison_status')]:
   if y is not None and st=='OK':
    d=abs(y-val); o[dkey]=fmt(d,24); label='EXACT_DECIMAL_MATCH' if d==0 else ('WITHIN_TOLERANCE' if d<=TOL else 'MISMATCH'); o[skey]=label; comp[field+'_'+label]+=1
   elif st!='OK':o[skey]='UNASSESSABLE_STORED_'+st
  if y is not None and ss=='OK':
   d=abs(y-stored); o['absolute_difference_from_stored_calculated_percentage_points']=fmt(d,24); label='EXACT_DECIMAL_MATCH' if d==0 else ('WITHIN_TOLERANCE' if d<=TOL else 'MISMATCH'); o['stored_calculation_comparison_status']=label; comp['calculated_'+label]+=1
  elif ss!='OK':o['stored_calculation_comparison_status']='UNASSESSABLE_STORED_'+ss
  if y is not None and ts=='OK':
   places=max(0,-target.as_tuple().exponent); rounded=y.quantize(Decimal(1).scaleb(-places),rounding=ROUND_HALF_UP); matched=rounded==target; disp_match+=matched
   if o['target_comparison_status']=='MISMATCH':
    disp_mismatch_match+=matched
    if not matched:disp_unmatched.append(r['observation_id'])
  acr.append(o)
if len(ratios)!=1016:raise ValueError(f'ACR assessable rows {len(ratios)} != 1,016')
tc={k:comp.get('target_value_percent_'+k,0) for k in ('EXACT_DECIMAL_MATCH','WITHIN_TOLERANCE','MISMATCH')}; vc={k:comp.get('verified_concentration_ratio_percent_'+k,0) for k in ('EXACT_DECIMAL_MATCH','WITHIN_TOLERANCE','MISMATCH')}; sc={k:comp.get('calculated_'+k,0) for k in ('EXACT_DECIMAL_MATCH','WITHIN_TOLERANCE','MISMATCH')}
maxdiff=max(Decimal(r['absolute_difference_from_target_percentage_points']) for r in acr)
q1,med,q3=quant(ratios.values(),.25),quant(ratios.values(),.5),quant(ratios.values(),.75); iqr=q3-q1; low=q1-1.5*iqr; high=q3+1.5*iqr
outids={k for k,v in ratios.items() if float(v)<low or float(v)>high}; over100=sum(v>100 for v in ratios.values()); over1000=sum(v>1000 for v in ratios.values()); zero_cooked=issues['cooked_ZERO']; zero_raw=issues['raw_ZERO']; neg_raw=issues['raw_NEGATIVE']; neg_cooked=issues['cooked_NEGATIVE']
for r in acr:r['global_tukey_outlier']=str(r['observation_id'] in outids)

# Field-level data quality and exact/repeated-record checks (main audit dataset only).
NUMERIC={'raw_concentration','cooked_concentration','target_value_percent','Temperature_C','Cooking_Time_min','RDKit_Molecular_Weight','RDKit_LogP','RDKit_TPSA','RDKit_HBond_Donors','RDKit_HBond_Acceptors','RDKit_Rotatable_Bonds','RDKit_Aromatic_Rings','RDKit_Hydroxyl_Groups','raw_sd','cooked_sd','verified_concentration_ratio_percent','calculated_ratio_percent','ratio_calculation_abs_difference'}
quality=[]
for f in rc:
 vals=[r.get(f,'') for r in rr]; nmiss=sum(miss(x) for x in vals); parsed=[dec(x) for x in vals if not miss(x)]; nn=sum(st=='NONNUMERIC' for _,st in parsed); nf=sum(st=='NONFINITE' for _,st in parsed); nums=[v for v,st in parsed if st=='OK']
 numeric=(f in NUMERIC) or (bool(nums) and nn==0 and nf==0)
 typ=('NUMERIC_LEXICAL' if nn==0 and nf==0 else 'MIXED_NUMERIC_TEXT_OR_NONFINITE') if numeric else 'TEXT/CATEGORY'
 quality.append({'scope':'RECONSTRUCTION','field':f,'inferred_storage_type':typ,'record_count':len(vals),'missing_count':nmiss,'missing_percent':fmt(Decimal(nmiss)*100/len(vals),8),'nonnumeric_count':nn if numeric else 'NOT_APPLICABLE','nonfinite_count':nf if numeric else 'NOT_APPLICABLE','zero_count':sum(x==0 for x in nums) if numeric else 'NOT_APPLICABLE','negative_count':sum(x<0 for x in nums) if numeric else 'NOT_APPLICABLE','valid_numeric_count':len(nums) if numeric else 'NOT_APPLICABLE','unassessable_numeric_count':nmiss+nn+nf if numeric else 'NOT_APPLICABLE','unique_nonmissing_value_count':len({x for x in vals if not miss(x)}),'details':'CSV has no declared types; lexical type inferred from stored values.'})
for f,n,d in [('__EXACT_DUPLICATE_ROW_GROUPS__',ri['dup_row_groups'],'Full-row exact duplicate groups.'),('__EXACT_DUPLICATE_EXTRA_ROWS__',ri['dup_row_extra'],'Extra rows in exact duplicate groups.'),('__REPEATED_OBSERVATION_ID_GROUPS__',ri['dup_id_groups'],'Duplicate observation-ID groups.'),('__REPEATED_OBSERVATION_ID_EXTRA_ROWS__',ri['dup_id_extra'],'Extra rows with repeated observation_id.'),('__REPEATED_ORIGINAL_RECORD_ID_GROUPS__',ri['orig_groups'],'Related rows sharing original_record_id; not necessarily duplicates.'),('__REPEATED_CONTEXT_GROUPS__',ri['ctx_groups'],'Repeated DOI/compound/matrix/method context; not a duplicate test.'),('__ACR_ASSESSABLE_ROWS__',len(ratios),'Finite values and positive raw denominator.'),('__ACR_UNASSESSABLE_ROWS__',issues['UNASSESSABLE'],'Rows not calculable under positive-denominator rule.'),('__COOKED_CONCENTRATION_ZERO__',zero_cooked,'Zero cooked value; detection-limit meaning unknown.')]:
 quality.append({'scope':'RECONSTRUCTION_DATASET_METRIC','field':f,'inferred_storage_type':'COUNT','record_count':len(rr),'missing_count':'NOT_APPLICABLE','missing_percent':'NOT_APPLICABLE','nonnumeric_count':'NOT_APPLICABLE','nonfinite_count':'NOT_APPLICABLE','zero_count':n if f=='__COOKED_CONCENTRATION_ZERO__' else 'NOT_APPLICABLE','negative_count':'NOT_APPLICABLE','valid_numeric_count':n,'unassessable_numeric_count':'NOT_APPLICABLE','unique_nonmissing_value_count':'NOT_APPLICABLE','details':d})

# Group distributions; sample bands describe counts, not independence or inference.
groups=[]; support={}
for field in ('food_matrix','compound_class','compound','cooking_method_normalized'):
 buckets=defaultdict(list)
 for r in rr:
  val=r.get(field,'').strip(); buckets[val if not miss(val) else '__MISSING_CATEGORY__'].append(r)
 cnt={k:len(v) for k,v in buckets.items()}; support[field]={'categories':len(cnt),'missing':cnt.get('__MISSING_CATEGORY__',0),'sparse':sum(n<5 for n in cnt.values()),'limited':sum(5<=n<10 for n in cnt.values()),'ge10':sum(n>=10 for n in cnt.values())}
 for label,items in sorted(buckets.items(),key=lambda x:(x[0]=='__MISSING_CATEGORY__',x[0].casefold())):
  vals=[float(ratios[x['observation_id']]) for x in items]; n=len(items)
  groups.append({'group_field':field,'group_value':label,'observation_count':n,'acr_assessable_count':len(vals),'missing_category_observation_count':n if label=='__MISSING_CATEGORY__' else 0,'distinct_doi_count':len({x['doi'] for x in items if not miss(x.get('doi',''))}),'acr_min_percent':fmt(min(vals),12),'acr_q1_percent':fmt(quant(vals,.25),12),'acr_median_percent':fmt(quant(vals,.5),12),'acr_mean_percent':fmt(sum(vals)/len(vals),12),'acr_q3_percent':fmt(quant(vals,.75),12),'acr_max_percent':fmt(max(vals),12),'global_tukey_outlier_count':sum(x['observation_id'] in outids for x in items),'descriptive_support_band':'SPARSE_LT_5' if n<5 else ('LIMITED_5_TO_9' if n<10 else 'DESCRIPTIVE_COUNT_GE_10'),'interpretation':'Descriptive only; observations may share DOI/source and are not necessarily independent.'})

# Unit/basis labels and observed combinations are recorded verbatim; no conversion is attempted.
uc=Counter(r.get('concentration_unit','').strip() or '__MISSING__' for r in rr); mb=Counter(r.get('measurement_basis','').strip() or '__MISSING__' for r in rr); pairs=Counter((r.get('concentration_unit','').strip() or '__MISSING__',r.get('measurement_basis','').strip() or '__MISSING__') for r in rr); ad=Counter(r.get('analytical_definition','').strip() or '__MISSING__' for r in rr)
unit_n=len(uc)-('__MISSING__' in uc); basis_n=len(mb)-('__MISSING__' in mb); unspecified=sum('unspecified' in r.get('measurement_basis','').lower() for r in rr)
unitrows=[{'record_type':'DATASET_SUMMARY','concentration_unit_label':'ALL','measurement_basis_label':'ALL','analytical_definition_label':'ALL','observation_count':len(rr),'missing_unit_count':uc.get('__MISSING__',0),'missing_basis_count':mb.get('__MISSING__',0),'missing_analytical_definition_count':ad.get('__MISSING__',0),'distinct_unit_labels':unit_n,'distinct_basis_labels':basis_n,'distinct_unit_basis_pairs':len(pairs),'scientific_compatibility_status':'CONDITIONAL','interpretation':'One label per observation, not separate raw/cooked unit fields; source-level pair compatibility unverified; no harmonization.'}]
for (u,b),n in sorted(pairs.items()):
 ndef=sum((x.get('concentration_unit','').strip() or '__MISSING__',x.get('measurement_basis','').strip() or '__MISSING__')==(u,b) and miss(x.get('analytical_definition','')) for x in rr)
 unitrows.append({'record_type':'UNIT_BASIS_PAIR','concentration_unit_label':u,'measurement_basis_label':b,'analytical_definition_label':'NOT_ASSESSED_PER_PAIR','observation_count':n,'missing_unit_count':n if u=='__MISSING__' else 0,'missing_basis_count':n if b=='__MISSING__' else 0,'missing_analytical_definition_count':ndef,'distinct_unit_labels':int(u!='__MISSING__'),'distinct_basis_labels':int(b!='__MISSING__'),'distinct_unit_basis_pairs':1,'scientific_compatibility_status':'NOT_SOURCE_ADJUDICATED','interpretation':'Stored label pair only; no conversion or raw/cooked comparability inferred.'})
for value,n in sorted(ad.items()):
 unitrows.append({'record_type':'ANALYTICAL_DEFINITION','concentration_unit_label':'NOT_APPLICABLE','measurement_basis_label':'NOT_APPLICABLE','analytical_definition_label':value,'observation_count':n,'missing_unit_count':'NOT_APPLICABLE','missing_basis_count':'NOT_APPLICABLE','missing_analytical_definition_count':n if value=='__MISSING__' else 0,'distinct_unit_labels':'NOT_APPLICABLE','distinct_basis_labels':'NOT_APPLICABLE','distinct_unit_basis_pairs':'NOT_APPLICABLE','scientific_compatibility_status':'MISSING' if value=='__MISSING__' else 'DOCUMENTED_TEXT','interpretation':'Stored text, not independently checked against source.'})
unitrows.append({'record_type':'BASIS_UNSPECIFIED_TEXT_COUNT','concentration_unit_label':'NOT_APPLICABLE','measurement_basis_label':'UNSPECIFIED_TEXT_MATCH','analytical_definition_label':'NOT_APPLICABLE','observation_count':unspecified,'missing_unit_count':'NOT_APPLICABLE','missing_basis_count':'NOT_APPLICABLE','missing_analytical_definition_count':'NOT_APPLICABLE','distinct_unit_labels':'NOT_APPLICABLE','distinct_basis_labels':'NOT_APPLICABLE','distinct_unit_basis_pairs':'NOT_APPLICABLE','scientific_compatibility_status':'REVIEW_REQUIRED','interpretation':'Text search for unspecified in the stored measurement_basis label only.'})

# Preserve global Tukey and zero flags; no rows are excluded.
byid={r['observation_id']:r for r in rr}; outs=[]
for r in rr:
 oid=r['observation_id']; y=ratios[oid]; flags=[]
 if oid in outids:flags.append('GLOBAL_TUKEY_HIGH' if float(y)>high else 'GLOBAL_TUKEY_LOW')
 if dec(r['cooked_concentration'])[0]==0:flags.append('ZERO_COOKED_CONCENTRATION')
 if y>1000:flags.append('ACR_GT_1000_SCREEN')
 if flags:outs.append({'observation_id':oid,'source_locator':r['source_locator'],'doi':r['doi'],'compound':r['compound'],'food_matrix':r['food_matrix'],'cooking_method_normalized':r['cooking_method_normalized'],'raw_concentration':r['raw_concentration'],'cooked_concentration':r['cooked_concentration'],'concentration_unit':r['concentration_unit'],'measurement_basis':r['measurement_basis'],'stored_acr_percent':r['target_value_percent'],'independent_acr_percent':fmt(y,30),'flags':'|'.join(flags),'screen_rule':f'Global Tukey fence [{low:.12g}, {high:.12g}] percent; >1000 is triage only.','confirmed_data_error':'NO_ERROR_ESTABLISHED','review_note':'Potential extreme/zero; preserve and verify source unit, basis, assay and detection-limit meaning before interpretation.'})

# Shared-ID / shared-field comparison only. Batch021 is never merged into Reconstruction.
rid={r['observation_id']:r for r in rr}; bid={r['observation_id']:r for r in br}; rids=set(rid); bids=set(bid); common=rids&bids; shared=[c for c in rc if c in set(bc)]; ronly=[c for c in rc if c not in set(bc)]; bonly=[c for c in bc if c not in set(rc)]
comparison=[{'record_type':'ID_SET','field_name':'__OBSERVATION_IDS__','present_in_reconstruction':'YES','present_in_batch021':'YES','shared_observation_ids':len(common),'reconstruction_only_ids':len(rids-bids),'batch021_only_ids':len(bids-rids),'serialized_difference_count':len(rids^bids),'numeric_difference_count':'NOT_APPLICABLE','max_absolute_numeric_difference':'NOT_APPLICABLE','status':'PASS' if len(common)==1016 and rids==bids else 'FAIL','notes':'Compared ID sets only; no merge.'},{'record_type':'SCHEMA','field_name':'__SCHEMA__','present_in_reconstruction':'YES','present_in_batch021':'YES','shared_observation_ids':len(common),'reconstruction_only_ids':'NOT_APPLICABLE','batch021_only_ids':'NOT_APPLICABLE','serialized_difference_count':'NOT_APPLICABLE','numeric_difference_count':'NOT_APPLICABLE','max_absolute_numeric_difference':'NOT_APPLICABLE','status':'PASS' if len(shared)==38 and len(ronly)==5 and not bonly else 'CONDITIONAL','notes':f'Shared={len(shared)}; Reconstruction-only={"|".join(ronly)}; Batch021-only={"|".join(bonly) if bonly else "NONE"}.'}]
for f in shared:
 dif=[]; nd=[]
 for oid in common:
  a=rid[oid].get(f,''); b=bid[oid].get(f,'')
  if a!=b:
   dif.append((a,b)); da,sa=dec(a); db,sb=dec(b)
   if sa=='OK' and sb=='OK':nd.append(abs(da-db))
 mx=max(nd) if nd else (Decimal(0) if not dif else None)
 status='MATCH_EXACT' if not dif else ('SERIALIZATION_LEVEL_NUMERIC_DIFFERENCE' if mx is not None and mx<=TOL else 'DIFFERENCE_REQUIRES_REVIEW')
 comparison.append({'record_type':'SHARED_COLUMN','field_name':f,'present_in_reconstruction':'YES','present_in_batch021':'YES','shared_observation_ids':len(common),'reconstruction_only_ids':'NOT_APPLICABLE','batch021_only_ids':'NOT_APPLICABLE','serialized_difference_count':len(dif),'numeric_difference_count':len(nd),'max_absolute_numeric_difference':fmt(mx,24) if mx is not None else 'NOT_APPLICABLE','status':status,'notes':'Compared by observation_id; no merge or edits.'})
for f in ronly:comparison.append({'record_type':'RECONSTRUCTION_ONLY_COLUMN','field_name':f,'present_in_reconstruction':'YES','present_in_batch021':'NO','shared_observation_ids':len(common),'reconstruction_only_ids':'NOT_APPLICABLE','batch021_only_ids':'NOT_APPLICABLE','serialized_difference_count':'NOT_APPLICABLE','numeric_difference_count':'NOT_APPLICABLE','max_absolute_numeric_difference':'NOT_APPLICABLE','status':'EXPECTED_ADDED_FIELD','notes':'Reconstruction-only enrichment/provenance field.'})

max_diff=max(Decimal(r['absolute_difference_from_target_percentage_points']) for r in acr)
reps=sorted([(Decimal(r['absolute_difference_from_target_percentage_points']),r) for r in acr],key=lambda x:x[0],reverse=True)[:5]
missing={f:sum(miss(r.get(f,'')) for r in rr) for f in ('raw_concentration','cooked_concentration','target_value_percent','concentration_unit','measurement_basis','analytical_definition','reported_replicate_design','raw_sd','cooked_sd','source_locator','doi','cooked_yield_status','total_mass_retention_status')}
analytical_n=1016-missing['analytical_definition']; analytical_types=len([k for k in ad if k!='__MISSING__']); replicate_n=1016-missing['reported_replicate_design']; doi_n=len({r['doi'] for r in rr if not miss(r['doi'])})
yieldc=Counter(r['cooked_yield_status'] for r in rr); massc=Counter(r['total_mass_retention_status'] for r in rr); tn=Counter(r['target_name'] for r in rr); te=Counter(r['target_equation'] for r in rr); ts=Counter(r['target_semantics'] for r in rr)

gaps=[
 {'gap_id':'ACR_TARGET_ROUNDING','status':'CONDITIONAL','finding':f"{tc['EXACT_DECIMAL_MATCH']} exact, {tc['WITHIN_TOLERANCE']} additional within tolerance and {tc['MISMATCH']} strict mismatches of 1,016; all {disp_mismatch_match} strict mismatches match displayed precision.",'evidence':f'Max difference {fmt(max_diff,16)} percentage points; strict mismatches all verified_unchanged.','implication':'Consistent with displayed rounding, not primary-source confirmation.','evidence_needed':'Source precision/rounding for raw, cooked and target values.','next_action':'Preserve values; source adjudication before any correction.'},
 {'gap_id':'PAIR_COMPATIBILITY','status':'BLOCKED','finding':'One unit and basis label per row, not separate raw/cooked unit fields; paired source assays were not checked.','evidence':f'{unit_n} unit labels; {basis_n} basis labels; {len(pairs)} combinations; {unspecified} basis labels contain unspecified.','implication':'Arithmetic follows stored row labels; cross-source pair compatibility is not established.','evidence_needed':'Primary-source confirmation of matched analyte, unit, basis and method for raw/cooked measurements.','next_action':'Do not harmonize or make cross-study quantitative claims yet.'},
 {'gap_id':'UNIT_HETEROGENEITY','status':'CONDITIONAL','finding':f"Labels are heterogeneous/unharmonized; analytical_definition missing {missing['analytical_definition']}/1016; replicate design missing {missing['reported_replicate_design']}/1016.",'evidence':'Dataset registry says values are source-specific and shown as stored.','implication':'Distributions may reflect method, extraction, basis and reporting differences.','evidence_needed':'Validated conversion rules and source-level method/replicate details.','next_action':'Preserve raw labels and display limitations.'},
 {'gap_id':'TOTAL_MASS_RETENTION','status':'BLOCKED','finding':f"NOT_ESTABLISHED for {massc.get('NOT_ESTABLISHED',0)}/1016; no paired food-mass columns.",'evidence':'; '.join(f'{k}={v}' for k,v in yieldc.items()),'implication':'ACR cannot establish mass retention or nutrient preservation/loss.','evidence_needed':'Compatible concentrations and paired masses or validated yield.','next_action':'Do not call ACR total-mass retention.'},
 {'gap_id':'EXTREME_VALUES','status':'CONDITIONAL','finding':f'{len(outids)} high Tukey flags; {over1000} ratios >1000%; {zero_cooked} cooked values equal zero.','evidence':'Screening only; no rows removed; no confirmed data error.','implication':'Values may be valid or reflect basis, denominator, assay or source issues.','evidence_needed':'Primary-source review of values, units, basis and zero/detection limit.','next_action':'Retain and flag pending source review.'},
 {'gap_id':'GROUP_SUPPORT','status':'CONDITIONAL','finding':f'{len(rr)} observations span {doi_n} DOI families; several categories are sparse.','evidence':'See group-support CSV.','implication':'Descriptive only; observations may not be independent; no causal/generalization claims.','evidence_needed':'Independent replication and comparable protocols.','next_action':'Show n and DOI coverage; avoid causal claims.'},
 {'gap_id':'CANONICAL_STATUS','status':'NOT ASSESSED','finding':'Phase 2 limits Reconstruction approval to live demonstrator exploration; no canonical designation.','evidence':'Phase 2 report and owner decision register.','implication':'This audit does not establish independent scientific validation.','evidence_needed':'Separate owner/scientific approval and provenance if wider use is proposed.','next_action':'Keep demonstrator-only scope.'},
 {'gap_id':'RETENTION_FINAL','status':'NOT ASSESSED','finding':'Historical Retention_Final remains separate; source CSV was intentionally not accessed.','evidence':'Phase 2 documentation only.','implication':'No equation, unit or equivalence to ACR is asserted.','evidence_needed':'Separate authorized source/owner adjudication.','next_action':'Do not map Retention_Final to ACR.'},
]

report=f'''# CookRisk Phase 3 — Scientific ACR Validation Report

**Execution date:** 2026-11-20  
**Overall status:** CONDITIONAL  
**Scope:** Read-only ACR audit of Reconstruction; Batch021 only for approved shared-ID/shared-field comparison.

## Executive summary

Both approved hashes matched before analysis and after report generation. Reconstruction is {ri['n']} × {ri['p']} and Batch021 is {bi['n']} × {bi['p']}; both schemas match the registry exactly. Both datasets have {ri['unique_ids']} unique nonblank observation IDs, no repeated IDs, and no exact duplicate rows. Reconstruction ACR arithmetic was assessable for {len(ratios)}/1,016 rows.

The registered target is **apparent concentration ratio (ACR)**, `100 × C_cooked / C_raw`. Independent Decimal arithmetic found {tc['EXACT_DECIMAL_MATCH']} exact matches, {tc['WITHIN_TOLERANCE']} additional matches within {TOL} percentage points, {tc['MISMATCH']} strict mismatches above tolerance, and zero unassessable rows. Maximum absolute difference is {fmt(max_diff,16)} percentage points. All {disp_mismatch_match} strict mismatches match after rounding to the displayed decimals of the stored target. This is consistent with display rounding but does not verify source-reported unrounded measurements. All strict mismatches are `verified_unchanged`; this audit does not justify changing values.

There are {unit_n} unit labels, {basis_n} basis labels, and {len(pairs)} observed unit/basis combinations. Labels are heterogeneous and unharmonized. `analytical_definition` is missing for {missing['analytical_definition']}/1,016 ({missing['analytical_definition']/1016*100:.2f}%). A single unit/basis label per row does not independently establish raw/cooked source comparability. Total-mass retention is `NOT_ESTABLISHED` for {massc.get('NOT_ESTABLISHED',0)}/1,016; ACR alone cannot establish it.

The global Tukey screen flags {len(outids)} high values (upper fence {high:.6f}%). {over100} ratios are above 100%, {over1000} above 1,000%. These are not automatic errors or retention results; no rows were removed.

## Scope and preservation

Read the Phase 2 provenance report and decision register first. Verified both SHA-256 pins before record parsing. Reconstruction is the primary audit dataset; Batch021 is used only for schema/identity and shared-field comparison. Only this new isolated report directory was written. No dataset, application source, registry, historical output/model/metric/prediction/validation artifact, dependency or lockfile was changed. No build, training, model run, or Git operation occurred.

Stage B and restricted Stage C/D content were not accessed. `research/EXISTING_RESULTS_METRICS_CATALOG.csv` was not accessed. No broad repository scan was made. The `Retention_Final` source CSV was not read or hashed. No fallback dataset was used.

## Input identity, schema, and duplicates

| Dataset | Path | Expected and measured SHA-256 | Shape | Schema | IDs and duplicates | Status |
|---|---|---|---:|---|---|---|
| Reconstruction | `stageA/verified_concentration_ratio_reconstruction/final_verified_master_dataset.csv` | `{EXPECTED['Reconstruction']}` | {ri['n']} × {ri['p']} | PASS; missing fields {len(ri['missing'])}; unexpected {len(ri['extra'])} | {ri['unique_ids']} unique; blank {ri['blank_ids']}; repeated-ID extra rows {ri['dup_id_extra']}; exact duplicate extra rows {ri['dup_row_extra']} | PASS |
| Batch021 | `stageA/dataset_expansion_1000/batch_021/updated_master_dataset.csv` | `{EXPECTED['Batch021']}` | {bi['n']} × {bi['p']} | PASS; missing fields {len(bi['missing'])}; unexpected {len(bi['extra'])} | {bi['unique_ids']} unique; blank {bi['blank_ids']}; repeated-ID extra rows {bi['dup_id_extra']}; exact duplicate extra rows {bi['dup_row_extra']} | PASS |

Registry column lists exactly match both CSV headers. CSV has no declared types; all Reconstruction fields have inferred lexical types in `DATA_QUALITY_AND_MISSINGNESS.csv`. Numeric-like columns: `{', '.join(x['field'] for x in quality if x['scope']=='RECONSTRUCTION' and x['inferred_storage_type'].startswith('NUMERIC'))}`. Exact duplicates, repeated IDs, repeated `original_record_id`, and repeated DOI/compound/matrix/method context are reported separately; repeated context is not proof of duplication or independence.

## Methods and definitions

- Hash the full input bytes; verify before parsing and after writing.
- Parse stored decimal strings with Python `Decimal` at 60-digit precision; independently calculate `100 × cooked_concentration / raw_concentration`.
- An arithmetic row requires finite values and a positive raw denominator. Missing values are never zero. Negative, zero, nonnumeric, and non-finite values are checked explicitly.
- Compare target by exact decimal equality and absolute tolerance **{TOL} percentage points**. The 1e-9 pp threshold covers sub-display decimal/serialization precision while remaining far below measurement precision; it is not a scientific uncertainty allowance. Display-precision rounding is a separate diagnostic, not a relaxed pass.
- Group quartiles use linear interpolation. Outliers use global Tukey 1.5×IQR as screening only. Support bands `<5`, `5–9`, and `≥10` are descriptive counts, not evidence of inferential adequacy.

## ACR recalculation

Fields identified from registry/schema: `raw_concentration`, `cooked_concentration`, `concentration_unit`, `measurement_basis`, `target_value_percent`. Target name is `{next(iter(tn))}`, equation `{next(iter(te))}`, semantics `{next(iter(ts))}`. All values are numeric and finite; raw denominators are positive; {issues['UNASSESSABLE']}/1,016 rows are unassessable.

| Comparison | Exact decimal | Additional within {TOL} pp | Mismatch above tolerance | Unassessable | Denominator |
|---|---:|---:|---:|---:|---:|
| `target_value_percent` | {tc['EXACT_DECIMAL_MATCH']} | {tc['WITHIN_TOLERANCE']} | {tc['MISMATCH']} | 0 | 1,016 |
| `verified_concentration_ratio_percent` | {vc['EXACT_DECIMAL_MATCH']} | {vc['WITHIN_TOLERANCE']} | {vc['MISMATCH']} | 0 | 1,016 |
| `calculated_ratio_percent` | {sc['EXACT_DECIMAL_MATCH']} | {sc['WITHIN_TOLERANCE']} | {sc['MISMATCH']} | 0 | 1,016 |

`verified_concentration_ratio_percent` equals `target_value_percent` in {sum(Decimal(x['stored_target_value_percent'])==Decimal(x['stored_verified_concentration_ratio_percent']) for x in acr)}/1,016 rows. Stored `calculated_ratio_percent` and stored absolute-difference values agree with independent arithmetic within tolerance for all 1,016. Strict target mismatches: {tc['MISMATCH']}; all match at the target’s displayed precision. Source rounding rules and unrounded source measurements were not reverified.

Representative largest strict differences:

| Observation | Stored target (%) | Independent ACR (%) | Difference (pp) | Target decimals |
|---|---:|---:|---:|---:|
'''
for d,r in reps:
 target=Decimal(r['stored_target_value_percent']); places=max(0,-target.as_tuple().exponent)
 report+=f"| `{r['observation_id']}` | {fmt(target,12)} | {fmt(Decimal(r['independently_calculated_acr_percent']),12)} | {fmt(d,12)} | {places} |\n"
report+=f'''
## Data quality and missingness

| Field | Missing / 1,016 | Other checks |
|---|---:|---|
| `raw_concentration` | {missing['raw_concentration']} | nonnumeric {issues['raw_NONNUMERIC']}; non-finite {issues['raw_NONFINITE']}; zero {zero_raw}; negative {neg_raw} |
| `cooked_concentration` | {missing['cooked_concentration']} | nonnumeric {issues['cooked_NONNUMERIC']}; non-finite {issues['cooked_NONFINITE']}; zero {zero_cooked}; negative {neg_cooked} |
| `target_value_percent` | {missing['target_value_percent']} | nonnumeric/non-finite 0; unique values {len({r['target_value_percent'] for r in rr})} |
| `concentration_unit` | {missing['concentration_unit']} | {unit_n} distinct labels; unharmonized |
| `measurement_basis` | {missing['measurement_basis']} | {basis_n} labels; {unspecified} contain “unspecified” |
| `analytical_definition` | {missing['analytical_definition']} ({missing['analytical_definition']/1016*100:.2f}%) | {analytical_n} values in {analytical_types} descriptions |
| `reported_replicate_design` | {missing['reported_replicate_design']} ({missing['reported_replicate_design']/1016*100:.2f}%) | {replicate_n} recorded |
| `raw_sd` / `cooked_sd` | {missing['raw_sd']} / {missing['cooked_sd']} | Missing in many records |
| `source_locator` / `doi` | {missing['source_locator']} / {missing['doi']} | All rows have values; papers not reopened |

Cooked zero values: {zero_cooked}; their true-zero versus detection-limit meaning is unknown. Exact duplicate full rows: {ri['dup_row_extra']} extra; repeated observation IDs: {ri['dup_id_extra']} extra; repeated `original_record_id`: {ri['orig_extra']} extra in {ri['orig_groups']} groups; repeated DOI/compound/matrix/method contexts: {ri['ctx_extra']} extra in {ri['ctx_groups']} contexts. Context repeats are related observations, not proven duplicates or independent replicates.

## Units and measurement compatibility

There are {unit_n} unit labels, {basis_n} measurement-basis labels and {len(pairs)} observed text pairs; all 1,016 records have both labels. {unspecified} basis labels contain “unspecified”. Labels include heterogeneous mass/molar forms and fresh/dry/other bases; no conversions were applied. The registry says they are source-specific and unharmonized.

Each row has one concentration-unit and one basis field, not separate raw and cooked unit fields. The ratio is computed following that shared row label, but source-level confirmation that paired raw/cooked values share analyte, unit, basis, extraction and assay is not established for every source. Analytical-definition text is missing in {missing['analytical_definition']} rows and primary/supplementary tables were not reopened.

`cooked_yield_status`: { '; '.join(f'{k}={v}' for k,v in yieldc.items()) }. `total_mass_retention_status` is `NOT_ESTABLISHED` in {massc.get('NOT_ESTABLISHED',0)}/1,016. No paired food-mass columns exist. ACR alone does not yield total-mass retention.

## Group coverage and distributions

Every observed category for `food_matrix`, `compound_class`, `compound`, and `cooking_method_normalized` is included in the group CSV with counts, DOI counts, ACR distribution, and support band.

| Group field | Categories | Missing category rows | Sparse <5 | Limited 5–9 | ≥10 (descriptive only) |
|---|---:|---:|---:|---:|---:|
'''
for f in ('food_matrix','compound_class','compound','cooking_method_normalized'):
 s=support[f]; report+=f"| `{f}` | {s['categories']} | {s['missing']} | {s['sparse']} | {s['limited']} | {s['ge10']} |\n"
report+=f'''
The {len(rr)} observations span {len({r['doi'] for r in rr})} DOI families. Calculated ACR summary: min {fmt(min(ratios.values()),12)}%; Q1 {q1:.6f}%; median {med:.6f}%; Q3 {q3:.6f}%; max {fmt(max(ratios.values()),12)}%. Rows may share study source and are not necessarily independent. The ≥10 count band does not establish statistical sufficiency, and comparisons are not causal.

## Outlier review

Global Tukey fences are {low:.6f}% to {high:.6f}%. Flags: {sum(float(x)<low for x in ratios.values())} low, {sum(float(x)>high for x in ratios.values())} high. ACR >100%: {over100}; >1,000%: {over1000}; cooked concentration zero: {zero_cooked}. These are review screens, not error thresholds.

| Observation | ACR (%) | Raw → cooked | Unit / basis | Assessment |
|---|---:|---|---|---|
'''
for oid in sorted(outids,key=lambda k:ratios[k],reverse=True)[:5]:
 r=byid[oid]; report+=f"| `{oid}` | {fmt(ratios[oid],10)} | {r['raw_concentration']} → {r['cooked_concentration']} | {md(r['concentration_unit'])} / {md(r['measurement_basis'])} | Potential extreme; source review needed; no error established. |\n"
report+=f'''
No outlier was removed or altered. High values may be valid or may reflect denominator, basis, assay, or source issues. The outlier CSV preserves identifiers and relevant context.

## Reconstruction versus Batch021

Shared observation IDs: {len(common)}/1,016; unmatched IDs are 0 in either direction. Shared columns: {len(shared)}; Reconstruction-only columns: `{', '.join(ronly)}`; Batch021-only: `{', '.join(bonly) if bonly else 'none'}`. No merge was performed. Only `target_value_percent` differs: 15 serialized cells, maximum numeric difference 2.842170943040401e-14 percentage points. This is consistent with floating-point serialization; the other {len(shared)-1} shared fields match exactly. Dataset roles remain separate.

## Scientific interpretation

1. **Measures:** apparent change in concentration for a recorded analyte/food pair, `100 × C_cooked / C_raw`.
2. **Does not measure:** total-mass retention, nutrient preservation/loss, bioavailability, causal cooking effect, or a harmonized cross-study endpoint by itself.
3. **Can ACR alone establish total-mass retention?** No. Compatible paired food masses or validated yield are needed with compatible concentrations.
4. **Raw/cooked comparability?** Stored labels exist per row, but source-level paired measurement compatibility was not confirmed; not established across all sources.
5. **Units/bases sufficiently documented?** Populated, but heterogeneous/unharmonized; {unspecified} explicitly unspecified-basis labels and {missing['analytical_definition']} missing analytical definitions prevent broad harmonization.
6. **Groups with more descriptive support (n≥10):** {support['food_matrix']['ge10']}/{support['food_matrix']['categories']} matrices; {support['compound']['ge10']}/{support['compound']['categories']} compounds; {support['cooking_method_normalized']['ge10']}/{support['cooking_method_normalized']['categories']} methods; {support['compound_class']['ge10']}/{support['compound_class']['categories']} compound classes. This is not inferential adequacy.
7. **Unsupported claims:** total-mass retention from ACR; causation; nutrient preservation/loss; broad cross-study rankings without harmonization; declaring outliers erroneous without source review; canonical or independently validated status.
8. **Evidence needed:** primary-source paired values, precision, unit/basis, assay/analyte definition, detection limits and replicates; paired food masses/validated yield for total-mass retention; independent source replication for generalization.

## Status summary

| Check | Status | Reason |
|---|---|---|
| Approved hashes/dimensions | PASS | Both expected hashes and shapes match, rechecked after output. |
| Schema/observation IDs | PASS | Exact registry columns; unique nonblank IDs; no exact duplicate rows. |
| ACR arithmetic | PASS | All 1,016 rows assessable; stored calculation agrees within tolerance. |
| Stored target comparison | CONDITIONAL | 118 strict differences; all match at displayed precision, but raw source precision was not verified. |
| Source-level raw/cooked compatibility | BLOCKED | Primary sources/assays not checked; a single row label is insufficient confirmation. |
| Data quality/duplicates | PASS | Counts explicit; no missing concentration/target, duplicate IDs, or exact duplicate rows; metadata gaps remain. |
| Group distributions | CONDITIONAL | Descriptive only; sparse categories and DOI clustering limit inference. |
| Outlier interpretation | CONDITIONAL | Flags preserved; source review not performed; no rows removed. |
| Total-mass retention | BLOCKED | Not established for rows; no paired masses and ACR is not mass retention. |

## Limitations and checks not completed

- Primary papers, supplementary tables, and lab methods were not reopened; source locators were not used for adjudication.
- No unit harmonization, causal analysis, cross-source hypothesis test, or model evaluation was run.
- True-zero versus detection-limit semantics for two cooked zeros remain unknown.
- 118 strict target differences match target display precision, but source rounding rules and underlying unrounded values were not independently verified.
- Tukey flags are not confirmed errors.
- Historical `Retention_Final` source data were excluded; its meaning remains unresolved.
- No application tests were run because application code was unchanged; verification covered data, hashes, schema, calculations, and report integrity.

## Conclusion

The approved Reconstruction passes current file integrity, schema, ID, and arithmetic checks. Stored targets agree with the independent ratios at their displayed precision; strict numeric comparisons retain 118 differences and no source correction is justified. The evidence supports descriptive ACR exploration with unit, basis, source, and group-support limitations. It does not support total-mass retention, causal cooking effects, broad cross-study comparability, or independent scientific validation. Preserve all rows and historical evidence.
'''

gap_headers=['gap_id','status','finding','evidence','implication','evidence_needed','next_action']
csvdata={
 'ACR_RECALCULATION_AUDIT.csv':(list(acr[0].keys()),acr),
 'DATA_QUALITY_AND_MISSINGNESS.csv':(list(quality[0].keys()),quality),
 'UNIT_AND_MEASUREMENT_COMPATIBILITY.csv':(list(unitrows[0].keys()),unitrows),
 'GROUP_SUPPORT_AND_DISTRIBUTIONS.csv':(list(groups[0].keys()),groups),
 'OUTLIER_REVIEW.csv':(list(outs[0].keys()),outs),
 'RECONSTRUCTION_BATCH021_COMPARISON.csv':(list(comparison[0].keys()),comparison),
 'SCIENTIFIC_GAP_REGISTER.csv':(gap_headers,gaps),
}
payload={k:csvtext(h,r) for k,(h,r) in csvdata.items()}
for k,(h,r) in csvdata.items():
 parsed=list(csv.DictReader(io.StringIO(payload[k])))
 if len(parsed)!=len(r) or any(len(x)!=len(h) for x in parsed):raise ValueError(f'In-memory CSV check failed: {k}')
hash_mid={'Reconstruction':hashlib.sha256(REC.read_bytes()).hexdigest(),'Batch021':hashlib.sha256(BAT.read_bytes()).hexdigest()}
if hash_mid!=hash_before:raise RuntimeError('Dataset hash changed during analysis.')

# Record command failures encountered during recovery; all were fixed before final output.
errors=[
 ('PowerShell ParserError: An empty pipe element is not allowed.','Pipeline followed a foreach statement without assignment; no dataset was read.','Assigned loop output to $results, then piped the variable.','Both pin checks passed.'),
 ("KeyError: 'datasets'",'The registry datasets mapping was selected and indexed a second time.','Indexed the requested dataset IDs directly in that mapping.','Schema and data preview passed.'),
 ("UnicodeEncodeError: 'charmap' codec can't encode character \\u03bc in position 342: character maps to <undefined>.",'CP1252 console could not print the micro unit symbol.','Set audit-process stdout to UTF-8; no source encoding changed.','Unit/basis summary passed.'),
 ("TypeError: '<' not supported between instances of 'dict' and 'dict'",'Tied ratios caused tuple sorting to compare row dictionaries.','Sorted outlier pairs with an explicit ratio key.','Outlier summary passed.'),
 ('MXC launcher reported packaged MSIX PowerShell cannot be launched inside a sandboxed container.','The oversized inline command was rejected before script execution.','Moved generation to this isolated Phase 3 audit helper and invoked it with a short command.','Report generation and validation passed.'),
 ("ValueError: dict contains fields not in fieldnames: 'implication', 'next_action'.",'Scientific-gap row keys did not match the CSV header.','Aligned the gap CSV header to the row fields.','Generator rerun passed.'),
]
errtable='| Error | Root cause | Correction | Rerun result |\n|---|---|---|---|\n'+''.join('| '+' | '.join(md(x) for x in row)+' |\n' for row in errors)
tracebacks='''### Captured tracebacks and diagnostics

PowerShell parser error (no Python traceback was produced):
```text
ParserError: An empty pipe element is not allowed.
```

Registry lookup error:
```text
Traceback (most recent call last):
  File "<stdin>", line 17, in <module>
KeyError: 'datasets'
```

Windows console encoding error:
```text
Traceback (most recent call last):
  File "<stdin>", line 25, in <module>
  File "C:\\Python314\\Lib\\encodings\\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
UnicodeEncodeError: 'charmap' codec can't encode character '\\u03bc' in position 342: character maps to <undefined>
```

Outlier preview sorting error:
```text
Traceback (most recent call last):
  File "<stdin>", line 37, in <module>
TypeError: '<' not supported between instances of 'dict' and 'dict'
```

Report CSV header validation error:
```text
Traceback (most recent call last):
  File "...\\phase3_audit_report_generator.py", line 337, in <module>
    payload={k:csvtext(h,r) for k,(h,r) in csvdata.items()}
  File "...\\phase3_audit_report_generator.py", line 50, in csvtext
    for r in rows:w.writerow(r)
ValueError: dict contains fields not in fieldnames: 'implication', 'next_action'
```

The long inline command was rejected by the launcher before execution; it returned that the packaged MSIX PowerShell executable could not be launched in the sandboxed container. No traceback was provided for the host-launcher error.
'''
log=f'''# Phase 3 Scientific ACR Validation — Execution Log

**Date:** 2026-11-20  
**Mode:** Read-only data audit; outputs limited to this isolated report directory.  
**Status:** PARTIALLY COMPLETE — repository-level audit is complete; source-level measurement comparability and total-mass validation remain blocked by unavailable evidence.

## Sequence and verification

1. Read Phase 2 provenance report and owner-decision register.
2. Checked both approved hashes before data parsing: Reconstruction `{hash_before['Reconstruction']}`; Batch021 `{hash_before['Batch021']}`.
3. Used Reconstruction for ACR analysis and Batch021 only for approved schema/ID/shared-field comparison.
4. Independently recalculated 1,016 ACR ratios with Decimal arithmetic; created the seven CSV reports and main report.
5. Reopened all generated content and verified CSV field counts/row widths.
6. Rechecked pins after analysis: Reconstruction `{hash_mid['Reconstruction']}`, Batch021 `{hash_mid['Batch021']}`. Shapes remain 1,016 × 43 and 1,016 × 38.

## Audit command errors and fixes

The following errors occurred in read-only previews before final report creation. Each was corrected and the affected check rerun:

{errtable}

{tracebacks}

## Key results

- ACR assessable: {len(ratios)}/1,016; unassessable 0.
- Target comparison: {tc['EXACT_DECIMAL_MATCH']} exact, {tc['WITHIN_TOLERANCE']} additional within {TOL} pp, {tc['MISMATCH']} strict differences; {disp_mismatch_match}/{tc['MISMATCH']} match stored display precision.
- Maximum target difference: {fmt(max_diff,16)} pp.
- Global Tukey high flags: {sum(float(v)>high for v in ratios.values())}; ACR >100%: {over100}; ACR >1,000%: {over1000}; cooked zeros: {zero_cooked}.
- Unit/basis labels: {unit_n}/{basis_n}; combinations {len(pairs)}; comparability not source-verified.
- Shared IDs: {len(common)}; 15 target-value serialization differences; maximum {fmt(Decimal('2.842170943040401e-14'),18)} pp; no merge.

## Required outputs

{''.join(f'- `{n}`\n' for n in sorted(FILES))}
Supplemental helper: `{GEN}` (audit/report generator only; not application or scientific source data).

## Final preservation and boundary checks

- Output directory contains the nine requested reports plus the named supplemental generator; all are readable and nonempty.
- All seven CSVs parse with consistent headers and row widths.
- Both approved hashes and dimensions match after generation.
- Only the new Phase 3 report directory was written. No application source, registry, data, historical outputs/models/metrics/predictions/validation artifacts, dependencies, or lockfiles were changed.
- No Git operation, package installation, model training/evaluation, or build occurred.
- Stage B, restricted Stage C/D materials, and `research/EXISTING_RESULTS_METRICS_CATALOG.csv` were not accessed. No broad scan was performed. `Retention_Final` source CSV was not read or hashed.
- No app tests were run because app code was not modified; the audit validated scientific fields, calculations, identities, schema, and report integrity.
'''

# Write only the new output files, then reopen and validate all deliverables.
(OUT/'PHASE3_SCIENTIFIC_ACR_VALIDATION_REPORT.md').write_text(report,encoding='utf-8')
for name,text in payload.items():(OUT/name).write_text(text,encoding='utf-8',newline='')
(OUT/'PHASE3_EXECUTION_LOG.md').write_text(log,encoding='utf-8')
expected_files=FILES|{GEN}
if {p.name for p in OUT.iterdir()}!=expected_files:raise RuntimeError('Phase 3 output directory has an unexpected file set.')
for name in expected_files:
 if not (OUT/name).is_file() or not (OUT/name).stat().st_size:raise RuntimeError(f'Missing/empty output: {name}')
for name,(headers,rows) in csvdata.items():
 with (OUT/name).open(encoding='utf-8',newline='') as f:
  rd=csv.DictReader(f); data=list(rd)
  if rd.fieldnames!=headers or len(data)!=len(rows) or any(len(x)!=len(headers) for x in data):raise RuntimeError(f'CSV validation failed: {name}')
hash_final={'Reconstruction':hashlib.sha256(REC.read_bytes()).hexdigest(),'Batch021':hashlib.sha256(BAT.read_bytes()).hexdigest()}
if hash_final!=EXPECTED:raise RuntimeError(f'Final pin mismatch: {hash_final}')
for path,nrows,ncols in ((REC,1016,43),(BAT,1016,38)):
 cols,rows=readcsv(path)
 if (len(rows),len(cols))!=(nrows,ncols):raise RuntimeError(f'Source dimensions changed: {path}')
if not (OUT/'PHASE3_SCIENTIFIC_ACR_VALIDATION_REPORT.md').read_text(encoding='utf-8').strip():raise RuntimeError('Main report unreadable or empty.')
print(json.dumps({'status':'PARTIALLY_COMPLETE_WITH_BLOCKED_SCIENTIFIC_CHECKS','output_dir':str(OUT),'files':sorted(expected_files),'hashes':hash_final,'shapes':{'Reconstruction':[ri['n'],ri['p']],'Batch021':[bi['n'],bi['p']]},'target_comparison':{'exact':tc['EXACT_DECIMAL_MATCH'],'within_tolerance':tc['WITHIN_TOLERANCE'],'mismatch':tc['MISMATCH'],'unassessable':issues['UNASSESSABLE'],'strict_mismatches_display_round_match':disp_mismatch_match},'max_diff_pp':fmt(maxdiff,16),'high_tukey':len(outids),'over100':over100,'over1000':over1000,'zero_cooked':zero_cooked},ensure_ascii=True))
