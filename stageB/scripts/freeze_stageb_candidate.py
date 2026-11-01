"""Freeze the selected Stage B retention model without modifying Phases 1-3."""
from pathlib import Path
import hashlib
import json
import platform
import sys

import joblib
import pandas as pd
from sklearn.compose import TransformedTargetRegressor
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PowerTransformer

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
from evaluate_missingness_features import augmented_features
sys.path.insert(0, str(REPO / "stageA" / "scripts"))
import run_stage_a as stage_a


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    input_path = REPO / "stageA" / "input" / "cookchem_molecular_retention_preprocessed.csv"
    final_dir = ROOT / "final_model"
    final_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(input_path)
    if len(df) != 1124 or df[stage_a.GROUP].nunique() != 197:
        raise ValueError("Dataset lock failed; refusing to freeze a changed dataset.")

    x = augmented_features(df)
    y = df[stage_a.TARGET]
    model = Pipeline([
        ("preprocess", stage_a.preprocessor(x.columns.tolist())),
        ("model", TransformedTargetRegressor(
            regressor=ExtraTreesRegressor(
                n_estimators=300,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=1,
            ),
            transformer=PowerTransformer(method="yeo-johnson", standardize=True),
        )),
    ])
    model.fit(x, y)
    model_path = final_dir / "cookrisk_retention_stageB_selected.joblib"
    joblib.dump(model, model_path)

    manifest = {
        "status": "FROZEN_SELECTED_CANDIDATE",
        "selection_basis": "Stage B Step 7, 5-fold GroupKFold by Canonical_Molecular_ID; mean fold metrics.",
        "model": "ExtraTreesRegressor",
        "model_parameters": {"n_estimators": 300, "min_samples_leaf": 2, "random_state": 42, "n_jobs": 1},
        "target": "Retention_Final",
        "target_transform": "PowerTransformer(method=yeo-johnson, standardize=True), fitted inside every validation training fold during selection; fitted on full data only for the frozen artifact.",
        "group_column": "Canonical_Molecular_ID",
        "selection_validation": {"method": "GroupKFold", "n_splits": 5, "rows": 1124, "unique_groups": 197},
        "features": {"base_phase2_recipe": stage_a.BASE_FEATURES, "stageB_additions": [column for column in x.columns if column not in stage_a.make_features(df).columns]},
        "like_for_like_metrics": {
            "phase2_original": {"MAE": 31.959809, "RMSE": 123.073056, "R2": 0.380461},
            "stageB_selected": {"MAE": 31.630524, "RMSE": 122.357915, "R2": 0.390691},
        },
        "input": {"path": str(input_path), "sha256": sha256(input_path)},
        "artifact": {"path": str(model_path), "sha256": sha256(model_path)},
        "inference_note": "Apply augmented_features from stageB/scripts/evaluate_missingness_features.py before model.predict. Predictions are on the original retention scale.",
        "software": {"python": platform.python_version(), "pandas": pd.__version__},
    }
    (final_dir / "stageB_selected_model_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (final_dir / "README.md").write_text(
        "# CookRisk Stage B Selected Retention Model\n\n"
        "Selected via Stage B Step 7. This artifact does not replace or alter historical Phase 1-3 outputs. "
        "It is fitted on all 1,124 rows only after model selection; do not report its in-sample performance as validation performance. "
        "Use the Step 7 grouped-CV metrics in the manifest for performance reporting.\n",
        encoding="utf-8",
    )
    print(f"Frozen artifact: {model_path}")


if __name__ == "__main__":
    main()
