# Stage C Phase 1 and Phase 1B handoff

Stage C Phase 1 is the software foundation for read-only Stage B integration, source-backed food composition, conservative compound mapping, mass/volume concentration normalization, raw-food exposure arithmetic, validation, and provenance. Phase 1B has expanded the data layer to 511 accepted ordinary-food measurements across 109 of 119 Stage B targets.

The Phase 1B final release and its reproducibility instructions are in `../releases/Phase1B-v1.0.0/`. The authoritative current ordinary-food coverage report is `../reports/phase1b/PHASE1B_COMPLETION_REPORT.md`; source batches, accepted/held/rejected decisions, and the coverage register are retained under `../reports/phase1b/`.

Seven final-target botanical measurements have primary quantitative reports and one additional irilone value is held as secondary-source evidence. All remain outside ordinary-food coverage. Ten Stage B targets therefore remain without accepted ordinary-food measurements; 7-methoxyflavanone and the exact pentamethoxyflavone also lack verified numeric matrix values.

Phase 1 does not apply Stage A cooking-retention predictions. It does not establish recipe-level dietary exposure across a population, bioavailability, clinical effects, or health risk. Phase 2 is a separate integration task.

The Stage B read-only connector resolves to the current `StageB_Final` package and checks its manifest. The Stage C release bundles a copy of that input package and a versioned Stage B snapshot. Reproduce the current tests and data validation with the commands in the release README.
