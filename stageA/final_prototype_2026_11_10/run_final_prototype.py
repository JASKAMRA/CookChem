"""Reproducible final Stage A research-prototype evaluation.

This program never changes its v1 parent dataset.  It evaluates apparent concentration
ratios only; it does not infer total-mass retention or authorize deployment.
"""
from __future__ import annotations
from pathlib import Path
import hashlib, json, math, shutil, warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold, KFold, LeaveOneGroupOut
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
try:
    from xgboost import XGBRegressor
    HAVE_XGB=True
except Exception:
    HAVE_XGB=False

R=Path(__file__).resolve().parent; P=R.parent/'recovery_v1_0_0_2026_11_10'; DATA=P/'expanded_clean_stageA_dataset.csv'
NUM_ALL=['raw_concentration','Temperature_C','Cooking_Time_min','RDKit_Molecular_Weight','RDKit_LogP','RDKit_TPSA','RDKit_HBond_Donors','RDKit_HBond_Acceptors','RDKit_Rotatable_Bonds','RDKit_Aromatic_Rings','RDKit_Hydroxyl_Groups']
MOL=NUM_ALL[3:]
PROCESS=['raw_concentration','Temperature_C','Cooking_Time_min']
CAT_PROCESS=['cooking_method_normalized','cooking_medium','measurement_basis','compound_class']
CAT_FULL=CAT_PROCESS+['food_matrix']
FEATURE_SETS={
 'molecular_descriptors_only':(MOL,[]),
 'cooking_experimental_only':(PROCESS,CAT_PROCESS),
 'molecular_plus_cooking':(MOL+PROCESS,CAT_PROCESS),
 'molecular_cooking_food_matrix':(MOL+PROCESS,CAT_FULL),
}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def metric(y,p): return {'r2':r2_score(y,p),'mae':mean_absolute_error(y,p),'rmse':math.sqrt(mean_squared_error(y,p))}
def make_pre(num,cat):
    tr=[]
    if num: tr.append(('numeric',Pipeline([('impute',SimpleImputer(strategy='median', keep_empty_features=True)),('scale',StandardScaler())]),num))
    if cat: tr.append(('categorical',Pipeline([('impute',SimpleImputer(strategy='most_frequent')),('onehot',OneHotEncoder(handle_unknown='ignore'))]),cat))
    return ColumnTransformer(tr, remainder='drop')
def model_spec(name):
    if name=='dummy': return DummyRegressor(strategy='mean'),{}
    if name=='ridge': return Ridge(alpha=10.0),{'alpha':10.0}
    if name=='random_forest': return RandomForestRegressor(n_estimators=25,min_samples_leaf=2,max_features=.8,random_state=42,n_jobs=1),{'n_estimators':25,'min_samples_leaf':2,'max_features':.8}
    if name=='extra_trees': return ExtraTreesRegressor(n_estimators=25,min_samples_leaf=2,max_features=.8,random_state=42,n_jobs=1),{'n_estimators':25,'min_samples_leaf':2,'max_features':.8}
    if name=='xgboost' and HAVE_XGB: return XGBRegressor(n_estimators=25,max_depth=3,min_child_weight=2,learning_rate=.04,subsample=.8,colsample_bytree=.8,reg_lambda=5,random_state=42,n_jobs=1,objective='reg:squarederror'),{'n_estimators':25,'max_depth':3,'min_child_weight':2}
    raise ValueError(name)
def fit_inner(name,num,cat,Xtr,ytr,groups,grouped):
    # Conservative pre-specified configurations are used identically in all folds.
    # This bounded configuration policy avoids selecting against outer holdouts and
    # keeps the small, highly grouped dataset from supporting a high-variance search.
    est,params=model_spec(name); return Pipeline([('preprocess',make_pre(num,cat)),('model',est)]),params
def evaluate(name,num,cat,kind,groups,d,report_label=None):
    X=d[num+cat]; y=d.target_value_percent.to_numpy(float); groups=np.asarray(groups)
    if kind=='random': splits=KFold(n_splits=5,shuffle=True,random_state=42).split(X,y); inner_grouped=False
    elif kind=='source': splits=LeaveOneGroupOut().split(X,y,groups); inner_grouped=True
    else: splits=GroupKFold(n_splits=min(5,len(np.unique(groups)))).split(X,y,groups); inner_grouped=True
    pred=np.full(len(d),np.nan); rows=[]; chosen=[]
    for fold,(tr,te) in enumerate(splits,1):
        m,params=fit_inner(name,num,cat,X.iloc[tr],y[tr],groups[tr],inner_grouped)
        m.fit(X.iloc[tr],y[tr]); pred[te]=m.predict(X.iloc[te])
        rows.append({'model':name,'validation':report_label or kind,'fold':fold,'train_n':len(tr),'test_n':len(te),'independent_groups_test':len(np.unique(groups[te])),'held_out_groups':'; '.join(sorted(map(str,np.unique(groups[te])))),**metric(y[te],pred[te])})
        chosen.append({'model':name,'validation':report_label or kind,'fold':fold,'best_inner_parameters':json.dumps(params,sort_keys=True)})
    pooled={'model':name,'validation':report_label or kind,'fold':'pooled','train_n':None,'test_n':len(d),'independent_groups_test':len(np.unique(groups)),'held_out_groups':'ALL_OOF',**metric(y,pred)}
    return pooled,rows,pred,chosen
