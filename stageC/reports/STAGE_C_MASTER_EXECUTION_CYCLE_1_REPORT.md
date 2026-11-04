# CookRisk Stage C — Master Execution Cycle 1 Baseline

**Date:** 2026-11-04  
**Purpose:** Baseline audit and next-cycle plan only. No Stage C implementation or scientific data was changed in this cycle.  
**Overall Stage C status:** **IN PROGRESS**  
**Repository:** branch `main`, HEAD `067c6d117bdcf4f9274606499150a859b7c791c6`.

## A. Executive summary

The 4 November master audit is broadly directionally correct, but this read-only baseline found two updates and one additional current test failure:

1. The host's current focused Stage C API suite ran **10 tests: 9 passed, 1 failed**. The failing review-action test expects an unauthenticated synthetic review to succeed. Current Stage D workflow deliberately rejects submissions when no trusted identity provider is configured. That rejection is fail-closed; it must not be bypassed to make the old expectation pass.
2. Current read-only release verification passes for Phase1B-v1.3.2 (1,324 artifacts), Phase2-v0.3.1 (50 artifacts), Phase3-v0.1.2 (47 artifacts), and the embedded StageB V20 package in exact-byte mode (839/839). The embedded V20 canonical-text mode still reports the known single newline-policy discrepancy. This resolves the earlier report of widespread nested mismatches for this local copy, but Windows clean-checkout reproduction remains unverified.
3. The active host is Python 3.14.7 and cannot import `jsonschema`. Formal schema validation is therefore not reproducible in the current environment. An older Cycle 5 report says 33 schemas passed Draft 2020-12 validation; the later dependency report says 50 files were JSON-parsed only, and the present host confirms the dependency is absent. Treat current formal validation as **not established** until the approved environment and exact command are available.

Phase1B's latest recorded content count is 584 food records/mappings, 116 compounds with quantitative data overall and 80 eligible in ordinary foods. These content counts were not recounted in this baseline; the verifier establishes packaged bytes, not scientific coverage. Phase 2's fixed audit boundary remains 117 observations, 22 candidate combinations and **zero accepted cooked-concentration outputs**. The 117 observations were not re-audited, extended, or recalculated.

The highest-value next local work is to make the app's review-action state explicit and safe when authentication is unavailable, then run focused tests. In parallel, the team needs an approved schema-validation environment and source-compatible cooking evidence; neither can be fabricated locally.

## B. Phase-wise status

Status meanings follow the required execution classifications. Prior status refers to the supplied 2026-11-04 master audit, not an assertion that the earlier audit freshly verified every item.

