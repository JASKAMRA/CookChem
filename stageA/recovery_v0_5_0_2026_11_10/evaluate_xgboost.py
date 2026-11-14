"""Independent XGBoost comparison using the identical fold-safe feature pipeline."""
from pathlib import Path
import math,pandas as pd,numpy as np
from xgboost import XGBRegressor
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from sklearn.model_selection import GroupKFold,LeaveOneGroupOut
from sklearn.metrics import r2_score,mean_absolute_error,mean_squared_error
R=Path(__file__).resolve().parent;d=pd.read_csv(R/'expanded_clean_stageA_dataset.csv');N=['Temperature_C','Cooking_Time_min','RDKit_Molecular_Weight','RDKit_LogP','RDKit_TPSA','RDKit_HBond_Donors','RDKit_HBond_Acceptors','RDKit_Rotatable_Bonds','RDKit_Aromatic_Rings','RDKit_Hydroxyl_Groups'];C=['compound_class','food_matrix','cooking_method_normalized','cooking_medium'];X=d[N+C];y=d.target_value_percent.to_numpy()
def make():return Pipeline([('p',ColumnTransformer([('n',Pipeline([('i',SimpleImputer(strategy='median')),('s',StandardScaler())]),N),('c',Pipeline([('i',SimpleImputer(strategy='most_frequent')),('o',OneHotEncoder(handle_unknown='ignore',sparse_output=False))]),C)])),('m',XGBRegressor(n_estimators=200,max_depth=3,learning_rate=.03,subsample=.8,colsample_bytree=.8,reg_lambda=5,random_state=42,n_jobs=1))])
out=[]
for name,g,sp in [('compound_grouped_5fold',d.canonical_molecular_id.astype(str).to_numpy(),GroupKFold(n_splits=5)),('leave_one_source_out',d.doi.astype(str).to_numpy(),LeaveOneGroupOut())]:
 p=np.full(len(d),np.nan)
 for fold,(tr,va) in enumerate(sp.split(X,y,g),1):
  m=make();m.fit(X.iloc[tr],y[tr]);p[va]=m.predict(X.iloc[va]);out.append({'validation':name,'fold':fold,'held_out':';'.join(sorted(set(g[va]))),'r2':r2_score(y[va],p[va]),'mae':mean_absolute_error(y[va],p[va]),'rmse':math.sqrt(mean_squared_error(y[va],p[va]))})
 out.append({'validation':name,'fold':'pooled','held_out':'ALL','r2':r2_score(y,p),'mae':mean_absolute_error(y,p),'rmse':math.sqrt(mean_squared_error(y,p))})
pd.DataFrame(out).to_csv(R/'xgboost_fold_metrics.csv',index=False)
