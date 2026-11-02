# StageB_Final checksum reconciliation — 2026-11-02

The prior manifest was preserved as `SHA256SUMS.previous.json` (SHA-256 `36f79fa2c1a53603109d326b23eab6985a17b45d130857c01bc4cbd08a040fa3`; 708 entries). It mismatched 661 listed file hashes against the package contents at reconciliation time.

The Stage B portable semantic validator was run against a temporary byte-for-byte copy of the release after refreshing its generated validation report. Result: exit 0; all 16 automated checks passed, with warnings only. No evidence/source/registry content was changed for this reconciliation. The new manifest is generated over every release file except the manifest itself, including this reconciliation record and refreshed validator outputs.

This record is part of the newly checksummed release. The previous manifest remains archived above.
