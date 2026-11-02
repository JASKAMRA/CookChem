# CookRisk Stage B — V16 continuation

**Status:** partial; not ready for the 160-compound target. **Baseline:** V15. **Current registry:** 136 compounds / 310 evidence records.

V16 is an isolated continuation copy. It preserves V15 data and historical warnings while extending the warning ledger with a row-level audit. The DOI for PMID 22512082 was verified from the primary publisher PDF and propagated to its linked bibliography, evidence, and study records. No new compound was admitted because the pending leads reviewed in this continuation did not meet the exact identity and primary evidence requirements.

## Key files

- `data/` — compound, evidence, bibliography, study, probe, and warning registries.
- `validation/V16_warning_audit.csv` — status and disposition for each inherited and new warning.
- `validation/V16_warning_audit_summary.json` — warning totals, categories, and severity-availability note.
- `validation/V16_pending_candidate_adjudication.csv` — decisions for the nine pending leads.
- `provenance/V16_metadata_correction_log.csv` — source and rationale for the PMID 22512082 DOI correction.
- `scripts/validate_v16_warnings.py` and `tests/test_v16_warning_audit.py` — warning-ledger lifecycle checks.
- `NEXT_STEPS.md` — resumable implementation checkpoint.

## Validation

From this directory, use Python 3:

```powershell
python scripts/validate_v16_warnings.py
python -m unittest tests.test_v16_warning_audit -v
python scripts/manifest_integrity.py verify . --mode exact
```

The Stage B regression ran with 44 passes and one test-harness failure: the root manifest enumeration detects a transient `.pyc` created by its dynamic import. V16-specific structural and warning checks pass. V16 exact manifest and clean-copy verification both pass at 744/744. Rebuild the manifest after any later edits. Read `RELEASE_STATUS.md` and `NEXT_STEPS.md` for all limitations and outstanding work.
