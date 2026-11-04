# StageB V20 hashing policy decision packet

Date: 2026-11-04  
Status: **OWNER DECISION REQUIRED — no release files changed**

## Question

Which artifact hashing contract governs `StageB_V20_20261103`: exact raw bytes, or canonicalized text (CRLF converted to LF) plus exact binary bytes?

## Evidence for exact raw-byte hashing

- The frozen `scripts/build_v20_manifest.py` computes SHA-256 directly from `p.read_bytes()` for every artifact.
- `history/reconciliations/2026-11-02/RECONCILIATION.md` says the manifest was generated over every release file; it does not describe text normalization.
- `history/reconciliations/2026-11-02/SHA256SUMS.previous.json` records the same raw hash for the affected CSV.
- `validation/clean_copy_comparison.csv` records the identical source and clean-copy hash for that CSV.
- `tests/test_v19_batch02.py::test_warning_ledger_and_audit_are_in_exact_manifest` explicitly validates V20 with `mode="exact"` and checks raw-byte hashes.
- Full current package check in exact mode: **839/839 entries match**, no missing or unexpected files.

## Conflicting evidence for canonical-text hashing

- `scripts/manifest_integrity.py` module documentation and default `verify_manifest(..., mode="canonical")` describe CRLF-to-LF normalization for recognized text files.
- `documentation/INTEGRITY_POLICY.md` says the manifest contains canonical-text hashes and identifies `validation/final_validation_results.csv` as reconciled to the LF-canonical digest.
- Yet the current manifest contains that CSV's raw CRLF digest, not the LF-canonical digest.

## Exact discrepancy and scope

Only `validation/final_validation_results.csv` differs under canonical mode. It has **17 CRLF pairs**. Its raw SHA-256 is `9494588fa341142fa98c34d0991c5b53321f0d28235a07ff9b45e4cd82e493b2`, matching the current manifest entry. Its LF-normalized SHA-256 is `d4172d01804bed6466d9868007b70733a752e67a8e3531edd63e21c9aa35b3c9`. All other **838** listed artifacts match both modes. Canonical verification reports **0 raw-byte mismatches**, confirming the sole finding is newline normalization.

The same result is reproduced in an isolated temporary copy by `stageB/tests/test_v20_manifest_policy.py`; the test neither writes to nor regenerates the frozen manifest.

## Alternatives for the owner

1. **Exact-byte contract for this V20 package.** Keep its current bytes, manifest and tested mode. In a separately versioned successor or documentation amendment, explicitly identify exact-byte policy and avoid implying that this release was canonical-text-normalized.
2. **Canonical-text contract for future successor packages.** Keep V20 unchanged as historical evidence. In a separately versioned successor, canonicalize text inputs before manifest creation, regenerate the successor manifest there, and test both canonical checkout and exact clean-copy expectations.

The current evidence establishes what the V20 manifest builder and its explicit test did (exact bytes), but conflicts with the release policy prose and verifier default. A maintainer/release owner must choose which rule governs future package construction. No rule is silently declared authoritative here. Do not alter V20's verifier, artifacts or manifest to resolve this packet.

## Validation

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s stageB/tests -v` — **48 passed**. The two new tests cover exact-vs-canonical scope and the isolated line-ending reproduction.
- `python3 stageC/releases/Phase1B-v1.3.2/verify_release.py` — **PASS, 1,324 artifacts**.
- `python3 stageC/scripts/build_phase2_v0_3_1_release.py --verify` — **PASS, 50 artifacts**.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s stageC/tests -p 'test_app_api.py' -v` — **10 passed**.
- Full Stage C: **249 tests, 2 errors, 5 skipped**. The errors are the frozen Phase4-v0.1.2 integrity rejection and unavailable `jsonschema` import.
- Full Stage D: **63 passed, 6 skipped** because `jsonschema` is unavailable.
- No frozen release files changed; V20 and V13 release trees contain no `__pycache__` files after the Stage B test run. `git diff --check` passes.
