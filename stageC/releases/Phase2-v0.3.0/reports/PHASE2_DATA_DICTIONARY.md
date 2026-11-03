# Phase 2 Data Dictionary

## Core records

| File | Row meaning | Key fields |
|---|---|---|
| `stageC/phase2/data/observed_cooking_pairs.csv` | One raw control vs one cooking-treatment group mean for one analyte | `pair_id`, source record, compound/matrix, treatment, conditions, raw/cooked mean and SD, unit, n, ratio, DOI, source locator, limitation |
| `stageC/reports/phase2/source_pair_audit_2026-11-03.csv` | One independently audited source observation; 117 rows | All source-pair fields plus table verification, source state/basis, cooking protocol, replicate/statistic, extraction/assay, recalculated ratio, URL, audit status/error codes |
| `stageC/phase2/data/observed_retention_evidence.csv` | One Stage B cooking/brewing retention item; four rows | Processing ID, compound/matrix, reported loss, derived retention interval where quantitative, evidence type, source, limitation |
| `stageC/reports/phase2/retention_compatibility_matrix_2026-11-03.csv` | One potential Phase1B food × retention-evidence match; 22 rows | Food/source IDs, context class, state, identities, unit/basis, evidence quality, disposition and blockers |
| `stageC/reports/phase2/source_condition_level_retention_candidates_2026-11-03.csv` | One potential Phase1B record × distinct primary cooking scenario; 63 rows | Food and compound IDs, matrix, method/time/pressure, source raw/cooked group means and SDs, apparent ratio, source locator, calculation status |
| `stageC/reports/phase2/identity_resolution_audit_2026-11-03.csv` | One of the 45 identity candidates | Original Stage A/B identifiers, names/SMILES/CIDs, explicit outcome, CID concordance, Stage A resolution state, review reason |
| `stageC/releases/Phase2-v0.1.0/data/cooked_concentration_estimates.csv` | Cooked estimate schema; zero data rows | A future estimate would require input/source IDs, retention, calculation, uncertainty, output unit/basis, warnings, validation state |

## Ratio and measurement fields

- `raw_mean_value`, `cooked_mean_value`: table group means; do not imply paired replicate observations.
- `raw_sd_value`, `cooked_sd_value`: source SDs; do not treat as SEM or confidence interval.
- `replicates_n`: source biological/experimental n; pumpkin paper has three biological replicates with analytical triplicates.
- `concentration_ratio_percent`: `100 × cooked group mean / raw group mean`, rounded in the intake; independent precision is in the source audit.
- `measurement_unit`: source intake's unit field. For the 33 turmeric rows, source audit flags the legacy “mg/g fresh rhizome” text as over-specific: source says mg/g plant material and does not define cooked denominator explicitly.
- `source_measurement_basis`: source paper's stated basis, not inferred from food state. Pumpkin tables use DW; turmeric table reports mg/g plant material with denominator limitation.
- `food_use_classification`: ordinary food, food ingredient, or prepared beverage. Context classes remain separate.
- `disposition`: accepted, rejected for numeric output, or unresolved; no blank or unsupported value is imputed as zero.
