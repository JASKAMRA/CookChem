# COOKRISK Phase 4 — Statistical and Historical ML Evidence Review

**Overall status: PARTIALLY COMPLETE**  
**Review date:** 2026-11-20  
**Phase 5/6:** Not started.

## Executive summary

The approved Reconstruction descriptive review and read-only review of named Batch021 historical ML evidence were completed as far as available records allow. Both approved dataset hashes and dimensions match. No model training, prediction generation, validation rerun, source-data edit, or historical artifact repair occurred.

Reconstruction contains 1,016 stored apparent concentration ratios (ACR). Mean=156.661%, median=88.377%, moment skewness=9.550; there are 97 upper Tukey flags. Excluding those flags from a sensitivity summary only gives mean=82.189% and median=82.714% over 919 rows. No data were changed or removed. Heterogeneous bases, DOI clustering, missing replicate metadata and incomplete analytical definitions preclude pooled inference or causal claims. ACR is not total-mass retention.

The Batch021 package has seven saved model families across compound-, food-matrix- and DOI-grouped evaluations. Three combined post1000 CSV files fail recorded SHA256SUMS checks. The current combined model comparison conflicts with checksum-matched per-model files and JSON/Markdown in 12/21 model/protocol rows. Both views show negative DOI-held-out R2 for every model, but values and ranking differ; no view was selected. A separate molecular/source ExtraTrees audit has a hash-matched Batch021 input and matching saved summary/fold/split/OOF checksums; pooled R2 is negative under both group strategies. Evidence does not support deployment, external-lab, temporal or real-world predictive claims.

## Scope and safety

Reviewed the required Phase 2 provenance and Phase 3 ACR reports/registers, approved Reconstruction and Batch021 identities, and named Stage A validation packages only. The restricted metrics catalog, Stage B, restricted Stage C/D materials, and Retention_Final source CSV were not accessed. Reconstruction was used only for descriptive statistics; Batch021 remained the historical ML evidence family. No existing source, dataset, registry, model, prediction, metric, validation output, dependency or lockfile was modified. No Git write operation occurred.

## Input identities

| Dataset | Approved role | Expected SHA-256 | Fresh SHA-256 | Shape | Result |
|---|---|---|---|---|---|
| stageA/dataset_expansion_1000/batch_021/updated_master_dataset.csv | Historical ML evidence | 111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8 | 111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8 | 1016 x 38 | VERIFIED |
| stageA/verified_concentration_ratio_reconstruction/final_verified_master_dataset.csv | Descriptive exploration only | f9391233a2d4231140d46aa58e864180eddb6f2c3a56b030df3f94ca25f083b0 | f9391233a2d4231140d46aa58e864180eddb6f2c3a56b030df3f94ca25f083b0 | 1016 x 43 | VERIFIED |

Molecular/source summary embeds the exact Batch021 input digest. Post1000 JSON lacks input_sha256; code/path and package sidecar link the adjacent Batch021 file, not a per-run digest.

| Combined Batch021 artifact | Actual SHA-256 | Sidecar SHA-256 | Result |
|---|---|---|---|
| post1000_model_comparison.csv | 2ba3635ceabd83311a82f4ad645096ad9be8a3ca86df5951b7734a58f44a97ff | 1f4358d154006d22f72b2334f6cbc5bbade964d257dcd54d6395b4a751a7dbac | MISMATCH |
| post1000_fold_metrics.csv | 3d9c94510f0808cac5600c3bd94c98978f0913f4d3fb44b772956e3d06a2c06a | cd6e98918560932a96a10dad3727688fcf8dd4902b899916aa426debb0206fef | MISMATCH |
| post1000_oof_predictions.csv | c24e5451e1726e92ffc4ac4e0e5f4eb4ed1a26f65857ad9f5239e4989f8de2db | 9d8471b9ceae36373cfda81473b321f781646b70fdd82543a4d4945a93cfa64d | MISMATCH |

The JSON summary, Markdown report and all 21 per-model comparison/fold/OOF component files match their sidecars. Component and JSON metrics agree for all 21 rows; current combined comparison differs for 12. The sidecar is a local checksum list, not a digital signature. The cause and intended output version are unestablished.

## Statistical methods and findings

