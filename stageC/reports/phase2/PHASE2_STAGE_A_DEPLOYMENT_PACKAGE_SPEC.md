# Phase 2 Stage A prediction deployment package specification

Status: **SPECIFICATION ONLY — no deployable Stage A package exists.** This document defines the minimum immutable handoff that a model owner must provide before Stage C may consume model predictions. It does not authorize modifying or executing Stage A, and it does not authorize using Stage A cross-validation rows as inference.

## Package boundary and exact layout

Deliver a new versioned directory outside frozen Stage A and existing release folders, for example:

```text
stageA_inference_packages/StageA-Retention-v1.0.0/
  package_manifest.json
  package_manifest.sha256
  target/retention_final_definition.json
  model/model_artifact.joblib
  model/model_metadata.json
  runtime/requirements.lock
  runtime/python_version.txt
  features/feature_schema.json
  features/preprocessing_contract.json
  features/serving_transform.py
  schemas/prediction_record.schema.json
  tests/golden_inputs.jsonl
  tests/golden_outputs.jsonl
  tests/test_results.json
  provenance/training_input.sha256
  provenance/training_code.sha256
  provenance/training_environment.sha256
  reports/model_selection_and_validation.md
  reports/scientific_target_adjudication.md
  reports/independent_review.md
```

The package must be self-contained or identify every immutable external artifact by stable URI and SHA-256. A copied model file without its source manifest and verified dependencies is not a deployment package. The deployment artifact must be a fitted serving model, not a list of out-of-fold predictions and not a training/evaluation script that retrains at runtime.

The versioned manifest field contract is [`stageC/schemas/stage_a_deployment_manifest.schema.json`](../../schemas/stage_a_deployment_manifest.schema.json). The metadata-only checker is [`stageC/src/stage_c/deployment_package.py`](../../src/stage_c/deployment_package.py), called with `validate_deployment_package(package_directory)`. It verifies the detached manifest hash, package-contained artifact paths and symlink/traversal safety, every listed file hash/size, all referenced hashes, ordered feature consistency across model metadata/schema/preprocessing, the target unit/denominator, the runtime serialization pin, and Draft 2020-12 declaration of the prediction output schema. It never imports or executes any model/package code. A `PASS` only means supplied metadata and files are internally consistent; the checker always leaves deployment readiness pending independent review and sets inference authorization to false.

## Required manifest fields

`package_manifest.json` must contain:

- Contract version, package ID/version, status, build date, owner, and intended runtime interface.
- Exact selected model name/class and selection decision. `best_model_by_RMSE`, benchmark selection, and deployed model selection must be represented as distinct decisions.
- `model_artifact_sha256`, `training_input_sha256`, `training_code_sha256`, `serving_transform_sha256`, `target_contract_sha256`, `feature_schema_sha256`, and `prediction_schema_sha256`.
- SHA-256 for every package artifact plus an artifact path, byte count, and media type. The detached manifest checksum must be verified before loading.
- Python version and a complete lock of direct and transitive runtime dependencies, including serialization-library versions. Do not substitute a current environment observation for the environment that serialized the model.
- Feature names, types, units, preprocessing steps, missing-value policy, category policy, engineered feature formulas and order. It must identify whether engineered features number five or eleven and reconcile the discrepancy in current reports before release.
- A target contract ID and a structured definition of `Retention_Final` (see the target-adjudication register). Model output `semantic_type` must be derived from this reviewed contract, not supplied ad hoc by a caller.
- Dataset/source version, immutable input path/URI, file checksum, record/group counts, and source/rights provenance sufficient to reproduce the training snapshot.
- The output-record canonicalization algorithm and row-level output checksum rule.
- Test results tied to this exact manifest hash; independent scientific and software reviewers; known limitations and unsupported input domain.

## Prediction record contract

For each new input prediction, emit one JSON object containing:

- Unique `prediction_id`, scenario/food/compound record IDs, and exact feature input values including units and state.
- Package ID/version, model class/artifact hash, training-data hash, training-code hash, serving-transform hash, runtime/lock hash, and target-contract hash.
- Point prediction and any supported prediction interval, with unit, semantic type, measurement basis, denominator, and input domain/range checks.
- All eight explicit compatibility assessments required by `stage_c.cooking_integration`: compound identity, food identity, matrix, food state, cooking method, cooking conditions, measurement basis, and denominator. Unknown is pending, false is incompatible.
- Scientific review status, reviewer, review reference, and date. An output checksum computed over canonical UTF-8 JSON with sorted keys and compact separators after excluding the `output_sha256` field itself.
- Source-level provenance or an explicit statement that the value is model-predicted. Never label a prediction as a measured source result.

