# Phase1B v1.3.1 reconciliation

This patch successor preserves v1.3.0 source values and the prior user-authorized closeout. It separates raw mapping presence, accepted mapping, identity completion, and scientific quantitative eligibility. The packaged StageB_V20_20261103 registry is authoritative for identity status.

## Independently derived inventory

- Food records: 584 (335 ordinary food, 221 food ingredient, 28 prepared beverage); 584 mappings.
- Raw mapped Stage B IDs: 130; 125 identity-complete and 5 identity-pending.
- Accepted mapped IDs: 121. Quantitatively eligible IDs after V20 identity reconciliation: 116 across all classes, 80 in ordinary food.
- Ordinary-food raw mapped IDs: 87; 84 complete and 3 pending in V20.
- Eleven accepted quantitative records were made eligible by reconciling stale identity status to V20. Concentrations, source records, mappings, and accepted-mapping flags were not changed.
- Nine IDs with raw mapping rows but no accepted mapping are visible in the new raw-mapping fields; their acceptance status was not promoted. Held quantitative candidates and medicinal-context rows remain ineligible.
- The 125 value recorded by v1.3.0 denotes identity-complete mapped IDs; it does not establish 125 scientifically eligible quantitative compounds. Corrected eligibility is 116 across all classes and 80 ordinary-food compounds.

## Validation

The successor keeps Phase1B-v1.3.0 immutable. See `CHECKPOINTS.json` for independent file hashes and counts, and `CHECKSUMS.json` for the package manifest. The prior closeout authorization is retained; corrected eligibility does not meet the approximate 120 target or the 130 minimum.