After the Reconstruction hash gate, Python standard-library CSV parsing and arithmetic were used. Quartiles use linear interpolation; SD is sample SD; skewness is the unadjusted standardized third central moment; MAD is unscaled. These are descriptive statistics, not uncertainty intervals or inference.

### Descriptive distributions

| Field | Valid n | Missing | Mean | Median | Sample SD | Q1 | Q3 | Min | Max | Skew |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ACR target (% points) | 1016 | 0 | 156.661 | 88.377 | 419.047 | 56.619 | 120.199 | 0.000 | 6536.364 | 9.550 |
| Raw concentration (mixed units) | 1016 | 0 | 74.026 | 11.590 | 206.909 | 2.555 | 39.920 | 0.038 | 2484.000 | 6.434 |
| Cooked concentration (mixed units) | 1016 | 0 | 345.146 | 9.185 | 3849.322 | 2.080 | 43.373 | 0.000 | 72030.000 | 14.383 |
| Temperature_C | 438 | 578 | 135.671 | 100.000 | 121.457 | 100.000 | 120.000 | 80.000 | 900.000 | 5.701 |
| Cooking_Time_min | 810 | 206 | 14.994 | 10.000 | 16.621 | 5.000 | 15.000 | 0.050 | 105.000 | 2.799 |
| raw_sd (mixed units) | 412 | 604 | 2.581 | 0.170 | 8.401 | 0.030 | 1.290 | 0.000 | 68.400 | 5.584 |
| cooked_sd (mixed units) | 418 | 598 | 7.915 | 0.190 | 51.310 | 0.030 | 0.992 | 0.000 | 590.000 | 9.420 |
| RDKit_Molecular_Weight | 1016 | 0 | 316.924 | 286.239 | 161.102 | 176.124 | 493.098 | 75.067 | 610.521 | 0.478 |
| RDKit_LogP | 1016 | 0 | 3.240 | 1.490 | 5.001 | -0.646 | 4.209 | -2.420 | 12.606 | 1.019 |
| RDKit_TPSA | 1016 | 0 | 82.089 | 75.990 | 60.723 | 40.460 | 107.220 | 0.000 | 269.430 | 0.904 |
| RDKit_HBond_Donors | 1016 | 0 | 2.892 | 2.000 | 2.179 | 2.000 | 4.000 | 0.000 | 10.000 | 1.018 |
| RDKit_HBond_Acceptors | 1016 | 0 | 4.101 | 3.000 | 3.583 | 2.000 | 6.000 | 0.000 | 16.000 | 1.338 |
| RDKit_Rotatable_Bonds | 1016 | 0 | 4.846 | 3.000 | 3.418 | 2.000 | 8.000 | 1.000 | 12.000 | 0.595 |
| RDKit_Aromatic_Rings | 1016 | 0 | 0.858 | 1.000 | 0.893 | 0.000 | 1.000 | 0.000 | 3.000 | 1.020 |
| RDKit_Hydroxyl_Groups | 1016 | 0 | 2.791 | 2.000 | 2.198 | 2.000 | 4.000 | 0.000 | 10.000 | 1.078 |

ACR is stored target_value_percent using the documented 100 x C_cooked/C_raw equation. Raw and cooked concentration summaries pool mixed units/bases and have no common physical interpretation. Temperature_C has 438 nonblank values (578 missing); Cooking_Time_min has 810 (206 missing). RDKit descriptors are compound-level calculated fields repeated across observations, not independent measurements. Source-specific definitions were not re-adjudicated.

### Group support and clustering

| Grouping field | Labels | Missing rows | Groups n<5 | Groups n=5-9 | Groups n>=10 | Singleton groups |
| --- | --- | --- | --- | --- | --- | --- |
| food_matrix | 66 | 0 | 11 | 31 | 24 | 3 |
| compound | 51 | 0 | 18 | 4 | 29 | 0 |
| compound_class | 10 | 0 | 0 | 1 | 9 | 0 |
| cooking_method_normalized | 41 | 0 | 8 | 14 | 19 | 2 |

The data have 32 DOI families, no blank DOI, and all families contain repeated rows. The largest family has 84 rows; top three contribute 24.21%. Phase 3 documented 232 extra repeated DOI/compound/matrix/method contexts across 82 contexts. These are related rows, not established independent replicates. Compound/class labels include wording variants; no harmonization occurred.

### Missingness and outlier sensitivity

