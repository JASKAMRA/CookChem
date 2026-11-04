# Stage A historical-versus-regenerated comparison — 2026-11-04

## Finding

**Stage A remains OPEN; no Stage B work was started.** The first observed divergence is in the fitted-model OOF predictions. Dataset values, target values, row/group alignment, GroupKFold validation membership, documented feature contract, model parameters and metric definitions show no recorded difference. Historical feature matrices, fitted preprocessing objects, model binaries, and full per-run environment/build metadata were not retained. Therefore the precise cause of the historical prediction difference cannot be proven.

Two independent runs under the new locked environment produce byte-identical OOF predictions, fold assignments/audit, tuning results, robustness results, and the new run manifest. The runner now emits path-independent `stageA_run_manifest.json` files with lock/code/input/output hashes, feature and fold assignments, preprocessing, models, packages, and platform; it does not reconstruct missing historical state. The integration test repeats the full benchmark in two fresh temporary trees and confirms byte-identical serialized outputs. This establishes repeatability of the current execution; it does not recover the missing historical environment.

## Dataset and row alignment

- Stage A input: `750124efc8b89dff1f67764064b1049b5db51fb1b2f222d4f91cd94c56945f89` (SHA-256); 1,124 rows, 47 input columns, 197 molecular groups. The runner verifies this hash before training.
- Historical OOF and regenerated OOF have identical `(Model, Record_ID, fold)` keys. All 5,620 actual target values and molecular IDs match the current file exactly; target differences: 0 rows, max absolute difference 0.
- For each model, historical and regenerated OOF row sequences both match the current input `Record_ID` order (1,124/1,124). The current input has 47 columns in the order shown in its CSV header. Historical run outputs do not retain the original source-column header/order or the input SHA, so that historical column ordering cannot be directly verified.

## Feature and target pipeline

- Tracked runner selects 22 ordered source predictors and constructs five deterministic features: `Temperature_C × Cooking_Time_min`, `log1p(Cooking_Time_min)`, `log1p(Initial_Concentration)`, `RDKit_LogP × Temperature_C`, `RDKit_TPSA × Cooking_Time_min`.
- Numeric preprocessing is median imputation plus standardization; categorical preprocessing is constant `Missing` imputation plus one-hot encoding (`handle_unknown=ignore`). Each transform is fitted inside each outer training fold.
- Runner does not construct the target; it consumes preprocessed `Retention_Final`, fits `log1p(y)`, and scores `expm1(clipped prediction)` on the original numeric scale.
- Historical feature matrices, transformed feature names, imputer/scaler state, and category vocabularies are absent. Thus there is no historical numeric feature array or digest for a direct feature-value diff. The versioned runner and model-selection documentation specify the same feature contract, but that cannot prove which exact implementation was executed for the old outputs.
- Current runner diff from `HEAD` includes input hash/validation checks, numeric target parsing, path-independent QA metadata, and a new run-manifest writer after training. The feature construction, preprocessing and estimator-fit code are unchanged. Historical execution provenance is not recorded.

## Fold-by-fold metrics

| Model | Historical MAE / RMSE / R² | Regenerated MAE / RMSE / R² | Δ RMSE |
|---|---:|---:|---:|
| ExtraTrees_reference | 31.964078264 / 141.308625749 / 0.255977895 | 31.969852036 / 141.341450390 / 0.255632196 | +0.032824641 |
| RandomForest | 33.026848031 / 143.092541454 / 0.237073874 | 33.025468357 / 143.073742774 / 0.237274318 | -0.018798680 |
| RBF_SVR | 34.781658537 / 141.439686646 / 0.254597124 | 34.781957342 / 141.440455754 / 0.254589017 | +0.000769108 |
| XGBoost | 35.419173781 / 139.489409564 / 0.275011755 | 35.586383992 / 141.218504760 / 0.256926607 | +1.729095196 |
| XGBoost_tuned | 34.611875903 / 138.694923156 / 0.283246831 | 34.662505483 / 138.410215057 / 0.286186463 | -0.284708099 |

The companion CSV contains all 25 model/fold comparisons, historical/regenerated row and group counts, overlap checks, fold metrics, target differences, prediction differences, and config comparison: [`stageA_historical_vs_regenerated_fold_comparison_2026-11-04.csv`](stageA_historical_vs_regenerated_fold_comparison_2026-11-04.csv). Exact train and validation molecular-group assignments for each of the five folds are listed in [`stageA_fold_group_assignments_2026-11-04.csv`](stageA_fold_group_assignments_2026-11-04.csv); historical validation membership is reconstructed from historical OOF fold labels, with training membership its complement.

