# CookRisk Execution Cycle 5 — final report

**Execution date:** 2026-11-04  
**Scope:** Stage C and Stage D scientific evidence, deployment readiness, uncertainty, review workflow, application, and integration.  
**Overall:** Meaningful additive progress delivered; several phases correctly remain in progress because required scientific decisions and human reviews are absent.

## A. Executive summary

Cycle 5 added a structured Stage A owner-decision and deployment gate, source-linked uncertainty-gap reporting, compound-separated synthetic sensitivity analysis, a broader multi-food literature screen, an expanded source-pinned mechanism registry, a traceable human evidence-review workflow, clearer interpretation decision traces, and a local browser prototype joining Stage C recipes/meals with Stage D review.

The literature search found two useful raw food-composition source comparisons (spinach/lutein and broccoli/ascorbic acid), with eight additional cooking observations preserved. Both raw comparisons show material source-to-source differences and neither compares predictions to published cooked data. They are not validation results. The mechanism registry contains 25 source-pinned candidates from seven studies; none has independent expert acceptance. The 317-row Stage D review queue is usable, but all 317 human statuses remain `NOT_REVIEWED`.

Verified test results include 261 Stage C tests, 63 Stage D tests, 79 isolated Phase 3 release tests, 13 Phase 4 registry tests, and 5 benchmark tests, all passing with zero failures or skips in the final verified runs. All 33 active JSON schemas passed Draft 2020-12 metaschema validation. Four pinned release manifests passed file-hash and byte-count checks. Passing software tests verifies software contracts only; it does not validate scientific predictions.

## B. Original roadmap status

### Stage C

| Phase | Status | Cycle 5 evidence and tests | Blocker and exact next action |
|---|---|---|---|
| 1 — Software Foundation | **COMPLETE** | Existing foundation retained; the local service now uses the existing calculation/contract modules. Stage C suite: 261 passed. | Maintain the existing contracts; no new completion claim is made by this cycle. |
| 1B — Food Data Acquisition | **COMPLETE_WITH_DOCUMENTED_LIMITATIONS** | Pinned Phase1B-v1.3.2 has 584 food rows and 584 mappings, 509 exact quantitative mappings. Catalog uncertainty text is not a structured interval. | Acquire source-compatible structured uncertainty and food-lot context; do not parse free-text notes into numeric ranges. |
| 2 — Cooking-Retention Integration | **IN_PROGRESS** | Added the RF-01–RF-15 owner tracker, package validator readiness gate, handoff, dashboard, and synthetic demo. Focused deployment tests: 22 passed. | Owner responses remain 0/15 approved. Obtain the completed decisions, full serialized package and manifest, target/denominator definition, and independent review before any inference. |
| 3 — Recipe & Meal Exposure Engine | **COMPLETE_WITH_DOCUMENTED_LIMITATIONS** | Existing recipe-to-meal path is exercised by the synthetic Cycle 5 integration test; isolated Phase3-v0.1.2 suite: 79 passed. The app keeps raw-reference and consumed amounts distinct. | Do not report cooked exposure until a compatible accepted Phase 2 estimate and required measurements exist. |
| 4 — Uncertainty & Sensitivity | **IN_PROGRESS** | Added a machine-readable gap registry, source-linked dimensions, and compound-specific interval sensitivity. Synthetic three-ingredient/two-compound example; focused uncertainty tests: 12 passed; registry tests: 13 passed. | The pinned catalog has no structured concentration intervals; analytical variability and cooking yield remain coverage-only until valid source-specific propagation contracts exist. |
| 5 — Exposure Validation & Benchmarking | **COMPLETE_WITH_DOCUMENTED_LIMITATIONS** | Broader nine-pair screen; ten quantitative observations; two raw-to-raw source contrasts; benchmark tests: 5 passed. See [screen and source matrix](phase5/CYCLE5_BROAD_BENCHMARK_SCREEN.md). | Obtain genuinely commensurate cooked observations and corresponding model estimates before calculating predictive validation metrics. |
| 6 — User-Facing Application | **IN_PROGRESS** | Local non-production UI and API now cover food/compound search, recipe/meal calculation, uncertainty/provenance, evidence filtering, mechanism candidates, assignment export, review history and explicit reviewer actions. API tests: 8 passed; JavaScript syntax check passed. | Complete browser-level workflow, accessibility, security/privacy and production-readiness reviews only after scientific gates are satisfied. |
| 7 — Stage C Finalization | **IN_PROGRESS** | Cross-stage lineage report and synthetic tests added; four pinned release manifests verified; no historical release overwritten. | Keep release open until Phase 2 decisions/data, comparable validation evidence and required independent reviews are resolved. |

