# StageB_Final integrity contract

## Artifact set

`manifests/SHA256SUMS.json` maps each StageB_Final artifact to a lowercase
SHA-256 digest. The manifest excludes itself and includes every other regular
file beneath this release. Symbolic links, absolute paths, parent traversal,
duplicate manifest paths, missing artifacts, and unlisted artifacts are
invalid.

The 708-entry `history/reconciliations/2026-11-02/SHA256SUMS.previous.json`
is preserved as the prior manifest. Four legitimate non-manifest files were
added after that snapshot: the reconciliation record, archived prior manifest,
this policy, and `scripts/manifest_integrity.py`. The current `StageB_Final`
manifest therefore has 712 unique entries, all resolving to files; there are
no missing or unlisted files.

## Hashing rules

Text files with recognized text suffixes are hashed after replacing CRLF
newline pairs with LF. This is the canonical-text digest and makes the
manifest stable across Git checkouts that apply `core.autocrlf`. Other files,
including PNG and PDF artifacts, are hashed as exact raw bytes; binary data is
never newline-normalized.

`scripts/manifest_integrity.py verify <release> --mode canonical` checks the
release contract used for a working-tree checkout. Its result separately
reports the number of raw-byte differences, so canonical text equivalence is
never presented as raw-byte equality. `--mode exact` requires raw-byte SHA-256
equality for every artifact. Use exact mode for a clean copy materialized with
canonical LF text bytes.

`scripts/manifest_integrity.py build <release>` writes a sorted manifest using
these rules, excludes the manifest itself, and does not rewrite any artifact.

## Reconciliation findings

- The test’s 708-entry expectation was stale. At the start of this repair, two
  legitimate reconciliation artifacts made the manifest count 710. The repair
  added this policy and its verifier, making the current manifest 712 entries.
  All 712 entries resolve exactly once; the manifest excludes itself.
- Four previously reported PNG mismatches were false positives from applying
  text newline normalization to binary files. Their exact SHA-256 digests
  match the manifest and their content-addressed filenames.
- `validation/final_validation_results.csv` was generated with CRLF line
  endings on the Windows checkout. Its prior digest matched those raw bytes,
  but differed from the canonical LF text digest used by the other text
  artifacts. The CSV content is retained; its manifest entry is changed to
  the LF-canonical digest.
- The prior manifest is retained unchanged as historical evidence.
