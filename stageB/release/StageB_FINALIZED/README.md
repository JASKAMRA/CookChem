# CookRisk Stage B — finalized release

**Authoritative deliverable:** `StageB_FINALIZED`.

**Release status:** `FINALIZED_WITH_DOCUMENTED_SCIENTIFIC_LIMITATIONS`.

This self-contained package consolidates the strongest validated Stage B evidence state: the 143-compound V18 baseline plus supported corrections from V19 batches 001–012. It contains 143 compounds, 317 interaction-evidence records, 133 drug/probe rows, 163 bibliography rows, 161 study rows, 317 source-audit dispositions, and 88 traceable warnings.

## Package contents

- `data/` — compound, drug/probe, interaction, bibliography, study, warning, and cooking-retention tables.
- `provenance/` — per-record source audit, claim support, publication-selection decisions, and archived metadata snapshots.
- `identity/` — chemical structure audit.
- `documentation/` — schemas, data dictionary, lineage, and scientific-use limitations.
- `scripts/` and `tests/` — structural, provenance, regression, and mutation validation.
- `validation/` — completed batch review records and finalization validation results.
- `manifests/SHA256SUMS.json` — exact-byte release manifest.

## Validate

From this directory, using Python 3:

```powershell
python scripts/validate_final.py .
python scripts/validate_stageb_finalized.py .
python scripts/mutation_test_final.py .
python -m unittest discover -s tests
```

The Stage B integration regression suite is run from the repository's `stageB/tests` directory. Exact manifest verification:

```powershell
python scripts/manifest_integrity.py verify . --mode exact
```

## Scientific scope and limitations

V19 batches 001–012 newly reviewed 53 of 317 evidence records against primary sources: 40 at Tier 1 full text and 13 at Tier 3 primary abstracts. The remaining 264 records retain explicit historical dispositions but were not newly source-reviewed in V19. Of 90 originally blank quantitative outcomes, 29 source-supported numeric values were recovered, 17 were dispositioned as qualitative, and 44 remain blank.

All 70 inherited warnings are preserved; 18 V19 warnings were added. Only two inherited warnings received warning-specific V19 rechecks. The final canonical warning disposition uses `Final_Disposition`; the historical `Audit_Status` values and `V19_warning_audit.csv` remain intact for traceability. Current counts are 5 RESOLVED, 15 PARTIALLY_RESOLVED, 26 VALID, 40 NEEDS_MANUAL_REVIEW, and 2 NOT_APPLICABLE. Severity was not recorded for the 88 warnings and has not been inferred.

The package is a literature evidence resource, not patient-specific clinical decision support. In-vitro, animal, abstract-only, and supplement-limited findings are clearly qualified. Technical finalization does not certify exhaustive scientific verification.