### Stage D

| Phase | Status | Cycle 5 evidence and tests | Blocker and exact next action |
|---|---|---|---|
| 1 — Evidence–Exposure Integration Architecture | **COMPLETE_WITH_DOCUMENTED_LIMITATIONS** | Existing cross-stage contracts remain in place; full Stage D suite: 63 passed. | Continue requiring pinned release provenance and comparability review for any future linkage. |
| 2 — Evidence Normalization & Classification | **COMPLETE_WITH_DOCUMENTED_LIMITATIONS** | Existing normalization is retained; missing/null/conflict states remain explicit. Full Stage D suite: 63 passed. | Human/source adjudication remains separate from normalized source labels. |
| 3 — Exposure–Evidence Comparability | **COMPLETE_WITH_DOCUMENTED_LIMITATIONS** | Six tri-state gates remain explicit; transient/unverified Phase 3 results are refused in Cycle 5 integration coverage. | Supply compatible, verified exposure and source context before any comparison can be resolved. |
| 4 — Mechanism-Based Integration | **IN_PROGRESS** | Registry expanded from 12 to 25 source-pinned candidates across 7 primary studies; mechanism tests: 13 passed. All 25 remain pending independent review. | Review the two abstract-only records, resolve documented source/identity discrepancies, and obtain independent reviewer dispositions. |
| 5 — Uncertainty & Evidence Assessment | **IN_PROGRESS** | Stable IDs, filters, action schemas, append-only hash-chained history, assignment export and coverage dashboard for 317 records; 19 focused tests passed. | Assign real reviewers and record source locator, rationale and review date. No automated state is a human decision. |
| 6 — Risk Interpretation Framework | **IN_PROGRESS** | Ordered rule trace and conservative gates preserve null, negative, missing and conflicting evidence; mechanism-only evidence cannot promote itself. Interpretation tests: 13 passed. | Obtain expert-approved policy and validate against appropriate external outcomes before any broader interpretation claim. |
| 7 — Validation & Benchmarking | **NOT_STARTED** | Cycle 5 raw source-to-source comparisons do not constitute model validation. | Define a compatible benchmark protocol and obtain matched cooked data plus valid model estimates. |
| 8 — Application & Reporting | **IN_PROGRESS** | Local research prototype exposes queue/search/review APIs and UI, assignment exports, source detail and audit history. Stage C API tests: 8 passed; JavaScript syntax check passed. | Authentication, multi-user controls, security/privacy, accessibility, and browser-level acceptance remain absent. |
| 9 — Final Integration & Release | **IN_PROGRESS** | Lineage and current release hashes checked; Stage B queue is still unreviewed and Phase 2 has no accepted cooked estimates. | Do not issue a final integrated release until the external scientific and human gates above are resolved. |

## C. Workstream deliverables

### A — Phase 2 owner handoff and deployment gate

- Added `stageC/src/stage_c/deployment_decisions.py`, `stageC/schemas/stage_a_owner_decision_tracker.schema.json`, and `stageC/data/phase2/owner_decision_tracker.json`.
- Added one-page handoff and readiness dashboard under [`stageC/reports/phase2`](phase2/STAGE_A_OWNER_HANDOFF_ONE_PAGE.md). All 15 RF questions are pending; no supplied model package is available, package integrity is blocked, independent acceptance is pending, and inference remains unauthorized.
- Added a reproducible synthetic demonstration and tests for decision completeness, package path/hash handling, tampering, and inconsistent records. No real Stage A model was loaded or executed.

