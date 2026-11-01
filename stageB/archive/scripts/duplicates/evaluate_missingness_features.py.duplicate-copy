"""Stage B, step 2: evaluate information-availability and thermal features."""
from pathlib import Path
import sys
import json
import math
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
sys.path.insert(0, str(REPO / "stageA" / "scripts"))
import run_stage_a as stage_a


def metrics(y, pred):
    return {"MAE": float(mean_absolute_error(y, pred)), "RMSE": float(math.sqrt(mean_squared_error(y, pred))), "R2": float(r2_score(y, pred))}


def augmented_features(df):
    """Features use only input availability and scientifically defined process terms."""
    x = stage_a.make_features(df)
    process_columns = ["Temperature_C", "Cooking_Time_min", "Pressure_kPa", "Microwave_Power_W", "Initial_Concentration", "Sample_Weight_g", "Replicates_n"]
    for column in process_columns:
        x[f"FE_Missing_{column}"] = df[column].isna().astype(np.int8)
    temperature = pd.to_numeric(df["Temperature_C"], errors="coerce")
    time = pd.to_numeric(df["Cooking_Time_min"], errors="coerce")
    x["FE_Thermal_Exposure"] = temperature * np.log1p(time)
    x["FE_Temperature_Squared"] = temperature ** 2
    x["FE_Log_Time_Squared"] = np.log1p(time) ** 2
    x["FE_Temp_Time_Observed"] = (temperature.notna() & time.notna()).astype(np.int8)
    return x


def evaluate(df, feature_mode):
    x = stage_a.make_features(df) if feature_mode == "reference" else augmented_features(df)
    y = df[stage_a.TARGET].to_numpy(float)
    groups = df[stage_a.GROUP].astype(str).to_numpy()
    splitter = GroupKFold(n_splits=5)
    predictions = np.full(len(df), np.nan)
    folds = []
    for fold, (train, valid) in enumerate(splitter.split(x, y, groups), 1):
        if set(groups[train]).intersection(set(groups[valid])):
            raise RuntimeError("Molecular group leakage")
        model = Pipeline([("preprocess", stage_a.preprocessor(x.columns.tolist())), ("model", ExtraTreesRegressor(n_estimators=300, min_samples_leaf=2, random_state=42, n_jobs=1))])
        model.fit(x.iloc[train], np.log1p(y[train]))
        pred = np.expm1(np.clip(model.predict(x.iloc[valid]), -20, 20))
        predictions[valid] = pred
        folds.append({"feature_mode": feature_mode, "fold": fold, "n": len(valid), **metrics(y[valid], pred)})
    overall = metrics(y, predictions)
    oof = pd.DataFrame({"Record_ID": df.Record_ID, "Canonical_Molecular_ID": groups, "actual": y, "predicted": predictions, "feature_mode": feature_mode})
    return overall, pd.DataFrame(folds), oof


def main():
    out = ROOT / "outputs"; out.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(REPO / "stageA" / "input" / "cookchem_molecular_retention_preprocessed.csv")
    if len(df) != 1124 or df[stage_a.GROUP].nunique() != 197:
        raise ValueError("Dataset lock failed")
    reference, ref_folds, ref_oof = evaluate(df, "reference")
    augmented, aug_folds, aug_oof = evaluate(df, "missingness_thermal_augmented")
    results = pd.DataFrame([{"Model": "ExtraTrees_reference", **reference}, {"Model": "ExtraTrees_missingness_thermal", **augmented}])
    for metric in ("MAE", "RMSE", "R2"):
        results[f"Delta_{metric}"] = results[metric] - reference[metric]
    results.to_csv(out / "stageB_step2_missingness_feature_results.csv", index=False)
    pd.concat([ref_folds, aug_folds], ignore_index=True).to_csv(out / "stageB_step2_fold_results.csv", index=False)
    pd.concat([ref_oof, aug_oof], ignore_index=True).to_csv(out / "stageB_step2_oof_predictions.csv", index=False)
    (out / "stageB_step2_feature_manifest.json").write_text(json.dumps({"new_features": [c for c in augmented_features(df).columns if c not in stage_a.make_features(df).columns], "validation": "5-fold GroupKFold by Canonical_Molecular_ID", "target": "log1p(Retention_Final); original-scale metrics", "dataset_lock": {"rows": 1124, "groups": 197}}, indent=2), encoding="utf-8")
    print(results.to_string(index=False))


if __name__ == "__main__": main()