| Phase | Previous status | Current status | Implemented / verified now | Remaining work and blockers |
|---|---|---|---|---|
| **Phase 1 — Software Foundation** | Partially Implemented | **IN PROGRESS** | Modular schemas, validation, mapping, units, provenance, exposure engine, CLI and tests exist. Current app API focused test result is 9 pass / 1 fail. Python 3.14.7 lacks `jsonschema`. | Resolve the review-action API/authentication contract without weakening identity checks; obtain an approved, complete schema dependency environment and establish formal validation; rerun regression tests safely. |
| **Phase 1B — Scientific Food Data Acquisition** | Implemented, Validation Pending | **IMPLEMENTED, VALIDATION PENDING** | Phase1B-v1.3.2 verifier: **PASS, 1,324 artifacts**, manifest SHA-256 `df3a95ae0957b68a89e38098c0824877196aa74ef7dd92573e6ab1f37e39b9b5`. Latest recorded coverage: 584 food rows/mappings; 116 quantitative compounds overall, 80 ordinary-food eligible. | Counts are reported from the latest continuation report, not recounted here. Embedded V20 exact mode passes; canonical mode reports one CRLF/LF policy discrepancy in `validation/final_validation_results.csv`. The owner hash-policy decision and Windows clean-copy check remain open. Do not equate 130 identity-complete compounds with quantitative food coverage. |
| **Phase 2 — Cooking-Retention Integration** | Implemented, Validation Pending | **IMPLEMENTED, VALIDATION PENDING** | Phase2-v0.3.1 verifier: **PASS, 50 artifacts**. Compatibility gates and evidence audit exist; accepted cooked output remains zero. | Fixed scope: 117 observations, 22 combinations. Basis, identity, matrix, condition/yield and retention evidence gaps remain. Stage A inference is unauthorized; RF-01–RF-15 remain pending. Do not calculate outputs until every evidence gate is met. |
| **Phase 3 — Recipe & Meal Exposure Engine** | Partially Implemented | **PARTIALLY IMPLEMENTED** | Phase3-v0.1.2 verifier: **PASS, 47 artifacts**. Recipe/meal engine, CLI, provenance and raw-reference calculations exist; guarded cooked path remains evidence-dependent. | Independent matched recipe/cooked benchmark and valid Phase 2 estimate are absent. Do not present raw-reference exposure as cooked exposure. |
| **Phase 4 — Uncertainty & Sensitivity Analysis** | Partially Implemented | **PARTIALLY IMPLEMENTED** | Uncertainty code, gap registries and deterministic/synthetic sensitivity tests exist. | Combined cooked uncertainty is not scientifically supported. Phase4-v0.1.2 is documented **UNRECOVERABLE** from searched accessible sources: 10/18 artifacts mismatch and detached digest fails. Keep it blocked and immutable; any future successor needs independently verified evidence and a new version. |
| **Phase 5 — Exposure Validation & Benchmarking** | Partially Implemented | **PARTIALLY IMPLEMENTED** | A bounded published-source screen contains 10 observations and two context-limited raw-to-raw comparisons, with scripts/tests and provenance. | This is not an independent exposure/model benchmark. The comparisons have material source/context differences; no validation performance claim is supported. Obtain a compatible independent reference dataset and prespecified metrics. |
| **Phase 6 — User-Facing Application** | Partially Implemented | **IN PROGRESS** | Local-first app and browser assets exist; app health/catalog now report Phase 4 as degraded/withheld while serving other verified data. Current API test confirms the real catalog loads 584 foods with Phase 4 blocked. | Current focused API run has one stale-success expectation for a review action; no identity provider exists, so safe behavior is rejection. UI/API should make disabled review submission explicit. Windows/browser, accessibility, security/privacy and production qualification remain unverified. |
| **Phase 7 — Stage C Finalization** | Partially Implemented | **IN PROGRESS** | Current local manifests for Phase1B, Phase2 and Phase3 verify; historical handoff and reproducibility reports exist. | Phase4 integrity failure, schema dependency, current focused API failure, historical full-suite errors/skips, Windows validation, independent scientific benchmarking and zero cooked outputs prevent final acceptance. No final release should be issued. |

### Task register

