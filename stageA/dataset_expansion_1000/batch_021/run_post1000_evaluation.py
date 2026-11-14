"""Post-1,000 compatibility, diversity, leakage and fold-safe evaluation."""
from pathlib import Path
import hashlib, json, math
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor, GradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold, LeaveOneGroupOut
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVR

R=Path(__file__).resolve().parent; df=pd.read_csv(R/'updated_master_dataset.csv')
NUM=['Temperature_C','Cooking_Time_min','RDKit_Molecular_Weight','RDKit_LogP','RDKit_TPSA','RDKit_HBond_Donors','RDKit_HBond_Acceptors','RDKit_Rotatable_Bonds','RDKit_Aromatic_Rings','RDKit_Hydroxyl_Groups']
CAT=['compound_class','food_matrix','cooking_method_normalized','cooking_medium']; X=df[NUM+CAT]; y=df.target_value_percent.to_numpy()
def metric(a,b): return {'r2':float(r2_score(a,b)),'mae':float(mean_absolute_error(a,b)),'rmse':float(math.sqrt(mean_squared_error(a,b)))}
def pipe(model): return Pipeline([('pre',ColumnTransformer([('n',Pipeline([('i',SimpleImputer(strategy='median')),('s',StandardScaler())]),NUM),('c',Pipeline([('i',SimpleImputer(strategy='most_frequent')),('o',OneHotEncoder(handle_unknown='ignore',sparse_output=False))]),CAT)])),('m',model)])
def cv(model, group, label, loso=False):
 splitter=LeaveOneGroupOut() if loso else GroupKFold(n_splits=min(5,len(set(group)))); pred=np.full(len(y),np.nan); out=[]
 for n,(tr,va) in enumerate(splitter.split(X,y,group),1):
  z=pipe(model); z.fit(X.iloc[tr],y[tr]); pred[va]=z.predict(X.iloc[va]); out.append({'validation':label,'fold':n,'held_out':';'.join(sorted(set(group[va]))),'n_valid':len(va),**metric(y[va],pred[va])})
 return pred,metric(y,pred),out
key=['doi','compound','food_matrix','cooking_method_normalized','Cooking_Time_min','raw_concentration','cooked_concentration']
new=df[df.doi.eq('10.3390/foods9050607')].copy(); delta=(df.target_value_percent-100*df.cooked_concentration/df.raw_concentration).abs()
compat={'rows':int(len(df)),'doi_families':int(df.doi.nunique()),'compounds':int(df.compound.nunique()),'food_matrices':int(df.food_matrix.nunique()),'methods':int(df.cooking_method_normalized.nunique()),'missing_doi':int(df.doi.isna().sum()),'preserved_legacy_zero_cooked_rows':int(((df.raw_concentration>0)&(df.cooked_concentration<=0)).sum()),'target_formula_deviations_over_0_01pp':int((delta>0.01).sum()),'max_target_rounding_deviation_pp':float(delta.max()),'duplicate_experiment_keys':int(df.duplicated(key).sum()),'aggregate_or_assay_named_rows':int(df.compound.astype(str).str.contains('total|activity|phenolic content|antioxidant',case=False,regex=True).sum()),'new_batch_rows':int(len(new)),'new_batch_nonpositive_raw_or_cooked':int(((new.raw_concentration<=0)|(new.cooked_concentration<=0)).sum()),'new_batch_formula_mismatches':int((~np.isclose(new.target_value_percent,100*new.cooked_concentration/new.raw_concentration,rtol=0,atol=1e-8)).sum()),'new_batch_duplicate_experiment_keys':int(new.duplicated(key).sum())}
assert compat['rows']>=1000 and compat['target_formula_deviations_over_0_01pp']==0 and compat['duplicate_experiment_keys']==0 and compat['aggregate_or_assay_named_rows']==0 and compat['new_batch_rows']==78 and compat['new_batch_nonpositive_raw_or_cooked']==0 and compat['new_batch_formula_mismatches']==0 and compat['new_batch_duplicate_experiment_keys']==0
for c,n in [('doi','observations_per_doi.csv'),('compound','observations_per_compound.csv'),('food_matrix','observations_per_food_matrix.csv'),('cooking_method_normalized','observations_per_cooking_method.csv'),('measurement_basis','observations_per_measurement_basis.csv')]: df.groupby(c).size().reset_index(name='observations').sort_values('observations',ascending=False).to_csv(R/n,index=False)
pd.crosstab(df.compound,df.food_matrix).to_csv(R/'compound_by_food_matrix.csv'); pd.crosstab(df.doi,df.food_matrix).to_csv(R/'source_by_food_matrix.csv'); pd.crosstab(df.doi,df.cooking_method_normalized).to_csv(R/'source_by_cooking_method.csv')
repkey=['compound','food_matrix','cooking_method_normalized','Cooking_Time_min','measurement_basis']; rep=df.groupby(repkey,dropna=False).agg(observations=('observation_id','size'),source_families=('doi','nunique'),dois=('doi',lambda x:';'.join(sorted(set(x))))).reset_index(); rep[rep.source_families>1].sort_values(['source_families','observations'],ascending=False).to_csv(R/'strict_cross_source_replication_cells.csv',index=False)
models={'dummy_median':DummyRegressor(strategy='median'),'ridge':Ridge(alpha=10),'random_forest':RandomForestRegressor(n_estimators=75,min_samples_leaf=2,random_state=42,n_jobs=1),'extra_trees':ExtraTreesRegressor(n_estimators=75,min_samples_leaf=2,random_state=42,n_jobs=1),'gradient_boosting':GradientBoostingRegressor(n_estimators=75,min_samples_leaf=3,learning_rate=.03,random_state=42),'svr_rbf':SVR(C=10,epsilon=.1)}
try:
 from xgboost import XGBRegressor; models['xgboost']=XGBRegressor(n_estimators=75,max_depth=4,learning_rate=.03,subsample=.8,colsample_bytree=.8,random_state=42,n_jobs=1,objective='reg:squarederror')