### B — Phase 4 uncertainty coverage

- Expanded `stageC/src/stage_c/uncertainty.py` and uncertainty schemas; added a gap-registry builder, compound-separated interval sensitivity, and test-only synthetic multi-compound meal fixture.
- Missing dimensions retain record/source identifiers and reasons. Yield and analytical variability are tracked but not numerically propagated without validated input semantics. Point estimates, deterministic interval endpoints and probability distributions remain distinct.
- Worked synthetic totals: C-1 = 0.625 mg with endpoint range 0.324–1.089 mg; C-2 = 0.425 mg with range 0.22032–0.74052 mg. These are synthetic software fixtures, not scientific measurements.
- See [`CYCLE5_UNCERTAINTY_GAPS_AND_MULTICOMPOUND_SENSITIVITY.md`](phase4/CYCLE5_UNCERTAINTY_GAPS_AND_MULTICOMPOUND_SENSITIVITY.md).

### C — Broader benchmark evidence screen

- Screened nine food/analyte combinations across spinach, broccoli, green tea, basil, plus onion as a scope boundary. Two primary studies yielded 10 transcribed observations and two context-limited raw source comparisons; eight cooked observations are preserved separately.
- Spinach/lutein: Chang et al. (2013), Table 2, five states, HPLC-DAD, triplicate experiments. Phase1B raw is 6.89 mg/100 g; study raw is 0.495 mg/100 g, a 13.919-fold source difference.
- Broccoli/ascorbic acid: Lee et al. (2018), Table 2, five states, HPLC-UV, duplicate trials/analyses. Phase1B raw is 131 mg/100 g; study raw is 66.804 mg/100 g, a 1.961-fold source difference.
- Candidate matrix records exact source locators and exclusion reasons. Dry-weight/wet-weight mismatch, tea preparation, analyte form, food matrix, and inaccessible quantitative source cells were not silently converted or inferred. No model prediction was compared; no external validation was performed.
- Source links and extraction details are in the [screen report](phase5/CYCLE5_BROAD_BENCHMARK_SCREEN.md); observations, candidate matrix, script, tests and manifest are in `stageC/reports/phase5/cycle5_broad_search/`.

### D — Mechanism evidence expansion

- Registry expanded by 13 records to 25 candidates across seven primary studies, sourced against the pinned Stage B file. Twenty-three source reviews used full text or full author manuscripts; two remain abstract-only.
- Candidate relations are separated into 18 inhibition/reduced-activity candidates, 2 induction/increased-activity candidates, and 5 unresolved transport/permeability candidates. This is descriptive extraction, not acceptance.
- PMID 22300367 discrepancy remains preserved. The losartan CYP2C9/CYP2C19 disagreement remains open. All records remain pending manual review and identity adjudication.
- See [mechanism registry report](../../stageD/reports/phase45_mechanism_registry_report.md) and reviewer packets.

### E — Evidence review workflow

- The 317-row Stage B evidence queue now has stable review IDs, server-side filters, assignment JSON/CSV exports, a coverage dashboard, event schemas and a hash-chained append-only reviewer-action log. Human decisions remain stored separately from the immutable source queue. The action schema is version 1.0.0; no prior action log existed to migrate, so no legacy migration is claimed. Unsupported schema versions fail closed; a future version change needs an explicit migration before old actions are reused.
- Expert accept/reject actions require an earlier ready-for-expert state and expert role. The action log is versioned; unsupported event/schema states fail closed. Successful action submissions receive a cumulative versioned backup snapshot. The prototype is single-writer, not a multi-user review database.
- Current state: 317/317 `NOT_REVIEWED`; zero source-verified, expert-accepted or expert-rejected; zero automatic approvals or negative inferences. No action was submitted by this cycle.
- See [review queue report](../../stageD/reports/phase5/evidence_review_queue_report.md).

### F — Interpretation framework

