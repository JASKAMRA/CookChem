# CookChem/CookRisk Computational Research Prototype Plan

**Planning checkpoint:** 18 November 2026  
**Purpose:** execution order for a professor-reviewable computational ML research prototype. This is not an implementation record. Stage B remains protected; Stage C/D material was not freshly inspected in this checkpoint.

## 1. Research aim and boundaries

**Working title:** *CookRisk: Machine Learning-Based Prediction of Cooking-Induced Changes in Bioactive Compound Concentrations.*

**Primary endpoint:** apparent concentration ratio (ACR), `100 × C_cooked / C_raw`, only where raw/cooked measurements refer to the same analyte and compatible matrix, measurement basis and units. Keep ACR separate from total-mass retention. Total-mass retention requires measured compatible raw/cooked food mass or a justified measured yield. Neither endpoint establishes bioavailability, human exposure, clinical risk, or cooking advice.

**Research aim:** characterize reported raw-to-cooked concentration changes, assess feature/model patterns under grouped validation, and determine whether those findings transfer to unseen source families. Negative and inconclusive findings are valid outcomes.

**Current conclusion from existing Stage A reports:** the ACR dataset/model work is promising as a research resource, but source-held-out results are poor/negative, there are zero reported strict cross-source protocol-identical replications, and no defensible general predictive model has been selected. No new inference claim is warranted.

## 2. Existing scientific work to preserve

1. Preserve all historical datasets, package outputs, `.joblib` artifacts, fold predictions and reports byte-for-byte.
2. Keep the 1,124-row `Retention_Final` benchmark separate from ACR datasets. The Stage A closure report says its current benchmark reproduction is complete and repeatable, but the historic-versus-regenerated prediction discrepancy remains open.
3. Do not merge the two reported 1,016-row ACR data frames: Batch 021 reports 51 canonical molecular identities; the reconstruction reports 48. Their current file hashes differ (`d866d0ff…d3c1` and `16dbbd9c…be99`, respectively), and their features/evaluation configuration differ.
4. Preserve the 439-row ACR prototype and its output history. Its manifest expects parent hash `d3960dc6…72005a`; the current parent/copy hash observed on 17 Nov is `475c60a7…40134a`. Reconcile this before treating its stored outputs as reproducible for current bytes.
5. Keep all OOF predictions labelled as held-out evaluation outputs. They are not fitted model inference for a new observation.
6. Maintain all RF-01–RF-15 decisions as pending until a documented owner/scientific reviewer decision is recorded. Do not infer an approval from project correspondence.

## 3. Research workflow

### A. Scientific data foundation

- Owner designates one ACR snapshot and version; record exact SHA-256 for raw inputs, curated outputs, scripts, feature contract, split configuration, and reports.
- Retain raw values and source units; store normalized values only with a verified formula and lineage.
- Build a data dictionary covering record ID, DOI/source family, source locator, compound and canonical identity, food matrix, preparation, time/temp/medium, raw/cooked values, measurement basis, replicate design, SD/uncertainty, ACR target, eligibility, and exclusion/review status.
- Audit duplicates at experimental-key level; distinguish technical assay repeats from independent cooking trials and source families.
- Preserve exclusions and unresolved identities/bases; do not “repair” values from assumptions.
- Do not call a snapshot “approved” until the project owner records the designation and any required scientific owner accepts its target and inclusion rules.

### B. Cooking-associated concentration analysis

- Start with per-record raw and cooked measurements in the source-reported unit and basis.
- Calculate ACR only for compatible pairs and retain calculation precision, reported rounding, and audit residual.
- Describe target distribution overall and by source; report count and denominator per table/figure.
- Present compound and cooking-method comparisons as descriptive and source-stratified first. Do not claim method effects from confounded observational comparisons.
- Flag ACR above 100% as concentration ratio behavior; never interpret it as increased analyte mass without mass/yield data.

### C. Computational ML evaluation

