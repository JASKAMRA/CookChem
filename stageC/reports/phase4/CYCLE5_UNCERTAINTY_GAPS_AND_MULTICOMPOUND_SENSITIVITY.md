# Cycle 5 — uncertainty gaps and compound-separated sensitivity

Status: **IN_PROGRESS**. This increment expands uncertainty coverage and reporting; it does not claim measured uncertainty for any catalog record or complete Phase 4.

## Catalog audit

The read-only Phase1B-v1.3.2 package contains **584 food-composition rows**, **584 mapping rows**, and **509 exact-identity mappings marked quantitative**. All 584 food rows contain an `uncertainty_notes` text field, but the schema has no structured concentration interval, standard-error, standard-deviation, or confidence-limit columns. Free text is retained as provenance and has not been converted to bounds. The package reports per-row source, method, sample-size and uncertainty notes; it does not provide standardized input intervals for recipe calculation.

The recipe engine does not persist an active user recipe/output corpus in the repository. Coverage is calculated against every recipe or meal output supplied at runtime. `build_uncertainty_gap_registry()` consolidates one or more such outputs and retains estimate, ingredient, food, compound, source IDs, DOI/URL/title, and reason for each missing or invalid dimension. A command-line builder accepts Phase 3 output JSON and writes the same machine-readable registry.

## Coverage dimensions

Coverage counts explicit source-backed intervals for:

- Food concentration and analytical variability.
- Ingredient quantity and cooked quantity.
- Cooking yield and cooking retention.
- Serving size, serving fraction, consumed fraction, and serving count.
- Recipe-level and meal-aggregation inputs.

Analytical variability and cooking yield are tracked separately and remain coverage-only. They are not multiplied into exposure because the current contracts do not define a validated application point and dimensional interpretation. Missing factors remain missing; text notes are not automatically parsed into numeric bounds. Point estimates, deterministic intervals, and probability distributions are distinguished explicitly. No distribution is assumed.

## Synthetic worked example

The test-only fixture `stageC/tests/fixtures/synthetic_multicompound_uncertainty_meal.json` contains three ingredients contributing to two compounds. It is not scientific evidence.

| Compound | Contributors | Point total | Source-bounded endpoint total |
|---|---|---:|---:|
| C-1 | I-MC-1, I-MC-2 | 0.625 mg | 0.324–1.089 mg |
| C-2 | I-MC-1, I-MC-3 | 0.425 mg | 0.22032–0.74052 mg |

The calculations are tested through the existing recipe and meal engine. Sensitivity contributors are grouped only by explicit `compound_id`; each result contains its own complete or partial interval status. The two compound totals are never added together. The ranges are deterministic synthetic endpoints, not probability or confidence intervals.

## Verification and limits

`stageC/tests/test_uncertainty_coverage.py` covers source-linked gap aggregation, duplicate ingredients, mixed units, missing bounds, reversed interval ordering, zero-valued factors, and compound separation. `stageC/tests/test_app_api.py` verifies that the application exposes the registry and compound-specific report. With the pinned development dependencies, the uncertainty suite passed **12/12**, including schema validation, and the current application API suite passed **8/8**. The active Stage C and Stage D schema set also passed Draft 2020-12 metaschema validation. No uncertainty test was skipped in these verified runs.

No cooked uncertainty interval was added: the pinned Phase 2 release still has zero accepted cooked estimates. No published-data comparison or external validation was performed as part of this uncertainty increment.
