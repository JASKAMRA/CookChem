from __future__ import annotations

import argparse
import gc
import itertools
import json
import math
import os
import platform
from collections import Counter
from dataclasses import dataclass
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
import shap
from sklearn.base import BaseEstimator, RegressorMixin, TransformerMixin
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.ensemble import (
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    HistGradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.feature_selection import SelectFromModel
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

RANDOM_SEED = 42
TARGET_COLUMN = "Retention_Final"
GROUP_COLUMN = "Canonical_Molecular_ID"
BASELINE_BEST = {
    "model": "hist_gradient_boosting",
    "feature_set": "molecular_plus_process",
    "target_representation": "log1p",
    "mae": 40.995285,
    "rmse": 129.015456,
    "r2": 0.311207,
}
MODEL_COMPLEXITY_RANK = {
    "ridge": 1,
    "gradient_boosting": 2,
    "hist_gradient_boosting": 2,
    "random_forest": 3,
    "extra_trees": 3,
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
    "RDKit_Heavy_Atom_Count",
]
SPARSE_FEATURES = ["Pressure_kPa", "Microwave_Power_W", "Oil_Type_Standardized"]
NUMERIC_SOURCE_COLUMNS = [
    "Temperature_C",
    "Cooking_Time_min",
    "Pressure_kPa",
    "Microwave_Power_W",
    "Sample_Weight_g",
    "Initial_Concentration",
    "Replicates_n",
    *MOLECULAR_FEATURES,
    TARGET_COLUMN,
]


@dataclass(frozen=True)
class ExperimentSpec:
    experiment_id: str
    stage: str
    feature_set_name: str
    notes: str
    feature_columns: tuple[str, ...]
    food_strategy: str
    engineered_features: tuple[str, ...]
    selection_strategy: str
    model_name: str
    target_representation: str
    hyperparameters: tuple[tuple[str, Any], ...] = ()
    tuned: bool = False
    tune_grid: tuple[tuple[str, tuple[Any, ...]], ...] = ()

    def hyperparameter_dict(self) -> dict[str, Any]:
        return dict(self.hyperparameters)

    def tune_grid_dict(self) -> dict[str, list[Any]]:
        return {key: list(values) for key, values in self.tune_grid}


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[3] if len(script_path.parents) >= 4 else script_path.parent
    parser = argparse.ArgumentParser(description="Run Phase 2 CookRisk modelling.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--dataset-path", type=Path, default=None)
    parser.add_argument("--baseline-root", type=Path, default=None)
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
    directories = {
        "output_root": output_root,
        "config_dir": output_root / "config",
        "figures_dir": output_root / "figures",
        "feature_analysis_dir": output_root / "feature_analysis",
        "shap_dir": output_root / "shap",
    }
    for directory in directories.values():
        directory.mkdir(parents=True, exist_ok=True)
    return directories


def validate_columns(df: pd.DataFrame, required_columns: list[str]) -> None:
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def safe_expm1(values: np.ndarray) -> np.ndarray:
    clipped = np.clip(values, a_min=-20, a_max=20)
    return np.expm1(clipped)


def coerce_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    coerced = df.copy()
    for column in NUMERIC_SOURCE_COLUMNS:
        if column in coerced.columns:
            coerced[column] = pd.to_numeric(coerced[column], errors="coerce")
    return coerced


def select_cv(groups: pd.Series, preferred_splits: int = 5) -> GroupKFold:
    unique_groups = int(groups.nunique())
    n_splits = min(preferred_splits, unique_groups)
    if n_splits < 2:
        raise ValueError("At least two unique molecular groups are required for grouped CV.")
    return GroupKFold(n_splits=n_splits)


def feature_columns_available(df: pd.DataFrame, columns: list[str]) -> list[str]:
    return [column for column in columns if column in df.columns]


class DataFrameFeatureBuilder(BaseEstimator, TransformerMixin):
    def __init__(
        self,
        feature_columns: list[str],
        food_strategy: str = "current",
        food_top_k: int = 20,
        engineered_features: list[str] | None = None,
    ) -> None:
        self.feature_columns = feature_columns
        self.food_strategy = food_strategy
        self.food_top_k = food_top_k
        self.engineered_features = engineered_features

    def fit(self, X: pd.DataFrame, y: pd.Series | None = None) -> "DataFrameFeatureBuilder":
        if self.food_strategy == "top_k_other" and "Food_Name_Standardized" in X.columns:
            value_counts = X["Food_Name_Standardized"].fillna("Missing").value_counts()
            self.top_food_categories_ = value_counts.head(self.food_top_k).index.tolist()
        else:
            self.top_food_categories_ = []
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        df = X.loc[:, self.feature_columns].copy()
        engineered_features = self.engineered_features or []

        if "Food_Name_Standardized" in df.columns:
            if self.food_strategy == "exclude":
                df = df.drop(columns=["Food_Name_Standardized"])
            elif self.food_strategy == "top_k_other":
                allowed = set(self.top_food_categories_)
                df["Food_Name_Standardized"] = (
                    X["Food_Name_Standardized"]
                    .fillna("Missing")
                    .map(lambda value: value if value in allowed else "Other")
                )
            else:
                df["Food_Name_Standardized"] = X["Food_Name_Standardized"].fillna("Missing")

        for engineered_feature in engineered_features:
            if engineered_feature == "log_cooking_time":
                df["FE_Log_Cooking_Time"] = np.log1p(pd.to_numeric(X["Cooking_Time_min"], errors="coerce"))
            elif engineered_feature == "log_initial_concentration":
                df["FE_Log_Initial_Concentration"] = np.log1p(
                    pd.to_numeric(X["Initial_Concentration"], errors="coerce")
                )
            elif engineered_feature == "temperature_time_interaction":
                df["FE_Temperature_x_Time"] = (
                    pd.to_numeric(X["Temperature_C"], errors="coerce")
                    * pd.to_numeric(X["Cooking_Time_min"], errors="coerce")
                )
            elif engineered_feature == "logp_temperature_interaction":
                df["FE_LogP_x_Temperature"] = (
                    pd.to_numeric(X["RDKit_LogP"], errors="coerce")
                    * pd.to_numeric(X["Temperature_C"], errors="coerce")
                )
            elif engineered_feature == "tpsa_time_interaction":
                df["FE_TPSA_x_Cooking_Time"] = (
                    pd.to_numeric(X["RDKit_TPSA"], errors="coerce")
                    * pd.to_numeric(X["Cooking_Time_min"], errors="coerce")
                )
            else:
                raise ValueError(f"Unsupported engineered feature: {engineered_feature}")
        return df

    def get_output_feature_names(self) -> list[str]:
        names = list(self.feature_columns)
        if self.food_strategy == "exclude" and "Food_Name_Standardized" in names:
            names.remove("Food_Name_Standardized")
        engineered_features = self.engineered_features or []
        engineered_map = {
            "log_cooking_time": "FE_Log_Cooking_Time",
            "log_initial_concentration": "FE_Log_Initial_Concentration",
            "temperature_time_interaction": "FE_Temperature_x_Time",
            "logp_temperature_interaction": "FE_LogP_x_Temperature",
            "tpsa_time_interaction": "FE_TPSA_x_Cooking_Time",
        }
        for engineered_feature in engineered_features:
            names.append(engineered_map[engineered_feature])
        return names


class CastToFloat32(BaseEstimator, TransformerMixin):
    def fit(self, X: Any, y: pd.Series | None = None) -> "CastToFloat32":
        return self

    def transform(self, X: Any) -> np.ndarray:
        return np.asarray(X, dtype=np.float32)


def build_preprocessor(output_columns: list[str]) -> tuple[ColumnTransformer, list[str], list[str]]:
    categorical_columns = [
        column
        for column in output_columns
        if column in {
            "Assay_Method_Standardized",
            "Compound_Class_Standardized",
            "Cooking_Medium_Standardized",
            "Cooking_Method_Standardized",
            "Food_Name_Standardized",
            "Initial_Unit_Standardized",
            "Oil_Type_Standardized",
        }
    ]
    numeric_columns = [column for column in output_columns if column not in categorical_columns]
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="Missing")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False, dtype=np.float32)),
        ]
    )
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_columns),
            ("cat", categorical_pipeline, categorical_columns),
        ],
        remainder="drop",
        sparse_threshold=0.0,
    )
    return preprocessor, numeric_columns, categorical_columns


