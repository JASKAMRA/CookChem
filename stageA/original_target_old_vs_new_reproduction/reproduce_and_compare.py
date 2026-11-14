"""Read-only controlled reproduction of historical Stage A molecular CV.

Writes only files beside this script.  It never alters project data or Git state.
"""
from __future__ import annotations
import hashlib, json, platform, sys
from pathlib import Path
import numpy as np
import pandas as pd
import sklearn
import xgboost
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBRegressor

ROOT = Path(r"C:\Users\kamra\Desktop\BTP\CookChem\stageA")
OUT = Path(__file__).resolve().parent
OLD = ROOT / "input" / "cookchem_molecular_retention_preprocessed.csv"
OLD_OOF = ROOT / "outputs" / "stageA_oof_predictions.csv"
NEW = ROOT / "dataset_expansion_1000" / "batch_021" / "updated_master_dataset.csv"

# These are the persisted modal XGBoost_tuned parameters in run_stage_a.py / outputs.
XGB = dict(n_estimators=450, max_depth=3, learning_rate=0.03,
           min_child_weight=3, subsample=0.8, colsample_bytree=0.8,
           reg_lambda=5, objective="reg:squarederror", random_state=42,
           n_jobs=1, tree_method="hist", verbosity=0)
OLD_NUM = ["Temperature_C", "Cooking_Time_min", "Pressure_kPa", "Microwave_Power_W",
           "Sample_Weight_g", "Initial_Concentration", "Replicates_n",
           "RDKit_Molecular_Weight", "RDKit_LogP", "RDKit_TPSA", "RDKit_HBond_Donors",
           "RDKit_HBond_Acceptors", "RDKit_Rotatable_Bonds", "RDKit_Aromatic_Rings",
           "RDKit_Hydroxyl_Groups", "RDKit_Heavy_Atom_Count"]
OLD_CAT = ["Assay_Method_Standardized", "Compound_Class_Standardized",
           "Cooking_Medium_Standardized", "Cooking_Method_Standardized",
           "Food_Name_Standardized", "Initial_Unit_Standardized", "Oil_Type_Standardized"]
DESC = ["RDKit_Molecular_Weight", "RDKit_LogP", "RDKit_TPSA", "RDKit_HBond_Donors",
        "RDKit_HBond_Acceptors", "RDKit_Rotatable_Bonds", "RDKit_Aromatic_Rings",
        "RDKit_Hydroxyl_Groups", "RDKit_Heavy_Atom_Count"]

def normdoi(x): return "" if pd.isna(x) else str(x).strip().lower().replace("https://doi.org/", "").replace("doi:", "")

def old_features(d):
    """Exact feature derivation used by historical run_stage_a.py."""
    x = d[OLD_NUM + OLD_CAT].copy()
    for c in OLD_NUM: x[c] = pd.to_numeric(x[c], errors="coerce")
    x["temperature_time_interaction"] = x["Temperature_C"] * x["Cooking_Time_min"]
    x["log_cooking_time"] = np.log1p(x["Cooking_Time_min"].clip(lower=0))
    x["log_initial_concentration"] = np.log1p(x["Initial_Concentration"].clip(lower=0))
    x["logp_temperature_interaction"] = x["RDKit_LogP"] * x["Temperature_C"]
    x["tpsa_time_interaction"] = x["RDKit_TPSA"] * x["Cooking_Time_min"]
    return x

def subset_features(d):
    """Only fields with explicit semantic counterparts; no substitutes for absent old fields."""
    x = pd.DataFrame({
        "Temperature_C": pd.to_numeric(d["Temperature_C"], errors="coerce"),
        "Cooking_Time_min": pd.to_numeric(d["Cooking_Time_min"], errors="coerce"),
        # Explicit mapping, not a new target: raw_concentration is the documented source value.
        "Initial_Concentration": pd.to_numeric(d["raw_concentration"], errors="coerce"),
        "Compound_Class_Standardized": d["compound_class"],
        "Cooking_Medium_Standardized": d["cooking_medium"],
        "Cooking_Method_Standardized": d["cooking_method_normalized"],
        "Food_Name_Standardized": d["food_matrix"],
    })
    for c in DESC:
        # Heavy atom count is absent from Batch021; it is deliberately omitted.
        if c in d.columns: x[c] = pd.to_numeric(d[c], errors="coerce")
    x["temperature_time_interaction"] = x["Temperature_C"] * x["Cooking_Time_min"]
    x["log_cooking_time"] = np.log1p(x["Cooking_Time_min"].clip(lower=0))
    x["log_initial_concentration"] = np.log1p(x["Initial_Concentration"].clip(lower=0))
    x["logp_temperature_interaction"] = x["RDKit_LogP"] * x["Temperature_C"]
    x["tpsa_time_interaction"] = x["RDKit_TPSA"] * x["Cooking_Time_min"]
    return x

