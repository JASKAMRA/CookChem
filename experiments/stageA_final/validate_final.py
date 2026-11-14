from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd
from sklearn.model_selection import GroupKFold
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from sklearn.metrics import r2_score,mean_absolute_error,mean_squared_error
from xgboost import XGBRegressor
P=Path(__file__).resolve().parents[2];O=Path(__file__).parent;D=P/'data/final/stageA_final_dataset.csv';H='ff7d9cb7388b63d8602b1b26bc0530032b32b3816f6128315eb005a3ae2b78d4'
assert hashlib.sha256(D.read_bytes()).hexdigest()==H
d=pd.read_csv(D);assert len(d)==1104 and d.Record_ID.is_unique and d.target.notna().all() and np.allclose(d.target,d.calculated_concentration_ratio_percent)
cats=['Assay_Method_Standardized','Compound_Class_Standardized','Cooking_Medium_Standardized','Cooking_Method_Standardized','Food_Name_Standardized','Initial_Unit_Standardized','Oil_Type_Standardized']
base=['Temperature_C','Cooking_Time_min','Pressure_kPa','Microwave_Power_W','Sample_Weight_g','Initial_Concentration','Replicates_n']+cats+['RDKit_Molecular_Weight','RDKit_LogP','RDKit_TPSA','RDKit_HBond_Donors','RDKit_HBond_Acceptors','RDKit_Rotatable_Bonds','RDKit_Aromatic_Rings','RDKit_Hydroxyl_Groups']
params=dict(objective='reg:squarederror',n_estimators=450,max_depth=3,learning_rate=.03,min_child_weight=3,subsample=.8,colsample_bytree=.8,reg_lambda=5.,random_state=42,n_jobs=1,tree_method='hist',verbosity=0)
def features(q):
 x=q[base].copy()
 for c in x.columns.difference(cats):x[c]=pd.to_numeric(x[c],errors='coerce')
 x['FE_Temperature_x_Time']=x.Temperature_C*x.Cooking_Time_min
 x['FE_Log_Cooking_Time']=np.log1p(x.Cooking_Time_min)
 x['FE_Log_Initial_Concentration']=np.log1p(x.Initial_Concentration)
 x['FE_LogP_x_Temperature']=x.RDKit_LogP*x.Temperature_C
 x['FE_TPSA_x_Cooking_Time']=x.RDKit_TPSA*x.Cooking_Time_min
 return x
def metric(y,p):return dict(r2=r2_score(y,p),mae=mean_absolute_error(y,p),rmse=np.sqrt(mean_squared_error(y,p)))
all_summary=[]
for design,q,group in [('molecular_grouped',d,'Canonical_Molecular_ID'),('source_heldout',d[d.evidence_classification.eq('primary_source_verified')].copy(),'DOI_Normalized')]:
 q=q.reset_index(drop=True);x=features(q);y=q.target.astype(float);g=q[group].astype(str);num=[c for c in x if c not in cats];prep=ColumnTransformer([('num',Pipeline([('impute',SimpleImputer(strategy='median')),('scale',StandardScaler())]),num),('cat',Pipeline([('impute',SimpleImputer(strategy='constant',fill_value='Missing')),('encode',OneHotEncoder(handle_unknown='ignore',sparse_output=False))]),cats)])
 rows=[];pred=[];diag=[]
 for fold,(tr,te) in enumerate(GroupKFold(5).split(x,y,g),1):
  model=Pipeline([('prep',prep),('xgb',XGBRegressor(**params))]);model.fit(x.iloc[tr],np.log1p(y.iloc[tr]));z=np.expm1(np.clip(model.predict(x.iloc[te]),-20,20));mg=len(set(q.iloc[tr].Canonical_Molecular_ID)&set(q.iloc[te].Canonical_Molecular_ID));sg=len(set(q.iloc[tr].DOI_Normalized)&set(q.iloc[te].DOI_Normalized));assert (mg if design=='molecular_grouped' else sg)==0
  rows.append(dict(design=design,fold=fold,train_rows=len(tr),test_rows=len(te),train_groups=g.iloc[tr].nunique(),test_groups=g.iloc[te].nunique(),molecular_overlap=mg,source_overlap=sg,**metric(y.iloc[te],z)))
  pred.extend(dict(design=design,fold=fold,Record_ID=q.iloc[i].Record_ID,DOI=q.iloc[i].DOI,Canonical_Molecular_ID=q.iloc[i].Canonical_Molecular_ID,actual=float(a),predicted=float(b),residual=float(a-b)) for i,a,b in zip(te,y.iloc[te],z))
  diag.append(dict(design=design,fold=fold,test_target_mean=float(y.iloc[te].mean()),test_target_std=float(y.iloc[te].std()),test_target_max=float(y.iloc[te].max()),test_above_100=int((y.iloc[te]>100).sum()),molecular_overlap=mg,source_overlap=sg))
  pd.DataFrame(rows).to_csv(O/f'{design}_fold_metrics.csv',index=False);pd.DataFrame(pred).to_csv(O/f'{design}_oof_predictions.csv',index=False)
 p=pd.DataFrame(pred);all_summary.append(dict(design=design,eligible_rows=len(q),excluded_rows=len(d)-len(q),groups=g.nunique(),mean_fold_r2=float(pd.DataFrame(rows).r2.mean()),sd_fold_r2=float(pd.DataFrame(rows).r2.std(ddof=1)),pooled_oof_r2=metric(p.actual,p.predicted)['r2'],pooled_mae=metric(p.actual,p.predicted)['mae'],pooled_rmse=metric(p.actual,p.predicted)['rmse']))
 pd.DataFrame(diag).to_csv(O/f'{design}_diagnostics.csv',index=False)
pd.concat([pd.read_csv(O/f'{n}_oof_predictions.csv') for n in ['molecular_grouped','source_heldout']]).to_csv(O/'final_oof_predictions.csv',index=False)
pd.concat([pd.read_csv(O/f'{n}_diagnostics.csv') for n in ['molecular_grouped','source_heldout']]).to_csv(O/'validation_diagnostics.csv',index=False)
pd.DataFrame(all_summary).to_csv(O/'final_validation_summary.csv',index=False)
(O/'validation_config.json').write_text(json.dumps(dict(dataset=str(D),sha256=H,target='target',target_semantics='apparent concentration ratio percent',features=base+['FE_Temperature_x_Time','FE_Log_Cooking_Time','FE_Log_Initial_Concentration','FE_LogP_x_Temperature','FE_TPSA_x_Cooking_Time'],model=params,source_eligibility='primary_source_verified only',cv='GroupKFold 5'),indent=2))
