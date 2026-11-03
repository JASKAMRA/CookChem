# CookRisk advanced execution report

Date: 2026-11-04  
Scope: Stage C completion work and bounded Stage D development.  
Repository head remained `8545029a4bae1bc923fdc840bbfe681b2d7bef03` on `main`; no Git metadata operation was performed.

## Stage C roadmap

| Roadmap phase | Status | Work and validation | Limitation and exact next action |
|---|---|---|---|
| 1. Software foundation | COMPLETE | Existing import, mapping, exposure, provenance, and validation interfaces were retained. Phase 3 hardening restored the legacy `validate_all`, food, mapping, and output validators. | No broader application UI has been built. |
| 1B. Food data acquisition | COMPLETE_WITH_DOCUMENTED_LIMITATIONS | Existing Phase1B-v1.3.2 remains authoritative: 584 food records, 130 raw-mapped compounds, 121 accepted mappings, 116 quantitatively eligible compounds overall, 80 ordinary-food eligible. Its 1,324-artifact manifest and embedded 839-entry Stage B V20 manifest were previously verified. | Accepted closeout retains the documented coverage shortfall; no data records were edited in this execution. |
| 2. Cooking-retention integration | IN_PROGRESS | Added a read-only supplied-output contract, Stage A provenance pins, eight explicit compatibility gates, semantic separation, and guarded concentration calculations. The Phase2-v0.3.1 adapter remains checksum-pinned and supplies zero accepted cooked estimates. Read-only Stage A inspection recorded the input and runner hashes, folds/features, environment, and existing OOF output structure. | Stage A has no serialized estimator, model artifact hash, serving interface, output manifest, or documented `Retention_Final` denominator/measurement basis. Do not run inference. Obtain an approved immutable inference package with target semantics and provenance before considering prediction use. |
| 3. Recipe and meal engine | COMPLETE_WITH_DOCUMENTED_LIMITATIONS | Tightened runtime identifier/type validation, fixed numeric-string schema bounds, added missing-mapping and missing-yield checks, and verified create/edit/validate/calculate/export workflows. Seven active Stage C schemas pass Draft 2020-12 meta-validation. Independent synthetic checks verify 50% concentration retention × 10 mg/kg = 5 mg/kg; total-mass retention additionally applies measured raw/cooked yield, with parallel volume-basis checks. | Live cooked estimates remain unavailable because Phase2-v0.3.1 has zero quantitative estimates and no accepted Stage A model artifact exists. Raw-reference results must not be described as cooked exposure. |
| 4. Uncertainty and sensitivity | IN_PROGRESS | Implemented source-typed interval propagation, explicit missing-uncertainty reporting, Phase 3 recipe/meal summaries, conditional retention bounds, and deterministic one-factor sensitivity ranking. Inputs remain bounds/scenarios; no probability distribution or confidence interval is inferred. | Food concentration, recipe quantity, and consumed-fraction uncertainty are not structured in current sources. Add only source-supported bounds when records provide them. |
| 5. Exposure validation and benchmarking | COMPLETE_WITH_DOCUMENTED_LIMITATIONS | Implemented an independent Decimal reference calculator, recipe/meal arithmetic recomputation and tamper checks, published-reference comparability gates, and separate software, regression, mathematical, published-data, and external-validation layers. | No published benchmark dataset was compared and no external scientific validation was conducted. Record a commensurate source dataset before making either claim. |
| 6. User-facing application | NOT_STARTED | No website was built, as directed. | Begin only after the Phase 3 schemas, result exports, and unresolved-data presentation are approved for the application. |
| 7. Stage C finalization | IN_PROGRESS | Built immutable Phase3-v0.1.2 successor and verified its complete artifact manifest. | Final Stage C release still depends on resolving Phase 2 integration inputs and the future application/finalization work. |

## Stage D roadmap

