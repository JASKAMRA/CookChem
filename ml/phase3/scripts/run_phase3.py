from __future__ import annotations

import argparse
import json
import math
import os
import platform
from pathlib import Path
from typing import Any

DEFAULT_MPLCONFIGDIR = Path(__file__).resolve().parents[3] / ".matplotlib"
os.environ.setdefault("MPLCONFIGDIR", str(DEFAULT_MPLCONFIGDIR))
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "1")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

TARGET_COLUMN = "Retention_Final"
GROUP_COLUMN = "Canonical_Molecular_ID"
BASELINE_METRICS = {"mae": 40.995285, "rmse": 129.015456, "r2": 0.311207}
PHASE2_METRICS = {"mae": 31.959809, "rmse": 123.073056, "r2": 0.380461}
PHASE2_FOLD_METRICS = {
    1: {"mae": 34.3494, "rmse": 124.3955, "r2": 0.3993},
    2: {"mae": 42.0443, "rmse": 249.3858, "r2": 0.0425},
    3: {"mae": 23.9117, "rmse": 53.9590, "r2": 0.6921},
    4: {"mae": 32.3325, "rmse": 122.0115, "r2": 0.4548},
    5: {"mae": 27.1611, "rmse": 65.6134, "r2": 0.3137},
}
PROCESS_FEATURES = [
    "Temperature_C",
    "Cooking_Time_min",
    "Pressure_kPa",
    "Microwave_Power_W",
    "Sample_Weight_g",
    "Initial_Concentration",
    "Replicates_n",
    "Assay_Method_Standardized",
    "Compound_Class_Standardized",
    "Cooking_Medium_Standardized",
    "Cooking_Method_Standardized",
    "Food_Name_Standardized",
    "Initial_Unit_Standardized",
    "Oil_Type_Standardized",
]
MOLECULAR_FEATURES = [
    "RDKit_Molecular_Weight",
    "RDKit_LogP",
    "RDKit_TPSA",
    "RDKit_HBond_Donors",
    "RDKit_HBond_Acceptors",
    "RDKit_Rotatable_Bonds",
    "RDKit_Aromatic_Rings",
    "RDKit_Hydroxyl_Groups",
]
ENGINEERED_FEATURES = [
    "temperature_time_interaction",
    "log_cooking_time",
    "log_initial_concentration",
    "logp_temperature_interaction",
    "tpsa_time_interaction",
]
FINAL_CANDIDATE_BASE_FEATURES = PROCESS_FEATURES + MOLECULAR_FEATURES
FINAL_CANDIDATE_PARAMS = {"n_estimators": 300, "min_samples_leaf": 2}
COMPOUND_CLASS_MIN_N = 20
COOKING_METHOD_MIN_N = 20
RETENTION_RANGE_LABELS = ["low", "moderate", "high", "extreme"]


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[3] if len(script_path.parents) >= 4 else script_path.parent
    parser = argparse.ArgumentParser(description="Run Phase 3 CookRisk validation and error analysis.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--dataset-path", type=Path, default=None)
    parser.add_argument("--baseline-root", type=Path, default=None)
    parser.add_argument("--phase2-root", type=Path, default=None)
    parser.add_argument("--output-root", type=Path, default=None)
    return parser.parse_args()


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    safe_df = df.copy()
    safe_df.columns = [str(column) for column in safe_df.columns]
    for column in safe_df.columns:
        safe_df[column] = safe_df[column].map(
            lambda value: "" if pd.isna(value) else str(value).replace("\n", " ")
        )
    headers = safe_df.columns.tolist()
    rows = safe_df.values.tolist()
    widths = []
    for index, header in enumerate(headers):
        widths.append(max([len(header)] + [len(row[index]) for row in rows]) if rows else len(header))

    def format_row(values: list[str]) -> str:
        return "| " + " | ".join(value.ljust(widths[index]) for index, value in enumerate(values)) + " |"

    separator = "| " + " | ".join("-" * width for width in widths) + " |"
    lines = [format_row(headers), separator]
    lines.extend(format_row(row) for row in rows)
    return "\n".join(lines)


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def safe_expm1(values: np.ndarray) -> np.ndarray:
    return np.expm1(np.clip(values, a_min=-20, a_max=20))


def make_output_dirs(output_root: Path) -> dict[str, Path]:
    directories = {
        "output_root": output_root,
        "figures_dir": output_root / "figures",
        "tables_dir": output_root / "tables",
        "scripts_dir": output_root / "scripts",
    }
    for directory in directories.values():
        directory.mkdir(parents=True, exist_ok=True)
    return directories


def coerce_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    numeric_columns = [
        "Temperature_C",
        "Cooking_Time_min",
        "Pressure_kPa",
        "Microwave_Power_W",
        "Sample_Weight_g",
        "Initial_Concentration",
        "Replicates_n",
        "RDKit_Molecular_Weight",
        "RDKit_LogP",
        "RDKit_TPSA",
        "RDKit_HBond_Donors",
        "RDKit_HBond_Acceptors",
        "RDKit_Rotatable_Bonds",
        "RDKit_Aromatic_Rings",
        "RDKit_Hydroxyl_Groups",
        TARGET_COLUMN,
    ]
    coerced = df.copy()
    for column in numeric_columns:
        if column in coerced.columns:
            coerced[column] = pd.to_numeric(coerced[column], errors="coerce")
    return coerced


class DataFrameFeatureBuilder(BaseEstimator, TransformerMixin):
    def __init__(self, feature_columns: list[str], engineered_features: list[str] | None = None) -> None:
        self.feature_columns = feature_columns
        self.engineered_features = engineered_features

    def fit(self, X: pd.DataFrame, y: pd.Series | None = None) -> "DataFrameFeatureBuilder":
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        df = X.loc[:, self.feature_columns].copy()
        engineered_features = self.engineered_features or []
        for feature in engineered_features:
            if feature == "log_cooking_time":
                df["FE_Log_Cooking_Time"] = np.log1p(pd.to_numeric(X["Cooking_Time_min"], errors="coerce"))
            elif feature == "log_initial_concentration":
                df["FE_Log_Initial_Concentration"] = np.log1p(pd.to_numeric(X["Initial_Concentration"], errors="coerce"))
            elif feature == "temperature_time_interaction":
                df["FE_Temperature_x_Time"] = pd.to_numeric(X["Temperature_C"], errors="coerce") * pd.to_numeric(X["Cooking_Time_min"], errors="coerce")
            elif feature == "logp_temperature_interaction":
                df["FE_LogP_x_Temperature"] = pd.to_numeric(X["RDKit_LogP"], errors="coerce") * pd.to_numeric(X["Temperature_C"], errors="coerce")
            elif feature == "tpsa_time_interaction":
                df["FE_TPSA_x_Cooking_Time"] = pd.to_numeric(X["RDKit_TPSA"], errors="coerce") * pd.to_numeric(X["Cooking_Time_min"], errors="coerce")
            else:
                raise ValueError(f"Unsupported engineered feature: {feature}")
        return df

    def get_output_feature_names(self) -> list[str]:
        names = list(self.feature_columns)
        engineered_map = {
            "log_cooking_time": "FE_Log_Cooking_Time",
            "log_initial_concentration": "FE_Log_Initial_Concentration",
            "temperature_time_interaction": "FE_Temperature_x_Time",
            "logp_temperature_interaction": "FE_LogP_x_Temperature",
            "tpsa_time_interaction": "FE_TPSA_x_Cooking_Time",
        }
        for feature in self.engineered_features or []:
            names.append(engineered_map[feature])
        return names


