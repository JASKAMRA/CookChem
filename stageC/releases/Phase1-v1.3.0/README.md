# CookRisk Stage C Phase 1 v1.3.0

Status: PHASE1_SOFTWARE_FOUNDATION_UPDATED_AND_VALIDATED.

This package updates the Phase 1 software foundation to the exact-manifest-verified StageB_FINALIZED registry (143 compounds). It includes the complete read-only Stage B source package and a 143-compound Stage C snapshot. Prior Stage C release folders are not bundled or modified.

The existing 511 food-composition records and 511 mapping rows are included byte-for-byte. Sixteen legacy-mapped compounds have current Stage B identity-review status, so 46 mapping rows remain traceable but cannot produce exposure estimates. Current identity-complete quantitative coverage is 93/143. No new food records or mappings were added.

## Reproduce checks

Run from this release directory:

```powershell
python verify_release.py
python stageB/release/StageB_FINALIZED/scripts/manifest_integrity.py verify stageB/release/StageB_FINALIZED --mode exact
python stageC/scripts/inspect_stage_b.py
python stageC/scripts/validate_phase1.py
pwsh -NoProfile -File stageC/scripts/validate_json_schemas.ps1
python -B -m unittest discover -s stageC/tests -v
```

`CHECKSUMS.json` covers every packaged artifact except itself and its detached digest. `CHECKSUMS.sha256` records the manifest digest.

## Known reviews

Thirty-six Stage B identity records remain open for expert or source adjudication. Sixteen of those compounds appear in 46 preserved legacy mapping rows; the current calculation engine blocks them until identity review is resolved. (+)-Catechin and (-)-epicatechin retain separate InChIKeys and a shared non-stereospecific SMILES for review.

The earlier workspace package `Phase1B-v1.0.0` is retained unchanged. Its existing verifier reports a detached checksum digest mismatch and artifact hash/size mismatches; this release does not rewrite that historical package.

Clean-copy validation passed: 72/72 Python tests, 8/8 JSON Schema fixtures, Stage B exact manifest 836/836, and Phase 1 validation with zero errors. See `VALIDATION_RESULTS.json` and `TEST_RESULTS.txt`.
