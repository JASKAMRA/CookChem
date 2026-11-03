# CookRisk Stage C

Stage C Phase 1 is the read-only integration, food-record validation, conservative mapping, Decimal unit conversion, raw-food calculation, and provenance foundation. The active connector verifies the exact manifest for `stageB/release/StageB_FINALIZED` before exposing its 143 compounds.

## Registry and preserved Phase 1B data

All 143 finalized Stage B compound IDs are available to Phase 1. The previous 119 IDs remain present; the 24 added IDs are imported without new food mappings. Registry names and chemical identifiers are compared with the Stage B identity audit. Pending identities and the catechin/epicatechin stereochemistry review remain visible.

The existing Phase 1B files remain unchanged: **511 quantitative food-composition records** and **511 mapping rows**. They contain 109 legacy mapped compounds, but Stage B currently marks 16 of those compounds for manual identity review; their 46 mapping rows are retained and blocked from exposure calculations. Current identity-complete quantitative coverage is **93 of 143 compounds**. The 24 newer compounds have no mappings, and 34 compounds have no legacy food mappings. Missing values remain missing.

Contextual botanical measurements remain separate from ordinary-food coverage. Values retain their source units and sample basis; the pipeline does not infer food density, fresh-weight equivalence, cooking retention, recipe dilution, bioavailability, or health risk.

## Validate and test

Run from the repository root with Python 3.14 or compatible Python 3:

```sh
python stageC/scripts/import_stage_b.py
python stageC/scripts/inspect_stage_b.py
python stageC/scripts/validate_phase1.py
pwsh -NoProfile -File stageC/scripts/validate_json_schemas.ps1
python -B -m unittest discover -s stageC/tests -v
```

This Stage C tree is part of the v1.3.0 package rooted one directory above. The prior Phase1B-v1.0.0 package remains a historical release in the source workspace and is not bundled here.
