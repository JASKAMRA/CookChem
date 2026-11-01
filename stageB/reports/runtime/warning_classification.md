# Classification of the 313 validator warnings

These are the row-level warnings emitted by the StageB_Final validator and stored in `stageB/validation/final_validation_results.json`. They are separate from the 55-row release warning ledger, which remains unchanged. No warning was closed or removed. Full per-record ID, code, related record, source, significance, Stage C impact, recommendation, and class are in [`warning_classification.csv`](warning_classification.csv). The validator emits no formal `Warning_ID`; that column is blank and `Audit_Row` is only a report row number.

| Classification | Count |
|---|---:|
| Critical | 0 |
| High | 13 |
| Medium | 300 |
| Low | 0 |
| Informational | 0 |
| Not Applicable | 0 |

## Counts by validator code

| Code | Count | Classification |
|---|---:|---|
| `NUMERIC_UNIT_REVIEW` | 13 | High |
| `OUTCOME_MISSING` | 90 | Medium |
| `SOURCE_AUDIT_MISSING` | 210 | Medium |

## Interpretation

- **210 `SOURCE_AUDIT_MISSING` (MEDIUM):** no separate source-audit row is present for the evidence record. Claim-support rows exist, but independent field-level source review is incomplete. Carry the warning; do not state that the claim has independent source verification.
- **90 `OUTCOME_MISSING` (MEDIUM):** quantitative outcome is blank. Do not coerce to zero or infer a number.
- **13 `NUMERIC_UNIT_REVIEW` (HIGH):** outcome text contains a number but the validator heuristic did not identify a supported unit or statistic. Manually inspect the cited source, analyte, unit, and context before numeric use. These are interaction outcomes, not food-concentration records.

These severity classes apply to downstream handling of affected records; they do not make every Stage B field unusable.
