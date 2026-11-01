"""Stage B, step 3: tail-aware target/loss evaluation with unchanged GroupKFold."""
from pathlib import Path
import sys
import math
import numpy as np
import pandas as pd
from sklearn.compose import TransformedTargetRegressor
from sklearn.ensemble import ExtraTreesRegressor, GradientBoostingRegressor, HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PowerTransformer

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
from evaluate_missingness_features import augmented_features
sys.path.insert(0, str(REPO / "stageA" / "scripts"))
import run_stage_a as stage_a


def metric(y, pred):
    return {"MAE": float(mean_absolute_error(y, pred)), "RMSE": float(math.sqrt(mean_squared_error(y, pred))), "R2": float(r2_score(y, pred))}


def estimator(name):
    if name == "ExtraTrees_log1p":
        return TransformedTargetRegressor(regressor=ExtraTreesRegressor(n_estimators=300, min_samples_leaf=2, random_state=42, n_jobs=1), func=np.log1p, inverse_func=np.expm1, check_inverse=False)
    if name == "ExtraTrees_YeoJohnson":
        return TransformedTargetRegressor(regressor=ExtraTreesRegressor(n_estimators=300, min_samples_leaf=2, random_state=42, n_jobs=1), transformer=PowerTransformer(method="yeo-johnson", standardize=True))
    if name == "HistGB_absolute_raw":
        return HistGradientBoostingRegressor(loss="absolute_error", learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=20, random_state=42)
    if name == "GradientBoosting_huber_raw":
        return GradientBoostingRegressor(loss="huber", n_estimators=250, learning_rate=0.03, max_depth=2, min_samples_leaf=8, random_state=42)
    raise ValueError(name)


def evaluate(df, name):
    x = augmented_features(df); y = df[stage_a.TARGET].to_numpy(float); groups = df[stage_a.GROUP].astype(str).to_numpy()
    splitter = GroupKFold(n_splits=5); oof = np.full(len(df), np.nan); folds = []
    for fold, (tr, va) in enumerate(splitter.split(x, y, groups), 1):
        if set(groups[tr]).intersection(groups[va]): raise RuntimeError("Molecular leakage")
        pipe = Pipeline([("preprocess", stage_a.preprocessor(x.columns.tolist())), ("model", estimator(name))])
        pipe.fit(x.iloc[tr], y[tr]); pred = np.maximum(pipe.predict(x.iloc[va]), 0)
        oof[va] = pred; folds.append({"Model": name, "Fold": fold, "n": len(va), **metric(y[va], pred)})
    return metric(y, oof), pd.DataFrame(folds), pd.DataFrame({"Model": name, "Record_ID": df.Record_ID, "Canonical_Molecular_ID": groups, "actual": y, "predicted": oof})


def main():
    out = ROOT / "outputs"; out.mkdir(exist_ok=True)
    df = pd.read_csv(REPO / "stageA" / "input" / "cookchem_molecular_retention_preprocessed.csv")
    if len(df) != 1124 or df[stage_a.GROUP].nunique() != 197: raise ValueError("Dataset lock failed")
    rows=[]; folds=[]; oofs=[]
    for name in ["ExtraTrees_log1p", "ExtraTrees_YeoJohnson", "HistGB_absolute_raw", "GradientBoosting_huber_raw"]:
        overall, fold, oof = evaluate(df, name); rows.append({"Model": name, **overall}); folds.append(fold); oofs.append(oof)
    results=pd.DataFrame(rows); ref=results.iloc[0]
    for col in ["MAE","RMSE","R2"]: results[f"Delta_{col}"]=results[col]-ref[col]
    results.to_csv(out / "stageB_step3_tail_aware_results.csv", index=False)
    pd.concat(folds).to_csv(out / "stageB_step3_fold_results.csv", index=False)
    pd.concat(oofs).to_csv(out / "stageB_step3_oof_predictions.csv", index=False)
    print(results.to_string(index=False))

if __name__ == "__main__": main()
