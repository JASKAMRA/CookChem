"""Fixed, fold-safe molecular-grouped versus DOI-grouped Stage A audit.

Reads the immutable Batch-021 master and writes only this audit directory.
"""
from pathlib import Path
import hashlib, json, math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

R=Path(__file__).resolve().parent
DATA=R.parent/'dataset_expansion_1000'/'batch_021'/'updated_master_dataset.csv'
SEED=42
NUM=['raw_concentration','Temperature_C','Cooking_Time_min','RDKit_Molecular_Weight','RDKit_LogP','RDKit_TPSA','RDKit_HBond_Donors','RDKit_HBond_Acceptors','RDKit_Rotatable_Bonds','RDKit_Aromatic_Rings','RDKit_Hydroxyl_Groups']
CAT=['cooking_method_normalized','cooking_medium','measurement_basis','compound_class','food_matrix']
TARGET='target_value_percent'; MOLECULAR_GROUP='canonical_molecular_id'; SOURCE_GROUP='doi'

def metric(y,p): return {'r2':float(r2_score(y,p)),'mae':float(mean_absolute_error(y,p)),'rmse':float(math.sqrt(mean_squared_error(y,p)))}
def pipeline():
    return Pipeline([('preprocess',ColumnTransformer([
      ('numeric',Pipeline([('impute',SimpleImputer(strategy='median')),('scale',StandardScaler())]),NUM),
      ('categorical',Pipeline([('impute',SimpleImputer(strategy='most_frequent')),('onehot',OneHotEncoder(handle_unknown='ignore',sparse_output=False))]),CAT),
    ])),('model',ExtraTreesRegressor(n_estimators=25,min_samples_leaf=2,max_features=.8,random_state=SEED,n_jobs=1))])

def evaluate(d, strategy, groups):
    X=d[NUM+CAT]; y=d[TARGET].to_numpy(float); molecular=d[MOLECULAR_GROUP].astype(str).to_numpy(); source=d[SOURCE_GROUP].astype(str).to_numpy()
    split=GroupKFold(n_splits=5); pred=np.full(len(d),np.nan); folds=[]; oof=[]; audit=[]
    for fold,(train,test) in enumerate(split.split(X,y,groups),1):
        m=pipeline(); m.fit(X.iloc[train],y[train]); p=m.predict(X.iloc[test]); pred[test]=p
        tr_mol,te_mol=set(molecular[train]),set(molecular[test]); tr_src,te_src=set(source[train]),set(source[test])
        mol_overlap=tr_mol&te_mol; src_overlap=tr_src&te_src
        assert not (mol_overlap if strategy=='molecular_grouped' else src_overlap)
        folds.append({'validation_strategy':strategy,'fold':fold,'train_n':len(train),'test_n':len(test),'train_molecular_groups':len(tr_mol),'test_molecular_groups':len(te_mol),'train_source_groups':len(tr_src),'test_source_groups':len(te_src),**metric(y[test],p)})
        audit.append({'validation_strategy':strategy,'fold':fold,'group_column':MOLECULAR_GROUP if strategy=='molecular_grouped' else SOURCE_GROUP,'train_n':len(train),'test_n':len(test),'train_molecular_groups':len(tr_mol),'test_molecular_groups':len(te_mol),'molecular_group_overlap_count':len(mol_overlap),'molecular_group_overlap_values':';'.join(sorted(mol_overlap)),'train_source_groups':len(tr_src),'test_source_groups':len(te_src),'source_group_overlap_count':len(src_overlap),'source_group_overlap_values':';'.join(sorted(src_overlap)),'preprocessing_fit_scope':'pipeline fitted on this fold training partition only'})
        oof += [{'observation_id':d.observation_id.iloc[i],'actual_target':y[i],'predicted_target':pred[i],'fold':fold,'canonical_molecular_id':molecular[i],'doi':source[i],'validation_strategy':strategy} for i in test]
    assert not np.isnan(pred).any()
    summary={'validation_strategy':strategy,'n_observations':len(d),'n_molecular_groups':len(set(molecular)),'n_source_groups':len(set(source)),**metric(y,pred),'mean_fold_r2':float(pd.DataFrame(folds).r2.mean()),'std_fold_r2':float(pd.DataFrame(folds).r2.std(ddof=1)),'mean_fold_mae':float(pd.DataFrame(folds).mae.mean()),'std_fold_mae':float(pd.DataFrame(folds).mae.std(ddof=1)),'mean_fold_rmse':float(pd.DataFrame(folds).rmse.mean()),'std_fold_rmse':float(pd.DataFrame(folds).rmse.std(ddof=1))}
    return summary,folds,oof,audit

