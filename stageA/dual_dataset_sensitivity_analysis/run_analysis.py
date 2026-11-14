from pathlib import Path
import pandas as pd,numpy as np
from sklearn.model_selection import GroupKFold
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score,mean_absolute_error,mean_squared_error
from xgboost import XGBRegressor
R=Path(r'C:\Users\kamra\Desktop\BTP\CookChem\stageA');O=Path(__file__).parent
old=pd.read_csv(R/'input/cookchem_molecular_retention_preprocessed.csv');l=pd.read_csv(R/'recovery_v0_1_0_2026_11_10/source_to_target_ledger.csv');n=pd.read_csv(R/'dataset_expansion_1000/batch_021/updated_master_dataset.csv');keys=set(n.original_record_id.dropna().astype(str)); nidx=n.dropna(subset=['original_record_id']).set_index('original_record_id')
def cl(r):
 if str(r.record_id) in keys:return 'primary_source_verified'
 if r.evidence_status=='DOI_MISMATCH':return 'arithmetic_consistent_source_conflict'
 if r.evidence_status=='TARGET_FORMULA_UNRESOLVED':return 'arithmetic_consistent_pairing_ambiguous'
 return 'arithmetic_consistent_source_metadata_missing'
a=l[l.retention_final_matches_stored_ratio].copy();a['evidence_classification']=a.apply(cl,axis=1);d=old.merge(a[['record_id','evidence_classification','calculated_concentration_ratio_percent']],left_on='Record_ID',right_on='record_id',how='inner');d['target']=d.calculated_concentration_ratio_percent.astype(float)
tiers={'strict_338':['primary_source_verified'],'extended_948':['primary_source_verified','arithmetic_consistent_source_metadata_missing'],'exploratory_989':list(a.evidence_classification.unique())}; datasets={k:d[d.evidence_classification.isin(v)].copy() for k,v in tiers.items()}
for k,x in datasets.items(): x.to_csv(O/f'{k}.csv',index=False)
num=['Temperature_C','Cooking_Time_min','Pressure_kPa','Microwave_Power_W','Sample_Weight_g','Initial_Concentration','Replicates_n','RDKit_Molecular_Weight','RDKit_LogP','RDKit_TPSA','RDKit_HBond_Donors','RDKit_HBond_Acceptors','RDKit_Rotatable_Bonds','RDKit_Aromatic_Rings','RDKit_Hydroxyl_Groups','RDKit_Heavy_Atom_Count'];cat=['Assay_Method_Standardized','Compound_Class_Standardized','Cooking_Medium_Standardized','Cooking_Method_Standardized','Food_Name_Standardized','Initial_Unit_Standardized','Oil_Type_Standardized']
def feat(q):
 x=q[num+cat].copy()
 for c in num:x[c]=pd.to_numeric(x[c],errors='coerce')
 x['temperature_time_interaction']=x.Temperature_C*x.Cooking_Time_min;x['log_cooking_time']=np.log1p(x.Cooking_Time_min.clip(lower=0));x['log_initial_concentration']=np.log1p(x.Initial_Concentration.clip(lower=0));x['logp_temperature_interaction']=x.RDKit_LogP*x.Temperature_C;x['tpsa_time_interaction']=x.RDKit_TPSA*x.Cooking_Time_min
 return x
def ev(q,group,tier,design):
 x=feat(q);y=q.target;g=q[group].astype(str);ns=list(x.select_dtypes(include=np.number));cs=[c for c in x if c not in ns]; pre=ColumnTransformer([('n',Pipeline([('i',SimpleImputer(strategy='median')),('s',StandardScaler())]),ns),('c',Pipeline([('i',SimpleImputer(strategy='constant',fill_value='Missing')),('o',OneHotEncoder(handle_unknown='ignore',sparse_output=False))]),cs)]); fm=[];pp=[]
 for f,(tr,te) in enumerate(GroupKFold(5).split(x,y,g),1):
  m=Pipeline([('p',pre),('x',XGBRegressor(n_estimators=450,max_depth=3,learning_rate=.03,min_child_weight=3,subsample=.8,colsample_bytree=.8,reg_lambda=5,random_state=42,objective='reg:squarederror',n_jobs=1,tree_method='hist',verbosity=0))]);m.fit(x.iloc[tr],np.log1p(y.iloc[tr]));z=np.expm1(np.clip(m.predict(x.iloc[te]),-20,20));td=set(q.iloc[te].DOI);trd=set(q.iloc[tr].DOI);fm.append(dict(tier=tier,design=design,fold=f,n_train=len(tr),n_test=len(te),train_groups=g.iloc[tr].nunique(),test_groups=g.iloc[te].nunique(),molecular_overlap=len(set(q.iloc[tr].Canonical_Molecular_ID)&set(q.iloc[te].Canonical_Molecular_ID)),doi_overlap=len(td&trd),r2=r2_score(y.iloc[te],z),mae=mean_absolute_error(y.iloc[te],z),rmse=mean_squared_error(y.iloc[te],z)**.5,test_target_mean=y.iloc[te].mean(),test_target_sd=y.iloc[te].std()))
  pp += [dict(tier=tier,design=design,fold=f,Record_ID=q.iloc[i].Record_ID,doi=q.iloc[i].DOI,molecular_id=q.iloc[i].Canonical_Molecular_ID,evidence=q.iloc[i].evidence_classification,actual=float(v),predicted=float(w)) for i,v,w in zip(te,y.iloc[te],z)]
 p=pd.DataFrame(pp);fm.append(dict(tier=tier,design=design,fold='pooled',n_train=np.nan,n_test=len(q),train_groups=np.nan,test_groups=g.nunique(),molecular_overlap=0,doi_overlap=np.nan,r2=r2_score(p.actual,p.predicted),mae=mean_absolute_error(p.actual,p.predicted),rmse=mean_squared_error(p.actual,p.predicted)**.5,test_target_mean=y.mean(),test_target_sd=y.std()));return pd.DataFrame(fm),p
