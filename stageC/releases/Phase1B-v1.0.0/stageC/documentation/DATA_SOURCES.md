# Data sources

## Stage B

The sole compound/evidence integration source is the checksum-verified `stageB/release/StageB_Final` release. Exact files and hashes are recorded in `data/stage_b_snapshot/import_manifest.json`. Stage B is rated `READY_WITH_WARNINGS`; its interaction evidence is not food composition.

## Food composition

Potential authoritative source families reviewed for suitability are USDA FoodData Central Foundation Foods and Experimental Foods. The registry is `data/food_composition/source_registry.csv`. No compound-level concentration record from these sources, a paper, a regional database, or a supplied laboratory dataset was ingested. Therefore the verified, unverified, and candidate quantitative-record counts are all zero. No API request or source record is claimed by this release.

Before admitting a record, verify analyte and food identity, food part/state, concentration and unit, moisture basis, source/database identifier and exact locator, and verification scope. An abstract does not establish full-text verification. Keep database-derived, primary analytical, secondary, lab, and user-supplied records distinct.
