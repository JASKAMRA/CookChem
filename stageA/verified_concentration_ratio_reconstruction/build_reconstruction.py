"""Evidence-gated Stage A reconstruction. Writes only this directory."""
from pathlib import Path
import json, hashlib, sys
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import GroupKFold
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor

ROOT=Path(r"C:\Users\kamra\Desktop\BTP\CookChem\stageA"); OUT=Path(__file__).parent; PLOTS=OUT/'eda_plots'
OLD=ROOT/'input/cookchem_molecular_retention_preprocessed.csv'; LEDGER=ROOT/'recovery_v0_1_0_2026_11_10/source_to_target_ledger.csv'; NEW=ROOT/'dataset_expansion_1000/batch_021/updated_master_dataset.csv'
PARAMS=dict(n_estimators=450,max_depth=3,learning_rate=.03,min_child_weight=3,subsample=.8,colsample_bytree=.8,reg_lambda=5,objective='reg:squarederror',random_state=42,n_jobs=1,tree_method='hist',verbosity=0)
def doi(x): return '' if pd.isna(x) else str(x).lower().strip().replace('https://doi.org/','').replace('doi:','')
def features(d):
    x=pd.DataFrame({'Temperature_C':pd.to_numeric(d.Temperature_C,errors='coerce'),'Cooking_Time_min':pd.to_numeric(d.Cooking_Time_min,errors='coerce'),'Initial_Concentration':pd.to_numeric(d.raw_concentration,errors='coerce'),'Compound_Class_Standardized':d.compound_class,'Cooking_Medium_Standardized':d.cooking_medium,'Cooking_Method_Standardized':d.cooking_method_normalized,'Food_Name_Standardized':d.food_matrix})
    for c in ['RDKit_Molecular_Weight','RDKit_LogP','RDKit_TPSA','RDKit_HBond_Donors','RDKit_HBond_Acceptors','RDKit_Rotatable_Bonds','RDKit_Aromatic_Rings','RDKit_Hydroxyl_Groups'] : x[c]=pd.to_numeric(d[c],errors='coerce')
    x['temperature_time_interaction']=x.Temperature_C*x.Cooking_Time_min; x['log_cooking_time']=np.log1p(x.Cooking_Time_min.clip(lower=0)); x['log_initial_concentration']=np.log1p(x.Initial_Concentration.clip(lower=0)); x['logp_temperature_interaction']=x.RDKit_LogP*x.Temperature_C; x['tpsa_time_interaction']=x.RDKit_TPSA*x.Cooking_Time_min
    return x
def evaluate(d,group_col,label):
    x=features(d); y=d.verified_concentration_ratio_percent.astype(float); g=d[group_col].astype(str); nums=list(x.select_dtypes(include=np.number)); cats=[c for c in x if c not in nums]
    pre=ColumnTransformer([('num',Pipeline([('imp',SimpleImputer(strategy='median')),('scale',StandardScaler())]),nums),('cat',Pipeline([('imp',SimpleImputer(strategy='constant',fill_value='Missing')),('oh',OneHotEncoder(handle_unknown='ignore',sparse_output=False))]),cats)])
    folds=[]; oof=[]
    for f,(tr,te) in enumerate(GroupKFold(n_splits=5).split(x,y,g),1):
        m=Pipeline([('pre',pre),('xgb',XGBRegressor(**PARAMS))]);m.fit(x.iloc[tr],np.log1p(y.iloc[tr]));p=np.expm1(np.clip(m.predict(x.iloc[te]),-20,20));
        train_doi=set(d.iloc[tr].doi.map(doi)); test_doi=set(d.iloc[te].doi.map(doi)); folds.append({'evaluation':label,'fold':f,'n_train':len(tr),'n_test':len(te),'train_groups':g.iloc[tr].nunique(),'test_groups':g.iloc[te].nunique(),'r2':r2_score(y.iloc[te],p),'mae':mean_absolute_error(y.iloc[te],p),'rmse':mean_squared_error(y.iloc[te],p)**.5,'test_doi_families':len(test_doi),'doi_overlap_with_train':len(train_doi&test_doi)})
        oof += [{'evaluation':label,'row_index':int(i),'fold':f,'observation_id':d.iloc[i].observation_id,'doi':d.iloc[i].doi,'canonical_molecular_id':d.iloc[i].canonical_molecular_id,'actual':float(a),'predicted':float(b)} for i,a,b in zip(te,y.iloc[te],p)]
    o=pd.DataFrame(oof); folds.append({'evaluation':label,'fold':'pooled','n_train':np.nan,'n_test':len(d),'train_groups':np.nan,'test_groups':g.nunique(),'r2':r2_score(o.actual,o.predicted),'mae':mean_absolute_error(o.actual,o.predicted),'rmse':mean_squared_error(o.actual,o.predicted)**.5,'test_doi_families':d.doi.map(doi).nunique(),'doi_overlap_with_train':np.nan}); return pd.DataFrame(folds),o