Blank counts: analytical_definition=451, reported_replicate_design=439, raw_sd=604, cooked_sd=598, Temperature_C=578, Cooking_Time_min=206. Phase 3 documented 20 concentration-unit labels and 15 basis labels, with 6 basis labels classified as unspecified. Raw/cooked compatibility remains unestablished; no paired food masses or validated yield establish total-mass retention.

The Tukey upper fence is 215.568607%; 97 values exceed it. ACR is >100% in 346 rows and >1,000% in 22; cooked concentration is zero in 2. Flags are review prompts, not errors. The sensitivity excludes high flags from a summary only; it is not a corrected dataset. Phase 3's 118 strict target differences remain unresolved at source precision; all matched displayed precision, but source rounding was not verified.

### Inferential analysis and limitations

No significance tests were run. Independence, a valid sampling unit, source-level measurement compatibility, pairing, replicate uncertainty and multiplicity plan are not established. Uneven groups, source clustering, heterogeneous units/bases, missing definitions/replicate design/SD, possible pseudoreplication and unverified source precision block inference and causal claims. Descriptive differences are noncausal; no p-values were generated.

## Historical ML evidence reviewed

Reviewed saved Batch021 post1000 outputs and the molecular/source validation audit. The former includes Dummy median, Ridge, Random Forest, Extra Trees, Gradient Boosting, SVR-RBF and XGBoost comparison metrics, folds, OOF outputs, summary, report, code and full-data Extra-Trees feature importance. A targeted package-level check found no serialized .pkl/.joblib/.model/.ubj estimator. No model or validation script was executed.

The model-specific runner uses GroupKFold(5) by canonical_molecular_id, GroupKFold(5) by food_matrix, and LeaveOneGroupOut by DOI (32 source folds). Fixed settings are in the code: RF/ET 10 trees; GB 25; XGBoost 10; Ridge alpha 10; SVR C=10/epsilon=0.1; seed 42 where configured. No tuning trace was located. A second static run_post1000_evaluation.py contains different 75-estimator tree settings and writes the same combined file names. This is a plausible alternate writer path, not proven cause.

Checksum-matched per-model/summary source-held-out R2 values are all negative (range -0.061816 to -0.012266); current combined values are also negative (range -0.065557 to -0.027488). The component/summary view has highest R2 for XGBoost (-0.012266); current combined CSV has highest R2 for Dummy median (-0.027488). The rankings differ. Do not compare/select across views. Post1000 values are pooled OOF metrics; mean-fold metrics were not derived.

The separate audit uses one ExtraTreesRegressor (25 trees, leaf=2, max_features=0.8, seed 42), five-fold GroupKFold and fold-local preprocessing. It distinguishes pooled R2 and mean-fold R2:

| Strategy | Pooled OOF R2 | Mean-fold R2 +/- SD | Pooled MAE | Pooled RMSE | Groups |
| --- | --- | --- | --- | --- | --- |
| molecular_grouped | -0.067833 | -0.256216 +/- 0.305977 | 102.391240 | 432.812778 | 48 molecular / 32 DOI |
| source_held_out | -0.065645 | -0.206527 +/- 0.193670 | 114.218984 | 432.369224 | 48 molecular / 32 DOI |

Molecular-grouped folds have zero molecular overlap but 17-20 DOI-family overlap. DOI-grouped folds have zero DOI overlap but 6-18 molecular-group overlap. They test different transfer questions. DOI holdout is not independent-laboratory holdout. Full-data feature importance is descriptive, not causal.

## Metric interpretation and leakage review

R2 is unitless; MAE/RMSE are target percentage points. Negative pooled OOF R2 describes residual variation relative to variation around the pooled target mean; it is not negative accuracy. Mean-fold R2 is distinct. Post1000 exact model values remain blocked by file-integrity/cross-file conflicts.

Reviewed feature lists exclude target_value_percent and cooked_concentration, so direct target-column leakage was not found in static code. The molecular/source audit includes raw_concentration, the target denominator; prediction-time availability is unspecified. Fold-local preprocessing is documented in code and saved audit. Tuning history, test reuse, exact complete row-level fold memberships, external source, temporal holdout, lab/site holdout and prospective deployment evidence are missing. Combined OOF lacks fold ID and fails its digest, so exact record-level leakage checks are blocked. No leakage PASS is claimed.

