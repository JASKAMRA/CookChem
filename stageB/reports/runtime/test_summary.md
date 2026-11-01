# Stage B automated test summary

## Final results

| Test layer | Result |
|---|---|
| New Stage B unittest suite | **13 passed, 0 failed** |
| Existing structural validator | **16/16 passed; 0 errors; 313 warnings** |
| Existing mutation suite | **12/12 detected; 0 missed** |
| Active-script safe runtime checks | **14/14 passed** |
| Release/archive integrity | **PASS** — 708 release checksums; 8,096 archive hashes |

## New test coverage

- Stable compound/evidence IDs; chemical identity cross-file fields; evidence-to-compound/probe/study references; bibliography links.
- Warning ledger uniqueness/status; source-audit and claim-support links; required files and core CSV schema headers.
- Manifest-listed file existence and SHA-256; read-only release-file hash check.
- Synthetic duplicate compound ID is detected by the archived validator in a temporary synthetic fixture.
- Synthetic missing value remains blank and distinct from an explicit synthetic zero. These are test-only values, not scientific observations.

## Regression notes

- New tests run with `stageB/.venv/Scripts/python.exe -m unittest discover -s stageB/tests -v`.
- Existing validation, mutation, and audit scripts were rerun under the isolated environment.
- All 14 active scripts have a safe runtime status. Three release-operation scripts received CLI and authoritative-target guard tests only; actual release creation/finalization/consolidation was intentionally not run.
- The first runtime attempt identified the missing XGBoost dependency; the Stage B requirements file was updated, then all affected scripts passed on rerun.
- No test changed Stage A or authoritative/historical release data.
