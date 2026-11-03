# Stage C Phase 1 and Phase 1B handoff

Stage C Phase 1 is the software foundation for read-only Stage B integration, source-backed food composition, conservative compound mapping, mass/volume concentration normalization, raw-food exposure arithmetic, validation, and provenance. The active connector now reads the exact-manifest-verified `StageB_FINALIZED` registry with 143 compounds. All 119 prior IDs remain and the 24 added IDs are available without inferred food mappings.

The existing Phase 1B dataset remains unchanged at 511 accepted ordinary-food measurements and 511 mappings. Of 109 legacy mapped compounds, 16 currently require Stage B identity review; the 46 affected mapping rows remain preserved and are blocked from exposure calculations. Identity-complete quantitative food coverage is 93/143. The 24 additions have no mappings, and 34 compounds have no legacy food mappings. The previous Phase 1B release documents its original 109/119 baseline. No new Phase 1B research or records were added during this software update.

The historical Phase 1B-v1.0.0 package remains in the source workspace and is not bundled in this software-foundation release. Its completion report, source batches, accepted/held/rejected decisions, and coverage register are included under `../reports/phase1b/`.

Seven final-target botanical measurements have primary quantitative reports and one additional irilone value is held as secondary-source evidence. All remain outside ordinary-food coverage. Ten Stage B targets therefore remain without accepted ordinary-food measurements; 7-methoxyflavanone and the exact pentamethoxyflavone also lack verified numeric matrix values.

Phase 1 does not apply Stage A cooking-retention predictions. It does not establish recipe-level dietary exposure across a population, bioavailability, clinical effects, or health risk. Phase 2 is a separate integration task.

The Stage B read-only connector resolves only to `stageB/release/StageB_FINALIZED` and verifies its exact manifest. The Phase 1 v1.3.0 release bundles the source package and the versioned Stage B snapshot. Reproduce the checks with the commands in the release README.