- Reproduce the existing ACR 1,016-row benchmark before adding models or features.
- Use one frozen dataset and identical outer splits for all model comparisons and feature ablations.
- Include median/mean baseline, Ridge/simple regression, Random Forest, Extra Trees, Gradient Boosting, RBF-SVR, and XGBoost only if present in the approved environment and justified by the registered configuration.
- Fit all preprocessing inside each train fold; no source/target leakage; source group means all rows from one DOI family are held out together.
- Report molecular-grouped and source-held-out results separately, including fold-level MAE, RMSE, R² (negative values included), records and groups.
- Do not choose a deployable model by ranking a negative source-held-out result. Do not tune on the confirmatory source holdout.

### D. Scientific pattern analysis

- Compare descriptor-only, process/cooking-only, combined, and combined-plus-food-matrix features with identical folds. Use fingerprints only if exact verified structures are available, sample support is adequate, and an ablation is prespecified.
- Analyze residuals by source, compound, matrix, method, and target range with subgroup sizes. Review large errors against primary sources before concluding they are model failures or data errors.
- Treat feature importance as descriptive model attribution, not a causal cooking mechanism.

### E. Evidence gaps and scientific limits

- Acquire independent, protocol-matched source observations before claiming cross-source generalization.
- Record missing time, temperature, medium, food state, basis, and replicate statistics explicitly.
- Keep source families, compound identities, foods and cooking protocols separate where incompatible.
- Stage B is not accessed; no interaction/evidence integration claim can be freshly verified in this checkpoint.
- Stage C/D are not freshly inspected. Prior planning records report Stage C accepted cooked estimates at zero and Stage D decisions pending, but those are inherited claims only.

## 4. Experiment register and execution decisions

| ID | Experiment | Dataset / target | Existing evidence | Execution decision now | Validation and limits |
|---|---|---|---|---|---|
| E1 | Raw vs cooked concentration pairs | One owner-designated ACR snapshot; raw/cooked units and basis retained | Reconstruction reports 1,016 raw/cooked pairs; ACR arithmetic audit and EDA exist. | Do not rerun now; first freeze snapshot/hash. | Recalculate ACR row-wise in isolated copy; disclose source rounding and incompatible records. |
| E2 | Compound-wise ACR | Same frozen ACR snapshot | Counts and distribution outputs exist; 48-vs-51 identity discrepancy across snapshots. | Proposed after identity/snapshot reconciliation. | Descriptive with source coverage and subgroup n; no causal interpretation. |
| E3 | Cooking-method ACR comparison | Same snapshot with exact source method + normalized category + conditions | 41 normalized methods and cross-tabs are reported for ACR packages. | Proposed after snapshot freeze; no new test here. | Stratify by source/food/compound, do not claim method effect where confounded. |
| E4 | Existing benchmark reproduction | Prefer the 1,016-row ACR reconstruction or Batch 021, but keep separate | Runners exist (`run_post1000_evaluation.py`, `build_reconstruction.py`); stored model results exist. | **BLOCKED for execution now:** no ML dependencies in active Python; current locked Stage A env absent; no install authorized. Prepare isolated scratch reproduction after environment is available. | Confirm exact dataset hash and compare outputs file-by-file; no overwrite. |
| E5 | Compound-grouped CV | Frozen ACR snapshot, canonical molecular IDs | Existing fold and OOF outputs reported for Batch 021 and reconstruction. | Reproduce as part of E4; no standalone training now. | Group separation audit, fold stability and adequate group counts. |
| E6 | DOI/source-family-held-out CV | Same snapshot, DOI family groups | Existing LOSO results are all negative for Batch 021; reconstruction also reports negative source-held-out performance. | Reproduce as part of E4. | Source-held-out is primary transport stress test, but source effects may combine method/matrix/assay shifts. Independent validation still required. |
| E7 | Feature ablation | Identical frozen source/compound splits | 439-row ACR package contains ablations; no equivalent 1,016-row ablation result identified in reviewed records. | Reproduce old ablation only after its hash issue is resolved; propose 1,016-row ablation only after E4 matches. | Prespecify families; same folds; no tuning on source holdouts; no causal claims. |
| E8 | Error/subgroup analysis | Frozen OOF predictions | Batch 021 source-LOSO errors and 439-row error-by-source/compound/matrix artifacts exist. | Recompute only after snapshot and OOF reproducibility is established. | Show sample sizes; inspect source record for large errors; retain all unexplained points. |
| E9 | Research evidence-gap analysis | All authorized Stage A evidence; protected stages marked unknown | Stage A compatibility/source-confounding/decision reports exist. | Can be maintained from documents without model training. | Stage B remains unknown; Stage C/D inherited status must not be represented as freshly verified. |