| Task ID | Phase | Existing implementation | Required work / acceptance criteria | Dependencies / evidence | Status |
|---|---|---|---|---|---|
| C1-01 | 1 | Schemas and validation functions exist; development dependencies are pinned in `stageC/requirements-dev.txt`. | Establish an owner-approved, reproducible environment including all conditional/format dependencies; run positive/negative Draft 2020-12 fixtures and record package/hash versions. | Current host lacks `jsonschema`; package source/license and complete lock not approved. | PENDING EXTERNAL INPUT |
| C1-02 | 1 / 6 | Review workflow route delegates to Stage D; current Stage D submission requires trusted authentication. | Make the UI/API state explicit and test unauthenticated rejection with no action-log or backup writes; never provide a fake provider. | Current focused API failure; `stageD/src/stage_d/reviewer_identity.py` says submission is disabled without a trusted provider. | IN PROGRESS |
| C1B-01 | 1B | Phase1B-v1.3.2 has a passing local manifest verifier. | Reconfirm quantitative-content count via an explicitly safe read-only method and document ordinary-food vs contextual/identity counts separately. | Existing continuation report records 116 overall / 80 ordinary; no recount in this cycle. | IMPLEMENTED, VALIDATION PENDING |
| C1B-02 | 1B / 7 | Embedded StageB V20 exact-byte manifest verifies 839/839 in current local package. | Obtain owner decision on exact vs canonical-text policy and run clean-copy/Windows verification against the chosen rule. | Exact passes; canonical mode fails only for newline-normalized `validation/final_validation_results.csv`; historical Windows result not reproduced. | PENDING EXTERNAL INPUT |
| C2-01 | 2 | Source-pair audit, crosswalk, compatibility reviews and a verified Phase2 release exist. | Keep 117-record audit boundary fixed; produce an accepted cooked estimate only when identity, basis, units, method, conditions, matrix, source quality and uncertainty all pass. | Existing report: 0 accepted, 21 unresolved spice combinations, 1 qualitative-only rejection. RF-01–RF-15 pending. | BLOCKED |
| C3-01 | 3 | Recipe/meal calculations and raw-reference exposure work for supported inputs. | Independently validate real recipe calculations and measured yield/mass balance; maintain raw/cooked distinction. | No suitable independent matched benchmark and no accepted cooked Phase2 values. | IMPLEMENTED, VALIDATION PENDING |
| C4-01 | 4 | Interval coverage/sensitivity machinery and synthetic fixtures exist. | Use only source-supported uncertainty inputs; document unsupported parameters; do not emit combined cooked intervals absent evidence. | Phase4-v0.1.2 integrity incident; uncertainty sources incomplete. | BLOCKED |
| C5-01 | 5 | Bounded source search and reproducible descriptive comparison exist. | Acquire a compatible independent benchmark, define inclusion rules/metrics before comparison and reproduce results. | Existing raw contrasts are context-limited and not validation. | PENDING EXTERNAL INPUT |
| C6-01 | 6 | Local app serves verified catalog and marks Phase4 context unavailable. | Show accurate degraded state; correct test/API behavior for missing auth without enabling unauthenticated reviews. | Current focused suite: 9 passed, 1 failed. | IN PROGRESS |
| C6-02 | 6 | Windows startup instructions exist; app uses standard-library server. | Have partner run the documented Windows startup and browser workflow on the reviewed working copy; record actual result. | No Windows/browser execution in this environment. | PENDING EXTERNAL INPUT |
| C7-01 | 7 | Phase1B/2/3 manifests pass locally. | Resolve actionable app/API test mismatch, schema validation, clean-copy/Windows chain checks, and full-suite issues; produce an immutable release only after acceptance criteria pass. | Latest recorded full Stage C suite: 249 total, 2 errors, 5 skipped; not rerun in this cycle. | IN PROGRESS |

## C. Files changed

### Created in this cycle

- `stageC/reports/STAGE_C_MASTER_EXECUTION_CYCLE_1_REPORT.md` — this baseline and plan.

### Existing user changes preserved, not created or edited in this cycle

Modified Stage C files already present at the start:

- `stageC/app/README.md`
- `stageC/app/server.py`
- `stageC/app/static/app.js`
- `stageC/app/static/style.css`
- `stageC/src/stage_c/release_adapters.py`
- `stageC/tests/test_app_api.py`

Pre-existing untracked Stage C materials were also preserved: continuation/dependency reports, three baseline snapshots, the RF decision register, and the Phase 4 integrity incident evidence tree under `stageC/reports/`. No Stage C file was deleted.

## D. Scientific integrity

- **Scientific data added this cycle:** none.
- **117 Phase 2 observations:** retained as the fixed already-audited boundary. They were not re-audited, extended, recalculated or regenerated. The test `stageC/tests/test_phase2_source_audit.py` executes a script that writes `stageC/reports/phase2/source_pair_audit_2026-11-03.csv`; the full suite was not run in-place to avoid rewriting that historical audit artifact.
- **Accepted cooked concentrations:** 0, according to the verified Phase2-v0.3.1 release contents and latest report. No measurement, raw reference, concentration ratio, Stage A OOF value or model prediction was promoted to a cooked estimate.
- **Stage A authorization:** not authorized; no Stage A code/model was executed or modified. RF-01–RF-15 remain pending; OOF predictions were not used as new-record inference.
- **Stage B:** source release remains read-only. No compound identity or evidence record was changed. Embedded V20 integrity was checked read-only only.
- **Unsupported assumptions:** none added. Missing evidence and uncertainty remain missing; Phase4-v0.1.2 stays withheld.

