# Authoritative Stage B release integrity report

## Result

**PASS** — independent hashes were recalculated after the validator, mutation suite, and new readiness tests. The frozen manifest SHA-256 before and after is `349021670220b89a6b147d82a1b483f6a741d0962a7dde7e883c3e661a1bfe4e` and matches.

| Check | Before baseline | After audit |
|---|---:|---:|
| Manifest entries | 708 | 708 |
| Missing files | 0 | 0 |
| Checksum mismatches | 0 | 0 |
| Compound anchors | 119 | 119 |
| Interaction evidence | 286 | 286 |
| Probe labels | 127 | 127 |
| Warning ledger rows | 55 | 55 |

- All 8,096 archived files matched the recorded SHA-256 values.
- All 18 relocated files matched their pre-move SHA-256 values.
- The release contains 709 files: the manifest-listed payload plus `SHA256SUMS.json` itself, which is not self-hashed.
- All 144 release CSVs parsed with consistent row widths. No exact duplicates or duplicate nonblank IDs were found in the compound, interaction-evidence, bibliography, or warning-ledger tables.
- The release does not package machine-readable JSON Schemas; schema checks here use the existing structural validator, documented field definitions, required CSV headers, foreign-key checks, and consistent CSV row widths.
- Required outputs and documentation are present; structural validation passed 16/16 checks with 0 errors.
- No Stage A or authoritative/historical Stage B release content was written during this audit. Runtime model writers used a disposable copy.

Machine-readable comparison: [`integrity_file_comparison.csv`](integrity_file_comparison.csv) (one baseline/after SHA-256 comparison per manifest entry), [`integrity_after.json`](integrity_after.json), and [`integrity_baseline.json`](integrity_baseline.json).
