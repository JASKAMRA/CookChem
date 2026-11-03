# CookRisk next advanced execution report

Date: 2026-11-04  
Scope: Stage C completion and bounded Stage D development across workstreams A–G.  
Repository: `main`, HEAD `8545029a4bae1bc923fdc840bbfe681b2d7bef03` at start and end. No branch, index, commit, or history operation was performed.

## A. Executive summary

Implemented Phase 2 deployment-readiness diagnostics and specification, expanded Stage C uncertainty and arithmetic validation, added a synthetic-only benchmark protocol, source-reviewed and structured three Stage D evidence records, hardened Stage C-to-Stage D provenance linkage, and drafted application workflows/API/export requirements.

The work is a verified working-tree increment, not a new release. Stage A remains unexecuted and unchanged; Stage B source records remain unchanged. Phase 2 still has zero accepted quantitative cooked-concentration estimates. Phase 3 examples remain raw-reference outputs. No published-data comparison, external scientific validation, dose-equivalence calculation, clinical risk interpretation, or medication advice was performed.

Remaining scientific blockers are the absent approved Stage A serving artifact and `Retention_Final` target definition, expert review of Stage D identities/mechanisms and the source-level transcription adjudication, and real commensurate benchmark data. The exact Phase 2 target questions and deployment package requirements are recorded in the linked Phase 2 reports.

## B. Original roadmap status

### Stage C

| Original roadmap phase | Status | Work completed and evidence | Remaining limitation and exact next action |
|---|---|---|---|
| **1. Software foundation** | COMPLETE | Existing Stage C interfaces and data paths are retained; full root suite passes 218/218. Seventeen active Stage C schemas pass Draft 2020-12 validation. | Broader application implementation remains gated by Phase 2, validation, and review-state requirements. |
| **1B. Food data acquisition** | COMPLETE_WITH_DOCUMENTED_LIMITATIONS | Phase1B-v1.3.2 remains the accepted source package. Its 1,324-artifact checksum set verifies; no food or mapping record was changed in this execution. | Preserve the recorded coverage shortfall. Any new scientific measurements require new source screening and an additive release. |
| **2. Cooking-retention integration** | IN_PROGRESS | Adapter requires provenance-complete supplied output, target-contract hash, canonical output checksum, and eight explicit compatibility gates with per-gate diagnostics. Added a deployment specification, acceptance checklist, 15 target-adjudication questions, and synthetic tests (19/19). Stage A input and runner were read-only hashed. | No serialized serving model, approved serving-model choice, complete locked runtime, or source-defined target/denominator exists. Obtain these from the Stage A owner, answer RF-01–RF-15 with source and row-level evidence, then pass the checklist. Do not run inference before that. |
| **3. Recipe and meal engine** | COMPLETE_WITH_DOCUMENTED_LIMITATIONS | Current Phase3-v0.1.2 package passes 79/79 tests. Its 47 artifacts and manifest verify. The actual example passed the new Stage D handoff smoke check and remains `PENDING` because review gates are unresolved. | Examples are raw-reference amounts (including the apple and apple+cocoa examples), not cooked estimates. Keep cooked outputs blocked until accepted Phase 2 evidence and measured basis inputs exist. |
| **4. Uncertainty and sensitivity** | IN_PROGRESS | Deterministic interval and one-factor sensitivity code distinguishes source-reported ranges, analytical measurement variability, literature-derived ranges, scenario bounds, and model-prediction uncertainty. Missing uncertainty has structured reason codes; model intervals require artifact, target-contract, and prediction references. Focused Phase 4/5 suite passes 36/36. | Current records mostly provide point inputs. No actual model-prediction interval was used. Add bounds only when supported by source-level concentration, amount, fraction, yield, or prediction provenance. |
| **5. Exposure validation and benchmarking** | COMPLETE_WITH_DOCUMENTED_LIMITATIONS | Decimal hand calculations, independent recipe/meal recomputation, mass/volume separation, boundary checks, provenance tamper checks, and published-reference comparability gates are implemented. A three-case synthetic fixture is explicitly test-only. | No published dataset comparison or external validation was performed. Select and document a commensurate real reference dataset before computing agreement metrics. |
| **6. User-facing application** | IN_PROGRESS | Stage C workflows, provenance/uncertainty/missing-data display rules, export specification, and a non-production OpenAPI 3.1 draft with three paths and 14 resolving internal references are documented. | No UI or service was built. Complete the scientific and release prerequisites, then freeze schemas and implement a compatibility-tested service. |
| **7. Stage C finalization** | IN_PROGRESS | Current Phase 3 and upstream release manifests were verified; no historical or current release files were altered. This report records test counts and handoff blockers. | Do not create a final release until Phase 2 has a scientifically approved deployment path and relevant uncertainty/benchmark requirements are satisfied. |

