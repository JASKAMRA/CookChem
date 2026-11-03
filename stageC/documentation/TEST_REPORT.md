# Stage C Phase 1 software-foundation verification

## Updated repository results

- Full Stage C `unittest` suite: **72 passed, 0 failed**.
- Phase 1 validation: **PASS** against `StageB_FINALIZED`; 143 compounds, 511 food records, 511 mapping rows, zero food or mapping errors, zero orphan references, and unchanged Stage B snapshot.
- Exact Stage B manifest: **836/836 entries pass**, manifest SHA-256 `b85f8293297cb5e447d2293e31cfcdafbef50497260d870d54f14da441c7359e`.
- Registry and identity audit: 143 exact IDs aligned; 107 identities marked complete and 36 remain under source or expert review.
- New-registry migration: all 119 prior IDs remain; 24 added IDs have no food mapping. Existing Phase 1B files remain unchanged at 511 rows each. Their 109 legacy mapped compounds include 16 with current identity-review status; the 46 associated mapping rows are preserved but blocked from exposure. Identity-complete quantitative coverage is 93/143.
- Active food and mapping SHA-256 values: `aa15fd49be4afd30d1f61fe06de9039d0a925c22a6c56e970ddc75033b04f127` and `9dcaadf0821aee15f1666ca26c88c592bb1e98a781eb533e246ddd94dab9ca97`.
- JSON Schema checks: **8/8 schema fixtures passed** in PowerShell `Test-Json`; the synthetic obsolete 119-compound manifest mutation was rejected.

The authoritative Stage B source has one repeated non-stereospecific SMILES across (+)-catechin and (-)-epicatechin, each with a distinct InChIKey. Both source records and their open stereochemistry review are preserved. No new food data, mappings, or Phase 1B research were introduced.

The previous Phase 1B release remains an untouched historical package against its original Stage B baseline. Its report and batch evidence remain in `reports/phase1b/` and `releases/Phase1B-v1.0.0/`.