def build_estimator(model_name: str, hyperparameters: dict[str, Any]) -> RegressorMixin:
    if model_name == "ridge":
        return Ridge(alpha=hyperparameters.get("alpha", 1.0))
    if model_name == "gradient_boosting":
        return GradientBoostingRegressor(random_state=RANDOM_SEED, **hyperparameters)
    if model_name == "hist_gradient_boosting":
        return HistGradientBoostingRegressor(random_state=RANDOM_SEED, **hyperparameters)
    if model_name == "random_forest":
        return RandomForestRegressor(random_state=RANDOM_SEED, n_jobs=1, **hyperparameters)
    if model_name == "extra_trees":
        return ExtraTreesRegressor(random_state=RANDOM_SEED, n_jobs=1, **hyperparameters)
    raise ValueError(f"Unsupported model: {model_name}")


def build_selector(selection_strategy: str) -> SelectFromModel | None:
    if selection_strategy == "none":
        return None
    if selection_strategy == "tree_importance_median":
        return SelectFromModel(
            estimator=ExtraTreesRegressor(
                n_estimators=250,
                random_state=RANDOM_SEED,
                n_jobs=1,
                min_samples_leaf=2,
            ),
            threshold="median",
        )
    raise ValueError(f"Unsupported selection strategy: {selection_strategy}")


def build_pipeline(spec: ExperimentSpec) -> tuple[RegressorMixin, DataFrameFeatureBuilder, list[str], list[str]]:
    feature_builder = DataFrameFeatureBuilder(
        feature_columns=list(spec.feature_columns),
        food_strategy=spec.food_strategy,
        food_top_k=20,
        engineered_features=list(spec.engineered_features),
    )
    output_columns = feature_builder.get_output_feature_names()
    preprocessor, numeric_columns, categorical_columns = build_preprocessor(output_columns)
    steps: list[tuple[str, Any]] = [
        ("feature_builder", feature_builder),
        ("preprocessor", preprocessor),
        ("float32", CastToFloat32()),
    ]
    selector = build_selector(spec.selection_strategy)
    if selector is not None:
        steps.append(("selector", selector))
    steps.append(("regressor", build_estimator(spec.model_name, spec.hyperparameter_dict())))
    base_pipeline = Pipeline(steps=steps)
    if spec.target_representation == "raw":
        return base_pipeline, feature_builder, numeric_columns, categorical_columns
    if spec.target_representation == "log1p":
        wrapped = TransformedTargetRegressor(
            regressor=base_pipeline,
            func=np.log1p,
            inverse_func=safe_expm1,
            check_inverse=False,
        )
        return wrapped, feature_builder, numeric_columns, categorical_columns
    raise ValueError(f"Unsupported target representation: {spec.target_representation}")


def get_fitted_pipeline(model: RegressorMixin) -> Pipeline:
    return model.regressor_ if isinstance(model, TransformedTargetRegressor) else model


def get_processed_feature_names(fitted_pipeline: Pipeline) -> list[str]:
    preprocessor = fitted_pipeline.named_steps["preprocessor"]
    feature_names = preprocessor.get_feature_names_out().tolist()
    if "selector" in fitted_pipeline.named_steps:
        selector = fitted_pipeline.named_steps["selector"]
        support = selector.get_support()
        feature_names = [name for name, keep in zip(feature_names, support, strict=False) if keep]
    return feature_names


def transform_for_shap(fitted_pipeline: Pipeline, X: pd.DataFrame) -> np.ndarray:
    built = fitted_pipeline.named_steps["feature_builder"].transform(X)
    transformed = fitted_pipeline.named_steps["preprocessor"].transform(built)
    if "selector" in fitted_pipeline.named_steps:
        transformed = fitted_pipeline.named_steps["selector"].transform(transformed)
    return transformed


def compute_metrics(actual: pd.Series, predicted: np.ndarray) -> dict[str, float]:
    safe_predicted = np.nan_to_num(predicted, nan=0.0, posinf=np.expm1(20), neginf=-1.0)
    return {
        "mae": float(mean_absolute_error(actual, safe_predicted)),
        "rmse": float(math.sqrt(mean_squared_error(actual, safe_predicted))),
        "r2": float(r2_score(actual, safe_predicted)),
    }


def metric_sort_key(row: pd.Series) -> tuple[Any, ...]:
    return (
        row["rmse_mean"],
        row["mae_mean"],
        -row["r2_mean"],
        row.get("rmse_sd", np.nan),
        row.get("mae_sd", np.nan),
        row.get("complexity_rank", 99),
    )


def expand_param_grid(grid: dict[str, list[Any]]) -> list[dict[str, Any]]:
    keys = list(grid.keys())
    values = [grid[key] for key in keys]
    return [dict(zip(keys, combination, strict=False)) for combination in itertools.product(*values)]


def evaluate_inner_cv(
    df: pd.DataFrame,
    groups: pd.Series,
    base_spec: ExperimentSpec,
    hyperparameters: dict[str, Any],
    inner_splits: int = 3,
) -> dict[str, float]:
    inner_cv = select_cv(groups, preferred_splits=inner_splits)
    rows = []
    inner_spec = ExperimentSpec(
        experiment_id=base_spec.experiment_id,
        stage=base_spec.stage,
        feature_set_name=base_spec.feature_set_name,
        notes=base_spec.notes,
        feature_columns=base_spec.feature_columns,
        food_strategy=base_spec.food_strategy,
        engineered_features=base_spec.engineered_features,
        selection_strategy=base_spec.selection_strategy,
        model_name=base_spec.model_name,
        target_representation=base_spec.target_representation,
        hyperparameters=tuple(sorted(hyperparameters.items())),
    )
    for train_idx, valid_idx in inner_cv.split(df, df[TARGET_COLUMN], groups):
        train_df = df.iloc[train_idx]
        valid_df = df.iloc[valid_idx]
        train_groups = set(train_df[GROUP_COLUMN].tolist())
        valid_groups = set(valid_df[GROUP_COLUMN].tolist())
        if train_groups.intersection(valid_groups):
            raise RuntimeError("Inner CV group leakage detected.")
        model, _, _, _ = build_pipeline(inner_spec)
        model.fit(train_df, train_df[TARGET_COLUMN])
        predicted = np.asarray(model.predict(valid_df), dtype=float)
        rows.append(compute_metrics(valid_df[TARGET_COLUMN], predicted))
        del model
        gc.collect()
    metrics_df = pd.DataFrame(rows)
    return {
        "mae_mean": float(metrics_df["mae"].mean()),
        "rmse_mean": float(metrics_df["rmse"].mean()),
        "r2_mean": float(metrics_df["r2"].mean()),
    }


def tune_hyperparameters_for_fold(
    train_df: pd.DataFrame,
    train_groups: pd.Series,
    spec: ExperimentSpec,
) -> tuple[dict[str, Any], pd.DataFrame]:
    grid = expand_param_grid(spec.tune_grid_dict())
    search_rows = []
    for hyperparameters in grid:
        metrics = evaluate_inner_cv(
            df=train_df,
            groups=train_groups,
            base_spec=spec,
            hyperparameters=hyperparameters,
        )
        search_rows.append(
            {
                "experiment_id": spec.experiment_id,
                "model": spec.model_name,
                "target_representation": spec.target_representation,
                "hyperparameters": json.dumps(hyperparameters, sort_keys=True),
                **metrics,
            }
        )
    search_df = pd.DataFrame(search_rows).sort_values(
        ["rmse_mean", "mae_mean", "r2_mean"],
        ascending=[True, True, False],
    )
    return json.loads(search_df.iloc[0]["hyperparameters"]), search_df