## 5. Model and feature plan

### Feature families

| Family | Existing availability | Planned handling |
|---|---|---|
| Molecular descriptors | Eight shared RDKit descriptors are reported complete in the reconstructed 1,016-row set. | Verify identity/descriptor consistency and recompute only in a separately authorized reproduction; record software version. |
| Molecular fingerprints | No fingerprint feature set identified in the current 1,016-row ACR runners; the 439-row report notes canonical SMILES absent from that dataset. | Do not fabricate structures. Consider only after verified structure coverage, preregistered fingerprint type/parameters, and adequate compound groups. |
| Food matrix | 66 matrices reported in ACR packages. | Categorical one-hot as existing benchmark, with source clustering and sparse-level risk disclosed. |
| Cooking method/medium | 41 normalized method labels reported; detailed medium and condition coverage varies. | Preserve original and normalized labels; do not impute missing protocol conditions as defaults. |
| Experimental conditions | Reconstruction EDA reports temperature 43.1% complete and duration 79.7% complete. | Report missingness; compare complete-case vs leakage-safe imputation only if prespecified. Keep sample weight, pressure, power, replicate, SD and assay where present in raw data. |
| Raw concentration | Included by 439-row final-prototype feature code; excluded from Batch 021 `NUM`/`CAT` list. | Feature set difference must be recorded; never compare metrics as if feature schemas were identical. |

### Model comparison protocol

1. Freeze target and eligible dataset; verify `target = 100 × cooked/raw` under source-compatible units and basis.
2. Lock record ordering and exact outer fold membership for compound-grouped and DOI-family-held-out designs.
3. Use a baseline and fixed predeclared configurations. If tuning is justified, nest it entirely within training folds.
4. Save fold metrics, pooled OOF predictions with record/source IDs, fit/config metadata, and output checksums to a new immutable run directory.
5. Report MAE, RMSE, R², fold distributions, n records/groups, target range, and baseline comparison. Negative/unstable values remain visible.
6. Only after exploratory analysis is frozen, obtain independent source data and run a blinded or locked confirmatory evaluation.

## 6. Research outputs to assemble (future authorized work)

- Versioned eligible-data manifest: exact input/output hashes, source list, inclusion/exclusion rules, target formula, software/config and snapshot owner designation.
- Data dictionary and source/identity/measurement-basis audits.
- EDA: dataset flow, target histograms/ECDF, source contribution, compound/food/method counts, missingness, target variation by source, and duplicate/leakage checks.
- Experiment configs: target, features, model parameters, seeds, groups, folds, metrics, environment and output paths.
- Reproduction record per existing benchmark with exact command and before/after hashes.
- Fold metrics, OOF predictions, predicted-versus-observed and residual plots, feature ablations, source/subgroup errors and fold-stability report.
- Scientific findings and limitations report that distinguishes exploratory, confirmatory, and blocked claims.
- Reproducibility manifest linking data, code, lockfile, run configuration, fold assignments and outputs by SHA-256.
- No new deployable model artifact unless an independent scientific gate and an explicit inference-package authorization pass. Existing experimental `.joblib` files remain preserved and marked non-deployable.

## 7. Recommended order of execution

### Step 1 — Snapshot adjudication (first milestone)

Ask the Stage A scientific owner to designate the canonical ACR snapshot and resolve why the two 1,016-row datasets contain 48 versus 51 canonical molecular identities. Reconcile the 439-row prototype’s expected `d396…` parent hash with current `475c…` bytes. Generate a new additive research manifest only after this adjudication; do not rewrite any existing manifest or dataset.

**Acceptance evidence:** owner decision record; exact raw/input/output hashes; explicit ACR target and eligibility; reconciled record/identity difference log; no input mutation.

### Step 2 — Reproducible environment

