# CookRisk Stage B — V13 versioned release

**Versioned release:** StageB_V13_20261102 (partial expansion; not a replacement for StageB_Final).

This release preserves the 119-compound StageB_Final snapshot and adds four primary-source-reviewed anchors, for 123 unique Compound_IDs and 290 interaction-evidence records. It retains 127 drug/probe labels, 153 bibliography rows, 153 study rows, and 57 warning-ledger rows. Batches 2–5 remain unexecuted; the target of 160 is not met. See `RELEASE_STATUS.md` and `documentation/V13_CANDIDATE_REVIEW.md`. No Stage C exposure integration or clinical food–drug inference is included.

## Structure

- `data/` — canonical registries, evidence, bibliography, warning ledger, and cooking-retention table.
- `provenance/` — selection decisions, candidate screening, source audit, claim support, and source register.
- `identity/` — chemical identity/structure audit.
- `validation/` — final audit reports, machine-readable tests, mutation results, and inherited audit outputs.
- `documentation/` — handoff, data dictionary, integration interface, and relevant historical handoffs.
- `scripts/` — portable final validation and mutation-testing scripts.
- `history/` — version lineage, V2–V12 reconciliation and adjacent-version changes, V12 file disposition map, and unique historical/support artifacts.
- `manifests/` — SHA-256 file manifest.

## Validate, test, and reproduce

Use Python 3 with only its standard library:

```powershell
python scripts/validate_final.py .
python scripts/mutation_test_final.py .
python scripts/manifest_integrity.py verify . --mode canonical
python scripts/mutation_test_final.py .
```

To rebuild into a new sibling directory, run from `Documents/CookChem/stageB/`:

```powershell
python StageB_Final/scripts/consolidate_final.py release_v12_20261030 StageB_Final_Rebuilt
```

The destination must be new or empty. The build runs a clean-copy comparison and creates its own checksum manifest.

The validator checks structure and relationships; it does not certify scientific truth. See `documentation/FINAL_HANDOFF.md` and `validation/manual_review_status.csv` for unresolved work. Original V2–V12 releases remain preserved beside this release under `Documents/CookChem/stageB/`; V12 remains unchanged.
