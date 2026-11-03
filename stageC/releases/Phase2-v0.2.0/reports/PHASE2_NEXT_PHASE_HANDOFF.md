# Phase 2 Next-Phase Handoff

## What is complete

- Deterministic Phase 1B-v1.3.0 integration and ordinary/contextual classification are retained in Phase2-v0.1.0.
- All 117 research-pair means/SDs/table locators are checked against the two primary sources and all ratios independently recomputed.
- Candidate identity decisions and 22 food-retention compatibility decisions are preserved at record level.
- No cooked-concentration output or model inference is claimed.

## Smallest scientific milestones

1. **Turmeric denominator bridge:** obtain source-specific moisture/dry-matter and cooked yield/denominator data for the exact Phase1B commercial powder and the Suresh samples, or leave the 20 records unresolved.
2. **Pepper sample-state bridge:** document whether the retail measurement's sampled pepper was whole or ground and its moisture/dry-weight basis; match that preparation to Suresh's powdered spice. Preserve three independent cooking scenarios.
3. **Identity review:** recover Stage A source-level chemical IDs/structures and perform isomer-aware graph comparison with a pinned cheminformatics toolkit. Review the 45 rows without accepting CID-only matches.
4. **Model gate:** recover the exact CSV with SHA-256 `cd51de3286d9fea7c4d87ce45f4c9c4301214b1944f72bff19c3b41ce0358c27`; recover the original joblib/transitive package lock; run a real new-record smoke test only after both gates pass.
5. **Phase 1B test migration:** maintain the historical checkpoint and tests; if root working-tree tests are expected to target the newest data, add a documented version-aware test/checkpoint fixture rather than rewriting historical counts.

## Data requirements for valid cooked concentration

For a selected food/analyte/process, obtain same-sample or defensibly compatible quantitative raw concentration, cooked edible yield, matched measurement basis, cooking conditions, and analyte lost to discarded media when claiming total retention. For concentration estimation only, use a source explicitly measuring the same post-cooked concentration basis and retain ratio semantics. Preserve source sample-level or group-mean uncertainty as supported.

## Exit gate

Do not label Phase 2 COMPLETE until at least one record passes identity, ordinary-food context (or a separately labeled ingredient context), matrix/state, basis, unit, process, quantitative evidence, provenance, and independent calculation checks—and the full test/reproducibility path passes. A zero-row cooked output is valid while those conditions are unmet.
