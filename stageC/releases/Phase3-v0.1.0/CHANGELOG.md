# Phase 3 changelog

## Phase3-v0.1.0 — 2026-11-03

- Adds JSON recipe and meal validation/storage and an existing-project CLI workflow.
- Adds explicit raw/cooked/serving/leftover mass accounting and separate beverage-volume accounting.
- Adds Phase1B exposure reuse, raw-reference totals, multi-recipe/direct-food aggregation, partial servings, and explicit leftover serving equivalents.
- Adds a read-only, checksum-verified adapter for Phase1B-v1.3.1, Phase2-v0.3.0, and Phase4-v0.1.2. Phase 4 numerical PK is not exposed to calculations.
- Cooked estimates remain unavailable when the versioned Phase 2 package has no eligible quantitative records.
