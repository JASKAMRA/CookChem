from __future__ import annotations

import argparse
import json
import math
import os
import platform
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_MPLCONFIGDIR = Path(__file__).resolve().parents[3] / ".matplotlib"
os.environ.setdefault("MPLCONFIGDIR", str(DEFAULT_MPLCONFIGDIR))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.base import RegressorMixin
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

RANDOM_SEED = 42
TARGET_COLUMN = "Retention_Final"
GROUP_COLUMN = "Canonical_Molecular_ID"
ID_COLUMNS = ["Record_ID", GROUP_COLUMN]
BEST_MODEL_SORT = ["rmse_mean", "mae_mean", "r2_mean"]


@dataclass(frozen=True)
class ExperimentSpec:
    feature_group: str
    target_representation: str
    model_name: str


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[3] if len(script_path.parents) >= 4 else script_path.parent
    parser = argparse.ArgumentParser(description="Run Phase 1 CookRisk baseline modelling.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--dataset-path", type=Path, default=None)
    parser.add_argument("--output-root", type=Path, default=None)
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


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
        cell_width = max([len(header)] + [len(row[index]) for row in rows]) if rows else len(header)
        widths.append(cell_width)

    def format_row(values: list[str]) -> str:
        return "| " + " | ".join(value.ljust(widths[index]) for index, value in enumerate(values)) + " |"

    separator = "| " + " | ".join("-" * width for width in widths) + " |"
    markdown_lines = [format_row(headers), separator]
    markdown_lines.extend(format_row(row) for row in rows)
    return "\n".join(markdown_lines)


