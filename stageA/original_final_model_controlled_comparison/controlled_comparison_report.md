# Stage A original vs final controlled comparison

## Recovered contracts
- Original script: `Retention_Final`, log1p target transform/inverse expm1, 22 base features plus five engineered features, median numeric imputation, StandardScaler, constant Missing categorical imputation and one-hot encoding. The recovered original `XGBoost_tuned` configuration is 450 trees, depth 3, learning rate 0.03, min-child-weight 3, subsample/colsample 0.8, lambda 5 and seed 42. Its recorded validation was 5-fold GroupKFold by `Canonical_Molecular_ID`, not random and not source-held-out.
- Final dataset: `target_value_percent`, exactly `100 * cooked_concentration / raw_concentration`; it predicts an apparent concentration ratio, not cooked concentration and not total-mass retention. Final tests use raw concentration, process variables, descriptors, basis, compound class and food matrix; no source identifier or target-derived feature is supplied.
- `Retention_Final` cannot be scientifically equated to the final ratio: the original manifest says its source equation is unresolved, and that table has no cooked-concentration field.

## Recovered historical score
- The actual historical `stageA_benchmark_results.csv` entry for tuned XGBoost is pooled OOF R² 0.2832 and mean fold R² 0.4004. The often-cited approximately 0.4 is therefore mean molecular-grouped fold R², not a source-held-out score.

## Controlled results

| experiment | n | sources | pooled OOF R² | MAE | RMSE |
|---|---:|---:|---:|---:|---:|
| A_original_random_validation | 1124 | 183 | 0.3399 | 31.1000 | 133.1047 |
| original_compound_grouped_reproduction | 1124 | 183 | 0.2438 | 35.0753 | 142.4605 |
| B_original_source_grouped | 1124 | 183 | 0.0143 | 42.5498 | 162.6481 |
| C_final_ratio_random | 1016 | 32 | 0.4656 | 72.9584 | 306.1703 |
| D_final_ratio_source_grouped | 1016 | 32 | -0.0663 | 115.1449 | 432.5042 |
| E_cooked_concentration_random | 1016 | 32 | 0.7764 | 146.3236 | 1819.3908 |
| E_cooked_concentration_source_grouped | 1016 | 32 | 0.0255 | 321.0597 | 3797.9634 |

## Answers
- **1. Random validation?** The ~0.4 historical result was compound-grouped, not random. But molecule grouping still leaves papers in both training and test sets. The controlled original random result is 0.3399, with 83–92 overlapping sources per fold; source-held-out is only 0.0143. Thus source overlap, not merely literal random splitting, is the principal explanation for the high-looking original metric.
- **2. Original unseen sources?** No useful transferable performance: source-grouped R² is 0.0143, despite a positive random-fold score.
- **3. Target change?** Yes. The original target is unresolved `Retention_Final`; the final target is explicitly the apparent ratio. They are not interchangeable.
- **4. Cooked concentration harder?** Numerically it is easier in this pooled exercise (0.7764 random, 0.0255 source-held-out) than ratio (0.4656 random, −0.0663 source-held-out), but this is not a valid scientific superiority claim because the final master deliberately preserves heterogeneous units/bases. Both targets use the same 1,016 observations and identical random and source fold assignments; raw concentration is included because it is available before cooking.
- **5. Cleaning versus smaller sample?** The expanded final master is 1,016 rows, so it is not smaller than the 1,124-row original. The historical 439-row verified subset was smaller, but no one-to-one observation mapping or identical target exists here; a causal cleaning-only effect cannot be identified.
- **6. Expanded versus original?** Under random folds final ratio (0.4656) is higher than original `Retention_Final` (0.3399), but under source-held-out final ratio (−0.0663) is lower than original (0.0143). Because targets, provenance and feature contracts differ, these magnitudes are descriptive rather than a causal contest.
- **7. Transferable signal?** No. Source-held-out R² is near zero or negative, and strict cross-source replication remains absent.
- All transforms are fit inside training folds. Source IDs are used only for splitting/audit, never as features.

## Fold evidence
- `controlled_fold_metrics.csv` gives R², MAE, RMSE, train/test counts and source counts for every fold. `*_fold_assignments.csv` gives immutable row-to-fold assignments.
