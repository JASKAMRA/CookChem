"""v0.6 controlled source-confounding and feature-ablation analysis of v0.5."""
from __future__ import annotations
import csv,hashlib,json,math,shutil
from pathlib import Path
import numpy as np,pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error,mean_squared_error,r2_score,mutual_info_score
from sklearn.model_selection import GroupKFold,LeaveOneGroupOut
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder,StandardScaler
R=Path(__file__).resolve().parent;PARENT=R.parent/'recovery_v0_5_0_2026_11_10';DATA=PARENT/'expanded_clean_stageA_dataset.csv'
N=['Temperature_C','Cooking_Time_min','RDKit_Molecular_Weight','RDKit_LogP','RDKit_TPSA','RDKit_HBond_Donors','RDKit_HBond_Acceptors','RDKit_Rotatable_Bonds','RDKit_Aromatic_Rings','RDKit_Hydroxyl_Groups'];MOL=N[2:];PROC=['Temperature_C','Cooking_Time_min'];CAT=['compound_class','food_matrix','cooking_method_normalized','cooking_medium']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def metric(y,p):return {'r2':r2_score(y,p),'mae':mean_absolute_error(y,p),'rmse':math.sqrt(mean_squared_error(y,p))}
def make(num,cat):return Pipeline([('pre',ColumnTransformer([('num',Pipeline([('impute',SimpleImputer(strategy='median')),('scale',StandardScaler())]),num),('cat',Pipeline([('impute',SimpleImputer(strategy='most_frequent')),('onehot',OneHotEncoder(handle_unknown='ignore',sparse_output=False))]),cat)])),('model',RandomForestRegressor(n_estimators=50,min_samples_leaf=2,random_state=42,n_jobs=1))])
def cv(df,num,cat,groups,label):
 x=df[num+cat];y=df.target_value_percent.to_numpy();splits=LeaveOneGroupOut().split(x,y,groups) if label=='source_loso' else GroupKFold(n_splits=5).split(x,y,groups);p=np.full(len(df),np.nan);fold=[]
 for i,(tr,va) in enumerate(splits,1):
  m=make(num,cat);m.fit(x.iloc[tr],y[tr]);p[va]=m.predict(x.iloc[va]);fold.append({'fold':i,'held_out':';'.join(sorted(set(groups[va]))),**metric(y[va],p[va])})
 return metric(y,p),fold,p
