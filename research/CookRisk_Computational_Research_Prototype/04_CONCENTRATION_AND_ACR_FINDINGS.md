# Concentration and ACR Findings

## Endpoint definitions

**Apparent concentration ratio:** `ACR (%) = 100 × C_cooked / C_raw`. Both measurements should refer to the same compound and compatible food state, unit, and basis. ACR characterizes apparent concentration change, not total analyte mass retained.

**Total-mass retention:** requires concentration together with compatible raw and cooked food mass or measured yield and any necessary moisture/basis reconciliation. Cooking-liquid disposition and edible portion also matter where relevant. Existing ACR fields alone do not establish this endpoint.

**Cooked concentration prediction:** predicts `C_cooked` itself in a unit/basis. Existing controlled comparisons note that heterogeneous units/bases make pooled cooked-concentration scores difficult to interpret scientifically.

**Historical `Retention_Final`:** separate 1,124-row benchmark target. Its equation is not resolved in the historical source manifest. Do not rename it ACR.

## Existing raw/cooked and ACR analysis

**Evidence status: REPORTED** in the named reconstruction EDA report; these values were not freshly recalculated for this package. For the separate verified ACR reconstruction, that existing report states:

- 1,016 observations; raw and cooked concentration fields each 100% complete.
- 32 DOI families, 48 compound identities, 66 food matrices, and 41 methods.
- 678 newly primary-source-verified rows and 338 historical rows reverified; zero historical rows corrected; 786 historical rows excluded.
- Maximum difference between recorded target and recomputed `100 × cooked/raw`: 0.004822 percentage points.
- Mean ACR 156.661%; median 88.377%; SD 419.047%; range 0–6,536.364%.
- 346/1,016 observations exceed 100%; 97 are flagged as IQR outliers and retained for review.
- Temperature is present in 43.1% of observations; cooking duration in 79.7%; eight reported molecular descriptors are complete across the package.

**Status:** REPORTED in `stageA/verified_concentration_ratio_reconstruction/final_dataset_eda_report.md`; not re-extracted from the primary publications or recomputed for this assembly. The same or related distribution values appear in the Batch021 EDA audit, but package provenance remains separate.

## Interpretation

ACR >100% can arise when measured concentration in the cooked sample is higher than the raw sample under the reported basis. Possible context includes water loss, matrix concentration, extraction/assay effects, sample-basis differences, or analytical variation. These values do not show that cooking increased total compound mass. Extreme values influence RMSE and R²; existing sensitivity analysis shows tail sensitivity but does not justify deleting those observations from the primary analysis.

## Existing evidence about true retention

A v0.7 harmonization note says a source reports a separate true-retention statistic, but that statistic is kept separate from project ACR. No FW-to-DW conversion was made. No total-mass retention outcome was calculated in the ACR packages reviewed here. Future mass-retention analysis is **PROPOSED/BLOCKED** until measured yield/mass and compatible basis evidence are available.

## Source references

- `stageA/recovery_v0_2_0_2026_11_10/target_definition_contract.md`
- `stageA/recovery_v0_7_0_2026_11_10/measurement_harmonisation_report.md`
- `stageA/verified_concentration_ratio_reconstruction/final_dataset_eda_report.md`
- `stageA/final_dataset_historical_model_and_eda_audit/final_dataset_eda_report.md`
- `stageA/dataset_expansion_1000/batch_021/post1000_validation_summary.json`
