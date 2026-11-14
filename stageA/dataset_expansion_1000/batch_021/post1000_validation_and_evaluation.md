# Post-1,000 validation and evaluation

## Completion checkpoint
- **1,016 verified observations**, **32 independent DOI families**, 51 compounds, 66 food matrices, and 41 normalized cooking-method labels.
- Batch 021 adds 78 direct primary-table observations from one new DOI family; it preserves all 938 Batch-020 rows.

## Compatibility and leakage results
```json
{
  "rows": 1016,
  "doi_families": 32,
  "compounds": 51,
  "food_matrices": 66,
  "methods": 41,
  "missing_doi": 0,
  "preserved_legacy_zero_cooked_rows": 2,
  "target_formula_deviations_over_0_01pp": 0,
  "max_target_rounding_deviation_pp": 0.004822448472793894,
  "duplicate_experiment_keys": 0,
  "aggregate_or_assay_named_rows": 0,
  "new_batch_rows": 78,
  "new_batch_nonpositive_raw_or_cooked": 0,
  "new_batch_formula_mismatches": 0,
  "new_batch_duplicate_experiment_keys": 0
}
```
- The 78 new rows are positive, formula-exact, uniquely keyed experimental observations.
- Two inherited pre-Batch-021 Vitamin-C cooked-zero rows are preserved and reported; they were not used to inflate new acquisition. Earlier stored targets differ from recomputation by at most 0.004823 percentage points due to historical rounding.

## Coverage, dominance and replication
- Largest DOI family: 10.3390/molecules31162740 with 84 rows (8.27%).
- Top three DOI families hold 246 rows (24.21%).
- Strict source-replication cells requiring same analyte, matrix, normalized method, time and basis: 0.
- The source-by-matrix/method and compound-by-matrix tables are retained in this package; larger coverage is still source-clustered.

## Fold-safe model evaluation
- Fixed resource-bounded specifications: Random Forest and Extra Trees 10 trees; Gradient Boosting 25 estimators; XGBoost 10 estimators; deterministic seed 42; all other settings as stated in `run_one_post1000_model.py`. The bound was needed to finish every fold within the execution limit, and results must not be compared as a hyperparameter-tuned benchmark.
- Source-family LOSO is primary. Best source-LOSO R²: **xgboost -0.0123**; lowest source-LOSO MAE: **svr_rbf 104.4087**. No model has positive source-held-out R².
- Therefore no model is selected for deployment, no Stage C integration is authorized, and apparent concentration ratios must not be interpreted as total-mass retention.

| model | validation | R² | MAE | RMSE |
|---|---|---:|---:|---:|
| dummy_median | compound_grouped_5fold | -0.0266 | 105.2416 | 424.3782 |
| extra_trees | compound_grouped_5fold | -0.0555 | 100.0337 | 430.3012 |
| gradient_boosting | compound_grouped_5fold | -0.0054 | 123.0268 | 419.9775 |
| random_forest | compound_grouped_5fold | -0.0809 | 103.9990 | 435.4629 |
| ridge | compound_grouped_5fold | 0.0525 | 131.1446 | 407.6877 |
| svr_rbf | compound_grouped_5fold | -0.0222 | 98.9854 | 423.4664 |
| xgboost | compound_grouped_5fold | 0.0141 | 128.3032 | 415.8792 |
| dummy_median | food_matrix_grouped_5fold | -0.0268 | 105.3095 | 424.4163 |
| extra_trees | food_matrix_grouped_5fold | 0.1858 | 108.1517 | 377.9238 |
| gradient_boosting | food_matrix_grouped_5fold | 0.0998 | 120.1380 | 397.3968 |
| random_forest | food_matrix_grouped_5fold | 0.1583 | 105.2850 | 384.2606 |
| ridge | food_matrix_grouped_5fold | 0.0725 | 160.8982 | 403.3686 |
| svr_rbf | food_matrix_grouped_5fold | -0.0246 | 102.2546 | 423.9573 |
| xgboost | food_matrix_grouped_5fold | 0.0131 | 129.3337 | 416.0886 |
| dummy_median | leave_one_source_out | -0.0275 | 105.8168 | 424.5577 |
| extra_trees | leave_one_source_out | -0.0618 | 114.0411 | 431.5917 |
| gradient_boosting | leave_one_source_out | -0.0140 | 125.5309 | 421.7590 |
| random_forest | leave_one_source_out | -0.0440 | 109.1779 | 427.9476 |
| ridge | leave_one_source_out | -0.0459 | 169.2727 | 428.3448 |
| svr_rbf | leave_one_source_out | -0.0320 | 104.4087 | 425.4924 |
| xgboost | leave_one_source_out | -0.0123 | 131.7957 | 421.4013 |

## Microwave diagnostic
- Extra-Trees full-data transformed-feature importance is descriptive only: c__cooking_medium_boiling/baking medium not reported; microwave conditions not reported=0.3511, c__cooking_medium_Microwave=0.0424, c__cooking_medium_microwave; 700 W, no water=0.0001, c__cooking_method_normalized_microwave roasting=0.0000, c__cooking_method_normalized_microwave=0.0000, c__cooking_medium_500 W microwave; covered vegetable vessel with 100 mL tap water below perforated tray=0.0000, c__cooking_method_normalized_microwave heating=0.0000, c__cooking_medium_microwave; 900 W, 6 mL water per 100 g=0.0000, c__cooking_medium_microwave; 800 W=0.0000, c__cooking_method_normalized_microwave cooking=0.0000, c__cooking_method_normalized_solid-state microwave cooking=0.0000, c__cooking_method_normalized_steaming then microwave=0.0000, c__cooking_method_normalized_microwave then steaming=0.0000, c__cooking_medium_microwave; 750 W=0.0000.