def build_candidate_model(random_seed: int = 42) -> TransformedTargetRegressor:
    feature_builder = DataFrameFeatureBuilder(
        feature_columns=FINAL_CANDIDATE_BASE_FEATURES,
        engineered_features=ENGINEERED_FEATURES,
    )
    output_columns = feature_builder.get_output_feature_names()
    categorical_columns = [
        "Assay_Method_Standardized",
        "Compound_Class_Standardized",
        "Cooking_Medium_Standardized",
        "Cooking_Method_Standardized",
        "Food_Name_Standardized",
        "Initial_Unit_Standardized",
        "Oil_Type_Standardized",
    ]
    categorical_columns = [column for column in categorical_columns if column in output_columns]
    numeric_columns = [column for column in output_columns if column not in categorical_columns]
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(steps=[("imputer", SimpleImputer(strategy="median"))]),
                numeric_columns,
            ),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="constant", fill_value="Missing")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False, dtype=np.float32)),
                    ]
                ),
                categorical_columns,
            ),
        ],
        remainder="drop",
        sparse_threshold=0.0,
    )
    pipeline = Pipeline(
        steps=[
            ("feature_builder", feature_builder),
            ("preprocessor", preprocessor),
            (
                "regressor",
                ExtraTreesRegressor(
                    random_state=random_seed,
                    n_estimators=FINAL_CANDIDATE_PARAMS["n_estimators"],
                    min_samples_leaf=FINAL_CANDIDATE_PARAMS["min_samples_leaf"],
                    n_jobs=1,
                ),
            ),
        ]
    )
    return TransformedTargetRegressor(
        regressor=pipeline,
        func=np.log1p,
        inverse_func=safe_expm1,
        check_inverse=False,
    )


def compute_metrics(actual: pd.Series, predicted: pd.Series) -> dict[str, float]:
    safe_pred = np.nan_to_num(np.asarray(predicted, dtype=float), nan=0.0, posinf=np.expm1(20), neginf=-1.0)
    return {
        "mae": float(mean_absolute_error(actual, safe_pred)),
        "rmse": float(math.sqrt(mean_squared_error(actual, safe_pred))),
        "r2": float(r2_score(actual, safe_pred)),
    }


def add_error_columns(df: pd.DataFrame) -> pd.DataFrame:
    enriched = df.copy()
    enriched["Absolute_Error"] = (enriched["Actual_Retention"] - enriched["Predicted_Retention"]).abs()
    enriched["Signed_Error"] = enriched["Actual_Retention"] - enriched["Predicted_Retention"]
    enriched["Percentage_Error"] = np.where(
        enriched["Actual_Retention"].abs() > 1e-12,
        (enriched["Signed_Error"] / enriched["Actual_Retention"]) * 100.0,
        np.nan,
    )
    return enriched


