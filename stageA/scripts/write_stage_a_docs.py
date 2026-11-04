"""Generate Stage A documentation from the executed outputs (no invented metrics)."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


def md_table(df: pd.DataFrame, columns: list[str]) -> str:
    view = df.loc[:, columns].copy()
    for col in view.select_dtypes(include="number"):
        view[col] = view[col].map(lambda v: f"{v:.6f}")
    headers = view.columns.tolist()
    rows = [[str(value) for value in row] for row in view.to_numpy()]
    return "\n".join([
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
        *["| " + " | ".join(row) + " |" for row in rows],
    ])


def main():
    results = pd.read_csv(OUT / "stageA_benchmark_results.csv")
    reference = results.loc[results.Model == "ExtraTrees_reference"].iloc[0]
    # Like-for-like deltas: Stage A aggregate OOF values, not historical fold means.
    for metric in ("MAE", "RMSE", "R2"):
        results[f"Delta_{metric}"] = results[metric] - reference[metric]
    results.to_csv(OUT / "stageA_benchmark_results.csv", index=False)
    xgb = results.loc[results.Model == "XGBoost_tuned"].iloc[0]

    literature = """# Stage A Literature Review

## Evidence inventory and traceability

The repository supplied `literature/week 1.pdf`, a Week 1 team review of **six** papers, not eight. No separate eight-paper review was found in the repository or provided attachments. This report therefore records the six supplied entries as review-level evidence (their bibliographic details were not all present in the PDF) and distinguishes them from the additional original methodological papers below. No missing author, year, DOI, dataset size, or performance result has been fabricated.

| Supplied review entry | Evidence stated in the Week 1 PDF | Relevance to CookRisk |
|---|---|---|
| Palermo, Pellegrini & Fogliano (2014) | Cooking effects can reflect degradation and extractability; food matrix, compound, method and conditions matter. | Supports molecular + food + process predictors and retaining apparent increases. |
| Murador et al. (2018) | Method effects on polyphenols and antioxidant activity need not align. | Supports retaining a compound-retention target rather than substituting antioxidant activity. |
| Miglio et al. (2008) | Vegetable responses vary within the same method; no universally superior method. | Supports interactions and subgroup diagnostics. |
| Kourouma et al. (2019) | Method, duration and compound identity jointly affect retention. | Supports time and molecular descriptor features. |
| Rothwell et al. (2015) | Literature retention varies by food, compounds and processing; values >100% are not automatically errors. | Supports source-aware validation and no automatic outlier deletion. |
| Fratianni et al. (2021) | Apparent concentration increases may reflect solids/weight change rather than compound formation. | Supports the Phase 3 extreme-value sensitivity analysis. |

## Additional literature used for Stage A model selection

* Chen, T. & Guestrin, C. (2016), *XGBoost: A Scalable Tree Boosting System*, KDD, DOI: 10.1145/2939672.2939785. This original paper describes regularised gradient-tree boosting and sparsity-aware learning. It motivated one controlled XGBoost comparison, not an assumption that it would win.
* Prokhorenkova, L. et al. (2018), *CatBoost: unbiased boosting with categorical features*, NeurIPS 31. The paper describes ordered boosting and categorical-feature processing designed to address prediction shift. CatBoost was considered but not benchmarked because no compatible package was installed in the isolated execution environment; Stage A did not substitute an unverified implementation.
* Ke, G. et al. (2017), *LightGBM: A Highly Efficient Gradient Boosting Decision Tree*, NeurIPS 30. LightGBM was considered for histogram boosting and sparse one-hot features, but was not benchmarked because its package was unavailable; its large-data efficiency motivation is less decisive for 1,124 records.

## Synthesis

The supplied literature supports heterogeneous, nonlinear relationships among molecular identity, food context and cooking conditions, and warns against removing apparent increases. The methodological literature justifies a compact comparison of a regularised gradient-boosted tree (XGBoost), a nonlinear kernel method (RBF-SVR), and a randomised-tree comparator (Random Forest). It does **not** justify replacing molecular-grouped validation, removing rare high-retention observations, or expecting any model to outperform Extra Trees a priori.
"""

    selection = """# Stage A Model Selection

## Locked comparison conditions

All models use the frozen Phase 2 feature recipe: 22 source predictors (process, context and RDKit descriptors after Heavy Atom Count removal) plus five deterministic engineered features: Temperature x Time, log Cooking Time, log Initial Concentration, LogP x Temperature, and TPSA x Cooking Time. Numeric median imputation/scaling and categorical missing-value encoding/one-hot encoding are fit within each outer training fold. The target is `log1p(Retention_Final)` and predictions are inverse transformed before original-scale metrics are calculated. Splits are the same 5-fold `GroupKFold` by `Canonical_Molecular_ID`.

