"""Stage B, step 7: compare original and improved recipes using fold-mean metrics."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
OUT = ROOT / "outputs"


def main():
    phase2 = pd.read_csv(REPO / "data" / "ml" / "phase2" / "phase2_results.csv")
    original = phase2.loc[(phase2["metric_level"] == "summary") & (phase2["experiment_id"] == "F05_extra_trees_log1p")].iloc[0]
    step3 = pd.read_csv(OUT / "stageB_step3_fold_results.csv")
    improved_folds = step3.loc[step3["Model"] == "ExtraTrees_YeoJohnson"].copy()
    improved = {metric: float(improved_folds[metric].mean()) for metric in ("MAE", "RMSE", "R2")}
    original_values = {"MAE": float(original["mae_mean"]), "RMSE": float(original["rmse_mean"]), "R2": float(original["r2_mean"])}
    rows = []
    for label, values, notes in [
        ("Phase 2 selected benchmark", original_values, "Frozen Phase 2 Extra Trees, log1p target, selected Phase 2 feature recipe."),
        ("Stage B candidate", improved, "Extra Trees, Step 2 missingness/thermal features, Yeo-Johnson target."),
    ]:
        rows.append({"Recipe": label, **values, "Notes": notes})
    comparison = pd.DataFrame(rows)
    for metric in ("MAE", "RMSE", "R2"):
        comparison[f"Delta_{metric}_vs_phase2"] = comparison[metric] - original_values[metric]
    comparison.to_csv(OUT / "stageB_step7_like_for_like_comparison.csv", index=False)
    conclusion = (
        "SELECT STAGE B CANDIDATE"
        if improved["MAE"] < original_values["MAE"] and improved["RMSE"] < original_values["RMSE"] and improved["R2"] > original_values["R2"]
        else "CANDIDATE REQUIRES TRADE-OFF REVIEW"
    )
    (OUT / "stageB_step7_decision.md").write_text(
        f"# Stage B Step 7 Decision\n\n"
        f"Original Phase 2 fold means: MAE {original_values['MAE']:.6f}, RMSE {original_values['RMSE']:.6f}, R2 {original_values['R2']:.6f}.\n\n"
        f"Stage B candidate fold means: MAE {improved['MAE']:.6f}, RMSE {improved['RMSE']:.6f}, R2 {improved['R2']:.6f}.\n\n"
        f"## Decision\n\n{conclusion}.\n\n"
        f"The comparison uses the same 5-fold molecular GroupKFold and fold-mean aggregation. The target transformation and new features differ intentionally as the Stage B intervention.\n",
        encoding="utf-8",
    )
    print(comparison.to_string(index=False))
    print(conclusion)


if __name__ == "__main__":
    main()