### Stage D

| Original roadmap phase | Status | Work completed and evidence | Remaining limitation and exact next action |
|---|---|---|---|
| **1. Evidence–exposure architecture** | COMPLETE_WITH_DOCUMENTED_LIMITATIONS | Stage D keeps source evidence and dietary exposure separate, with exact Stage B IDs and hashes. Cross-stage contract checks the Phase 3 release chain and single ingredient estimate. | Have a reviewer verify release manifests before setting the recorded verification assertion; use source-compatible records only. |
| **2. Evidence normalization** | COMPLETE_WITH_DOCUMENTED_LIMITATIONS | Deterministic normalization preserves raw Stage B text and provenance. Unknown study labels and null, negative, ambiguous, and conflicting findings stay distinct and pending. | The 317-row source was not automatically approved or fully normalized; continue record-level expert review. |
| **3. Exposure–evidence comparability** | COMPLETE_WITH_DOCUMENTED_LIMITATIONS | Six tri-state gates fail closed. Cross-stage output preserves dietary amount, raw/cooked concentration and units, experimental dose text, and missing inputs separately. `READY_FOR_REVIEW` never means clinical equivalence. | No dose conversion, ratio, or clinical interpretation is implemented. Human reviewers must adjudicate all gates with source references. |
| **4. Mechanism-based integration** | IN_PROGRESS | Three records (`SB-0003`, `SB-0046`, `SB-0048`) from two primary studies were checked against full text. For PMID 22300367, abstract, Table 1, and later discussion support the same dose assignment while one Results sentence reverses it; Stage D records a source-level extraction adjudication and preserves the conflicting text and raw Stage B record. | Independent expert confirmation, compound/target identity review, and mechanism acceptance remain open. The source did not issue a correction notice. Do not treat the extraction adjudication as clinical evidence acceptance. |
| **5. Uncertainty and evidence assessment** | IN_PROGRESS | Added nonnumeric review states and reason codes for source matching, identity, directness, assay context, study design, endpoint reconciliation, replication, food context, exposure relevance, and interpretation. Review sample is 3 records from 317; no numeric evidence scores. | Complete broader record-level review with qualified reviewers; keep all unresolved criteria visible. |
| **6. Risk interpretation** | NOT_STARTED | No risk score, clinical interpretation, or medication advice was implemented. | Requires accepted evidence, validated exposure, and a separately approved transparent interpretation framework. |
| **7. Validation and benchmarking** | NOT_STARTED | Synthetic contract and mutation tests are software checks only. | Establish a preregistered scientific validation plan and independently curated commensurate data before any external-validation claim. |
| **8. Application and reporting** | IN_PROGRESS | Stage D user workflow and review/export requirements are drafted and linked to the shared API contract. | No production UI or service exists. Complete human-review workflows and security/privacy prerequisites before implementation. |
| **9. Final integration and release** | IN_PROGRESS | Cross-stage code, schemas, integration tests, application requirements, and this report are present in the working tree. No Stage D release was created. | Complete expert review, validate real matched records, freeze contracts, and run a release-specific complete test and manifest cycle before publishing. |

## C. Workstream results

### A — Stage C Phase 2 readiness

**Files:** `stageC/src/stage_c/cooking_integration.py`, `stageC/schemas/stage_a_prediction.schema.json`, `stageC/tests/test_cooking_integration.py`, `stageC/reports/phase2/STAGE_A_INTEGRATION_READINESS.md`, `PHASE2_STAGE_A_DEPLOYMENT_PACKAGE_SPEC.md`, and `RETENTION_FINAL_TARGET_QUESTIONS_2026-11-04.md`.

The adapter accepts supplied predictions only, verifies canonical output checksums and registered provenance, reports each of eight compatibility gates, and keeps complete-but-unapproved predictions ineligible. Tests cover each gate, missing source/model/target fields, checksum mutation, model-label misuse, and synthetic calculation examples. Focused result: **19 passed**.

Workspace input SHA-256 is `cd51de3286d9fea7c4d87ce45f4c9c4301214b1944f72bff19c3b41ce0358c27`; runner SHA-256 is `a2de32f24600d18df6a503aba001ce4484295f0802b2ba7d09bbaa6bfc704d0c`. The older readiness JSON's `750124…` hash belongs to a `/Users/ayushkamboj3/...` path, not this Windows workspace. XGBoost is the RMSE leader in one QA field; the report retains Extra Trees as overall benchmark. Neither is a registered serving-model choice. Fifteen target questions remain open.

### B/C — Stage C Phase 4 uncertainty and Phase 5 validation

