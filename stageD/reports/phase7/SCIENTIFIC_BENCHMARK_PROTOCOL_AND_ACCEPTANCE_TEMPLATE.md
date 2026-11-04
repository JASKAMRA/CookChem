# Stage D Phase 7 — Scientific Benchmark Protocol and Acceptance Template

**Status:** PROTOCOL TEMPLATE ONLY — no cases selected, benchmark run, or independent review completed.  
**Roadmap basis:** Stage D Phase 7 requires validation using published interaction case studies, independent scientific review, and reproducibility testing.

## Governance gate before evaluation

A qualified scientific owner must approve this protocol version, inclusion/exclusion rules, case set, reference adjudication process, metrics, and acceptance thresholds before any system output is compared with reference decisions. Record the approval below. Do not choose thresholds after seeing results.

- Protocol version:
- Approving owner / role:
- Approval date and record:
- Independent reviewers and qualifications:
- Conflicts of interest declared:
- Locked case-set identifier and exact-byte digest:
- Software/release identifier and digest:
- Protocol deviations approved before analysis:

## Case selection protocol

Use published case studies that can be reviewed from authorized primary sources. Select cases before running the CookRisk interpretation workflow. Include examples that exercise the framework's documented evidence states (human/clinical, animal, in-vitro/mechanistic, positive, negative, null, mixed/conflicting, missing context, and unavailable or noncomparable dietary exposure) only where suitable sources exist. The panel sets and records the target count; no count or result is assumed here.

For each candidate case, preserve:

- Source citation and access level (full text, author manuscript, or abstract).
- Exact source page/table/figure locator and source file/reference digest.
- Study design, population/model, compound/drug identities as reported, route, dose/basis, timing, preparation/matrix, and outcome language.
- Contradictions, limitations, missing context, and why the case is eligible or excluded.
- Exact Stage C release/estimate reference when exposure is part of the case; if absent, label exposure unavailable and do not fabricate a comparison.

Exclude or separately classify cases with irrecoverable citation, identity, context, or provenance. Never infer the reference label from CookRisk output.

## Independent reference adjudication

1. At least two qualified reviewers independently classify each locked case using the approved Stage D categories and record source-located rationale, supporting/contradicting evidence, uncertainty, comparability, and limitations.
2. Reviewers must not see the software classification before their independent entries are locked, where blinding is operationally feasible. If not feasible, disclose the deviation and rationale.
3. Resolve disagreement through a named qualified adjudicator. Preserve both initial decisions and the adjudication trail; do not overwrite dissent.
4. Keep machine triage, software classification, expert adjudication, and scientific approval as separate fields.
5. Negative and null findings remain scoped to study conditions. The benchmark does not establish clinical risk or patient-level validity.

## Prespecified analysis plan (owner approval required)

Report counts of eligible, excluded, unresolved, and adjudicated cases by evidence category and reference state. Compare the software's categorical output with the locked adjudicated reference using:

- A complete confusion/count matrix, including unresolved and abstained outputs.
- Exact agreement and per-category agreement with denominators.
- Disagreement inventory with case references and reviewer rationale.
- Coverage/abstention rate, so withheld results are not hidden by scoring only resolved cases.
- Reproducibility check: same locked inputs, software version, and environment must produce byte-identical serialized outputs or documented deterministic equivalence under a predeclared rule.

Any additional statistic (for example chance-corrected agreement) and its interpretation must be approved before evaluation. No performance threshold is set by this template. The qualified owner must predeclare minimum acceptable agreement, coverage, and discrepancy resolution criteria before the run.

## Reproducibility record

Record exact commands, OS/build, Python and dependency lock, package hashes, source dataset/case-set digests, Stage C/Stage D release digests, random seeds (if applicable), output digest, and all deviations. Do not regenerate or overwrite historical source records or frozen releases. Synthetic tests validate software only and are not benchmark cases.

## Benchmark result and acceptance template

```text
Stage D Phase 7 benchmark acceptance record

Protocol version and approval reference:
Case-set ID and exact-byte SHA-256:
Number proposed / included / excluded / unresolved / adjudicated:
Inclusion/exclusion reasons and counts:
Independent reviewers and qualifications:
Blinding status and deviations:
Reference adjudication method:
Software/release ID and SHA-256:
Environment and dependency lock/hash:
Exact execution command(s):
Exact agreement result and denominator:
Per-category agreement counts and denominators:
Coverage/abstention counts and denominator:
Confusion/count matrix location and digest:
Disagreement inventory location and digest:
Reproducibility rerun command and exact result:
Prespecified thresholds approved before run:
Thresholds met / not met / not assessable:
Scientific limitations and unresolved cases:
Reviewer/adjudicator sign-off and dates:
Owner acceptance decision and evidence reference:
Status: NOT RUN / RUN, PENDING REVIEW / ACCEPTED / REJECTED
```

**Acceptance rule:** mark Phase 7 scientifically accepted only after the owner-approved protocol is executed on the locked published case set, independent adjudications are complete, results meet the preapproved thresholds, discrepancies and limitations are documented, and reproducibility evidence is reviewed. No result or approval is recorded in this template.
