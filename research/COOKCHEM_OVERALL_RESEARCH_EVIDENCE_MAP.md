# CookChem/CookRisk Overall Research Evidence Map

**Checkpoint:** 18 November 2026 — inspection and evidence mapping only  
**Purpose:** professor-reviewable inventory of existing research, its target/data compatibility, and the limits of the evidence. This is not a claim that every cited source or model output has been independently reproduced.

## 1. Executive assessment

CookRisk has a substantial computational research record: source-linked raw/cooked observations, multiple ACR dataset reconstructions, feature and coverage audits, grouped/source-held-out model evaluations, out-of-fold predictions, ablation/error outputs, and reproducibility scripts. The strongest present contribution is a traceable experimental ACR research dataset and an honest demonstration that apparent in-sample/grouped performance does not establish transport to an unseen DOI family.

The project does **not** currently support a general-purpose cooking prediction model. Existing ACR source-family-held-out metrics are negative, strict protocol-identical cross-source replication is reported as zero, and there is no accepted deployable model. Dataset snapshots with the same row count are not necessarily the same observations or identities. In particular, `Retention_Final` in the Stage A benchmark is not automatically the ACR endpoint.

This checkpoint inspected Stage A and existing planning documents. Stage B was not accessed. Stage C/D source files were not opened; their statements below are inherited from an earlier planning tracker and are explicitly **not freshly verified** here.

## 2. Research questions and evidence status

| Research question | Existing evidence | Current conclusion supported | Limitation / status |
|---|---|---|---|
| What raw-to-cooked concentration changes are reported? | Two ACR-oriented 1,016-row packages contain raw concentration, cooked concentration, unit/basis, source locator and target fields; reported EDA includes target range/distribution. | The existing packages document a large set of reported pairs and calculate ACR as `100 × C_cooked / C_raw`. | The packages are different snapshots and not interchangeable. Primary-source values were not re-extracted in this checkpoint. |
| How does ACR vary by compound, matrix and method? | Coverage counts, source/matrix cross-tabs, method categories, target distribution, compound counts and grouped model features exist. | Descriptive stratification is possible and has been reported in part. | Source and protocol are clustered; unadjusted differences are not causal cooking effects. Some subgroups are sparse. |
| Can molecular and cooking features predict ACR? | Batch 021 and reconstruction packages contain fixed model evaluations and OOF predictions; older ACR prototype includes ablation outputs. | Models have been explored under grouped and source-held-out splits. | Every reported Batch 021 source-LOSO R² is negative. No model is supported for unseen-source prediction. |
| Are the existing experiments reproducible? | Scripts, locks, manifests, results, and instructions exist for several packages. | Some analyses are reproducible in principle. | Current Python is 3.14.7 with no pandas/NumPy/scikit-learn/matplotlib/XGBoost; no compatible Stage A environment was present. Some manifests omit hashes; one ACR manifest hash conflicts with current input bytes. No experiment was rerun here. |
| What evidence gaps limit stronger claims? | Stage A reports document zero strict cross-source replications and incomplete source-held-out generalization. | The immediate scientific gap is independent, protocol-comparable source evidence and a single owner-designated ACR snapshot. | Stage B was not inspected; Stage C/D status is only inherited from prior report summaries. |

## 3. Dataset and target inventory

Hashes marked **checked in this checkpoint** are exact-byte SHA-256 values calculated read-only on 18 Nov 2026; they were not added to or written into existing manifests.