## E. Testing and validation

| Test / validation category | Passed | Failed / errored | Skipped / blocked | Command and evidence status |
|---|---:|---:|---:|---|
| Current focused Stage C API tests | 9 | 1 | 0 | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s stageC/tests -p 'test_app_api.py' -v` — **ran now**. Failure: `test_review_action_api_uses_separate_log_and_snapshots_history`, expected HTTP 200; got 400 because no trusted identity provider is configured. Synthetic action is not written successfully. |
| Full Stage C suite | — | 2 errors in last recorded full run | 5 skipped in last recorded full run | `python3 -m unittest discover -s stageC/tests -v` — latest recorded report says 249 total, 2 errors, 5 skipped. **Not rerun now**; the Phase2 audit test rewrites the fixed audit report in-place. |
| Phase1B release manifest | 1,324 artifacts | 0 | 0 | `PYTHONDONTWRITEBYTECODE=1 python3 stageC/releases/Phase1B-v1.3.2/verify_release.py` — **ran now, PASS**. |
| Phase2 release manifest | 50 artifacts | 0 | 0 | `PYTHONDONTWRITEBYTECODE=1 python3 stageC/scripts/build_phase2_v0_3_1_release.py --verify` — **ran now, PASS**. |
| Phase3 release manifest | 47 artifacts | 0 | 0 | `PYTHONDONTWRITEBYTECODE=1 python3 stageC/scripts/build_phase3_v0_1_2_release.py --verify` — **ran now, PASS**. |
| Embedded StageB V20 exact hash verification | 839 entries | 0 | 0 | `PYTHONDONTWRITEBYTECODE=1 python3 <embedded V20>/scripts/manifest_integrity.py verify <embedded V20> --mode exact` — **ran now, PASS**; 839 manifest entries and files, no mismatches. StageB was not modified. |
| Embedded StageB V20 canonical-text verification | 838 entries match under canonical digest; 0 raw-byte mismatches | 1 canonical mismatch | 0 | Same command with `--mode canonical` — **ran now, reports FAIL for `validation/final_validation_results.csv`**: manifest raw digest `949458…` vs canonical digest `d4172d…`. This is the documented exact-vs-canonical policy conflict, not missing/corrupt raw bytes. |
| Formal JSON Schema validation | 0 established now | — | BLOCKED | `PYTHONDONTWRITEBYTECODE=1 python3 -c 'import jsonschema'` — **BLOCKED**, module unavailable in current Python 3.14.7 host. Earlier report claims conflict; no schema validation rerun. JSON parsing is not formal validation. |
| Windows/browser compatibility | — | — | NOT RUN | Instructions exist, but no Windows/browser environment was used. |

Tests above are software verification only. None constitutes independent food science validation.

## F. Reproducibility and integrity

- Runtime inspected: Python **3.14.7**, pip **26.2.1** per latest environment report. This is not the recommended Python 3.12.14 environment from Stage A model provenance.
- `stageC/requirements-dev.txt` pins `attrs==26.1.0`, `jsonschema==4.26.0`, `jsonschema-specifications==2025.9.1`, `referencing==0.37.0`, `rpds-py==2026.9.1`; it is not a complete lock because Python 3.12 conditional/format dependencies are not fully pinned. No packages were installed.
- Phase1B-v1.3.2 manifest SHA-256: `df3a95ae0957b68a89e38098c0824877196aa74ef7dd92573e6ab1f37e39b9b5` — verified now.
- Phase2-v0.3.1: 50 files — verified now. Phase3-v0.1.2 manifest SHA-256 `8a0d532ff35cc8ac88d5cedc0231caf35b94aebac6501c30c55b5db48ff1a9ec` — verified now.
- Embedded StageB V20 raw/exact mode passes 839/839. Canonical mode is inconsistent with exact manifest bytes for one CRLF file; owner decision remains open. Windows clean-copy behavior remains unknown.
- Phase4-v0.1.2 does **not** verify: its incident report records a bad detached digest and 10 of 18 listed artifacts mismatching. Do not regenerate that historical manifest.
- Deterministic app calculation/release chain is not a substitute for an independent scientific benchmark. The current app shows Phase4 context unavailable and Phase2 accepted cooked estimates 0.

## G. Protected scope verification

- Stage A files and model artifacts were not inspected by execution, modified, or run. Read-only Stage A metadata in prior reports remains the only evidence used.
- Stage B source data and evidence records were not modified. The embedded V20 manifest was verified read-only in exact and canonical modes; no hashing policy was chosen.
- No Git branch, index, commit, remote, or history operation occurred. No GitHub or other remote Git access occurred.
- The test run used the repository's temporary Stage D review-log paths and removed them on completion. Existing uncommitted changes remained preserved.

## H. Remaining work and first implementation cycle recommendation

| Task | Priority | Owner / dependency | Acceptance criteria | Recommended next action |
|---|---|---|---|---|
| C6-01 — explicit unavailable reviewer-auth state | P1, locally actionable | App maintainer; no trusted identity provider currently configured | API returns a clear authorization-unavailable response; UI indicates review submission is disabled; test asserts no action log/backup is written; no synthetic identity provider or human approval is introduced. The focused API suite passes under the intended fail-closed contract. | **Recommended first implementation cycle (Cycle 2):** restrict edits to `stageC/app/server.py`, `stageC/app/static/app.js`, `stageC/app/README.md`, and `stageC/tests/test_app_api.py`. Preserve all existing edits and clarify the Stage D identity-provider dependency instead of enabling a submission. |
| C1-01 — approved schema environment | P1, externally dependent | Project owner/maintainer must approve package source, license and complete pins | Draft 2020-12 positive/negative fixture tests and `$ref` validation run in a clean environment with recorded lock/hash. | Request/obtain approved offline wheelhouse or mirror and complete lock; do not guess dependency versions. |
| C1B-02 — release hashing policy / Windows reproduction | P2, owner and partner dependent | Release owner chooses exact-byte or canonical-text rule; partner Windows device | Chosen rule is documented; exact packaged dependency passes from clean checkout; no release files are rewritten. | Preserve current exact bytes, prepare decision record and schedule partner verification. |
| C2-01 — scientifically compatible cooked result | P2, scientific evidence / Stage A authorization | Primary source evidence and pending RF decisions | Every compatibility gate has traceable evidence; cooked output can be independently reproduced. | Maintain 0 accepted until compatible source data and authorization exist. |
| C5-01 — independent exposure benchmark | P2, external scientific data/review | Suitable published reference data and defined comparability criteria | Independent script/data, prespecified metrics and reproducible discrepancy analysis. | Screen candidate sources; do not label descriptive raw contrasts as validation. |
| C4-01 — Phase 4 uncertainty context | P3, authenticated source/reviewer input | Verified evidence source and approved uncertainty method | New versioned package validates cleanly; bounds are source-backed and uncertainty is not invented. | Keep v0.1.2 blocked; only begin successor after valid evidence and owner release approval. |
| C6-02 — partner portability | P3, partner device | Windows startup plus browser checks on reviewed revision | Recorded actual startup, API and browser results on Windows; no claim based on instructions alone. | Partner follows `py -3 stageC/app/server.py --host 127.0.0.1 --port 8765` in a clean checkout. |

## I. Final classification

**IN PROGRESS.** Stage C has functioning raw-reference software, several locally verified immutable packages, documented scientific provenance and useful fail-closed behavior. It is not complete: the present API test suite has one failure tied to an unconfigured trusted identity provider; formal schema validation is unavailable on the current host; Phase4-v0.1.2 is unrecoverable/unverified; Phase 2 has zero accepted cooked estimates; independent exposure validation and Windows browser verification remain pending. No scientific or deployment claim is upgraded by this baseline.