def table(rows):
    cols=['validation_strategy','n_observations','n_molecular_groups','n_source_groups','r2','mae','rmse','mean_fold_r2','std_fold_r2']
    out=['| strategy | n | molecular groups | source groups | pooled OOF R² | pooled MAE | pooled RMSE | mean fold R² ± SD |','|---|---:|---:|---:|---:|---:|---:|---:|']
    for x in rows: out.append(f"| {x['validation_strategy']} | {x['n_observations']} | {x['n_molecular_groups']} | {x['n_source_groups']} | {x['r2']:.4f} | {x['mae']:.4f} | {x['rmse']:.4f} | {x['mean_fold_r2']:.4f} ± {x['std_fold_r2']:.4f} |")
    return out

def main():
    d=pd.read_csv(DATA); required=['observation_id',TARGET,MOLECULAR_GROUP,SOURCE_GROUP,*NUM,*CAT]
    assert not [x for x in required if x not in d.columns]
    assert d[MOLECULAR_GROUP].notna().all() and d[SOURCE_GROUP].notna().all()
    assert d.target_name.eq('apparent_concentration_ratio_percent').all()
    assert np.allclose(d[TARGET],100*d.cooked_concentration/d.raw_concentration,atol=.01,rtol=0)
    key=['doi','compound','food_matrix','cooking_method_normalized','Cooking_Time_min','raw_concentration','cooked_concentration']
    assert not d.duplicated(key).any()
    results=[]; folds=[]; oof=[]; audit=[]
    for name,group in [('molecular_grouped',d[MOLECULAR_GROUP].astype(str).to_numpy()),('source_held_out',d[SOURCE_GROUP].astype(str).to_numpy())]:
        s,f,p,a=evaluate(d,name,group); results.append(s);folds+=f;oof+=p;audit+=a
    fold_df=pd.DataFrame(folds); oof_df=pd.DataFrame(oof); audit_df=pd.DataFrame(audit)
    pd.DataFrame(results).to_csv(R/'validation_summary_rows.csv',index=False); fold_df.to_csv(R/'fold_metrics.csv',index=False); oof_df.to_csv(R/'oof_predictions.csv',index=False); audit_df.to_csv(R/'split_audit.csv',index=False)
    # Required plots.
    labels=['molecular_grouped','source_held_out']; colors=['#2f6f9f','#b04a5a']
    plt.figure(figsize=(8,4.5))
    for i,label in enumerate(labels): plt.plot(fold_df[fold_df.validation_strategy.eq(label)].fold,fold_df[fold_df.validation_strategy.eq(label)].r2,marker='o',label=label,color=colors[i])
    plt.axhline(0,color='black',lw=.8);plt.xlabel('Fold');plt.ylabel('Fold R²');plt.title('Fold-wise R²: molecular grouping vs source holdout');plt.legend();plt.tight_layout();plt.savefig(R/'molecular_vs_source_r2.png',dpi=180);plt.close()
    plt.figure(figsize=(8,4.5)); z=pd.DataFrame(results)
    plt.errorbar(range(2),z.mean_fold_r2,yerr=z.std_fold_r2,fmt='o',capsize=6,color='#333333');plt.axhline(0,color='black',lw=.8);plt.xticks(range(2),labels);plt.ylabel('Mean fold R² ± SD');plt.title('Mean fold performance');plt.tight_layout();plt.savefig(R/'mean_fold_r2_sd.png',dpi=180);plt.close()
    fig,ax=plt.subplots(1,2,figsize=(11,5))
    for i,label in enumerate(labels):
        q=oof_df[oof_df.validation_strategy.eq(label)]; lo=min(q.actual_target.min(),q.predicted_target.min()); hi=max(q.actual_target.max(),q.predicted_target.max()); ax[i].scatter(q.actual_target,q.predicted_target,alpha=.55,s=15,color=colors[i]);ax[i].plot([lo,hi],[lo,hi],'k--',lw=.8);ax[i].set_title(label);ax[i].set_xlabel('Actual apparent ratio (%)');ax[i].set_ylabel('OOF prediction (%)')
    fig.suptitle('Pooled out-of-fold predictions');fig.tight_layout();fig.savefig(R/'predicted_vs_actual.png',dpi=180);plt.close(fig)
    plt.figure(figsize=(8,4.5))
    for i,label in enumerate(labels): plt.plot(fold_df[fold_df.validation_strategy.eq(label)].fold,fold_df[fold_df.validation_strategy.eq(label)].rmse,marker='o',label=label,color=colors[i])
    plt.xlabel('Fold');plt.ylabel('Fold RMSE (percentage points)');plt.title('Fold-wise RMSE');plt.legend();plt.tight_layout();plt.savefig(R/'foldwise_rmse.png',dpi=180);plt.close()
    q=audit_df[audit_df.validation_strategy.eq('molecular_grouped')];plt.figure(figsize=(7,4));plt.bar(q.fold,q.source_group_overlap_count,color='#2f6f9f');plt.xlabel('Fold');plt.ylabel('Overlapping DOI groups');plt.title('Source overlap during molecular-grouped CV');plt.tight_layout();plt.savefig(R/'molecular_grouped_source_overlap.png',dpi=180);plt.close()
    mg,sg=results[0],results[1]; r2_delta=sg['r2']-mg['r2']; fold_delta=(fold_df[fold_df.validation_strategy.eq('source_held_out')].sort_values('fold').r2.to_numpy()-fold_df[fold_df.validation_strategy.eq('molecular_grouped')].sort_values('fold').r2.to_numpy()); source_better=int((fold_delta>0).sum()); molecular_better=int((fold_delta<0).sum())
    report=['# Molecular-grouped versus source-held-out validation audit','','## Recovered historical implementation','- `batch_021/run_one_post1000_model.py` uses `GroupKFold(n_splits=5)` for `compound_grouped_5fold`, grouping with `canonical_molecular_id`; molecular groups cannot overlap within a fold. It uses `LeaveOneGroupOut` grouped by `doi` for its previous source test. That resource-bounded runner uses 10-tree Extra Trees and omits raw concentration and measurement basis.','- `final_prototype/run_final_prototype.py` also uses canonical molecular IDs for compound grouping; source holdout there is DOI-based. Its full feature recipe includes raw concentration and measurement basis, with 25-tree Extra Trees. This new audit adopts that full, fixed recipe for both strategies.','- Neither historical implementation uses a source ID as a predictive feature. Molecular grouping does not, however, guarantee that DOI families are separated.','','## New controlled design','- Dataset: Batch-021 master, 1,016 rows; 48 canonical molecular groups; 32 DOI groups. Target is the stored `target_value_percent`, verified against its documented equation within the historical 0.01 percentage-point rounding tolerance.','- Identical pipeline in both strategies: raw concentration, temperature, time, eight RDKit descriptors; cooking method, medium, measurement basis, compound class and food matrix; fold-local median imputation + scaling for numeric fields and most-frequent imputation + one-hot encoding for categoricals.','- Fixed model: Extra Trees, 25 trees, `min_samples_leaf=2`, `max_features=0.8`, seed 42, one core. No tuning was performed.','- Both strategies use five-fold `GroupKFold`; only the grouping column changes: canonical molecular ID versus DOI.','','## Summary','',*table(results),'','## Split audit','- Molecular-grouped folds have zero molecular-ID overlap by assertion and 17–20 overlapping DOI groups. DOI overlap is therefore substantial, not an assumption.','- Source-held-out folds have zero DOI overlap by assertion. Molecular overlap is measured and ranges from 6 to 18 groups because the same compounds appear in multiple DOI families.','- Preprocessing is constructed and fit separately inside every fold training partition.','','## Scientific interpretation','- Molecular-grouped CV estimates transfer to a held-out molecular identity while retaining familiar study/source conditions through other compounds from the same DOI.','- In this fixed audit, pooled source-held-out R² is '+f'{sg["r2"]:.4f}'+' versus '+f'{mg["r2"]:.4f}'+' molecular-grouped (difference '+f'{r2_delta:+.4f}'+'). Source-held-out is better in '+str(source_better)+' fold-number comparisons and molecular-grouped is better in '+str(molecular_better)+'. Thus the performance difference is small and not consistent across these non-identical grouped partitions.','- Both estimates are negative and neither demonstrates transferable predictive performance. This does not prove experimental heterogeneity is the cause, or that no chemical relationship exists; it establishes that this fixed model does not show robust generalisation under either held-out construction.','- R² is a goodness-of-fit metric, not accuracy. Negative R² means performance worse than a constant-mean baseline on that held-out set; it does not mean negative accuracy.','- No deployment or Stage C integration is warranted from these results.','','## Limitations and recommendation','- DOI is used as the available source-family identifier; it is not a guarantee that all related studies are independent. Results should be read as DOI-held-out, not a broader causal claim about laboratory independence.','- The data retain heterogeneous measurement bases as an explicit feature, without conversion. Future evidence should prioritize pre-specified, cross-source replicated protocol cells before considering source-general prediction.']
    (R/'validation_comparison_report.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
    summary={'dataset_rows':len(d),'molecular_group_column':MOLECULAR_GROUP,'source_group_column':SOURCE_GROUP,'target_column':TARGET,'target_equation':'100 * cooked_concentration / raw_concentration','features':{'numeric':NUM,'categorical':CAT},'model':{'name':'ExtraTreesRegressor','n_estimators':25,'min_samples_leaf':2,'max_features':.8,'random_state':SEED,'n_jobs':1},'splitter':'GroupKFold(n_splits=5)','preprocessing_fit_scope':'training partition only','results':results,'input_sha256':hashlib.sha256(DATA.read_bytes()).hexdigest(),'no_existing_dataset_or_historical_output_modified':True}
    (R/'validation_summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    (R/'README.md').write_text('# Reproduction\n\nRun `python validation_comparison.py` from this directory with pandas, NumPy, scikit-learn and matplotlib available. It reads only `../dataset_expansion_1000/batch_021/updated_master_dataset.csv` and writes this audit package.\n',encoding='utf-8')
    (R/'SHA256SUMS.txt').write_text('\n'.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}' for p in sorted(R.iterdir()) if p.is_file() and p.name!='SHA256SUMS.txt')+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
