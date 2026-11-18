# Owner Decision Request — Proposed M1 Evidence and Quantity Contract

**Decision requested:** whether to register and authorize this work.  
**Current status:** NOT AUTHORIZED. This document is a request only; it does not create an official task ID or change the Stage C sequence.

## Decisions for the project owner

Please record one answer for each item:

1. **Task registration and placement:** Should the proposed contract work be registered as a new official Stage C task? If yes, provide its official task ID, phase, register location, and acceptance criteria. Do not use `M1` as an official ID unless you assign it through the official register.
2. **C1B-02 dependency:** Choose one:
   - **Proceed independently:** authorize this narrowly scoped contract task while C1B-02 remains blocked, and document why this does not bypass a required predecessor gate.
   - **Wait:** do not begin until C1B-02’s owner-designated handoff and partner Windows/browser verification are complete.
3. **Canonical contract:** Approve or reject the recommendation below. Identify the authoritative existing schema and any contracts it composes with.
4. **Edit scope:** Approve the exact candidate files listed below, remove files from scope, or add a file with a written reason. No file is editable until this list is approved.
5. **Scientific semantics:** Approve, amend, or return the definitions and compatibility policies below for qualified scientific-owner review.
6. **Testing boundary:** Approve the synthetic cases, isolated command/suite, and explicit exclusions below. Confirm that fixtures stay outside scientific datasets/releases and tests do not access Stage B or rewrite historical outputs.
7. **Schema environment:** Confirm whether the already documented C1-01 Python 3.14.7/macOS arm64 environment may be reused for the focused Draft 2020-12 tests; this request does not authorize changing its lock or installing dependencies.

## Sequencing decision: C1B-02

The current task evidence says C1B-02 is blocked on an owner-designated handoff and partner Windows/browser verification. The proposed M1 task has no official ID and no registered dependency declaration. Therefore **M1 cannot proceed merely because it is technically independent**.

Recommended disposition: register it in the official sequence and explicitly decide whether a bounded Phase 1 contract task may proceed while C1B-02 is blocked. If the official sequence or predecessor rules require C1B-02 first, M1 waits. If the owner authorizes independent work, record the dependency rationale and ensure it does not implement C2-01 or change any Phase 1B/Phase 2 release or scientific data. No bypass is assumed here.

## Recommended contract to evaluate first

**Recommendation (not a decision):** evaluate `stageC/schemas/food_composition_schema.json` as the candidate anchor. It already carries source-reported and normalized concentration/unit fields, food state and use classification, moisture basis, analytical method, source references, and source/mapping review metadata. That makes it the closest existing source-measurement contract and reduces the risk of creating a duplicate schema.

Before changing it, compare its scope with `stageC/schemas/phase2_source_pair_audit.schema.json`, `stageC/schemas/phase2_cooked_concentration.schema.json`, `stageC/schemas/provenance_schema.json`, the semantics and gates in `stageC/src/stage_c/cooking_integration.py`, and the recipe/yield contract. The likely design is to compose or reference these use-specific contracts where appropriate, not force audit rows, predictions, and measured food composition into one record. The owner/scientific lead must decide which contract is canonical and how consumers remain backward compatible.

## Minimum candidate file list requiring approval

This is a proposed allowlist only. **No listed file has been authorized for modification yet.**

1. `stageC/schemas/food_composition_schema.json` — candidate anchor; modify only if approved as canonical.
2. `stageC/src/stage_c/cooking_integration.py` — only if an existing compatibility/quantity behavior gap is demonstrated; avoid parallel gates.
3. `stageC/tests/test_cooking_integration.py` — focused behavior tests for the approved contract.
4. `stageC/tests/test_food_composition_contract.py` — proposed new focused schema/contract test module if existing tests cannot cover the approved shape without unrelated coupling.
5. `stageC/tests/fixtures/evidence_quantity_contract/` — proposed new, clearly synthetic fixtures only; never scientific observations or release inputs.
6. `stageC/reports/research_prototype/M1_CONTRACT_IMPLEMENTATION_REPORT.md` — proposed task evidence report after authorization and execution.

No Phase 1B/Phase 2 release, manifest, accepted observation, source dataset, Stage A/B/D file, app integration, or dependency lock is in the proposed scope. Any essential scope expansion requires a separate written owner decision before editing.

## Scientific definitions requiring approval

The owner/scientific lead should approve these definitions and any conversion policy. A qualified reviewer must resolve source-specific scientific compatibility; project-owner approval alone does not adjudicate source evidence.