| Snapshot / artifact | Size and target | Provenance and fields | Recorded result / use | Compatibility and reproducibility status |
|---|---|---|---|---|
| `stageA/input/cookchem_molecular_retention_preprocessed.csv` | 1,124 rows, 47 columns; contains `Retention_Final` and `Apparent_Increase`. `Retention_Final` is not established as ACR by its column name. | Source/DOI, molecular IDs, food/method/conditions, initial concentration, descriptors, and historical target fields. | Stage A closure register records it as the current benchmark input; 5-fold GroupKFold experiment uses `log1p(Retention_Final)` then inverse-transforms for metrics. | SHA-256 checked and matches Stage A closure record: `750124efc8b89dff1f67764064b1049b5db51fb1b2f222d4f91cd94c56945f89`. This is a distinct target from the ACR research title. Current register says rerun repeatability passed but historical predictions/metrics discrepancy remains open. |
| `stageA/recovery_v1_0_0_2026_11_10/expanded_clean_stageA_dataset.csv` and `stageA/final_prototype_2026_11_10/authoritative_v1_dataset_copy.csv` | Reported 439 eligible observations, 10 DOI families; target explicitly `apparent concentration ratio`. | The final-prototype package uses descriptors, raw concentration, temperature/time and method/medium/basis/compound-class/food-matrix features. Its report says canonical SMILES are not included in the 439-row dataset. | Existing model comparisons, folds, OOF, feature ablation, feature importance, source/food/compound errors and plots. No deployable saved model; package decision says no defensible general model. | Both current files have the same checked SHA-256 `475c60a737be166fca208f2573a9916eef7983e00b5ddbff39f336408c40134a`. The package manifest expects parent SHA `d3960dc6ec808ca1783cbb2c57d35fb4676da04feeff675280c1f07eb072005a`. **Mismatch:** stored outputs cannot be assumed to describe the current bytes until reconciled. |
| `stageA/dataset_expansion_1000/batch_021/updated_master_dataset.csv` | Reported 1,016 rows, 32 DOI families, 51 compounds, 66 food matrices, 41 normalized methods; explicit ACR target (`target_value_percent`, equation field). | Richer raw/cooked, source locator, identity, basis, protocol, descriptors, SD/replicate and retention-status fields. | `run_post1000_evaluation.py`, per-model runner, saved model comparisons, fold metrics, OOF predictions, source error and feature-importance files. Seven model families are reported: median baseline, Ridge, RF, Extra Trees, Gradient Boosting, RBF-SVR, XGBoost. | Current file SHA-256 checked: `d866d0ffab8c335e0469f2815c3cdf518b3d019be1bdf2e37ba2ced2e7d5d3c1`; package manifest records rows/parent/new batch but does not record this dataset hash. Existing reports say all seven source-LOSO R² values are negative; no strict replication cells. Model results are reported, not rerun here. |
| `stageA/verified_concentration_ratio_reconstruction/final_verified_master_dataset.csv` | Reported 1,016 rows, 32 DOI families, **48** canonical molecular identities, 66 matrices, 41 methods; explicit `100 × C_cooked/C_raw` target. | Reconstruction manifest describes 338 re-verified historical rows, 678 recovery-labelled primary-source rows, zero corrected historical targets, and 786 excluded historical rows. EDA reports 100% raw/cooked and descriptor completeness; temperature completeness 43.1%, duration 79.7%. | Contains per-row target calculation audit, source provenance manifest, identity manifest, split audit, EDA plots, fold metrics and OOF predictions. Fixed-configuration XGBoost comparison is reported. | Current file SHA-256 checked: `16dbbd9c38a21675a2644b415289004e5a8eb7091e97a96dae645ed2bf52be99`; the reconstruction manifest lists input/output names and counts but not this output digest. This package has 48 identities while Batch 021 has 51: same row count does **not** mean same dataset. Do not merge their metrics. |
| Earlier Stage A recovery/model packages (`recovery_v0_2`–`v0_5`) | Multiple smaller historical datasets and targets; exact counts/targets differ by version. | Versioned manifests, source/evidence reports, target contracts and feature sets exist. | Serialized `.joblib` models are present in v0.2, v0.3, v0.4 and v0.5 packages. Their package documentation labels them experimental/DO NOT DEPLOY. | These artifacts must not be treated as models for the current 1,016-row ACR snapshots without a verified dataset/target/environment match. Artifact contents were not loaded. |

### Dataset compatibility rule

Keep at least these three analytic families separate:

1. **Historical `Retention_Final` benchmark:** 1,124 rows; not automatically ACR.
2. **Batch 021 ACR expansion:** 1,016 rows / 51 identities; source-family evaluation package.
3. **Verified ACR reconstruction:** 1,016 rows / 48 identities; distinct reconstruction and XGBoost comparison.

The 439-row prototype is an earlier ACR package whose current parent bytes do not match its recorded manifest. A row-count match, similar project name, or shared DOI count is not sufficient to combine data or metrics. Do not use OOF predictions as new-record predictions.

## 4. Existing experiment evidence map (E1–E9)

Status legend: **Existing/reported** means artifacts/reports exist; **reproduction needed** means results were not rerun in this checkpoint; **blocked** means the present environment, input identity, or independent evidence gate prevents a responsible new execution.

