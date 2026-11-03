# Stage B checksum gate status — 2026-11-02

## Finding

The Stage C read-only connector cannot load `stageB/release/StageB_Final` in its current state. Running `python3 stageC/scripts/build_compound_mapping.py` returns `Stage B release checksum mismatch` for the connector's eight allowlisted files:

- `data/compound_registry.csv`
- `data/cooking_retention_evidence.csv`
- `data/drug_probe_registry.csv`
- `data/interaction_evidence.csv`
- `data/publication_bibliography.csv`
- `data/study_registry.csv`
- `data/warning_ledger.csv`
- `documentation/data_dictionary.md`

An independent read-only hash comparison found 661 mismatches among the 708 paths in the current `manifests/SHA256SUMS.json`; zero listed paths were missing. This indicates broad divergence between the current release tree and its manifest, beyond the connector's eight-file allowlist.

The preserved Stage C import manifest is tied to the earlier Stage B manifest SHA-256 `349021670220b89a6b147d82a1b483f6a741d0962a7dde7e883c3e661a1bfe4e`. The Stage C baseline recheck report records a PASS at `2026-11-02T10:35:00Z`; this new check is later and shows the release tree no longer matches its manifest. Historical PASS reports are retained as point-in-time records and are not rewritten.

## Handling

No Stage B content, manifest, or Stage C snapshot was modified. Candidate evidence gathering can continue in batch directories. Ingestion, mapping rebuild, validation, and accepted-coverage updates must wait for the release owner to restore a verified Stage B release or publish a new reconciled release with matching hashes.


## Resolution (2026-11-02)

The earlier blocked finding above is historical. The release owner authorized reconciliation in this task. Stage B validation passed 16/16 checks on a byte-for-byte temporary copy; the prior manifest was archived, a reconciled manifest was generated, and the Stage C connector verified 710/710 entries with zero mismatches. Stage C imported a new versioned snapshot and the current Phase 1 validation passes. See `STAGEB_RELEASE_RECONCILIATION_2026-11-02.md`.