except Exception: pass
groups={'compound_grouped_5fold':(df.canonical_molecular_id.astype(str).to_numpy(),False),'food_matrix_grouped_5fold':(df.food_matrix.astype(str).to_numpy(),False),'leave_one_source_out':(df.doi.astype(str).to_numpy(),True)}
results=[]; folds=[]; oof=[]
for name,model in models.items():
 for label,(g,loso) in groups.items():
  pred,s,detail=cv(model,g,label,loso); results.append({'model':name,'validation':label,**s}); folds += [{'model':name,**z} for z in detail]
  oof += [{'observation_id':df.iloc[i].observation_id,'model':name,'validation':label,'actual_percent':y[i],'predicted_percent':pred[i],'group':g[i],'source_doi':df.doi.iloc[i]} for i in range(len(df))]
pd.DataFrame(results).to_csv(R/'post1000_model_comparison.csv',index=False); pd.DataFrame(folds).to_csv(R/'post1000_fold_metrics.csv',index=False); pd.DataFrame(oof).to_csv(R/'post1000_oof_predictions.csv',index=False)
sl=[]; g=df.doi.astype(str).to_numpy()
for n,(tr,va) in enumerate(LeaveOneGroupOut().split(X,y,g),1):
 z=pipe(models['extra_trees']); z.fit(X.iloc[tr],y[tr]); p=z.predict(X.iloc[va]); sl.append({'fold':n,'doi':g[va][0],'n_valid':len(va),**metric(y[va],p),'mean_error':float(np.mean(p-y[va]))})
pd.DataFrame(sl).sort_values('mae',ascending=False).to_csv(R/'extra_trees_source_loso_errors.csv',index=False)
full=pipe(models['extra_trees']); full.fit(X,y); imp=pd.DataFrame({'feature':full.named_steps['pre'].get_feature_names_out(),'importance':full.named_steps['m'].feature_importances_}).sort_values('importance',ascending=False); imp.to_csv(R/'extra_trees_feature_importance.csv',index=False); mic=imp[imp.feature.str.contains('microwave',case=False,na=False)]
dom=(df.groupby('doi').size().sort_values(ascending=False).head(10)/len(df)*100).round(2)
report=['# Post-1,000 validation and evaluation','','## Compatibility validation','```json',json.dumps(compat,indent=2),'```','- Two preserved pre-Batch-021 Vitamin-C rows have zero cooked concentration and target 0; they are reported rather than silently removed. The 78 newly admitted rows are all positive and formula-exact.','- Earlier target values are stored rounded; their maximum recomputation difference is reported above and none exceeds 0.01 percentage points.','','## Diversity and dominance',f'- Master: {len(df)} observations; {df.doi.nunique()} DOI families; {df.compound.nunique()} compounds; {df.food_matrix.nunique()} food matrices; {df.cooking_method_normalized.nunique()} normalized methods.',f'- Largest DOI family: {dom.index[0]} ({int(df.groupby("doi").size().max())} rows; {dom.iloc[0]:.2f}%).',f'- Strict cross-source replication cells (same analyte/matrix/method/time/basis): {int((rep.source_families>1).sum())}.','- Count tables and coverage cross-tabs are saved beside this report.','','## Evaluation interpretation','- Source-family LOSO is the primary unseen-source stress test. Results are experimental and do not authorize deployment or Stage C integration.','- Food-matrix and compound grouped results are secondary checks; they do not remove source clustering.','- Microwave transformed-feature importance: '+(', '.join(f"{x.feature}={x.importance:.4f}" for _,x in mic.iterrows()) if len(mic) else 'none')+'. This is descriptive, not causal.','','## Model results',pd.DataFrame(results).to_markdown(index=False,floatfmt='.4f')]
(R/'post1000_validation_and_evaluation.md').write_text('\n'.join(report)+'\n',encoding='utf-8'); (R/'post1000_validation_summary.json').write_text(json.dumps({'compatibility':compat,'models':list(models),'target_reached':True,'stage_c_integration_authorized':False},indent=2)+'\n',encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
(R/'SHA256SUMS.txt').write_text('\n'.join(f'{sha(p)}  {p.name}' for p in sorted(R.iterdir()) if p.is_file() and p.name!='SHA256SUMS.txt')+'\n',encoding='utf-8')
print(json.dumps({'compatibility':compat,'models':list(models),'rows':len(df)},indent=2))