| Roadmap phase | Status | Work and validation | Limitation and exact next action |
|---|---|---|---|
| 1. Evidence–exposure architecture | COMPLETE_WITH_DOCUMENTED_LIMITATIONS | Added versioned evidence and exposure-comparability contracts preserving exact Stage B IDs, source provenance, and distinct dietary versus experimental quantities. | Actual Phase 3 comparison is gated until a verified exposure plus source-compatible evidence is available. |
| 2. Evidence normalization | COMPLETE_WITH_DOCUMENTED_LIMITATIONS | Added deterministic normalization for recognized human PK, controlled clinical, animal, and in-vitro labels; unknown labels and ambiguous/null/conflicting outcomes remain visible and pending. Tests cover provenance and non-acceptance. | No census or automated approval of all Stage B evidence was attempted. |
| 3. Exposure–evidence comparability | COMPLETE_WITH_DOCUMENTED_LIMITATIONS | Six explicit tri-state criteria cover compound identity, route, dose basis, time window, population/model, and preparation/matrix. Positive criteria mean `READY_FOR_REVIEW`, not dose equivalence. | No numeric ratio or actual clinical interpretation is implemented. |
| 4. Mechanism-based integration | IN_PROGRESS | Read 317 Stage B interaction rows without modification. Built three source-pinned candidate records from two primary studies: SB-0003, SB-0046, SB-0048. The first article was checked against full text; the second against its PubMed abstract. | All mechanistic interpretations and identities remain pending manual review. SB-0046's abstract/full-text endpoint discrepancy is preserved. Resolve it against the full article/tables; do not select either conflicting number automatically. |
| 5. Uncertainty and evidence assessment | IN_PROGRESS | Added nonnumeric review criteria for source match, identity, directness, assay context, study design, endpoint reconciliation, replication, food context, exposure relevance, and interpretation. No arbitrary evidence scores. | All scientific quality criteria remain unassessed pending expert review; the three-row sample is not a full Stage B assessment. |
| 6. Risk interpretation | NOT_STARTED | No risk score, medication advice, or patient-specific interpretation was created. | Requires accepted evidence and validated exposure plus a separately approved transparent interpretation framework. |
| 7. Validation and benchmarking | NOT_STARTED | Software contract/mutation tests are present; they are not external scientific validation. | Requires independently curated benchmark data and a prospective validation protocol. |
| 8. Application and reporting | NOT_STARTED | No user-facing Stage D application was built. | Defer until review status and interpretation limits can be represented faithfully. |
| 9. Final integration and release | NOT_STARTED | Stage D remains a working tree, not a released package. | Release only after record-level review, exposure integration, and validation gates are established. |

## Tests and release evidence

- Stage C root suite: **199 passed, 0 failed, 0 skipped** (`python -m unittest discover -s stageC/tests -v`).
- Stage C Phase 4 registry suite: **13 passed, 0 failed, 0 skipped** (`python -m unittest discover -s stageC/phase4/tests -v`).
- Stage D normalization, comparability, and mechanism suite: **18 passed, 0 failed, 0 skipped** (`python -m unittest discover -s stageD/tests -v`).
- Phase3-v0.1.2 isolated package suite: **79 passed, 0 failed, 0 skipped** (`python -m unittest discover -s stageC/releases/Phase3-v0.1.2/stageC/tests -v`).
- Formal Draft 2020-12 validation ran with the exact pinned development dependency `jsonschema==4.26.0` and pinned transitive packages. Seven active Stage C schemas passed metaschema validation; positive and negative fixtures exercised recipe, meal, Stage A handoff, and Stage D contracts.
- Prior failures during implementation were corrected: the initial runtime test exposed a non-string recipe name accepted by the custom validator; the integration run caught a temporarily incomplete `validation.py` edit before the legacy APIs were restored; schema fixture/path and pinned Stage A hash typos were fixed. No failures or skips remained in the final runs listed above.
- Phase3-v0.1.2: 47 artifacts; manifest SHA-256 `8a0d532ff35cc8ac88d5cedc0231caf35b94aebac6501c30c55b5db48ff1a9ec`. Historical Phase3-v0.1.1 and all upstream packages remain preserved.
- Existing pinned example calculations remain raw-reference outputs: apple recipe 11.2950 mg; apple+cocoa meal 21.11650 mg. The tested Phase2 cooked-evidence record count is zero; neither example is a cooked-dose estimate.

