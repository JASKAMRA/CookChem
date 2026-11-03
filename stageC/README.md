# CookRisk Stage C

## Current handoff

Phase1B's corrected successor is [Phase1B-v1.3.2](releases/Phase1B-v1.3.2/README.md). It separates raw mapping presence, identity completion, accepted mapping, and scientific quantitative eligibility. The V20-based package contains 584 records and mappings; 130 compounds have raw mapping rows, 125 of these are identity-complete, 121 are accepted mappings, 116 are scientifically eligible quantitative compounds across all food classes, and 80 are eligible in ordinary food. The 125 count is not a substitute for quantitative eligibility.

The Phase 2 evidence-release scope is closed within the fixed 117-pair boundary in [Phase2-v0.3.1](releases/Phase2-v0.3.1/README.md), with documented scientific limitations and zero cooked-concentration estimates. The Phase 2 roadmap remains **IN_PROGRESS** pending Stage A owner decisions, a hashed deployment package, target/denominator approval, and scientific compatibility acceptance. Its 63 candidates, 22 compatibility rows, 584 applicability rows, and 197 identity crosswalk rows have recorded dispositions. Two unrecoverable historical test logs are disclosed in the release manifest.

Phase 3's functional recipe/meal engine is available through the [`cookrisk-stagec recipe` and `meal` CLI](reports/phase3/PHASE3_USER_GUIDE.md). It validates and stores structured recipes, adds ingredients, calculates ingredient/recipe/meal exposures, tracks measured mass and beverage-volume balance, reports leftovers and partial servings, and exports provenance. Its CLI verifies and uses Phase1B-v1.3.2 and Phase2-v0.3.1 read-only. The guarded cooked interval path remains incomplete because Phase2-v0.3.1 contains zero quantitative cooked-concentration estimates.

Phase 4 has an `IN_PROGRESS` versioned evidence layer. No approved Phase 4/Stage D specification was found, so its scope is explicitly proposed in [the Phase 4 scope document](phase4/PROPOSED_SCOPE.md). Phase4-v0.1.2 contains one full-text primary human PK source and six separate pending evidence rows: five condition-level Cmax values and one qualitative statistical result. The identity link is name-only, applicability is context-limited, and all six await independent review. Phase 3's read-only selector returns zero contextual records and never exposes numerical PK evidence to exposure calculations.

## Advanced execution update — 2026-11-04

- Phase 3 schema and runtime validation were hardened. All seven active Stage C Draft 2020-12 schemas (recipe, meal, Stage A handoff, Phase 2, and Phase 4) pass metaschema validation with the pinned `jsonschema==4.26.0` dependency. Recipe/meal fixtures now reject string-encoded values outside numeric bounds.
- Phase 3's Stage A handoff and guarded concentration calculations are implemented in `src/stage_c/cooking_integration.py`; no supplied Stage A prediction is currently eligible because the inspected package contains no serialized model artifact/hash and does not define `Retention_Final`'s denominator or measurement basis. See [the readiness report](reports/phase2/STAGE_A_INTEGRATION_READINESS.md).
- Stage C Phase 4 now has source-typed bounded interval propagation, deterministic sensitivity ranking, and explicit missing-uncertainty reports. Stage C Phase 5 now independently recomputes exposure arithmetic and keeps software, mathematical, published-data, and external validation distinct. No published-data or external validation claim is made.
- Stage D has working evidence-normalization and comparability contracts. Twelve mechanism candidates across six primary studies are source-pinned and remain pending independent review; the 317-row queue preserves machine triage separately from human review. This is not an exhaustive mechanism census or completed source review.
- Current validation at that checkpoint: Stage C working-tree regression passed 239/239; Phase4 registry passed 13/13; Stage D suite passed 46/46; Phase3-v0.1.2 isolated package passed 79/79. All 27 working Stage C/Phase 4/Stage D schemas passed Draft 2020-12 metaschema checks.

## Protected boundaries

- Stage A was inspected read-only for its current docs, input hash, runner hash, and outputs; it was not changed, imported, trained, or used for inference.
- Stage B remains read-only.
- Earlier versioned releases remain preserved; successors are additive.
- Phase4-v0.1.0 and v0.1.1 remain immutable; v0.1.2 is their checksummed successor.
- The repository's earlier Phase 1 working tree remains the distinct Phase1-v1.3.0 foundation and is not the V20-based Phase1B package.

## Current validation

- Phase1B-v1.3.2 package manifest and embedded V20 manifest verified; reconciliation/byte-integrity tests: 4/4 passed.
- Phase2-v0.3.1 manifest verified; release tests: 7/7 passed.
- Phase3-v0.1.1 remains immutable; Phase3-v0.1.2 is the tested successor.
- Current Stage C working-tree regression: 239 passed, 0 failed, 0 skipped; Stage D suite: 46 passed, 0 failed, 0 skipped.
- Phase 3 focused engine, CLI, schema, and pinned-release integration tests are recorded in [the current progress report](PHASE2_PHASE3_PROGRESS.md).
- Phase4-v0.1.2 source and packaged registry tests: 13/13 passed in each location.
- The full Stage C regression suite and bundled Phase1B/Phase2 release tests are recorded in [the current progress report](PHASE2_PHASE3_PROGRESS.md).
- Archived-byte comparison confirms Phase1B-v1.3.0 and Phase2-v0.1.0/v0.2.0 match their Git archive bytes. Phase1-v1.3.0 has newline-only drift in 877 current worktree files; `.gitattributes` now specifies exact release bytes for future checkouts.

See [PHASE2_PHASE3_PROGRESS.md](PHASE2_PHASE3_PROGRESS.md) for the detailed checkpoint, outstanding work, and known limitations.
# Local application prototype

A non-production local prototype is available in [`app/README.md`](app/README.md). It uses the pinned Phase 1B and Phase 2 inputs, the existing recipe/meal engine, and Stage D evidence/comparability contracts. Start it with `python stageC/app/server.py --host 127.0.0.1 --port 8765`. The UI keeps raw reference amounts separate from cooked estimates, which remain unavailable because the pinned Phase 2 release has zero accepted cooking estimates.

Phase 4 uncertainty propagation and coverage increments are documented in [`reports/phase4/UNCERTAINTY_IMPLEMENTATION.md`](reports/phase4/UNCERTAINTY_IMPLEMENTATION.md). Structured raw-input bounds require source-backed intervals at every multiplicative factor. No probability distributions are assumed.

