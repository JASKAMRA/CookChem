# Feature Ablation, Importance, and Prediction Error

## Feature blocks already evaluated

Existing packages evaluate molecular descriptors, experimental/cooking variables, combined feature sets, and food-matrix additions. Results are package-specific and not directly pooled.

### v0.6 controlled ACR ablation (v0.5 parent; 379 observations; 8 DOI families)

**Evidence status: REPORTED** in `stageA/recovery_v0_6_0_2026_11_10/feature_ablation_comparison.csv`; not rerun for this package. MAE/RMSE units are ACR percentage points; R² is dimensionless.

| Feature set | Validation | R² | MAE (ACR percentage points) | RMSE (ACR percentage points) | Evidence status |
|---|---|---:|---:|---:|
| Full | Compound-grouped 5-fold | .400334 | 41.4568 | 142.4551 | REPORTED |
| Full | Source LOSO | −.041562 | 56.1391 | 187.7438 | REPORTED |
| Molecular descriptors only | Compound-grouped | −.034464 | 63.8312 | 187.1031 | REPORTED |
| Molecular descriptors only | Source LOSO | −.417074 | 98.5151 | 218.9876 | REPORTED |
| Cooking process only | Compound-grouped | .481932 | 41.9581 | 132.4087 | REPORTED |
| Cooking process only | Source LOSO | −.111392 | 62.4088 | 193.9352 | REPORTED |
| Molecular + cooking | Source LOSO | −.041176 | 56.0980 | 187.7090 | REPORTED |
| Food matrix + cooking | Source LOSO | −.070158 | 63.4129 | 190.3036 | REPORTED |

Source: `stageA/recovery_v0_6_0_2026_11_10/feature_ablation_comparison.csv`. The source report says the best source-held-out MAE was molecular+process, but the R² remained negative. Removing microwave medium yielded source R² −.646079; removing medium variables yielded −.184181; removing likely source proxies yielded −.208438.

### 439-row prototype ablation (hash-mismatch caveat)

**Evidence status: REPORTED; attribution to current dataset bytes BLOCKED/UNVERIFIED.** MAE/RMSE are on the reported ACR percentage-point scale.

Existing ExtraTrees ablations across the reported 439-row ACR package found negative source-heldout R² across descriptor-only (−.1170), process-only (−.0669), combined molecular/process (−.0327), and molecular/process/food matrix (−.0470). Because the package manifest parent hash conflicts with later current file bytes, treat these as **REPORTED/BLOCKED-UNVERIFIED**, not reproduced results tied to current bytes. See `stageA/final_prototype_2026_11_10/ablation_study.csv`.

## Feature importance and source proxy warning

**Evidence status: REPORTED** for the existing v0.5/v0.6 importance outputs; values were not regenerated for this package.

The v0.6 full-fit feature importance assigns 0.69844 to one-hot `cooking_medium_Microwave`; the next listed numeric features are much smaller (e.g., LogP .05570, TPSA .03615). The v0.5 iteration reported microwave medium importance .6725. The v0.6 report notes this category is concentrated in the source-by-medium matrix. It is therefore a plausible source/protocol proxy. Importance is model-dependent and associational; it is not evidence that microwave cooking causally changes retention.

## Error, residual, and subgroup outputs

**Evidence status: REPORTED.** Existing packages contain predicted-vs-observed figures, residual distributions, OOF errors, fold metrics, and group summaries by source, compound, food matrix, method, and target range. The 1,016-row reconstruction EDA reports a largest DOI family of 84 observations, largest compound of 130, and a top-three source share of 24.21%. These coverage imbalances inform subgroup interpretation but do not identify causes of error.

Existing error analysis highlights:

- the extreme ACR tail has disproportionate impact on RMSE/R²;
- errors vary by source/compound/food/method in saved summaries;
- molecular folds can retain DOI overlap;
- large residuals require source-record review before being attributed to model failure or data error.

No new residual calculation or subgroup analysis was run for this assembly. Exact saved output paths are indexed in [Appendix A](appendices/APPENDIX_A_EVIDENCE_FILE_INDEX.md) and the source reports.