## What is supported

- **Historical evidence:** saved grouped Batch021 evaluations exist; the separate molecular/source audit embeds the exact Batch021 input hash; pooled and mean-fold metrics are separate.
- **Not independently reproduced:** model fits, predictions and metrics. No evaluation code was rerun.
- **Not supported:** positive unseen-source performance, external-lab transfer, temporal generalization, deployment, causal cooking effects, or total-mass retention from ACR.
- **Unresolved:** combined post1000 outputs fail their recorded digests and 12/21 metric rows conflict; intended version and cause are unknown.

## Errors and corrections

- The initial package probe under Python 3.14 raised `ModuleNotFoundError: No module named 'pandas'`. This was an environment limitation. No dependency was installed; standard-library CSV, JSON, hashing and arithmetic were sufficient.
- A long inline command was rejected by the execution launcher with: `MXC launcher: The target executable 'C:\Program Files\WindowsApps\OpenAI.CodexPrimaryRuntime.v26-1116-1220-0_26.1116.1220.0_x64__3k8sg7r9htsxt\dependencies\native\powershell\pwsh.exe' appears to be a packaged (MSIX) app. Packaged apps cannot be launched inside a sandboxed container. Uninstall the packaged version and install an unpackaged build.` No audit code ran from that command. It was replaced with a saved, scoped report helper and a short invocation; no software was installed or changed.
- The first helper run reported `FileExistsError: [WinError 183] Cannot create a file when that file already exists` for the new Phase 4 output directory. The helper file had already created its parent directory. The helper was corrected to accept its own directory and create it idempotently.
- The next helper run reported `NameError: name 'protocols' is not defined. Did you mean: 'protocol'?` in a new report-generation variable reference. The typo was corrected to the already-defined protocol map and the helper was rerun.
- A subsequent guard stopped with `Output reports already exist; refusing overwrite` after the previous run had written four partial Phase 4 CSVs. The directory was inspected; it contained only the new helper and those partial Phase 4 outputs. The guard was narrowed to allow only the helper and the seven explicitly named Phase 4 outputs; the incomplete report outputs were regenerated from the approved inputs. No pre-existing project evidence was touched.
- A later helper compile failed with SyntaxError: (unicode error) 'unicodeescape' codec can't decode bytes in position 2170-2171: truncated \UXXXXXXXX escape. Cause: a Windows path in a normal triple-quoted log string was parsed as an escape. Correction: make the generated log a raw f-string and rerun.
- The next compile attempt reported SyntaxError: unterminated string literal (detected at line 527). Cause: captured traceback text contained a triple-quote delimiter that closed the generated log literal. Correction: replace the delimiter/caret excerpt with plain explanatory text.
- The following compile attempt reported IndentationError: unexpected indent at line 526. Cause: the caret line remained after replacing the embedded delimiter. Correction: replace the caret excerpt with plain text.
- Review of the first generated report found that a literal substring check counted one basis label containing the exact word “unspecified”, while Phase 3's broader documented classification is six labels. Cause: lexical counting did not reproduce Phase 3's semantic category. Correction: use and label the Phase 3 documented six-label classification; source data remain unchanged.
- Review also caught a draft statistical-table sentence that combined two different target comparisons. The first concerned 118 stored-target versus recalculated-ACR strict differences; the second concerned 15 Reconstruction/Batch021 serialized cells. The table text was separated and corrected; no input or historical output changed.
- The final helper execution completed. No further errors occurred.

## Unresolved gaps and safe next action

See ML_PROVENANCE_GAP_REGISTER.csv and VALIDATION_DESIGN_REVIEW.csv. The evidence owner must identify the intended combined-output version and explain the hash/metric divergence before exact comparative claims are used. Do not regenerate or replace historical outputs under this task. Scientific inference requires compatible source-level measurements, replicate uncertainty and an identified independent sampling unit.

## Conclusion

Phase 4 is **PARTIALLY COMPLETE**. Safe descriptive and named historical-evidence checks are completed, but inferential analysis is scientifically blocked and consolidated post1000 metrics are inconsistent with checksum-matched component evidence. Do not close this as a validated-performance review until artifact provenance and scientific gaps are addressed. This does not imply a metric is false; its intended version and interpretation are not established. No Phase 5 work started.
