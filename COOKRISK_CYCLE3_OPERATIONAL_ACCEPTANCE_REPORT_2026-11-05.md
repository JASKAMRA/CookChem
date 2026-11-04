# CookRisk — Cycle 3 Operational Acceptance Report

**Date:** 2026-11-05  
**Status:** Stage C and Stage D remain **INCOMPLETE**. No operational or scientific acceptance is claimed.

## Actual work completed

### Stage D review workflow

- The Stage D register and generated worklists were validated structurally from Stage D artifacts. The v1.1.0-to-v1.2.0 mapping contains **342 unique stable review IDs: 317 evidence records and 25 mechanism candidates**. Required source/release identifiers, source locators, 64-character source digests and schema mappings are present; all records remain pending. A fresh validation/build to a temporary directory reported 342 pending, 0 assigned and 0 decisions. v1.1.0 SHA-256: `825813103669585f36fe7aabb54d74869deafd09fdcb4dfe18d63176ec8d5723`; v1.2.0 SHA-256: `9953d65d8733d45cf3efa9d62c08c8bb6579eb16c07051f504bc74ae46f603bb`.
- This is **index/reference-shape verification only**. The register points to protected Stage B-derived source material. Because Stage B is inaccessible by instruction, none of the 342 source documents, source hashes, or scientific identities were cross-checked against those protected originals. That requires the authorized custodian/reviewer in the controlled environment.
- Hardened review-event verification: audit sequence values must be real integers (not booleans), event IDs/statuses must be well-typed, dates must be valid ISO dates, qualifications must be verified attestations for the correct review type, and final sign-off must be a nonempty string. The API rejects malformed sign-off values before writing. Added a synthetic case showing that even a correctly signed/hash-chained event is rejected when its review date is malformed.
- Added a practical onboarding and decision-return procedure to the existing reviewer guide. Real decisions must enter through the authenticated provider workflow. Offline packets, edited CSVs, unsigned JSON and self-asserted sign-offs do not change review status.
- No bulk import pathway was added: the official Stage D roadmap and closure register reviewed for this cycle do not register a bulk-import task or acceptance contract. Existing provider-signed events can be verified by the approved workflow, but an external package is not imported into a production ledger by this code.

### Stage D live-service readiness

- Reused the provider and checkpoint interfaces, bounded retry implementation and owner provisioning checklist from Cycle 2. Synthetic tests continue to exercise assignment authorization, qualification checks, fail-closed submission, retry/recovery, and audit integrity.
- No identity provider, trusted reviewer roster, credentials, independent checkpoint service, endpoint, or external receipt is provisioned. Live authentication and checkpoint operation remain unverified.

### Stage D Phase 7

- Hardened case-lock and runner input parsing against duplicate JSON keys, non-standard JSON constants, malformed UTF-8, duplicate case IDs, non-string categories and malformed reference structures. Invalid/unavailable formal schema validation still fails closed.
- Benchmark results now record the exact-byte SHA-256 of the approval file as well as the case set, runner, interpretation module, schema and dependency lock. The runner requires valid exact-byte case-set, approval and dependency-lock digests. Synthetic tests verify determinism and rejection behavior; they do not represent scientific results.
- No case set or thresholds were approved; no scientific benchmark was executed.

### Stage C C1B-02 and later phases

- The 46-file candidate manifest was rechecked read-only: SHA-256 remains `c2e809c8bbda167c0fd20c7b99d86fb9c22331427d7ccb5c16771c33937b805b`.
- Existing owner and partner procedures already specify exact-byte checks, runtime prerequisites, API/browser checks, degraded Phase 4 behavior and result-return fields. They remain unchanged. No archive, current owner-designated revision or partner Windows/browser result is available. **C1B-02 remains blocked under its original acceptance criteria.** Later Stage C tasks remain behind this sequence gate; no later phase was started.

## Tests and validation

