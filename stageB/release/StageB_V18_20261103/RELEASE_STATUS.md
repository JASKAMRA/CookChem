# Stage B V18 release status

- Release: `StageB_V18_20261103`
- Immutable parent: `StageB_V17_20261103`
- Scope retained: 143 compounds, 317 interaction evidence records, 70 warning rows.
- Status: successor with documented scientific and source-review limitations.

## V18 integrity corrections

1. Reconciled warning lifecycle status: the 70-row V17 warning-by-warning audit and V17 warning ledger contained inconsistent `Audit_Status` values. V18 uses the fresh per-warning audit disposition in `Audit_Status` and preserves each original V17 ledger value in `V17_Ledger_Audit_Status`. The reconciliation is recorded in `validation/V18_warning_disposition_reconciliation.csv`.
2. Reconciled source-audit coverage: V17 had 118 source-audit rows covering 107 unique evidence IDs (11 duplicate rows) and 210 evidence IDs without a separate source-audit row. V18 now has one explicit source-audit disposition per each of 317 evidence IDs; the 11 duplicate rows are traceably logged.

## Critical source-review limitation

V18 did not independently reopen and review all 317 original sources. For the 210 newly added audit dispositions, bibliographic/source locators and historical status were carried forward from the one-per-evidence V17 `claim_support_and_verification.csv` and evidence records. The records explicitly state that current source review is pending; their historical verification tier is not represented as a V18 independent review. This repairs coverage and traceability, not the scientific verification gap. The requested full-text/table review, quantitative re-extraction, chemical identity re-adjudication, and all manual warning reviews are not complete. No scientific outcomes or identities were altered.

## Warning status

All 70 inherited warning IDs remain present. Status reconciliation changes are listed with record-level rationale and source references. Scientific uncertainty and manual-review dispositions remain open.

## Validation

Manifest verification, structural checks, referential integrity, source-audit row coverage, unique warning IDs, status-to-audit alignment, and mutation tests are run against this release and recorded under `validation/`.

## Verification outcomes

The V18 structural validator passed 16/16 checks with zero errors; it still reports non-fatal data-quality warnings. The V18 integrity/mutation suite covers source-audit coverage, duplicate IDs, invalid verification tiers, warning status drift, and unsupported closure. Predecessor-specific V15/V16/V17 tests are retained under `tests/history/` and are not run against the successor because their assertions require the historical release to remain byte-for-byte unchanged. The current V18 suite targets V18.

An automated dataset sweep found no duplicate nonblank compound, evidence, PMID, DOI, or study keys, and no broken evidence-to-compound/drug/study or study-to-publication references. It found 90 blank quantitative-outcome fields; these remain blank. This sweep does not substitute for primary-source review or confirm that all scientific claims are correct.

V18 `Verification_Date` is blank where the historical verification date was not recorded. `Disposition_Date` records only the V18 bookkeeping date and must not be interpreted as a source review date.

## Final counts and remaining work

V18 warning disposition counts are 3 resolved, 14 partially resolved, 26 still valid, 25 needing manual review, and 2 not applicable. Ten V17 ledger statuses were inconsistent with the row-by-row V17 audit; V18 reconciles these to the audit, with original ledger values retained. V9-W01 closure was rechecked against all 14 registry/identity-audit records and their recorded PubChem API locators. V16-W01 was rechecked by exact read-only manifest verification. V3-W04's 12 affected PMIDs are present in the current bibliography.

The V18 source audit is complete as a **coverage/disposition index**, not as a primary literature review. No source content was independently reopened in this V18 run; all 210 added records remain explicitly pending. The 25 manual-review warnings, quantitative-value re-extraction, full identity adjudication, and broader source verification remain incomplete. Consequently V18 is a successor with remediation in progress, not a claim that the complete scientific remediation mission has passed.

Validation results: V18 structural validation 16/16 checks passed, zero errors, 108 non-fatal warnings; V18 integrity and mutation tests 10/10 passed; repository Stage B regression 46/46 passed; V16 exact manifest 744/744 passed; V17 exact manifest 765/765 passed. V18 exact manifest and clean-copy verification are recorded after final packaging.