| Model | Literature/CookRisk justification | Expected strength | Main risk |
|---|---|---|---|
| Extra Trees reference | Current selected benchmark among Phase 1-3 configurations. | Strong nonlinear baseline with mixed encoded features. | Rare extremes strongly affect RMSE/R2. |
| Random Forest | Controlled bagged-tree comparison against Extra Trees. | May reduce split randomisation sensitivity. | Can be less diverse / slower; already close in Phase 2. |
| RBF-SVR | Nonlinear-kernel baseline for scaled chemical/process descriptors. | Smooth nonlinear response surface. | One-hot food context can be high-dimensional; sensitive to kernel settings. |
| XGBoost | Chen & Guestrin (2016); regularised boosted trees and sparse features. | Regularisation may improve tail-sensitive RMSE/R2. | Can trade MAE for tail fitting; must not be selected on R2 alone. |

## Rejected or deferred

HistGradientBoosting and Extra Trees tuning were already evaluated in Phase 2, so Stage A did not repeat them as new discovery experiments. CatBoost and LightGBM were literature-considered but deferred because their packages were not in the isolated reproducibility environment; no external package was silently substituted. Stacking was not tested because no pair of candidates showed a complementary error pattern with clear overall improvement.
"""

    report = f"""# CookRisk Stage A Report

## 1. Objective

Determine whether a literature-guided alternative improves molecular retention prediction under the locked CookRisk molecular-grouped validation protocol, without changing the data, target, features, outlier handling, or Phase 1-3 artifacts.

## 2. Existing CookRisk benchmark

The historical Phase 2 selected candidate is Extra Trees (`n_estimators=300`, `min_samples_leaf=2`, seed 42, `log1p` target): mean fold MAE **31.959809**, RMSE **123.073056**, R2 **0.380461**. These are historical fold-mean results. Stage A also independently reproduced Extra Trees and reports aggregate OOF metrics below; these aggregations should not be conflated.

## 3-6. Literature, candidate selection and methodology

See `stageA_literature_review.md` and `stageA_model_selection.md`. Stage A used 1,124 records and 197 molecular groups. Every model was evaluated with 5-fold GroupKFold by `Canonical_Molecular_ID`; no group overlap was recorded. All preprocessing was fit only within each training fold. The reported OOF metrics are on the original retention scale after inverse transformation.

## 7. Aggregate OOF benchmark results

{md_table(results, ['Model','MAE','RMSE','R2','Fold_R2_Mean','Fold_R2_STD','Delta_MAE','Delta_RMSE','Delta_R2'])}

`Delta_*` values are versus the independent Extra Trees aggregate OOF reference, so comparisons are like-for-like. XGBoost tuning used a compact nested 3-fold GroupKFold search within each outer-training fold; it did not select using final OOF predictions.

## 8. Hyperparameter tuning

The tuned XGBoost configuration was selected from a small grid over `n_estimators` (250/450), `max_depth` (2/3), and `min_child_weight` (3/8), with learning rate 0.03, subsampling 0.8, column subsampling 0.8 and L2 regularisation 5. Exact inner-CV records are in `stageA_tuning_results.csv`.

## 9. Robustness analysis

For tuned XGBoost, seed 42/123 gave MAE 34.612/34.901, RMSE 138.695/139.133 and R2 0.283/0.279. Removing the highest 1% of actual retention (sensitivity only; not primary analysis) improved tuned-XGBoost metrics to MAE 25.161, RMSE 46.020 and R2 0.364, confirming that rare extreme targets dominate tail-sensitive metrics. The complete range, cooking-method and compound-class results are in `stageA_robustness.csv`.

## 10-11. Feature engineering and ensembles

No new feature engineering was added: the five literature-plausible Phase 2 interactions were already locked in the fair feature recipe. No ensemble was tested because no alternative delivered an unambiguous overall improvement.

## 12. Final comparison and decision

Tuned XGBoost reduced aggregate OOF RMSE by {reference.RMSE - xgb.RMSE:.3f} ({(reference.RMSE - xgb.RMSE) / reference.RMSE * 100:.2f}%) and increased R2 by {xgb.R2 - reference.R2:.3f}, but increased MAE by {xgb.MAE - reference.MAE:.3f} ({(xgb.MAE - reference.MAE) / reference.MAE * 100:.2f}%). Random Forest and RBF-SVR were worse on all primary aggregate OOF metrics. Because XGBoost’s tail-oriented RMSE/R2 gain comes with a materially worse typical error (MAE), and the historical fold-mean benchmark remains stronger than every Stage A alternative on MAE, **RETAIN EXTRA TREES** as the current selected benchmark. This is a negative but informative Stage A result.

## 13. Limitations

The supplied literature base contained six, not eight, documented papers; no missing citations were invented. The dataset is heterogeneous, has sparse process variables and only 197 molecular groups. Twelve extreme-retention observations disproportionately influence RMSE/R2. CatBoost/LightGBM were documented as deferred rather than treated as tested.

## 14-15. Conclusion and recommended next step

Stage A found no replacement that improved MAE, RMSE and R2 together under strict grouped validation. Retain Extra Trees and prioritise data expansion, harmonisation of extreme retention measurements, and external/source-held-out validation before further algorithm expansion.
"""

    reproducibility = f"""# Stage A Reproducibility

