# CookRisk M0 Baseline Verification

**Date:** 17 November 2026  
**Mode:** Read-only baseline and scope check  
**Decision:** M0 documentation completed. M1 implementation **BLOCKED pending official task authorization and file-scope approval**.

## 1. Preservation baseline

Command executed:

```text
git status --short
```

Observed status:

```text
?? reports/research_prototype/
```

The directory contains planning documents created in the prior authorized planning task. It was preserved. No pre-existing tracked file was modified by this M0 check. No branch, index, history, remote, or Git configuration operations were performed. No Stage B material was accessed.

## 2. Official roadmap and task position

The authoritative phase sequence was read from `COOKRISK_DEVELOPMENT_ROADMAP.md`. It defines Stage C Phases 1, 1B, and 2–7, followed by Stage D Phases 1–9. It does not define an M0/M1 milestone or an official research-prototype integration stage.

The available Stage C task register is `stageC/reports/STAGE_C_MASTER_EXECUTION_CYCLE_1_REPORT.md` (dated 2026-11-04). Its registered Stage C tasks include C1-01, C1-02, C1B-01, C1B-02, C2-01, C3-01, C4-01, C5-01, C6-01, C6-02, and C7-01. It does not register M1 or an equivalent generalized “evidence and quantity contract” task. The register predates later completion records, so its individual statuses must be reconciled with later task evidence before being treated as current.

The later `stageC/reports/STAGE_C_CLOSURE_REPORT_2026-11-05.md` records C1-01 complete for its stated environment, C1B-01 complete, C1-02 isolated behavior verified with limitations, and C1B-02 blocked pending a current owner-reviewed handoff and genuine partner Windows/browser evidence. It explicitly places C1B-02 before C2-01 and subsequent phases. The current C1B-02 designation/handoff records still identify owner designation/runtime provisioning and partner execution as external requirements. Therefore the earliest registered predecessor gate remains C1B-02; C2-01 has not been unblocked by this planning request.

**Current authorized Stage C task for this proposed work:** none established. `M1` is a supplementary milestone label from the planning blueprint, not an official task ID. No task-specific authorization was found that permits a new unified schema/contract, its fixtures, or associated source/test edits. The request itself requires stopping before implementation when this authorization is absent.

## 3. Relevant existing contracts and behavior inspected

Only authorized Stage C schemas, modules, tests, and reports were inspected. No Stage B file or embedded Stage B data was opened.

| Existing artifact | Relevant coverage | M1 implication |
|---|---|---|
| `stageC/schemas/food_schema.json` | Food name, part, state, and coarse moisture-basis vocabulary. | Does not contain the full measurement/provenance/quantity contract. |
| `stageC/schemas/compound_schema.json` | Compound ID, canonical name, aliases, identifiers, identity status/context. | Identity vocabulary exists, but the schema is not a full measurement record. |
| `stageC/schemas/food_composition_schema.json` | Reported and normalized concentration/unit, state, moisture basis, method, food-use class, source/citation and review fields. | Much of the raw composition contract already exists; a new parallel composition schema would duplicate it. Some fields are optional strings, so explicit unknown/status semantics are not uniform. |
| `stageC/schemas/phase2_source_pair_audit.schema.json` | Source locator, compound and matrix labels, cooking method, raw/cooked means, unit, recalculated ratio and source status. | Covers an audit-row use case, not a canonical compositional measurement or all quantity types. |
| `stageC/schemas/phase2_cooked_concentration.schema.json` | Cooked estimate identifiers, raw concentration/unit, retention source, calculation pathway, provenance and validation status. | Covers an output record; it does not define all raw/cooked measurement details requested for M1. |
| `stageC/schemas/provenance_schema.json` | Calculation provenance and input source IDs. | Existing provenance contract exists, but required Stage B release fields and permissive extras mean it is not a standalone unified evidence contract. |
| `stageC/src/stage_c/cooking_integration.py` | Versioned supplied-prediction validation; ACR/concentration-retention/total-mass-retention semantics; eight fail-closed identity/state/method/condition/basis/denominator gates; calculation trace and measured-mass requirements. | This is an existing compatibility and calculation contract. Any extension should reuse it rather than create a parallel gate implementation. |
| `stageC/src/stage_c/phase2_retention.py` | Four compatibility booleans for applying a source-bounded interval; decimal validation; no identity adjudication. | Narrow calculation helper; not the full record contract. |
| `stageC/src/stage_c/recipe_engine.py` and `stageC/schemas/recipe.schema.json` | Recipe/meal quantities, mass balance, servings, consumed fraction, leftovers, raw-reference results, guarded cooked path. | Already models partial recipe calculations and yield/mass-balance inputs; reuse is preferable to new parallel recipe fields. |
| `stageC/tests/test_cooking_integration.py`, `test_phase2_retention.py`, `test_phase2_integration.py`, `test_recipe_engine.py`, `test_recipe_schema.py` | Existing synthetic compatibility, calculation, recipe, and schema behavior. | Before adding tests, an authorized task should map requested cases to these suites and add only uncovered scenarios. |

This inspection was source/schema review only. It did not execute tests, read datasets, regenerate the 117 observations, or validate any scientific record.

## 4. Preliminary compatibility decision table

This is an M0 gap map, **not** a new schema, official compatibility contract, or scientific decision.

