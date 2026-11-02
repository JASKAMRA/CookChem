# Stage B V19 release status

- Release: `StageB_V19_20261103`
- Immutable parent: `StageB_V18_20261103`
- Status: `SCIENTIFIC_REMEDIATION_IN_PROGRESS`
- Scope: 143 compounds, 317 evidence records, 133 drug/probe rows, 163 bibliography rows, 161 study rows, and 88 warning rows.
- Completed scientific-review batches: V19-001 through V19-012.

## Scientific work completed

V19 has individually reviewed 53 of 317 evidence records against primary sources: 40 at Tier 1 (full text) and 13 at Tier 3 (primary abstract). The other 264 records have not received a new V19 source-content review. Inherited audit rows remain explicit dispositions, not evidence of new review.

Batch 011 re-extracted PMID 21870106 Methods, study flow and Table 1 for SB-0003–SB-0005. It added exact probe doses, participant flow, units, geometric mean ratios, confidence intervals and significance markers; retained the abstract/Table 1 midazolam Tmax/t1/2 discrepancy while transcribing the table labels; repaired three residual metadata-cache pointers under V19-W10; and opened V19-W17 for the source's inconsistent CYP2C19/CYP2C9 label for the losartan probe.

Batch 012 reviewed the primary PubMed and publisher abstracts for SB-0013 (PMID 27981349). It clarified the reported control and treatment values, doses and sequential design, repaired the metadata pointers under V19-W10, and opened V19-W18 because the accessible abstract does not specify the AUC interval. No interval or missing statistic was inferred; the publisher identifies full text as subscription content.

Of the 90 quantitative-outcome fields blank in V18, 29 now contain source-supported numerical results, 17 have source-supported qualitative dispositions, and 44 remain blank pending individual source review. Batches 011 and 012 expanded already populated outcomes and did not fill original blanks by inference.

All 70 inherited warning IDs are preserved. V19 adds V19-W01 through V19-W18. Current dispositions are 5 RESOLVED, 15 PARTIALLY_RESOLVED, 26 STILL_VALID, 40 NEEDS_MANUAL_REVIEW, and 2 NOT_APPLICABLE. Only two inherited warnings received new V19 warning-specific rechecks: V3-W04 (partial source recheck; historical resolved status retained) and V5-source_reporting_units (changed from STILL_VALID to PARTIALLY_RESOLVED after source-supported recovery for one component). The other 68 inherited warnings remain historical carry-forwards, not newly source-verified.

Among V19-added warnings, V19-W10 (metadata-cache pointers) and V19-W14 (individual-compound evidence-category labels) are resolved with underlying corrections and verification references. V19-W01, V19-W02–W09, V19-W11–W13, and V19-W15–W18 remain open as specified in the warning ledger. Severity was not recorded in the inherited schema; all 88 rows remain `NOT_RECORDED` rather than having invented severity values.

## Validation state

Focused validators for V19 batches 001–012 pass. The combined V19 batch tests, Stage B regression tests, structural checks, and exact-manifest results are recorded in `validation/V19_final_release_checks.json`. V18 remains read-only and its exact manifest is preserved. V19 is not scientifically complete: 264 evidence records, 68 inherited warnings, 44 original blank quantitative outcomes, compound-identity adjudication, full numerical/design review, publication and cohort-overlap review, and other unresolved scientific work remain. See `NEXT_STEPS.md` for the resumable queue and completion gates.
