# Stage D Phase 5 — Stage B evidence review queue

**Status: IN_PROGRESS — reproducible machine triage and reviewer queue prepared; no human source review or expert adjudication performed.**

## Scope and source integrity

The queue is built from the read-only source `stageB/release/StageB_V20_20261103/data/interaction_evidence.csv`. Its SHA-256 is pinned to `358665c339e0ab673bb846d16d30e75dbed2b9587ae4df91baddfb5493a3b8e6`. The builder refuses a different digest, row count, missing identifier, or duplicate `Evidence_ID`. Every source row is retained in the new derived JSON queue with its original CSV fields, Evidence_ID, Compound_ID, release, hash, and row number. Stage B itself was not edited.

## Queue and review states

`stageD/data/evidence_review_queue.json` is a deterministic, 317-record work queue. `stageD/src/stage_d/evidence_queue.py` rebuilds it from the pinned CSV and validates referential, status, and statistics invariants. Its schema is `stageD/schemas/evidence_review_queue.schema.json`.

Each record separates:

- `source_record`: the original CSV string values, preserved as supplied.
- `machine_assessment`: conservative routing labels, normalized category and polarity, explicit source conflict group, and missing-field list. `source_verification` is always `NOT_PERFORMED`.
- `human_review`: `NOT_REVIEWED` plus empty reviewer, date, rationale, and citation fields. No expert decisions or negative-evidence conclusions were generated.

Machine routing uses only explicit source conflict groups, the exact source identity label `verified_exact`, and presence of a declared set of source/context fields. `READY_FOR_EXPERT_REVIEW` means those fields are present and no explicit conflict or non-exact identity label triggered a queue; it does not mean the source was verified or the record was accepted. Group IDs use exact source text/labels and are review aids, not canonical compound/drug/target identity decisions. Opposite findings are not programmatically inferred as conflicts.

## Coverage snapshot

| Inventory | Count |
|---|---:|
| Source records preserved | 317 |
| Unique Evidence_ID values | 317 |
| Machine triage: CONFLICT_REVIEW | 63 |
| Machine triage: IDENTITY_PENDING | 199 |
| Machine triage: READY_FOR_EXPERT_REVIEW | 55 |
| Human state: NOT_REVIEWED | 317 |
| Source-verified / expert accepted / expert rejected | 0 / 0 / 0 |
| Explicit conflict records / groups | 63 / 45 |
| Exact duplicate candidates | 0 groups / 0 rows |
| Missing fields in the defined core source/context list | 0 |

Finding labels from the existing deterministic normalization contract: **182 positive, 8 negative, 13 null, 63 conflicting, 51 unclear**. These are preserved source-text classifications for triage; they are not a quality score or a new scientific decision. The source contains 5 normalized study categories: 70 human pharmacokinetic, 4 controlled clinical, 52 animal, 190 in vitro, and 1 other human clinical record.

The grouping index contains 5 source evidence-category groups, 143 Stage B Compound_ID groups, 133 exact drug-name groups, 162 exact source-and-study groups, 161 Study_ID groups, 195 exact source-reported target/context text groups, and 45 explicit conflict groups. There were no exact duplicates when comparing all source fields other than Evidence_ID. This exact check cannot rule out semantic duplicates that use different wording or metadata.

## Verification

Focused tests: `python -m unittest stageD.tests.test_evidence_queue -v` — **7 passed, 0 failed, 1 skipped**. The skipped test is the optional Draft 2020-12 validator check because `jsonschema` is not installed in the current environment; schema JSON parsing, queue invariants, source/hash pinning, full record preservation, group references, human/machine state separation, null/conflict protection, and mutation rejection all passed. No source-level scientific review, expert acceptance, or primary-source verification was performed by this queue build.

To rebuild from the pinned source at the repository root in PowerShell:

```powershell
$env:PYTHONPATH = "stageD/src"
python -m stage_d.evidence_queue
```

## Limitations and next review actions

