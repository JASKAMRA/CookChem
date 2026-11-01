# Stage B script runtime audit

All 14 active files in `stageB/scripts/` were checked on Python 3.14.7 in `stageB/.venv/`. Model/result writers ran on an isolated copy of the required inputs and current outputs. The build/finalize/consolidate operations were not run as release operations; each was tested against the authoritative destination and correctly refused it.

The modeling, audit, validation, and mutation scripts have no command-line arguments and use script-relative project paths. `build.py` takes `source_release destination`; `finalize.py` takes `candidate`; `consolidate.py` takes `source_release destination`. These argument forms were checked through `--help` and guard tests.

| Script | Safe test result | Exit | Time (s) | Inputs | Outputs / safety |
|---|---:|---:|---:|---|---|
| `audit.py` | **PASS** | 0 | 1.94 | Reads the authoritative release and its SHA-256 manifest. | Writes `stageB/validation/release_audit.json`. Read-only with respect to the release. |
| `validate.py` | **PASS** | 0 | 6.87 | Reads `StageB_Final`; validator runs on a temporary release copy. | Writes validation JSON/CSV under `stageB/validation/`. Release contents are not written. |
| `mutation_tests.py` | **PASS** | 0 | 16.12 | Copies `StageB_Final` to a temporary directory and injects 12 test mutations there. | Writes mutation JSON/CSV under `stageB/validation/`. Mutations confined to disposable copies. |
| `build.py` | **PASS** | 2 | 0.71 | Explicit source release path and destination path. | Would create a staging build. Only authoritative-release refusal guard was exercised; no build created. |
| `finalize.py` | **PASS** | 2 | 0.69 | Explicit staging candidate directory. | Would update the named candidate. Only authoritative-release refusal guard was exercised; no candidate finalized. |
| `consolidate.py` | **PASS** | 2 | 0.76 | Explicit source release and destination directory. | Would create a consolidated release at the destination. Only authoritative-release refusal guard was exercised; no competing release created. |
| `audit_extreme_retention.py` | **PASS** | 0 | 4.27 | Stage A preprocessed retention dataset. | Writes extreme-retention audit tables and report. Executed against a disposable project copy. |
| `evaluate_missingness_features.py` | **PASS** | 0 | 96.08 | Stage A preprocessed dataset; runs 5-fold grouped validation. | Writes Step 2 metrics, folds, OOF predictions, and feature manifest. Executed against a disposable project copy. |
| `evaluate_tail_aware_models.py` | **PASS** | 0 | 106.53 | Stage A preprocessed dataset; grouped 5-fold model evaluation. | Writes Step 3 metrics, folds, and OOF predictions. Executed against a disposable project copy. |
| `evaluate_extreme_detectability.py` | **PASS** | 0 | 15.46 | Stage A preprocessed dataset; grouped 5-fold classification. | Writes Step 4 metrics, folds, and OOF predictions. Executed against a disposable project copy. |
| `evaluate_catboost.py` | **PASS** | 0 | 53.43 | Stage A dataset and Step 3 reference metrics. | Writes Step 5 CatBoost results, folds, and OOF predictions. Executed against a disposable project copy. |
| `tune_best_extra_trees.py` | **PASS** | 0 | 316.71 | Stage A dataset and Step 3 baseline; nested grouped tuning. | Writes Step 6 tuning log, metrics, folds, and OOF predictions. Executed against a disposable project copy. |
| `final_like_for_like_comparison.py` | **PASS** | 0 | 2.02 | Phase 2 summary and Step 3 fold results. | Writes Step 7 comparison and decision note. Executed against a disposable project copy. |
| `freeze_stageb_candidate.py` | **PASS** | 0 | 14.13 | Stage A preprocessed dataset; dataset row/group lock. | Writes selected model and manifest under `final_model/`. Executed against a disposable project copy; original model artifact untouched. |

**Totals:** 14 safe script checks passed; 0 failed; 0 blocked; 0 scripts without a safe check. The full build, finalization, and consolidation operations were **not run (3 operations)**; their safety guards were tested instead.

Complete captured stdout, stderr, exit codes, durations, and test modes: [`script_runtime_results.json`](script_runtime_results.json). First-pass model imports exposed missing XGBoost in the Stage B dependency file; it was added and all affected scripts passed on rerun.