- All 25 fold membership sets match. Train/validation row and group counts match, and group overlap is zero in both runs.
- Maximum absolute fold-metric differences across the 25 model-fold pairs: MAE 0.579371; RMSE 4.403477; R² 0.040129.
- The historical and regenerated fold-audit files are byte-identical (SHA-256 `1584f6025f807f1422080ae6a2d1d5c5865d7cb0a032dd36e84ddc750235bc8a`).

## Per-record prediction differences

| Model | Different predictions / 1,124 | Mean absolute difference | Maximum absolute difference |
|---|---:|---:|---:|
| ExtraTrees_reference | 1063 | 0.226509151 | 8.861521331 |
| RandomForest | 1082 | 0.245468158 | 12.654233851 |
| RBF_SVR | 949 | 0.008055816 | 0.277541252 |
| XGBoost | 1124 | 2.212736347 | 62.237731934 |
| XGBoost_tuned | 1124 | 2.076785206 | 28.147033691 |

Historical OOF SHA-256: `d4589732c5f9b90c01b23486edef40b86737b49e7a8921e7955576ae2e7e9e3b`. Regenerated OOF SHA-256 (same across two current locked runs): `c2c1c689f542118e45f2f96fa013db6831d5f7e05ad753c30874bc1e3fda2159`.

## Model configuration, metrics, and environment

- Both result files list the same five estimators and same selected tuned-XGBoost parameters: `n_estimators=450`, `max_depth=3`, `learning_rate=0.03`, `min_child_weight=3`, `subsample=0.8`, `colsample_bytree=0.8`, `reg_lambda=5.0`.
- Tracked runner config: ExtraTrees/RandomForest 300 estimators, leaf size 2, random state 42, one job; RBF-SVR `C=10`, `epsilon=0.1`, `gamma=scale`; XGBoost `tree_method=hist`, seed 42, one job. Historical summaries do not serialize every fixed parameter for untuned models; configuration is recovered from the tracked code/docs, not a historical run manifest.
- GroupKFold: 5 folds by `Canonical_Molecular_ID`; GroupKFold itself is not shuffled; seed 42 is used by estimators (seed 123 only in robustness sensitivity).
- Metrics are MAE, `sqrt(MSE)` and R². Independent calculations from historical and regenerated OOF prediction tables both match their saved summary metrics to floating-point precision.
- Historical environment records Python 3.12.14, NumPy 2.5.3, pandas 3.0.6, scikit-learn 1.9.1 and XGBoost 3.4.1, but omits a complete transitive lock, joblib/SciPy versions, platform/OpenMP version, and run-level package manifest.
- Historical QA stores an absolute input path under `C:\\Users\\kamra\\Desktop\\CookChem\\...` and the earlier reproduction instructions used PowerShell. This suggests the old run may have been on Windows, while the verified reruns were on macOS arm64. The path is not an explicit platform attestation, so a Windows-versus-macOS numerical effect is plausible but unproven.
- Current locked environment: macOS 26.6 arm64, Python 3.12.14, pip 25.0.1, NumPy 2.5.3, pandas 3.0.6, scikit-learn 1.9.1, XGBoost 3.4.1, SciPy 1.18.1, joblib 1.6.0, cloudpickle 3.1.2, narwhals 2.28.0, python-dateutil 4.0.0, threadpoolctl 3.7.0, tzdata 2026.6; Homebrew `libomp` 23.1.5.
- Repeatability under this lock rules out observed nondeterminism in the current environment. It cannot distinguish an unrecorded historical dependency/runtime difference from a different historical execution/configuration.

## Earliest divergence and closure

**Earliest observable divergence:** model-generated OOF predictions after fold-specific preprocessing and estimator fitting. No earlier difference is observed in available recorded data, target values, row alignment, fold membership, named feature contract, model parameters, or metric formulas. Because historical transformed feature matrices, fitted preprocessors, serialized estimators, and full environment metadata are unavailable, the exact internal step within fit/predict cannot be identified more narrowly.

Tests: `/tmp/cookrisk-stagea-locktest/bin/python -m unittest discover -s stageA/tests -v` — 12 passed; `pip check` — no broken requirements. Full benchmark and documentation generation were run only in disposable trees; stored outputs remain unchanged. RF-01–RF-15 are all PENDING (0/15 approved). Stage A inference remains blocked, and Stage B remains unstarted. **Stage A closure criteria are NOT SATISFIED** until this discrepancy is accepted as a bounded limitation or explained with recovered provenance, and Linux/Windows execution is validated or explicitly dispositioned.
