# EDA: verified concentration-ratio reconstruction

## Coverage

{
  "final_rows": 1016,
  "verified_original_rows": 338,
  "corrected_original_rows": 0,
  "excluded_original_rows": 786,
  "new_primary_source_verified_rows": 678,
  "doi_families": 32,
  "compounds": 48,
  "food_matrices": 66,
  "methods": 41,
  "max_ratio_calc_difference": 0.004822448472793894
}

## Target distribution

- Mean: 156.661; median: 88.377; standard deviation: 419.047.
- Range: 0.000 to 6536.364; observations above 100%: 346.
- IQR outliers: 97. These are retained for review because a concentration ratio above 100% may reflect concentration, matrix-water change, or analytical variation; it is not interpreted as mass retention.

## Completeness and identity

- Raw/cooked concentration completeness: 100.0%/100.0%.
- Temperature and duration completeness: 43.1%/79.7%.
- Available RDKit descriptor completeness across the eight shared descriptors: 100.0%.
- Largest DOI family: 84 observations; largest compound: 130 observations.

All 1,016 modelling rows have documented raw and cooked concentrations, compatible recorded basis/unit fields, a primary-source locator, and the same explicit apparent-concentration-ratio target. The plots summarize target, source, compound, food-matrix, and method coverage. Source-, compound-, matrix-, and method-level target variation is available directly in `final_verified_master_dataset.csv` and should be interpreted with source/protocol context.
