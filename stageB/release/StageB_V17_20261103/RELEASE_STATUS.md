# Stage B V17 final release status

**Release:** `StageB_V17_20261103`  
**Baseline:** `StageB_V16_20261102`  
**Status:** FINAL — VERIFIED WITH DOCUMENTED SCIENTIFIC LIMITATIONS

## Approved dataset

- 143 compounds, including seven V17 additions; 317 interaction evidence records.
- 133 drug/probe rows, 163 bibliography rows, 161 study rows, and 70 warning rows (66 inherited plus four V17).
- The approved final scope is frozen at 143. No successor release was created.

## Warning audit

All 70 warnings have an individual V17 disposition in `validation/V17_warning_by_warning_audit.csv`: 3 resolved, 14 partially resolved, 26 still valid, 25 requiring manual review, and 2 not applicable to the approved current scope. Inherited `Audit_Status` values remain unchanged for historical traceability; fresh V17 results are stored separately. Severity remains `NOT_RECORDED`.

Three technical issues were verified as resolved: the historical Crossref metadata lookup warning (V3-W04), missing V9 structure fields (V9-W01), and the V15 metadata/manifest count discrepancy corrected in V16 (V16-W01). Twenty V14/V15 evidence claims gained source-located claim-support and source-audit rows. V11-W03 remains partially resolved because 210 of 317 evidence records still lack a separate source-audit row; no full-text re-extraction is claimed for those rows.

## Scientific limitations

- S-equol’s quantitative inhibition values are sourced to the located dissertation; journal full-text verification remains outstanding (V17-W03). Its production is microbiome-dependent.
- Phloridzin’s study reports in-vitro OATP2B1 inhibition; the rat rosuvastatin experiment in that paper tested phloretin aglycone (V17-W04).
- The 70-row warning audit reconciles each warning against current V17 records, source locators and validation. It does not claim that all 317 scientific outcomes were independently re-extracted from full text. Source gaps, unresolved stereochemistry, study overlap and historical provenance limitations remain explicitly open.
- No in-vitro or animal finding is treated as a confirmed human food–drug interaction.

## Validation

- V17 focused tests: 15/15 passed.
- Stage B root regression: 46/46 passed after finalization edits.
- Structural/provenance validation: PASS with documented warnings; zero structural errors.
- Warning report: 70/70 reconciled; all five status categories validated.
- Exact manifest and independent clean-copy verification: 765/765 files passed.

See `validation/V17_warning_by_warning_audit.csv`, `validation/V17_warning_audit_status.json`, `validation/final_validation_results.json`, and `release_metadata.json` for record-level details.