- `stageD/src/stage_d/interpretation.py` now returns ordered rule traces and explicit rationale. Known conflicts take precedence; missing evidence maps to insufficient evidence; mechanism-only findings cannot reach research relevance; null/negative results stay scoped to tested conditions; completed expert decisions require reference and rationale.
- Synthetic boundary cases and output schema were expanded. This is a nonclinical research state framework, not an expert-approved policy, clinical risk score, or FDA/ICH-endorsed rule set.
- See [interpretation design](../../stageD/reports/phase6/INTERPRETATION_FRAMEWORK_DESIGN.md).

### G — Local research application

- Reused the existing recipe, meal, evidence, comparability and contract modules. Added food/compound search, mapped-only compound choices, input validation messages, cooked-estimate eligibility messaging, provenance, uncertainty coverage, CSV/JSON export, and distinct raw/cooked reference display.
- Added Stage D queue filters, record detail, mechanism candidate display, review history, assignment CSV export, coverage, and confirmed human-action submission using server-returned workflow states. No formula was duplicated in JavaScript.
- Reviewer actions go to Stage D JSONL history and backup snapshots; Stage B records remain read-only. The event schema has a version and rejects incompatible versions; there were no existing event rows to migrate, so a future schema migration path remains follow-up work. The local server refuses public bind addresses. The app is clearly non-production.
- Setup and limits: [`stageC/app/README.md`](../app/README.md). Liquid cooked estimates are withheld because the current form/API has no cooked-volume measurement.

### H — Cross-stage integration and release readiness

- Added [`CYCLE5_DATA_LINEAGE_AND_RELEASE_READINESS.md`](phase7/CYCLE5_DATA_LINEAGE_AND_RELEASE_READINESS.md) and `stageC/tests/test_cycle5_integration.py`.
- Synthetic recipe → meal → uncertainty linkage passes; a transient/unverified Phase 3 result is blocked from evidence comparison. App API tests preserve source provenance and avoid cooked values without compatible evidence.
- Four pinned packages passed manifest, byte-count and SHA-256 checks: Phase1B-v1.3.2 (1,324 artifacts), Phase2-v0.3.1 (50), Phase3-v0.1.2 (47), Phase4-v0.1.2 (18). Phase1B's own release verifier also passed.
- No performance bottleneck is demonstrated for the current 317-record local review corpus. No load test, security review, concurrency test, or performance optimization was justified or claimed.

## D. Scientific evidence acquisition

The benchmark screen is broader than the earlier onion/quercetin search. The 10 study observations comprise five spinach/lutein preparation states and five broccoli/ascorbic-acid states. Raw-to-raw values are mathematically comparable on a mass basis, but food lots, geography, sample handling, extraction methods and analytical protocols differ. The comparisons therefore describe source discrepancies only. The eight cooked concentrations and study retention observations are not compared to Stage C outputs because no matched cooked model estimate exists.

Seven other candidate combinations were excluded from paired comparison for documented reasons including wet/dry basis mismatch, tea preparation mismatch, uncertain operational analyte equivalence, nonmatching glycoside/aglycone identity, uncalibrated chromatograms, or inaccessible exact quantitative table data. No value was estimated from a figure or inferred from a percentage.

Mechanism source extraction added six rows from the 2025 food-additive transporter/Caco-2 study (PMID 40773056) while retaining interference and assay limitations, plus separate Stage B endpoints already supported by full-text sources. Inhibition, induction, substrate, permeability and author-interpreted human probe phenotypes remain distinct. The exact source references and locators are in the linked workstream report and reviewer packets.

## E. Application

Start from the repository root with:

```powershell
python stageC/app/server.py --host 127.0.0.1 --port 8765
```

Then open `http://127.0.0.1:8765/`. The service is loopback-only and uses pinned local data. Application API route tests are in-process because this managed Windows execution environment denies local socket creation; no remote service is used. Reviewer action persistence is an append-only JSONL hash chain separate from Stage B plus cumulative versioned backups. There is no authentication, multi-user coordination, or production qualification. JavaScript syntax was checked with `node --check`; no browser automation or accessibility audit was run.

