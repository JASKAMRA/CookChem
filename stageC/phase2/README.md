# Stage C Phase 2 — final bounded review

**Roadmap status: IN_PROGRESS — evidence-scope closeout is complete, deployment closure is pending.** The current evidence release is bounded to the 117 existing observed cooking pairs. Phase 2 remains in progress until the Stage A target/serving decisions, approved model package, deployment environment, and scientific compatibility prerequisites are supplied and accepted.

**Current data release: Phase2-v0.3.1 — COMPLETE_WITH_DOCUMENTED_LIMITATIONS.** This immutable package preserves Phase2-v0.3.0 and updates the dependency to byte-verified Phase1B-v1.3.2. The Phase1B successor's embedded StageB_V20 package matches all 839 raw-byte manifest entries, and the Phase2-v0.3.1 package manifest and seven release tests pass. The scientific result remains zero justified cooked-concentration estimates; see `stageC/PHASE2_PHASE3_PROGRESS.md` for the release validation record. A complete data review does not close the deployment workstream.

The versioned release is [Phase2-v0.3.1](../releases/Phase2-v0.3.1/README.md), which depends on Phase1B-v1.3.2. It records final decisions for 63 retention candidates, 22 food/evidence combinations, all 584 Phase1B applicability rows, and all 197 identity-crosswalk groups. The release produces zero cooked concentration estimates because analytical basis, matrix/condition transfer, or cooked yield is unresolved where required.

The 117 observed pairs remain empirical source transcriptions: 33 turmeric pairs and 84 pumpkin-leaf pairs covering 24 analytes. They are concentration ratios, not total analyte-mass retention. The turmeric unit field now follows the source wording, “mg/g plant material”; fresh rhizome is the starting material, and the cooked-sample denominator remains uncertain. Pumpkin-leaf values retain their dry-weight basis.

## Scientific boundary

- Do not infer cooked concentration, mass retention, yield, moisture corrections, or uncertainty from the observed ratios.
- Candidate and applicability statuses preserve unresolved identity, matrix, cooking-condition, basis, and yield requirements.
- The Curcumin CID discrepancy remains visible. Unresolved cross-stage structures and stereochemistry are not joined by CID alone.
- Stage A was not accessed or run for this finalization. Stage B remains read-only.
- Two historical test logs referenced by the v0.2.0 package could not be recovered exactly; the successor lists them as excluded artifacts and does not fabricate them.

See the [Phase 2 finalization report](../releases/Phase2-v0.3.1/reports/PHASE2_FINALIZATION_REPORT.md), [scientific limitations](../releases/Phase2-v0.3.1/reports/PHASE2_SCIENTIFIC_LIMITATIONS.md), and [validation report](../releases/Phase2-v0.3.1/reports/PHASE2_VALIDATION_REPORT.md).