def main():
 R.mkdir(exist_ok=True); d=pd.read_csv(DATA)
 # Eligibility is intentionally inclusive only where the parent provenance/target contract is intact.
 reasons=[]; desc=d[MOL].apply(pd.to_numeric,errors='coerce').notna().all(axis=1)
 for i,x in d.iterrows():
  why=[]
  if x.target_name!='apparent_concentration_ratio_percent': why.append('target_name_not_apparent_ratio')
  if not np.isfinite(float(x.raw_concentration)) or float(x.raw_concentration)<=0: why.append('invalid_raw_concentration')
  if not np.isfinite(float(x.cooked_concentration)) or float(x.cooked_concentration)<0: why.append('invalid_cooked_concentration')
  # Historical source tables retain targets rounded to two decimals in some records.
  # A 0.01 percentage-point tolerance validates that documented rounding without
  # recalculating or replacing the authoritative target values.
  if not np.isfinite(float(x.target_value_percent)) or abs(float(x.target_value_percent)-100*float(x.cooked_concentration)/float(x.raw_concentration))>0.01: why.append('target_formula_mismatch')
  if not desc.iloc[i]: why.append('incomplete_verified_descriptor_vector')
  if not str(x.canonical_molecular_id).strip(): why.append('missing_verified_canonical_molecular_id')
  reasons.append(';'.join(why) if why else 'ELIGIBLE')
 d['eligibility_reason']=reasons; eligible=d[d.eligibility_reason.eq('ELIGIBLE')].copy()
 d.to_csv(R/'dataset_with_eligibility_audit.csv',index=False); eligible.to_csv(R/'final_modelling_dataset.csv',index=False)
 pd.DataFrame({'observation_id':d.observation_id,'eligibility_reason':reasons}).to_csv(R/'eligibility_filter_log.csv',index=False)
 if len(eligible)!=len(d): raise RuntimeError('Unexpected exclusion; inspect eligibility log before modelling.')
 # Persist plain feature matrix/target separately for transparent reproduction.
 X=eligible[NUM_ALL+CAT_FULL].copy(); X.to_csv(R/'feature_matrix.csv',index=False); pd.DataFrame({'observation_id':eligible.observation_id,'apparent_concentration_ratio_percent':eligible.target_value_percent}).to_csv(R/'target_vector.csv',index=False)
 schema={'target':'apparent_concentration_ratio_percent','equation':'100 * C_cooked / C_raw','semantic_limit':'Apparent concentration ratio; not true total-mass retention.','numeric_features':NUM_ALL,'categorical_features':CAT_FULL,'descriptor_features':MOL,'canonical_smiles':'Not stored in the authoritative 439-row dataset. Canonical molecular identifiers and precomputed verified RDKit descriptors are used; no SMILES were invented or backfilled.','basis_handling':'Measurement basis is an explicit categorical feature. No fresh/dry conversion or pooled basis assumption is performed.'}
 (R/'feature_schema.json').write_text(json.dumps(schema,indent=2)+'\n',encoding='utf-8')
 # Main candidate comparison: full feature set, fold-safe inner configuration selection.
 models=['dummy','ridge','random_forest','extra_trees']+(['xgboost'] if HAVE_XGB else [])
 validations={'random':np.arange(len(eligible)),'compound_grouped':eligible.canonical_molecular_id.astype(str).to_numpy(),'food_matrix_grouped':eligible.food_matrix.astype(str).to_numpy(),'source_held_out':eligible.doi.astype(str).to_numpy()}
 allsum=[]; allfold=[]; allpred=[]; allparams=[]
 num,cat=FEATURE_SETS['molecular_cooking_food_matrix']
 for kind,g in validations.items():
  k='random' if kind=='random' else ('source' if kind=='source_held_out' else 'group')
  for name in models:
   s,f,p,z=evaluate(name,num,cat,k,g,eligible,kind); allsum.append(s);allfold.extend(f);allparams.extend(z)
   allpred.extend({'observation_id':eligible.observation_id.iloc[i],'model':name,'validation':kind,'actual':eligible.target_value_percent.iloc[i],'prediction':p[i],'residual':p[i]-eligible.target_value_percent.iloc[i],'doi':eligible.doi.iloc[i],'compound':eligible.compound.iloc[i],'food_matrix':eligible.food_matrix.iloc[i],'cooking_method':eligible.cooking_method_normalized.iloc[i]} for i in range(len(eligible)))
 summary=pd.DataFrame(allsum); folds=pd.DataFrame(allfold); preds=pd.DataFrame(allpred)
 summary.to_csv(R/'model_comparison.csv',index=False); folds.to_csv(R/'fold_metrics.csv',index=False); pd.DataFrame(allparams).to_csv(R/'inner_search_selections.csv',index=False);preds.to_csv(R/'out_of_fold_predictions.csv',index=False)
 # Controlled ablation with Extra Trees, identical group definitions across each validation perspective.
 ab=[];abfold=[]
 for fs,(n,c) in FEATURE_SETS.items():
  for label,g in [('compound_grouped',validations['compound_grouped']),('source_held_out',validations['source_held_out'])]:
   s,f,_,_=evaluate('extra_trees',n,c,'source' if label=='source_held_out' else 'group',g,eligible,label);s['feature_set']=fs;ab.append(s)
   for q in f:q['feature_set']=fs
   abfold.extend(f)
 pd.DataFrame(ab).to_csv(R/'ablation_study.csv',index=False);pd.DataFrame(abfold).to_csv(R/'ablation_fold_metrics.csv',index=False)
 # Within-source interpolation only: random folds inside sufficiently sized single DOI families.
 within=[]
 for doi,g in eligible.groupby('doi'):
  if len(g)<20: continue
  s,f,_,_=evaluate('extra_trees',num,cat,'random',np.arange(len(g)),g.reset_index(drop=True))
  s['doi']=doi;s['interpretation']='Within-source random interpolation diagnostic only; not external generalisation.';within.append(s)
 pd.DataFrame(within).to_csv(R/'within_source_interpolation_metrics.csv',index=False)
 # Best source-OOF candidate is diagnostic, not a model-selection authorization.
 best=summary[summary.validation.eq('source_held_out')].sort_values(['mae','rmse']).iloc[0]
 bp=preds[(preds.validation=='source_held_out')&(preds.model==best.model)].copy()
 for col in ['compound','food_matrix','cooking_method','doi']:
  bp.groupby(col).apply(lambda z:pd.Series(metric(z.actual,z.prediction))).reset_index().to_csv(R/f'error_by_{col}.csv',index=False)
 bp.sort_values('residual',key=lambda x:x.abs(),ascending=False).head(25).to_csv(R/'largest_source_held_out_errors.csv',index=False)
 # Full-data feature importance describes fit only; it is not a causal finding.
 fm,_=fit_inner('extra_trees',num,cat,eligible[num+cat],eligible.target_value_percent,eligible.doi,True); fm.fit(eligible[num+cat],eligible.target_value_percent)
 names=fm.named_steps['preprocess'].get_feature_names_out(); imp=pd.DataFrame({'feature':names,'importance':fm.named_steps['model'].feature_importances_}).sort_values('importance',ascending=False);imp.to_csv(R/'full_fit_feature_importance.csv',index=False)
 # Publication-quality diagnostics, generated from OOF estimates.
 plt.figure(figsize=(7,5));plt.hist(eligible.target_value_percent,bins=30,color='#306998');plt.xlabel('Apparent concentration ratio (%)');plt.ylabel('Observations');plt.tight_layout();plt.savefig(R/'target_distribution.png',dpi=160);plt.close()
 plt.figure(figsize=(6,6));plt.scatter(bp.actual,bp.prediction,alpha=.7);lo=min(bp.actual.min(),bp.prediction.min());hi=max(bp.actual.max(),bp.prediction.max());plt.plot([lo,hi],[lo,hi],'k--');plt.xlabel('Actual apparent ratio (%)');plt.ylabel('Source-held-out prediction (%)');plt.title(f'{best.model}: source-held-out OOF');plt.tight_layout();plt.savefig(R/'source_held_out_actual_vs_predicted.png',dpi=160);plt.close()
 plt.figure(figsize=(7,5));plt.hist(bp.residual,bins=30,color='#b34d4d');plt.xlabel('Prediction minus actual (%)');plt.ylabel('Observations');plt.tight_layout();plt.savefig(R/'source_held_out_residual_distribution.png',dpi=160);plt.close()
 q=summary[summary.validation.eq('source')].sort_values('mae');plt.figure(figsize=(7,4));plt.bar(q.model,q.mae,color='#4f81bd');plt.ylabel('Source-held-out MAE (percentage points)');plt.xticks(rotation=25,ha='right');plt.tight_layout();plt.savefig(R/'source_held_out_model_comparison.png',dpi=160);plt.close()
 # Reports and provenance copies.
 shutil.copy2(DATA,R/'authoritative_v1_dataset_copy.csv');shutil.copy2(P/'source_verification_ledger.csv',R/'source_verification_ledger.csv');shutil.copy2(P/'exclusion_log.csv',R/'parent_exclusion_log.csv')
 write=lambda n,t:(R/n).write_text(t.strip()+'\n',encoding='utf-8')
 write('descriptor_coverage_report.md',f'''# Descriptor coverage

All **{len(eligible)}/{len(d)}** eligible observations have finite values for each of the eight existing RDKit fields: molecular weight, LogP, TPSA, H-bond donors, H-bond acceptors, rotatable bonds, aromatic rings, and hydroxyl groups. Repeated canonical molecular IDs were checked for descriptor consistency; the source table carries canonical IDs and descriptor values, but does **not** carry canonical SMILES. No molecular identity, SMILES, or descriptor was invented or resolved externally in this implementation.

The descriptor vector is included in every molecular feature experiment. `descriptor_identity_consistency.csv` records the consistency check.
''')
 cons=eligible.groupby('canonical_molecular_id')[MOL].nunique(dropna=False).max(axis=1).reset_index(name='maximum_distinct_value_count');cons['consistent']=cons.maximum_distinct_value_count.eq(1);cons.to_csv(R/'descriptor_identity_consistency.csv',index=False)
 write('model_scope_and_limitations.md',f'''# Model scope and limitations

## Decision: C — no defensible predictive model is currently supported

The package implements working, fold-safe research experiments, but no serialized prediction model is released. The best descriptive source-held-out candidate was `{best.model}` (pooled R² {best.r2:.4f}, MAE {best.mae:.2f}, RMSE {best.rmse:.2f}). Source-held-out performance is a stress test dominated by source-specific compound, food, basis and protocol domains; it does not demonstrate new-source generalisation.

All results predict only the observed **apparent concentration ratio** `100 × cooked concentration / raw concentration`. They must not be interpreted as total-mass retention, clinical advice, cooking guidance, or deployment evidence. Measurement basis is represented but never converted. The lack of strict cross-source protocol-identical replications remains the decisive scientific blocker.

The only potentially legitimate future use is restricted descriptive, within-source interpolation after a separate, pre-specified assessment of that source's experimental design. This package makes no end-user prediction claim and does not modify Stage C.
''')
 write('model_comparison_report.md',f'''# Model comparison

All preprocessing occurs inside the training portion of every outer fold. The small, strongly grouped dataset does not support a high-variance optimisation search, so this final reproducibility run uses documented conservative, pre-specified configurations (recorded per fold in `inner_search_selections.csv`) rather than tuning against outer results. Models: Dummy mean baseline, Ridge, Random Forest, Extra Trees, and {'XGBoost' if HAVE_XGB else 'XGBoost unavailable'}. Random split is diagnostic only. Compound-, food-, and source-held-out metrics are reported in CSV form with every fold's training/test counts and held-out groups.

The selected diagnostic source-held-out row is `{best.model}`: R² {best.r2:.4f}; MAE {best.mae:.2f}; RMSE {best.rmse:.2f}. This is not a deployment selection.
''')
 write('ablation_report.md','''# Descriptor ablation

Extra Trees was evaluated with identical outer group definitions across four feature sets: descriptors only; process/experimental only; descriptors plus process; and descriptors plus process plus food matrix. Read `ablation_study.csv` together with source-held-out results: an improvement in random or compound-held-out evaluation is not evidence of source generalisation. Molecular descriptors are genuinely passed to the estimator in all molecular feature sets; their contribution is empirical, not assumed.''')
 write('reproduction_instructions.md','''# Reproduction

1. Run `python run_final_prototype.py` from this package directory or repository root.
2. Run `python validate_final_prototype.py`.

The script reads only the v1 authoritative copy and writes this package. It requires Python with pandas, NumPy, scikit-learn, matplotlib, and optionally xgboost. It creates no Git or remote changes.
''')
 manifest={'package':'StageA_FinalPrototype_2026-11-10','parent_dataset':str(DATA),'parent_sha256':sha(DATA),'eligible_rows':len(eligible),'source_families':int(eligible.doi.nunique()),'target':'apparent concentration ratio; not total-mass retention','model_scope_decision':'C_NO_DEFENSIBLE_GENERAL_PREDICTIVE_MODEL','saved_model':False,'stage_c_integration_authorized':False,'xgboost_available':HAVE_XGB}
 (R/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
 (R/'SHA256SUMS.txt').write_text('\n'.join(f'{sha(p)}  {p.name}' for p in sorted(R.iterdir()) if p.is_file() and p.name!='SHA256SUMS.txt')+'\n',encoding='utf-8')
 print(json.dumps(manifest,indent=2))
if __name__=='__main__': main()
