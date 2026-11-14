# Historical `Retention_Final` molecular-grouped verification

## Verified historical result
- Dataset: `stageA/input/cookchem_molecular_retention_preprocessed.csv`, 1124 observations and 197 molecular groups.
- Target: `Retention_Final`.
- Model: `XGBoost_tuned`; 450 estimators, depth 3, learning rate 0.03, min child weight 3, subsample 0.8, column subsample 0.8, L2 lambda 5, seed 42.
- Split: five-fold `GroupKFold` on `Canonical_Molecular_ID`; saved OOF predictions establish each molecular group appears in one fold.
- Saved OOF recomputation: pooled R² 0.2832, MAE 34.6119, RMSE 138.6949.
- Mean fold R² 0.4004, SD 0.1890. The fold metrics are stored in `original_target_molecular_cv_metrics.csv`.
- The historical script builds preprocessing pipelines inside each outer training fold and applies log1p/expm1 to the target. Saved OOF predictions are complete and correspond exactly to input `Retention_Final` values.

## Scientific status
- This is a genuine historical result within its molecular-grouped design, not a result on the final 1,016-row dataset. The historical script and manifest state that `Retention_Final` construction is unresolved, so it is not a verified scientific retention target.
- It predates the later recovery packages and their explicit apparent-concentration-ratio target contract. It cannot be treated as a validated final-target result or as unseen-source generalisation.
- Batch 021 does not contain a `Retention_Final` column. A final-dataset original-target rerun is therefore not admissible and was not fabricated.
