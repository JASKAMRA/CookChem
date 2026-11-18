# CookRisk Existing Scientific and Computational Results — Master Inventory

**Inventory date:** 18 November 2026  
**Task type:** read-only extraction of existing results. No model training, dependency installation, experiment rerun, dataset change, or historical-output overwrite was performed.

## Scope and status key

This inventory covers authorized Stage A research artifacts and the existing research-level evidence map. Stage B protected content was not accessed. Stage C/D source trees were not reopened because they are restricted in the current project context; any status about them is explicitly inherited/secondary and is not represented as freshly checked. Existing attached planning notes are not substituted for inaccessible source evidence.

- **A — REPORTED:** stored in an existing report, table, prediction, or plot; not independently rerun by this inventory.
- **B — REPRODUCED:** a prior repository report documents an independent rerun/check; this label does not mean we reran it today.
- **C — PROPOSED:** future work or a stated recommendation, not a result.
- **D — BLOCKED/UNVERIFIED:** insufficient current evidence, a recorded blocker, unavailable source, or artifact/snapshot mismatch prevents verification.

The machine-readable metrics catalog contains the canonical aggregate and fold rows discovered in the selected comparison tables. It preserves source paths and CSV row numbers. Per-model mirror CSVs are not repeated when a combined canonical table exists; their row-equivalent results are represented in the combined table.

## Executive findings

1. CookRisk contains several generations of Stage A data and modelling work, but the target contracts differ. The 1,124-row historical benchmark predicts `Retention_Final` after `log1p`; it is not established as ACR. The recovered research datasets use the explicit apparent concentration ratio `100 × C_cooked / C_raw`, and this endpoint is not total-mass retention.
2. Existing ACR results show weak transfer to held-out DOI families. The 439-row prototype's reported source-held-out R² values range roughly −0.0475 to −0.1104 across models. Batch 021 reports negative source-LOSO R² for every listed model. A controlled ExtraTrees audit on the 1,016-row Batch021 master reports R² −0.0678 for molecule-grouped and −0.0656 for DOI-held-out validation. These are separate analyses/snapshots and should not be pooled.
3. ACR can exceed 100%: the verified reconstruction reports 346/1,016 observations above 100%, range 0–6,536.364%, median 88.377%, mean 156.661%. These are concentration ratios and can reflect concentration, water/mass changes, extraction, or analytical variation; they are not mass-retention values.
4. A prior Stage A benchmark rerun is recorded as repeatable under its pinned Python 3.12.14 environment, and two clean runs produced byte-identical generated OOF predictions/fold assignments. The historical-vs-regenerated prediction discrepancy is unresolved because historical transitive dependency and run provenance were not preserved. This prior reproduction is not repeated here.
5. No supported general-purpose deployable model is established. Multiple package decisions explicitly retain “research prototype / not validated for deployment”; the final-prototype manifest states no saved model and no defensible general predictive model. The `.joblib` artifacts are experimental packages with explicit non-deployment restrictions.
6. Stage A is not fully closed: its closure record retains the historical discrepancy and RF-01–RF-15 human decisions as pending. Current environment could not rerun analyses (no compatible research environment checked into the active runtime); this inventory intentionally did not try.

## Dataset and target inventory

