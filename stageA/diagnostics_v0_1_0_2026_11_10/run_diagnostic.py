"""Forensic, non-deployment comparison of historical and recovered Stage A data."""
from __future__ import annotations
import csv, hashlib, json, math
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold, KFold, LeaveOneGroupOut
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent; FIG=OUT/'figures'; FIG.mkdir(exist_ok=True)
NUM=['temperature_c','time_min','mw','logp','tpsa','hbd','hba','rot','aromatic','hydroxyl']
CAT=['compound_class','food','method','medium']
INPUTS={
 'historical_1124':ROOT/'stageA/input/cookchem_molecular_retention_preprocessed.csv',
 'v02_verified_117':ROOT/'stageA/recovery_v0_2_0_2026_11_10/clean_stageA_dataset.csv',
 'v03_verified_338':ROOT/'stageA/recovery_v0_3_0_2026_11_10/expanded_clean_stageA_dataset.csv',
}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def metric(y,p): return {'r2':float(r2_score(y,p)),'mae':float(mean_absolute_error(y,p)),'rmse':float(math.sqrt(mean_squared_error(y,p)))}
def pipe():
 return Pipeline([('pre',ColumnTransformer([('n',Pipeline([('i',SimpleImputer(strategy='median')),('s',StandardScaler())]),NUM),('c',Pipeline([('i',SimpleImputer(strategy='most_frequent')),('o',OneHotEncoder(handle_unknown='ignore',sparse_output=False))]),CAT)])),('m',ExtraTreesRegressor(n_estimators=20,min_samples_leaf=2,random_state=42,n_jobs=1))])
def normalized(name,path):
 d=pd.read_csv(path)
 if name=='historical_1124':
  out=pd.DataFrame({'id':d.Record_ID,'source':d.Source_Paper_Key.fillna(d.DOI).astype(str),'compound':d.Canonical_Molecular_ID.astype(str),'target':pd.to_numeric(d.Retention_Final),'temperature_c':pd.to_numeric(d.Temperature_C),'time_min':pd.to_numeric(d.Cooking_Time_min),'mw':pd.to_numeric(d.RDKit_Molecular_Weight),'logp':pd.to_numeric(d.RDKit_LogP),'tpsa':pd.to_numeric(d.RDKit_TPSA),'hbd':pd.to_numeric(d.RDKit_HBond_Donors),'hba':pd.to_numeric(d.RDKit_HBond_Acceptors),'rot':pd.to_numeric(d.RDKit_Rotatable_Bonds),'aromatic':pd.to_numeric(d.RDKit_Aromatic_Rings),'hydroxyl':pd.to_numeric(d.RDKit_Hydroxyl_Groups),'compound_class':d.Compound_Class_Standardized,'food':d.Food_Name_Standardized,'method':d.Cooking_Method_Standardized,'medium':d.Cooking_Medium_Standardized})
 else:
  out=pd.DataFrame({'id':d.iloc[:,0] if 'observation_id' in d else d.record_id,'source':d.doi.astype(str),'compound':d.canonical_molecular_id.astype(str),'target':pd.to_numeric(d.target_value_percent),'temperature_c':pd.to_numeric(d.Temperature_C),'time_min':pd.to_numeric(d.Cooking_Time_min),'mw':pd.to_numeric(d.RDKit_Molecular_Weight),'logp':pd.to_numeric(d.RDKit_LogP),'tpsa':pd.to_numeric(d.RDKit_TPSA),'hbd':pd.to_numeric(d.RDKit_HBond_Donors),'hba':pd.to_numeric(d.RDKit_HBond_Acceptors),'rot':pd.to_numeric(d.RDKit_Rotatable_Bonds),'aromatic':pd.to_numeric(d.RDKit_Aromatic_Rings),'hydroxyl':pd.to_numeric(d.RDKit_Hydroxyl_Groups),'compound_class':d.compound_class,'food':d.food_matrix,'method':d.cooking_method_normalized,'medium':d.cooking_medium})
 for c in CAT: out[c]=out[c].fillna('MISSING').astype(str)
 return out
def components(source,compound):
 parent={}
 def find(x):
  parent.setdefault(x,x)
  if parent[x]!=x:parent[x]=find(parent[x])
  return parent[x]
 def union(a,b):
  a,b=find(a),find(b)
  if a!=b:parent[b]=a
 for s,c in zip(source,compound):union('s:'+s,'c:'+c)
 return np.array([find('s:'+s) for s in source])
