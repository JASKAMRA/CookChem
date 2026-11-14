# Historical molecular-grouped CV reproduction

## Scope and safeguards
This is a read-only audit. It writes only this directory; no Stage A source dataset, historical output, Stage B/C/D content, Git state, or GitHub content was changed.

## Exact historical experiment recovered
- Old input: `C:\Users\kamra\Desktop\BTP\CookChem\stageA\input\cookchem_molecular_retention_preprocessed.csv` (1124 rows; 197 molecular groups).
- Target: `Retention_Final`.
- Split: 5-fold `GroupKFold` grouped by `Canonical_Molecular_ID`; random seed is 42 for XGBoost (the splitter itself is deterministic and unshuffled).
- Model: XGBoost tuned modal configuration persisted in historical code: 450 estimators, depth 3, learning rate 0.03, min child weight 3, subsample/colsample 0.8, L2=5, log1p target transform.
- Preprocessing is fit inside each outer training fold: numeric median imputation + scaling; categorical constant imputation + one-hot encoding. Five documented engineered features are included.

## Reproduction result
- Reproduced pooled R²: 0.275796; MAE: 34.691844; RMSE: 139.413911.
- Mean fold R²: 0.394287; fold R²: 0.379576, 0.079417, 0.491659, 0.506393, 0.514390.
- Saved historical pooled R²: 0.283247. Fold assignments matched: 100.0%; maximum prediction delta: 70.7551.

## Final Batch021 target recovery
- Final master: 1016 rows. `338` rows map uniquely by historical `Record_ID` and agree on normalized DOI and canonical molecule.
- For those matches, |`Retention_Final` − `target_value_percent`| has maximum 0.047107 and mean 0.003350; this supports the documented final apparent concentration-ratio target, with storage/rounding differences—not a separate reconstructed target.
- The remaining 678 final rows have no admissible historical-target mapping and were not assigned an invented target.

## Separate mapped-subset experiment
This is not an exact old-versus-new feature comparison. The final master lacks Pressure_kPa, Microwave_Power_W, Sample_Weight_g, Replicates_n, assay method, oil type, and the historical unit field. The subset run uses only named semantic counterparts (temperature, time, raw concentration, class, medium, method, food, and descriptors), with the same fold-local preprocessing, log target transform, XGBoost parameters, and molecular grouping. It does not substitute unavailable fields.
- Rows: 338; molecular groups: 45; DOI families: 6.
- Pooled R²: 0.313623; MAE: 47.218921; RMSE: 161.110649.

## Interpretation limits
The old full-data result is a molecular-grouped, not source-held-out, estimate. Molecular groups can appear in multiple DOI families across folds, so it does not demonstrate performance on unseen sources. The 338-row mapped test is smaller and uses a reduced feature set, so it cannot isolate dataset expansion from feature-schema change. It must not be presented as a deployable or source-generalisation score.

## Runtime
Python 3.10.11; pandas 2.2.3; scikit-learn 1.5.2; xgboost 3.2.0; Windows-10-10.0.26300-SP0.