allm=[];allp=[];ints=[]
for k,q in datasets.items():
 ints.append(dict(tier=k,rows=len(q),molecular_ids=q.Canonical_Molecular_ID.nunique(),doi_groups=q.DOI.nunique(),compounds=q.Compound_Name.nunique(),missing_doi=q.DOI.isna().sum(),missing_target=q.target.isna().sum(),duplicate_record_ids=q.Record_ID.duplicated().sum(),**{f'count_{z}':(q.evidence_classification==z).sum() for z in a.evidence_classification.unique()}))
 m,p=ev(q,'Canonical_Molecular_ID',k,'molecular_grouped');allm.append(m);allp.append(p); elig=q[q.DOI.notna() & (q.DOI.astype(str).str.len()>0) & (q.evidence_classification!='arithmetic_consistent_source_conflict')].copy()
 m,p=ev(elig,'DOI',k,'source_held_out');m['eligible_rows']=len(elig);m['excluded_unreliable_source']=len(q)-len(elig);allm.append(m);allp.append(p)
pd.DataFrame(ints).to_csv(O/'dataset_integrity_report.csv',index=False);M=pd.concat(allm);P=pd.concat(allp);M[M.design=='molecular_grouped'].to_csv(O/'molecular_grouped_fold_metrics.csv',index=False);M[M.design=='source_held_out'].to_csv(O/'source_heldout_fold_metrics.csv',index=False);P.to_csv(O/'predictions_oof.csv',index=False)
summ=M[M.fold=='pooled'].copy();summ['mean_fold_r2']=[M[(M.tier==r.tier)&(M.design==r.design)&(M.fold!='pooled')].r2.mean() for _,r in summ.iterrows()];summ['sd_fold_r2']=[M[(M.tier==r.tier)&(M.design==r.design)&(M.fold!='pooled')].r2.std() for _,r in summ.iterrows()];summ.to_csv(O/'summary_metrics.csv',index=False)
common=set(datasets['strict_338'].Record_ID); checks=[]
for k in ['extended_948','exploratory_989']:
 q=datasets[k][datasets[k].Record_ID.isin(common)].set_index('Record_ID');s=datasets['strict_338'].set_index('Record_ID');checks.append(dict(comparison=k,ids_identical=set(q.index)==set(s.index),targets_identical=np.allclose(q.target.sort_index(),s.target.sort_index()),features_identical=q[old.columns].sort_index().equals(s[old.columns].sort_index()),molecular_ids_identical=(q.Canonical_Molecular_ID.sort_index()==s.Canonical_Molecular_ID.sort_index()).all(),note='Predictions may differ because outer training sets differ.'))
pd.DataFrame(checks).to_csv(O/'common_338_reproducibility.csv',index=False)
report='# Final comparison report\n\nExact fixed historical XGBoost configuration and fold-local preprocessing were used. Target is apparent concentration ratio, not total-mass retention.\n\n'+summ[['tier','design','n_test','test_groups','mean_fold_r2','sd_fold_r2','r2','mae','rmse']].to_markdown(index=False)+'\n\nStrict records are primary-source verified. Extended and exploratory tiers are not fully verified. Source-held-out rows exclude source-conflict records; missing-source metadata records retain their stored DOI only for grouping and remain weaker evidence. Molecular-grouped DOI overlap is recorded per fold.\n';(O/'FINAL_COMPARISON_REPORT.md').write_text(report);(O/'README.md').write_text('Run python stageA/dual_dataset_sensitivity_analysis/run_analysis.py from project root. Outputs are isolated here.\n')
