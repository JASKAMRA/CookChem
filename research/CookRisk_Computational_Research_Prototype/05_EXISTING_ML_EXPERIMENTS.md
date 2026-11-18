# Existing Machine-Learning Experiments

All metrics below are existing saved results. **No model was trained in assembling this document.** Values are kept with their dataset, target, and validation design; they are not one cross-version leaderboard.

## Historical `Retention_Final` benchmark (1,124 rows)

Five model evaluations are reported under a 5-fold GroupKFold split by `Canonical_Molecular_ID`, with fold-local preprocessing and log1p/expm1 target handling in the current Stage A procedure. This result table does not establish that five serialized fitted models exist. The stored `stageA_benchmark_results.csv` aggregate OOF values are:

| Model | Pooled OOF R² | MAE | RMSE | Mean fold R² | Status |
|---|---:|---:|---:|---:|---|
| ExtraTrees reference | 0.255978 | 31.964078 | 141.308626 | 0.380461 | REPORTED; project reference retained |
| Random Forest | 0.237074 | 33.026848 | 143.092541 | 0.341500 | REPORTED |
| RBF-SVR | 0.254597 | 34.781659 | 141.439687 | 0.379352 | REPORTED |
| XGBoost | 0.275012 | 35.419174 | 139.489410 | 0.383296 | REPORTED |
| Tuned XGBoost | 0.283247 | 34.611876 | 138.694923 | 0.400376 | REPORTED; lower RMSE/higher R² but worse MAE than ExtraTrees |

Source: `stageA/outputs/stageA_benchmark_results.csv` and `stageA/stageA_report.md`. **Status: REPORTED** for these saved comparisons; prior reproduction evidence applies only to current-pipeline repeatability, not historical equivalence. ExtraTrees was retained because no alternative improved MAE, RMSE, and R² together. Historical Phase 2 selected ExtraTrees reports fold-mean MAE 31.959809, RMSE 123.073056, R² 0.380461; these are fold means and must not be confused with pooled OOF values. The target is not established as ACR, and its original unit semantics remain unresolved.

For all ACR model rows below, MAE and RMSE are on the ACR target scale and are **ACR percentage points**; R² is dimensionless. These are reported outputs unless explicitly identified otherwise.

## ACR model packages (versioned and separate)

| Dataset/snapshot | Model/result context | Existing reported result | Status and limitation |
|---|---|---|---|
| v0.2.0, n=117, 24 molecular groups, 2 DOI | Compound-grouped model comparison | RF pooled R² .3210, MAE 12.6379, RMSE 24.0182; ExtraTrees R² .3012, MAE 12.3103, RMSE 24.3661 | REPORTED; only two DOI families, non-deployable package |
| v0.3.0, n=338, 45 groups, 6 DOIs | Compound grouped and leave-one-source-out | Ridge grouped R² .3853; RF grouped MAE 48.1166/RMSE 163.3667; source-LOSO R² negative for every listed model | REPORTED; changed data from v0.2 |
| v0.4.0, n=374, 46 groups, 7 DOIs | Compound grouped and source LOSO | Ridge grouped R² .4123; ExtraTrees grouped MAE 44.0411/RMSE 151.3577; source LOSO remains negative | REPORTED; changed data |
| v0.5.0, n=379, 49 groups, 8 DOIs | Compound grouped and source LOSO | RF grouped R² .3847/MAE 41.3572/RMSE 144.2958; RF source R² −.0628; ET source R² −.0393 | REPORTED; source-heldout stress test |
| v0.6.0 controlled ablation, same 379 rows | RF feature ablations | Full feature set compound-grouped R² .4003; source LOSO R² −.0416; molecular+process source MAE 56.0980 | REPORTED; source/protocol confounding remains |
| Final prototype, reported n=439, 10 DOIs | Dummy/Ridge/RF/ET/XGB across random, compound, food and source validation | Source R² ranges from −.0276 (Ridge) to −.1104 (XGB) in saved source table; RF source R² −.0475 | REPORTED saved outputs; current-dataset attribution BLOCKED/UNVERIFIED because of the parent-hash mismatch; manifest says no fitted model saved |
| Batch021, n=1,016, 32 DOIs, 51 compound labels / 48 IDs | 7 model families × 3 validation designs | Saved table reports negative source-LOSO R² for all models; exact values are in source comparison CSV | REPORTED; source-transfer not demonstrated; zero strict source-replication cells reported |
| Verified ACR reconstruction, n=1,016, 48 IDs, 32 DOIs | Fixed historical XGBoost configuration, reduced semantic features | Compound pooled R² .059831, mean-fold R² .083504, MAE 91.328150, RMSE 406.117246; source-heldout pooled R² −.073710, mean-fold R² −.253519, MAE 115.432912, RMSE 434.002111 | REPORTED; not an exact historical feature replay |
| Batch021-labelled fixed ExtraTrees audit, n=1,016 | Same ExtraTrees recipe for molecular vs DOI grouping | Molecular pooled R² −.067833/MAE 102.3912/RMSE 432.8128; DOI-heldout R² −.065645/MAE 114.2190/RMSE 432.3692 | REPORTED saved values; input SHA-256 `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8`; exact input file unavailable, current Batch021 attribution BLOCKED/UNVERIFIED |
| Evidence-tier sensitivity: strict 338 / extended 948 / exploratory 989 | Molecular vs source-heldout, tier-specific | Strict molecular R² .285545/source −.043373; extended molecular .482825/source −.014530; exploratory molecular .249884/source .007768 on 971 source-eligible rows | REPORTED; tiers and source filters differ; not a monotonic model-performance comparison |
| Strict 338 recovered subset | Fixed historical XGBoost on verified rows | Mean molecular fold R² −2.462845 (SD 6.775628), mean MAE 46.671816, mean RMSE 147.158865 | REPORTED negative result; MAE/RMSE in ACR percentage points; not directly comparable with broad historical score |

## Model families and feature sets present

Saved comparisons include median baseline, Ridge, Random Forest, Extra Trees, Gradient Boosting, RBF-SVR, XGBoost, and tuned XGBoost. ACR ablations include molecular descriptors only, cooking/process features only, combined molecular+process, and versions adding food-matrix or removing source-linked medium variables. XGBoost was deferred in some versions when unavailable; CatBoost/LightGBM are described as deferred rather than tested in the Stage A report.

## Where to inspect original evidence

The package-specific fold results, OOF predictions, split assignments, errors, and manifests are in the source directories listed in [appendix A](appendices/APPENDIX_A_EVIDENCE_FILE_INDEX.md). Curated numerical rows are in [tables/EXISTING_METRICS_SELECTED.csv](tables/EXISTING_METRICS_SELECTED.csv); the full inventory table is `research/EXISTING_RESULTS_METRICS_CATALOG.csv`.
