"""Run the independent CookRisk Stage A benchmark.

Historical Phase 1-3 artifacts are deliberately read-only inputs.  This script
recreates the locked Phase 2 feature recipe and makes every learned transform
inside each molecular GroupKFold training partition.
"""
from __future__ import annotations

import json
import math
import platform
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold, ParameterGrid
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVR
from xgboost import XGBRegressor


# The Stage A directory is the parent of this script's scripts/ directory.
ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "input" / "cookchem_molecular_retention_preprocessed.csv"
OUT = ROOT / "outputs"
SEED = 42
TARGET = "Retention_Final"
GROUP = "Canonical_Molecular_ID"

BASE_FEATURES = [
    "Temperature_C", "Cooking_Time_min", "Pressure_kPa", "Microwave_Power_W",
    "Sample_Weight_g", "Initial_Concentration", "Replicates_n",
    "Assay_Method_Standardized", "Compound_Class_Standardized",
    "Cooking_Medium_Standardized", "Cooking_Method_Standardized",
    "Food_Name_Standardized", "Initial_Unit_Standardized", "Oil_Type_Standardized",
    "RDKit_Molecular_Weight", "RDKit_LogP", "RDKit_TPSA", "RDKit_HBond_Donors",
    "RDKit_HBond_Acceptors", "RDKit_Rotatable_Bonds", "RDKit_Aromatic_Rings",
    "RDKit_Hydroxyl_Groups",
]
CATEGORICAL = {
    "Assay_Method_Standardized", "Compound_Class_Standardized",
    "Cooking_Medium_Standardized", "Cooking_Method_Standardized",
    "Food_Name_Standardized", "Initial_Unit_Standardized", "Oil_Type_Standardized",
}
ENGINEERED = [
    "temperature_time_interaction", "log_cooking_time", "log_initial_concentration",
    "logp_temperature_interaction", "tpsa_time_interaction",
]
BENCHMARK = {"MAE": 31.959809, "RMSE": 123.073056, "R2": 0.380461}


