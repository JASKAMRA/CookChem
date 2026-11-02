# Resume instructions

Read `BASELINE_AUDIT.md`, `SOURCE_SCREENING_RULES.md`, `CHECKPOINTS.json`, `SEARCH_COVERAGE_REPORT.md`, and `NEXT_STEPS.md`. Batches 001, 002 and 003 are completed. Active production contains six validated USDA aggregate rows and six mappings across four compounds. Batch 003 adds EGCG and theaflavin as prepared-beverage records; its source notes, candidates, accepted input, exposure input/results, and independent arithmetic check are in `batches/batch_003_usda_tea/`.

The immediate next task is to get the official April 2018 SR Legacy download from the USDA FoodData Central download page and inspect caffeine for NDB 14209. Do not use the third-party copy of an SR26 report as an ingested source. Re-run focused Stage C tests after changes and the full suite/active validator at milestones. Compare Stage A, Stage B, Stage B archive and historical-release hashes with `BASELINE_CHECKSUMS.json`; do not edit those protected trees.