## F. Human review

**Actual human source reviews entered during this cycle: 0.** All 317 queue entries remain `NOT_REVIEWED`; all 25 mechanism candidates remain pending independent review. The UI action form was not submitted. Synthetic mutation tests use explicitly named synthetic reviewers and temporary files; they do not change repository review state. Machine triage, assignment and export are not human review.

## G. Scientific integrity

- Stage A inference executed: **NO**.
- Stage A source modified: **NO**.
- Stage B original source records modified: **NO**.
- Accepted cooked-concentration estimates: **0**.
- Published-data comparison: **YES**, two raw-to-raw source discrepancies only; no model prediction comparison.
- External predictive validation: **NO**.
- Expert review/acceptance: **0** actual dispositions.
- Clinical interpretation or patient-specific advice: **NO**.
- Missing values remained missing; no uncertainty ranges, source observations or human decisions were fabricated.

## H. Release integrity and test results

Read-only Git checks showed no changes under `stageA` or `stageB`; HEAD stayed `8545029a4bae1bc923fdc840bbfe681b2d7bef03`. No Git branch, index, commit, pull, push or history operation was performed. No historical release was overwritten and no Cycle 5 release package was created. The release hash checks establish byte integrity, not scientific validity.

Final verified tests and checks:

| Suite/check | Result |
|---|---:|
| Stage C root tests | 261 passed, 0 failed, 0 skipped |
| Stage C Phase 4 registry | 13 passed, 0 failed, 0 skipped |
| Stage D full suite | 63 passed, 0 failed, 0 skipped |
| Phase3-v0.1.2 isolated suite | 79 passed, 0 failed, 0 skipped |
| Active Stage C / Phase 4 / Stage D schema metaschemas | 33 valid, 0 invalid |
| Stage A deployment tracker/package tests | 22 passed, 0 failed, 0 skipped |
| Uncertainty coverage | 12 passed, 0 failed, 0 skipped |
| Benchmark ingestion/comparison | 5 passed, 0 failed, 0 skipped |
| Mechanism registry | 13 passed, 0 failed, 0 skipped |
| Evidence queue + review workflow | 19 passed, 0 failed, 0 skipped |
| Interpretation | 13 passed, 0 failed, 0 skipped |
| Application API | 8 passed, 0 failed, 0 skipped |
| Cross-stage integration | 1 passed, 0 failed, 0 skipped |
| Pinned release manifests | 1,439 packaged artifacts verified across four releases |
| Browser JavaScript syntax | `node --check` passed |

Focused rows overlap their corresponding full suites and are not additive to the total. Initial verification attempts included a wrong Phase 3 discovery path (`NO TESTS RAN`), an incorrect benchmark module import path, and a schema check without the temporary pinned `jsonschema` dependency. These were corrected by using the package's actual test directory, unittest discovery in the benchmark folder, and the pinned development dependency; the corrected runs above pass. An early uncertainty integration test also exposed an import-path and decimal-string assertion mismatch; both were corrected, after which the cross-stage test passed. No unresolved test failure remains.

## I. Next milestone — three highest-value actions

1. **Close the Phase 2 owner gate.** Obtain all 15 RF decisions, the complete serialized model package and artifact manifest, an agreed `Retention_Final` numerator/denominator and operational target definition, and independent scientific/operational review. Until then, keep Stage A inference unauthorized and accepted cooked estimates at zero.
2. **Acquire a matched cooking benchmark and resolve compatible Phase 2 evidence.** Source a study with the same food matrix, exact analyte identity, raw/cooked preparation, analytical method, concentration basis, cooking conditions, and replication. Obtain the corresponding valid Stage C estimate only after Phase 2 approval; then run a pre-specified comparison. Current raw-source discrepancies do not meet this prerequisite.
3. **Begin real Stage D review.** Assign the 317-row review work package and the 25 mechanism candidates to named qualified reviewers. Require source locators, identity/context/conflict adjudication, dated rationale, and a separate expert disposition before any evidence or interpretation status advances.