def evaluate(x, y, groups, label, fixed_folds=None):
    nums = list(x.select_dtypes(include=[np.number]).columns)
    cats = [c for c in x.columns if c not in nums]
    pre = ColumnTransformer([
        ("num", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), nums),
        ("cat", Pipeline([("impute", SimpleImputer(strategy="constant", fill_value="Missing")),
                            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]), cats),
    ])
    rows=[]; out=[]
    if fixed_folds is None:
        split_iter = ((fold,tr,te) for fold,(tr,te) in enumerate(GroupKFold(n_splits=5).split(x,y,groups),1))
    else:
        split_iter = ((int(fold), np.flatnonzero(fixed_folds.to_numpy()!=fold), np.flatnonzero(fixed_folds.to_numpy()==fold)) for fold in sorted(fixed_folds.unique()))
    for fold,tr,te in split_iter:
        pipe=Pipeline([("pre",pre),("model",XGBRegressor(**XGB))])
        pipe.fit(x.iloc[tr], np.log1p(y.iloc[tr]))
        pr=np.expm1(np.clip(pipe.predict(x.iloc[te]),-20,20))
        rows.append(dict(experiment=label,fold=fold,n_train=len(tr),n_test=len(te),
                         molecular_groups_train=groups.iloc[tr].nunique(),molecular_groups_test=groups.iloc[te].nunique(),
                         r2=r2_score(y.iloc[te],pr),mae=mean_absolute_error(y.iloc[te],pr),
                         rmse=mean_squared_error(y.iloc[te],pr)**.5))
        out.extend(dict(row_index=int(i),fold=fold,y_true=float(a),y_pred=float(b)) for i,a,b in zip(x.index[te],y.iloc[te],pr))
    o=pd.DataFrame(out).sort_values("row_index")
    p=o.y_pred.to_numpy(); actual=o.y_true.to_numpy()
    summary=dict(experiment=label,fold="pooled",n_train=np.nan,n_test=len(actual),
                 molecular_groups_train=np.nan,molecular_groups_test=groups.nunique(),
                 r2=r2_score(actual,p),mae=mean_absolute_error(actual,p),rmse=mean_squared_error(actual,p)**.5)
    return pd.DataFrame(rows+[summary]),o