| Quantity or rule | Proposed definition for decision |
|---|---|
| **Apparent concentration ratio (ACR)** | `C_cooked / C_raw` as a unitless ratio, optionally displayed as `100 × ratio` percent. Same analyte and compatible numerator/denominator basis are required. It is not total-mass retention. |
| **Total-mass retention** | `100 × (C_cooked × M_cooked) / (C_raw × M_raw)`. Requires comparable concentration measurements and measured raw/cooked edible mass, or an explicitly approved and source-supported yield conversion. Concentration units and mass units must be dimensionally compatible. |
| **Cooked concentration** | Absolute measured concentration in the cooked/as-eaten matrix with explicit unit, denominator, state, and source; a calculated value is allowed only through an approved compatible pathway with traceable inputs. |
| **Yield** | Food mass after preparation divided by starting edible food mass, with the denominator and handling stated. Yield is not analyte retention. Confirm whether the contract stores a fraction or percent and how evaporation/draining/edible losses are represented. |
| **Other quantity** | Preserve the source-defined name, formula, unit, and denominator. Do not coerce it into ACR, retention, yield, or cooked concentration. |
| **Measurement basis** | Keep as-received, as-analyzed, wet-weight, dry-weight, lyophilized, cooked/as-eaten, source-defined, and unknown as distinct values. Unknown remains unknown. No generic moisture conversion. |
| **Unit conversion** | Convert only with dimensionally valid, explicitly recorded formulas and source-supported inputs. Preserve original value/unit; store normalized value/unit and conversion provenance separately. Do not treat basis conversion as a unit conversion. |
| **Cooking-method compatibility** | Require the owner-approved fields needed for the intended endpoint (for example method, time, temperature, medium, equipment, draining, and sample handling). Missing required conditions remain unavailable; method-name similarity alone is not equivalence. |
| **Identity compatibility** | Food and compound must have source-supported, reviewed identities at the level required by the claim. Missing or ambiguous identity blocks calculation. |
| **Evidence quality** | Qualitative-only evidence cannot support a numeric retention or concentration estimate. Conflicting source evidence remains conflicted until qualified review; do not average or choose the favorable result automatically. |
| **Unavailable states** | Distinguish at least missing, unresolved, incompatible, conflicting, not evaluated, and blocked by authorization. A missing value is never numeric zero. |

## Minimum synthetic test and fixture scope requiring approval

All fixtures must contain conspicuous synthetic identifiers/labels and be isolated from scientific data, release builds, and source acquisition. Requested cases:

1. Compatible measured raw/cooked concentrations with same identity, basis, and valid units.
2. Incompatible raw/cooked measurement bases.
3. Different or dimensionally incompatible units; also verify a valid conversion retains original values and formula.
4. Missing food identity.
5. Unresolved compound identity.
6. Missing required cooking conditions.
7. Total-mass retention requested without measured raw/cooked mass or an approved yield.
8. Qualitative-only cooking evidence offered for a numeric estimate.
9. Missing raw concentration.
10. Unsupported or unclassified retention estimate, including ACR incorrectly offered as mass retention.
11. Conflicting source evidence; result stays unresolved/conflicted.
12. Valid partial recipe calculation; supported components are traceable and the overall result is explicitly partial, with no unsupported total.

Required outcomes: positive cases validate only when all approved gates pass; negative/unresolved cases return a reason-coded nonnumeric result; cooked-concentration and total-mass-retention calculations are withheld when required evidence is absent. These tests establish software behavior only, not scientific validity.

Proposed test boundary: focused approved schema/contract and `test_cooking_integration.py` tests only, using the approved C1-01 environment if the owner permits. Do **not** run tests that load Stage B, query protected snapshots, or rewrite historical Stage C audit outputs (including the existing in-place Phase 2 source-audit test) unless a separate safe isolated procedure is authorized.

## Blank owner authorization record

```text
Official task ID: ______________________________________________
Official phase and register entry/link: _________________________
Task title and acceptance criteria approved: ____________________
Decision on proceeding while C1B-02 is blocked: PROCEED / WAIT
If PROCEED, predecessor/dependency rationale: ___________________
Canonical contract selected: ___________________________________
Contract composition/backward-compatibility decision: ___________
Approved files (copy exact paths): _____________________________
Scientific definitions approved/amended: _______________________
Required qualified scientific reviewer/role: ___________________
Approved fixture/test files and exact test command: ______________
Stage B exclusion/test isolation confirmed: YES / NO
C1-01 environment reuse approved: YES / NO
Additional files or scope exceptions and reasons: _______________
Owner name and documented authority: ___________________________
Owner signature or recorded approval reference: _________________
Date: _________________________________________________________
```

## STOP condition

**Do not implement, edit schemas/source/tests, add fixtures, or run M1 tests until the authorization record above is completed and the official task register contains the approved task ID, placement, acceptance criteria, dependency decision, canonical contract, and exact file allowlist.** A conversational “yes” without the task/scope details does not resolve scientific semantics or file ownership. If the owner chooses WAIT, stop M1 until the specified C1B-02 acceptance evidence is complete.
