"""Grouped-CV experimental model for the v0.2 apparent-ratio target."""
from __future__ import annotations
import csv, hashlib, json, math, platform, sys
from pathlib import Path
import joblib, numpy as np, pandas as pd, sklearn
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import ExtraTreesRegressor, GradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, median_absolute_error
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVR

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "clean_stageA_dataset.csv"
PACKAGE = ROOT / "model_package"
NUM = ["Temperature_C", "Cooking_Time_min", "RDKit_Molecular_Weight", "RDKit_LogP", "RDKit_TPSA", "RDKit_HBond_Donors", "RDKit_HBond_Acceptors", "RDKit_Rotatable_Bonds", "RDKit_Aromatic_Rings", "RDKit_Hydroxyl_Groups"]
CAT = ["compound_class", "food_matrix", "cooking_method_normalized", "cooking_medium"]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def metrics(y, p): return {"r2": float(r2_score(y,p)), "mae": float(mean_absolute_error(y,p)), "rmse": float(math.sqrt(mean_squared_error(y,p))), "median_ae": float(median_absolute_error(y,p))}
def pipe(model):
    pre = ColumnTransformer([("num", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), NUM), ("cat", Pipeline([("impute", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]), CAT)])
    return Pipeline([("preprocess", pre), ("model", model)])

def main():
    df = pd.read_csv(DATA)
    x, y, groups = df[NUM + CAT], df["target_value_percent"].astype(float).to_numpy(), df["canonical_molecular_id"].astype(str).to_numpy()
    if len(df) < 100 or len(set(groups)) < 20: raise RuntimeError("Dataset is too small for the predeclared experimental benchmark")
    models = {"dummy_median": DummyRegressor(strategy="median"), "ridge": Ridge(alpha=10), "random_forest": RandomForestRegressor(n_estimators=400, min_samples_leaf=2, random_state=42, n_jobs=1), "extra_trees": ExtraTreesRegressor(n_estimators=400, min_samples_leaf=2, random_state=42, n_jobs=1), "gradient_boosting": GradientBoostingRegressor(random_state=42, n_estimators=150, min_samples_leaf=3, learning_rate=.03), "svr_rbf": SVR(C=10, epsilon=.1, gamma="scale")}
    try:
        from xgboost import XGBRegressor
        models["xgboost"] = XGBRegressor(n_estimators=200, max_depth=3, learning_rate=.03, subsample=.8, colsample_bytree=.8, reg_lambda=5, random_state=42, n_jobs=1)
    except ImportError: pass
    splitter = GroupKFold(n_splits=5); summary=[]; all_oof=[]
    for name, estimator in models.items():
        pred=np.full(len(df), np.nan); folds=[]
        for fold,(tr,va) in enumerate(splitter.split(x,y,groups),1):
            if set(groups[tr]) & set(groups[va]): raise RuntimeError("compound leakage")
            p=pipe(estimator); p.fit(x.iloc[tr],y[tr]); pred[va]=p.predict(x.iloc[va]); folds.append({"model":name,"fold":fold,**metrics(y[va],pred[va]),"validation_groups":len(set(groups[va]))})
        summary.append({"model":name,**metrics(y,pred),"fold_mean_r2":float(np.mean([z['r2'] for z in folds])),"fold_mean_mae":float(np.mean([z['mae'] for z in folds]))})
        all_oof.extend({"record_id":df.iloc[i].record_id,"model":name,"actual_percent":y[i],"predicted_percent":pred[i],"compound_group":groups[i],"source_doi":df.iloc[i].doi,"food_matrix":df.iloc[i].food_matrix,"cooking_method":df.iloc[i].cooking_method_normalized} for i in range(len(df)))
    results=pd.DataFrame(summary).sort_values(["mae","rmse"]); results.to_csv(ROOT / "model_comparison.csv",index=False); pd.DataFrame(all_oof).to_csv(ROOT / "oof_predictions.csv",index=False)
    best=results.iloc[0].model; final=pipe(models[best]); final.fit(x,y); PACKAGE.mkdir(exist_ok=True); artifact=PACKAGE / "experimental_concentration_ratio_model.joblib"; joblib.dump(final,artifact)
    config={"status":"EXPERIMENTAL_NOT_DEPLOYABLE","selected_model":best,"selection_metric":"compound-grouped OOF MAE","target":{"name":"apparent_concentration_ratio_percent","equation":"100 * C_cooked / C_raw","semantic_limit":"not total-mass retention"},"validation":{"scheme":"5-fold GroupKFold by canonical molecular ID","source_holdout":"NOT_RUN: only two source DOI families","food_holdout":"NOT_RUN: only two food matrices","cooking_method_holdout":"NOT_RUN: insufficient independent support"},"features":{"numeric":NUM,"categorical":CAT},"dataset":{"rows":len(df),"compound_groups":len(set(groups)),"sha256":sha(DATA)},"software":{"python":sys.version,"platform":platform.platform(),"sklearn":sklearn.__version__},"artifact_sha256":sha(artifact),"stage_c_integration_authorized":False}
    (PACKAGE / "model_manifest.json").write_text(json.dumps(config,indent=2)+"\n")
    (PACKAGE / "DO_NOT_DEPLOY.md").write_text("This package predicts an apparent concentration ratio only. It is experimental, has not passed source/food holdout validation, and must not be used for Stage C cooked-exposure estimates.\n")
    columns = list(results.columns)
    markdown = "| " + " | ".join(columns) + " |\n| " + " | ".join(["---"] * len(columns)) + " |\n"
    markdown += "\n".join("| " + " | ".join(str(row[col]) for col in columns) + " |" for _, row in results.iterrows())
    (ROOT / "stageA_model_comparison.md").write_text("# Experimental grouped-CV comparison\n\n"+markdown+"\n\nThe result is not evidence of source, food, or clinical generalisation. The serialized package is deliberately marked non-deployable.\n")
    (ROOT / "stageC_integration_report.md").write_text("# Stage C integration\n\nNo Stage C code was changed. This experimental model predicts a concentration ratio, not total-mass retention; it lacks yield/mass inputs and fails the deployment gate. Existing Stage C fail-closed handling remains correct.\n")
    (ROOT / "FINAL_STATUS.md").write_text(f"# Final status\n\n- Target: **apparent concentration ratio** (`100 * C_cooked / C_raw`)\n- Verified rows trained: **{len(df)}**\n- New literature rows acquired: **0**\n- Best compound-grouped experimental model: **{best}**\n- Deployment: **BLOCKED**\n- Stage C model-prediction integration: **BLOCKED**\n\nThe model is an experimental benchmark only. Two source and food families are insufficient to establish generalisation.\n", encoding="utf-8")
    files=[p for p in ROOT.rglob('*') if p.is_file() and p.name not in {"SHA256SUMS.txt"} and "__pycache__" not in p.parts]
    (ROOT / "SHA256SUMS.txt").write_text("".join(f"{sha(p)}  {p.relative_to(ROOT)}\n" for p in sorted(files)))

if __name__ == "__main__": main()
