# StageB_Final checksum reconciliation — 2026-11-02

## Manifest count and contract

The preserved prior manifest has 708 entries (SHA-256 `36f79fa2c1a53603109d326b23eab6985a17b45d130857c01bc4cbd08a040fa3`). Relative to that snapshot, the then-current release had two legitimate reconciliation artifacts: this report and `SHA256SUMS.previous.json`, giving 710. The integrity repair added `documentation/INTEGRITY_POLICY.md` and `scripts/manifest_integrity.py`; the repaired StageB_Final now has 712 manifest entries. Its verifier detects missing, extra, duplicate, malformed, unsafe, and modified files; the manifest excludes itself. The release-readiness test validates the artifact set against the manifest rather than a fixed historical count.

## The five reported checksum exceptions

The four PNGs were checked using raw bytes only. Their prior manifest digest exactly equals the current raw SHA-256; all bytes and sizes are preserved. The earlier five-mismatch report was an artifact of applying newline normalization to binary images, which is invalid.

| Artifact | Prior digest | Current raw digest | Bytes | Finding |
|---|---|---|---:|---|
| `validation/audit/346a67a10bde0265d468303af3935872dfcdfc234c5cc46d5c19f2f62b472122_page-2.png` | `346a67a10bde0265d468303af3935872dfcdfc234c5cc46d5c19f2f62b472122` | same | 169516 | Exact binary match |
| `validation/audit/56a1aa76c7e67425bb5ef5a8ae8b3129e66d8bee4e33258436b2cb33bc9cc240_page-1.png` | `56a1aa76c7e67425bb5ef5a8ae8b3129e66d8bee4e33258436b2cb33bc9cc240` | same | 129390 | Exact binary match |
| `validation/audit/7b1c2a999db178d694c4b0d6a1b52e576ac7d8c8dbd6e27d9a780de3021d0c4e_page-4.png` | `7b1c2a999db178d694c4b0d6a1b52e576ac7d8c8dbd6e27d9a780de3021d0c4e` | same | 179896 | Exact binary match |
| `validation/audit/a4cf2e274c98a7e790303e82b32a883fed627e08fbbf1c0dd20ad22ccd95fb95_page-3.png` | `a4cf2e274c98a7e790303e82b32a883fed627e08fbbf1c0dd20ad22ccd95fb95` | same | 102135 | Exact binary match |
| `validation/final_validation_results.csv` | `9494588fa341142fa98c34d0991c5b53321f0d28235a07ff9b45e4cd82e493b2` | `d4172d01804bed6466d9868007b70733a752e67a8e3531edd63e21c9aa35b3c9` | 765 prior / 748 current | CRLF-to-LF only; normalized bytes are identical. Prior digest matches the Git HEAD CRLF bytes. The current digest is canonical-LF. No CSV content change. |

The old raw-byte manifest and Windows `core.autocrlf=true` checkout can differ for text even when normalized text is identical. New manifests hash recognized text as canonical LF, preserve exact raw hashes for binary artifacts, and separately offer exact-byte mode. A clean copy materialized with LF text passes exact-byte verification. Git configuration was not changed.

## Validation

The Stage B structural validator reports 16/16 checks passed, zero errors, and inherited review warnings. The checksum unit/mutation suite and release-specific regression suite passed. The authoritative StageB_Final data was not expanded; V13 curation was made in a separate versioned copy.