| Snapshot / release family | Reported coverage | Endpoint and semantics | Evidence/status notes |
|---|---|---|---|
| Historical Stage A benchmark input (`stageA/input/cookchem_molecular_retention_preprocessed.csv`) | 1,124 rows, 197 canonical molecular groups, 183 DOI families per controlled comparison | `Retention_Final`; Stage A reproduction uses `log1p`/`expm1`. Its original scientific equation is unresolved in the historical manifest. | Exact-byte SHA-256 recorded in Stage A closure: `750124efc8b89dff1f67764064b1049b5db51fb1b2f222d4f91cd94c56945f89`; prior run report says matches. Do not relabel as ACR. B for the documented fresh-run repeatability; historical equivalence D. |
| Recovery v0.2.0 | 117 source-pair observations, 24 molecular groups, 2 DOI families, 2 matrices | ACR `100 × cooked/raw`; basis-compatible pairs only. | Narrow initial verified dataset. Model table and experimental `.joblib` exist; deliberately non-deployable. A. |
| Recovery v0.3.0 | 338 rows, 45 compound groups, 6 DOI families, 9 matrices, 12 methods | ACR. 221 recovered historical rows added to the 117; report says no new literature rows. | Six DOI family counts documented; grouped and source LOSO results saved. A. |
| Recovery v0.4.0 | 374 rows, 46 groups, 7 DOI families, 14 matrices | ACR from compatible same-basis raw/cooked pairs. | 36 newly admitted independent-source rows. A. |
| Recovery v0.5.0 | 379 rows, 49 groups, 8 DOI families, 15 matrices and methods | ACR only. | One new DOI contributed five related potato/vitamin-C treatments; one candidate paper was excluded for unspecified basis, another remained pending for source-table access. A. |
| Recovery v0.6.0 | Same exact v0.5 parent, 379 rows; no new observations | ACR | Controlled source-confounding and ablation diagnostics. A. |
| Recovery v0.7–v1.0 | v1.0 remains 439 observations / 10 DOI families; v1.0 adds no observations and no strict protocol matches | ACR research track | Candidate investigations/harmonization and source-match feasibility; report explicitly says no model trained in v1.0. A/D depending on item; see gaps. |
| Final prototype (439-row family) | 439 eligible rows, 10 DOI families (per manifest) | Apparent concentration ratio, not total-mass retention | Current dataset bytes in the evidence map did not match the saved manifest parent hash. Saved outputs are reported but their association to present bytes is D until reconciliation. No saved model. |
| Batch021 / post-1000 family | 1,016 observations, 32 DOI families, 51 compound labels/48 canonical IDs, 66 matrices, 41 normalized methods | `target_value_percent = 100 × C_cooked / C_raw` | Adds 78 source-table pairs; verifies target calculation and exact duplicate experiment keys in its stored validator. A. Dataset hash not recorded in its manifest. |
| Verified concentration-ratio reconstruction | 1,016 observations, 32 DOI families, 48 molecular IDs, 66 matrices, 41 methods | `verified_concentration_ratio_percent = 100 × C_cooked / C_raw` | Different packaged reconstruction from the Batch021 master despite equal row/source totals; identity counts differ. Current exact-byte hash was recorded in the evidence map, but no matching data hash in manifest; do not treat as identical. A/D for hash provenance. |
| Strict/extended/exploratory recovery tiers | 338, 948, 989 arithmetic-matching candidate rows (tier-specific; source-heldout exploratory uses 971 rows after exclusions) | ACR, evidence-tier-specific | 338 strict source-verified; extended/exploratory tiers have looser evidence qualification. Never mix their metrics as one dataset. A. |

### Raw/cooked and retention endpoint findings

- The ACR research contracts require matching raw and cooked concentration units/bases. The ACR equation is an apparent concentration ratio. No inference of total analyte mass is warranted absent cooked yield/raw and cooked mass, moisture basis reconciliation, liquid disposition, and compatible measurement basis.
- The verified reconstruction report states raw/cooked concentration completeness of 100%/100%; temperature completeness 43.1%, cooking-time completeness 79.7%; descriptor completeness 100%. This is source-reported coverage, not freshly recomputed here.
- Its target summary: mean 156.661%, median 88.377%, SD 419.047, min 0, max 6,536.364; 346 values exceed 100%; 97 IQR outliers retained. Outliers above 100 are kept for review and are not automatically corrected.
- The current 1,124-row benchmark contains `Retention_Final` and `Apparent_Increase`; its reproduction contract is `Retention_Final`. Historical target semantics are unresolved. Cooked concentration in the controlled 1,016-row experiment is yet another target, in heterogeneous units/bases, and is not directly comparable with ACR.
- Explicit true-retention statistics in one literature source are kept separate from ACR in the v0.7 harmonization report. No FW-to-DW conversion was performed there.

## Results register

