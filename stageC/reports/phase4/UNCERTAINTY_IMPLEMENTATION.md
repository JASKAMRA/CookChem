# Stage C Phase 4 uncertainty coverage and sensitivity

Status: **IN_PROGRESS**. This increment adds structured uncertainty metadata transport, raw-input endpoint propagation, recipe/meal coverage and compound-specific sensitivity. It does not make Phase 4 complete.

## What the code supports

- `stageC/src/stage_c/uncertainty.py` validates source-referenced nonnegative intervals and preserves the interval source class (measured, source-reported, literature-derived, scenario, or model prediction). Missing bounds never become zero-width intervals.
- `stageC/src/stage_c/recipe_engine.py` carries structured `provenance.uncertainty_inputs` through to each Phase 3 ingredient estimate and records the normalized ingredient quantity used by the calculation.
- `stageC/schemas/uncertainty_inputs.schema.json` defines source-traceable interval metadata for concentration, analytical variability, ingredient quantity, serving size/fractions/count, retention, cooked quantity/yield, recipe level and meal aggregation.
- For raw-reference estimates, `assess_phase3_structured_input_uncertainty` propagates lower and upper endpoints only when all four multiplicative factors have valid source bounds: food concentration, normalized ingredient quantity, serving fraction, and consumed fraction.
- Phase 2 cooked intervals continue through the existing independently validated retention pathway. Multi-ingredient recipe and meal sensitivity is additive and is grouped by compound; distinct compounds are never summed together.
- Coverage output reports missing concentration, quantity, serving-size, serving-fraction, consumed-fraction, serving-count and retention bounds per estimate, with recipe/meal aggregate uncertainty status.
- Coverage now separately inventories analytical variability and cooking-yield bounds as source-linked dimensions. These dimensions are coverage-only: there is no propagation through a yield or analytical-variability factor until its source-specific meaning and units are contractually defined.
- `build_uncertainty_gap_registry()` combines recipe and meal result coverage by dimension while retaining estimate, ingredient, food, compound, source IDs and available source locators. `stageC/scripts/build_uncertainty_gap_registry.py` writes the reproducible JSON report from one or more Phase 3 result objects.
- Multi-compound interval sensitivity is emitted as separate per-compound reports. Every contributor must carry a nonempty compound ID; missing or mixed identities fail closed.
- Top-level `recipe_level` and `meal_aggregation` metadata are validated and reported as coverage rows when supplied. They are not numerically applied as multipliers because their scientific meaning and application point must be defined by a source-specific contract first.

## Interpretation limits

Bounds are deterministic endpoints, not probability intervals, confidence intervals, or variance contributions. The system does not create distributions or correlations. A Phase 2 retention interval currently supports a cooked amount only conditional on point-valued concentration, cooked quantity and serving/consumed fractions. The combined cooked-input uncertainty path is not implemented because no compatible Phase 2 quantitative estimates are accepted and no validated combined contract is available. Recipe-level and meal-aggregation metadata are coverage-only until their factor semantics are defined. Current published food-composition entries usually lack analytical uncertainty; recipe quantities and fractions are entered as point values unless a user supplies source-backed bounds.

## Synthetic demonstration

`stageC/tests/fixtures/synthetic_uncertainty_recipe_meal.json` and `stageC/tests/fixtures/synthetic_multicompound_uncertainty_meal.json` contain explicitly synthetic two-ingredient and three-ingredient/two-compound examples. Tests verify lower/upper arithmetic at ingredient, recipe and meal levels; source-linked gap aggregation; width ranking; missing-factor withholding; duplicate ingredient preservation; zero-factor behavior; unit mismatch; reversed bounds; and cross-compound aggregation rejection. These fixtures are not evidence and are not part of a dataset or release.

No Monte Carlo analysis was added because defensible probability distributions and dependence assumptions are unavailable.
