# Phase 1 handoff

**Release:** Phase1-v1.0.0. **Scope:** Stage B read-only connection, food composition ingestion/normalization, conservative mapping, raw-food exposure, validation, CLI, and provenance. Stage A integration and cooking retention are excluded.

The imported release is `stageB/release/StageB_Final`, status `READY_WITH_WARNINGS`, with 119 stable compound IDs and 9 allowlisted CSV sources. Snapshot checksums match. Warning IDs are exposed on compound records and propagated to estimates. Preserve inherited identity, food-occurrence, supplement-context, numeric/unit, and source-audit limitations.

No qualifying quantitative food records were actually ingested; verified, candidate, and unverified quantitative records are each zero. All 119 compounds currently lack quantitative food data. Thus there are no real source-backed calculations; the arithmetic demonstration is synthetic and exists only in tests. Missing values remain missing.

Release contents are defined by `../releases/Phase1-v1.0.0/RELEASE.json`, which hashes the shipped Stage C code, schemas, templates, snapshot, and source registry. Current interpreter is Python 3.14.7; implementation uses the standard library. Rebuild/test and CLI validation details are in reports. Known limitation: pytest package is unavailable, so tests ran under unittest.