### R-01 — Historical Stage A model benchmark (`Retention_Final`)
**Status:** A (saved historical comparison) and B (prior independent current-pipeline reproduction/repeatability, narrowly scoped).  
**Source:** `stageA/stageA_report.md` sections 2, 7–12; `stageA/outputs/stageA_benchmark_results.csv`; reproduction and closure reports.  
**Snapshot/target:** 1,124 rows, 197 groups; `Retention_Final`, `log1p` target and inverse `expm1`; 5-fold GroupKFold by `Canonical_Molecular_ID`.  
**Reported results:** Stage A current-pipeline OOF table: ExtraTrees R² .255978 / MAE 31.9641 / RMSE 141.3086; RF .237074 / 33.0268 / 143.0925; RBF-SVR .254597 / 34.7817 / 141.4397; XGBoost .275012 / 35.4192 / 139.4894; tuned XGBoost .283247 / 34.6119 / 138.6949. Tuned XGB improves RMSE/R² over the independent ExtraTrees aggregate but worsens MAE; the project retains ExtraTrees based on the combined tradeoff. Historical Phase 2 selected ExtraTrees fold-mean R² .380461, fold-mean MAE 31.9598, RMSE 123.0731; these fold means are not aggregate OOF metrics.  
**Reproduction/limitation:** A prior report records two clean Python 3.12.14 runs with byte-identical OOF/folds. Historical predictions remain discrepant: fold membership matched but 1,063/1,124 ExtraTrees predictions differed; historical full dependency provenance absent. Stored and regenerated results must remain distinct.

### R-02 — Stage A robustness and tail sensitivity
**Status:** A.  
**Source:** `stageA/stageA_report.md` §9; `stageA/outputs/stageA_robustness.csv`.  
**Target/snapshot:** same 1,124-row `Retention_Final` benchmark.  
**Result:** tuned XGBoost seed 42 vs 123: MAE 34.612 vs 34.901; RMSE 138.695 vs 139.133; R² .283 vs .279. Removing highest 1% actual retention only for sensitivity gave MAE 25.161, RMSE 46.020, R² .364; report identifies 12 extreme observations as disproportionate contributors to RMSE/R².  
**Limit:** sensitivity exclusion is not the primary analysis and does not justify deleting outliers.

### R-03 — Historical old-output reproduction and discrepancy
**Status:** B for the specific old-run reproduction documented in its report; unresolved historical reconciliation remains D.  
**Source:** `stageA/original_target_old_vs_new_reproduction/reproduction_report.md`, `experiment_comparison.csv`, `old_dataset_historical_vs_reproduced.csv`; `stageA/reports/STAGE_A_HISTORICAL_VS_REGENERATED_COMPARISON_2026-11-04.md`.  
**Result:** reported reproduced historical pooled metrics R² .275796, MAE 34.691844, RMSE 139.413911; mean fold R² .394287 with fold R² .379576, .079417, .491659, .506393, .514390. Stored historical pooled R² .283247; fold assignments matched 100%, max prediction delta 70.7551. A separate controlled comparison recovers stored tuned-XGB pooled R² .2832 and mean fold R² .4004.  
**Limit:** reproductions use recorded configuration but differ from stored historical values; do not choose the better score or claim exact reproduction.

### R-04 — Recovery v0.2 to v0.5 ACR model progression
**Status:** A.  
**Sources:** each version's `stageA_model_comparison.md`, `dataset_expansion_report.md`, `FINAL_ITERATION_2_REPORT.md`, and model/fold CSVs.  
**Results:** v0.2 (n=117, 24 compounds/2 DOI): RF R² .3210, MAE 12.6379, RMSE 24.0182; ExtraTrees R² .3012, MAE 12.3103, RMSE 24.3661 (RF lowest RMSE; ET lower MAE). v0.3 (n=338, 45 groups/6 DOI): best compound-grouped reported R² Ridge .3853; best MAE/RMSE RF 48.1166/163.3667, while all source-LOSO model R² are negative (Ridge −.1005, RF −.0512, ET −.0326, others near zero/negative). v0.4 (n=374, 46 groups/7 DOI): Ridge grouped R² .4123, ET MAE 44.0411, RMSE 151.3577; source-LOSO remains negative. v0.5 (n=379, 49 groups/8 DOI): RF grouped R² .3847, MAE 41.3572, RMSE 144.2958; source LOSO RF R² −.0628; ET source R² −.0393. XGBoost grouped R² .2978 and source R² −.0275.  
**Limit:** versions have different rows and source coverage; metrics are not a same-data model leaderboard. Fold rows and target contracts are versioned beside each output.