def make_output_dirs(output_root: Path) -> dict[str, Path]:
    figures_dir = output_root / "figures"
    audit_dir = output_root / "audit"
    config_dir = output_root / "config"
    for directory in [output_root, figures_dir, audit_dir, config_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    return {
        "output_root": output_root,
        "figures_dir": figures_dir,
        "audit_dir": audit_dir,
        "config_dir": config_dir,
    }


def validate_columns(df: pd.DataFrame, required_columns: list[str]) -> None:
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def build_feature_groups(df: pd.DataFrame, manifest: dict[str, Any]) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    manifest_audit = manifest["feature_audit"]
    excluded_leakage = sorted(
        set(manifest_audit["excluded_leakage_columns"] + [TARGET_COLUMN, GROUP_COLUMN, "Apparent_Increase"])
    )
    excluded_identifiers = sorted(set(manifest_audit["excluded_identifiers"]))

    process_features = [
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
    molecular_features = [
        feature for feature in manifest_audit["molecular_descriptors"] if feature in df.columns
    ]
    process_features = [feature for feature in process_features if feature in df.columns]

    feature_groups = {
        "process_only": process_features,
        "molecular_only": molecular_features,
        "molecular_plus_process": process_features + molecular_features,
    }
    exclusions = {
        "leakage": excluded_leakage,
        "identifiers": excluded_identifiers,
    }
    return feature_groups, exclusions


def coerce_model_numeric_columns(df: pd.DataFrame, feature_groups: dict[str, list[str]]) -> pd.DataFrame:
    numeric_candidates = sorted(
        set(feature_groups["molecular_only"]).union(
            {
                "Temperature_C",
                "Cooking_Time_min",
                "Pressure_kPa",
                "Microwave_Power_W",
                "Sample_Weight_g",
                "Initial_Concentration",
                "Replicates_n",
                TARGET_COLUMN,
            }
        )
    )
    coerced = df.copy()
    for column in numeric_candidates:
        if column in coerced.columns:
            coerced[column] = pd.to_numeric(coerced[column], errors="coerce")
    return coerced


def classify_columns(df: pd.DataFrame, manifest: dict[str, Any], feature_groups: dict[str, list[str]], exclusions: dict[str, list[str]]) -> pd.DataFrame:
    process_features = set(feature_groups["process_only"])
    molecular_features = set(feature_groups["molecular_only"])
    categorical_candidates = set(manifest["feature_audit"]["categorical_predictors"])
    identifiers = set(exclusions["identifiers"])
    leakage = set(exclusions["leakage"])
    audit_like = {
        "Apparent_Increase",
        "PubChem_CID",
        "PubChem_CID_Resolved",
        "Canonical_SMILES",
        "Authors",
        "Country",
        "Journal",
        "Scientific_Name",
        "Plant_Part",
        "Year",
        "Initial_Unit",
    }

    rows: list[dict[str, Any]] = []
    for column in df.columns:
        dtype = str(df[column].dtype)
        missing_count = int(df[column].isna().sum())
        non_missing_count = int(df[column].notna().sum())
        unique_non_null = int(df[column].dropna().nunique())
        if column == TARGET_COLUMN:
            role = "target"
        elif column == GROUP_COLUMN or column in identifiers:
            role = "identifier"
        elif column in leakage:
            role = "leakage"
        elif column in molecular_features:
            role = "numeric_predictor"
        elif column in process_features and column in categorical_candidates:
            role = "categorical_predictor"
        elif column in process_features:
            role = "numeric_predictor"
        elif column in audit_like:
            role = "provenance_or_review"
        else:
            role = "other"
        rows.append(
            {
                "column": column,
                "dtype": dtype,
                "role": role,
                "missing_count": missing_count,
                "missing_percentage": round((missing_count / len(df)) * 100, 4),
                "non_missing_count": non_missing_count,
                "unique_non_null_values": unique_non_null,
            }
        )
    return pd.DataFrame(rows).sort_values(["role", "missing_percentage", "column"], ascending=[True, False, True])


def build_dataset_audit(df: pd.DataFrame, feature_groups: dict[str, list[str]], manifest: dict[str, Any]) -> tuple[dict[str, Any], pd.DataFrame]:
    target = df[TARGET_COLUMN]
    group_sizes = df.groupby(GROUP_COLUMN, dropna=False).size().rename("observation_count").reset_index()
    candidate_predictors = feature_groups["molecular_plus_process"]
    candidate_missingness = (
        pd.DataFrame(
            {
                "column": candidate_predictors,
                "dtype": [str(df[column].dtype) for column in candidate_predictors],
                "missing_count": [int(df[column].isna().sum()) for column in candidate_predictors],
                "missing_percentage": [round(float(df[column].isna().mean() * 100), 4) for column in candidate_predictors],
                "non_missing_count": [int(df[column].notna().sum()) for column in candidate_predictors],
                "unique_non_null_values": [int(df[column].dropna().nunique()) for column in candidate_predictors],
            }
        )
        .sort_values(["missing_percentage", "column"], ascending=[False, True])
        .reset_index(drop=True)
    )
    incomplete_descriptors = []
    for descriptor in feature_groups["molecular_only"]:
        missing_rows = int(df[descriptor].isna().sum())
        if missing_rows > 0:
            incomplete_descriptors.append({"descriptor": descriptor, "missing_rows": missing_rows})

    incomplete_descriptor_compounds = (
        df.loc[df["RDKit_Hydroxyl_Groups"].isna(), [GROUP_COLUMN, "Canonical_Compound_Name"]]
        .drop_duplicates()
        .sort_values([GROUP_COLUMN, "Canonical_Compound_Name"])
    )

    audit = {
        "dataset_path": "data/preprocessing/final/cookchem_molecular_retention_preprocessed.csv",
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "unique_canonical_molecular_id": int(df[GROUP_COLUMN].nunique()),
        "target_missing_count": int(target.isna().sum()),
        "target_min": float(target.min()),
        "target_max": float(target.max()),
        "target_median": float(target.median()),
        "target_mean": float(target.mean()),
        "target_std": float(target.std(ddof=1)),
        "target_skewness": float(target.skew()),
        "apparent_increase_count_gt_100": int((target > 100).sum()),
        "group_size_summary": {
            "min": int(group_sizes["observation_count"].min()),
            "median": float(group_sizes["observation_count"].median()),
            "mean": float(group_sizes["observation_count"].mean()),
            "max": int(group_sizes["observation_count"].max()),
        },
        "predictors_with_extremely_high_missingness": candidate_missingness.loc[
            candidate_missingness["missing_percentage"] >= 80, "column"
        ].tolist(),
        "incomplete_molecular_descriptors": incomplete_descriptors,
        "rdkit_hydroxyl_groups_missing_rows": int(df["RDKit_Hydroxyl_Groups"].isna().sum()),
        "rdkit_hydroxyl_groups_incomplete_compounds": incomplete_descriptor_compounds.to_dict(orient="records"),
    }
    return audit, candidate_missingness


def save_audit_files(
    audit: dict[str, Any],
    candidate_missingness: pd.DataFrame,
    column_audit: pd.DataFrame,
    group_sizes: pd.DataFrame,
    output_dirs: dict[str, Path],
) -> None:
    (output_dirs["audit_dir"] / "dataset_audit.json").write_text(
        json.dumps(audit, indent=2),
        encoding="utf-8",
    )
    candidate_missingness.to_csv(output_dirs["audit_dir"] / "candidate_predictor_missingness.csv", index=False)
    column_audit.to_csv(output_dirs["audit_dir"] / "column_audit.csv", index=False)
    group_sizes.to_csv(output_dirs["audit_dir"] / "group_observation_counts.csv", index=False)


def select_cv(groups: pd.Series) -> GroupKFold:
    unique_groups = int(groups.nunique())
    n_splits = 5 if unique_groups >= 5 else unique_groups
    if n_splits < 2:
        raise ValueError("At least two unique molecular groups are required for grouped CV.")
    return GroupKFold(n_splits=n_splits)


def build_preprocessor(df: pd.DataFrame, features: list[str], for_linear_model: bool) -> tuple[ColumnTransformer, list[str], list[str]]:
    categorical_columns = [column for column in features if not pd.api.types.is_numeric_dtype(df[column])]
    numeric_columns = [column for column in features if column not in categorical_columns]

    numeric_steps: list[tuple[str, Any]] = [("imputer", SimpleImputer(strategy="median"))]
    if for_linear_model:
        numeric_steps.append(("scaler", StandardScaler()))

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="Missing")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline(steps=numeric_steps), numeric_columns),
            ("cat", categorical_pipeline, categorical_columns),
        ],
        remainder="drop",
        sparse_threshold=0.0,
    )
    return preprocessor, numeric_columns, categorical_columns