def splits(kind,d):
 n=len(d)
 if kind=='random_5fold':return KFold(n_splits=5,shuffle=True,random_state=42).split(d),None
 groups=d.compound.to_numpy() if kind=='compound_grouped_5fold' else d.source.to_numpy() if kind=='source_loso' else components(d.source.to_numpy(),d.compound.to_numpy())
 unique=len(set(groups))
 if kind=='source_loso': return (LeaveOneGroupOut().split(d,d.target,groups) if 2<=unique<=20 else None),groups
 return (GroupKFold(n_splits=min(5,unique)).split(d,d.target,groups) if unique>=2 else None),groups
def evaluate(dataset,kind,log_target=False):
 d=dataset; iterator,groups=splits(kind,d)
 if iterator is None:return [],[],{'status':'INFEASIBLE','dataset':d.name,'validation':kind,'target_transform':'log1p' if log_target else 'none','reason':'source LOSO intentionally not run when more than 20 source families; use source-grouped/component validation instead'}
 x=d[NUM+CAT];y=d.target.to_numpy();pred=np.full(len(d),np.nan);folds=[]
 for f,(tr,va) in enumerate(iterator,1):
  model=pipe(); train_y=np.log1p(y[tr]) if log_target else y[tr];model.fit(x.iloc[tr],train_y);p=model.predict(x.iloc[va]);p=np.expm1(p) if log_target else p;pred[va]=p
  folds.append({'dataset':d.name,'validation':kind,'target_transform':'log1p' if log_target else 'none','fold':f,'train_rows':len(tr),'validation_rows':len(va),'train_compounds':len(set(d.compound.iloc[tr])),'validation_compounds':len(set(d.compound.iloc[va])),'train_sources':len(set(d.source.iloc[tr])),'validation_sources':len(set(d.source.iloc[va])),**metric(y[va],p)})
 summary={'status':'OK','dataset':d.name,'validation':kind,'target_transform':'log1p' if log_target else 'none',**metric(y,pred)}
 oof=[{'dataset':d.name,'validation':kind,'target_transform':summary['target_transform'],'id':d.id.iloc[i],'source':d.source.iloc[i],'compound':d.compound.iloc[i],'food':d.food.iloc[i],'method':d.method.iloc[i],'actual':y[i],'predicted':pred[i],'residual':y[i]-pred[i]} for i in range(len(d))]
 return folds,oof,summary