def run_experiment(
    df: pd.DataFrame,
    cv: GroupKFold,
    spec: ExperimentSpec,
    serious_candidate: bool = True,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    fold_rows: list[dict[str, Any]] = []
    oof_rows: list[dict[str, Any]] = []
    fold_audit_rows: list[dict[str, Any]] = []
    tuning_rows: list[dict[str, Any]] = []

    for fold_index, (train_idx, valid_idx) in enumerate(
        cv.split(df, df[TARGET_COLUMN], df[GROUP_COLUMN]),
        start=1,
    ):
        train_df = df.iloc[train_idx]
        valid_df = df.iloc[valid_idx]
        train_groups = set(train_df[GROUP_COLUMN].tolist())
        valid_groups = set(valid_df[GROUP_COLUMN].tolist())
        group_intersection = sorted(train_groups.intersection(valid_groups))
        if group_intersection:
            raise RuntimeError(f"Group leakage detected in {spec.experiment_id} fold {fold_index}.")

        fit_spec = spec
        selected_hyperparameters = spec.hyperparameter_dict()
        if spec.tuned:
            selected_hyperparameters, tuning_df = tune_hyperparameters_for_fold(
                train_df=train_df,
                train_groups=train_df[GROUP_COLUMN],
                spec=spec,
            )
            fit_spec = ExperimentSpec(
                experiment_id=spec.experiment_id,
                stage=spec.stage,
                feature_set_name=spec.feature_set_name,
                notes=spec.notes,
                feature_columns=spec.feature_columns,
                food_strategy=spec.food_strategy,
                engineered_features=spec.engineered_features,
                selection_strategy=spec.selection_strategy,
                model_name=spec.model_name,
                target_representation=spec.target_representation,
                hyperparameters=tuple(sorted(selected_hyperparameters.items())),
                tuned=spec.tuned,
                tune_grid=spec.tune_grid,
            )
            tuning_rows.extend(
                {
                    **row,
                    "outer_fold": fold_index,
                }
                for row in tuning_df.to_dict(orient="records")
            )

        model, feature_builder, numeric_columns, categorical_columns = build_pipeline(fit_spec)
        model.fit(train_df, train_df[TARGET_COLUMN])
        predicted = np.asarray(model.predict(valid_df), dtype=float)
        metrics = compute_metrics(valid_df[TARGET_COLUMN], predicted)

        fitted_pipeline = get_fitted_pipeline(model)
        processed_features = get_processed_feature_names(fitted_pipeline)

        fold_rows.append(
            {
                "metric_level": "fold",
                "experiment_id": spec.experiment_id,
                "stage": spec.stage,
                "feature_set_name": spec.feature_set_name,
                "model": spec.model_name,
                "target_representation": spec.target_representation,
                "food_strategy": spec.food_strategy,
                "selection_strategy": spec.selection_strategy,
                "engineered_features": "|".join(spec.engineered_features),
                "removed_features": "|".join(sorted(set(PROCESS_FEATURES + MOLECULAR_FEATURES) - set(spec.feature_columns))),
                "fold": fold_index,
                "mae": metrics["mae"],
                "rmse": metrics["rmse"],
                "r2": metrics["r2"],
                "train_rows": int(len(train_df)),
                "validation_rows": int(len(valid_df)),
                "train_groups": int(len(train_groups)),
                "validation_groups": int(len(valid_groups)),
                "group_intersection_count": 0,
                "feature_count_before_encoding": len(feature_builder.get_output_feature_names()),
                "feature_count_after_processing": len(processed_features),
                "hyperparameters": json.dumps(selected_hyperparameters, sort_keys=True),
                "notes": spec.notes,
            }
        )
        fold_audit_rows.append(
            {
                "experiment_id": spec.experiment_id,
                "stage": spec.stage,
                "fold": fold_index,
                "train_rows": int(len(train_df)),
                "validation_rows": int(len(valid_df)),
                "train_groups": int(len(train_groups)),
                "validation_groups": int(len(valid_groups)),
                "group_intersection_count": 0,
            }
        )

        if serious_candidate:
            for record_id, molecular_id, actual, pred in zip(
                valid_df["Record_ID"],
                valid_df[GROUP_COLUMN],
                valid_df[TARGET_COLUMN],
                predicted,
                strict=False,
            ):
                oof_rows.append(
                    {
                        "Record_ID": record_id,
                        "Canonical_Molecular_ID": molecular_id,
                        "Actual_Retention": float(actual),
                        "Predicted_Retention": float(pred),
                        "Fold": fold_index,
                        "Model": spec.model_name,
                        "Feature_Set": spec.feature_set_name,
                        "Target_Representation": spec.target_representation,
                        "Experiment_ID": spec.experiment_id,
                        "Stage": spec.stage,
                    }
                )
        del model
        gc.collect()

    return fold_rows, oof_rows, fold_audit_rows, tuning_rows


def summarise_results(fold_results: pd.DataFrame) -> pd.DataFrame:
    summary = (
        fold_results.groupby(
            [
                "experiment_id",
                "stage",
                "feature_set_name",
                "model",
                "target_representation",
                "food_strategy",
                "selection_strategy",
                "engineered_features",
                "removed_features",
                "notes",
            ],
            dropna=False,
        )
        .agg(
            mae_mean=("mae", "mean"),
            mae_sd=("mae", "std"),
            rmse_mean=("rmse", "mean"),
            rmse_sd=("rmse", "std"),
            r2_mean=("r2", "mean"),
            r2_sd=("r2", "std"),
            folds=("fold", "count"),
            avg_features_after_processing=("feature_count_after_processing", "mean"),
        )
        .reset_index()
    )
    summary["metric_level"] = "summary"
    summary["complexity_rank"] = summary["model"].map(MODEL_COMPLEXITY_RANK).fillna(99)
    return summary.sort_values(
        ["rmse_mean", "mae_mean", "r2_mean", "rmse_sd", "mae_sd", "complexity_rank"],
        ascending=[True, True, False, True, True, True],
    )


def stage_winner(summary: pd.DataFrame, stage: str) -> pd.Series:
    subset = summary[summary["stage"] == stage].copy()
    if subset.empty:
        raise ValueError(f"No summary rows found for stage {stage}.")
    return subset.sort_values(
        ["rmse_mean", "mae_mean", "r2_mean", "rmse_sd", "mae_sd", "complexity_rank"],
        ascending=[True, True, False, True, True, True],
    ).iloc[0]


def build_phase2_starting_report(
    baseline_root: Path,
    baseline_summary: pd.DataFrame,
    baseline_report_path: Path,
    phase2_feature_columns: list[str],
    dataset_missingness: pd.DataFrame,
    output_dirs: dict[str, Path],
) -> None:
    top_baseline = baseline_summary.sort_values(["rmse_mean", "mae_mean", "r2_mean"], ascending=[True, True, False])
    lines = [
        "# CookRisk Phase 2 Starting Report",
        "",
        f"- Generated from Phase 1 artifacts on {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- Baseline root: `{baseline_root}`",
        f"- Baseline report: `{baseline_report_path}`",
        "",
        "## Phase 1 benchmark",
        "",
        f"- Best model: `{BASELINE_BEST['model']}`",
        f"- Best features: `{BASELINE_BEST['feature_set']}`",
        f"- Best target: `{BASELINE_BEST['target_representation']}`",
        f"- MAE: {BASELINE_BEST['mae']:.6f}",
        f"- RMSE: {BASELINE_BEST['rmse']:.6f}",
        f"- R2: {BASELINE_BEST['r2']:.6f}",
        "",
        "## Phase 1 models tested",
        "",
        dataframe_to_markdown(top_baseline[["model", "feature_group", "target_representation", "mae_mean", "rmse_mean", "r2_mean"]]),
        "",
        "## Current predictor set entering Phase 2",
        "",
        "- `molecular_plus_process` predictor columns:",
        f"- {', '.join(phase2_feature_columns)}",
        "",
        "## Current missingness",
        "",
        dataframe_to_markdown(dataset_missingness),
        "",
        "## Current limitations carried forward from Phase 1",
        "",
        "- Sparse predictors remain unresolved: Pressure_kPa, Microwave_Power_W, Oil_Type_Standardized.",
        "- Food_Name_Standardized remains high-cardinality at 158 observed categories.",
        "- Descriptor redundancy is plausible and must be tested under grouped CV rather than assumed from correlation tables alone.",
        "- The benchmark favors log1p target modeling, but Phase 2 should still compare raw versus log1p when the feature recipe stabilizes.",
        "",
    ]
    (output_dirs["feature_analysis_dir"] / "phase2_starting_report.md").write_text("\n".join(lines), encoding="utf-8")


def save_feature_analysis(df: pd.DataFrame, output_dirs: dict[str, Path]) -> tuple[pd.DataFrame, pd.DataFrame]:
    predictor_missingness = (
        pd.DataFrame(
            {
                "column": PROCESS_FEATURES + MOLECULAR_FEATURES,
                "missing_count": [int(df[column].isna().sum()) for column in PROCESS_FEATURES + MOLECULAR_FEATURES],
                "missing_percentage": [round(float(df[column].isna().mean() * 100), 4) for column in PROCESS_FEATURES + MOLECULAR_FEATURES],
                "unique_non_null_values": [int(df[column].dropna().nunique()) for column in PROCESS_FEATURES + MOLECULAR_FEATURES],
            }
        )
        .sort_values(["missing_percentage", "column"], ascending=[False, True])
        .reset_index(drop=True)
    )
    predictor_missingness.to_csv(output_dirs["feature_analysis_dir"] / "current_predictor_missingness.csv", index=False)

    food_frequency = (
        df["Food_Name_Standardized"]
        .fillna("Missing")
        .value_counts()
        .rename_axis("Food_Name_Standardized")
        .reset_index(name="observation_count")
    )
    food_frequency.to_csv(output_dirs["feature_analysis_dir"] / "food_frequency.csv", index=False)

    descriptor_corr = df[MOLECULAR_FEATURES].corr().round(6)
    descriptor_corr.to_csv(output_dirs["feature_analysis_dir"] / "descriptor_correlation_matrix.csv")

    sparse_summary_rows = []
    for column in SPARSE_FEATURES:
        sparse_summary_rows.append(
            {
                "column": column,
                "missing_count": int(df[column].isna().sum()),
                "missing_percentage": round(float(df[column].isna().mean() * 100), 4),
                "reported_target_mean": float(df.loc[df[column].notna(), TARGET_COLUMN].mean()),
                "missing_target_mean": float(df.loc[df[column].isna(), TARGET_COLUMN].mean()),
                "reported_target_median": float(df.loc[df[column].notna(), TARGET_COLUMN].median()),
                "missing_target_median": float(df.loc[df[column].isna(), TARGET_COLUMN].median()),
            }
        )
    pd.DataFrame(sparse_summary_rows).to_csv(output_dirs["feature_analysis_dir"] / "sparse_feature_summary.csv", index=False)
    return predictor_missingness, food_frequency


def instantiate_spec(
    experiment_id: str,
    stage: str,
    feature_set_name: str,
    notes: str,
    feature_columns: list[str],
    food_strategy: str,
    engineered_features: list[str],
    selection_strategy: str,
    model_name: str,
    target_representation: str,
    hyperparameters: dict[str, Any] | None = None,
    tuned: bool = False,
    tune_grid: dict[str, list[Any]] | None = None,
) -> ExperimentSpec:
    return ExperimentSpec(
        experiment_id=experiment_id,
        stage=stage,
        feature_set_name=feature_set_name,
        notes=notes,
        feature_columns=tuple(feature_columns),
        food_strategy=food_strategy,
        engineered_features=tuple(engineered_features),
        selection_strategy=selection_strategy,
        model_name=model_name,
        target_representation=target_representation,
        hyperparameters=tuple(sorted((hyperparameters or {}).items())),
        tuned=tuned,
        tune_grid=tuple((key, tuple(values)) for key, values in sorted((tune_grid or {}).items())),
    )


def compare_with_baseline(summary_row: pd.Series) -> dict[str, float]:
    return {
        "delta_mae": float(summary_row["mae_mean"] - BASELINE_BEST["mae"]),
        "delta_rmse": float(summary_row["rmse_mean"] - BASELINE_BEST["rmse"]),
        "delta_r2": float(summary_row["r2_mean"] - BASELINE_BEST["r2"]),
        "pct_mae": float(((summary_row["mae_mean"] - BASELINE_BEST["mae"]) / BASELINE_BEST["mae"]) * 100),
        "pct_rmse": float(((summary_row["rmse_mean"] - BASELINE_BEST["rmse"]) / BASELINE_BEST["rmse"]) * 100),
    }


def build_figures(
    summary_results: pd.DataFrame,
    oof_predictions: pd.DataFrame,
    best_experiment: pd.Series,
    output_dirs: dict[str, Path],
) -> None:
    sns.set_theme(style="whitegrid")

    baseline_vs_phase2 = pd.DataFrame(
        [
            {
                "label": "Phase 1 baseline",
                "mae": BASELINE_BEST["mae"],
                "rmse": BASELINE_BEST["rmse"],
                "r2": BASELINE_BEST["r2"],
            },
            {
                "label": "Phase 2 best",
                "mae": best_experiment["mae_mean"],
                "rmse": best_experiment["rmse_mean"],
                "r2": best_experiment["r2_mean"],
            },
        ]
    )
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for axis, metric in zip(axes, ["mae", "rmse", "r2"], strict=False):
        sns.barplot(data=baseline_vs_phase2, x="label", y=metric, ax=axis)
        axis.set_title(metric.upper())
        axis.set_xlabel("")
    fig.tight_layout()
    fig.savefig(output_dirs["figures_dir"] / "phase1_vs_phase2_performance.png", dpi=200)
    plt.close(fig)

    sparse_subset = summary_results[summary_results["stage"] == "A_sparse_ablation"].copy()
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=sparse_subset, x="feature_set_name", y="rmse_mean", hue="target_representation", ax=ax)
    ax.set_title("Sparse-feature ablation comparison")
    ax.set_xlabel("Feature set")
    ax.set_ylabel("Mean RMSE")
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    fig.savefig(output_dirs["figures_dir"] / "sparse_feature_ablation.png", dpi=200)
    plt.close(fig)

    selection_subset = summary_results[summary_results["stage"] == "E_feature_selection"].copy()
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(data=selection_subset, x="feature_set_name", y="rmse_mean", hue="selection_strategy", ax=ax)
    ax.set_title("Feature-selection comparison")
    ax.set_xlabel("Feature set")
    ax.set_ylabel("Mean RMSE")
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    fig.savefig(output_dirs["figures_dir"] / "feature_selection_comparison.png", dpi=200)
    plt.close(fig)

    model_subset = summary_results[summary_results["stage"] == "F_model_comparison"].copy()
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=model_subset, x="model", y="rmse_mean", hue="target_representation", ax=ax)
    ax.set_title("Model comparison")
    ax.set_xlabel("Model")
    ax.set_ylabel("Mean RMSE")
    fig.tight_layout()
    fig.savefig(output_dirs["figures_dir"] / "model_comparison.png", dpi=200)
    plt.close(fig)

    best_oof = oof_predictions[oof_predictions["Experiment_ID"] == best_experiment["experiment_id"]].copy()
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(best_oof["Actual_Retention"], best_oof["Predicted_Retention"], alpha=0.55, edgecolor="none")
    maximum = max(float(best_oof["Actual_Retention"].max()), float(best_oof["Predicted_Retention"].max()))
    ax.plot([0, maximum], [0, maximum], linestyle="--", color="black", linewidth=1)
    ax.set_title("Best Phase 2 model: predicted vs actual")
    ax.set_xlabel("Actual retention")
    ax.set_ylabel("Predicted retention")
    fig.tight_layout()
    fig.savefig(output_dirs["figures_dir"] / "best_model_predicted_vs_actual.png", dpi=200)
    plt.close(fig)

    residuals = best_oof["Actual_Retention"] - best_oof["Predicted_Retention"]
    fig, ax = plt.subplots(figsize=(7, 6))
    sns.histplot(residuals, bins=30, kde=True, ax=ax)
    ax.set_title("Best Phase 2 model: residuals")
    ax.set_xlabel("Residual (actual - predicted)")
    fig.tight_layout()
    fig.savefig(output_dirs["figures_dir"] / "best_model_residuals.png", dpi=200)
    plt.close(fig)