| ID | Research question and data/target | Method / existing result | New execution needed? | Reproducibility, validation and limitation |
|---|---|---|---|---|
| E1 | What raw-to-cooked concentration pairs exist? ACR 1,016-row packages; raw/cooked concentration and explicit ACR formula. | Reconstruction EDA reports 1,016 pairs and max target recomputation difference 0.004822 pp; all raw/cooked values reported complete. Batch 021 reports two inherited zero-cooked Vitamin-C rows retained and disclosed. | No new scientific experiment now; source-level verification/reconciliation remains. | Reports and audit artifacts exist. This checkpoint did not re-extract papers or validate every row. ACR describes concentration ratio only. |
| E2 | How do ACR observations vary across compounds? Separate each ACR snapshot; do not use `Retention_Final`. | Compound counts, target distributions and fold predictions exist. Reconstruction reports 48 identities/largest compound 130 rows; Batch 021 reports 51 identities. | Descriptive compound-wise summary should be regenerated only after snapshot selection. | No inferential claim is supported by counts alone; compound is confounded with source/matrix/protocol. |
| E3 | How do reported ACRs differ by cooking method? Use exact source method, normalized labels, time/temperature, basis. | 41 normalized labels and source × method/matrix tables exist in Batch 021; final prototype has method-feature analyses. | Reproduce stratified descriptive analysis after freezing one ACR dataset. | Not a causal comparison: method, food, compound, basis and source are entangled; time/temp missingness is material. |
| E4 | Can existing ACR benchmark be reproduced? Candidate: Batch 021 and/or verified reconstruction; do not substitute 1,124 `Retention_Final`. | Batch 021 runner and reconstruction builder/evaluation outputs exist. Separate 1,124-row Stage A benchmark was already reproduced twice according to its register, but with a different target. | Yes, but only in a disposable copy after exact snapshot/environment validation. | Not run here. Python 3.14.7 lacks pandas, NumPy, scikit-learn, matplotlib and XGBoost; the documented 3.12.14 lock environment was not present. The 439-row package has a parent-hash mismatch. |
| E5 | Does performance transfer to unseen compounds? ACR evaluations with canonical molecular grouping. | Batch 021 reports compound-grouped five-fold metrics and OOF for seven models. Reconstruction reports XGBoost molecular-grouped mean fold R² 0.0835. | Reproduction is needed before using as a new finding. | A molecular-grouped split is not source-held-out validation. Historical benchmark metrics use a different target/data context and are not compared here. |
| E6 | Does performance transfer to unseen DOI families? | Batch 021 reports source-LOSO R² negative for every model; least-negative XGBoost R² −0.0123, MAE 131.80; RBF-SVR lowest MAE 104.4087 with R² −0.0320. Reconstruction XGBoost reports source-held-out pooled R² −0.0737 and mean-fold R² −0.2535, MAE 115.4329, RMSE 434.0021. | Reproduce both separately if each snapshot is retained; do not combine. | Evidence indicates poor source transfer in both reported analyses. These exact results remain report-derived until clean-copy reproductions. Strict protocol-identical source replication is reported as zero. |
| E7 | Do molecular descriptors and cooking features improve ACR prediction? | Four feature-set ablations exist in the 439-row package (descriptors; experimental/process; combined; plus matrix). Batch 021/reconstruction feature pipelines use numeric RDKit descriptors and categorical cooking/matrix features; no fingerprints are reported there. | An ACR 1,016-row ablation is a proposed new experiment, not an existing result. | The 439-row result is subject to the manifest/input mismatch. Importance is association within a fitted model, not causation. Verified structures/fingerprints may be inadequate; no fingerprints should be invented. |
| E8 | Where are large errors and unstable subgroups? | Batch 021 has per-source LOSO errors and feature importance; 439-row package has error-by-DOI/compound/matrix and largest source-held-out errors; OOF files exist. | Reproduce on the selected, hash-frozen dataset before interpreting residuals. | Outliers and zero-cooked legacy rows must remain visible; subgroup summaries need sample counts. Residual patterns can diagnose, not establish causal mechanisms. |
| E9 | What prevents stronger scientific conclusions? | Stage A compatibility, source-confounding, coverage and decision reports; evidence acquisition status in continuous log. | No model run required to report known gaps; updates need evidence review. | Main blocker: lack of strict independent protocol-matched replication and poor source-held-out performance. RF-01–RF-15 are documented pending in the Stage A register; no inference claim follows. |

## 5. Stage boundary and cross-stage evidence status

