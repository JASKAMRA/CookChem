# V19 scientific-remediation handoff

## Stable checkpoint

The release is `StageB_V19_20261103`, parented to immutable `StageB_V18_20261103`, and remains `SCIENTIFIC_REMEDIATION_IN_PROGRESS`. V19 batches 001–012 are recorded and their focused validators pass. Do not repeat those source reviews unless resolving a new discrepancy.

At this checkpoint, 53/317 evidence records have a new V19 source-content review (40 Tier 1 full text; 13 Tier 3 primary abstracts); 264 records remain. Batch 011 reviewed SB-0003–SB-0005 against PMID 21870106 and repaired three residual cache paths. Batch 012 reviewed SB-0013 against primary abstracts, repaired its cache pointers and left its unspecified AUC interval open under V19-W18. Of 90 inherited blank quantitative outcomes, 29 are populated from source-supported numeric values, 17 have source-supported qualitative dispositions, and 44 remain blank. All 70 inherited warning IDs are preserved; only two received a new V19 warning-specific recheck. The exact record-level status and reasons are in `validation/V19_warning_audit.csv` and `data/warning_ledger.csv`.

## Resume queue

1. Reconstruct a remaining-evidence queue from `data/interaction_evidence.csv` joined to `provenance/source_audit.csv`. Exclude only records with an actual V19 source review; do not treat inherited tiers or carried-forward locators as new review.
2. Review the next batch of records against legitimate primary full text and supplements where available. Record the actual section/table/page and source tier. If only an abstract is accessible, retain Tier 3 and the abstract-level limitations. If no claim can be verified, record the attempted locators and leave the outcome unresolved.
3. Continue warning-specific review for the 68 inherited warnings still carried forward, prioritizing `NEEDS_MANUAL_REVIEW` and `PARTIALLY_RESOLVED` rows. Preserve each warning ID; correct underlying data before changing its lifecycle status.
4. Investigate the 44 remaining blank outcomes one record at a time. Distinguish “not reported,” “not accessible,” and “schema cannot represent source result.” Never infer a value or replace missing data with zero.
5. Continue the 143-compound identity audit, all populated numerical outcomes and experimental-design fields, the 163 bibliography and 161 study rows, duplicate/reference integrity, and possible cohort overlap. Preserve uncertainty where sources do not establish identity or overlap.
6. After each batch, run its focused validator and mutation tests, inspect the diff, update the progress report and release metadata, then rebuild the exact V19 manifest. Keep V18 read-only and do not access Stage A or Stage C.
7. Do not call V19 complete until all 317 records have individual source dispositions, warning and outcome workstreams have been addressed, and the final scientific and integrity checks support release completion. Otherwise retain the in-progress status and update this handoff with exact completed and remaining counts.

## Open V19 scientific warnings

- `V19-W01`: SB-0012 AUC unit and comparator-print ambiguity.
- `V19-W02`–`V19-W09`: source/model or reporting discrepancies retained for manual adjudication.
- `V19-W11`–`V19-W13`: source-level treatment-timing, CI-threshold, and cell-line-label discrepancies.
- `V19-W15`: shared apparent Ki range lacks individual-compound attribution and a recoverable denominator in the accessible abstract.
- `V19-W16`: SB-0137 thymol FICI 0.750 lies on overlapping classification boundaries; the paper’s table label is preserved.
- `V19-W17`: SB-0005 / PMID 21870106 Methods label losartan as CYP2C19, while abstract, Results and Table 1 label the ratio as CYP2C9; source adjudication remains open.
- `V19-W18`: SB-0013 / PMID 27981349 primary abstract omits the AUC sampling interval; full text or source clarification is required before assigning an interval.

`V19-W10` and `V19-W14` are resolved with corrections and verification references in the warning ledger. Do not close any open scientific warning without new source evidence and a passing regression check.