Use the existing Stage A Python 3.12.14 lock only after confirming its provenance and availability. Install only in an approved isolated environment in a later authorized execution. Do not alter the lock or use current Python 3.14.7 with missing dependencies as an implied reproduction.

**Acceptance evidence:** interpreter and platform; exact package versions/hashes; `pip check`; environment manifest; no project source/data writes.

### Step 3 — Reproduce descriptive and model outputs in a disposable copy

Copy the chosen dataset, approved scripts and configs to a temporary workspace; run the reproduction scripts there so historical package outputs stay unchanged. Validate dataset before fitting and compare generated hashes, fold membership, metrics and OOF alignment with the cited reports.

**Acceptance evidence:** exact command, temporary input hash, complete metric/fold comparison, output hashes, discrepancies and test results. No Stage B/C/D access.

### Step 4 — Reproduce or improve experiment design

Only after Step 3 matches, run same-split descriptor/process/matrix ablations and error analyses. Any changed feature definition or model configuration gets a new run ID, never overwrites historical evidence. Do not tune on the source-held-out test.

**Acceptance evidence:** preregistered config, fold-safe pipeline, equal folds across arms, fold-level metrics and uncertainty, error audit.

### Step 5 — Independent evidence and confirmatory evaluation

Arrange new protocol-comparable data from independent studies/laboratories. Predefine inclusion criteria, target, source grouping, metric and acceptance threshold with the scientific owner before examining outcomes. If no independent replication can be acquired, record that the generalization hypothesis remains unresolved.

**Acceptance evidence:** source provenance and compatibility review; locked independent set; predictions frozen before outcome reveal where feasible; independent review and complete result manifest.

### Step 6 — Professor review package

Assemble the evidence map, research protocol, one canonical dataset dictionary/manifest, scripts/configs, fold metrics/OOF outputs/plots, findings and limitations. Clearly label inherited reports versus reproduced runs. Do not build an application or imply clinical utility.

## 8. Explicit blockers and decisions

1. **Canonical ACR dataset:** owner must select among separate existing snapshots and resolve 48-vs-51 identity records.
2. **439-row package checksum:** owner/data maintainer must resolve the manifest `d396…` versus current `475c…` mismatch; no model reproduction should use that package until reconciled.
3. **Environment:** current Python 3.14.7 lacks all required ML libraries; approved Stage A 3.12.14 environment is not present. No install was made in this checkpoint.
4. **Historical target:** `Retention_Final` benchmark must remain separate from ACR until its scientific target semantics are explicitly adjudicated.
5. **Scientific decisions:** RF-01–RF-15 are pending in the Stage A register. Clarify which decisions block target interpretation/confirmatory claims versus exploratory ACR reproduction; do not infer approval.
6. **Independent evidence:** zero strict protocol-identical cross-source replications are reported; no generalization claim until independent evidence exists.
7. **Stage B:** entirely uninspected and unavailable in this plan; custodian authorization required for any future evidence integration.
8. **Stages C/D:** not accessed now. Prior status summaries are report-derived only and require separate authorization/verification before any cross-stage claim.

## 9. Stop conditions

- Do not train until a canonical ACR snapshot, exact byte hash, target/eligibility contract, reproducible environment, and permitted run scope are recorded.
- Do not overwrite package outputs, historical metrics, datasets, manifests, or model artifacts. Use a new isolated output path.
- Do not promote OOF predictions to new-record inference.
- Do not make deployment, causal, bioavailability, human-exposure, clinical-risk or cooking-guidance claims.
- Do not present Stage B/C/D work as newly inspected or validated.

## 10. Checkpoint result and recommended next action

This checkpoint created an evidence map and an execution plan only. No model was trained, no package was installed, no test was run, and no historical scientific artifact was modified.

**Recommended next action:** obtain a documented Stage A owner decision designating the canonical 1,016-row ACR reconstruction and authorizing an isolated, hash-verified reproduction of its existing E1–E8 analysis. Resolve its identity-count difference from Batch 021 and record the newly observed dataset hash before any training. This is the shortest path to a professor-reviewable research package because it fixes the unit of evidence first; running another model on an ambiguous snapshot would only add another incomparable metric set.