def main():
 datasets={n:normalized(n,p) for n,p in INPUTS.items()}
 for n,d in datasets.items():d.name=n
 comparison=[];summaries=[];folds=[];oof=[];importance=[]
 for n,d in datasets.items():
  comparison.append({'dataset':n,'rows':len(d),'compounds':d.compound.nunique(),'sources':d.source.nunique(),'foods':d.food.nunique(),'methods':d.method.nunique(),'target_min':d.target.min(),'target_median':d.target.median(),'target_mean':d.target.mean(),'target_sd':d.target.std(),'target_max':d.target.max(),'above_100_fraction':float((d.target>100).mean()),'input_sha256':sha(INPUTS[n])})
  for kind in ['random_5fold','compound_grouped_5fold','source_loso','compound_and_source_components']:
   for transformed in [False,True]:
    f,o,s=evaluate(d,kind,transformed);folds.extend(f);oof.extend(o);summaries.append(s)
  full=pipe();full.fit(d[NUM+CAT],d.target); names=full.named_steps['pre'].get_feature_names_out(); values=full.named_steps['m'].feature_importances_
  importance.extend({'dataset':n,'feature':str(feature),'importance':float(value),'interpretation':'descriptive full-data importance only; not causal or deployment evidence'} for feature,value in zip(names,values))
 pd.DataFrame(comparison).to_csv(OUT/'dataset_comparison.csv',index=False);pd.DataFrame(summaries).to_csv(OUT/'validation_comparison.csv',index=False);pd.DataFrame(folds).to_csv(OUT/'fold_level_metrics.csv',index=False);pd.DataFrame(oof).to_csv(OUT/'oof_predictions.csv',index=False);pd.DataFrame(importance).sort_values(['dataset','importance'],ascending=[True,False]).to_csv(OUT/'feature_importance.csv',index=False)
 # Distribution, source effects, outliers and simple figures.
 out=[]
 for n,d in datasets.items():
  for _,r in d.sort_values('target',ascending=False).head(15).iterrows():out.append({'dataset':n,'id':r.id,'source':r.source,'compound':r.compound,'food':r.food,'method':r.method,'target':r.target,'outlier_reason':'top target value; retained, not automatically erroneous'})
  plt.figure(figsize=(7,4));plt.hist(d.target,bins=30);plt.title(n+' target distribution');plt.xlabel('apparent ratio / stored target');plt.ylabel('rows');plt.tight_layout();plt.savefig(FIG/(n+'_hist.png'),dpi=140);plt.close()
 pd.DataFrame(out).to_csv(OUT/'outlier_analysis.csv',index=False)
 hist=datasets['historical_1124']; htext='''# Original experiment reconstruction\n\n## Verdict: NOT REPRODUCIBLE AND SCIENTIFICALLY NOT COMPARABLE\n\nRepository searches found no serialized Stage A model, fold assignments, run manifest, preprocessing state, or output carrying the claimed `R²≈0.4861`, `RMSE≈41.37`, and `MAE≈20.77` combination. The current tracked Stage A benchmark uses `log1p(Retention_Final)`, grouped folds by `Canonical_Molecular_ID`, and reports different pooled OOF results. The Stage B manifest describes a separate artifact with a Yeo–Johnson target transform and fold-mean R² 0.390691. These cannot establish the claimed 0.4861 run.\n\nThe historical 1,124-row target is `Retention_Final`; it is not scientifically interchangeable with the source-verified apparent-ratio target used by v0.2/v0.3.\n''';(OUT/'original_experiment_reconstruction.md').write_text(htext,encoding='utf-8')
 (OUT/'target_distribution_analysis.md').write_text('# Target distribution analysis\n\nSee `dataset_comparison.csv`, `outlier_analysis.csv`, and `figures/`. Historical target values extend to 3650, while recovered data use verified apparent concentration ratios. Values above 100 are retained because they can represent concentration/basis effects; they are not total-mass retention evidence.\n',encoding='utf-8')
 source_lines=['# Source-family analysis','']
 for n,d in datasets.items():source_lines+=['## '+n,d.groupby('source').target.agg(['count','mean','median','min','max']).to_csv()]
 (OUT/'source_family_analysis.md').write_text('\n'.join(source_lines),encoding='utf-8')
 top=pd.DataFrame(importance).sort_values(['dataset','importance'],ascending=[True,False]).groupby('dataset').head(8)
 (OUT/'feature_diagnostic.md').write_text('# Feature diagnostic\n\nCommon diagnostic features are molecular descriptors, temperature, duration, food, method, medium, and compound class. `Apparent_Increase`, final concentration, reported retention, and source ID are excluded. Food and method may nevertheless proxy source because recovered families are tightly coupled to their matrices/protocols. Missing process fields are imputed within folds; their high missingness limits prediction-time utility.\n\n## Descriptive full-data feature importance\n\n'+top.to_csv(index=False)+'\nImportance is not evidence of causal or cross-source predictive value.\n',encoding='utf-8')
 (OUT/'model_error_analysis.md').write_text('# Model error analysis\n\nUse `oof_predictions.csv` by dataset, validation strategy, source, compound, food, and method. Random CV estimates within-source interpolation. Compound grouping is stricter. Source LOSO and connected compound/source components test transfer across evidence families; their results should control deployment decisions.\n',encoding='utf-8')
 (OUT/'reproducibility_report.md').write_text('# Reproducibility\n\nRun `python stageA/diagnostics_v0_1_0_2026_11_10/run_diagnostic.py`. It reads existing inputs only and writes only this directory. No model artifact is deployed or replaced.\n',encoding='utf-8')
 (OUT/'FINAL_STAGE_A_DECISION.md').write_text('# Final Stage A decision\n\n## Direction: D — pause deployment modelling and acquire independent experimental evidence\n\nKeep the historical model only as a non-comparable benchmark. Continue source-verified apparent-ratio work for research, but do not package it for Stage C until multiple independent source/matrix families support source-held-out performance and a mass/yield-compatible target is established.\n',encoding='utf-8')
 files=[p for p in OUT.rglob('*') if p.is_file() and p.name!='SHA256SUMS.txt'];(OUT/'SHA256SUMS.txt').write_text(''.join(f'{sha(p)}  {p.relative_to(OUT)}\n' for p in sorted(files)))
if __name__=='__main__':main()