def fit_final_model_and_shap(
    df: pd.DataFrame,
    selected_spec: ExperimentSpec,
    output_dirs: dict[str, Path],
) -> tuple[pd.DataFrame, list[str]]:
    final_model, _, _, _ = build_pipeline(selected_spec)
    final_model.fit(df, df[TARGET_COLUMN])
    fitted_pipeline = get_fitted_pipeline(final_model)
    feature_names = get_processed_feature_names(fitted_pipeline)
    transformed = transform_for_shap(fitted_pipeline, df)
    regressor = fitted_pipeline.named_steps["regressor"]

    explainer = shap.Explainer(regressor, transformed, feature_names=feature_names)
    shap_values = explainer(transformed)

    importance = pd.DataFrame(
        {
            "feature": feature_names,
            "mean_abs_shap": np.abs(shap_values.values).mean(axis=0),
        }
    ).sort_values("mean_abs_shap", ascending=False)
    importance.to_csv(output_dirs["shap_dir"] / "shap_global_importance.csv", index=False)

    plt.figure(figsize=(10, 6))
    shap.summary_plot(shap_values.values, transformed, feature_names=feature_names, show=False)
    plt.tight_layout()
    plt.savefig(output_dirs["shap_dir"] / "shap_summary.png", dpi=200, bbox_inches="tight")
    plt.close()

    top_features = importance["feature"].head(3).tolist()
    for feature in top_features:
        feature_index = feature_names.index(feature)
        plt.figure(figsize=(8, 6))
        shap.dependence_plot(
            feature_index,
            shap_values.values,
            transformed,
            feature_names=feature_names,
            show=False,
            interaction_index=None,
        )
        plt.tight_layout()
        safe_name = feature.replace(" ", "_").replace("/", "_")
        plt.savefig(output_dirs["shap_dir"] / f"shap_dependence_{safe_name}.png", dpi=200, bbox_inches="tight")
        plt.close()

    return importance, top_features


