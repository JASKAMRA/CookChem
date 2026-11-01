# CookRisk Stage B Runtime Readiness

Audit date: 2026-11-01. Stage B verification only; no Stage C code or scientific datasets were created.

## Explicit Stage C readiness decision

### READY_WITH_WARNINGS

Stage C may begin controlled integration of Stage B identity and evidence metadata. Structural integrity, safe script runtime, automated tests, and checksums passed. Keep warning and verification fields attached. Stage B does **not** provide raw-food concentrations, so it cannot by itself support dietary exposure calculations. Review the 13 HIGH unit/statistic flags before using affected outcomes quantitatively; retain the identity and food-occurrence review flags.

## A. Environment

- Python **3.14.7**, isolated environment `stageB/.venv/Scripts/python.exe`.
- Stage B declares no Python version. Stage A records Python 3.12.14; only Python 3.14.7 was available.
- Direct packages installed in the venv: `numpy==2.5.4`, `pandas==3.1.0`, `scikit-learn==1.9.1`, `catboost==1.2.10`, `joblib==1.6.0`, `xgboost==3.4.1`.
- `pip check` passed; no resolver conflicts. Stage A records NumPy 2.5.3 and pandas 3.0.6, so exact numerical reproducibility against those versions is not established. No global package was changed.

Details: [`dependency_report.md`](../reports/runtime/dependency_report.md).

## B. Script runtime results

- Active scripts: **14**; safe checks passed: **14**; failed: **0**; blocked: **0**; scripts without a safe check: **0**. The full build, finalization, and consolidation operations were not run (**3 operations**); their authoritative-target guards were tested.
- Modeling and output writers ran on a disposable copy of Stage A inputs and existing Stage B outputs.
- Build, finalize, and consolidate passed CLI and authoritative-release refusal checks. Actual release operations were deliberately not run.

Details: [`script_runtime_report.md`](../reports/runtime/script_runtime_report.md), including inputs, outputs, safety notes, exit codes, durations, stdout, and stderr.

## C. Release integrity

- `StageB_Final`: **PASS**; 708 manifest entries independently checked; 0 missing files; 0 mismatches.
- Before/after counts unchanged: 119 compounds, 286 evidence rows, 127 probe labels, 55 warning-ledger rows.
- Historical archive hashes: 8,096/8,096 matched; relocated files 18/18 matched.
- All 144 release CSV files had consistent row widths; no exact duplicate rows or duplicate nonblank IDs in core tables. No Stage A or release content changed.

Details: [`integrity_report.md`](../reports/runtime/integrity_report.md).

## D. Warning classification

- Validator warnings: **313**, all classified: critical **0**, high **13**, medium **300**, low **0**, informational **0**, not applicable **0**.
- The 13 HIGH items need manual unit/statistic verification before numeric use. The 300 MEDIUM items indicate missing source-audit rows or blank outcome descriptions.
- The distinct release warning ledger remains unchanged: 55 records (39 unresolved, 13 partially resolved, 2 not applicable, 1 resolved).

Details and the complete 313-row file: [`warning_classification.md`](../reports/runtime/warning_classification.md) and [`warning_classification.csv`](../reports/runtime/warning_classification.csv).

## E. Automated testing

- New unit/integration checks: **13 passed, 0 failed**.
- Existing validator: **16/16** checks passed, 0 errors, 313 warnings.
- Existing mutation tests: **12/12** detected, 0 missed.
- Independent release/archive integrity passed.

Details: [`test_summary.md`](../reports/runtime/test_summary.md).

## F. Stage C compatibility

- Stable Compound_ID, Evidence_ID, and Study_ID fields are available and unique. The 119 registry IDs match the identity-audit IDs.
- PubChem CID, SMILES, InChI, InChIKey, identity source, and status are present for all compounds; **19** identity rows still need manual chemical review.
- Food context has 119 rows; **105** inherited occurrence reviews remain incomplete and **17** rows describe supplement/medicinal botanicals.
- Claim-support coverage is 286/286; separate source-audit coverage is 76/286.
- No raw-food concentration dataset is included. Three cooking-retention records are a distinct data type, not food composition.
- Stage C can consume identity/evidence/provenance metadata under the stated conditions, but exposure calculation requires separately verified food-composition measurements.

Details: [`stage_c_compatibility.md`](../reports/runtime/stage_c_compatibility.md).

## Conditions for Stage C

1. Preserve every identity, source-verification, food-context, and warning status.
2. Review the 13 HIGH numeric/unit flags before using those outcomes as numbers; review the 19 pending identity records before exact structure mapping.
3. Preserve the 105 inherited food-occurrence review gaps and keep 17 supplement/medicinal contexts separate.
4. Obtain a separately sourced raw-food concentration dataset before calculating exposure.
5. Do not merge interaction evidence, cooking-retention findings, and food-composition measurements into one evidence type.
