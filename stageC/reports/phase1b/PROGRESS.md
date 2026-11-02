# Stage C Phase 1B Progress

- Historical release `Phase1-v1.2.0` remains preserved; no new release was created. The official USDA SR Legacy April 2018 CSV archive was downloaded and caffeine FDC 171890 / NDB 14209 was verified against the component tables; API provenance remains separately identified.
- Batches 010–015 each screened 25 distinct Stage B targets against primary-source panels (150 batch-specific outcomes total). Batches 010–015 contributed 85 quantitative food records. Batch 015 added eight raw common-bean records spanning eight analytes and newly covered one Stage B compound.
- Active dataset: 99 accepted food-composition records and 99 mappings, covering 39/119 compounds; 80 have no accepted quantitative measurement. Validation reports 19 identity-review entries.
- Search log: 289 source/compound events, spanning all 119 Stage B IDs. This establishes logged screening coverage, not exhaustive literature absence.
- Food evidence covers berries, citrus, fresh fruit/vegetables/spices, culinary and native herbs, native Australian fruits/spices, and Portuguese common beans. Semi-quantitative panels and dry/fresh bases remain explicitly flagged.
- Exact stereochemistry, positional isomers, glycosides/aglycones, free/bound fractions, and units/bases were not conflated. Batch 014 heatmap-only findings and Batch 015 generic stereoisomer values were not ingested. Paired cooked-bean values are held out of Phase 1B.
- No new exposure estimates were calculated; study-specific dried ingredients/raw-seed dry-weight measurements lack compatible individual as-consumed serving inputs.
- Active validation: PASS, 99 records, 99 mappings, zero orphan/error findings. Active and clean-copy regression outcomes are in `CLEAN_COPY_VALIDATION.json`.
- Protected integrity recheck: PASS (Stage A 19/19, Stage B Final 709/709, Stage B archive 8,096/8,096, Phase1-v1.2.0 package 816/816). Historical release files remain untouched.
