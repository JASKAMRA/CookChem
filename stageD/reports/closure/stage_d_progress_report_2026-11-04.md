# CookRisk — Stage D Progress Report

**Report date:** 4 November 2026  
**Scope:** Stage D work completed and verified to date  
**Overall status:** **NOT COMPLETE — local engineering is substantially implemented; operational and scientific closure remain pending.**

## 1. What Stage D is doing

Stage D connects evidence about food compounds and experimental findings to a cautious review process. It preserves source records, checks whether a comparison is supportable, and routes uncertain evidence to human reviewers. It does not produce a clinical risk score or automatically approve evidence.

## 2. Work completed

### Evidence contracts and source traceability

- Added normalized evidence records that retain the original source labels and provenance while making study type, findings, and context easier to review.
- Added cross-stage comparison contracts that bind records by exact IDs and release hashes.
- Kept dietary exposure, experimental dose, and raw or cooked concentration separate. Missing amounts, mismatched provenance, and unsupported units or bases fail closed; no conversion or dose-equivalence claim is invented.

### Six-gate exposure comparability

The comparison checks cover compound identity, route, units and basis, time window, population or model, and preparation or sample matrix. Each gate returns a pass-pending-human-review, fail, or pending result with a reason. Passing the automated checks only makes a case ready for human review.

### Mechanism evidence and reviewer packets

- The Stage D mechanism registry contains **25 candidates linked to 7 study identifiers**.
- The registry and all 25 packet records passed the local source-pin and record-contract checks.
- Packets separate source text, machine-generated candidate labels, discrepancies, and empty reviewer fields. Packet generation does not approve a mechanism.

### Record-level evidence review

- The Stage D queue contains **317 evidence records** with stable review IDs, preserved source fields, machine-triage labels, and separate human-review state.
- The current reviewer register identifies **9 records with missing citation or context fields** and **63 records with conflict-group labels**.
- Review exports are protected against spreadsheet formula injection. Coverage and workload distinguish pending, in-progress, and terminal decisions.

### Review workflow and integrity

- Human actions are tied to queue records and constrained by explicit review-state transitions.
- Expert decisions require structured supporting and contradicting findings, source locators, limitations, and an exposure-comparability status.
- The durable assignment ledger supports signed append-only assignment and reassignment history, prevents duplicate active assignments, serializes concurrent writes, and reports integrity failures.
- Review and assignment audit chains can be checked locally. An external checkpoint adapter can anchor their heads; no external checkpoint service is configured.

### Interpretation framework

Stage D includes a nonclinical interpretation framework that keeps uncertainty visible and avoids numerical risk scores or patient-specific conclusions. It is a design and engineering foundation, not scientific or clinical approval.

## 3. Review materials

The versioned [human review register](/Users/ayushkamboj3/CookChem/stageD/reports/closure/human_review_register_v1.0.0.json) contains **342 pending items**: 317 evidence records and 25 mechanism candidates. It preserves source references and includes empty decision, rationale, and authorization fields. No human decisions were generated. Its SHA-256 is recorded in the adjacent `.sha256` file.

## 4. Phase-label note

Existing Stage D documents explicitly label a **Phase 4/5 mechanism tranche**, a **Phase 5 evidence queue**, a **Phase 6 interpretation framework**, and a **Phase 8 application-readiness report**. Because a Phase 8 document exists, the earlier statement that Stage D has only six phases is not supported by the repository evidence reviewed for this report. This report therefore summarizes verified work by workstream and cites only phase labels present in Stage D records; it does not infer completion of unverified phase numbers.

## 5. Validation performed

The safe Stage D test set ran **77 tests: 71 passed, 6 skipped, 0 failed**. Five tests were skipped because the approved `jsonschema` dependency was unavailable; one frozen-source integration test was not run. Skipped tests are not counted as passed.

Python syntax compilation passed, all 9 Stage D schema files parsed as JSON, the review register rebuilt byte-for-byte with its recorded checksum, and `git diff --check -- stageD` passed. JSON parsing does not count as formal Draft 2020-12 validation.

## 6. What remains

- Configure an approved identity provider, trusted issuer-bound keys, reviewer roster, expiry and revocation checks, key rotation, and deployment-owner approval.
- Configure an independently administered checkpoint service for both audit histories.
- Supply the approved `jsonschema` version pin and trusted package source, then run formal schema validation.
- Obtain qualified human review of all **317 evidence records** and **25 mechanism candidates**.
- Confirm the deployment storage supports the assignment ledger's locking and durability requirements.

Until those conditions are met, production review authorization remains blocked and Stage D remains open. See the [closure register](/Users/ayushkamboj3/CookChem/stageD/reports/closure/stage_d_closure_register_2026-11-04.md) for item-level statuses and exact prerequisites.

## 7. Scope boundaries observed

Stage A was not modified. Stage B and Stage C were not touched or tested. Stages E, F, and G were not modified. No GitHub or remote Git operations occurred.
