# Phase 3 changelog

## Phase3-v0.1.2 — 2026-11-04

- Formally validates every active Stage C Draft 2020-12 schema; fixes decimal-string bounds for recipe/meal quantities, counts, and fractions.
- Rejects malformed runtime recipe/meal identifiers and preserves unresolved mapping and missing batch-yield states.
- Adds a supplied Stage A output contract with pinned input/runner hashes, provenance, explicit semantics, eight compatibility gates, scientific review status, and blocked mock outputs.
- Separates apparent concentration ratio, concentration retention, total-mass retention, measured retention, and model-predicted retention; requires measured mass or volume yield for total-mass retention calculations.
- Adds bounded, non-probabilistic uncertainty propagation and independent arithmetic validation foundations.
- Stage A remains read-only and unexecuted; Phase2-v0.3.1 remains at zero quantitative cooked estimates.