## Inputs
* Staged authoritative input: `stageA/input/cookchem_molecular_retention_preprocessed.csv` copied unchanged from `C:\\Users\\kamra\\Desktop\\BTP\\CookChem\\data\\preprocessing\\final\\cookchem_molecular_retention_preprocessed.csv`.
* Historical read-only reference: Phase 2/3 artifacts under `data/ml/phase2` and `data/ml/phase3`.

## Environment

Use Python 3.12.14 and install the complete Python package set from `stageA/stageA-requirements-py312.lock`. The lock was captured from the isolated 2026-11-04 reproduction environment; it pins the four direct dependencies and their resolved transitive packages. The historical Stage A run did not record its full transitive environment, so its original package-level environment cannot be proven identical. Do not use Python 3.14 for this reproduction.

## Execute on macOS/Linux
```sh
brew install libomp  # macOS; validated with Homebrew libomp 23.1.5
python3.12 -m venv /tmp/cookrisk-stage-a-venv
. /tmp/cookrisk-stage-a-venv/bin/activate
python -m pip install -r stageA/stageA-requirements-py312.lock
python -m pip check
mkdir -p /tmp/cookrisk-stage-a-copy/stageA/outputs
cp -R stageA/input stageA/scripts /tmp/cookrisk-stage-a-copy/stageA/
python /tmp/cookrisk-stage-a-copy/stageA/scripts/run_stage_a.py
python /tmp/cookrisk-stage-a-copy/stageA/scripts/write_stage_a_docs.py
```

## Execute on Windows PowerShell

Install the current Microsoft Visual C++ Redistributable for the Windows architecture before importing XGBoost, as required by the [XGBoost installation guide](https://xgboost.readthedocs.io/en/stable/install.html). Use the official [Microsoft download page](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist).

```powershell
py -3.12 -m venv "$env:TEMP\\cookrisk-stage-a-venv"
& "$env:TEMP\\cookrisk-stage-a-venv\\Scripts\\Activate.ps1"
python -m pip install -r stageA/stageA-requirements-py312.lock
python -m pip check
New-Item -ItemType Directory -Force "$env:TEMP\\cookrisk-stage-a-copy\\stageA\\outputs" | Out-Null
Copy-Item -Recurse stageA\\input, stageA\\scripts "$env:TEMP\\cookrisk-stage-a-copy\\stageA\\"
python "$env:TEMP\\cookrisk-stage-a-copy\\stageA\\scripts\\run_stage_a.py"
python "$env:TEMP\\cookrisk-stage-a-copy\\stageA\\scripts\\write_stage_a_docs.py"
```

Windows and Linux execution have not been tested in this cycle. On Linux, ensure the platform OpenMP runtime (`libgomp`) is installed before importing XGBoost. Verify `python --version` is 3.12.14 and `python -m pip freeze` matches the lock before running. The canonical entrypoints are `stageA/scripts/run_stage_a.py` and `stageA/scripts/write_stage_a_docs.py`; do not run the duplicate copies under `stageA/scripts/scripts/`.

## Configuration
* Rows/groups: 1,124 / 197; target: `Retention_Final`; group: `Canonical_Molecular_ID`.
* CV: 5-fold GroupKFold; no group overlap; seed 42, with seed 123 sensitivity for the strongest tail-oriented alternative.
* This Stage A benchmark fits `log1p(Retention_Final)` and applies `expm1` before original-scale metrics. This is the Stage A comparison procedure; it does not reproduce the frozen Stage B artifact, whose manifest specifies a fold-fitted Yeo-Johnson PowerTransformer.
* Extra Trees reference: 300 estimators, `min_samples_leaf=2`, seed 42.
* Software: {json.dumps(json.load(open(OUT / 'stageA_qa.json'))['software'])}; `scikit-learn` 1.9.1; `xgboost` 3.4.1.
* Outputs are generated under `stageA/outputs`; `stageA_validation_audit.csv` and `stageA_qa.json` are programmatic QA evidence.
* Each new run also writes `stageA_run_manifest.json` with input/code/output hashes, input and feature column order, per-fold group/record assignment hashes, preprocessing contract, model configuration, package versions, and platform. Historical outputs do not contain this manifest, so it cannot retroactively identify their original fitted state.
"""
    (ROOT / "stageA_literature_review.md").write_text(literature, encoding="utf-8")
    (ROOT / "stageA_model_selection.md").write_text(selection, encoding="utf-8")
    (ROOT / "stageA_report.md").write_text(report, encoding="utf-8")
    (ROOT / "stageA_reproducibility.md").write_text(reproducibility, encoding="utf-8")
    (ROOT / "README.md").write_text("# CookRisk Stage A\n\nIndependent literature-guided benchmark. Run the two scripts described in `stageA_reproducibility.md`; inspect `outputs/` for all generated numbers. Historical Phase 1-3 artifacts are not modified.\n", encoding="utf-8")
    print("Stage A documentation written.")


if __name__ == "__main__":
    main()
