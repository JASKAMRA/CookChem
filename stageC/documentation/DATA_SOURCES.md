# Data sources

## Stage B

The sole compound/evidence integration source is the exact-manifest-verified `stageB/release/StageB_FINALIZED` release. The 143-compound registry and its identity audit are cross-checked by exact `Compound_ID`, name, and chemical-identifier fields. The nine-file read-only import and source hashes are recorded in `data/stage_b_snapshot_20261103/import_manifest.json`. Stage B interaction evidence is not food composition.

## Food composition

The existing Phase 1B dataset contains 511 accepted quantitative food records and 511 mappings from the earlier 119-compound baseline. Of its 109 mapped compounds, 16 currently have Stage B identity-review status; their 46 legacy mapping rows remain traceable but cannot produce exposure estimates. Identity-complete quantitative coverage is 93 of 143. This software-foundation update did not acquire or add scientific food records.

Before admitting a record, verify analyte and food identity, food part/state, concentration and unit, moisture basis, source/database identifier and exact locator, and verification scope. An abstract does not establish full-text verification. Keep database-derived, primary analytical, secondary, lab, and user-supplied records distinct.