The current adapter requires an output SHA-256 over this canonical payload and refuses to admit it while no approved model, artifact hash, or target-contract hash is registered.

## Release acceptance checklist

### Scientific target and source basis

- [ ] Each `Retention_Final` question in `RETENTION_FINAL_TARGET_QUESTIONS_2026-11-04.md` is answered with original source/table/method references and row-level derivation evidence.
- [ ] Independent scientific reviewer signs the target definition and says whether the target is concentration retention, total-mass retention, apparent concentration ratio, or another quantity.
- [ ] Unit, numerator, denominator, sample/mass basis, treatment of moisture/yield and values above 100 are explicit and internally consistent.
- [ ] Same-analyte identity, food matrix, raw/cooked state, cooking condition, assay, and sampling point are recorded. Chemical transformations are not silently treated as retention.

### Model and reproducibility

- [ ] A single serving model is selected by a documented decision that reconciles `XGBoost_tuned` as the RMSE leader with the report's decision to retain Extra Trees as overall benchmark.
- [ ] The exact serialized fitted Stage A artifact exists and its bytes match the manifest hash. No Stage B artifact or OOF row is substituted.
- [ ] The training snapshot's exact bytes are available or immutably retrievable and match the manifest SHA-256. The hash is recalculated from the actual path in the release environment.
- [ ] Training/serving code, feature list/order, preprocessing, and engineered features have matching hashes and no hidden dependency on unversioned Stage A files.
- [ ] Python and transitive runtime dependencies are locked to the serialization-compatible environment; isolated installation succeeds without network-time resolution.
- [ ] Repeated golden-input calls produce the expected outputs, stable IDs and valid checksums; malformed, non-finite, out-of-domain, and unsupported-category inputs fail with actionable diagnostics.

### Stage C compatibility and review

- [ ] Prediction JSON Schema is Draft 2020-12 valid and rejects semantically impossible unit/target combinations.
- [ ] Output provenance hashes verify and point to the exact package and scenario input.
- [ ] All eight compatibility gates are individually reviewed and explicitly true for the specific application; any false/pending gate blocks calculation.
- [ ] Independent scientific review is `approved` with named reviewer, date and durable review reference. Code review alone is not scientific approval.
- [ ] One controlled synthetic end-to-end test verifies provenance preservation, compatibility diagnostics, target semantics and independent expected arithmetic. No Stage A execution is needed for that test.
- [ ] A deployment audit confirms no training, model import, or inference was run in the protected workspace while this package was being prepared.
- [ ] Versioned package manifest, detached checksum, test results, limitations and upstream release IDs are independently verified before enabling the adapter.

Until every applicable checklist item passes, the Stage A model path remains disabled. Independently source-verified Phase 2 observed measurements may continue to be reported under their own semantic and compatibility rules; this does not make a model prediction eligible.

## Owner response and synthetic verification

The owner handoff is tracked row-by-row in [`owner_decision_tracker.json`](../../data/phase2/owner_decision_tracker.json) against [`stage_a_owner_decision_tracker.schema.json`](../../schemas/stage_a_owner_decision_tracker.schema.json). The tracker requires owner response, supporting artifact, source locator, decision date, scientific reviewer, approval status and unresolved rationale for each RF-01–RF-15 row. `APPROVED` is rejected unless response, artifact, locator, ISO date and reviewer are present. The evaluator checks completeness only and never adjudicates the scientific answer. See the [`one-page handoff`](STAGE_A_OWNER_HANDOFF_ONE_PAGE.md) and [`generated readiness dashboard`](STAGE_A_DEPLOYMENT_READINESS_DASHBOARD.md); current status is 0/15 approved, no package supplied, deployment blocked, and inference unauthorized.

Run the reproducible pending-state dashboard demo with:

```powershell
python stageC/scripts/demo_phase2_owner_decisions.py --write-report
python -m unittest discover -s stageC/tests -p test_deployment_decisions.py -v
python -m unittest discover -s stageC/tests -p test_stage_a_deployment.py -v
```

The synthetic package-validator tests are run with:

```powershell
python -m unittest discover -s stageC/tests -p test_stage_a_deployment.py -v
```

These tests use placeholder bytes and synthetic metadata only. They do not load a model, perform inference, or stand in for a real deployment package.
