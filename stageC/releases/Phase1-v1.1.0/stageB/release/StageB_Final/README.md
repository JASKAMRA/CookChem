# CookRisk Stage B — authoritative final release

**Authoritative release:** this directory (`StageB_Final`).

This is the consolidated Stage B literature-evidence package, based on the immutable V12 release. It contains 119 compound anchors, 286 interaction-evidence rows, 127 probe labels, 151 PMID publications, 148 distinct nonblank DOIs, and 55 warning-ledger rows. Evidence classes: Animal: 51, Controlled clinical: 4, Human pharmacokinetic: 70, In vitro: 160, Other human clinical: 1. The final audit also flags 210 missing source-audit rows, 90 blank quantitative-outcome fields, and 13 numeric/unit review items.

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
```

To rebuild into a new sibling directory, run from `Documents/CookChem/stageB/`:

```powershell
python StageB_Final/scripts/consolidate_final.py release_v12_20261030 StageB_Final_Rebuilt
```

The destination must be new or empty. The build runs a clean-copy comparison and creates its own checksum manifest.

The validator checks structure and relationships; it does not certify scientific truth. See `documentation/FINAL_HANDOFF.md` and `validation/manual_review_status.csv` for unresolved work. Original V2–V12 releases remain preserved beside this release under `Documents/CookChem/stageB/`; V12 remains unchanged.