### R-05 — v0.6 source-confounding and feature ablation
**Status:** A.  
**Source:** `stageA/recovery_v0_6_0_2026_11_10/source_confounding_report.md`; `feature_ablation_comparison.csv`; `full_fit_feature_importance.csv`.  
**Target/snapshot:** v0.5 exact 379-row parent, ACR; no observations added.  
**Results:** full model grouped R² .4003, MAE 41.4568, RMSE 142.4551 vs source-LOSO R² −.0416, MAE 56.1391, RMSE 187.7438. Best source-LOSO MAE ablation is molecular-plus-cooking: R² −.0412, MAE 56.0980, RMSE 187.7090. Descriptor-only source-LOSO R² −.4171; cooking-process-only source-LOSO R² −.1114; food-matrix-plus-cooking source-LOSO R² −.0702. Full-fit importance for `cooking_medium_Microwave` is .6984. Prior v0.5 importance was .6725 for transformed microwave medium category.  
**Limit:** high-cardinality medium label is source-linked; importance is associational and potentially a source/protocol proxy, not a causal microwave effect. Source LOSO negative across all ablations.

### R-06 — 439-row final-prototype model comparisons and ablations
**Status:** D for verification against current dataset bytes; saved results are A as historical reports.  
**Sources:** `stageA/final_prototype_2026_11_10/model_comparison_report.md`, `model_comparison.csv`, `ablation_report.md`, `ablation_study.csv`, `manifest.json`.  
**Reported results:** Random split best XGBoost R² .4840 (MAE 37.0386, RMSE 123.0925); compound grouping best RF R² .2042 (MAE 42.5560, RMSE 152.8649); source split all negative, RF R² −.0475/MAE 51.5826/RMSE175.3872. Source split XGB R² −.1104. Ablation across source-heldout: cooking-only R² −.0669, MAE58.6208; descriptors-only R² −.1170, MAE72.2353; combined molecular+cooking+matrix R² −.0470, MAE53.3318.  
**Limit:** final-prototype manifest expects parent hash `d3960d…`; current file hash was observed as `475c60…` in prior authorized inventory. Therefore persisted metrics cannot be tied to the current data snapshot until reconciled. No model saved; no defensible general model per manifest.

### R-07 — Batch021 seven-model evaluation (1,016-row ACR master)
**Status:** A.  
**Sources:** `stageA/dataset_expansion_1000/batch_021/post1000_model_comparison.csv`, `post1000_validation_summary.json`, `post1000_fold_metrics.csv`, `dataset_expansion_report.md`.  
**Target/snapshot:** explicit ACR; n=1,016, 32 DOI, 51 compound labels, 48 canonical IDs, 66 matrices, 41 methods; 78 new direct primary-table pairs added, preserving the preceding 938.  
**Result:** 7 model families × 3 designs = 21 aggregate rows, and the package reports 294 fold metric rows; 21,336 OOF prediction rows are reported in package evidence. Source-LOSO R² is negative across every model. In one saved source-LOSO result set, SVR has MAE 104.4087/R² −.0320, XGBoost R² −.0123/MAE 131.80; best metric depends on model/summary version and is not a deployability basis. Strict source-replicated protocol cells are reported as zero. Full exact rows live in the CSV, not an inferred recalculation here.  
**Limit:** model comparisons are reported; no experiment rerun. Severe target tail (max >6,500%) affects RMSE. Manifest does not contain a dataset SHA; snapshot agreement needs a hash-linked manifest.

### R-08 — Controlled molecular vs DOI-held-out ExtraTrees audit
**Status:** A.  
**Source:** `stageA/molecular_vs_source_validation_audit/validation_comparison_report.md`, `validation_summary.json`, `validation_summary_rows.csv`, `fold_metrics.csv`, OOF and figures.  
**Target/snapshot:** Batch021 master, n=1,016, 48 molecular IDs/32 DOI, ACR. ExtraTrees 25 trees, leaf 2, max_features .8, seed 42; same feature recipe and five folds, only grouping variable changes; fold-local imputation/scaling/one-hot.  
**Results:** molecular-grouped pooled R² −.0678329, MAE 102.3912, RMSE 432.8128, mean-fold R² −.2562 ± .3060. DOI-heldout pooled R² −.0656454, MAE 114.2190, RMSE 432.3692, mean-fold R² −.2065 ± .1937. Molecular folds had zero molecule overlap but 17–20 DOI overlaps; source folds had zero DOI overlap and 6–18 molecular overlaps.  
**Limit:** both strategies negative; tiny pooled difference +.0022 is not consistent across fold-number comparisons; DOI is an imperfect independence proxy.