def build_final_report(
    baseline_summary: pd.DataFrame,
    summary_results: pd.DataFrame,
    fold_results: pd.DataFrame,
    oof_predictions: pd.DataFrame,
    feature_analysis: dict[str, pd.DataFrame],
    stage_winners: dict[str, pd.Series],
    best_experiment: pd.Series,
    shap_importance: pd.DataFrame,
    top_shap_features: list[str],
    output_dirs: dict[str, Path],
) -> None:
    improvement = compare_with_baseline(best_experiment)
    lines = [
        "# CookRisk Phase 2 Report",
        "",
        "## 1. Phase 1 benchmark",
        "",
        f"- Model: `{BASELINE_BEST['model']}`",
        f"- Features: `{BASELINE_BEST['feature_set']}`",
        f"- Target: `{BASELINE_BEST['target_representation']}`",
        f"- MAE: {BASELINE_BEST['mae']:.6f}",
        f"- RMSE: {BASELINE_BEST['rmse']:.6f}",
        f"- R2: {BASELINE_BEST['r2']:.6f}",
        "",
        "## 2. Phase 2 objectives",
        "",
        "- Preserve the GroupKFold unseen-compound validation logic.",
        "- Test sparse-feature decisions, food-cardinality handling, descriptor redundancy, engineered features, selection, and tuning under the same grouped-CV framework.",
        "- Improve the benchmark only when the trade-off is clear on RMSE, MAE, R2, and fold stability.",
        "",
        "## 3. Sparse-feature investigation",
        "",
        dataframe_to_markdown(summary_results[summary_results["stage"] == "A_sparse_ablation"][["experiment_id", "feature_set_name", "model", "target_representation", "mae_mean", "rmse_mean", "r2_mean"]]),
        "",
        f"- Stage winner: `{stage_winners['A_sparse_ablation']['experiment_id']}`",
        "",
        "## 4. High-cardinality food investigation",
        "",
        dataframe_to_markdown(summary_results[summary_results["stage"] == "B_food_cardinality"][["experiment_id", "feature_set_name", "food_strategy", "mae_mean", "rmse_mean", "r2_mean"]]),
        "",
        f"- Stage winner: `{stage_winners['B_food_cardinality']['experiment_id']}`",
        "",
        "## 5. Molecular descriptor redundancy analysis",
        "",
        dataframe_to_markdown(feature_analysis["descriptor_correlation"].round(3)),
        "",
        dataframe_to_markdown(summary_results[summary_results["stage"] == "C_descriptor_redundancy"][["experiment_id", "feature_set_name", "removed_features", "mae_mean", "rmse_mean", "r2_mean"]]),
        "",
        f"- Stage winner: `{stage_winners['C_descriptor_redundancy']['experiment_id']}`",
        "",
        "## 6. Feature engineering",
        "",
        dataframe_to_markdown(summary_results[summary_results["stage"] == "D_feature_engineering"][["experiment_id", "engineered_features", "mae_mean", "rmse_mean", "r2_mean"]]),
        "",
        f"- Stage winner: `{stage_winners['D_feature_engineering']['experiment_id']}`",
        "",
        "## 7. Feature selection",
        "",
        dataframe_to_markdown(summary_results[summary_results["stage"] == "E_feature_selection"][["experiment_id", "selection_strategy", "avg_features_after_processing", "mae_mean", "rmse_mean", "r2_mean"]]),
        "",
        f"- Stage winner: `{stage_winners['E_feature_selection']['experiment_id']}`",
        "",
        "## 8. Model comparison",
        "",
        dataframe_to_markdown(summary_results[summary_results["stage"] == "F_model_comparison"][["experiment_id", "model", "target_representation", "mae_mean", "rmse_mean", "r2_mean", "rmse_sd"]]),
        "",
        f"- Stage winner: `{stage_winners['F_model_comparison']['experiment_id']}`",
        "",
        "## 9. Hyperparameter optimization",
        "",
        dataframe_to_markdown(summary_results[summary_results["stage"] == "G_hyperparameter_tuning"][["experiment_id", "model", "target_representation", "mae_mean", "rmse_mean", "r2_mean", "rmse_sd"]]),
        "",
        f"- Stage winner: `{stage_winners['G_hyperparameter_tuning']['experiment_id']}`",
        "",
        "## 10. SHAP interpretation",
        "",
        "- SHAP was run only for the final selected candidate, after model selection.",
        f"- Top SHAP features: {', '.join(top_shap_features)}",
        "",
        dataframe_to_markdown(shap_importance.head(10)),
        "",
        "## 11. Final candidate model",
        "",
        f"- Experiment ID: `{best_experiment['experiment_id']}`",
        f"- Model: `{best_experiment['model']}`",
        f"- Feature set: `{best_experiment['feature_set_name']}`",
        f"- Target representation: `{best_experiment['target_representation']}`",
        f"- Selection strategy: `{best_experiment['selection_strategy']}`",
        f"- Mean MAE: {best_experiment['mae_mean']:.6f} +- {best_experiment['mae_sd']:.6f}",
        f"- Mean RMSE: {best_experiment['rmse_mean']:.6f} +- {best_experiment['rmse_sd']:.6f}",
        f"- Mean R2: {best_experiment['r2_mean']:.6f} +- {best_experiment['r2_sd']:.6f}",
        "",
        "## 12. Comparison with Phase 1 baseline",
        "",
        f"- Delta MAE: {improvement['delta_mae']:.6f} ({improvement['pct_mae']:.2f}%)",
        f"- Delta RMSE: {improvement['delta_rmse']:.6f} ({improvement['pct_rmse']:.2f}%)",
        f"- Delta R2: {improvement['delta_r2']:.6f}",
        "",
        "## 13. Fold-wise performance",
        "",
        dataframe_to_markdown(fold_results[fold_results["experiment_id"] == best_experiment["experiment_id"]][["fold", "mae", "rmse", "r2"]]),
        "",
        "## 14. Mean +- SD performance",
        "",
        dataframe_to_markdown(summary_results[["experiment_id", "stage", "model", "feature_set_name", "target_representation", "mae_mean", "mae_sd", "rmse_mean", "rmse_sd", "r2_mean", "r2_sd"]]),
        "",
        "## 15. Remaining limitations",
        "",
        "- Grouped validation is scientifically stronger than row-wise splits, but the dataset still has repeated-compound imbalance and only 197 unique molecular groups.",
        "- Sparse process variables remain difficult to estimate because their non-missing support is tiny even when retained.",
        "- High-cardinality context features can still hurt transfer if future foods differ from the observed standardized food space.",
        "- SHAP explains model behavior for the selected model; it does not prove causal cooking mechanisms.",
        "",
        "## 16. Recommended Phase 3 work",
        "",
        "- Perform deeper error analysis on the saved genuine OOF predictions.",
        "- Inspect whether the remaining hardest compounds or conditions cluster in specific food or compound classes.",
        "- Validate the final candidate against additional robustness checks before any downstream risk-scoring claims.",
        "",
    ]
    (output_dirs["output_root"] / "phase2_report.md").write_text("\n".join(lines), encoding="utf-8")


def save_config(
    repo_root: Path,
    dataset_path: Path,
    baseline_root: Path,
    output_dirs: dict[str, Path],
    selected_specs: list[ExperimentSpec],
) -> None:
    config = {
        "repo_root": str(repo_root),
        "dataset_path": str(dataset_path),
        "baseline_root": str(baseline_root),
        "output_root": str(output_dirs["output_root"]),
        "random_seed": RANDOM_SEED,
        "target_column": TARGET_COLUMN,
        "group_column": GROUP_COLUMN,
        "cv_method": "GroupKFold",
        "cv_splits": 5,
        "experiments": [
            {
                "experiment_id": spec.experiment_id,
                "stage": spec.stage,
                "feature_set_name": spec.feature_set_name,
                "food_strategy": spec.food_strategy,
                "engineered_features": list(spec.engineered_features),
                "selection_strategy": spec.selection_strategy,
                "model_name": spec.model_name,
                "target_representation": spec.target_representation,
                "hyperparameters": spec.hyperparameter_dict(),
                "tuned": spec.tuned,
                "tune_grid": spec.tune_grid_dict(),
                "notes": spec.notes,
            }
            for spec in selected_specs
        ],
        "software": {
            "python": platform.python_version(),
            "pandas": pd.__version__,
            "numpy": np.__version__,
            "matplotlib": matplotlib.__version__,
            "shap": shap.__version__,
        },
    }
    (output_dirs["config_dir"] / "phase2_config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")