| Stage | Status for this checkpoint | Evidence treatment |
|---|---|---|
| Stage A | Inspected read-only, including source code, reports, manifests, dataset headers/row count and exact-byte hashes. No training, model loading, tests, installation, or file writes occurred. | Detailed above. Any metrics are cited as existing reports, not newly reproduced. |
| Stage B | **NOT INSPECTED — protected.** | No source files, embedded snapshots, data, hashes, counts, or contents were accessed. Prior planning summaries are not a substitute for authorized custodian review. |
| Stage C | Source files and datasets not inspected in this checkpoint. | Only the prior `reports/research_prototype/COOKRISK_EXECUTION_TRACKER.md` summary is available as inherited context; it reported 117 Phase 2 observations and zero accepted cooked estimates and a pending portability gate. This was not refreshed or verified here. |
| Stage D | Source files and datasets not inspected in this checkpoint. | The same prior tracker reported 342 records pending, zero decisions, and external service/benchmark requirements. This is inherited report-derived context, not current verified status. |

## 6. Strongest existing contributions and limitations

### Strongest contributions

- A reproducible Stage A benchmark framework with exact input hash guard, grouped folds, saved OOF outputs, metric recalculation, repeated-run checks, and a recorded remaining historical discrepancy.
- A large ACR-focused, source-linked dataset reconstruction with record-level target/provenance audits and an explicit exclusion ledger.
- A separate Batch 021 ACR evaluation with compound-, food-matrix- and source-family-held-out performance, fold metrics and OOF predictions.
- Existing 439-row ACR feature-ablation/error-analysis package and earlier experimental `.joblib` artifacts, all clearly limited from deployment claims.
- Consistent scientific language in reports distinguishing ACR from total-mass retention and acknowledging poor source generalization.

### Claims not currently supported

- A model that generalizes to new source families or laboratories.
- Independent validation: no strict protocol-identical cross-source replication is reported.
- Causal effect of a cooking method from the observational source-clustered data.
- Total-mass retention, bioavailability, human exposure, or clinical risk from ACR alone.
- One combined dataset of 1,124, 1,016, and 439 rows or a single set of metrics across those packages.
- A deployable model from saved OOF predictions or an experimental model artifact.
- Fresh Stage B/C/D completion or acceptance in this checkpoint.

## 7. Reproducibility and evidence references

Primary Stage A references inspected:

- `stageA/STAGE_A_CLOSURE_AND_TRANSITION_2026-11-04.md`
- `stageA/STAGE_A_REPRODUCTION_AUDIT_2026-11-04.md`
- `stageA/STAGE_A_RF01_RF15_EVIDENCE_MATRIX_2026-11-04.md`
- `stageA/STAGE_A_RF01_RF15_HUMAN_DECISION_HANDOFF_2026-11-04.md`
- `stageA/stageA_reproducibility.md` and `stageA/stageA-requirements-py312.lock`
- `stageA/CONTINUOUS_RECOVERY_LOG.md` and `stageA/CONTINUOUS_RECOVERY_STATE.json`
- `stageA/dataset_expansion_1000/batch_021/manifest.json`, `post1000_validation_and_evaluation.md`, `run_post1000_evaluation.py`, `run_one_post1000_model.py`, and saved reports/outputs
- `stageA/verified_concentration_ratio_reconstruction/manifest.json`, `README.md`, `model_evaluation_report.md`, `final_dataset_eda_report.md`, `build_reconstruction.py`, source/split/target audits and OOF outputs
- `stageA/final_prototype_2026_11_10/manifest.json`, `run_final_prototype.py`, `reproduction_instructions.md`, `model_scope_and_limitations.md`, ablation and error reports
- `stageA/989_observation_recovery_audit/` and `stageA/final_dataset_historical_model_and_eda_audit/` reports

Current environment check: CPython 3.14.7; no Stage A ML dependencies were available (`pandas`, NumPy, scikit-learn, matplotlib and XGBoost absent). No package was installed. No test or model run was executed. `stageA/stageA-requirements-py312.lock` documents Python 3.12.14 for the registered benchmark reproduction, but that environment was not present at the checked temporary path.

## 8. Recommended next action

Before further analysis, the Stage A owner should designate one canonical ACR snapshot for this research package. Recommended candidate for review is `verified_concentration_ratio_reconstruction/final_verified_master_dataset.csv`, because its report records explicit ACR semantics, row-level provenance/target audits, source counts, and exclusion reasoning. This is **not yet an approved canonical dataset**: its generated dataset hash is not included in its manifest and it differs from the Batch 021 dataset (48 vs 51 reported molecular identities despite both having 1,016 rows).

The next authorized research task should compare the candidate snapshots and source/identity dispositions, record exact-byte hashes for every input/output/configuration, approve the target contract and group keys, then reproduce E1–E3 and the existing Batch 021/reconstruction model results in an isolated copy. Until that is done, do not merge metrics, train a new model, or use any model for new-record prediction.
