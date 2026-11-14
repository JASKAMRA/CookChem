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
R=Path(__file__).resolve().parent;D=R/'expanded_clean_stageA_dataset.csv';P=R/'model_package'
NUM=['Temperature_C','Cooking_Time_min','RDKit_Molecular_Weight','RDKit_LogP','RDKit_TPSA','RDKit_HBond_Donors','RDKit_HBond_Acceptors','RDKit_Rotatable_Bonds','RDKit_Aromatic_Rings','RDKit_Hydroxyl_Groups'];CAT=['compound_class','food_matrix','cooking_method_normalized','cooking_medium']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pipe(model):return Pipeline([('pre',ColumnTransformer([('n',Pipeline([('i',SimpleImputer(strategy='median')),('s',StandardScaler())]),NUM),('c',Pipeline([('i',SimpleImputer(strategy='most_frequent')),('o',OneHotEncoder(handle_unknown='ignore',sparse_output=False))]),CAT)])),('m',model)])
def metric(y,p):return {'r2':float(r2_score(y,p)),'mae':float(mean_absolute_error(y,p)),'rmse':float(math.sqrt(mean_squared_error(y,p)))}
def cv(model,x,y,g,loso=False):
 splits=LeaveOneGroupOut().split(x,y,g) if loso else GroupKFold(n_splits=5).split(x,y,g);p=np.full(len(y),np.nan);fold=[]
 for n,(tr,va) in enumerate(splits,1):
  m=pipe(model);m.fit(x.iloc[tr],y[tr]);p[va]=m.predict(x.iloc[va]);fold.append({'fold':n,'validation_group':';'.join(sorted(set(g[va]))),**metric(y[va],p[va])})
 return p,metric(y,p),fold
def main():
 df=pd.read_csv(D);x=df[NUM+CAT];y=df.target_value_percent.to_numpy();cg=df.canonical_molecular_id.astype(str).to_numpy();sg=df.doi.astype(str).to_numpy()
 models={'dummy_median':DummyRegressor(strategy='median'),'ridge':Ridge(alpha=10),'random_forest':RandomForestRegressor(n_estimators=400,min_samples_leaf=2,random_state=42,n_jobs=1),'extra_trees':ExtraTreesRegressor(n_estimators=400,min_samples_leaf=2,random_state=42,n_jobs=1),'gradient_boosting':GradientBoostingRegressor(n_estimators=150,min_samples_leaf=3,learning_rate=.03,random_state=42),'svr_rbf':SVR(C=10,epsilon=.1)}
 results=[];folds=[];oof=[]
 for name,m in models.items():
  pred,s,f=cv(m,x,y,cg);results.append({'model':name,'validation':'compound_grouped_5fold',**s});folds += [{'model':name,'validation':'compound_grouped_5fold',**z} for z in f];oof += [{'observation_id':df.iloc[i].observation_id,'model':name,'actual_percent':y[i],'predicted_percent':pred[i],'compound_group':cg[i],'source_doi':sg[i]} for i in range(len(df))]
  _,s,f=cv(m,x,y,sg,True);results.append({'model':name,'validation':'leave_one_source_out',**s});folds += [{'model':name,'validation':'leave_one_source_out',**z} for z in f]
 res=pd.DataFrame(results);res.to_csv(R/'model_comparison.csv',index=False);pd.DataFrame(folds).to_csv(R/'fold_results.csv',index=False);pd.DataFrame(oof).to_csv(R/'oof_predictions.csv',index=False)
 best=res[res.validation=='compound_grouped_5fold'].sort_values(['mae','rmse']).iloc[0].model;final=pipe(models[best]);final.fit(x,y);P.mkdir(exist_ok=True);a=P/'experimental_apparent_concentration_ratio_model.joblib';joblib.dump(final,a)
 man={'status':'EXPERIMENTAL_NOT_DEPLOYABLE','selected_model':best,'selection_metric':'compound-grouped OOF MAE','target':'apparent concentration ratio, not total-mass retention','dataset_rows':len(df),'compound_groups':len(set(cg)),'source_families':len(set(sg)),'dataset_sha256':sha(D),'artifact_sha256':sha(a),'features':{'numeric':NUM,'categorical':CAT},'stage_c_integration_authorized':False,'software':{'python':sys.version,'platform':platform.platform(),'sklearn':sklearn.__version__}}
 (P/'model_manifest.json').write_text(json.dumps(man,indent=2)+'\n');(P/'DO_NOT_DEPLOY.md').write_text('Experimental apparent-concentration-ratio model. Never treat output as total-mass retention or a Stage C exposure multiplier.\n')
 table='| model | validation | R² | MAE | RMSE |\n|---|---|---:|---:|---:|\n'+'\n'.join(f'| {z.model} | {z.validation} | {z.r2:.4f} | {z.mae:.4f} | {z.rmse:.4f} |' for _,z in res.iterrows())
 (R/'stageA_model_comparison.md').write_text('# v0.4 experimental model comparison\n\n'+table+'\n\nSource LOSO remains a stress test, not a claim of deployment-level unseen-source generalisation.\n')
 (R/'stageC_readiness_report.md').write_text('# Stage C readiness\n\nBLOCKED. This target is an apparent fresh-weight concentration ratio; no validated mass/yield conversion exists. The existing fail-closed Stage C adapter was preserved.\n')
 files=[p for p in R.rglob('*') if p.is_file() and p.name!='SHA256SUMS.txt' and '__pycache__' not in p.parts];(R/'SHA256SUMS.txt').write_text(''.join(f'{sha(p)}  {p.relative_to(R)}\n' for p in sorted(files)))
if __name__=='__main__':main()