def main() -> None:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    dataset_path = (args.dataset_path or (repo_root / "data" / "preprocessing" / "final" / "cookchem_molecular_retention_preprocessed.csv")).resolve()
    baseline_root = (args.baseline_root or (repo_root / "data" / "ml" / "baseline")).resolve()
    output_root = (args.output_root or (repo_root / "data" / "ml" / "phase2")).resolve()
    output_dirs = make_output_dirs(output_root)

    manifest = read_json(repo_root / "data" / "preprocessing" / "final" / "preprocessing_manifest.json")
    baseline_results = pd.read_csv(baseline_root / "baseline_results.csv")
    baseline_summary = baseline_results[baseline_results["metric_level"] == "summary"].copy()
    baseline_summary = baseline_summary.rename(columns={"feature_group": "feature_group"})

    df = coerce_numeric_columns(pd.read_csv(dataset_path))
    validate_columns(df, ["Record_ID", GROUP_COLUMN, TARGET_COLUMN])
    cv = select_cv(df[GROUP_COLUMN], preferred_splits=5)

    available_process = feature_columns_available(df, PROCESS_FEATURES)
    available_molecular = feature_columns_available(df, MOLECULAR_FEATURES)
    current_feature_columns = available_process + available_molecular

    predictor_missingness, food_frequency = save_feature_analysis(df, output_dirs)
    descriptor_correlation = df[available_molecular].corr()
    feature_analysis = {
        "predictor_missingness": predictor_missingness,
        "food_frequency": food_frequency,
        "descriptor_correlation": descriptor_correlation,
    }
    build_phase2_starting_report(
        baseline_root=baseline_root,
        baseline_summary=baseline_summary,
        baseline_report_path=baseline_root / "baseline_report.md",
        phase2_feature_columns=current_feature_columns,
        dataset_missingness=predictor_missingness,
        output_dirs=output_dirs,
    )

    executed_specs: list[ExperimentSpec] = []
    all_fold_rows: list[dict[str, Any]] = []
    all_oof_rows: list[dict[str, Any]] = []
    all_fold_audit_rows: list[dict[str, Any]] = []
    all_tuning_rows: list[dict[str, Any]] = []

    def run_and_collect(specs: list[ExperimentSpec]) -> pd.DataFrame:
        for spec in specs:
            executed_specs.append(spec)
            fold_rows, oof_rows, fold_audit_rows, tuning_rows = run_experiment(df=df, cv=cv, spec=spec)
            all_fold_rows.extend(fold_rows)
            all_oof_rows.extend(oof_rows)
            all_fold_audit_rows.extend(fold_audit_rows)
            all_tuning_rows.extend(tuning_rows)
        fold_df = pd.DataFrame(all_fold_rows)
        return summarise_results(fold_df)

    stage_a_specs = [
        instantiate_spec(
            experiment_id="A01_full_sparse_reference",
            stage="A_sparse_ablation",
            feature_set_name="full_phase1_feature_recipe",
            notes="Phase 2 sparse-feature reference using the frozen Phase 1 best model recipe.",
            feature_columns=current_feature_columns,
            food_strategy="current",
            engineered_features=[],
            selection_strategy="none",
            model_name="hist_gradient_boosting",
            target_representation="log1p",
        ),
        instantiate_spec(
            experiment_id="A02_no_pressure",
            stage="A_sparse_ablation",
            feature_set_name="no_pressure",
            notes="Ablation of Pressure_kPa only.",
            feature_columns=[column for column in current_feature_columns if column != "Pressure_kPa"],
            food_strategy="current",
            engineered_features=[],
            selection_strategy="none",
            model_name="hist_gradient_boosting",
            target_representation="log1p",
        ),
        instantiate_spec(
            experiment_id="A03_no_microwave",
            stage="A_sparse_ablation",
            feature_set_name="no_microwave",
            notes="Ablation of Microwave_Power_W only.",
            feature_columns=[column for column in current_feature_columns if column != "Microwave_Power_W"],
            food_strategy="current",
            engineered_features=[],
            selection_strategy="none",
            model_name="hist_gradient_boosting",
            target_representation="log1p",
        ),
        instantiate_spec(
            experiment_id="A04_no_oil",
            stage="A_sparse_ablation",
            feature_set_name="no_oil",
            notes="Ablation of Oil_Type_Standardized only.",
            feature_columns=[column for column in current_feature_columns if column != "Oil_Type_Standardized"],
            food_strategy="current",
            engineered_features=[],
            selection_strategy="none",
            model_name="hist_gradient_boosting",
            target_representation="log1p",
        ),
        instantiate_spec(
            experiment_id="A05_no_sparse_features",
            stage="A_sparse_ablation",
            feature_set_name="no_sparse_features",
            notes="Ablation of Pressure_kPa, Microwave_Power_W, and Oil_Type_Standardized together.",
            feature_columns=[column for column in current_feature_columns if column not in SPARSE_FEATURES],
            food_strategy="current",
            engineered_features=[],
            selection_strategy="none",
            model_name="hist_gradient_boosting",
            target_representation="log1p",
        ),
    ]
    summary_results = run_and_collect(stage_a_specs)
    stage_a_winner = stage_winner(summary_results, "A_sparse_ablation")
    stage_a_features = next(spec.feature_columns for spec in stage_a_specs if spec.experiment_id == stage_a_winner["experiment_id"])

    stage_b_specs = [
        instantiate_spec(
            experiment_id="B01_food_current",
            stage="B_food_cardinality",
            feature_set_name="food_current",
            notes="Keep Food_Name_Standardized as-is after sparse-feature decision.",
            feature_columns=list(stage_a_features),
            food_strategy="current",
            engineered_features=[],
            selection_strategy="none",
            model_name="hist_gradient_boosting",
            target_representation="log1p",
        ),
        instantiate_spec(
            experiment_id="B02_food_excluded",
            stage="B_food_cardinality",
            feature_set_name="food_excluded",
            notes="Exclude Food_Name_Standardized after sparse-feature decision.",
            feature_columns=list(stage_a_features),
            food_strategy="exclude",
            engineered_features=[],
            selection_strategy="none",
            model_name="hist_gradient_boosting",
            target_representation="log1p",
        ),
        instantiate_spec(
            experiment_id="B03_food_top20_other",
            stage="B_food_cardinality",
            feature_set_name="food_top20_other",
            notes="Collapse food categories to top-20 plus Other, fitted within each training fold.",
            feature_columns=list(stage_a_features),
            food_strategy="top_k_other",
            engineered_features=[],
            selection_strategy="none",
            model_name="hist_gradient_boosting",
            target_representation="log1p",
        ),
    ]
    summary_results = run_and_collect(stage_b_specs)
    stage_b_winner = stage_winner(summary_results, "B_food_cardinality")
    stage_b_spec = next(spec for spec in stage_b_specs if spec.experiment_id == stage_b_winner["experiment_id"])

    reduced_descriptor_drop_heavy = [column for column in stage_b_spec.feature_columns if column != "RDKit_Heavy_Atom_Count"]
    reduced_descriptor_drop_hydroxyl = [column for column in stage_b_spec.feature_columns if column != "RDKit_Hydroxyl_Groups"]
    reduced_descriptor_drop_pair = [
        column for column in stage_b_spec.feature_columns if column not in {"RDKit_Heavy_Atom_Count", "RDKit_Hydroxyl_Groups"}
    ]
    stage_c_specs = [
        instantiate_spec(
            experiment_id="C01_keep_all_descriptors",
            stage="C_descriptor_redundancy",
            feature_set_name="descriptor_full",
            notes="Retain all descriptors after sparse/food decisions.",
            feature_columns=list(stage_b_spec.feature_columns),
            food_strategy=stage_b_spec.food_strategy,
            engineered_features=[],
            selection_strategy="none",
            model_name="hist_gradient_boosting",
            target_representation="log1p",
        ),
        instantiate_spec(
            experiment_id="C02_drop_heavy_atom_count",
            stage="C_descriptor_redundancy",
            feature_set_name="descriptor_no_heavy_atom_count",
            notes="Drop RDKit_Heavy_Atom_Count because it is almost perfectly correlated with RDKit_Molecular_Weight.",
            feature_columns=reduced_descriptor_drop_heavy,
            food_strategy=stage_b_spec.food_strategy,
            engineered_features=[],
            selection_strategy="none",
            model_name="hist_gradient_boosting",
            target_representation="log1p",
        ),
        instantiate_spec(
            experiment_id="C03_drop_hydroxyl_groups",
            stage="C_descriptor_redundancy",
            feature_set_name="descriptor_no_hydroxyl_groups",
            notes="Drop RDKit_Hydroxyl_Groups because it is highly redundant and carries the only descriptor missingness.",
            feature_columns=reduced_descriptor_drop_hydroxyl,
            food_strategy=stage_b_spec.food_strategy,
            engineered_features=[],
            selection_strategy="none",
            model_name="hist_gradient_boosting",
            target_representation="log1p",
        ),
        instantiate_spec(
            experiment_id="C04_drop_heavy_atom_and_hydroxyl",
            stage="C_descriptor_redundancy",
            feature_set_name="descriptor_compact_pair",
            notes="Drop both RDKit_Heavy_Atom_Count and RDKit_Hydroxyl_Groups after redundancy review.",
            feature_columns=reduced_descriptor_drop_pair,
            food_strategy=stage_b_spec.food_strategy,
            engineered_features=[],
            selection_strategy="none",
            model_name="hist_gradient_boosting",
            target_representation="log1p",
        ),
    ]
    summary_results = run_and_collect(stage_c_specs)
    stage_c_winner = stage_winner(summary_results, "C_descriptor_redundancy")
    stage_c_spec = next(spec for spec in stage_c_specs if spec.experiment_id == stage_c_winner["experiment_id"])

    stage_d_specs = [
        instantiate_spec(
            experiment_id="D01_no_engineering",
            stage="D_feature_engineering",
            feature_set_name="no_engineering",
            notes="Carry forward the selected sparse/food/redundancy recipe without new engineered features.",
            feature_columns=list(stage_c_spec.feature_columns),
            food_strategy=stage_c_spec.food_strategy,
            engineered_features=[],
            selection_strategy="none",
            model_name="hist_gradient_boosting",
            target_representation="log1p",
        ),
        instantiate_spec(
            experiment_id="D02_temp_time_interaction",
            stage="D_feature_engineering",
            feature_set_name="temp_time_interaction",
            notes="Add temperature-time interaction and log cooking time to capture joint thermal exposure.",
            feature_columns=list(stage_c_spec.feature_columns),
            food_strategy=stage_c_spec.food_strategy,
            engineered_features=["temperature_time_interaction", "log_cooking_time"],
            selection_strategy="none",
            model_name="hist_gradient_boosting",
            target_representation="log1p",
        ),
        instantiate_spec(
            experiment_id="D03_targeted_interactions",
            stage="D_feature_engineering",
            feature_set_name="targeted_interactions",
            notes="Add temperature-time, log cooking time, log initial concentration, logP-temperature, and TPSA-time interactions.",
            feature_columns=list(stage_c_spec.feature_columns),
            food_strategy=stage_c_spec.food_strategy,
            engineered_features=[
                "temperature_time_interaction",
                "log_cooking_time",
                "log_initial_concentration",
                "logp_temperature_interaction",
                "tpsa_time_interaction",
            ],
            selection_strategy="none",
            model_name="hist_gradient_boosting",
            target_representation="log1p",
        ),
    ]
    summary_results = run_and_collect(stage_d_specs)
    stage_d_winner = stage_winner(summary_results, "D_feature_engineering")
    stage_d_spec = next(spec for spec in stage_d_specs if spec.experiment_id == stage_d_winner["experiment_id"])

    stage_e_specs = [
        instantiate_spec(
            experiment_id="E01_full_engineered_features",
            stage="E_feature_selection",
            feature_set_name="full_engineered_features",
            notes="Use the best engineered recipe without supervised feature selection.",
            feature_columns=list(stage_d_spec.feature_columns),
            food_strategy=stage_d_spec.food_strategy,
            engineered_features=list(stage_d_spec.engineered_features),
            selection_strategy="none",
            model_name="hist_gradient_boosting",
            target_representation="log1p",
        ),
        instantiate_spec(
            experiment_id="E02_selected_engineered_features",
            stage="E_feature_selection",
            feature_set_name="selected_engineered_features",
            notes="Apply tree-based SelectFromModel inside the fold-safe pipeline.",
            feature_columns=list(stage_d_spec.feature_columns),
            food_strategy=stage_d_spec.food_strategy,
            engineered_features=list(stage_d_spec.engineered_features),
            selection_strategy="tree_importance_median",
            model_name="hist_gradient_boosting",
            target_representation="log1p",
        ),
    ]
    summary_results = run_and_collect(stage_e_specs)
    stage_e_winner = stage_winner(summary_results, "E_feature_selection")
    stage_e_spec = next(spec for spec in stage_e_specs if spec.experiment_id == stage_e_winner["experiment_id"])

    stage_f_specs = [
        instantiate_spec(
            experiment_id="F01_ridge_log1p",
            stage="F_model_comparison",
            feature_set_name="selected_phase2_recipe",
            notes="Linear reference on the selected Phase 2 feature recipe.",
            feature_columns=list(stage_e_spec.feature_columns),
            food_strategy=stage_e_spec.food_strategy,
            engineered_features=list(stage_e_spec.engineered_features),
            selection_strategy=stage_e_spec.selection_strategy,
            model_name="ridge",
            target_representation="log1p",
            hyperparameters={"alpha": 1.0},
        ),
        instantiate_spec(
            experiment_id="F02_gradient_boosting_log1p",
            stage="F_model_comparison",
            feature_set_name="selected_phase2_recipe",
            notes="GradientBoosting on the selected Phase 2 feature recipe.",
            feature_columns=list(stage_e_spec.feature_columns),
            food_strategy=stage_e_spec.food_strategy,
            engineered_features=list(stage_e_spec.engineered_features),
            selection_strategy=stage_e_spec.selection_strategy,
            model_name="gradient_boosting",
            target_representation="log1p",
        ),
        instantiate_spec(
            experiment_id="F03_hist_gradient_boosting_log1p",
            stage="F_model_comparison",
            feature_set_name="selected_phase2_recipe",
            notes="HistGradientBoosting on the selected Phase 2 feature recipe.",
            feature_columns=list(stage_e_spec.feature_columns),
            food_strategy=stage_e_spec.food_strategy,
            engineered_features=list(stage_e_spec.engineered_features),
            selection_strategy=stage_e_spec.selection_strategy,
            model_name="hist_gradient_boosting",
            target_representation="log1p",
        ),
        instantiate_spec(
            experiment_id="F04_random_forest_log1p",
            stage="F_model_comparison",
            feature_set_name="selected_phase2_recipe",
            notes="RandomForest on the selected Phase 2 feature recipe.",
            feature_columns=list(stage_e_spec.feature_columns),
            food_strategy=stage_e_spec.food_strategy,
            engineered_features=list(stage_e_spec.engineered_features),
            selection_strategy=stage_e_spec.selection_strategy,
            model_name="random_forest",
            target_representation="log1p",
            hyperparameters={"n_estimators": 300, "min_samples_leaf": 2},
        ),
        instantiate_spec(
            experiment_id="F05_extra_trees_log1p",
            stage="F_model_comparison",
            feature_set_name="selected_phase2_recipe",
            notes="ExtraTrees on the selected Phase 2 feature recipe.",
            feature_columns=list(stage_e_spec.feature_columns),
            food_strategy=stage_e_spec.food_strategy,
            engineered_features=list(stage_e_spec.engineered_features),
            selection_strategy=stage_e_spec.selection_strategy,
            model_name="extra_trees",
            target_representation="log1p",
            hyperparameters={"n_estimators": 300, "min_samples_leaf": 2},
        ),
        instantiate_spec(
            experiment_id="F06_hist_gradient_boosting_raw",
            stage="F_model_comparison",
            feature_set_name="selected_phase2_recipe",
            notes="Raw-target HistGradientBoosting comparison on the selected Phase 2 feature recipe.",
            feature_columns=list(stage_e_spec.feature_columns),
            food_strategy=stage_e_spec.food_strategy,
            engineered_features=list(stage_e_spec.engineered_features),
            selection_strategy=stage_e_spec.selection_strategy,
            model_name="hist_gradient_boosting",
            target_representation="raw",
        ),
    ]
    summary_results = run_and_collect(stage_f_specs)
    stage_f_winner = stage_winner(summary_results, "F_model_comparison")

    stage_g_specs = [
        instantiate_spec(
            experiment_id="G01_hist_gradient_boosting_tuned",
            stage="G_hyperparameter_tuning",
            feature_set_name="selected_phase2_recipe_tuned",
            notes="Nested grouped-CV tuning for HistGradientBoosting.",
            feature_columns=list(stage_e_spec.feature_columns),
            food_strategy=stage_e_spec.food_strategy,
            engineered_features=list(stage_e_spec.engineered_features),
            selection_strategy=stage_e_spec.selection_strategy,
            model_name="hist_gradient_boosting",
            target_representation="log1p",
            tuned=True,
            tune_grid={
                "learning_rate": [0.03, 0.05],
                "max_leaf_nodes": [15, 31],
                "min_samples_leaf": [20],
            },
        ),
        instantiate_spec(
            experiment_id="G02_extra_trees_tuned",
            stage="G_hyperparameter_tuning",
            feature_set_name="selected_phase2_recipe_tuned",
            notes="Nested grouped-CV tuning for ExtraTrees.",
            feature_columns=list(stage_e_spec.feature_columns),
            food_strategy=stage_e_spec.food_strategy,
            engineered_features=list(stage_e_spec.engineered_features),
            selection_strategy=stage_e_spec.selection_strategy,
            model_name="extra_trees",
            target_representation="log1p",
            tuned=True,
            tune_grid={
                "n_estimators": [200],
                "max_depth": [None, 18],
                "min_samples_leaf": [1, 2],
                "max_features": ["sqrt"],
            },
        ),
    ]
    summary_results = run_and_collect(stage_g_specs)

    stage_winner_map = {
        "A_sparse_ablation": stage_a_winner,
        "B_food_cardinality": stage_b_winner,
        "C_descriptor_redundancy": stage_c_winner,
        "D_feature_engineering": stage_d_winner,
        "E_feature_selection": stage_e_winner,
        "F_model_comparison": stage_f_winner,
        "G_hyperparameter_tuning": stage_winner(summary_results, "G_hyperparameter_tuning"),
    }
    best_experiment = pd.DataFrame(stage_winner_map.values()).sort_values(
        ["rmse_mean", "mae_mean", "r2_mean", "rmse_sd", "mae_sd", "complexity_rank"],
        ascending=[True, True, False, True, True, True],
    ).iloc[0]

    best_spec = next(spec for spec in executed_specs if spec.experiment_id == best_experiment["experiment_id"])
    if best_spec.tuned:
        tuning_df = pd.DataFrame(all_tuning_rows)
        best_tuning_rows = tuning_df[tuning_df["experiment_id"] == best_spec.experiment_id].copy()
        winning_config = Counter(best_tuning_rows.sort_values(["outer_fold", "rmse_mean"]).groupby("outer_fold").first()["hyperparameters"]).most_common(1)[0][0]
        selected_best_spec = instantiate_spec(
            experiment_id=best_spec.experiment_id,
            stage=best_spec.stage,
            feature_set_name=best_spec.feature_set_name,
            notes=best_spec.notes,
            feature_columns=list(best_spec.feature_columns),
            food_strategy=best_spec.food_strategy,
            engineered_features=list(best_spec.engineered_features),
            selection_strategy=best_spec.selection_strategy,
            model_name=best_spec.model_name,
            target_representation=best_spec.target_representation,
            hyperparameters=json.loads(winning_config),
        )
    else:
        selected_best_spec = best_spec

    fold_results = pd.DataFrame(all_fold_rows)
    summary_results = summarise_results(fold_results)
    oof_predictions = pd.DataFrame(all_oof_rows)
    fold_audit = pd.DataFrame(all_fold_audit_rows)
    tuning_results = pd.DataFrame(all_tuning_rows)

    summary_results.to_csv(output_dirs["output_root"] / "phase2_experiment_log.csv", index=False)
    pd.concat([fold_results, summary_results], ignore_index=True, sort=False).to_csv(
        output_dirs["output_root"] / "phase2_results.csv",
        index=False,
    )
    oof_predictions.sort_values(["Experiment_ID", "Fold", "Record_ID"]).to_csv(
        output_dirs["output_root"] / "phase2_oof_predictions.csv",
        index=False,
    )
    fold_audit.to_csv(output_dirs["feature_analysis_dir"] / "fold_group_audit.csv", index=False)
    if not tuning_results.empty:
        tuning_results.to_csv(output_dirs["config_dir"] / "nested_tuning_results.csv", index=False)

    shap_importance, top_shap_features = fit_final_model_and_shap(
        df=df,
        selected_spec=selected_best_spec,
        output_dirs=output_dirs,
    )
    build_figures(summary_results, oof_predictions, best_experiment, output_dirs)
    build_final_report(
        baseline_summary=baseline_summary,
        summary_results=summary_results,
        fold_results=fold_results,
        oof_predictions=oof_predictions,
        feature_analysis=feature_analysis,
        stage_winners=stage_winner_map,
        best_experiment=best_experiment,
        shap_importance=shap_importance,
        top_shap_features=top_shap_features,
        output_dirs=output_dirs,
    )
    save_config(repo_root, dataset_path, baseline_root, output_dirs, executed_specs)

    improvement = compare_with_baseline(best_experiment)
    sparse_helped = stage_a_winner["rmse_mean"] < BASELINE_BEST["rmse"]
    engineering_helped = stage_d_winner["rmse_mean"] < stage_c_winner["rmse_mean"]
    selection_helped = stage_e_winner["rmse_mean"] < stage_d_winner["rmse_mean"]
    molecular_useful = "RDKit_" in "|".join(selected_best_spec.feature_columns)

    print("PHASE-1 BASELINE")
    print(f"- model: {BASELINE_BEST['model']}")
    print(f"- features: {BASELINE_BEST['feature_set']}")
    print(f"- target: {BASELINE_BEST['target_representation']}")
    print(f"- MAE: {BASELINE_BEST['mae']:.6f}")
    print(f"- RMSE: {BASELINE_BEST['rmse']:.6f}")
    print(f"- R2: {BASELINE_BEST['r2']:.6f}")
    print("PHASE-2 BEST")
    print(f"- model: {best_experiment['model']}")
    print(f"- features: {best_experiment['feature_set_name']}")
    print(f"- target: {best_experiment['target_representation']}")
    print(f"- MAE: {best_experiment['mae_mean']:.6f}")
    print(f"- RMSE: {best_experiment['rmse_mean']:.6f}")
    print(f"- R2: {best_experiment['r2_mean']:.6f}")
    print("IMPROVEMENT")
    print(f"- absolute change in MAE: {improvement['delta_mae']:.6f}")
    print(f"- absolute change in RMSE: {improvement['delta_rmse']:.6f}")
    print(f"- absolute change in R2: {improvement['delta_r2']:.6f}")
    print(f"- percentage change in MAE: {improvement['pct_mae']:.2f}%")
    print(f"- percentage change in RMSE: {improvement['pct_rmse']:.2f}%")
    print(f"- whether sparse features helped: {'yes' if sparse_helped else 'no'}")
    print(f"- whether feature engineering helped: {'yes' if engineering_helped else 'no'}")
    print(f"- whether feature selection helped: {'yes' if selection_helped else 'no'}")
    print(f"- whether molecular information remained useful: {'yes' if molecular_useful else 'no'}")
    print(f"- which features were most important according to SHAP: {', '.join(top_shap_features)}")
    print("- major remaining limitations: repeated-compound imbalance, sparse process-support, high-cardinality context, and non-causal interpretability.")
    print("Phase 2 complete.")
    print(f"- exact script path: {Path(__file__).resolve()}")
    print(f"- exact results path: {output_dirs['output_root'] / 'phase2_results.csv'}")
    print(f"- exact experiment log path: {output_dirs['output_root'] / 'phase2_experiment_log.csv'}")
    print(f"- exact OOF prediction path: {output_dirs['output_root'] / 'phase2_oof_predictions.csv'}")
    print(f"- exact report path: {output_dirs['output_root'] / 'phase2_report.md'}")


if __name__ == "__main__":
    main()