def main():
    old=pd.read_csv(OLD); new=pd.read_csv(NEW)
    saved=pd.read_csv(OLD_OOF); saved=saved[saved.Model=="XGBoost_tuned"].copy()
    saved=saved.rename(columns={"actual":"y_true","predicted":"y_pred"})
    # The historical OOF artifact is the authoritative record of GroupKFold assignment;
    # this avoids a changed tie-order in the installed scikit-learn release.
    historical_folds=old.Record_ID.map(saved.set_index("Record_ID").fold)
    if historical_folds.isna().any(): raise RuntimeError("Saved historical OOF lacks one or more old records")
    # Original historical replay.
    om,oo=evaluate(old_features(old), pd.to_numeric(old.Retention_Final), old.Canonical_Molecular_ID.astype(str), "old_1124_historical_target", historical_folds)
    oo=oo.merge(old[["Record_ID","DOI","Canonical_Molecular_ID","Retention_Final"]],left_on="row_index",right_index=True)
    oo.to_csv(OUT/"old_dataset_oof_predictions.csv",index=False)
    om.to_csv(OUT/"old_dataset_reproduced_fold_metrics.csv",index=False)
    compare=oo.merge(saved[["Record_ID","fold","y_true","y_pred"]],on="Record_ID",how="left",suffixes=("_reproduced","_historical"))
    compare["prediction_delta"] = compare.y_pred_reproduced-compare.y_pred_historical
    compare["fold_match"] = compare.fold_reproduced==compare.fold_historical
    compare.to_csv(OUT/"old_dataset_historical_vs_reproduced.csv",index=False)
    # ID mapping demands a unique historical record AND matching DOI and canonical molecule.
    hkey=old[["Record_ID","DOI","Canonical_Molecular_ID","Retention_Final"]].copy()
    hkey["doi_norm"]=hkey.DOI.map(normdoi)
    dupe=hkey.Record_ID.duplicated(keep=False)
    lookup=hkey[~dupe].set_index("Record_ID")
    audit=[]; keep=[]
    for i,r in new.iterrows():
        rid=r.original_record_id
        status="NO_HISTORICAL_RECORD_ID" if pd.isna(rid) else "UNMATCHED_OR_NONUNIQUE_ID"
        oldtarget=np.nan; doi_ok=False; mol_ok=False
        if not pd.isna(rid) and rid in lookup.index:
            q=lookup.loc[rid]; doi_ok=normdoi(r.doi)==q.doi_norm; mol_ok=str(r.canonical_molecular_id)==str(q.Canonical_Molecular_ID)
            if doi_ok and mol_ok: status="UNAMBIGUOUS_PROVENANCE_MATCH"; oldtarget=float(q.Retention_Final); keep.append(i)
            else: status="IDENTIFIER_PROVENANCE_CONFLICT"
        audit.append(dict(row_index=i,observation_id=r.observation_id,original_record_id=rid,doi=r.doi,
                          canonical_molecular_id=r.canonical_molecular_id,target_value_percent=r.target_value_percent,
                          mapped_retention_final=oldtarget,mapping_status=status,doi_match=doi_ok,molecule_match=mol_ok))
    audit=pd.DataFrame(audit); audit.to_csv(OUT/"new_dataset_target_recovery_audit.csv",index=False)
    nm=no=None
    if keep:
        sub=new.loc[keep].copy(); target=audit.loc[keep,"mapped_retention_final"].astype(float)
        nm,no=evaluate(subset_features(sub),target,sub.canonical_molecular_id.astype(str),"new_1016_provenance_mapped_338_subset")
        no=no.merge(sub[["observation_id","original_record_id","doi","canonical_molecular_id","target_value_percent"]],left_on="row_index",right_index=True)
        nm.to_csv(OUT/"new_dataset_fold_metrics.csv",index=False); no.to_csv(OUT/"new_dataset_oof_predictions.csv",index=False)
    else: pd.DataFrame().to_csv(OUT/"new_dataset_fold_metrics.csv",index=False); pd.DataFrame().to_csv(OUT/"new_dataset_oof_predictions.csv",index=False)
    exp=pd.concat([om.assign(dataset="old",target="Retention_Final",feature_spec="historical complete"),
                   nm.assign(dataset="new_subset",target="mapped Retention_Final",feature_spec="common semantic fields only") if nm is not None else pd.DataFrame()])
    exp.to_csv(OUT/"experiment_comparison.csv",index=False)
    split_rows=[]
    for name,data,folds,doi_col,mol_col in [("old",old,historical_folds,"DOI","Canonical_Molecular_ID"), ("new_mapped_subset",sub,no.set_index("row_index").fold.reindex(sub.index),"doi","canonical_molecular_id")]:
        for fold in sorted(folds.unique()):
            test=folds==fold; train=~test
            test_dois=set(data.loc[test,doi_col].map(normdoi)); train_dois=set(data.loc[train,doi_col].map(normdoi))
            split_rows.append(dict(experiment=name,fold=int(fold),n_test=int(test.sum()),test_molecular_groups=data.loc[test,mol_col].nunique(),test_doi_families=len(test_dois),doi_families_shared_with_training=len(test_dois & train_dois),cv="5-fold GroupKFold Canonical_Molecular_ID"))
    split=pd.DataFrame(split_rows)
    split.to_csv(OUT/"split_audit.csv",index=False)
    targetdiff=(audit.loc[audit.mapping_status=="UNAMBIGUOUS_PROVENANCE_MATCH","mapped_retention_final"].astype(float)-pd.to_numeric(audit.loc[audit.mapping_status=="UNAMBIGUOUS_PROVENANCE_MATCH","target_value_percent"])).abs()
    lines=["# Historical molecular-grouped CV reproduction", "", "## Scope and safeguards", "This is a read-only audit. It writes only this directory; no Stage A source dataset, historical output, Stage B/C/D content, Git state, or GitHub content was changed.", "", "## Exact historical experiment recovered", f"- Old input: `{OLD}` ({len(old)} rows; {old.Canonical_Molecular_ID.nunique()} molecular groups).", "- Target: `Retention_Final`.", "- Split: 5-fold `GroupKFold` grouped by `Canonical_Molecular_ID`; random seed is 42 for XGBoost (the splitter itself is deterministic and unshuffled).", "- Model: XGBoost tuned modal configuration persisted in historical code: 450 estimators, depth 3, learning rate 0.03, min child weight 3, subsample/colsample 0.8, L2=5, log1p target transform.", "- Preprocessing is fit inside each outer training fold: numeric median imputation + scaling; categorical constant imputation + one-hot encoding. Five documented engineered features are included.", "", "## Reproduction result", f"- Reproduced pooled R²: {om.iloc[-1].r2:.6f}; MAE: {om.iloc[-1].mae:.6f}; RMSE: {om.iloc[-1].rmse:.6f}.", f"- Mean fold R²: {om.iloc[:-1].r2.mean():.6f}; fold R²: {', '.join(f'{v:.6f}' for v in om.iloc[:-1].r2)}.", f"- Saved historical pooled R²: {r2_score(saved.y_true,saved.y_pred):.6f}. Fold assignments matched: {compare.fold_match.mean():.1%}; maximum prediction delta: {compare.prediction_delta.abs().max():.6g}.", "", "## Final Batch021 target recovery", f"- Final master: {len(new)} rows. `{audit.mapping_status.eq('UNAMBIGUOUS_PROVENANCE_MATCH').sum()}` rows map uniquely by historical `Record_ID` and agree on normalized DOI and canonical molecule.", f"- For those matches, |`Retention_Final` − `target_value_percent`| has maximum {targetdiff.max():.6f} and mean {targetdiff.mean():.6f}; this supports the documented final apparent concentration-ratio target, with storage/rounding differences—not a separate reconstructed target.", f"- The remaining {len(new)-len(keep)} final rows have no admissible historical-target mapping and were not assigned an invented target.", "", "## Separate mapped-subset experiment", "This is not an exact old-versus-new feature comparison. The final master lacks Pressure_kPa, Microwave_Power_W, Sample_Weight_g, Replicates_n, assay method, oil type, and the historical unit field. The subset run uses only named semantic counterparts (temperature, time, raw concentration, class, medium, method, food, and descriptors), with the same fold-local preprocessing, log target transform, XGBoost parameters, and molecular grouping. It does not substitute unavailable fields.", f"- Rows: {len(keep)}; molecular groups: {new.loc[keep,'canonical_molecular_id'].nunique()}; DOI families: {new.loc[keep,'doi'].map(normdoi).nunique()}.", f"- Pooled R²: {nm.iloc[-1].r2:.6f}; MAE: {nm.iloc[-1].mae:.6f}; RMSE: {nm.iloc[-1].rmse:.6f}." if nm is not None else "- No admissible mapping; no subset model was run.", "", "## Interpretation limits", "The old full-data result is a molecular-grouped, not source-held-out, estimate. Molecular groups can appear in multiple DOI families across folds, so it does not demonstrate performance on unseen sources. The 338-row mapped test is smaller and uses a reduced feature set, so it cannot isolate dataset expansion from feature-schema change. It must not be presented as a deployable or source-generalisation score.", "", "## Runtime", f"Python {sys.version.split()[0]}; pandas {pd.__version__}; scikit-learn {sklearn.__version__}; xgboost {xgboost.__version__}; {platform.platform()}."]
    (OUT/"reproduction_report.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    (OUT/"README.md").write_text("Run `python reproduce_and_compare.py` from this directory. Inputs are read-only project CSV files; all generated outputs remain here.\n",encoding="utf-8")
    manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.is_file()}
    (OUT/"SHA256SUMS.txt").write_text("\n".join(f"{v}  {k}" for k,v in sorted(manifest.items()))+"\n",encoding="utf-8")
if __name__=="__main__": main()
