# Stage A owner handoff — `Retention_Final`

**Current gate: BLOCKED.** No approved serialized serving package or agreed operational target contract is available. Stage A remains frozen, no model is loaded or run, and cooked-concentration estimates remain **0**.

## Materials needed to resume review

1. **Complete RF-01–RF-15 in the structured tracker** at [`../../data/phase2/owner_decision_tracker.json`](../../data/phase2/owner_decision_tracker.json). For each item provide the owner response, supporting artifact, exact source locator, decision date, named scientific reviewer, approval status, and rationale for anything unresolved. A response becomes approved only when all supporting fields are present; this software cannot verify scientific truth.
2. **Supply the serialized package and complete manifest** described by [`PHASE2_STAGE_A_DEPLOYMENT_PACKAGE_SPEC.md`](PHASE2_STAGE_A_DEPLOYMENT_PACKAGE_SPEC.md). Include every listed byte artifact, exact SHA-256 and size, model metadata, ordered feature/preprocessing contracts, training provenance, runtime lock, target definition, output schema, and named review references.
3. **Resolve target semantics from primary methods/data.** Define the `Retention_Final` formula and scale; numerator/denominator and basis; paired replicate and cooked yield; moisture and liquid handling; analyte transformations; assay recovery/censoring; >100 values; missing/sentinel treatment; supported target domain; unit standardization; data transformations; and `Apparent_Increase` provenance/leakage.
4. **Obtain independent scientific and operational review.** Confirm the model artifact and lineage, scientific applicability and uncertainty, output contract, and whether any future supplied prediction record can be linked to Stage C. Provide reviewer/date/reference for each acceptance.

## Current readiness snapshot

The machine-readable dashboard is [`STAGE_A_DEPLOYMENT_READINESS_DASHBOARD.md`](STAGE_A_DEPLOYMENT_READINESS_DASHBOARD.md). It currently shows 0/15 approved owner decisions, no package integrity result, independent review pending, deployment blocked, and inference unauthorized. A package validator PASS is only a metadata/hash result and cannot change those approval requirements.

## Safe resumption sequence

Complete the tracker and artifact handoff → run the metadata-only package validator → resolve all failures → conduct independent scientific/operational review → document a separately authorized deployment decision. Phase 2 stays **IN_PROGRESS** until those steps are actually completed.