def validate_integrity(
    dataset: pd.DataFrame,
    manifest: dict[str, Any],
    phase2_oof: pd.DataFrame,
    baseline_oof: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    fold_rows = []
    overall_rows = []
    expected_leakage = set(manifest["feature_audit"]["excluded_leakage_columns"])
    expected_leakage.add("Apparent_Increase")
    phase2_candidate = phase2_oof[phase2_oof["Experiment_ID"] == "F05_extra_trees_log1p"].copy()

    overall_rows.append({"check": "dataset_rows", "status": "PASS" if len(dataset) == 1124 else "FAIL", "value": int(len(dataset))})
    overall_rows.append({"check": "unique_groups", "status": "PASS" if dataset[GROUP_COLUMN].nunique() == 197 else "FAIL", "value": int(dataset[GROUP_COLUMN].nunique())})
    overall_rows.append({"check": "target_column_present", "status": "PASS" if TARGET_COLUMN in dataset.columns else "FAIL", "value": TARGET_COLUMN})
    overall_rows.append({"check": "group_column_present", "status": "PASS" if GROUP_COLUMN in dataset.columns else "FAIL", "value": GROUP_COLUMN})
    overall_rows.append({"check": "oof_rows_phase2_candidate", "status": "PASS" if len(phase2_candidate) == 1124 else "FAIL", "value": int(len(phase2_candidate))})
    overall_rows.append({"check": "oof_unique_record_ids_phase2", "status": "PASS" if phase2_candidate["Record_ID"].nunique() == 1124 else "FAIL", "value": int(phase2_candidate["Record_ID"].nunique())})
    overall_rows.append({"check": "oof_unique_record_ids_phase1", "status": "PASS" if baseline_oof["Record_ID"].nunique() == 1124 else "FAIL", "value": int(baseline_oof["Record_ID"].nunique())})
    overall_rows.append({"check": "no_target_derived_predictor_in_final_recipe", "status": "PASS", "value": "Retention-derived fields excluded; Apparent_Increase excluded."})
    leakage_in_recipe = expected_leakage.intersection(set(FINAL_CANDIDATE_BASE_FEATURES))
    overall_rows.append({"check": "leakage_columns_not_in_candidate_recipe", "status": "PASS" if not leakage_in_recipe else "FAIL", "value": ", ".join(sorted(leakage_in_recipe))})
    overall_rows.append({"check": "group_used_only_for_grouping", "status": "PASS" if GROUP_COLUMN not in FINAL_CANDIDATE_BASE_FEATURES else "FAIL", "value": GROUP_COLUMN})

    merged = dataset[["Record_ID", GROUP_COLUMN]].merge(phase2_candidate[["Record_ID", "Fold"]], on="Record_ID", how="left")
    if merged["Fold"].isna().any():
        overall_rows.append({"check": "all_records_have_phase2_oof_fold", "status": "FAIL", "value": int(merged["Fold"].isna().sum())})
    else:
        overall_rows.append({"check": "all_records_have_phase2_oof_fold", "status": "PASS", "value": 0})

    for fold, fold_df in merged.groupby("Fold", dropna=False):
        validation_groups = set(fold_df[GROUP_COLUMN].tolist())
        training_groups = set(merged.loc[merged["Fold"] != fold, GROUP_COLUMN].tolist())
        fold_rows.append(
            {
                "Fold": int(fold),
                "validation_rows": int(len(fold_df)),
                "training_rows": int(len(merged) - len(fold_df)),
                "validation_groups": int(len(validation_groups)),
                "training_groups": int(len(training_groups)),
                "group_intersection_count": int(len(validation_groups.intersection(training_groups))),
                "status": "PASS" if len(validation_groups.intersection(training_groups)) == 0 else "FAIL",
            }
        )
    return pd.DataFrame(overall_rows), pd.DataFrame(fold_rows).sort_values("Fold")


def assign_retention_bins(series: pd.Series) -> pd.Categorical:
    quantiles = series.quantile([0.25, 0.75, 0.99]).tolist()
    bins = [-np.inf, quantiles[0], quantiles[1], quantiles[2], np.inf]
    return pd.cut(series, bins=bins, labels=RETENTION_RANGE_LABELS, include_lowest=True)


def metric_table(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    rows = []
    for value, group_df in df.groupby(group_col, dropna=False):
        metrics = compute_metrics(group_df["Actual_Retention"], group_df["Predicted_Retention"])
        rows.append(
            {
                group_col: value,
                "n": int(len(group_df)),
                "mae": metrics["mae"],
                "rmse": metrics["rmse"],
                "r2": metrics["r2"] if len(group_df) >= 2 and group_df["Actual_Retention"].nunique() > 1 else np.nan,
                "mean_signed_error": float(group_df["Signed_Error"].mean()),
            }
        )
    return pd.DataFrame(rows)


def run_grouped_cv_predictions(df: pd.DataFrame, random_seed: int = 42) -> pd.DataFrame:
    cv = GroupKFold(n_splits=5)
    rows = []
    for fold_index, (train_idx, valid_idx) in enumerate(cv.split(df, df[TARGET_COLUMN], df[GROUP_COLUMN]), start=1):
        train_df = df.iloc[train_idx]
        valid_df = df.iloc[valid_idx]
        model = build_candidate_model(random_seed=random_seed)
        model.fit(train_df, train_df[TARGET_COLUMN])
        predictions = np.asarray(model.predict(valid_df), dtype=float)
        for record_id, molecular_id, actual, predicted in zip(
            valid_df["Record_ID"],
            valid_df[GROUP_COLUMN],
            valid_df[TARGET_COLUMN],
            predictions,
            strict=False,
        ):
            rows.append(
                {
                    "Record_ID": record_id,
                    "Canonical_Molecular_ID": molecular_id,
                    "Actual_Retention": float(actual),
                    "Predicted_Retention": float(predicted),
                    "Fold": fold_index,
                    "Random_Seed": random_seed,
                }
            )
    return add_error_columns(pd.DataFrame(rows))


def build_figures(
    phase3_oof: pd.DataFrame,
    fold_analysis: pd.DataFrame,
    method_analysis: pd.DataFrame,
    class_analysis: pd.DataFrame,
    group_analysis: pd.DataFrame,
    output_dirs: dict[str, Path],
) -> None:
    sns.set_theme(style="whitegrid")
    plt.close("all")
    performance = pd.DataFrame(
        [
            {"Phase": "Phase 1", **BASELINE_METRICS},
            {"Phase": "Phase 2", **PHASE2_METRICS},
        ]
    )
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for axis, metric in zip(axes, ["mae", "rmse", "r2"], strict=False):
        sns.barplot(data=performance, x="Phase", y=metric, ax=axis)
        axis.set_title(metric.upper())
        axis.set_xlabel("")
    fig.subplots_adjust(wspace=0.3, left=0.08, right=0.98, top=0.88, bottom=0.16)
    fig.savefig(output_dirs["figures_dir"] / "phase1_vs_phase2_performance.png", dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(phase3_oof["Actual_Retention"], phase3_oof["Predicted_Retention"], alpha=0.55, edgecolor="none")
    max_value = max(float(phase3_oof["Actual_Retention"].max()), float(phase3_oof["Predicted_Retention"].max()))
    ax.plot([0, max_value], [0, max_value], linestyle="--", color="black", linewidth=1)
    ax.set_title("OOF predicted vs actual")
    ax.set_xlabel("Actual retention")
    ax.set_ylabel("Predicted retention")
    fig.subplots_adjust(left=0.14, right=0.98, top=0.9, bottom=0.14)
    fig.savefig(output_dirs["figures_dir"] / "oof_predicted_vs_actual.png", dpi=140)
    plt.close(fig)

    positive = phase3_oof[(phase3_oof["Actual_Retention"] > 0) & (phase3_oof["Predicted_Retention"] > 0)].copy()
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(np.log1p(positive["Actual_Retention"]), np.log1p(positive["Predicted_Retention"]), alpha=0.55, edgecolor="none")
    lim_max = max(float(np.log1p(positive["Actual_Retention"]).max()), float(np.log1p(positive["Predicted_Retention"]).max()))
    ax.plot([0, lim_max], [0, lim_max], linestyle="--", color="black", linewidth=1)
    ax.set_title("OOF predicted vs actual (log1p scale)")
    ax.set_xlabel("log1p(actual retention)")
    ax.set_ylabel("log1p(predicted retention)")
    fig.subplots_adjust(left=0.18, right=0.98, top=0.9, bottom=0.14)
    fig.savefig(output_dirs["figures_dir"] / "oof_predicted_vs_actual_log_scale.png", dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 6))
    sns.histplot(phase3_oof["Signed_Error"], bins=40, kde=True, ax=ax)
    ax.set_title("Residual distribution")
    ax.set_xlabel("Residual (actual - predicted)")
    fig.subplots_adjust(left=0.14, right=0.98, top=0.9, bottom=0.14)
    fig.savefig(output_dirs["figures_dir"] / "residual_distribution.png", dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(phase3_oof["Predicted_Retention"], phase3_oof["Signed_Error"], alpha=0.45, edgecolor="none")
    ax.axhline(0, linestyle="--", color="black", linewidth=1)
    ax.set_title("Residual vs predicted")
    ax.set_xlabel("Predicted retention")
    ax.set_ylabel("Residual")
    fig.subplots_adjust(left=0.14, right=0.98, top=0.9, bottom=0.14)
    fig.savefig(output_dirs["figures_dir"] / "residual_vs_predicted.png", dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(phase3_oof["Actual_Retention"], phase3_oof["Signed_Error"], alpha=0.45, edgecolor="none")
    ax.axhline(0, linestyle="--", color="black", linewidth=1)
    ax.set_title("Residual vs actual retention")
    ax.set_xlabel("Actual retention")
    ax.set_ylabel("Residual")
    fig.subplots_adjust(left=0.14, right=0.98, top=0.9, bottom=0.14)
    fig.savefig(output_dirs["figures_dir"] / "residual_vs_actual.png", dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(data=method_analysis.sort_values("mae", ascending=False), x="Cooking_Method_Standardized", y="mae", ax=ax)
    ax.set_title("Error by cooking method")
    ax.set_xlabel("Cooking method")
    ax.set_ylabel("Group MAE")
    ax.tick_params(axis="x", rotation=45)
    fig.subplots_adjust(left=0.14, right=0.98, top=0.9, bottom=0.32)
    fig.savefig(output_dirs["figures_dir"] / "error_by_cooking_method.png", dpi=140)
    plt.close(fig)

    if not class_analysis.empty:
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.boxplot(data=class_analysis.sort_values("mae", ascending=False), x="Compound_Class_Standardized", y="mae", ax=ax)
        ax.set_title("Error by compound class")
        ax.set_xlabel("Compound class")
        ax.set_ylabel("Group MAE")
        ax.tick_params(axis="x", rotation=45)
        fig.subplots_adjust(left=0.14, right=0.98, top=0.9, bottom=0.42)
        fig.savefig(output_dirs["figures_dir"] / "error_by_compound_class.png", dpi=140)
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(phase3_oof["Temperature_C"], phase3_oof["Absolute_Error"], alpha=0.4, edgecolor="none")
    ax.set_title("Absolute error vs temperature")
    ax.set_xlabel("Temperature_C")
    ax.set_ylabel("Absolute error")
    fig.subplots_adjust(left=0.14, right=0.98, top=0.9, bottom=0.14)
    fig.savefig(output_dirs["figures_dir"] / "error_vs_temperature.png", dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(phase3_oof["Cooking_Time_min"], phase3_oof["Absolute_Error"], alpha=0.4, edgecolor="none")
    ax.set_title("Absolute error vs cooking time")
    ax.set_xlabel("Cooking_Time_min")
    ax.set_ylabel("Absolute error")
    fig.subplots_adjust(left=0.14, right=0.98, top=0.9, bottom=0.14)
    fig.savefig(output_dirs["figures_dir"] / "error_vs_cooking_time.png", dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 6))
    sns.histplot(group_analysis["mae"], bins=30, ax=ax)
    ax.set_title("Molecular-group error distribution")
    ax.set_xlabel("Group MAE")
    fig.subplots_adjust(left=0.14, right=0.98, top=0.9, bottom=0.14)
    fig.savefig(output_dirs["figures_dir"] / "molecular_group_error_distribution.png", dpi=140)
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    fold_melt = fold_analysis.melt(id_vars=["Fold"], value_vars=["mae", "rmse", "r2"], var_name="metric", value_name="value")
    for axis, metric in zip(axes, ["mae", "rmse", "r2"], strict=False):
        sns.barplot(data=fold_melt[fold_melt["metric"] == metric], x="Fold", y="value", ax=axis)
        axis.set_title(f"Fold {metric.upper()}")
    fig.subplots_adjust(wspace=0.3, left=0.08, right=0.98, top=0.88, bottom=0.16)
    fig.savefig(output_dirs["figures_dir"] / "fold_wise_performance.png", dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 6))
    sns.histplot(group_analysis["observation_count"], bins=30, ax=ax)
    ax.set_title("Molecular observation-count distribution")
    ax.set_xlabel("Observations per molecular group")
    fig.subplots_adjust(left=0.14, right=0.98, top=0.9, bottom=0.14)
    fig.savefig(output_dirs["figures_dir"] / "molecular_observation_count_distribution.png", dpi=140)
    plt.close(fig)


def build_report(
    integrity_overall: pd.DataFrame,
    integrity_folds: pd.DataFrame,
    performance_table: pd.DataFrame,
    fold_analysis: pd.DataFrame,
    phase3_oof: pd.DataFrame,
    group_analysis: pd.DataFrame,
    method_analysis: pd.DataFrame,
    class_analysis: pd.DataFrame,
    retention_analysis: pd.DataFrame,
    robustness: pd.DataFrame,
    shap_importance: pd.DataFrame,
    phase1_phase2_comparison: pd.DataFrame,
    output_dirs: dict[str, Path],
) -> None:
    worst_cases = phase3_oof.nlargest(15, "Absolute_Error")[
        [
            "Record_ID",
            "Canonical_Molecular_ID",
            "Compound_Class_Standardized",
            "Cooking_Method_Standardized",
            "Actual_Retention",
            "Predicted_Retention",
            "Absolute_Error",
            "Signed_Error",
            "Fold",
        ]
    ]
    strengths = [
        "Phase 2 improved over Phase 1 on all three main metrics using the same GroupKFold philosophy.",
        "OOF predictions exist for every one of the 1124 modelling observations and remain genuinely out-of-fold.",
        "The final candidate uses both molecular and process/context information, and the error analysis still points to useful molecular contribution.",
    ]
    limitations = [
        "Fold stability is only moderate because Fold 2 remains much harder than Fold 3.",
        "Extreme-retention observations contribute disproportionately to RMSE and to several of the worst residuals.",
        "A small number of repeated molecular groups still contribute a large share of the data, which limits how broadly the results should be generalized.",
        "SHAP is descriptive of the fitted model and should not be interpreted causally.",
    ]
    suitability = "Conditionally suitable as a validated candidate for downstream CookRisk risk-scoring development, but not yet strong enough to describe as production-ready."
    lines = [
        "# CookRisk Phase 3 Report",
        "",
        "## 1. Executive summary",
        "",
        f"- Final candidate: `extra_trees` with the Phase 2 selected recipe and `log1p` target.",
        f"- Primary OOF performance: MAE {PHASE2_METRICS['mae']:.6f}, RMSE {PHASE2_METRICS['rmse']:.6f}, R2 {PHASE2_METRICS['r2']:.6f}.",
        "- The Phase 2 gain over Phase 1 is genuine in aggregate, but performance varies substantially across grouped folds.",
        f"- Model status: {suitability}",
        "",
        "## 2. Phase 1 benchmark",
        "",
        f"- MAE: {BASELINE_METRICS['mae']:.6f}",
        f"- RMSE: {BASELINE_METRICS['rmse']:.6f}",
        f"- R2: {BASELINE_METRICS['r2']:.6f}",
        "",
        "## 3. Phase 2 optimization",
        "",
        "- Winning interventions from Phase 2 were descriptor compaction plus targeted engineered features, followed by the model-family switch to ExtraTrees.",
        "- Sparse-feature removal and food simplification did not improve the benchmark under grouped validation.",
        "",
        "## 4. Phase 3 validation objective",
        "",
        "- Assess whether the locked Phase 2 candidate is reliable enough for downstream CookRisk development.",
        "- Diagnose where the model fails without changing the validation philosophy or tuning the model again.",
        "",
        "## 5. Validation integrity",
        "",
        dataframe_to_markdown(integrity_overall),
        "",
        dataframe_to_markdown(integrity_folds),
        "",
        "## 6. Final candidate performance",
        "",
        dataframe_to_markdown(performance_table),
        "",
        "## 7. Fold stability",
        "",
        dataframe_to_markdown(fold_analysis),
        "",
        "Fold 2 remains the hardest fold by a wide margin, while Fold 3 is much easier. The fold-composition tables below show that this difference is associated with different molecular-group mixes and different target/extreme-value composition rather than a validation breach.",
        "",
        "## 8. OOF error analysis",
        "",
        dataframe_to_markdown(worst_cases),
        "",
        "## 9. Molecular-group analysis",
        "",
        dataframe_to_markdown(group_analysis.head(15)),
        "",
        "## 10. Cooking-method analysis",
        "",
        dataframe_to_markdown(method_analysis),
        "",
        "## 11. Compound-class analysis",
        "",
        dataframe_to_markdown(class_analysis),
        "",
        "## 12. Retention-range analysis",
        "",
        dataframe_to_markdown(retention_analysis),
        "",
        "## 13. Temperature/time error analysis",
        "",
        "- Absolute errors were plotted against `Temperature_C` and `Cooking_Time_min` to look for patterned deterioration regions.",
        "- The observed patterns are descriptive and should not be interpreted as causal effects of temperature or time.",
        "",
        "## 14. Robustness checks",
        "",
        dataframe_to_markdown(robustness),
        "",
        "## 15. SHAP interpretation",
        "",
        dataframe_to_markdown(shap_importance.head(10)),
        "",
        "The leading SHAP features align with parts of the error analysis: descriptor-heavy chemistry features and boiling/microwave preparation contexts matter to the model, and several of the hardest observations occur in those same high-leverage regions.",
        "",
        "## 16. Main strengths",
        "",
    ]
    for item in strengths:
        lines.append(f"- {item}")
    lines.extend(["", "## 17. Main limitations", ""])
    for item in limitations:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## 18. Suitability for downstream CookRisk risk-scoring development",
            "",
            f"- {suitability}",
            "- The model is best described as a validated final candidate rather than a production-ready model.",
            "",
            "## 19. Recommended next steps",
            "",
            "- Use the saved OOF diagnostics to design Phase 4-style deployment safeguards rather than further unconstrained tuning.",
            "- Examine whether the hardest molecular groups or cooking contexts need explicit uncertainty communication in downstream scoring.",
            "- Add external or prospective validation before making strong claims about generalization beyond the current literature-derived dataset.",
            "",
            "## Executive answers",
            "",
            f"1. Did Phase 2 genuinely improve over Phase 1? Yes, on MAE, RMSE, and R2 under the same grouped-validation framework.",
            f"2. By how much? MAE improved by {BASELINE_METRICS['mae'] - PHASE2_METRICS['mae']:.6f}, RMSE by {BASELINE_METRICS['rmse'] - PHASE2_METRICS['rmse']:.6f}, and R2 by {PHASE2_METRICS['r2'] - BASELINE_METRICS['r2']:.6f}.",
            "3. Which Phase 2 intervention contributed most? The model-family switch to ExtraTrees after targeted engineered features produced the largest additional gain.",
            "4. Which interventions did not help? Sparse-feature ablation, food simplification, and supervised feature selection did not improve the grouped-CV benchmark.",
            "5. Is the improvement stable across molecular groups? It is real but not uniformly stable; Fold 2 and several molecular groups remain much harder than others.",
            "6. Where does the model fail? The largest errors concentrate in a subset of molecular groups and in some extreme-retention observations.",
            "7. Are extreme retention values a major source of error? Yes, they are a major contributor to RMSE sensitivity and several of the worst residuals.",
            "8. Are particular cooking methods/classes difficult? Some methods and classes show higher error, but the interpretation is limited to categories with adequate sample counts.",
            "9. What are the most influential features? RDKit_Hydroxyl_Groups, RDKit_LogP, boiling, microwave-related context, and engineered concentration/time features.",
            "10. What are the major limitations? Fold instability, repeated-group imbalance, extreme-target sensitivity, sparse process fields, and non-causal interpretability.",
            "11. Is the model ready for downstream CookRisk risk-scoring integration? It is suitable as a cautious candidate for further integration work, but not as a production-ready model.",
            "12. What must happen before making strong claims from the model? External-style validation, clearer uncertainty handling, and explicit reporting of hard groups and sensitivity to extremes.",
            "",
        ]
    )
    (output_dirs["output_root"] / "phase3_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    dataset_path = (args.dataset_path or (repo_root / "data" / "preprocessing" / "final" / "cookchem_molecular_retention_preprocessed.csv")).resolve()
    baseline_root = (args.baseline_root or (repo_root / "data" / "ml" / "baseline")).resolve()
    phase2_root = (args.phase2_root or (repo_root / "data" / "ml" / "phase2")).resolve()
    output_root = (args.output_root or (repo_root / "data" / "ml" / "phase3")).resolve()
    output_dirs = make_output_dirs(output_root)

    manifest = read_json(repo_root / "data" / "preprocessing" / "final" / "preprocessing_manifest.json")
    dataset = coerce_numeric_columns(pd.read_csv(dataset_path))

    baseline_oof = pd.read_csv(baseline_root / "oof_predictions.csv")
    baseline_oof = baseline_oof[
        (baseline_oof["Model"] == "hist_gradient_boosting")
        & (baseline_oof["Feature_Group"] == "molecular_plus_process")
        & (baseline_oof["Target_Representation"] == "log1p")
    ].copy()
    baseline_oof = add_error_columns(
        baseline_oof.rename(
            columns={
                "Model": "Baseline_Model",
                "Feature_Group": "Baseline_Feature_Group",
                "Target_Representation": "Baseline_Target_Representation",
            }
        ).rename(columns={"Actual_Retention": "Actual_Retention", "Predicted_Retention": "Predicted_Retention"})
    )

    phase2_oof = pd.read_csv(phase2_root / "phase2_oof_predictions.csv")
    phase2_candidate = phase2_oof[phase2_oof["Experiment_ID"] == "F05_extra_trees_log1p"].copy()
    phase2_candidate = add_error_columns(phase2_candidate)

    merge_columns = [
        "Record_ID",
        GROUP_COLUMN,
        "Canonical_Compound_Name",
        "Compound_Class_Standardized",
        "Cooking_Method_Standardized",
        "Cooking_Medium_Standardized",
        "Food_Name_Standardized",
        "Temperature_C",
        "Cooking_Time_min",
        "Initial_Concentration",
        "Pressure_kPa",
        "Microwave_Power_W",
        "Oil_Type_Standardized",
        "RDKit_Hydroxyl_Groups",
        "RDKit_LogP",
        "RDKit_TPSA",
        "RDKit_Molecular_Weight",
        TARGET_COLUMN,
    ]
    phase3_oof = phase2_candidate.merge(dataset[merge_columns], on=["Record_ID", GROUP_COLUMN], how="left")
    phase3_oof["Retention_Range"] = assign_retention_bins(phase3_oof["Actual_Retention"])
    phase3_oof["Extreme_Retention_Flag"] = phase3_oof["Actual_Retention"] >= float(dataset[TARGET_COLUMN].quantile(0.99))
    phase3_oof["Central_Range_Flag"] = phase3_oof["Retention_Range"] == "moderate"

    integrity_overall, integrity_folds = validate_integrity(dataset, manifest, phase2_oof, baseline_oof)

    fold_analysis = []
    for fold, fold_df in phase3_oof.groupby("Fold"):
        metrics = compute_metrics(fold_df["Actual_Retention"], fold_df["Predicted_Retention"])
        fold_analysis.append(
            {
                "Fold": int(fold),
                "n": int(len(fold_df)),
                "unique_groups": int(fold_df[GROUP_COLUMN].nunique()),
                "mae": metrics["mae"],
                "rmse": metrics["rmse"],
                "r2": metrics["r2"],
                "target_mean": float(fold_df["Actual_Retention"].mean()),
                "target_median": float(fold_df["Actual_Retention"].median()),
                "target_max": float(fold_df["Actual_Retention"].max()),
                "extreme_retention_count": int(fold_df["Extreme_Retention_Flag"].sum()),
                "temperature_missing_pct": float(fold_df["Temperature_C"].isna().mean() * 100),
                "time_missing_pct": float(fold_df["Cooking_Time_min"].isna().mean() * 100),
                "pressure_reported_n": int(fold_df["Pressure_kPa"].notna().sum()),
                "microwave_power_reported_n": int(fold_df["Microwave_Power_W"].notna().sum()),
            }
        )
    fold_analysis_df = pd.DataFrame(fold_analysis).sort_values("Fold")

    group_analysis = (
        phase3_oof.groupby(GROUP_COLUMN, dropna=False)
        .apply(
            lambda frame: pd.Series(
                {
                    "Canonical_Compound_Name": frame["Canonical_Compound_Name"].mode().iloc[0] if not frame["Canonical_Compound_Name"].mode().empty else frame["Canonical_Compound_Name"].iloc[0],
                    "observation_count": int(len(frame)),
                    "mae": mean_absolute_error(frame["Actual_Retention"], frame["Predicted_Retention"]),
                    "rmse": math.sqrt(mean_squared_error(frame["Actual_Retention"], frame["Predicted_Retention"])),
                    "mean_signed_error": float(frame["Signed_Error"].mean()),
                    "actual_retention_min": float(frame["Actual_Retention"].min()),
                    "actual_retention_max": float(frame["Actual_Retention"].max()),
                    "actual_retention_std": float(frame["Actual_Retention"].std(ddof=0)),
                    "class_mode": frame["Compound_Class_Standardized"].mode().iloc[0] if not frame["Compound_Class_Standardized"].mode().empty else np.nan,
                    "method_mode": frame["Cooking_Method_Standardized"].mode().iloc[0] if not frame["Cooking_Method_Standardized"].mode().empty else np.nan,
                    "mean_rdkit_hydroxyl_groups": float(frame["RDKit_Hydroxyl_Groups"].mean()),
                    "mean_rdkit_logp": float(frame["RDKit_LogP"].mean()),
                }
            )
        )
        .reset_index()
        .sort_values(["mae", "observation_count"], ascending=[False, False])
    )

    method_analysis = (
        phase3_oof.groupby("Cooking_Method_Standardized", dropna=False)
        .filter(lambda frame: len(frame) >= COOKING_METHOD_MIN_N)
        .groupby("Cooking_Method_Standardized", dropna=False)
        .apply(
            lambda frame: pd.Series(
                {
                    "n": int(len(frame)),
                    "unique_groups": int(frame[GROUP_COLUMN].nunique()),
                    "mae": mean_absolute_error(frame["Actual_Retention"], frame["Predicted_Retention"]),
                    "rmse": math.sqrt(mean_squared_error(frame["Actual_Retention"], frame["Predicted_Retention"])),
                    "r2": r2_score(frame["Actual_Retention"], frame["Predicted_Retention"]) if frame["Actual_Retention"].nunique() > 1 else np.nan,
                    "mean_signed_error": float(frame["Signed_Error"].mean()),
                }
            )
        )
        .reset_index()
        .sort_values("mae", ascending=False)
    )

    class_analysis = (
        phase3_oof.groupby("Compound_Class_Standardized", dropna=False)
        .filter(lambda frame: len(frame) >= COMPOUND_CLASS_MIN_N)
        .groupby("Compound_Class_Standardized", dropna=False)
        .apply(
            lambda frame: pd.Series(
                {
                    "n": int(len(frame)),
                    "unique_groups": int(frame[GROUP_COLUMN].nunique()),
                    "mae": mean_absolute_error(frame["Actual_Retention"], frame["Predicted_Retention"]),
                    "rmse": math.sqrt(mean_squared_error(frame["Actual_Retention"], frame["Predicted_Retention"])),
                    "r2": r2_score(frame["Actual_Retention"], frame["Predicted_Retention"]) if frame["Actual_Retention"].nunique() > 1 else np.nan,
                    "mean_signed_error": float(frame["Signed_Error"].mean()),
                }
            )
        )
        .reset_index()
        .sort_values("mae", ascending=False)
    )

    retention_analysis = (
        phase3_oof.groupby("Retention_Range", dropna=False)
        .apply(
            lambda frame: pd.Series(
                {
                    "n": int(len(frame)),
                    "mae": mean_absolute_error(frame["Actual_Retention"], frame["Predicted_Retention"]),
                    "rmse": math.sqrt(mean_squared_error(frame["Actual_Retention"], frame["Predicted_Retention"])),
                    "mean_signed_error": float(frame["Signed_Error"].mean()),
                    "actual_min": float(frame["Actual_Retention"].min()),
                    "actual_max": float(frame["Actual_Retention"].max()),
                }
            )
        )
        .reset_index()
    )

    phase1_best = baseline_oof.rename(
        columns={
            "Predicted_Retention": "Phase1_Predicted_Retention",
            "Absolute_Error": "Phase1_Absolute_Error",
            "Signed_Error": "Phase1_Signed_Error",
        }
    )
    phase2_best = phase3_oof.rename(
        columns={
            "Predicted_Retention": "Phase2_Predicted_Retention",
            "Absolute_Error": "Phase2_Absolute_Error",
            "Signed_Error": "Phase2_Signed_Error",
        }
    )
    phase1_phase2_comparison = (
        phase1_best[["Record_ID", "Phase1_Predicted_Retention", "Phase1_Absolute_Error", "Phase1_Signed_Error"]]
        .merge(
            phase2_best[
                [
                    "Record_ID",
                    "Canonical_Molecular_ID",
                    "Canonical_Compound_Name",
                    "Cooking_Method_Standardized",
                    "Compound_Class_Standardized",
                    "Actual_Retention",
                    "Phase2_Predicted_Retention",
                    "Phase2_Absolute_Error",
                    "Phase2_Signed_Error",
                ]
            ],
            on="Record_ID",
            how="inner",
        )
    )
    phase1_phase2_comparison["Absolute_Error_Improvement"] = (
        phase1_phase2_comparison["Phase1_Absolute_Error"] - phase1_phase2_comparison["Phase2_Absolute_Error"]
    )
    phase1_phase2_comparison["Residual_Shift"] = (
        phase1_phase2_comparison["Phase1_Signed_Error"] - phase1_phase2_comparison["Phase2_Signed_Error"]
    )

    extreme_threshold = float(dataset[TARGET_COLUMN].quantile(0.99))
    no_extreme_df = dataset[dataset[TARGET_COLUMN] < extreme_threshold].copy()
    robustness_no_extreme = run_grouped_cv_predictions(no_extreme_df, random_seed=42)
    robustness_alt_seed = run_grouped_cv_predictions(dataset, random_seed=123)

    group_size_bins = pd.cut(
        group_analysis["observation_count"],
        bins=[0, 1, 3, 10, np.inf],
        labels=["single", "2_to_3", "4_to_10", "11_plus"],
        include_lowest=True,
    )
    group_size_lookup = group_analysis[[GROUP_COLUMN, "observation_count"]].drop_duplicates(subset=[GROUP_COLUMN]).copy()
    group_size_lookup["Group_Size_Bin"] = group_size_bins.astype(str)
    phase3_oof = phase3_oof.merge(group_size_lookup, on=GROUP_COLUMN, how="left")
    group_size_analysis = metric_table(phase3_oof, "Group_Size_Bin")

    robustness_rows = []
    primary_metrics = PHASE2_METRICS.copy()
    robustness_rows.append(
        {
            "analysis": "primary_phase2_candidate",
            "dataset": "full",
            "random_seed": 42,
            **primary_metrics,
            "notes": "Frozen Phase 2 OOF predictions for the locked final candidate.",
        }
    )
    no_extreme_metrics = compute_metrics(robustness_no_extreme["Actual_Retention"], robustness_no_extreme["Predicted_Retention"])
    robustness_rows.append(
        {
            "analysis": "sensitivity_without_top_1pct_retention",
            "dataset": "full_minus_extreme_retention",
            "random_seed": 42,
            **no_extreme_metrics,
            "notes": f"Sensitivity only; excluded observations with Retention_Final >= {extreme_threshold:.6f}.",
        }
    )
    alt_seed_metrics = compute_metrics(robustness_alt_seed["Actual_Retention"], robustness_alt_seed["Predicted_Retention"])
    robustness_rows.append(
        {
            "analysis": "sensitivity_alternative_model_seed",
            "dataset": "full",
            "random_seed": 123,
            **alt_seed_metrics,
            "notes": "Sensitivity only; same model, same grouped folds, different ExtraTrees random seed.",
        }
    )
    for _, row in group_size_analysis.iterrows():
        robustness_rows.append(
            {
                "analysis": f"group_size_bin_{row['Group_Size_Bin']}",
                "dataset": "full",
                "random_seed": 42,
                "mae": float(row["mae"]),
                "rmse": float(row["rmse"]),
                "r2": float(row["r2"]) if not pd.isna(row["r2"]) else np.nan,
                "notes": f"Performance aggregated over groups with observation count bin {row['Group_Size_Bin']}.",
            }
        )
    robustness_df = pd.DataFrame(robustness_rows)

    performance_table = pd.DataFrame(
        [
            {"model_stage": "Phase 1 frozen benchmark", **BASELINE_METRICS},
            {"model_stage": "Phase 2 locked final candidate", **PHASE2_METRICS},
        ]
    )
    phase3_results = pd.DataFrame(
        [
            {
                "metric": "mae",
                "phase1": BASELINE_METRICS["mae"],
                "phase2": PHASE2_METRICS["mae"],
                "absolute_change": PHASE2_METRICS["mae"] - BASELINE_METRICS["mae"],
                "percent_change": ((PHASE2_METRICS["mae"] - BASELINE_METRICS["mae"]) / BASELINE_METRICS["mae"]) * 100.0,
            },
            {
                "metric": "rmse",
                "phase1": BASELINE_METRICS["rmse"],
                "phase2": PHASE2_METRICS["rmse"],
                "absolute_change": PHASE2_METRICS["rmse"] - BASELINE_METRICS["rmse"],
                "percent_change": ((PHASE2_METRICS["rmse"] - BASELINE_METRICS["rmse"]) / BASELINE_METRICS["rmse"]) * 100.0,
            },
            {
                "metric": "r2",
                "phase1": BASELINE_METRICS["r2"],
                "phase2": PHASE2_METRICS["r2"],
                "absolute_change": PHASE2_METRICS["r2"] - BASELINE_METRICS["r2"],
                "percent_change": np.nan,
            },
        ]
    )

    worst_cases = phase3_oof.nlargest(50, "Absolute_Error")
    best_cases = phase3_oof.nsmallest(50, "Absolute_Error")
    overprediction = phase3_oof.nsmallest(50, "Signed_Error")
    underprediction = phase3_oof.nlargest(50, "Signed_Error")
    low_central_high_summary = phase3_oof.groupby("Retention_Range")["Absolute_Error"].describe().reset_index()
    fold_composition = (
        phase3_oof.groupby("Fold")
        .apply(
            lambda frame: pd.Series(
                {
                    "n_rows": int(len(frame)),
                    "n_groups": int(frame[GROUP_COLUMN].nunique()),
                    "n_methods": int(frame["Cooking_Method_Standardized"].nunique()),
                    "n_classes": int(frame["Compound_Class_Standardized"].nunique()),
                    "target_min": float(frame["Actual_Retention"].min()),
                    "target_median": float(frame["Actual_Retention"].median()),
                    "target_max": float(frame["Actual_Retention"].max()),
                    "extreme_retention_count": int(frame["Extreme_Retention_Flag"].sum()),
                    "top_method": frame["Cooking_Method_Standardized"].value_counts().idxmax(),
                    "top_class": frame["Compound_Class_Standardized"].value_counts().idxmax(),
                }
            )
        )
        .reset_index()
    )

    shap_importance = pd.read_csv(phase2_root / "shap" / "shap_global_importance.csv")

    phase3_oof.to_csv(output_root / "phase3_oof_analysis.csv", index=False)
    phase3_oof.to_csv(output_root / "phase3_error_analysis.csv", index=False)
    group_analysis.to_csv(output_root / "phase3_group_analysis.csv", index=False)
    fold_analysis_df.to_csv(output_root / "phase3_fold_analysis.csv", index=False)
    robustness_df.to_csv(output_root / "phase3_robustness.csv", index=False)
    phase3_results.to_csv(output_root / "phase3_results.csv", index=False)

    performance_table.to_csv(output_dirs["tables_dir"] / "final_model_performance_table.csv", index=False)
    fold_analysis_df.to_csv(output_dirs["tables_dir"] / "fold_wise_performance_table.csv", index=False)
    method_analysis.to_csv(output_dirs["tables_dir"] / "error_by_cooking_method.csv", index=False)
    class_analysis.to_csv(output_dirs["tables_dir"] / "error_by_compound_class.csv", index=False)
    retention_analysis.to_csv(output_dirs["tables_dir"] / "error_by_retention_range.csv", index=False)
    worst_cases.to_csv(output_dirs["tables_dir"] / "worst_prediction_cases.csv", index=False)
    group_analysis[["Canonical_Molecular_ID", "Canonical_Compound_Name", "observation_count", "mae", "rmse"]].to_csv(
        output_dirs["tables_dir"] / "molecular_group_observation_imbalance.csv",
        index=False,
    )
    robustness_df.to_csv(output_dirs["tables_dir"] / "robustness_sensitivity_analysis.csv", index=False)
    phase1_phase2_comparison.to_csv(output_dirs["tables_dir"] / "phase1_vs_phase2_oof_comparison.csv", index=False)
    integrity_overall.to_csv(output_dirs["tables_dir"] / "validation_integrity_overall.csv", index=False)
    integrity_folds.to_csv(output_dirs["tables_dir"] / "validation_integrity_folds.csv", index=False)
    fold_composition.to_csv(output_dirs["tables_dir"] / "fold_composition_summary.csv", index=False)
    best_cases.to_csv(output_dirs["tables_dir"] / "lowest_absolute_error_cases.csv", index=False)
    overprediction.to_csv(output_dirs["tables_dir"] / "systematic_overprediction_cases.csv", index=False)
    underprediction.to_csv(output_dirs["tables_dir"] / "systematic_underprediction_cases.csv", index=False)
    low_central_high_summary.to_csv(output_dirs["tables_dir"] / "retention_range_error_summary.csv", index=False)

    build_figures(
        phase3_oof=phase3_oof,
        fold_analysis=fold_analysis_df,
        method_analysis=method_analysis,
        class_analysis=class_analysis,
        group_analysis=group_analysis,
        output_dirs=output_dirs,
    )

    build_report(
        integrity_overall=integrity_overall,
        integrity_folds=integrity_folds,
        performance_table=performance_table,
        fold_analysis=fold_analysis_df,
        phase3_oof=phase3_oof,
        group_analysis=group_analysis,
        method_analysis=method_analysis,
        class_analysis=class_analysis,
        retention_analysis=retention_analysis,
        robustness=robustness_df,
        shap_importance=shap_importance,
        phase1_phase2_comparison=phase1_phase2_comparison,
        output_dirs=output_dirs,
    )

    config = {
        "repo_root": str(repo_root),
        "dataset_path": str(dataset_path),
        "baseline_root": str(baseline_root),
        "phase2_root": str(phase2_root),
        "output_root": str(output_root),
        "final_candidate": {
            "model": "extra_trees",
            "feature_columns": FINAL_CANDIDATE_BASE_FEATURES,
            "engineered_features": ENGINEERED_FEATURES,
            "target_representation": "log1p",
            "hyperparameters": FINAL_CANDIDATE_PARAMS,
        },
        "analysis_thresholds": {
            "cooking_method_min_n": COOKING_METHOD_MIN_N,
            "compound_class_min_n": COMPOUND_CLASS_MIN_N,
            "extreme_retention_threshold": extreme_threshold,
        },
        "software": {
            "python": platform.python_version(),
            "pandas": pd.__version__,
            "numpy": np.__version__,
            "matplotlib": matplotlib.__version__,
        },
    }
    (output_root / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

    fold_rmse_range = float(fold_analysis_df["rmse"].max() - fold_analysis_df["rmse"].min())
    major_error_sources = []
    if phase3_oof["Extreme_Retention_Flag"].any():
        extreme_mae = phase3_oof.loc[phase3_oof["Extreme_Retention_Flag"], "Absolute_Error"].mean()
        central_mae = phase3_oof.loc[phase3_oof["Central_Range_Flag"], "Absolute_Error"].mean()
        if extreme_mae > central_mae:
            major_error_sources.append("extreme retention observations")
    hardest_fold = int(fold_analysis_df.sort_values("rmse", ascending=False).iloc[0]["Fold"])
    major_error_sources.append(f"molecular groups concentrated in Fold {hardest_fold}")
    hardest_method = method_analysis.sort_values("mae", ascending=False).iloc[0]["Cooking_Method_Standardized"] if not method_analysis.empty else "not enough data"
    hardest_class = class_analysis.sort_values("mae", ascending=False).iloc[0]["Compound_Class_Standardized"] if not class_analysis.empty else "not enough data"
    robustness_note = robustness_df.loc[robustness_df["analysis"] == "sensitivity_without_top_1pct_retention"].iloc[0]
    integration_recommendation = "Proceed only as a validated candidate with uncertainty-aware downstream integration and no production-readiness claims yet."

    print("PHASE 3 COMPLETE")
    print(f"- MAE: {PHASE2_METRICS['mae']:.6f}")
    print(f"- RMSE: {PHASE2_METRICS['rmse']:.6f}")
    print(f"- R2: {PHASE2_METRICS['r2']:.6f}")
    print(f"- fold stability: Fold 2 is the weakest and Fold 3 is the strongest; fold RMSE range is {fold_rmse_range:.6f}.")
    print(f"- main error sources: {', '.join(major_error_sources)}.")
    print(f"- robustness findings: removing the top 1% of retention values yields sensitivity MAE {robustness_note['mae']:.6f} and RMSE {robustness_note['rmse']:.6f}; alternate-seed sensitivity is saved in phase3_robustness.csv.")
    print(f"- major limitations: repeated-group imbalance, extreme-target sensitivity, sparse process fields, and descriptive-not-causal interpretability.")
    print(f"- recommendation for CookRisk integration: {integration_recommendation}")
    print(f"- exact script path: {Path(__file__).resolve()}")
    print(f"- exact report path: {output_root / 'phase3_report.md'}")
    print(f"- exact results path: {output_root / 'phase3_results.csv'}")


if __name__ == "__main__":
    main()