def make_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Apply only the frozen Phase 2 deterministic feature definitions."""
    x = frame.loc[:, BASE_FEATURES].copy()
    x["FE_Temperature_x_Time"] = pd.to_numeric(frame["Temperature_C"], errors="coerce") * pd.to_numeric(frame["Cooking_Time_min"], errors="coerce")
    x["FE_Log_Cooking_Time"] = np.log1p(pd.to_numeric(frame["Cooking_Time_min"], errors="coerce"))
    x["FE_Log_Initial_Concentration"] = np.log1p(pd.to_numeric(frame["Initial_Concentration"], errors="coerce"))
    x["FE_LogP_x_Temperature"] = pd.to_numeric(frame["RDKit_LogP"], errors="coerce") * pd.to_numeric(frame["Temperature_C"], errors="coerce")
    x["FE_TPSA_x_Cooking_Time"] = pd.to_numeric(frame["RDKit_TPSA"], errors="coerce") * pd.to_numeric(frame["Cooking_Time_min"], errors="coerce")
    return x


def preprocessor(columns: list[str]) -> ColumnTransformer:
    cats = [col for col in columns if col in CATEGORICAL]
    nums = [col for col in columns if col not in cats]
    return ColumnTransformer([
        ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), nums),
        ("cat", Pipeline([("imputer", SimpleImputer(strategy="constant", fill_value="Missing")), ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]), cats),
    ], sparse_threshold=0.0)


def model_factory(name: str, params: dict, seed: int = SEED):
    if name == "ExtraTrees_reference":
        return ExtraTreesRegressor(n_estimators=300, min_samples_leaf=2, random_state=seed, n_jobs=1)
    if name == "RandomForest":
        return RandomForestRegressor(n_estimators=300, min_samples_leaf=2, random_state=seed, n_jobs=1)
    if name == "RBF_SVR":
        return SVR(kernel="rbf", C=params.get("C", 10.0), epsilon=params.get("epsilon", 0.1), gamma=params.get("gamma", "scale"))
    if name in {"XGBoost", "XGBoost_tuned"}:
        return XGBRegressor(
            objective="reg:squarederror", n_estimators=params.get("n_estimators", 300),
            max_depth=params.get("max_depth", 3), learning_rate=params.get("learning_rate", 0.03),
            min_child_weight=params.get("min_child_weight", 5), subsample=params.get("subsample", 0.8),
            colsample_bytree=params.get("colsample_bytree", 0.8), reg_lambda=params.get("reg_lambda", 5.0),
            random_state=seed, n_jobs=1, tree_method="hist", verbosity=0,
        )
    raise ValueError(f"Unsupported model: {name}")


def metrics(actual: np.ndarray, predicted: np.ndarray) -> dict[str, float]:
    return {
        "MAE": float(mean_absolute_error(actual, predicted)),
        "RMSE": float(math.sqrt(mean_squared_error(actual, predicted))),
        "R2": float(r2_score(actual, predicted)),
    }


def evaluate(df: pd.DataFrame, name: str, params: dict | None = None, seed: int = SEED, tuning: bool = False):
    params = params or {}
    x = make_features(df)
    y = pd.to_numeric(df[TARGET], errors="raise").to_numpy(float)
    groups = df[GROUP].astype(str).to_numpy()
    splitter = GroupKFold(n_splits=5)
    oof = np.full(len(df), np.nan)
    folds, audit = [], []
    for fold, (train_idx, valid_idx) in enumerate(splitter.split(x, y, groups), 1):
        train_groups, valid_groups = set(groups[train_idx]), set(groups[valid_idx])
        overlap = train_groups.intersection(valid_groups)
        if overlap:
            raise RuntimeError(f"Group leakage in fold {fold}: {sorted(overlap)[:3]}")
        estimator = model_factory(name, params, seed)
        pipe = Pipeline([("preprocess", preprocessor(x.columns.tolist())), ("model", estimator)])
        pipe.fit(x.iloc[train_idx], np.log1p(y[train_idx]))
        pred = np.expm1(np.clip(pipe.predict(x.iloc[valid_idx]), -20, 20))
        oof[valid_idx] = pred
        fold_metric = metrics(y[valid_idx], pred)
        folds.append({"Model": name, "Fold": fold, "MAE": fold_metric["MAE"], "RMSE": fold_metric["RMSE"], "R2": fold_metric["R2"], "sample_count": len(valid_idx), "parameters": json.dumps(params, sort_keys=True), "tuning": tuning})
        audit.append({"Model": name, "Fold": fold, "train_rows": len(train_idx), "validation_rows": len(valid_idx), "train_groups": len(train_groups), "validation_groups": len(valid_groups), "group_intersection_count": len(overlap)})
    if np.isnan(oof).any():
        raise RuntimeError("OOF predictions are incomplete")
    total = metrics(y, oof)
    fold_df = pd.DataFrame(folds)
    summary = {"Model": name, **total, "Fold_R2_Mean": float(fold_df.R2.mean()), "Fold_R2_STD": float(fold_df.R2.std(ddof=1)), "Fold_MAE_Mean": float(fold_df.MAE.mean()), "Fold_MAE_STD": float(fold_df.MAE.std(ddof=1)), "Fold_RMSE_Mean": float(fold_df.RMSE.mean()), "Fold_RMSE_STD": float(fold_df.RMSE.std(ddof=1)), "parameters": json.dumps(params, sort_keys=True), "tuning": tuning}
    oof_df = pd.DataFrame({"Model": name, "Record_ID": df["Record_ID"].astype(str), GROUP: groups, "actual": y, "predicted": oof, "fold": np.nan, "tuning": tuning})
    for row in folds:
        fold = int(row["Fold"])
        valid_idx = list(splitter.split(x, y, groups))[fold - 1][1]
        oof_df.loc[valid_idx, "fold"] = fold
    return summary, fold_df, oof_df, pd.DataFrame(audit)


def choose_tuned_xgb(df: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    """Use only outer-training data for each selection record; final OOF remains untouched."""
    grid = list(ParameterGrid({"n_estimators": [250, 450], "max_depth": [2, 3], "learning_rate": [0.03], "min_child_weight": [3, 8], "subsample": [0.8], "colsample_bytree": [0.8], "reg_lambda": [5.0]}))
    x = make_features(df)
    y = df[TARGET].to_numpy(float)
    groups = df[GROUP].astype(str).to_numpy()
    outer = GroupKFold(n_splits=5)
    chosen, logs = [], []
    for outer_fold, (train_idx, _) in enumerate(outer.split(x, y, groups), 1):
        inner = GroupKFold(n_splits=3)
        entries = []
        for params in grid:
            scores = []
            for inner_train, inner_valid in inner.split(x.iloc[train_idx], y[train_idx], groups[train_idx]):
                tr = train_idx[inner_train]; va = train_idx[inner_valid]
                pipe = Pipeline([("preprocess", preprocessor(x.columns.tolist())), ("model", model_factory("XGBoost", params))])
                pipe.fit(x.iloc[tr], np.log1p(y[tr]))
                pred = np.expm1(np.clip(pipe.predict(x.iloc[va]), -20, 20))
                scores.append(metrics(y[va], pred))
            entry = {"outer_fold": outer_fold, "parameters": json.dumps(params, sort_keys=True), "inner_MAE_mean": float(np.mean([s["MAE"] for s in scores])), "inner_RMSE_mean": float(np.mean([s["RMSE"] for s in scores])), "inner_R2_mean": float(np.mean([s["R2"] for s in scores]))}
            entries.append(entry); logs.append(entry)
        winner = sorted(entries, key=lambda row: (row["inner_RMSE_mean"], row["inner_MAE_mean"], -row["inner_R2_mean"]))[0]
        chosen.append(json.loads(winner["parameters"]))
    # The modal selected recipe avoids post-hoc selection over final OOF predictions.
    selected_json = pd.Series([json.dumps(p, sort_keys=True) for p in chosen]).mode().iat[0]
    return json.loads(selected_json), pd.DataFrame(logs)


def robustness(df: pd.DataFrame, name: str, params: dict, oof: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for seed in (42, 123):
        result, _, _, _ = evaluate(df, name, params, seed=seed)
        rows.append({"analysis": "seed_sensitivity", "model": name, "subset": "full", "seed": seed, **{k: result[k] for k in ("MAE", "RMSE", "R2")}, "n": len(df)})
    threshold = float(oof.actual.quantile(0.99))
    keep = oof.actual < threshold
    rows.append({"analysis": "top_1pct_exclusion_sensitivity", "model": name, "subset": f"actual < {threshold:.6f}", "seed": 42, **metrics(oof.loc[keep, "actual"], oof.loc[keep, "predicted"]), "n": int(keep.sum())})
    ranges = pd.cut(oof.actual, bins=[-np.inf, 56.8, 94.4, 512.297735, np.inf], labels=["low", "moderate", "high", "extreme"])
    for label in ranges.cat.categories:
        mask = ranges == label
        rows.append({"analysis": "retention_range", "model": name, "subset": str(label), "seed": 42, **metrics(oof.loc[mask, "actual"], oof.loc[mask, "predicted"]), "n": int(mask.sum())})
    merged = oof.merge(df[["Record_ID", "Cooking_Method_Standardized", "Compound_Class_Standardized"]], on="Record_ID", how="left")
    for column, analysis in [("Cooking_Method_Standardized", "cooking_method"), ("Compound_Class_Standardized", "compound_class")]:
        for value, subset in merged.groupby(column, dropna=False):
            if len(subset) >= 20:
                rows.append({"analysis": analysis, "model": name, "subset": str(value), "seed": 42, **metrics(subset.actual, subset.predicted), "n": len(subset)})
    return pd.DataFrame(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(INPUT)
    required = ["Record_ID", GROUP, TARGET, *BASE_FEATURES]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Input is missing required columns: {missing}")
    if df["Record_ID"].duplicated().any() or df[TARGET].isna().any():
        raise ValueError("Input Record_ID/target QA failed")
    if len(df) != 1124 or df[GROUP].nunique() != 197:
        raise ValueError("Unexpected Stage A dataset dimensions; do not benchmark a changed dataset")

    initial = [("ExtraTrees_reference", {}), ("RandomForest", {}), ("RBF_SVR", {}), ("XGBoost", {})]
    summaries, folds, oofs, audits = [], [], [], []
    for name, params in initial:
        summary, fold, oof, audit = evaluate(df, name, params)
        summaries.append(summary); folds.append(fold); oofs.append(oof); audits.append(audit)

    initial_table = pd.DataFrame(summaries).set_index("Model")
    # Tune only the boosted-tree candidate when its RMSE is not materially worse than Extra Trees.
    tuned_params, tuning_log = choose_tuned_xgb(df)
    tuned_summary, tuned_fold, tuned_oof, tuned_audit = evaluate(df, "XGBoost_tuned", tuned_params, tuning=True)
    summaries.append(tuned_summary); folds.append(tuned_fold); oofs.append(tuned_oof); audits.append(tuned_audit)

    summary_df = pd.DataFrame(summaries)
    for metric, base in [("MAE", BENCHMARK["MAE"]), ("RMSE", BENCHMARK["RMSE"]), ("R2", BENCHMARK["R2"])]:
        summary_df[f"Delta_{metric}"] = summary_df[metric] - base
    summary_df["Notes"] = summary_df["Model"].map({
        "ExtraTrees_reference": "Independent reproduction using the frozen Phase 2 recipe; historical benchmark remains authoritative.",
        "RandomForest": "Same preprocessing and grouped folds; non-boosted tree ensemble comparator.",
        "RBF_SVR": "Same preprocessing and grouped folds; nonlinear kernel comparator.",
        "XGBoost": "Untuned literature-guided gradient-boosted-tree comparator.",
        "XGBoost_tuned": "Nested 3-fold grouped tuning within each outer training fold; modal selected recipe used for final OOF evaluation.",
    })
    summary_df.to_csv(OUT / "stageA_benchmark_results.csv", index=False)
    pd.concat(folds, ignore_index=True).to_csv(OUT / "stageA_fold_results.csv", index=False)
    oof_all = pd.concat(oofs, ignore_index=True)
    if oof_all.duplicated(["Model", "Record_ID"]).any():
        raise RuntimeError("Duplicate OOF model-record predictions")
    oof_all.to_csv(OUT / "stageA_oof_predictions.csv", index=False)
    pd.concat(audits, ignore_index=True).to_csv(OUT / "stageA_validation_audit.csv", index=False)
    tuning_log.to_csv(OUT / "stageA_tuning_results.csv", index=False)

    best = summary_df.sort_values(["RMSE", "MAE", "R2"], ascending=[True, True, False]).iloc[0]
    best_oof = oof_all[oof_all.Model == best.Model].copy()
    robust = robustness(df, str(best.Model).replace("_tuned", "") if best.Model == "XGBoost_tuned" else str(best.Model), tuned_params if best.Model == "XGBoost_tuned" else {}, best_oof)
    robust.to_csv(OUT / "stageA_robustness.csv", index=False)

    qa = {
        "input": str(INPUT), "rows": len(df), "unique_molecular_groups": int(df[GROUP].nunique()),
        "target": TARGET, "group_column": GROUP, "cv": "GroupKFold(n_splits=5)",
        "all_group_intersections_zero": bool((pd.concat(audits)["group_intersection_count"] == 0).all()),
        "no_duplicate_oof": True, "historical_phase2_benchmark": BENCHMARK,
        "selected_tuned_xgboost_parameters": tuned_params, "best_stageA_model_by_RMSE": str(best.Model),
        "software": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__},
    }
    (OUT / "stageA_qa.json").write_text(json.dumps(qa, indent=2), encoding="utf-8")
    print(summary_df[["Model", "MAE", "RMSE", "R2", "Delta_MAE", "Delta_RMSE", "Delta_R2"]].to_string(index=False))
    print(f"Stage A complete: {OUT}")


if __name__ == "__main__":
    main()