### R-09 — Dual evidence-tier sensitivity analysis
**Status:** A.  
**Source:** `stageA/dual_dataset_sensitivity_analysis/summary_metrics.csv`, fold metrics, integrity report, OOF tables.  
**Results:** strict 338 molecular grouped pooled R² .2855, MAE46.4983, RMSE164.37296; source-heldout R² −.04337, MAE65.3345, RMSE198.6381. Extended 948 molecular grouped R² .48283, MAE30.7058, RMSE93.8794; source-heldout R² −.01453, MAE41.5242, RMSE131.4875. Exploratory 989 molecular grouped R² .24988, MAE35.9635, RMSE149.5238; source heldout pooled R² .00777 on n=971 after excluding 18 unreliable-source rows, MAE46.4496/RMSE173.4949.  
**Limit:** evidence qualification differs by tier; changing rows and source filters change difficulty. Do not interpret extended/exploratory higher scores as better scientific validity or compare tier deltas causally.

### R-10 — Strict 338 source-verification subset negative result
**Status:** A.  
**Source:** `stageA/989_observation_recovery_audit/989_recovery_audit_report.md` and `molecular_grouped_model_metrics.csv`.  
**Result:** 338 observations, 45 molecular identities, 6 DOI families; fixed historical XGBoost molecular-CV mean fold R² −2.462845 (SD 6.775628), mean MAE46.6718, mean RMSE147.1589. Report states DOI overlap occurs in every molecular fold.  
**Limit:** not directly comparable with historical 0.4004 despite historical features/parameters because evidence-qualified subset/target provenance differs. 651 formerly excluded arithmetic matches divide into 610 metadata-missing/no contradiction, 23 pairing ambiguous, 18 DOI/source conflict; 81 discrepant and 54 non-comparable records remain separate. These are audit outcomes, not metric corrections.

### R-11 — Raw/cooked target and dataset integrity audits
**Status:** A.  
**Sources:** `stageA/verified_concentration_ratio_reconstruction/final_dataset_eda_report.md`; `stageA/final_dataset_historical_model_and_eda_audit/final_dataset_eda_report.md`; Batch021 `post1000_validation_summary.json`.  
**Results:** reconstruction reports 338 historical rows reverified; 0 corrected; 786 excluded; 678 newly primary-source-verified; max ACR formula difference .004822 pp. Batch021 validation reports 0 ACR formula deviations >.01 percentage points, max rounding deviation .004822 pp, zero duplicate experiment keys, zero missing DOI, and 2 preserved legacy rows with cooked concentration zero. Final dataset EDA reports max DOI family 84 rows and top three 246/1,016 (24.21%); temperature missing in 578 and cook time in 206.  
**Limit:** values above 100 are concentration-ratio phenomena, not total mass retention. Formula agreement verifies arithmetic, not source correctness or measurement-basis compatibility beyond package evidence.

### R-12 — EDA and subgroup diagnostics
**Status:** A.  
**Sources/outputs:** `stageA/verified_concentration_ratio_reconstruction/eda_plots/`; `stageA/final_dataset_historical_model_and_eda_audit/eda_plots/`; `stageA/diagnostics_v0_1_0_2026_11_10/target_distribution_analysis.md`; corresponding data tables.  
**Results:** EDA plots and tables cover target distribution, compound/source/matrix/method counts, descriptors, missingness, correlations, target by source/food/method, IQR outliers, and historical target distribution. 97 IQR outliers among 1,016 in one report; 346 ACR values >100. Findings are descriptive and document imbalance and sparsity.  
**Limit:** correlation/stratified variation does not establish cooking or molecular causality. Plots are cataloged separately.

### R-13 — OOF predictions, fold checks, and reproducibility artifacts
**Status:** B for specified prior benchmark reruns; A for saved OOFs not covered by that reproduction.  
**Sources:** `stageA/outputs/stageA_oof_predictions.csv`, `stageA/outputs/stageA_fold_results.csv`, package OOF files, fold assignment and split audit files, `stageA/STAGE_A_REPRODUCTION_AUDIT_2026-11-04.md`, `stageA/STAGE_A_CLOSURE_AND_TRANSITION_2026-11-04.md`.  
**Result:** existing benchmark contains 5 models × 1,124 OOF rows = 5,620 prediction records; prior audit checked row IDs/actuals/group alignment, all five folds, and two fresh-run outputs byte-identical. A separate historical-vs-regenerated prediction discrepancy is retained. Other package OOF tables exist for 439/1,016/strict-tier experiments; these are stored validation predictions and never new-record inference.  
**Limit:** current task did not recompute OOF metrics; OOF artifact presence alone is not independent reproduction.

