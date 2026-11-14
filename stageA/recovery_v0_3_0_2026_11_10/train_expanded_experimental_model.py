from __future__ import annotations
import hashlib,json,math,sys,platform
from pathlib import Path
import joblib,numpy as np,pandas as pd,sklearn
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import ExtraTreesRegressor,RandomForestRegressor,GradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error,mean_squared_error,r2_score
from sklearn.model_selection import GroupKFold,LeaveOneGroupOut
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from sklearn.svm import SVR
ROOT=Path(__file__).resolve().parent; DATA=ROOT/'expanded_clean_stageA_dataset.csv'; PACKAGE=ROOT/'model_package'
NUM=['Temperature_C','Cooking_Time_min','RDKit_Molecular_Weight','RDKit_LogP','RDKit_TPSA','RDKit_HBond_Donors','RDKit_HBond_Acceptors','RDKit_Rotatable_Bonds','RDKit_Aromatic_Rings','RDKit_Hydroxyl_Groups'];CAT=['compound_class','food_matrix','cooking_method_normalized','cooking_medium']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def make(m):return Pipeline([('pre',ColumnTransformer([('n',Pipeline([('i',SimpleImputer(strategy='median')),('s',StandardScaler())]),NUM),('c',Pipeline([('i',SimpleImputer(strategy='most_frequent')),('o',OneHotEncoder(handle_unknown='ignore',sparse_output=False))]),CAT)])),('m',m)])
def score(y,p):return {'r2':float(r2_score(y,p)),'mae':float(mean_absolute_error(y,p)),'rmse':float(math.sqrt(mean_squared_error(y,p)))}
def evaluate(est,x,y,groups,kind):
 splits=LeaveOneGroupOut().split(x,y,groups) if kind=='source_loso' else GroupKFold(n_splits=5).split(x,y,groups);pred=np.full(len(y),np.nan);fold=[]
 for f,(tr,va) in enumerate(splits,1):
  p=make(est);p.fit(x.iloc[tr],y[tr]);pred[va]=p.predict(x.iloc[va]);fold.append({'fold':f,'validation_group':';'.join(sorted(set(groups[va]))),**score(y[va],pred[va])})
 return pred,score(y,pred),fold
def main():
 df=pd.read_csv(DATA);x=df[NUM+CAT];y=df.target_value_percent.astype(float).to_numpy();cg=df.canonical_molecular_id.astype(str).to_numpy();sg=df.doi.astype(str).to_numpy()
 models={'dummy_median':DummyRegressor(strategy='median'),'ridge':Ridge(alpha=10),'random_forest':RandomForestRegressor(n_estimators=400,min_samples_leaf=2,random_state=42,n_jobs=1),'extra_trees':ExtraTreesRegressor(n_estimators=400,min_samples_leaf=2,random_state=42,n_jobs=1),'gradient_boosting':GradientBoostingRegressor(n_estimators=150,min_samples_leaf=3,learning_rate=.03,random_state=42),'svr_rbf':SVR(C=10,epsilon=.1)}
 try:
  from xgboost import XGBRegressor;models['xgboost']=XGBRegressor(n_estimators=200,max_depth=3,learning_rate=.03,subsample=.8,colsample_bytree=.8,reg_lambda=5,random_state=42,n_jobs=1)
 except ImportError:pass
 rows=[];oof=[];fold_rows=[]
 for name,m in models.items():
  p,s,f=evaluate(m,x,y,cg,'compound');rows.append({'model':name,'validation':'compound_grouped_5fold',**s});fold_rows.extend({'model':name,'validation':'compound_grouped_5fold',**q} for q in f);oof.extend({'observation_id':df.iloc[i].observation_id,'model':name,'actual_percent':y[i],'predicted_percent':p[i],'compound_group':cg[i],'source_doi':sg[i]} for i in range(len(df)))
  _,ss,sf=evaluate(m,x,y,sg,'source_loso');rows.append({'model':name,'validation':'leave_one_source_out',**ss});fold_rows.extend({'model':name,'validation':'leave_one_source_out',**q} for q in sf)
 result=pd.DataFrame(rows);result.to_csv(ROOT/'model_comparison.csv',index=False);pd.DataFrame(fold_rows).to_csv(ROOT/'fold_results.csv',index=False);pd.DataFrame(oof).to_csv(ROOT/'oof_predictions.csv',index=False);best=result[result.validation=='compound_grouped_5fold'].sort_values(['mae','rmse']).iloc[0].model;final=make(models[best]);final.fit(x,y);PACKAGE.mkdir(exist_ok=True);artifact=PACKAGE/'experimental_apparent_concentration_ratio_model.joblib';joblib.dump(final,artifact)
 man={'status':'EXPERIMENTAL_NOT_DEPLOYABLE','selected_model':best,'selection_metric':'compound-grouped OOF MAE','target':'apparent concentration ratio, not total-mass retention','dataset_rows':len(df),'compound_groups':len(set(cg)),'source_families':len(set(sg)),'dataset_sha256':sha(DATA),'artifact_sha256':sha(artifact),'features':{'numeric':NUM,'categorical':CAT},'validation_limit':'LOSO source result is exploratory; each source is also a distinct matrix/compound family. No Stage C integration authorized.','software':{'python':sys.version,'platform':platform.platform(),'sklearn':sklearn.__version__},'stage_c_integration_authorized':False};(PACKAGE/'model_manifest.json').write_text(json.dumps(man,indent=2)+'\n');(PACKAGE/'DO_NOT_DEPLOY.md').write_text('Experimental apparent-concentration-ratio model. Never treat output as total-mass retention or a Stage C exposure multiplier.\n')
 table='| model | validation | r2 | mae | rmse |\n|---|---|---:|---:|---:|\n'+'\n'.join(f"| {r.model} | {r.validation} | {r.r2:.4f} | {r.mae:.4f} | {r.rmse:.4f} |" for _,r in result.iterrows());(ROOT/'stageA_model_comparison.md').write_text('# v0.3 experimental model comparison\n\n'+table+'\n\nCompound-group validation assesses unseen compounds only. Source LOSO is reported as a stress test, not a generalisation claim.\n')
 (ROOT/'stageC_readiness_report.md').write_text('# Stage C readiness\n\nBLOCKED. The v0.3 target remains a concentration ratio and has no validated mass/yield conversion. Existing fail-closed Stage C code was preserved.\n')
 (ROOT/'FINAL_STATUS.md').write_text(f'# v0.3 final status\n\n- Expanded verified dataset: {len(df)} observations from {len(set(sg))} source DOI families.\n- Best compound-grouped experimental model: {best}.\n- Target: apparent concentration ratio only.\n- Deployment and Stage C prediction integration: BLOCKED.\n')
 files=[p for p in ROOT.rglob('*') if p.is_file() and p.name!='SHA256SUMS.txt' and '__pycache__' not in p.parts];(ROOT/'SHA256SUMS.txt').write_text(''.join(f'{sha(p)}  {p.relative_to(ROOT)}\n' for p in sorted(files)))
if __name__=='__main__':main()
