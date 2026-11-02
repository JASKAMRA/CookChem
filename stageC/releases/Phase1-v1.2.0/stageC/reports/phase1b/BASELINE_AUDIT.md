# Phase 1B baseline audit

Audit performed before Phase 1B data or source-registry edits.

- Repository: `C:\Users\dakshant\Desktop\CookChem`.
- Stage B authoritative release: `stageB/release/StageB_Final`; manifest verified, 708 entries, 0 mismatches; SHA-256 of manifest `349021670220b89a6b147d82a1b483f6a741d0962a7dde7e883c3e661a1bfe4e`.
- Recalculated Stage B counts: 119 compounds, 286 interaction-evidence rows, 55 warning-ledger rows.
- Stage C active database: 0 food-composition rows; 0 mappings. No real exposure calculations are present.
- Phase 1 release: `Phase1-v1.0.0`; 61 listed release artifacts. Existing test report: 44/44 PASS, clean-copy PASS.
- Protected tree file counts and deterministic tree SHA-256 values are in `BASELINE_CHECKSUMS.json`, covering all Stage A files, authoritative Stage B, Stage B historical archive, and the original Stage C Phase 1 release.
- No project source or data files were modified before this baseline was written.