### R-14 — Feature importance/ablation and error analysis
**Status:** A.  
**Sources:** `stageA/recovery_v0_6_0_2026_11_10/feature_ablation_comparison.csv`, `full_fit_feature_importance.csv`, final-prototype `ablation_study.csv`, importance outputs, source/compound/matrix/method OOF error summaries.  
**Results:** multiple feature sets were tested; cooking medium can dominate full-fit importance (~.698 in v0.6), while descriptor-only source-LOSO R² is −.417. Highest-1% tail removal improves sensitivity metrics, but is not primary. Error and subgroup tables stratify by DOI, compound, food, and method.  
**Limits:** feature importance is model-conditional and noncausal; error categories are confounded by study and measurement conditions; include output path in catalog.

### R-15 — Failed, negative, inconclusive, or blocked results
**Status:** A/D.  
- No model family establishes useful DOI-held-out transfer in the reported 1,016-row ACR results. This is a negative result, not proof that no molecular signal exists.
- `Retention_Final` historical predictions do not exactly match regenerated predictions, although fold assignments do; cause unresolved due absent historical transitive package/run records.
- Strict 338 qualified subset has very poor mean fold molecular R² (−2.46); not directly comparable to broad historical score.
- v1.0 acquired no new observations or strict protocol matches (zero); no model trained.
- Existing v0.5 candidate evidence includes one exclusion for unspecified fresh/dry-weight basis and one pending source table; these are evidence-acquisition outcomes, not negative biochemical outcomes.
- Final-prototype saved metrics are unverified against current dataset bytes because manifest parent hash differs.
- No independent cross-source experimental replication cells are reported in Batch021.
- Stage A inference/deployment is blocked; saved experimental `.joblib` artifacts are not verified deployable models.

## Model artifacts and intended use

Four `.joblib` files are inventoried under `stageA/recovery_v0_2_0_2026_11_10/model_package/`, v0.3.0, v0.4.0, and v0.5.0. Their package names mark them experimental concentration-ratio models; the v0.2 model manifest is specifically named `experimental_concentration_ratio_model.joblib`, later ones `experimental_apparent_concentration_ratio_model.joblib`. Version README/manifest and `DO_NOT_DEPLOY.md` restrict intended use to experimental/research inspection; they do not satisfy a verified deployable model package. Do not deserialize or use them for new-record prediction. Separately, Stage A 1,124-row benchmark stores OOF predictions/results, not a deployable fit artifact. The final-prototype manifest explicitly says `saved_model: false`, `model_scope_decision: C_NO_DEFENSIBLE_GENERAL_PREDICTIVE_MODEL`, and no Stage C integration authorized.

## Existing scripts and outputs (not executed here)

Reproduction/training scripts and configuration are present in version folders (e.g. `stageA/scripts/run_stage_a.py`, `stageA/recovery_v0_*/training_and_evaluation_scripts/`, `stageA/final_prototype_2026_11_10/run_final_prototype.py`, Batch021 runners). They are evidence of a path to reproduction, not proof a current user can execute it. Prior environment report records Python 3.12.14 and pinned dependencies for the main Stage A benchmark; current runtime was not used for analysis. Fold assignments, OOF prediction CSVs, manifests, model comparison tables, EDA tables, ablation CSVs, error summaries and figures are stored at their package paths.

## Access boundary

Only authorized Stage A and existing research-summary materials were consulted. Stage B protected data and any embedded snapshot were not accessed. Stage C/D source files were not reopened in this task. No data/model artifact was modified and no experiment was run. Five requested inventory files are additive under `research/`.

