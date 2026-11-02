# CookRisk Stage B — V17 final release

**Status:** FINAL — VERIFIED WITH DOCUMENTED SCIENTIFIC LIMITATIONS  
**Baseline:** `StageB_V16_20261102`  
**Approved scope:** 143 compounds and 317 interaction evidence records.

The seven V17 additions are Apigetrin, Myricitrin, Prunin, Quercitrin, Sunset Yellow FCF, S-equol and Phloridzin. The release contains 133 drug/probe rows, 163 bibliography rows, 161 study rows and 70 warning rows. No further expansion is authorized.

All 70 warning rows have a fresh V17 disposition in `validation/V17_warning_by_warning_audit.csv`. Historical warning dispositions remain traceable in the warning ledger. Warnings concerning source gaps, study attribution, exposure and unresolved expert review remain open. The 317-record evidence registry is structurally linked; source-audit coverage is incomplete and is documented under V11-W03.

In-vitro and animal findings remain distinct from human clinical interactions. S-equol numerical values remain attributed to the located dissertation because the journal full text was not accessible. The phloridzin animal rosuvastatin results belong to phloretin, not phloridzin.

## Release contents

- `data/` — compound, interaction evidence, probe, bibliography, study and warning tables.
- `identity/` — structure identity audit.
- `provenance/` — selection, source, claim-support and food-context records.
- `validation/V17_warning_by_warning_audit.csv` — current 70-row audit and dispositions.
- `validation/V17_warning_audit_status.json` — reconciled audit status and counts.
- `validation/final_validation_results.json` — structural/provenance validator results.
- `manifests/SHA256SUMS.json` — deterministic release manifest.

## Validation

Run `python -B scripts/validate_v17.py` and `python -B -m unittest tests.test_v17_integrity -v` from this directory. The Stage B root regression and independent clean-copy manifest verification are recorded in `release_metadata.json` and `validation/final_validation_results.json`.
