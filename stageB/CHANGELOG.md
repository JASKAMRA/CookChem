# Stage B change log

## Repository organization pass

- Moved the root Stage B versioned scripts into `archive/scripts/`, preserving their original filenames and bytes: V11/V12 builders, finalizers, mutation tests, the V11 local audit, and the former final-package consolidation, validation, and mutation utilities.
- Added version-independent active entry points in `scripts/`: `build.py`, `finalize.py`, `consolidate.py`, `validate.py`, `mutation_tests.py`, and `audit.py`. The V12 build/finalization and consolidated-release validation logic were selected after inspecting their interfaces and release lineage. Build/finalize/consolidate require explicit staging paths and guard the authoritative release.
- Moved the unique `freeze_stageb_candidate.py` from the accidentally nested `scripts/scripts/` folder to `scripts/`. Preserved the seven byte-identical nested copies under `archive/scripts/duplicates/`; their SHA-256 equality was checked before relocation.
- Copied all available V2–V12 release folders, expansion folders, V6 restart/sandbox folders, and legacy Stage B workspace materials from the previous Documents location into `archive/releases/`; originals remain unchanged. Copied the existing `StageB_Final` release into `release/StageB_Final/` without rebuilding it.
- Added before/after file inventories and release check results under `validation/`.
- Relocating `freeze_stageb_candidate.py` one directory level aligned its existing script-relative root calculation; the other model scripts already resolve shared Stage A imports from the repository root. Static import-path inspection resolved every internal Stage B/Stage A module. Runtime model imports could not be exercised in this environment because NumPy, pandas, scikit-learn, CatBoost, and joblib are not installed.
- Added Stage B dependency and usage documentation. Shared root files and Stage A were left in place.
- No scientific records, identifiers, classifications, numerical evidence, warnings, model results, or Stage A files were intentionally changed.

## Validation notes

Results of manifest verification, structural validation, mutation tests, path/import checks, and archive comparisons are recorded in `validation/`. This organization pass does not upgrade the scientific review status of the source release.