### R-16 — Controlled literature acquisition / dataset expansion batches
**Status:** A (source-admission and dataset-size reports; no new models were run in these batches).  
**Sources:** `stageA/dataset_expansion_1000/batch_001/` through `batch_021/dataset_expansion_report.md`, each batch manifest and source/provenance tables.  
**Reported sequence:** controlled master grows from 451 rows at Batch001 through 471 (B002), 488 (B003), 524 (B004), 539 (B005), 573 (B006), 600 (B007), 635 (B008), 667 (B009), 707 (B010), 719 (B011), 749 (B012), 757 (B013), 796 (B015), 828 (B016), 858 (B018), 914 (B019), 938 (B020), and 1,016 (B021). Missing batch numbers in that list were not silently filled from assumption; per-folder batch reports are the authority. The sequence adds individually reported raw/cooked source-table pairs under ACR with explicit exclusions for non-detects, aggregate endpoints, unresolved identity, incompatible/unspecified basis, or replicate expansion. Batch021 adds 78 pairs from a new source while preserving 938 parent rows.  
**Actual result:** the acquisition track reached the stated 1,000-observation count and 32 DOI-family count in Batch021. It does not establish a balanced or confirmatory dataset; most batch reports explicitly say no model retraining occurred.  
**Limit:** all rows are apparent concentration ratios, not total-mass retention. Dataset count growth is not itself independent validation. The reports preserve exclusions and unresolved candidates. See every batch report for exact DOI/table/method details; the metrics catalog separately includes model-result tables only.

### R-17 — Cross-source replication feasibility and targeted evidence acquisition
**Status:** A (reported feasibility findings); C for future acquisition decisions.  
**Sources:** `stageA/recovery_v0_7_0_2026_11_10/matched_evidence_report.md`; `stageA/recovery_v0_8_0_2026_11_10/candidate_b_extraction_report.md`; `stageA/recovery_v0_9_0_2026_11_10/complete_dataset_coverage_report.md`, `source_confounding_diagnostic_report.md`, domain readiness reports; `stageA/recovery_v1_0_0_2026_11_10/candidate_literature_investigation_report.md`, `iteration_summary.md`, domain modelling-readiness reports.  
**Reported results:** v0.7 reports 407 observations/9 DOIs and six categorical exact compound × food × method × basis overlaps, but only two source observations each; protocol identity remains insufficient. v0.8 adds 32 sweet-potato phenolic ACR pairs from one DOI; neochlorogenic acid values remain outside model-ready rows due to unverified canonical descriptor identity. v0.9 reports 439 rows, 10 DOIs, six categorical cross-source matches but zero strict, fully reported protocol-identical cross-source replications. v1.0 added zero observations and zero strict matches; no model was trained. Candidate literature decisions are documented, including evidence not admitted because basis labels, raw/cooked individual values, analyte identity, or protocol alignment did not satisfy the locked contract.  
**Limit:** the categorical overlap counts do not constitute strict independent replication. The reported decisions are evidence-screening findings, not measurements or experimental predictions.

## Research outputs inventory pointers

- **Dataset and source admission:** version manifests, `dataset_expansion_report.md` files, source provenance/mapping ledgers, exclusion/candidate audits, and target calculation audits in each Stage A release family.
- **Raw/cooked concentration analysis:** source-pair tables, `final_verified_master_dataset.csv`, `target_calculation_audit.csv`, `target_value_percent`, unit/basis matrices, and source locator columns. These are original reported measurements/calculated ratios; no additional raw/cooked result was generated here.
- **OOF/fold records:** Stage A `outputs/`, recovery v0.3–0.6 fold tables, final-prototype and Batch021 OOF/fold files, reconstruction split/fold audits, and source/molecular overlap matrices. The metrics catalog contains comparison and fold metric rows; prediction-level OOF data remain in their existing package paths.
- **Error/subgroup results:** source, compound, matrix and method error summary CSVs and OOF diagnostics in `final_prototype_2026_11_10/`, `dataset_expansion_1000/batch_021/`, `verified_concentration_ratio_reconstruction/`, `989_observation_recovery_audit/`, and `diagnostics_v0_1_0_2026_11_10/`. Their interpretation depends on each package's target and split.
- **Feature importance:** `recovery_v0_5_0_2026_11_10/feature_importance.csv`, `recovery_v0_6_0_2026_11_10/full_fit_feature_importance.csv`, final-prototype importance output, Batch021 ExtraTrees importance, and diagnostics importance. These are model-dependent descriptions, not causal effects.
- **Unresolved historical metric comparison:** `stageA/reports/STAGE_A_HISTORICAL_VS_REGENERATED_COMPARISON_2026-11-04.md` and `stageA/reports/stageA_historical_vs_regenerated_fold_comparison_2026-11-04.csv` are the most detailed current discrepancy references. No cause is invented.