## Key deliverable files

- Stage C implementation: `stageC/src/stage_c/recipe_engine.py`, `stageC/src/stage_c/cooking_integration.py`, `stageC/src/stage_c/uncertainty.py`, and `stageC/src/stage_c/validation.py`.
- Stage C schemas/tests: `stageC/schemas/recipe.schema.json`, `meal.schema.json`, and `stage_a_prediction.schema.json`; focused tests are `stageC/tests/test_recipe_schema.py`, `test_recipe_engine.py`, `test_cooking_integration.py`, and `test_phase4_phase5_foundations.py`.
- Stage C reports/build: `stageC/reports/phase2/STAGE_A_INTEGRATION_READINESS.md`, `stageC/reports/phase4/UNCERTAINTY_FOUNDATION.md`, `stageC/reports/phase5/VALIDATION_FOUNDATION.md`, `stageC/reports/ADVANCED_EXECUTION_REPORT.md`, and `stageC/scripts/build_phase3_v0_1_2_release.py`.
- Stage D implementation: `stageD/src/stage_d/contracts.py` and `mechanisms.py`; schemas are under `stageD/schemas/`; the pinned read-only sample is `stageD/data/mechanism_evidence_registry.json`, built by `stageD/scripts/build_mechanism_registry.py`. Contract and source-pinned tests are `stageD/tests/test_contracts.py` and `test_mechanisms.py`.
- Stage D findings: `stageD/reports/phase45_mechanism_registry_report.md`. Phase3-v0.1.2 preserves all of its source, schemas, tests, reports, and development pins in its 47-artifact manifest.

## Source-backed Stage D candidates

The source registry copies its three Stage B rows verbatim; its source CSV SHA-256 is `358665c339e0ab673bb846d16d30e75dbed2b9587ae4df91baddfb5493a3b8e6`. It covers [PMID 21870106](https://pubmed.ncbi.nlm.nih.gov/21870106/) and [PMID 22300367](https://pubmed.ncbi.nlm.nih.gov/22300367/). Source observations are deliberately narrow: the first study uses a midazolam probe in a berberine human study; the second has an hBCRP assay and human sulfasalazine arm. This does not establish ordinary-food exposure equivalence or clinical risk. Two of the second article's records are abstract-reviewed only; endpoint reconciliation remains open. Full notes and source locators are in [the Stage D mechanism report](../../stageD/reports/phase45_mechanism_registry_report.md).

## Protection and handoff

- Stage A was inspected read-only and was not modified, imported, trained, or used for inference.
- Stage B source records were read-only. Stage D candidates preserve raw fields without updating Stage B.
- No historical release was overwritten. Phase3-v0.1.2 is additive.
- No branch, index, commit, push, reset, stash, or history operation was performed; Git remains the user's responsibility.

## Remaining work

1. Acquire a scientifically approved Stage A deployable artifact and target-unit/denominator contract; until then keep the cooked-estimate set empty.
2. Obtain source-backed analytical and recipe-quantity uncertainty bounds before producing full uncertainty intervals for current foods.
3. Compare Phase 3 outputs to a commensurate published reference dataset; keep external validity unclaimed.
4. Have an expert reconcile the source-level endpoint discrepancy in the Stage D BCRP/sulfasalazine article and adjudicate compound/target identities.
5. Continue Stage D record-level source review; do not assign evidence scores or clinical interpretation automatically.
6. Implement Stage C and Stage D applications only after their core outputs and review states are approved.
