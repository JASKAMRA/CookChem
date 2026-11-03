# Stage A cooking-retention integration readiness

Audit updated: **2026-11-04**. Inspection and hashing below are read-only. Stage A was not imported, run, changed, retrained, or used to generate predictions.

## Decision

**BLOCKED — no Stage A prediction may be applied to food-composition data.** The adapter and its synthetic tests are implementation artifacts, not a deployed inference package or scientific approval. No prediction is admitted until a source-defined target contract, selected serving model, model artifact, reproducible runtime, output manifest, and scientific compatibility approvals are available. See the [deployment package specification and acceptance checklist](PHASE2_STAGE_A_DEPLOYMENT_PACKAGE_SPEC.md).

## Current Stage A handoff inventory

| Artifact | Read-only observation |
|---|---|
| Dataset in this workspace | `stageA/input/cookchem_molecular_retention_preprocessed.csv`; 1,124 rows / 197 molecular groups in `stageA/outputs/stageA_qa.json` |
| Workspace dataset SHA-256 | `cd51de3286d9fea7c4d87ce45f4c9c4301214b1944f72bff19c3b41ce0358c27` (computed 2026-11-04; it matches the expected hash recorded by the old model manifest) |
| Current runner SHA-256 | `a2de32f24600d18df6a503aba001ce4484295f0802b2ba7d09bbaa6bfc704d0c` (computed 2026-11-04) |
| Existing `stageA/outputs/stageA_oof_predictions.csv` | Cross-validation predictions for observed records; not an arbitrary-input inference interface |
| Serialized Stage A model and model hash | **Not found / not registered.** No Stage A serving estimator can be loaded through this contract. |
| Training environment lock and Stage A prediction manifest | **Not found.** The QA file records some package versions, not a full transitive lock or an input/code/model/output manifest. |
| `Retention_Final` target contract | **Not found.** It is used as a numeric target with `log1p` transformation, but its scientific operational definition and output basis are not established. |

The distinct Stage B artifact at `stageB/final_model/cookrisk_retention_stageB_selected.joblib` is not a Stage A deployment package. This audit did not load it, import Stage A, or run inference from either source. Stage B and its model artifacts remain outside this Stage A handoff.

## Reconcile model-selection statements before deployment

The model name is not currently a stable serving contract. The following statements have different meanings and must not be collapsed into “the deployed model is ready”:

| Source path | Source date / read date | Statement | Interpretation for deployment |
|---|---|---|---|
| `stageA/outputs/stageA_qa.json`, last modified 2026-10-29 11:52:47Z | Read 2026-11-04 | `best_stageA_model_by_RMSE` is `XGBoost_tuned`; selected tuning parameters are recorded. | Metric-specific best result only. It does not declare a serving artifact. |
| `stageA/stageA_report.md`, last modified 2026-10-29 11:52:47Z | Read 2026-11-04 | Retain Extra Trees as the current benchmark/selection because XGBoost's RMSE/R² gain comes with worse MAE and does not improve all metrics. | Overall model-selection decision, but still no serialized Stage A inference package. |
| `stageA/stageA_model_selection.md`, last modified 2026-10-29 11:52:47Z | Read 2026-11-04 | Extra Trees is the current selected benchmark among the earlier Phase 1–3 configurations. | Consistent with retaining the benchmark; it does not identify a serving artifact or bind a hash. |
| `stageC/reports/phase2/model_inference_readiness_2026-11-03.json`, last modified 2026-11-03 16:08:18Z | Read 2026-11-04 | `selected_model` is `ExtraTreesRegressor`; the file also reports its current input as `/Users/ayushkamboj3/CookChem/...` with SHA-256 `750124efc8b89dff1f67764064b1049b5db51fb1b2f222d4f91cd94c56945f89`, versus expected `cd51de3286d9fea7c4d87ce45f4c9c4301214b1944f72bff19c3b41ce0358c27`, and sets `sha256_mismatch=true`. | This is a dated audit from a different machine/path. The local Windows Stage A input was re-hashed on 2026-11-04 and is `cd51de3286d9fea7c4d87ce45f4c9c4301214b1944f72bff19c3b41ce0358c27`, matching the expected hash. Do not present the JSON's 7501… hash as the current workspace file. Rebuild the audit from this workspace before using any readiness fields. |

