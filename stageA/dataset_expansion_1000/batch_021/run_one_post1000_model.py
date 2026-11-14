"""Run one fixed-specification model across all post-1,000 holdouts."""
from pathlib import Path
import sys, math
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
R=Path(__file__).resolve().parent; name=sys.argv[1]; df=pd.read_csv(R/'updated_master_dataset.csv')
NUM=['Temperature_C','Cooking_Time_min','RDKit_Molecular_Weight','RDKit_LogP','RDKit_TPSA','RDKit_HBond_Donors','RDKit_HBond_Acceptors','RDKit_Rotatable_Bonds','RDKit_Aromatic_Rings','RDKit_Hydroxyl_Groups']; CAT=['compound_class','food_matrix','cooking_method_normalized','cooking_medium']; X=df[NUM+CAT]; y=df.target_value_percent.to_numpy()
models={'dummy_median':DummyRegressor(strategy='median'),'ridge':Ridge(alpha=10),'random_forest':RandomForestRegressor(n_estimators=10,min_samples_leaf=2,random_state=42,n_jobs=1),'extra_trees':ExtraTreesRegressor(n_estimators=10,min_samples_leaf=2,random_state=42,n_jobs=1),'gradient_boosting':GradientBoostingRegressor(n_estimators=25,min_samples_leaf=3,learning_rate=.03,random_state=42),'svr_rbf':SVR(C=10,epsilon=.1)}
if name=='xgboost':
 from xgboost import XGBRegressor
 models[name]=XGBRegressor(n_estimators=10,max_depth=4,learning_rate=.03,subsample=.8,colsample_bytree=.8,random_state=42,n_jobs=1,objective='reg:squarederror')
assert name in models; model=models[name]
def pipe(): return Pipeline([('pre',ColumnTransformer([('n',Pipeline([('i',SimpleImputer(strategy='median')),('s',StandardScaler())]),NUM),('c',Pipeline([('i',SimpleImputer(strategy='most_frequent')),('o',OneHotEncoder(handle_unknown='ignore',sparse_output=False))]),CAT)])),('m',model)])
def met(a,b): return {'r2':float(r2_score(a,b)),'mae':float(mean_absolute_error(a,b)),'rmse':float(math.sqrt(mean_squared_error(a,b)))}
groups={'compound_grouped_5fold':(df.canonical_molecular_id.astype(str).to_numpy(),False),'food_matrix_grouped_5fold':(df.food_matrix.astype(str).to_numpy(),False),'leave_one_source_out':(df.doi.astype(str).to_numpy(),True)}
rows=[]; folds=[]; predrows=[]
for label,(g,loso) in groups.items():
 split=LeaveOneGroupOut() if loso else GroupKFold(n_splits=min(5,len(set(g)))); pred=np.full(len(y),np.nan)
 for i,(tr,va) in enumerate(split.split(X,y,g),1):
  z=pipe(); z.fit(X.iloc[tr],y[tr]); pred[va]=z.predict(X.iloc[va]); folds.append({'model':name,'validation':label,'fold':i,'held_out':';'.join(sorted(set(g[va]))),'n_valid':len(va),**met(y[va],pred[va])})
 rows.append({'model':name,'validation':label,**met(y,pred)})
 predrows += [{'observation_id':df.iloc[i].observation_id,'model':name,'validation':label,'actual_percent':y[i],'predicted_percent':pred[i],'group':g[i],'source_doi':df.doi.iloc[i]} for i in range(len(df))]
pd.DataFrame(rows).to_csv(R/f'post1000_model_comparison_{name}.csv',index=False); pd.DataFrame(folds).to_csv(R/f'post1000_fold_metrics_{name}.csv',index=False); pd.DataFrame(predrows).to_csv(R/f'post1000_oof_predictions_{name}.csv',index=False)
if name=='extra_trees':
 src=pd.DataFrame(folds); src[src.validation.eq('leave_one_source_out')].sort_values('mae',ascending=False).to_csv(R/'extra_trees_source_loso_errors.csv',index=False)
 z=pipe(); z.fit(X,y); imp=pd.DataFrame({'feature':z.named_steps['pre'].get_feature_names_out(),'importance':z.named_steps['m'].feature_importances_}).sort_values('importance',ascending=False); imp.to_csv(R/'extra_trees_feature_importance.csv',index=False)
print(pd.DataFrame(rows).to_string(index=False))