def build_estimator(model_name: str) -> RegressorMixin:
    if model_name == "dummy":
        return DummyRegressor(strategy="mean")
    if model_name == "ridge":
        return Ridge(alpha=1.0)
    if model_name == "hist_gradient_boosting":
        return HistGradientBoostingRegressor(random_state=RANDOM_SEED)
    raise ValueError(f"Unsupported model: {model_name}")


def build_model(
    df: pd.DataFrame,
    features: list[str],
    model_name: str,
    target_representation: str,
) -> tuple[RegressorMixin, list[str], list[str]]:
    preprocessor, numeric_columns, categorical_columns = build_preprocessor(
        df=df,
        features=features,
        for_linear_model=model_name == "ridge",
    )
    estimator = build_estimator(model_name=model_name)
    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("regressor", estimator),
        ]
    )
    if target_representation == "raw":
        return pipeline, numeric_columns, categorical_columns
    if target_representation == "log1p":
        transformed = TransformedTargetRegressor(
            regressor=pipeline,
            func=np.log1p,
            inverse_func=np.expm1,
            check_inverse=False,
        )
        return transformed, numeric_columns, categorical_columns
    raise ValueError(f"Unsupported target representation: {target_representation}")


def run_experiment(
    df: pd.DataFrame,
    cv: GroupKFold,
    groups: pd.Series,
    spec: ExperimentSpec,
    features: list[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    y = df[TARGET_COLUMN]
    fold_rows: list[dict[str, Any]] = []
    oof_rows: list[dict[str, Any]] = []
    fold_audit_rows: list[dict[str, Any]] = []

    for fold_index, (train_idx, validation_idx) in enumerate(cv.split(df[features], y, groups), start=1):
        train_df = df.iloc[train_idx]
        validation_df = df.iloc[validation_idx]

        train_groups = set(train_df[GROUP_COLUMN].tolist())
        validation_groups = set(validation_df[GROUP_COLUMN].tolist())
        group_intersection = sorted(train_groups.intersection(validation_groups))
        if group_intersection:
            raise RuntimeError(
                f"Grouped CV leakage detected in fold {fold_index} for {spec}: {group_intersection[:5]}"
            )

        model, numeric_columns, categorical_columns = build_model(
            df=df,
            features=features,
            model_name=spec.model_name,
            target_representation=spec.target_representation,
        )
        model.fit(train_df[features], train_df[TARGET_COLUMN])
        predictions = np.asarray(model.predict(validation_df[features]), dtype=float)

        mae = float(mean_absolute_error(validation_df[TARGET_COLUMN], predictions))
        rmse = float(math.sqrt(mean_squared_error(validation_df[TARGET_COLUMN], predictions)))
        r2 = float(r2_score(validation_df[TARGET_COLUMN], predictions))

        fold_rows.append(
            {
                "metric_level": "fold",
                "fold": fold_index,
                "model": spec.model_name,
                "feature_group": spec.feature_group,
                "target_representation": spec.target_representation,
                "mae": mae,
                "rmse": rmse,
                "r2": r2,
                "train_rows": int(len(train_df)),
                "validation_rows": int(len(validation_df)),
                "train_groups": int(len(train_groups)),
                "validation_groups": int(len(validation_groups)),
                "group_intersection_count": 0,
                "numeric_features": "|".join(numeric_columns),
                "categorical_features": "|".join(categorical_columns),
                "all_features": "|".join(features),
            }
        )
        fold_audit_rows.append(
            {
                "model": spec.model_name,
                "feature_group": spec.feature_group,
                "target_representation": spec.target_representation,
                "fold": fold_index,
                "train_rows": int(len(train_df)),
                "validation_rows": int(len(validation_df)),
                "train_groups": int(len(train_groups)),
                "validation_groups": int(len(validation_groups)),
                "group_intersection_count": 0,
            }
        )

        for record_id, molecular_id, actual, predicted in zip(
            validation_df["Record_ID"],
            validation_df[GROUP_COLUMN],
            validation_df[TARGET_COLUMN],
            predictions,
            strict=False,
        ):
            oof_rows.append(
                {
                    "Record_ID": record_id,
                    "Canonical_Molecular_ID": molecular_id,
                    "Actual_Retention": float(actual),
                    "Predicted_Retention": float(predicted),
                    "Fold": fold_index,
                    "Model": spec.model_name,
                    "Feature_Group": spec.feature_group,
                    "Target_Representation": spec.target_representation,
                }
            )

    return fold_rows, oof_rows, fold_audit_rows


def summarise_results(fold_results: pd.DataFrame) -> pd.DataFrame:
    summary = (
        fold_results.groupby(["model", "feature_group", "target_representation"], dropna=False)
        .agg(
            mae_mean=("mae", "mean"),
            mae_sd=("mae", "std"),
            rmse_mean=("rmse", "mean"),
            rmse_sd=("rmse", "std"),
            r2_mean=("r2", "mean"),
            r2_sd=("r2", "std"),
            folds=("fold", "count"),
        )
        .reset_index()
    )
    summary["metric_level"] = "summary"
    summary["fold"] = np.nan
    return summary


def build_report(
    repo_root: Path,
    dataset_audit: dict[str, Any],
    candidate_missingness: pd.DataFrame,
    column_audit: pd.DataFrame,
    fold_audit: pd.DataFrame,
    fold_results: pd.DataFrame,
    summary_results: pd.DataFrame,
    feature_groups: dict[str, list[str]],
    exclusions: dict[str, list[str]],
    output_dirs: dict[str, Path],
) -> None:
    best_row = summary_results.sort_values(["rmse_mean", "mae_mean", "r2_mean"], ascending=[True, True, False]).iloc[0]
    best_oof = pd.read_csv(output_dirs["output_root"] / "oof_predictions.csv")
    best_oof = best_oof[
        (best_oof["Model"] == best_row["model"])
        & (best_oof["Feature_Group"] == best_row["feature_group"])
        & (best_oof["Target_Representation"] == best_row["target_representation"])
    ]

    report_lines = [
        "# CookRisk Phase 1 Baseline Report",
        "",
        "## 1. Dataset used",
        "",
        "- Source dataset: `data/preprocessing/final/cookchem_molecular_retention_preprocessed.csv`",
        f"- Repository root: `{repo_root}`",
        f"- Rows: {dataset_audit['row_count']}",
        f"- Unique `Canonical_Molecular_ID`: {dataset_audit['unique_canonical_molecular_id']}",
        "",
        "## 2. Dataset statistics",
        "",
        f"- Target missingness: {dataset_audit['target_missing_count']}",
        f"- Target range: {dataset_audit['target_min']:.6f} to {dataset_audit['target_max']:.6f}",
        f"- Target median: {dataset_audit['target_median']:.6f}",
        f"- Target mean: {dataset_audit['target_mean']:.6f}",
        f"- Target standard deviation: {dataset_audit['target_std']:.6f}",
        f"- Target skewness: {dataset_audit['target_skewness']:.6f}",
        f"- Apparent increases (>100%): {dataset_audit['apparent_increase_count_gt_100']}",
        f"- Group size min/median/mean/max: {dataset_audit['group_size_summary']['min']} / {dataset_audit['group_size_summary']['median']:.2f} / {dataset_audit['group_size_summary']['mean']:.2f} / {dataset_audit['group_size_summary']['max']}",
        "",
        "### Candidate predictor missingness",
        "",
        dataframe_to_markdown(candidate_missingness),
        "",
        "## 3. Predictor groups",
        "",
    ]

    for group_name, features in feature_groups.items():
        report_lines.append(f"- `{group_name}`: {', '.join(features)}")
    report_lines.extend(
        [
            "",
            "## 4. Leakage audit",
            "",
            "- `Canonical_Molecular_ID` used only as the grouping variable and never as a predictor.",
            "- `Apparent_Increase` excluded because it is derived from the reviewed retention target.",
            f"- Explicit leakage exclusions from preprocessing manifest: {', '.join(exclusions['leakage'])}",
            f"- Identifier/provenance exclusions from X: {', '.join(exclusions['identifiers'])}",
            "",
            "## 5. Validation strategy",
            "",
            "- Cross-validation: `GroupKFold(n_splits=5)`",
            "- Grouping column: `Canonical_Molecular_ID`",
            "- Programmatic train/validation group-overlap check: PASS",
            "",
            dataframe_to_markdown(fold_audit),
            "",
            "## 6. Missing-value strategy",
            "",
            "- No rows were dropped for predictor missingness.",
            "- Numerical predictors: fold-safe median imputation within each training fold.",
            "- Categorical predictors: fold-safe constant `Missing` category, then one-hot encoding with `handle_unknown='ignore'`.",
            "- `RDKit_Hydroxyl_Groups` retained with fold-safe imputation; missing rows explicitly reported in the audit.",
            "",
            "## 7. Models",
            "",
            "- `dummy`: `DummyRegressor(strategy='mean')`",
            "- `ridge`: `Ridge(alpha=1.0)`",
            "- `hist_gradient_boosting`: `HistGradientBoostingRegressor(random_state=42)`",
            "",
            "## 8. Target representations",
            "",
            "- `raw`: modelled directly on `Retention_Final`.",
            "- `log1p`: trained on `log1p(Retention_Final)` and inverse-transformed with `expm1` before computing MAE, RMSE, and R2 on the original scale.",
            "",
            "## 9. Complete experiment matrix",
            "",
            dataframe_to_markdown(summary_results[["model", "feature_group", "target_representation", "folds"]]),
            "",
            "## 10. Fold-wise metrics",
            "",
            dataframe_to_markdown(fold_results[["model", "feature_group", "target_representation", "fold", "mae", "rmse", "r2"]]),
            "",
            "## 11. Mean +- SD metrics",
            "",
            dataframe_to_markdown(summary_results[["model", "feature_group", "target_representation", "mae_mean", "mae_sd", "rmse_mean", "rmse_sd", "r2_mean", "r2_sd"]]),
            "",
            "## 12. Best baseline",
            "",
            "- Selection rule: lowest mean RMSE on the original retention scale; ties broken by lower mean MAE, then higher mean R2.",
            f"- Best model: `{best_row['model']}`",
            f"- Feature group: `{best_row['feature_group']}`",
            f"- Target representation: `{best_row['target_representation']}`",
            f"- MAE: {best_row['mae_mean']:.6f} +- {best_row['mae_sd']:.6f}",
            f"- RMSE: {best_row['rmse_mean']:.6f} +- {best_row['rmse_sd']:.6f}",
            f"- R2: {best_row['r2_mean']:.6f} +- {best_row['r2_sd']:.6f}",
            f"- OOF rows for best baseline: {len(best_oof)}",
            "",
            "## 13. Limitations",
            "",
            "- Pressure, microwave power, and oil type remain scientifically plausible but extremely sparse, so baseline estimates for their utility remain unstable.",
            "- Food name is high-cardinality and may add variance without necessarily improving unseen-compound generalization.",
            "- Grouped validation is honest for unseen-compound performance, but repeated-compound imbalance still means a few compounds dominate the sample count.",
            "- Descriptor correlations from EDA remain exploratory; the grouped-CV baseline is the first actual predictive test.",
            "",
            "## 14. Recommendations for Phase 2",
            "",
            "- Revisit whether ultra-sparse process variables should be grouped, excluded, or re-expressed after inspecting the baseline results.",
            "- Explore feature engineering only after locking the Phase 1 benchmark and its exact leakage-safe feature lists.",
            "- Consider controlled comparisons that reduce food-cardinality burden without leaking compound identity.",
            "- Reserve SHAP, detailed error analysis, and broader model tuning for the next phase only.",
            "",
            "## Supplementary audit outputs",
            "",
            f"- Column audit: `{output_dirs['audit_dir'] / 'column_audit.csv'}`",
            f"- Candidate predictor missingness: `{output_dirs['audit_dir'] / 'candidate_predictor_missingness.csv'}`",
            f"- Group observation counts: `{output_dirs['audit_dir'] / 'group_observation_counts.csv'}`",
            f"- Dataset audit JSON: `{output_dirs['audit_dir'] / 'dataset_audit.json'}`",
            "",
            "## Predictor role audit",
            "",
            dataframe_to_markdown(column_audit),
            "",
        ]
    )
    (output_dirs["output_root"] / "baseline_report.md").write_text("\n".join(report_lines), encoding="utf-8")


def make_figures(summary_results: pd.DataFrame, best_oof: pd.DataFrame, output_dirs: dict[str, Path]) -> None:
    sns.set_theme(style="whitegrid")

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(best_oof["Actual_Retention"], best_oof["Predicted_Retention"], alpha=0.6, edgecolor="none")
    max_value = float(max(best_oof["Actual_Retention"].max(), best_oof["Predicted_Retention"].max()))
    ax.plot([0, max_value], [0, max_value], linestyle="--", color="black", linewidth=1)
    ax.set_title("Best Baseline: Predicted vs Actual")
    ax.set_xlabel("Actual retention")
    ax.set_ylabel("Predicted retention")
    fig.tight_layout()
    fig.savefig(output_dirs["figures_dir"] / "best_baseline_predicted_vs_actual.png", dpi=200)
    plt.close(fig)

    residuals = best_oof["Actual_Retention"] - best_oof["Predicted_Retention"]
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.histplot(residuals, bins=30, kde=True, ax=ax)
    ax.set_title("Best Baseline: Residual distribution")
    ax.set_xlabel("Residual (actual - predicted)")
    fig.tight_layout()
    fig.savefig(output_dirs["figures_dir"] / "best_baseline_residual_distribution.png", dpi=200)
    plt.close(fig)

    metric_plot = summary_results.melt(
        id_vars=["model", "feature_group", "target_representation"],
        value_vars=["mae_mean", "rmse_mean", "r2_mean"],
        var_name="metric",
        value_name="value",
    )
    fig, ax = plt.subplots(figsize=(12, 6))
    metric_plot["experiment"] = (
        metric_plot["model"] + " | " + metric_plot["feature_group"] + " | " + metric_plot["target_representation"]
    )
    sns.barplot(data=metric_plot, x="experiment", y="value", hue="metric", ax=ax)
    ax.set_title("Baseline model comparison")
    ax.set_xlabel("Experiment")
    ax.set_ylabel("Metric value")
    ax.tick_params(axis="x", rotation=90)
    fig.tight_layout()
    fig.savefig(output_dirs["figures_dir"] / "baseline_model_comparison.png", dpi=200)
    plt.close(fig)

    target_compare = summary_results.melt(
        id_vars=["model", "feature_group", "target_representation"],
        value_vars=["mae_mean", "rmse_mean", "r2_mean"],
        var_name="metric",
        value_name="value",
    )
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=target_compare, x="feature_group", y="value", hue="target_representation", ax=ax)
    ax.set_title("Raw vs transformed target performance")
    ax.set_xlabel("Feature group")
    ax.set_ylabel("Metric value")
    fig.tight_layout()
    fig.savefig(output_dirs["figures_dir"] / "raw_vs_transformed_target_performance.png", dpi=200)
    plt.close(fig)


def save_config(
    repo_root: Path,
    dataset_path: Path,
    output_dirs: dict[str, Path],
    feature_groups: dict[str, list[str]],
    exclusions: dict[str, list[str]],
    cv: GroupKFold,
) -> None:
    config = {
        "repo_root": str(repo_root),
        "dataset_path": str(dataset_path),
        "output_root": str(output_dirs["output_root"]),
        "random_seed": RANDOM_SEED,
        "target_column": TARGET_COLUMN,
        "group_column": GROUP_COLUMN,
        "cv_method": "GroupKFold",
        "cv_splits": cv.n_splits,
        "feature_groups": feature_groups,
        "leakage_exclusions": exclusions["leakage"],
        "identifier_exclusions": exclusions["identifiers"],
        "software": {
            "python": platform.python_version(),
            "pandas": pd.__version__,
            "numpy": np.__version__,
            "matplotlib": matplotlib.__version__,
        },
    }
    (output_dirs["config_dir"] / "baseline_config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")


def main() -> None:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    dataset_path = (args.dataset_path or (repo_root / "data" / "preprocessing" / "final" / "cookchem_molecular_retention_preprocessed.csv")).resolve()
    output_root = (args.output_root or (repo_root / "data" / "ml" / "baseline")).resolve()
    output_dirs = make_output_dirs(output_root)

    manifest_path = repo_root / "data" / "preprocessing" / "final" / "preprocessing_manifest.json"
    df = pd.read_csv(dataset_path)
    manifest = read_json(manifest_path)

    validate_columns(df, [TARGET_COLUMN, GROUP_COLUMN, "Record_ID"])
    feature_groups, exclusions = build_feature_groups(df, manifest)
    df = coerce_model_numeric_columns(df, feature_groups)
    column_audit = classify_columns(df, manifest, feature_groups, exclusions)
    dataset_audit, candidate_missingness = build_dataset_audit(df, feature_groups, manifest)
    group_sizes = df.groupby(GROUP_COLUMN, dropna=False).size().rename("observation_count").reset_index()
    save_audit_files(dataset_audit, candidate_missingness, column_audit, group_sizes, output_dirs)

    groups = df[GROUP_COLUMN]
    cv = select_cv(groups)
    save_config(repo_root, dataset_path, output_dirs, feature_groups, exclusions, cv)

    specs = [
        ExperimentSpec(feature_group=feature_group, target_representation=target_representation, model_name=model_name)
        for feature_group in ["process_only", "molecular_only", "molecular_plus_process"]
        for target_representation in ["raw", "log1p"]
        for model_name in ["dummy", "ridge", "hist_gradient_boosting"]
    ]

    all_fold_rows: list[dict[str, Any]] = []
    all_oof_rows: list[dict[str, Any]] = []
    all_fold_audit_rows: list[dict[str, Any]] = []

    for spec in specs:
        features = feature_groups[spec.feature_group]
        fold_rows, oof_rows, fold_audit_rows = run_experiment(
            df=df,
            cv=cv,
            groups=groups,
            spec=spec,
            features=features,
        )
        all_fold_rows.extend(fold_rows)
        all_oof_rows.extend(oof_rows)
        all_fold_audit_rows.extend(fold_audit_rows)

    fold_results = pd.DataFrame(all_fold_rows)
    summary_results = summarise_results(fold_results)
    results_export = pd.concat([fold_results, summary_results], ignore_index=True, sort=False)
    results_export.to_csv(output_dirs["output_root"] / "baseline_results.csv", index=False)

    oof_df = pd.DataFrame(all_oof_rows)
    oof_df.sort_values(["Model", "Feature_Group", "Target_Representation", "Fold", "Record_ID"]).to_csv(
        output_dirs["output_root"] / "oof_predictions.csv",
        index=False,
    )

    fold_audit = pd.DataFrame(all_fold_audit_rows).sort_values(
        ["model", "feature_group", "target_representation", "fold"]
    )
    fold_audit.to_csv(output_dirs["audit_dir"] / "fold_group_audit.csv", index=False)

    best_row = summary_results.sort_values(["rmse_mean", "mae_mean", "r2_mean"], ascending=[True, True, False]).iloc[0]
    best_oof = oof_df[
        (oof_df["Model"] == best_row["model"])
        & (oof_df["Feature_Group"] == best_row["feature_group"])
        & (oof_df["Target_Representation"] == best_row["target_representation"])
    ]
    make_figures(summary_results, best_oof, output_dirs)
    build_report(
        repo_root=repo_root,
        dataset_audit=dataset_audit,
        candidate_missingness=candidate_missingness,
        column_audit=column_audit,
        fold_audit=fold_audit,
        fold_results=fold_results,
        summary_results=summary_results,
        feature_groups=feature_groups,
        exclusions=exclusions,
        output_dirs=output_dirs,
    )

    print("DATASET")
    print(f"- rows: {dataset_audit['row_count']}")
    print(f"- unique molecular groups: {dataset_audit['unique_canonical_molecular_id']}")
    print(f"- target range: {dataset_audit['target_min']:.6f} to {dataset_audit['target_max']:.6f}")
    print(f"- target skewness: {dataset_audit['target_skewness']:.6f}")
    print("VALIDATION")
    print(f"- CV method: GroupKFold")
    print(f"- number of folds: {cv.n_splits}")
    print(f"- group variable: {GROUP_COLUMN}")
    print("- confirmation that no group crossed train/validation: PASS")
    print("BEST BASELINE")
    print(f"- model: {best_row['model']}")
    print(f"- feature group: {best_row['feature_group']}")
    print(f"- target representation: {best_row['target_representation']}")
    print(f"- MAE: {best_row['mae_mean']:.6f}")
    print(f"- RMSE: {best_row['rmse_mean']:.6f}")
    print(f"- R2: {best_row['r2_mean']:.6f}")
    print("Phase 1 baseline complete.")
    print(f"- exact script path: {Path(__file__).resolve()}")
    print(f"- exact results path: {output_dirs['output_root'] / 'baseline_results.csv'}")
    print(f"- exact OOF prediction path: {output_dirs['output_root'] / 'oof_predictions.csv'}")
    print(f"- exact report path: {output_dirs['output_root'] / 'baseline_report.md'}")
    print("- any unresolved issues: ultra-sparse process variables remain baseline-included and should be revisited in Phase 2.")


if __name__ == "__main__":
    main()
