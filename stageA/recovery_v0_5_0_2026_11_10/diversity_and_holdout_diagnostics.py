from pathlib import Path
import json,math,pandas as pd,numpy as np,joblib
from sklearn.metrics import r2_score,mean_absolute_error,mean_squared_error
from sklearn.model_selection import GroupKFold,LeaveOneGroupOut
R=Path(__file__).resolve().parent;df=pd.read_csv(R/'expanded_clean_stageA_dataset.csv');m=joblib.load(R/'model_package/experimental_apparent_concentration_ratio_model.joblib');f=json.loads((R/'model_package/model_manifest.json').read_text())['features'];X=df[f['numeric']+f['categorical']];y=df.target_value_percent.to_numpy()
def counts(col,name):df.groupby(col).size().reset_index(name='observations').to_csv(R/name,index=False)
counts('doi','observations_per_doi.csv');counts('compound','observations_per_compound.csv');counts('food_matrix','observations_per_food_matrix.csv');counts('cooking_method_normalized','observations_per_cooking_method.csv')
pd.crosstab(df.compound,df.food_matrix).to_csv(R/'compound_by_food_matrix.csv');pd.crosstab(df.doi,df.food_matrix).to_csv(R/'source_by_food_matrix.csv');pd.crosstab(df.doi,df.cooking_method_normalized).to_csv(R/'source_by_cooking_method.csv')
rows=[]
for label,g,splitter in [('food_matrix_grouped_5fold',df.food_matrix.astype(str).to_numpy(),GroupKFold(n_splits=5)),('cooking_method_LOSO',df.cooking_method_normalized.astype(str).to_numpy(),LeaveOneGroupOut())]:
 p=np.full(len(df),np.nan)
 for n,(tr,va) in enumerate(splitter.split(X,y,g),1):
  q=joblib.load(R/'model_package/experimental_apparent_concentration_ratio_model.joblib');q.fit(X.iloc[tr],y[tr]);p[va]=q.predict(X.iloc[va]);rows.append({'validation':label,'fold':n,'held_out':';'.join(sorted(set(g[va]))),'r2':r2_score(y[va],p[va]),'mae':mean_absolute_error(y[va],p[va]),'rmse':math.sqrt(mean_squared_error(y[va],p[va]))})
 rows.append({'validation':label,'fold':'pooled','held_out':'ALL','r2':r2_score(y,p),'mae':mean_absolute_error(y,p),'rmse':math.sqrt(mean_squared_error(y,p))})
pd.DataFrame(rows).to_csv(R/'additional_holdout_metrics.csv',index=False)
pre=m.named_steps['pre'];est=m.named_steps['m'];imp=pd.DataFrame({'feature':pre.get_feature_names_out(),'importance':est.feature_importances_}).sort_values('importance',ascending=False);imp.to_csv(R/'feature_importance.csv',index=False)
mic=imp[imp.feature.str.contains('microwave',case=False,na=False)];(R/'dataset_diversity_report.md').write_text('# Dataset diversity report\n\n'+f'- Rows: {len(df)}; DOI families: {df.doi.nunique()}; compounds: {df.compound.nunique()}; food matrices: {df.food_matrix.nunique()}; cooking methods: {df.cooking_method_normalized.nunique()}.\n- Cross-tabulations and count tables are saved beside this report.\n- New v0.5 evidence adds one independent DOI but only five related potato/vitamin-C treatments; it improves source count, not broad matrix/compound balance.\n- Microwave transformed-feature importance: '+(', '.join(f'{x.feature}={x.importance:.4f}' for _,x in mic.iterrows()) or 'none')+'. This is descriptive, not causal.\n')
