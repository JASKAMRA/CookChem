# Stage B final release status

- Release: `StageB_FINALIZED`
- Status: `FINALIZED_WITH_DOCUMENTED_SCIENTIFIC_LIMITATIONS`
- Selected source: `StageB_V19_20261103`, completed V19 batches 001–012
- Immutable baseline parent: `StageB_V18_20261103`
- Scope: 143 compounds, 317 evidence records, 133 drug/probe rows, 163 bibliography rows, 161 studies, and 317 source-audit dispositions.

## Selection and retained work

The older `StageB_Final` contains 119 compounds and 286 evidence rows. V18 contains the full 143-compound/317-evidence dataset but reports no independent V19 source-content rechecks. V19 preserves the same complete data scope, adds 53 individual primary-source reviews, 18 traceable warnings, supported data corrections, 12 completed review batches, and focused validators with passing tests. Its exact manifest and the immutable V18 parent manifest passed before consolidation. V19 was therefore selected as the best available source state.

All V19-001 through V19-012 changes are retained. No V19-013 or other partial research change was present or copied. V19's `NEXT_STEPS.md` was excluded because its open-ended research queue is superseded by this finalization directive. The V19 release and earlier releases are retained as read-only historical records; `StageB_FINALIZED` is the sole authoritative Stage B evidence deliverable.

## Final warning dispositions

The 88 warning IDs are retained without deletion. `data/warning_ledger.csv` adds the canonical `Final_Disposition` column and preserves the original `Audit_Status` field from the completed V19 audit. The only vocabulary mapping is `STILL_VALID` to `VALID`; warning meaning and evidence are unchanged.

- RESOLVED: 5
- PARTIALLY_RESOLVED: 15
- VALID: 26
- NEEDS_MANUAL_REVIEW: 40
- NOT_APPLICABLE: 2

Two inherited warning rows received warning-specific V19 rechecks; 68 were carried forward from V18/V17 without a new V19 recheck. Among new V19 warnings, W10 (metadata locators) and W14 (individual-compound evidence labels) were resolved with corrections and verification references. Open scientific uncertainties remain open. All 88 warning severities are `NOT_RECORDED`.

## Source and outcome scope

V19 independently reviewed 53 of 317 evidence records against primary sources: 40 full-text reviews (Tier 1) and 13 primary-abstract reviews (Tier 3). The other 264 retain historical dispositions and are not represented as new reviews. Of 90 originally blank quantitative outcomes, 29 source-supported values were recovered, 17 outcomes were dispositioned qualitatively, and 44 remain blank.

## Validation

Final structural, referential, warning, source-audit, regression, mutation, exact-manifest, and clean-copy results are recorded in `validation/final_release_validation.json` and `validation/final_validation_results.json`. The package remains technically reproducible while its scientific limitations stay visible.