The queue is a handoff tool and corpus inventory, not an evidence appraisal. Reviewers still need to check the primary article and exact locator, compound and drug identity, study context, endpoint semantics, source conflicts, negative/null findings, and the relevance of each reported preparation. The machine grouping keys do not infer targets or resolve semantic duplicates. Reviewer name, date, rationale, and cited source location must be recorded before any reviewed state is assigned. Machine triage and passing software checks do not establish source validity or scientific conclusions.

## Execution Cycle 5 — record-level workflow foundation

The additive queue schema is now **1.1.0**. Every row has a stable opaque `review_id` derived from the pinned Stage B SHA-256 and its Evidence_ID. IDs are stable for this exact source version and change if the pinned source changes. The generated queue remains a deterministic snapshot: all **317 human states remain `NOT_REVIEWED`**, and the audit action log is not seeded with synthetic or assumed decisions.

`stageD/src/stage_d/evidence_review_workflow.py` provides filters for compound, drug, study/title/DOI/PMID, evidence category, outcome-polarity source-text label, conflict status/group, source identity label, source verification, and current review status. Query filters are string matching against preserved labels; they do not adjudicate identities or scientific findings.

Reviewer actions are stored separately from the source queue as append-only JSON Lines. Every action requires a stable review ID, Evidence_ID, reviewer name/role, ISO review date, exact source locator, rationale, and an explicit resulting state. A SHA-256 hash chain detects event edits, reordering, truncation, duplicate IDs, broken record links, and invalid state transitions. Expert acceptance/rejection requires an explicit prior `READY_FOR_EXPERT_REVIEW` event and `reviewer_role=expert`. No UI action or queue build creates review events. Expert states are terminal in this initial workflow; no correction/reopen policy has been configured. The log is a local single-writer foundation, not a multi-user database.

Assignment exports include source-pinned references, source labels, machine triage, and current reviewer state. JSON and CSV exports are available; exporting or assigning work does not count as review. The coverage dashboard separately reports machine counts, reviewer states, source verification, and review coverage, with automatic approval and automatic negative inference hard-fixed at zero. Current assignment/coverage data remain unchanged until a human action is explicitly appended.

### Current coverage dashboard

See [`evidence_review_coverage_dashboard.json`](../../data/phase5/evidence_review_coverage_dashboard.json) and its contract [`evidence_review_coverage.schema.json`](../../schemas/evidence_review_coverage.schema.json). The unassigned 317-row work package is [`evidence_review_assignment_unassigned.json`](../../data/phase5/evidence_review_assignment_unassigned.json). The dashboard currently reports 317/317 NOT_REVIEWED, 0 source-verified, 0 expert-accepted, 0 expert-rejected, 0% review coverage, and zero automatic approvals or negative inferences.

### Filtered export examples

From the repository root in PowerShell:

```powershell
$env:PYTHONPATH = "stageD/src"
python -m stage_d.evidence_review_workflow --conflict-status CONFLICT --json-output stageD/data/phase5/conflict_assignment.json --csv-output stageD/data/phase5/conflict_assignment.csv
python -m stage_d.evidence_review_workflow --compound MOL-E8216E9AF4FCDA58 --human-review-status NOT_REVIEWED --json-output stageD/data/phase5/compound_assignment.json
python -m stage_d.evidence_review_workflow --coverage-output stageD/data/phase5/evidence_review_coverage_dashboard.json
```

The machine-readable reviewer event contract is [`evidence_review_action.schema.json`](../../schemas/evidence_review_action.schema.json); assignment exports use [`evidence_review_assignment.schema.json`](../../schemas/evidence_review_assignment.schema.json). Human decisions remain absent from the tracked data until supplied by reviewers.

### Cycle 5 focused tests

- Queue integrity and stable IDs: **8 passed, 0 failed, 0 skipped** with the pinned Draft 2020-12 validator.
- Workflow filters, exports, action lifecycle, hash-chain tampering/truncation, human-only approval/negative assessment: **9 passed, 0 failed, 0 skipped** with the pinned validator.
- Combined focused review workflow: **19 passed, 0 failed, 0 skipped**. No human source review was performed by these tests.
