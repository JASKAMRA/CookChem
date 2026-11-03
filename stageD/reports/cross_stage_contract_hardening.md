# Stage D cross-stage contract hardening

**Status: IMPLEMENTED AND UNIT TESTED; not a production comparison service.**

`build_cross_stage_comparison` links one Stage C Phase 3 recipe ingredient estimate to one normalized Stage B record. It requires the Phase 3 calculation and selected ingredient estimate to be complete; a single recipe (not a meal aggregate); caller-confirmed Phase 3 manifest verification; the expected Stage B release and SHA-256; matching Stage B hashes in the Phase 3 result, estimate and provenance; matching Stage B `Evidence_ID` and `Compound_ID`; and explicit finite nonnegative exposure bounds and concentration units. A missing amount remains an error, not zero. Reversed interval bounds and inconsistent provenance are rejected.

The output preserves dietary consumed amount (mg), raw-food concentration/unit, and cooked-food concentration/unit as separate fields. A cooked interval requires both bounds, an explicit unit, a non-raw cooked status, and a linked retention evidence ID. Missing cooked values remain null. These dietary fields stay separate from experimental dose text. Experimental dose values and experimental concentrations remain unnormalized/null because the Stage B normalization contract has no independently typed fields for them. The comparator performs no unit conversion, dose ratio, dose equivalence, or clinical interpretation. All six comparability checks remain caller-supplied tri-state adjudications. `READY_FOR_REVIEW` means the checks were marked true and the record still awaits scientific review.

## Verification boundary

The caller must verify that the named Phase 3 release manifest and each listed artifact match their SHA-256 values before setting `phase3_manifest_verification="verified"`. This function validates and records that assertion; it does not access the filesystem or cryptographically verify the release itself. Integration tests use a synthetic Phase 3 envelope and synthetic manifest hash; the current immutable Phase 3-v0.1.2 manifest is verified separately in the execution report. No release artifact was modified.

## Test coverage

The synthetic integration tests cover exact ID/hash binding, separate raw/cooked dietary concentrations, separate dietary and experimental fields, pending and failed gates, incomplete/unverified release rejection, inconsistent provenance, missing measurements and units, reversed bounds, and schema tampering. The focused contract module now has 18 tests; the final full Stage D suite result is recorded in `stageC/reports/NEXT_ADVANCED_EXECUTION_REPORT.md`. Run with:

```powershell
python -m unittest stageD.tests.test_contracts -v
```

An initial run without development dependencies skipped two formal schema tests. Those were subsequently rerun with the pinned development dependencies and passed.