**Files:** `stageC/src/stage_c/uncertainty.py`, `stageC/src/stage_c/validation.py`, `stageC/schemas/uncertainty_assessment.schema.json`, `stageC/schemas/synthetic_validation_benchmark.schema.json`, `stageC/tests/test_phase4_phase5_foundations.py`, `stageC/tests/fixtures/synthetic_validation_benchmark.json`, and the Phase 4/5 reports/protocol under `stageC/reports/`.

Supported bounds remain deterministic and source-referenced; unknown uncertainty is described explicitly, not replaced with zero. Cooked interval acceptance verifies compatibility, evidence provenance, endpoint ordering, and reconstruction from concentration, portion, and consumed fraction. The benchmark fixture is synthetic-only; it cannot support a published-data or external-validation claim. Focused result: **36 passed**. Separate legacy validation tests: **8 passed**. No real published data were compared.

### D/E — Stage D Phase 4 mechanisms and Phase 5 evidence assessment

**Files:** Stage D mechanism code, schemas, registry, tests, and `stageD/reports/phase45_mechanism_registry_report.md`.

Read-only review covered 317 Stage B rows; the bounded registry contains three source-pinned records from two primary studies. Stage B interaction CSV SHA-256 remains `358665c339e0ab673bb846d16d30e75dbed2b9587ae4df91baddfb5493a3b8e6`. PMID 22300367 abstract/Table 1 assign AUC changes as 2.0-fold at microdose and 3.2-fold at therapeutic dose; one Results sentence reverses those assignments. Table 1 displayed means (79.4/43.5 and 19.0/5.89) arithmetically support approximately 1.83 and 3.23, respectively; these ratios of group means are only a consistency check, not the study's paired estimates. The Stage D extraction is marked `resolved_source_record_level`; independent review and overall acceptance remain pending. The full-text paper and metadata were checked at the [publisher](https://bpspubs.onlinelibrary.wiley.com/doi/10.1111/j.1476-5381.2012.01887.x) and [PubMed](https://pubmed.ncbi.nlm.nih.gov/22300367/). PMID 21870106 was checked against its [primary full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC4898966/).

Review labels are nonnumeric; tests keep null, negative-under-tested-conditions, mixed, conflicting, and unclear outcomes distinct. The full Stage D suite passes **27/27** with formal schema checks.

### F — Stage D Phase 1–3 cross-stage contract

**Files:** `stageD/src/stage_d/contracts.py`, `stageD/schemas/exposure_comparison.schema.json`, `stageD/tests/test_contracts.py`, `stageD/README.md`, and `stageD/reports/cross_stage_contract_hardening.md`.

`build_cross_stage_comparison` binds a Phase 3 recipe ingredient estimate to one exact Stage B `Evidence_ID` and `Compound_ID`, checks upstream release hashes and the supplied manifest-verification assertion, validates source provenance and nonnegative bounds, and fails closed for unsupported or incomplete records. Dietary amounts, raw concentration, cooked concentration, units, and retention evidence are distinct from source-reported experimental dose and concentration. No conversions or ratios are produced. Synthetic integration tests cover tampering, mismatched IDs/hashes, missing units, and review gates. The actual Phase3-v0.1.2 example also passed an integration smoke check and remained `PENDING`. The caller must perform cryptographic package verification before asserting `phase3_manifest_verification="verified"`.

### G — Stage C Phase 6 / Stage D Phase 8 application readiness

**Files:** `stageC/reports/phase6/USER_WORKFLOWS_AND_REPORT_EXPORT.md`, `stageC/reports/phase6/API_CONTRACT_DRAFT.json`, and `stageD/reports/phase8/APPLICATION_READINESS.md`.

The draft defines food/recipe/cooking and evidence-review workflows, source and uncertainty display, missing-data states, JSON/CSV/PDF export content, three non-production endpoints, and production prerequisites. JSON parsing and all 14 local OpenAPI references passed a structural check. No service or UI was built, and no unsupported cooked or clinical output is exposed.

## D. Tests and validation results

| Suite/check | Observed result |
|---|---:|
| Stage C root tests | **218 passed, 0 failed, 0 skipped** |
| Stage C Phase 4 registry | **13 passed, 0 failed, 0 skipped** |
| Stage C Phase 4/5 uncertainty and validation foundations | **36 passed, 0 failed, 0 skipped** |
| Stage C Phase 2 adapter | **19 passed, 0 failed, 0 skipped** |
| Stage D complete suite | **27 passed, 0 failed, 0 skipped** |
| Phase3-v0.1.2 isolated package | **79 passed, 0 failed, 0 skipped** |
| Active Stage C schemas | **17/17** Draft 2020-12 metaschema-valid |
| Active Stage D schemas | **4/4** Draft 2020-12 metaschema-valid |
| Current Phase 3 example cross-stage smoke | **Passed**, schema-valid; decision stayed `PENDING` |
| Application API draft structure | **Passed**, 3 paths and 14 local references resolved |

