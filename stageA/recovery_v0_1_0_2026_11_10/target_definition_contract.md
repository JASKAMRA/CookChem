# Target-definition contract — status BLOCKED

## No approved Stage A model target

No common target is approved for retraining or inference in this release.

### Verified limited target family

`VERIFIED_APPARENT_RATIO = 100 × C_cooked / C_raw`

This is a unit-preserving cooked/raw concentration ratio for the 117 linked Phase 2 observations. It is not total-mass retention. It cannot yield cooked analyte mass without compatible raw/cooked yield, moisture basis, and cooking-liquid disposition.

### Explicitly prohibited substitutions

- Do not call an apparent concentration ratio total-mass retention.
- Do not use `Apparent_Increase` as a predictor.
- Do not invent a yield factor or infer it from food type.
- Do not pass `Retention_Final` model outputs into a Stage C cooked-exposure calculation.

## Requirements to approve any future target

For every admitted source row: original paper locator; original values and units; numerator and denominator; raw/cooked basis; yield and liquid disposition when total-mass retention is claimed; reproducible equation; named scientific review.
