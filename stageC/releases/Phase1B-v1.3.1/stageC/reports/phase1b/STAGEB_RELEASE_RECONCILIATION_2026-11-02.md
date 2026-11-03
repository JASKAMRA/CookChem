# Stage B release reconciliation — 2026-11-02

The previous `StageB_Final` manifest SHA-256 was `36f79fa2c1a53603109d326b23eab6985a17b45d130857c01bc4cbd08a040fa3`. Its 708 listed hashes disagreed with 661 files in the committed release tree. The old manifest was preserved at `stageB/release/StageB_Final/history/reconciliations/2026-11-02/SHA256SUMS.previous.json`.

The Stage B portable validator ran on a temporary byte-for-byte copy before reconciliation: **16/16 automated checks passed**, zero errors, 313 warnings. The warnings remain in the Stage B validation output and cover existing source/outcome review limitations. The validator does not establish scientific truth.

No Stage B evidence, identity, compound, or source-registry data were edited. The generated validation report was refreshed, a reconciliation record was added, and a new SHA-256 manifest was generated over all 710 release files other than the manifest itself. The new manifest SHA-256 is:

`52a5ee457f5730ee1642c2a51b121ad0d8ef1165f1a51e66f0260a25c2fc1024`

The Stage C connector independently verifies the reconciled package with 710 manifest entries and zero mismatches. A new versioned Stage C snapshot, `stageC/data/stage_b_snapshot_20261102`, was imported against this manifest. The prior snapshot was preserved as `stageC/data/stage_b_snapshot_pre_reconcile_20261102`.

This reconciliation repairs hash alignment; it does not clear the Stage B package's documented scientific review warnings.