The checksum comparison is therefore explicit: **local Stage A file `cd51…` = manifest-expected `cd51…`; prior machine-specific audit value `7501…` ≠ `cd51…`.** The current adapter has no approved serving model name, artifact hash, or target-contract hash registered. It no longer treats either “best by RMSE” or a benchmark name as a deployment decision.

## Exact `Retention_Final` target questions

These questions are unresolved and block numerical integration. The model target name and its `log1p` transform do not answer them. Source owners must answer from the original cited methods/tables and the row-level derivation, not by assuming a familiar meaning for “retention.” See the [target adjudication register](RETENTION_FINAL_TARGET_QUESTIONS_2026-11-04.md).

## Implemented handoff and diagnostics

`stageC/src/stage_c/cooking_integration.py` accepts only caller-supplied, provenance-complete records. It never imports or executes Stage A. All eight scientific compatibility decisions are explicit `true` / `false` / `null`; output now includes a per-gate PASS/FAIL/PENDING explanation. A failed gate is incompatible, an unknown gate is pending, and passing all gates still does not substitute for scientific approval.

For a supplied model prediction, input and runner hashes must match the inspected hashes, a model/output/target-contract SHA-256 and runtime metadata are required, and `output_sha256` must verify against the canonical record (sorted-key compact UTF-8 JSON with the checksum field excluded). **Even a structurally valid record remains blocked** while the Stage A artifact, selected serving model, and `Retention_Final` target contract are unregistered. Every calculation response, complete or incomplete, carries prediction ID, provenance and gate diagnostics.

The new metadata-only package audit is exposed as `stageC/src/stage_c/deployment_package.py` and its Draft 2020-12 contract is `stageC/schemas/stage_a_deployment_manifest.schema.json`. It checks the detached manifest checksum, every listed artifact's SHA-256 and byte count, safe package-relative paths, model/target/runtime/feature/preprocessing/output/training references, feature order and units, explicit target numerator/denominator, and the serialization-library pin. It never loads a model or executes package code. A successful integrity result still returns `deployment_readiness=PENDING_REVIEW` and `inference_authorized=false`; file metadata cannot provide scientific approval.

The nine synthetic package-validator tests pass. They cover intact metadata-only package files, a changed file, missing runtime file, non-ratio target unit, absent denominator, mismatched preprocessing order, path traversal, wrong output-schema draft, and the acceptance-schema declaration. **No real Stage A deployment package was supplied or tested.** See the consolidated [owner response packet for RF-01–RF-15](RETENTION_FINAL_OWNER_RESPONSE_TEMPLATE.md); every owner answer remains pending.

Apparent concentration ratios are not treated as retention. Total-mass retention requires measured raw/cooked yield on the same supported unit basis. Concentration retention and total-mass retention remain separate semantics. All executable examples and tests use synthetic fixtures only.

## Current acceptance status

- Adapter contract and defensive calculation arithmetic: implemented; focused synthetic test module passes **19/19** when run with `PYTHONPATH=stageC/.test-deps` (Python package `jsonschema==4.26.0`). The test calls `Draft202012Validator.check_schema`, validates the fixture against Draft 2020-12, and rejects a ratio-unit retention record; formal schema validation **PASS**.
- Deployment manifest schema and metadata-only package validator: implemented; focused synthetic package tests **9/9 passed**. Validator reports integrity separately from readiness and never authorizes inference. The schema is JSON-parseable; formal Draft 2020-12 meta-validation should be included in the final active-schema pass.
- Consolidated owner response for RF-01–RF-15: created; **0/15 questions resolved**. Each row specifies scientific rationale, repository evidence, required decision/artifact, and consequence if unanswered.
- Phase 2 observed source-pair ledger: retained as the independent, source-backed observed evidence path; no source rows were modified here.
- Stage A predicted-retention path: blocked; zero Stage A inference executed and zero Stage A predictions consumed.
- Cooked estimates from Stage A: **0 eligible predictions**. Do not use out-of-fold rows or the separate Stage B model artifact as substitute inference output.
- Phase3-v0.1.2 and historical releases: preserved.