Exact focused command:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest stageD.tests.test_phase7_benchmark_runner stageD.tests.test_phase7_case_lock stageD.tests.test_review_operations stageD.tests.test_reviewer_worklists stageD.tests.test_checkpoint_retry stageD.tests.test_review_authorization stageD.tests.test_validation_status -v
```

Result: **36 tests run, 35 passed, 0 failed, 1 skipped.** The skipped formal-schema test reports `jsonschema is not installed; formal fixture check unavailable`.

Register/worklist validation command:

```text
PYTHONDONTWRITEBYTECODE=1 python3 stageD/scripts/build_reviewer_worklists.py --output-dir /private/tmp/cookrisk-cycle3-verified-worklists
```

Result: 317 evidence + 25 mechanism; 342 pending; 0 assigned; 0 decisions. This wrote only temporary test worklists.

Environment check: `python3 --version` returned **Python 3.14.7**; `python3 -m pip show jsonschema` reported the package not found. No `python3.12` or `uv` executable and no Stage D virtual environment were found in the scoped checks. Stage D declares no approved `jsonschema` version/lock and trusted package artifacts; no install was attempted. JSON parsing is not formal Draft 2020-12 validation.

## Files changed this cycle

- `stageD/src/stage_d/review_operations.py`
- `stageD/tests/test_review_operations.py`
- `stageD/reports/closure/REVIEWER_ONBOARDING_AND_QUALIFICATION_GUIDE.md`
- `stageD/scripts/prepare_phase7_case_lock.py`
- `stageD/tests/test_phase7_case_lock.py`
- `stageD/scripts/run_phase7_benchmark.py`
- `stageD/tests/test_phase7_benchmark_runner.py`
- `COOKRISK_CYCLE3_OPERATIONAL_ACCEPTANCE_REPORT_2026-11-05.md` (this report)

No Stage C files were changed. No Stage A, Stage B, scientific source, or Stage D readiness-register contents were modified.

## Remaining acceptance gaps and required external actions

### Owner / security / IT

1. Approve the reviewer qualification policy and trusted identity-provider configuration; provision issuer-bound keys, verified roster/roles, qualification attestations, expiry/revocation, deployment owner and secrets management.
2. Provision an independently administered checkpoint service, configure its adapter, trust/retention policy and credentials, and return externally verifiable publish/verify, tamper, outage and recovery evidence.
3. Approve an exact Stage D schema-validation environment: Python support range, `jsonschema` and format dependencies, complete transitive pins, trusted package source/wheel hashes, and applicable license record. Then run formal Draft 2020-12 schema tests. No Stage D dependency installation was authorized by the available pin/provenance evidence.
4. For C1B-02, approve the exact existing 46-file manifest contents/exclusions, name an authorized archive creator, separately provision all required runtime inputs, designate the current immutable revision or owner-created archive and record its exact-byte digest. The manifest hash above identifies the manifest, not an archive.

### Qualified scientific reviewers / owner

1. Verify reviewer identities, qualifications and conflicts in the owner-controlled roster; make genuine assignments through the authenticated service.
2. Review the protected source records in the authorized controlled environment, return source-located rationale, uncertainty, decision and sign-off for the 317 evidence records and 25 mechanism candidates, and preserve supporting and contradictory evidence. Stage B-derived source material must not be provided to this workspace.
3. Resolve or confirm the five DOI and four PMID metadata gaps from authorized primary records; none was inferred here.
4. Approve the Phase 7 case set, inclusion rules, adjudication references, protocol, thresholds and implementation release before any benchmark run. Qualified independent reviewers must supply locked case judgments; results must then be independently reviewed.

### Authorized partner

After owner approval and provisioning, execute the existing Windows/PowerShell handoff against the designated current archive and runtime inputs. Return exact archive/manifest/dependency hash outputs, OS/PowerShell/Python/browser versions, startup console, health response, browser observations, degraded Phase 4 behavior, and the completed result template. No partner result exists yet.

## Preservation statement

Stage A was untouched. Stage B was not accessed. The accepted 117 Phase 2 observations, frozen releases, historical evidence, scientific datasets and C1B-02 manifest were preserved. No approval, reviewer decision, partner result, live integration or scientific benchmark is claimed. No Git or remote operation was performed.
