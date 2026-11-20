# Final Model and R2 Evidence Consolidation

Date: 2026-11-20

## Scope

Read-only consolidation of saved evidence through Phase 4. No training, predictions, pooled metric recalculation, source-data or application changes. Arithmetic fold means only were checked. The 1124-row historical Retention_Final benchmark, Batch021 ACR, Reconstruction ACR, and 338-row strict subset remain separate.

## Historical Stage A benchmark

| Model | Pooled R2 | Mean-fold R2 | Mean from five saved folds | Status |
|---|---:|---:|---:|---|
| ExtraTrees_reference | 0.255978 | 0.380461 | 0.380461 | pool: REPORTED â€” PROVENANCE INCOMPLETE; mean: VERIFIED FROM SAVED RECORDS |
| RandomForest | 0.237074 | 0.341500 | 0.341500 | pool: REPORTED â€” PROVENANCE INCOMPLETE; mean: VERIFIED FROM SAVED RECORDS |
| RBF_SVR | 0.254597 | 0.379352 | 0.379352 | pool: REPORTED â€” PROVENANCE INCOMPLETE; mean: VERIFIED FROM SAVED RECORDS |
| XGBoost | 0.275012 | 0.383296 | 0.383296 | pool: REPORTED â€” PROVENANCE INCOMPLETE; mean: VERIFIED FROM SAVED RECORDS |
| XGBoost_tuned | 0.283247 | 0.400376 | 0.400376 | CONFLICTING SAVED EVIDENCE |


All five initial means match the saved five-fold records. Each model has 1124 OOF rows and unique IDs. The output folder has no checksum sidecar; earlier reports document different historical and current source digests. Four model rows have empty parameter fields.

Tuned XGBoost conflicts with a separate saved replay: initial pooled/mean-fold 0.283247/0.400376; replay 0.275796/0.394287. Replay report, folds, OOF and comparison match their sidecar, but replay input SHA is absent. Preserve both and choose neither. The QA JSON R2=0.380461 is ambiguous and equals ExtraTrees mean-fold; do not show it as another pooled result.

## Batch021 ACR fixed audit

| Evaluation | Pooled OOF R2 | Mean-fold R2 | Status |
|---|---:|---:|---|
| Molecular grouped, GroupKFold(5) | -0.067833 | -0.256216 | VERIFIED FROM SAVED RECORDS |
| DOI/source-held-out, GroupKFold(5) | -0.065645 | -0.206527 | VERIFIED FROM SAVED RECORDS |

Both means match saved folds. Summary input SHA matches Batch021 111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8 and six targeted artifacts match sidecars. Historical saved results only; DOI is not proof of laboratory independence.

## Reconstruction ACR XGBoost

| Evaluation | Pooled R2 saved | Mean-fold R2 from folds | Status |
|---|---:|---:|---|
| Molecular grouped | 0.059831 | 0.083504 | pooled: REPORTED â€” PROVENANCE INCOMPLETE; mean: VERIFIED FROM SAVED RECORDS |
| Source held-out | -0.073710 | -0.253519 | pooled: REPORTED â€” PROVENANCE INCOMPLETE; mean: VERIFIED FROM SAVED RECORDS |

Saved model settings: 450 trees, depth 3, lr .03, min-child-weight 3, subsample/column-sample .8, L2 5, seed 42, log1p and fold-local preprocessing. Features are reduced versus historical. No output sidecar/build-time digest; not independently validated.

## Strict verified subset

338 rows: saved five-fold molecular mean is -2.462845 (SD 6.775628). Mean is VERIFIED FROM SAVED RECORDS. No pooled OOF artifact/value located; pooled R2 is UNVERIFIED / NOT ASSESSABLE.

## Phase 4 post1000 conflicts

21 per-model comparison/fold/OOF component files and JSON/Markdown summaries match their sidecars. All three combined comparison/fold/OOF files fail recorded hashes. Twelve of 21 comparison rows differ in R2, MAE and RMSE; both versions are recorded in the conflict register. Nine rows agree numerically, but the aggregate file remains checksum-invalid. Metrics are pooled OOF; mean-fold was not derived. Post1000 JSON lacks per-run input SHA. The alternate static runner is a possible, not proven, explanation.

## Friend-reported values

Pooled 0.3301 and mean-fold 0.2990: REPORTED â€” SUPPORTING RECORDS NOT FOUND. Both remain UNVERIFIED.

## Application display guidance

Current Existing ML Results filters to Batch021 fixed-audit rows; Validation & Generalization separates pooled and mean-fold values and plots saved folds. It does not display the Stage A benchmark, Reconstruction XGBoost, strict subset or post1000 multi-model set. If displayed, use exact statuses in the consolidated register. Show both conflicting tuned-XGBoost/post1000 values; never conflate pooled and mean-fold R2. Keep Retention_Final semantics unresolved and ACR distinct from total-mass retention. No application changes were made.

## Answers

1. Stage A pooled/mean-fold: Extra Trees .255978/.380461; Random Forest .237074/.341500; RBF-SVR .254597/.379352; XGBoost .275012/.383296; tuned XGBoost .283247/.400376.
2. All five initial means match saved fold arithmetic; tuned XGBoost also conflicts with replay mean .394287.
3. Batch021 fixed audit is consistent. Retention_Final is a different target/dataset; tuned replay conflicts; post1000 has 12 internal row conflicts.
4. Batch021 fixed Extra Trees pooled/mean values agree; separate post1000 has conflicts.
5. Reconstruction pooled/mean: molecular .059831/.083504; source-held-out -.073710/-.253519.
6. Strict subset mean -2.462845; pooled UNVERIFIED.
7. 0.3301/.2990 UNVERIFIED.
8. Three aggregate sidecar mismatches, 12 differing rows; alternate writer is only a hypothesis.
9. No evidence proves overwrite; originals remain present, while divergence is confirmed.
10. Keep model/dataset/split distinctions and display exact statuses from the CSV register.

Full-precision records and source paths are in the CSV registers. No existing reports or records were changed.