| Requested concept | Existing home identified | M0 disposition |
|---|---|---|
| Food identity | `food_schema.json`, `food_composition_schema.json`, cooking adapter gates | Partially represented across contracts; canonical linkage/version needs task-owner decision. |
| Compound identity | `compound_schema.json`, composition schema, cooking adapter gates | Partially represented; unresolved identity must stay unresolved. |
| Preparation identity/method | Phase 2 audit schema, cooking adapter conditions, recipe preparation fields | Distributed across contracts. Do not add another method vocabulary without an authorized integration design. |
| Original source value/unit | `food_composition_schema.json`, Phase 2 source-pair audit schema | Represented in use-specific records; preserve source form and avoid overwriting. |
| Normalized value/unit | `food_composition_schema.json`, recipe/calculation layers | Represented, but conversion provenance/validity must remain explicit. |
| State and measurement basis | Food/composition schemas and cooking adapter | Partially represented; basis semantics and unknown states are not fully unified. |
| Quantity type (ACR, retention, cooked concentration, yield, other) | `cooking_integration.py` semantic vocabulary; multiple output schemas | Important semantics already exist in code but are distributed; not permission to create a replacement. |
| Raw/cooked values and mass/yield | Phase 2 audit schema, cooked output schema, recipe schema/engine | Distributed; specific calculations already fail closed when evidence/mass is missing. |
| Provenance/locator | Composition, Phase 2 audit, output, provenance schemas | Several overlapping contracts exist; select a canonical composition path before adding fields. |
| Evidence/review status | Composition verification fields; cooking adapter scientific review; Stage D review contracts | Separate source verification, compatibility, and human review states; do not collapse them. |
| Reason-coded unavailable states | Cooking adapter diagnostics and recipe calculation statuses | Some reason coding exists; full cross-API vocabulary would need authorized task scope. |

## 5. Smallest safe implementation scope — not authorized yet

The smallest safe future implementation should be an additive, versioned extension or composition of existing Stage C contracts, not a new parallel schema or new calculation implementation. Before editing, an authorized task owner must identify the canonical contract to extend, the exact API/consumer compatibility requirement, migration/backward-compatibility expectations, and the allowed file list. Likely candidates for review—not authorized edit targets—are the existing composition schema, Phase 2 audit/output schemas, `cooking_integration.py`, and its focused test module.

The requested 12 fixture scenarios could be distributed across existing focused suites. A future task should first map each case to existing test coverage, avoid the `test_phase2_source_audit.py` path that rewrites a historical audit output in place, and run only isolated tests explicitly allowed by that task. Synthetic fixtures must be stored only under an authorized test-fixture path and marked as synthetic.

## 6. M1 authorization and dependency blockers

Before M1 implementation, obtain a task record or explicit owner authorization that establishes:

1. Official task ID and location in the Stage C task register/sequence. If this is a new task, the owner must approve its registration; do not treat `M1` or `RP-*` as official IDs.
2. Confirmation whether it is allowed to proceed while C1B-02 remains blocked, or whether it depends on C1B-02/C2-01. Do not bypass the registered predecessor gate.
3. Exact files permitted for edits, including schema/API/test/documentation ownership and any protected release exclusions.
4. Canonical contract selection and whether the task extends an existing schema or composes existing schemas. No duplicate evidence/quantity schema should be introduced by assumption.
5. Backward-compatibility and versioning policy for existing Phase 1B/Phase 2/recipe consumers.
6. Scientific owner approval for definitions of ACR, concentration retention, total-mass retention, cooked concentration, yield, basis, and the states that make each calculation eligible.
7. Test command/suite boundary, especially assurance that tests do not load Stage B or rewrite protected/historical Stage C outputs.
8. Confirmation of the permitted synthetic fixture location and rule that fixtures cannot enter scientific releases/datasets.

Formal JSON Schema validation is already documented complete under C1-01 for its locked CPython 3.14.7/macOS arm64 environment. That does not automatically authorize changing or expanding C1-01, nor establish validation on another platform. An M1 task may reuse the approved environment only if its owner authorizes those test files and execution scope.

## 7. Deliverable status

| Requested deliverable | Status |
|---|---|
| M0 baseline verification report | **Completed** — this document. |
| M1 evidence/quantity contract | **Not created** — implementation stopped because no official task ID/file scope was established. Existing overlapping contracts need an authorized canonicalization decision first. |
| Compatibility decision table | **Preliminary gap map included above**; not an authoritative scientific contract. |
| Synthetic fixture suite (12 cases) | **Not created or run** — would be implementation outside an established task scope. |
| Test execution report | **No M1 tests run** — 0 passed, 0 failed, 0 skipped; test execution was intentionally not attempted. Existing reports contain earlier test evidence but it is not new M1 evidence. |
| Remaining scientific gaps | Basis, protocol, compatible raw/cooked evidence, measured yield/mass, source conflicts, identity review, and independent validation remain scientific evidence questions; synthetic tests cannot resolve them. |
| Next recommended milestone | Obtain official owner registration/authorization and exact scope for the contract work, while respecting the current C1B-02 predecessor gate. If the owner does not authorize a new task or determine it is sequence-eligible, continue C1B-02 through its existing owner/partner requirements rather than implementing M1. |

## 8. Files changed and boundaries

Only this new additive report was created. No existing code, schema, test, dataset, release, manifest, or historical output was changed. The pre-existing untracked `reports/research_prototype/` directory was preserved; no files in it were overwritten. Stage B and embedded Stage B snapshots were not accessed. No Stage A data/model was read or executed. The fixed 117-observation boundary was not queried, tested, recalculated, or changed. No Stage D files were read or modified. No tests were run. No remote Git operation was performed.