The first final Stage C run found one stale test assertion requiring exactly seven schemas. It was changed to enumerate the active schemas and require core schemas; the focused schema tests then passed **10/10**, and the complete rerun passed **218/218**. An interim Stage D test assertion expected the previous error-message order after stronger validation; the assertion was corrected, cooked/raw distinction coverage was added, and the final Stage D run passed **27/27**. These intermediate failures are resolved; no final suite has failures or skips.

An early direct module-name invocation of the Phase 4/5 test file failed before tests ran because its sibling test helper was not on `sys.path`; discovery-mode execution passed. The final Stage C root run includes that module and passed. The formal manifest verifier was also adapted to the distinct Phase 1B, Phase 2, and Phase 3 manifest formats before all packages passed.

The pinned development packages (`jsonschema==4.26.0` and pinned transitive dependencies from `stageC/requirements-dev.txt`) were installed into a temporary workspace-only folder for formal checks. That folder is removed after verification.

Reproduction commands after installing `stageC/requirements-dev.txt` into the active interpreter:

```powershell
python -m unittest discover -s stageC/tests
python -m unittest discover -s stageC/phase4/tests
python -m unittest discover -s stageD/tests
python -m unittest discover -s stageC/releases/Phase3-v0.1.2/stageC/tests
```

Focused workstream commands:

```powershell
python -m unittest discover -s stageC/tests -p test_cooking_integration.py
python -m unittest discover -s stageC/tests -p test_phase4_phase5_foundations.py
python -m unittest discover -s stageD/tests -p test_contracts.py
```

## E. Scientific integrity statement

- **Stage A inference executed:** NO.
- **Stage A source modified or imported for inference:** NO.
- **Stage B source records modified:** NO. The authoritative Stage B interaction CSV still hashes to `358665c339e0ab673bb846d16d30e75dbed2b9587ae4df91baddfb5493a3b8e6`; `git diff --name-only -- stageA stageB` is empty.
- **Accepted cooked exposure estimates:** NONE in Phase2-v0.3.1 (zero quantitative cooking estimates). The current example calculations are raw-reference outputs.
- **Published-data comparison or external scientific validation performed:** NO.
- **Clinical risk interpretation or patient-specific advice implemented:** NO.
- **Synthetic data:** confined to explicitly labeled tests/fixtures and never presented as scientific evidence.
- **Stage D BCRP/sulfasalazine discrepancy:** transcribed consistently for Stage D using the abstract/Table 1 assignment, with the conflicting sentence preserved. Independent expert review remains pending; the raw Stage B row was not edited.

## F. Release and repository integrity

Manifest sidecars and all listed artifacts verified:

| Package | Artifacts checked | Manifest SHA-256 | Result |
|---|---:|---|---|
| Phase1B-v1.3.2 | 1,324 | `df3a95ae0957b68a89e38098c0824877196aa74ef7dd92573e6ab1f37e39b9b5` | PASS |
| Phase2-v0.3.1 | 50 | `2b72e4df095002952fcf2eef2af3381425384317d6ea259b81676ed8c243746e` | PASS |
| Phase3-v0.1.1 (historical) | 26 | `546286e6c409048a7b5abba33f4c3be7c2cf9ec424c37991b0cb8d82ab37c31b` | PASS |
| Phase3-v0.1.2 | 47 | `8a0d532ff35cc8ac88d5cedc0231caf35b94aebac6501c30c55b5db48ff1a9ec` | PASS |

No release was created or modified. Git remained on `main` at HEAD `8545029a4bae1bc923fdc840bbfe681b2d7bef03`; no index/history operation occurred. The working tree contains existing uncommitted Stage C work plus the additions from this execution; nothing was staged or committed.

## G. Next milestone — three highest-value actions

1. **Close Phase 2 deployment semantics.** Obtain the Stage A owner's answers to RF-01–RF-15, select and approve one serving model, provide a serialized artifact and complete dependency lock with verified hashes, and pass the deployment acceptance checklist. No inference before these prerequisites.
2. **Complete Stage D expert review.** Independently confirm the PMID 22300367 source-level extraction, then adjudicate compound/target identity and mechanism evidence for the bounded records without changing Stage B raw rows.
3. **Establish real validation evidence.** Select a primary published food/cooking dataset with matching compound, matrix, preparation, conditions, measurement basis, units, yield, analytical method, and source quality; ingest it as a reference and run the documented comparison before claiming published or external validation.
