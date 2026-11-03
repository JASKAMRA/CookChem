# Stage C Phase 1 and Phase 1B handoff

Phase 1 provides the software foundation: Stage B connector, source-backed food composition, conservative mapping, unit normalization, raw-food arithmetic, validation, and provenance. The current Phase 1B successor uses the versioned `StageB_V20_20261103` identity-adjudicated snapshot, not the older `StageB_FINALIZED` baseline.

Phase 1B is closed by user acceptance at **125/130** identity-complete compounds with accepted quantitative ordinary-food measurements. There are 143 compounds total, 130 identity-complete, 13 identity-pending, 584 food records and 584 mappings. The approximate 120 target is met; the 130 minimum remains five short. Five gaps remain documented and unresolved. The validation report confirms zero food errors, zero mapping errors and zero snapshot changes.

Phase 1 does not apply cooking retention. Phase 2 is now underway as a separate cooking-retention integration. Its first increment is a strict Stage A–Stage B identity crosswalk and an observed-evidence ledger. The Stage A folder contains 1,124 grouped-validation records and OOF predictions, but no serialized fitted estimator or preprocessing pipeline; OOF predictions must not be used as deployment predictions. Phase 2 must preserve measured versus modelled evidence, and must verify exact compound identity, food matrix, cooking conditions, and measurement basis before applying retention.

See `stageC/phase2/README.md` and `stageC/reports/phase2/PHASE2_KICKOFF_READINESS_AUDIT.md` at the repository root for the Phase 2 work in progress. Stage A source files remain unchanged.
