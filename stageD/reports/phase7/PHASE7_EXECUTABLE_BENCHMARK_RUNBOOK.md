# Stage D Phase 7 — Executable Scientific Benchmark Runbook

**Status:** Ready for owner completion; no scientific cases have been run. Thresholds and acceptance remain owner decisions.

## Inputs required before executing

1. Owner-approved protocol and approval record, including case inclusion/exclusion rules, case count, reference categories, minimum exact/per-category agreement, minimum coverage, discrepancy handling, and reproducibility rule.
2. Locked case-set JSON with exact-byte SHA-256. Every case needs a stable ID, validated Stage D interpretation input, and a blinded independent reference category entered before software results are exposed.
3. At least two qualified independent reviewers, their qualifications/conflicts, adjudication records, and a named adjudicator for disagreements.
4. Immutable Stage D implementation/release ID and digest, Stage C exposure release digest when exposure is used, Python/dependency lock and hashes, environment details, and approved result location.

Do not proceed until the owner has signed the protocol and the case set is locked. Synthetic fixtures are test fixtures, never scientific benchmark cases.

## Case-set shape

```json
{
  "schema_version": "1.0.0",
  "case_set_id": "OWNER-ASSIGNED-ID",
  "protocol_version": "OWNER-APPROVED-VERSION",
  "cases": [
    {
      "case_id": "STABLE-CASE-ID",
      "input": {"assessment_id": "STABLE-CASE-ID"},
      "reference_category": "OWNER-ADJUDICATED-CATEGORY",
      "independent_review_refs": ["REVIEW-1-RECORD", "REVIEW-2-RECORD"],
      "adjudication_reference": "owner-controlled adjudication locator"
    }
  ]
}
```

The production case must satisfy `stageD/schemas/risk_interpretation.schema.json` input contract and `stageD/src/stage_d/interpretation.py` validator. Supported output categories are `REQUIRES_EXPERT_REVIEW`, `INSUFFICIENT_EVIDENCE`, `MECHANISTIC_EVIDENCE_ONLY`, `EXPOSURE_COMPARABILITY_PENDING`, `RESEARCH_RELEVANCE_SUPPORTED`, and `EXPERIMENTAL_EVIDENCE`. Confirm category/version fields against the frozen implementation before locking the owner case set.

## Approval record

The approval file is owner-signed JSON with: `status=APPROVED`, `approver_identity`, `approver_role`, `approval_date`, `signature_reference`, `approval_reference`, `protocol_version`, `case_set_sha256`, `implementation_release_id`, `thresholds.minimum_exact_agreement`, `thresholds.minimum_coverage`, predeclared `thresholds.minimum_per_category_agreement`, and an explicit `abstention_categories` list. The runner checks these fields but does not cryptographically authenticate the owner; the approval reference must be independently confirmed before execution. The runner refuses absent approval, a case digest mismatch, missing thresholds, incomplete/duplicate independent-review references, or an empty case set.

## Reproduction procedure

From repository root, once the owner has supplied candidate cases and the approved Draft 2020-12 environment is active:

```sh
python3 --version
python3 -m pip freeze --all > benchmark-environment.txt
shasum -a 256 path/to/approved-case-set.json path/to/approval.json path/to/dependency-lock.txt
PYTHONDONTWRITEBYTECODE=1 python3 stageD/scripts/prepare_phase7_case_lock.py \
  --case-set path/to/candidate-case-set.json \
  --output path/to/controlled-lock/case-set-lock-candidate.json
shasum -a 256 path/to/candidate-case-set.json path/to/controlled-lock/case-set-lock-candidate.json
PYTHONDONTWRITEBYTECODE=1 python3 stageD/scripts/run_phase7_benchmark.py \
  --case-set path/to/approved-case-set.json \
  --approval path/to/approval.json \
  --output path/to/controlled-results/phase7-results.json
shasum -a 256 path/to/controlled-results/phase7-results.json
PYTHONDONTWRITEBYTECODE=1 python3 stageD/scripts/run_phase7_benchmark.py \
  --case-set path/to/approved-case-set.json \
  --approval path/to/approval.json \
  --output path/to/controlled-results/phase7-results-rerun.json
cmp path/to/controlled-results/phase7-results.json path/to/controlled-results/phase7-results-rerun.json
```

The first script creates only a `CANDIDATE_NOT_APPROVED` exact-byte manifest. The owner must inspect and approve case IDs, source locators, independent review/adjudication references, protocol version, thresholds, and the case-set SHA-256 before creating the `APPROVED` file consumed by the runner. Formal schema validation must return `VALID`; if the approved validator is unavailable, locking/benchmark preparation stops without creating an approved manifest or result.

Store exact stdout/stderr, runtime and platform, package lock/hash, case/approval hashes, source access/locator manifest, result hash, rerun comparison, deviations, and the independent reviewers' locked records. The runner reports confusion counts, exact and per-category agreement with denominators, unresolved/abstained output, coverage, and whether owner thresholds are met. It does not create an approval decision.

## Results and acceptance

Record included/excluded/unresolved case counts; class denominators; confusion matrix; exact/per-class agreement; coverage and abstention; disagreements and adjudication; reproducibility comparison; threshold outcome; owner acceptance; and limitations. Mark scientific acceptance only after the complete protocol acceptance rule in `SCIENTIFIC_BENCHMARK_PROTOCOL_AND_ACCEPTANCE_TEMPLATE.md` is satisfied and signed.