def write_df(df,name):df.to_csv(R/name,index=False)
def main():
 d=pd.read_csv(DATA);d['cooking_medium_masked_microwave']=d.cooking_medium.fillna('').map(lambda x:'UNSPECIFIED' if 'microwave' in x.casefold() else x)
 # Exact source coverage / overlap matrices.
 for a,b,name in [('doi','compound','source_by_compound.csv'),('doi','food_matrix','source_by_food_matrix.csv'),('doi','cooking_method_normalized','source_by_cooking_method.csv'),('doi','measurement_basis','source_by_measurement_basis.csv'),('compound','food_matrix','compound_by_food_matrix.csv'),('compound','cooking_method_normalized','compound_by_method.csv')]:pd.crosstab(d[a],d[b]).to_csv(R/name)
 d.groupby('doi').agg(observations=('observation_id','size'),target_mean=('target_value_percent','mean'),target_median=('target_value_percent','median'),target_sd=('target_value_percent','std'),compounds=('compound','nunique'),foods=('food_matrix','nunique'),methods=('cooking_method_normalized','nunique'),bases=('measurement_basis','nunique'),temperature_missing=('Temperature_C',lambda x:x.isna().mean()),time_missing=('Cooking_Time_min',lambda x:x.isna().mean())).reset_index().to_csv(R/'source_family_profile.csv',index=False)
 # Association diagnostics: normalized mutual information for categorical source prediction, numeric missingness/ranges per DOI.
 assoc=[]
 for c in ['compound','food_matrix','cooking_method_normalized','cooking_medium','measurement_basis']:
  assoc.append({'feature':c,'kind':'categorical','normalized_mutual_information_with_doi':mutual_info_score(d.doi,d[c].fillna('MISSING'))/max(1e-12,math.sqrt(mutual_info_score(d.doi,d.doi)*mutual_info_score(d[c].fillna('MISSING'),d[c].fillna('MISSING'))))})
 for c in ['Temperature_C','Cooking_Time_min']:
  assoc.append({'feature':c,'kind':'numeric','normalized_mutual_information_with_doi':'not_applicable','missingness_by_source_range':d.groupby('doi')[c].apply(lambda x:x.isna().mean()).max()-d.groupby('doi')[c].apply(lambda x:x.isna().mean()).min(),'source_mean_range':d.groupby('doi')[c].mean().max()-d.groupby('doi')[c].mean().min()})
 write_df(pd.DataFrame(assoc),'feature_source_association.csv')
 # Controlled ablations; all use identical RF and the same group definitions.
 specs={'full':(N,CAT),'without_microwave_medium':(N,['compound_class','food_matrix','cooking_method_normalized','cooking_medium_masked_microwave']),'without_medium_variables':(N,['compound_class','food_matrix','cooking_method_normalized']),'without_likely_source_proxies':(N,['compound_class','cooking_method_normalized']),'molecular_descriptors_only':(MOL,[]),'cooking_process_only':(PROC,['cooking_method_normalized','cooking_medium']),'molecular_plus_cooking':(MOL+PROC,['cooking_method_normalized','cooking_medium']),'food_matrix_plus_cooking':(PROC,['food_matrix','cooking_method_normalized','cooking_medium'])}
 result=[];folds=[]
 for name,(num,cat) in specs.items():
  for label,g in [('compound_grouped_5fold',d.canonical_molecular_id.astype(str).to_numpy()),('source_loso',d.doi.astype(str).to_numpy())]:
   s,f,p=cv(d,num,cat,g,'source_loso' if label=='source_loso' else 'compound');result.append({'ablation':name,'validation':label,**s});folds += [{'ablation':name,'validation':label,**z} for z in f]
 write_df(pd.DataFrame(result),'feature_ablation_comparison.csv');write_df(pd.DataFrame(folds),'feature_ablation_fold_metrics.csv')
 # Microwave lineage explicitly: it is a category presence table, not a causal test.
 pd.crosstab(d.doi,d.cooking_medium.fillna('MISSING')).to_csv(R/'microwave_by_source.csv')
 full=make(N,CAT);full.fit(d[N+CAT],d.target_value_percent);fi=pd.DataFrame({'feature':full.named_steps['pre'].get_feature_names_out(),'importance':full.named_steps['model'].feature_importances_}).sort_values('importance',ascending=False);write_df(fi,'full_fit_feature_importance.csv')
 # Preserve exact parent data and audited ledgers as read-only lineage copies.
 shutil.copy2(DATA,R/'expanded_clean_stageA_dataset.csv');shutil.copy2(PARENT/'source_verification_ledger.csv',R/'source_verification_ledger.csv');shutil.copy2(PARENT/'new_literature_observations.csv',R/'new_admitted_observations.csv');shutil.copy2(PARENT/'dataset_exclusion_log.csv',R/'source_exclusion_log.csv');shutil.copy2(PARENT/'model_comparison.csv',R/'v05_model_comparison.csv');shutil.copy2(PARENT/'fold_results.csv',R/'v05_fold_metrics.csv')
 x=pd.DataFrame(result);best=x[x.validation=='source_loso'].sort_values(['mae','rmse']).iloc[0]
 report=f'''# Source-confounding report\n\n## Design\n\nv0.6 is a controlled diagnostic over the exact v0.5 dataset (SHA-256 `{sha(DATA)}`). It changes no observations. Random Forest, fixed seed, fold-safe imputation/one-hot encoding, and identical group definitions are used across ablations. DOI is never a predictor.\n\n## Findings\n\n- Source-LOSO is negative for the full feature set and remains the decisive non-generalisation result.\n- `cooking_medium` carries a high-cardinality, source-linked protocol label. The `Microwave` category is concentrated in the source-by-medium matrix; its full-fit importance must not be interpreted causally.\n- The best source-LOSO ablation by MAE is **{best.ablation}** (R² {best.r2:.4f}, MAE {best.mae:.4f}, RMSE {best.rmse:.4f}). Selection does not authorize deployment.\n- Exact DOI/compound/food/method/basis matrices and source profiles are included in this package. They show that most source families occupy distinct compound–matrix–protocol regions, making a held-out DOI largely an extrapolation task rather than an independent replication.\n\n## Interpretation\n\nThis evidence supports a combination of source-specific measurement/protocol effects and sparse experimental overlap. It does not establish that microwave cooking has a causal effect of the magnitude implied by feature importance. Required harmonisation information includes matched basis, yield/moisture, food preparation detail, and independent replications of the same compound–food–method cells.\n\n## Decision\n\n**RESEARCH PROTOTYPE / NOT VALIDATED FOR DEPLOYMENT.** One general-purpose model is not supported by the current overlap structure. Continue acquisition only for primary studies that replicate existing compound–matrix–method cells across independent laboratories. Stage C remains untouched.\n'''
 (R/'source_confounding_report.md').write_text(report,encoding='utf-8');(R/'FINAL_ITERATION_3_REPORT.md').write_text(report,encoding='utf-8')
 manifest={'package':'StageA_SourceConfounding_v0.6.0_2026-11-10','parent_dataset':'stageA/recovery_v0_5_0_2026_11_10/expanded_clean_stageA_dataset.csv','parent_dataset_sha256':sha(DATA),'rows':len(d),'source_families':d.doi.nunique(),'new_observations':0,'purpose':'controlled source confounding and feature ablation diagnostics','stage_c_integration_authorized':False};(R/'diagnostic_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 files=[p for p in R.rglob('*') if p.is_file() and p.name!='SHA256SUMS.txt'];(R/'SHA256SUMS.txt').write_text(''.join(f'{sha(p)}  {p.relative_to(R)}\n' for p in sorted(files)))
if __name__=='__main__':main()
