# Stage C Phase 4 — Uncertainty Foundation

## Scope

This is an additive analysis layer over the existing Phase 3 recipe and meal outputs. It does not modify the recipe engine, CLI, source food-composition records, Stage A/B data, or historical releases.

## Implemented

- `src/stage_c/uncertainty.py` classifies Phase 3 ingredient estimates and Phase 3 recipe/meal compound totals.
- Source-referenced Phase 2 retention bounds remain bounded intervals, conditional on reported concentration, cooked quantity, serving fraction, and consumed fraction. They are not probability or confidence intervals.
- Phase 3 point estimates remain point estimates. The module explicitly lists missing analytical, quantity, and fraction uncertainty; it never represents missing uncertainty as a zero-width interval.
- Incomplete Phase 3 estimates remain non-quantifiable.
- Generic factor propagation accepts only explicit nonnegative, source-referenced intervals. Reported, measured, derived, and assumed scenarios must use matching provenance classes. Assumed inputs are labeled `SCENARIO_ENVELOPE`.
- Sensitivity ranks one-factor-at-a-time interval widths with other factors held at their reported point values. The output says it is non-probabilistic and is not variance attribution.

## Data limits and interpretation

The current Stage C food-composition schema has free-text `uncertainty_notes`, not structured analytical uncertainty. Recipe quantities and consumed fractions are point values. As a result, current raw-food ingredient results usually classify as `POINT_ESTIMATE_ONLY`; no additional uncertainty bounds are inferred. A cooked estimate can carry a Phase 2 retention interval, but that interval only covers the retention range under the stated point inputs. If Phase 3 lacks complete source evidence, the helper withholds quantitative bounds.

The generic propagation helper checks required metadata and numerical interval consistency, but it cannot authenticate a cited source or reconcile units on behalf of the caller. Callers must verify the cited evidence and normalize all factors to dimensionally compatible units first. The Phase 3 classifier requires the existing `provenance.retention_evidence` record, including its evidence ID and source reference.

## Tests

`tests/test_phase4_phase5_foundations.py` exercises real Phase 3 recipe and meal calculation outputs, retention-backed intervals, explicit missing uncertainty, source-class consistency, assumed scenario labels, propagation, and deterministic sensitivity ranking. Tests use synthetic fixtures and do not constitute evidence about real food composition.