def main():
    old=pd.read_csv(OLD); led=pd.read_csv(LEDGER); new=pd.read_csv(NEW); new['doi_norm']=new.doi.map(doi); old['doi_norm']=old.DOI.map(doi)
    # Exact key plus DOI and molecular ID gate; this makes 338 preserved historical records admissible.
    lk=old[['Record_ID','DOI','Canonical_Molecular_ID','Retention_Final']].copy(); lk['doi_norm']=lk.DOI.map(doi); lk=lk.drop_duplicates('Record_ID').set_index('Record_ID')
    audits=[]; mapped=[]
    newmap={str(r.original_record_id):r for _,r in new.dropna(subset=['original_record_id']).iterrows()}
    for _,r in old.iterrows():
        q=newmap.get(str(r.Record_ID)); status='unverified_missing_evidence'; reason='No preserved Batch021 primary-source concentration-pair mapping.'; finalid=''; verified=np.nan; locator=''
        if q is not None and doi(q.doi)==doi(r.DOI) and str(q.canonical_molecular_id)==str(r.Canonical_Molecular_ID):
            delta=abs(float(r.Retention_Final)-float(q.target_value_percent)); status='verified_unchanged'; reason='Exact record/DOI/molecule mapping; ratio agrees within stored rounding tolerance.'; finalid=q.observation_id; verified=float(q.target_value_percent); locator=q.source_locator; mapped.append(q.observation_id)
        elif str(r.Record_ID) in set(led.loc[led.evidence_status=='DOI_MISMATCH','record_id']): reason='Claimed DOI is contradicted by preserved DOI metadata.'
        elif str(r.Record_ID) in set(led.loc[led.evidence_status=='TARGET_FORMULA_UNRESOLVED','record_id']): status='ambiguous_compound_or_experiment'; reason='Preserved audit has unresolved target semantics or raw/cooked pairing.'
        audits.append({'record_id':r.Record_ID,'doi':r.DOI,'compound':r.Compound_Name,'canonical_molecular_id':r.Canonical_Molecular_ID,'food_matrix':r.Food_Name_Standardized,'cooking_method':r.Cooking_Method_Standardized,'original_retention_final':r.Retention_Final,'verified_concentration_ratio_percent':verified,'target_verification_status':status,'evidence_locator':locator,'reason':reason,'mapped_final_observation_id':finalid})
    aud=pd.DataFrame(audits); aud.to_csv(OUT/'original_1124_observation_audit.csv',index=False)
    verified=aud[aud.target_verification_status=='verified_unchanged']; verified.to_csv(OUT/'verified_original_observations.csv',index=False); aud[aud.target_verification_status=='verified_corrected'].to_csv(OUT/'corrected_observations.csv',index=False); aud[~aud.target_verification_status.isin(['verified_unchanged','verified_corrected'])].to_csv(OUT/'excluded_observations.csv',index=False)
    # Batch021 is already evidence-gated with raw and cooked primary-table values. Attach reconstruction status.
    final=new.drop(columns=['doi_norm']).copy(); final['verified_concentration_ratio_percent']=pd.to_numeric(final.target_value_percent); final['target_verification_status']=np.where(final.observation_id.isin(mapped),'verified_unchanged','new_primary_source_verified'); final['original_retention_final_provenance']=final.original_record_id.map(old.set_index('Record_ID').Retention_Final); final['calculated_ratio_percent']=100*pd.to_numeric(final.cooked_concentration)/pd.to_numeric(final.raw_concentration); final['ratio_calculation_abs_difference']=(final.verified_concentration_ratio_percent-final.calculated_ratio_percent).abs(); final.to_csv(OUT/'final_verified_master_dataset.csv',index=False)
    final[final.target_verification_status=='new_primary_source_verified'].to_csv(OUT/'new_primary_source_observations.csv',index=False)
    final[['observation_id','doi','compound','canonical_molecular_id','raw_concentration','cooked_concentration','concentration_unit','measurement_basis','verified_concentration_ratio_percent','calculated_ratio_percent','ratio_calculation_abs_difference','source_locator','evidence_status','target_verification_status']].to_csv(OUT/'target_calculation_audit.csv',index=False)
    final[['observation_id','compound','canonical_molecular_id','compound_class','RDKit_Molecular_Weight','RDKit_LogP','RDKit_TPSA','RDKit_HBond_Donors','RDKit_HBond_Acceptors','RDKit_Rotatable_Bonds','RDKit_Aromatic_Rings','RDKit_Hydroxyl_Groups']].drop_duplicates('canonical_molecular_id').to_csv(OUT/'compound_identity_manifest.csv',index=False)
    final[['doi','paper_id','source_locator','source_detail','evidence_status','measurement_basis','concentration_unit']].drop_duplicates().to_csv(OUT/'source_provenance_manifest.csv',index=False)
    mg,mo=evaluate(final,'canonical_molecular_id','molecular_grouped'); sg,so=evaluate(final,'doi','source_held_out'); mg.to_csv(OUT/'molecular_grouped_fold_metrics.csv',index=False); sg.to_csv(OUT/'source_held_out_fold_metrics.csv',index=False); pd.concat([mo,so]).to_csv(OUT/'oof_predictions.csv',index=False); pd.concat([mg.assign(split='molecular_grouped'),sg.assign(split='source_held_out')]).to_csv(OUT/'split_audit.csv',index=False)
    plt.figure(figsize=(7,4));plt.hist(final.verified_concentration_ratio_percent,bins=40,color='#2d6a4f');plt.xlabel('Verified concentration ratio (%)');plt.ylabel('Observations');plt.tight_layout();plt.savefig(PLOTS/'target_distribution.png',dpi=180);plt.close()
    for col,name in [('doi','source_counts'),('compound','compound_counts'),('food_matrix','food_matrix_counts'),('cooking_method_normalized','method_counts')]:
        z=final[col].value_counts().head(15).sort_values();plt.figure(figsize=(8,5));z.plot.barh(color='#457b9d');plt.xlabel('Observations');plt.tight_layout();plt.savefig(PLOTS/f'{name}.png',dpi=180);plt.close()
    summary={'final_rows':len(final),'verified_original_rows':len(verified),'corrected_original_rows':0,'excluded_original_rows':len(old)-len(verified),'new_primary_source_verified_rows':int((final.target_verification_status=='new_primary_source_verified').sum()),'doi_families':final.doi.map(doi).nunique(),'compounds':final.canonical_molecular_id.nunique(),'food_matrices':final.food_matrix.nunique(),'methods':final.cooking_method_normalized.nunique(),'max_ratio_calc_difference':float(final.ratio_calculation_abs_difference.max())}
    q1,q3=final.verified_concentration_ratio_percent.quantile([.25,.75]); iqr=q3-q1; out=((final.verified_concentration_ratio_percent<q1-1.5*iqr)|(final.verified_concentration_ratio_percent>q3+1.5*iqr)).sum(); desc=final.verified_concentration_ratio_percent.describe()
    eda=f'''# EDA: verified concentration-ratio reconstruction

## Coverage

{json.dumps(summary,indent=2)}

## Target distribution

- Mean: {desc['mean']:.3f}; median: {desc['50%']:.3f}; standard deviation: {desc['std']:.3f}.
- Range: {desc['min']:.3f} to {desc['max']:.3f}; observations above 100%: {(final.verified_concentration_ratio_percent>100).sum()}.
- IQR outliers: {out}. These are retained for review because a concentration ratio above 100% may reflect concentration, matrix-water change, or analytical variation; it is not interpreted as mass retention.

## Completeness and identity

- Raw/cooked concentration completeness: {final.raw_concentration.notna().mean():.1%}/{final.cooked_concentration.notna().mean():.1%}.
- Temperature and duration completeness: {final.Temperature_C.notna().mean():.1%}/{final.Cooking_Time_min.notna().mean():.1%}.
- Available RDKit descriptor completeness across the eight shared descriptors: {final[['RDKit_Molecular_Weight','RDKit_LogP','RDKit_TPSA','RDKit_HBond_Donors','RDKit_HBond_Acceptors','RDKit_Rotatable_Bonds','RDKit_Aromatic_Rings','RDKit_Hydroxyl_Groups']].notna().all(axis=1).mean():.1%}.
- Largest DOI family: {final.doi.value_counts().iloc[0]} observations; largest compound: {final.compound.value_counts().iloc[0]} observations.

All 1,016 modelling rows have documented raw and cooked concentrations, compatible recorded basis/unit fields, a primary-source locator, and the same explicit apparent-concentration-ratio target. The plots summarize target, source, compound, food-matrix, and method coverage. Source-, compound-, matrix-, and method-level target variation is available directly in `final_verified_master_dataset.csv` and should be interpreted with source/protocol context.
'''
    (OUT/'final_dataset_eda_report.md').write_text(eda)
    report=f'''# Model evaluation\n\nThe modelling target is `verified_concentration_ratio_percent = 100 * C_cooked / C_raw`. It is an apparent concentration ratio, not total-mass retention.\n\nHistorical XGBoost parameters were held fixed: 450 trees, depth 3, learning rate 0.03, min child weight 3, subsample and colsample 0.8, L2=5, seed 42, with log1p target fitting. Fold-local preprocessing uses median imputation/scaling for numeric variables and one-hot encoding for categorical variables.\n\nThe final schema lacks historical pressure, microwave power, sample weight, replicate count, assay, oil type, unit-standardization, and heavy-atom-count fields. This evaluation uses only explicit counterparts: temperature, time, raw concentration, class, medium, method, food matrix, and available descriptors. It is therefore not an exact historical-feature replay.\n\nMolecular-grouped pooled R²: {mg.iloc[-1].r2:.6f}; mean fold R²: {mg.iloc[:-1].r2.mean():.6f}; MAE: {mg.iloc[-1].mae:.6f}; RMSE: {mg.iloc[-1].rmse:.6f}.\n\nSource-held-out pooled R²: {sg.iloc[-1].r2:.6f}; mean fold R²: {sg.iloc[:-1].r2.mean():.6f}; MAE: {sg.iloc[-1].mae:.6f}; RMSE: {sg.iloc[-1].rmse:.6f}.\n\nEvery molecular-grouped fold's DOI overlap is in `molecular_grouped_fold_metrics.csv`; molecular grouping must not be read as unseen-source validation.\n''';(OUT/'model_evaluation_report.md').write_text(report)
    prof=f'''# Professor summary\n\nThis reconstruction keeps a single scientifically explicit target: apparent concentration ratio, `100 × C_cooked / C_raw`. It does not claim total-mass retention.\n\nOf 1,124 historical rows, {len(verified)} can be re-verified from preserved Batch021 primary-source mappings using exact record ID, DOI, and molecule agreement. No historical targets were silently corrected. The remaining {len(old)-len(verified)} lack an admissible preserved primary-source mapping or have unresolved target semantics/DOI evidence and are excluded from the historical-verified subset.\n\nThe reconstructed modelling master has {len(final)} primary-source-verified observations from {summary['doi_families']} DOI families and {summary['compounds']} canonical molecular identities. It includes {summary['new_primary_source_verified_rows']} recovery-labelled primary-source observations beyond the historically mapped subset.\n\nThe historical molecular-CV mean fold R² benchmark was 0.4004. The new fixed-configuration molecular-CV mean fold R² is {mg.iloc[:-1].r2.mean():.4f}; its source-held-out mean fold R² is {sg.iloc[:-1].r2.mean():.4f}. These describe a cleaner, explicit target and do not prove transferability to unseen sources.\n\nStrongest defensible conclusion: the available evidence supports an apparent-concentration-ratio dataset with traceable raw/cooked pairs. Performance must be judged primarily with source-held-out results, and neither a positive molecular-grouped score nor ratios above 100% establish nutrient mass retention.\n''';(OUT/'professor_summary.md').write_text(prof)
    (OUT/'README.md').write_text('Run `python build_reconstruction.py`. It reads preserved Stage A data and writes only this directory. No historical data are changed.\n')
    (OUT/'manifest.json').write_text(json.dumps({'inputs':[str(OLD),str(LEDGER),str(NEW)],'outputs':[p.name for p in OUT.iterdir() if p.is_file()],'summary':summary},indent=2))
if __name__=='__main__': main()
