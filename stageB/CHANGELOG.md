# Stage B change log

## Repository organization pass

- Moved the root Stage B versioned scripts into `archive/scripts/`, preserving their original filenames and bytes: V11/V12 builders, finalizers, mutation tests, the V11 local audit, and the former final-package consolidation, validation, and mutation utilities.
- Added version-independent active entry points in `scripts/`: `build.py`, `finalize.py`, `consolidate.py`, `validate.py`, `mutation_tests.py`, and `audit.py`. The V12 build/finalization and consolidated-release validation logic were selected after inspecting their interfaces and release lineage. Build/finalize/consolidate require explicit staging paths and guard the authoritative release.
- Moved the unique `freeze_stageb_candidate.py` from the accidentally nested `scripts/scripts/` folder to `scripts/`. Preserved the seven byte-identical nested copies under `archive/scripts/duplicates/`; their SHA-256 equality was checked before relocation.
- Preserved available V2–V12 release folders, expansion folders, V6 restart/sandbox folders, and legacy Stage B workspace materials under `archive/releases/`. Copied the existing `StageB_Final` release into `release/StageB_Final/` without rebuilding it.
- Added before/after file inventories and release check results under `validation/`.
- Relocating `freeze_stageb_candidate.py` one directory level aligned its existing script-relative root calculation; the other model scripts already resolve shared Stage A imports from the repository root. Static import-path inspection resolved every internal Stage B/Stage A module. Runtime model imports could not be exercised in this environment because NumPy, pandas, scikit-learn, CatBoost, and joblib are not installed.
- Added Stage B dependency and usage documentation. Shared root files and Stage A were left in place.
- No scientific records, identifiers, classifications, numerical evidence, warnings, model results, or Stage A files were intentionally changed.

## Validation notes

Results of manifest verification, structural validation, mutation tests, path/import checks, and archive comparisons are recorded in `validation/`. This organization pass does not upgrade the scientific review status of the source release.

## Final verification refresh (2026-11-01)

- Re-ran the active evidence workflow from the repository root: validation passed all 16 checks with 313 existing warnings and zero errors; mutation testing detected all 12 injected integrity failures; the 708-entry `StageB_Final` checksum manifest had no mismatches.
- Confirmed the Stage B release counts remain 119 compound anchors, 286 evidence records, 127 probe labels, and 55 warning rows.
- Confirmed that no Stage B-specific Python scripts remain at the repository root. Kept `reports/run_dataset_forensic_audit.py` in place because it audits the shared dataset and uses project-wide `data/` and `reports/` paths.
- Removed an unused, empty root-level `food_drug_stageB/` directory and refreshed the baseline inventory classifications and destination paths. Added three preserved nested historical inventory files to the complete Stage B after-inventory; generated inventory files are excluded to avoid self-referential checksums.
- Made the active build/finalize/consolidate command descriptions version-neutral and changed the audit report to store a repository-relative release path.
- No scientific pipeline logic, identifiers, values, classifications, warnings, Stage A files, or authoritative release files were changed in this refresh.

## Runtime readiness audit (2026-11-01)

- Added an isolated Stage B virtual environment and installed the declared model dependencies without changing global Python packages.
- Added `xgboost==3.4.1` to `requirements-stageB.txt` after runtime testing showed that Stage B imports the Stage A module, which imports XGBoost at module load. All 14 active scripts then passed their appropriate safe runtime checks; the three release-operation wrappers were exercised through help and authoritative-target refusal checks only.
- Added 13 read-only release-readiness tests with explicitly synthetic fixtures, plus script-by-script runtime, dependency, integrity, warning-classification, Stage C compatibility, and test-summary reports.
- Independently rehashed all 708 authoritative release entries, compared before/after record counts, and verified 8,096 historical archive files and 18 relocated files against recorded SHA-256 values.
- Classified the 313 validation warnings without altering the 55-row release warning ledger. The resulting Stage C decision is READY_WITH_WARNINGS; the report documents the conditions and the absence of raw-food concentration data.
