# CookRisk Stage C — Phase 1B V20 successor

This package validates against `stageB/release/StageB_V20_20261103`, an identity-adjudicated registry with 143 compounds: 130 identity-complete and 13 identity-pending. The accepted quantitative ordinary-food dataset has 570 records/mappings and covers 115 unique identity-complete compounds.

The 120 approximate target is five compounds short, and the 130 minimum is fifteen short. Identity-only resolution does not count as quantitative food coverage. Held, spiked, context-only and non-retrievable values are excluded. Stage A is outside this release.

Run `python3 scripts/validate_phase1.py` from the package root to revalidate the Phase 1 connector and data. The Phase 1B closeout is in `reports/phase1b/PHASE1B_CLOSEOUT_2026-11-03.md`.
