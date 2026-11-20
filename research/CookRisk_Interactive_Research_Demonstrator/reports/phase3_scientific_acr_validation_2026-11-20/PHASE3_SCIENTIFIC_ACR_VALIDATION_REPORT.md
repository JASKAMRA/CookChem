# CookRisk Phase 3 — Scientific ACR Validation Report

**Execution date:** 2026-11-20  
**Overall status:** CONDITIONAL  
**Scope:** Read-only ACR audit of Reconstruction; Batch021 only for approved shared-ID/shared-field comparison.

## Executive summary

Both approved hashes matched before analysis and after report generation. Reconstruction is 1016 × 43 and Batch021 is 1016 × 38; both schemas match the registry exactly. Both datasets have 1016 unique nonblank observation IDs, no repeated IDs, and no exact duplicate rows. Reconstruction ACR arithmetic was assessable for 1016/1,016 rows.

The registered target is **apparent concentration ratio (ACR)**, `100 × C_cooked / C_raw`. Independent Decimal arithmetic found 58 exact matches, 840 additional matches within 1E-9 percentage points, 118 strict mismatches above tolerance, and zero unassessable rows. Maximum absolute difference is 0.004822448472808542 percentage points. All 118 strict mismatches match after rounding to the displayed decimals of the stored target. This is consistent with display rounding but does not verify source-reported unrounded measurements. All strict mismatches are `verified_unchanged`; this audit does not justify changing values.

There are 20 unit labels, 15 basis labels, and 23 observed unit/basis combinations. Labels are heterogeneous and unharmonized. `analytical_definition` is missing for 451/1,016 (44.39%). A single unit/basis label per row does not independently establish raw/cooked source comparability. Total-mass retention is `NOT_ESTABLISHED` for 1016/1,016; ACR alone cannot establish it.

The global Tukey screen flags 97 high values (upper fence 215.568607%). 346 ratios are above 100%, 22 above 1,000%. These are not automatic errors or retention results; no rows were removed.

## Scope and preservation

Read the Phase 2 provenance report and decision register first. Verified both SHA-256 pins before record parsing. Reconstruction is the primary audit dataset; Batch021 is used only for schema/identity and shared-field comparison. Only this new isolated report directory was written. No dataset, application source, registry, historical output/model/metric/prediction/validation artifact, dependency or lockfile was changed. No build, training, model run, or Git operation occurred.

Stage B and restricted Stage C/D content were not accessed. `research/EXISTING_RESULTS_METRICS_CATALOG.csv` was not accessed. No broad repository scan was made. The `Retention_Final` source CSV was not read or hashed. No fallback dataset was used.

## Input identity, schema, and duplicates

| Dataset | Path | Expected and measured SHA-256 | Shape | Schema | IDs and duplicates | Status |
|---|---|---|---:|---|---|---|
| Reconstruction | `stageA/verified_concentration_ratio_reconstruction/final_verified_master_dataset.csv` | `f9391233a2d4231140d46aa58e864180eddb6f2c3a56b030df3f94ca25f083b0` | 1016 × 43 | PASS; missing fields 0; unexpected 0 | 1016 unique; blank 0; repeated-ID extra rows 0; exact duplicate extra rows 0 | PASS |
| Batch021 | `stageA/dataset_expansion_1000/batch_021/updated_master_dataset.csv` | `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8` | 1016 × 38 | PASS; missing fields 0; unexpected 0 | 1016 unique; blank 0; repeated-ID extra rows 0; exact duplicate extra rows 0 | PASS |

Registry column lists exactly match both CSV headers. CSV has no declared types; all Reconstruction fields have inferred lexical types in `DATA_QUALITY_AND_MISSINGNESS.csv`. Numeric-like columns: `raw_concentration, cooked_concentration, target_value_percent, Temperature_C, Cooking_Time_min, RDKit_Molecular_Weight, RDKit_LogP, RDKit_TPSA, RDKit_HBond_Donors, RDKit_HBond_Acceptors, RDKit_Rotatable_Bonds, RDKit_Aromatic_Rings, RDKit_Hydroxyl_Groups, raw_sd, cooked_sd, verified_concentration_ratio_percent, original_retention_final_provenance, calculated_ratio_percent, ratio_calculation_abs_difference`. Exact duplicates, repeated IDs, repeated `original_record_id`, and repeated DOI/compound/matrix/method context are reported separately; repeated context is not proof of duplication or independence.

## Methods and definitions

- Hash the full input bytes; verify before parsing and after writing.
- Parse stored decimal strings with Python `Decimal` at 60-digit precision; independently calculate `100 × cooked_concentration / raw_concentration`.
- An arithmetic row requires finite values and a positive raw denominator. Missing values are never zero. Negative, zero, nonnumeric, and non-finite values are checked explicitly.
- Compare target by exact decimal equality and absolute tolerance **1E-9 percentage points**. The 1e-9 pp threshold covers sub-display decimal/serialization precision while remaining far below measurement precision; it is not a scientific uncertainty allowance. Display-precision rounding is a separate diagnostic, not a relaxed pass.
- Group quartiles use linear interpolation. Outliers use global Tukey 1.5×IQR as screening only. Support bands `<5`, `5–9`, and `≥10` are descriptive counts, not evidence of inferential adequacy.

## ACR recalculation

Fields identified from registry/schema: `raw_concentration`, `cooked_concentration`, `concentration_unit`, `measurement_basis`, `target_value_percent`. Target name is `apparent_concentration_ratio_percent`, equation `100 * C_cooked / C_raw`, semantics `apparent concentration ratio; not total-mass retention`. All values are numeric and finite; raw denominators are positive; 0/1,016 rows are unassessable.

| Comparison | Exact decimal | Additional within 1E-9 pp | Mismatch above tolerance | Unassessable | Denominator |
|---|---:|---:|---:|---:|---:|
| `target_value_percent` | 58 | 840 | 118 | 0 | 1,016 |
| `verified_concentration_ratio_percent` | 58 | 840 | 118 | 0 | 1,016 |
| `calculated_ratio_percent` | 58 | 958 | 0 | 0 | 1,016 |

`verified_concentration_ratio_percent` equals `target_value_percent` in 1016/1,016 rows. Stored `calculated_ratio_percent` and stored absolute-difference values agree with independent arithmetic within tolerance for all 1,016. Strict target mismatches: 118; all match at the target’s displayed precision. Source rounding rules and unrounded source measurements were not reverified.

Representative largest strict differences:

| Observation | Stored target (%) | Independent ACR (%) | Difference (pp) | Target decimals |
|---|---:|---:|---:|---:|
| `REC-R243` | 78.54 | 78.5448224485 | 0.00482244847281 | 2 |
| `REC-R1053` | 98.76 | 98.7551867220 | 0.00481327800830 | 2 |
| `REC-R237` | 31.57 | 31.5747893258 | 0.00478932584270 | 2 |
| `REC-R232` | 178.2 | 178.195224719 | 0.00477528089888 | 1 |
| `REC-R1051` | 89.32 | 89.3153526971 | 0.00464730290456 | 2 |

## Data quality and missingness

| Field | Missing / 1,016 | Other checks |
|---|---:|---|
| `raw_concentration` | 0 | nonnumeric 0; non-finite 0; zero 0; negative 0 |
| `cooked_concentration` | 0 | nonnumeric 0; non-finite 0; zero 2; negative 0 |
| `target_value_percent` | 0 | nonnumeric/non-finite 0; unique values 967 |
| `concentration_unit` | 0 | 20 distinct labels; unharmonized |
| `measurement_basis` | 0 | 15 labels; 6 contain “unspecified” |
| `analytical_definition` | 451 (44.39%) | 565 values in 24 descriptions |
| `reported_replicate_design` | 439 (43.21%) | 577 recorded |
| `raw_sd` / `cooked_sd` | 604 / 598 | Missing in many records |
| `source_locator` / `doi` | 0 / 0 | All rows have values; papers not reopened |

Cooked zero values: 2; their true-zero versus detection-limit meaning is unknown. Exact duplicate full rows: 0 extra; repeated observation IDs: 0 extra; repeated `original_record_id`: 0 extra in 0 groups; repeated DOI/compound/matrix/method contexts: 232 extra in 82 contexts. Context repeats are related observations, not proven duplicates or independent replicates.

## Units and measurement compatibility

There are 20 unit labels, 15 measurement-basis labels and 23 observed text pairs; all 1,016 records have both labels. 6 basis labels contain “unspecified”. Labels include heterogeneous mass/molar forms and fresh/dry/other bases; no conversions were applied. The registry says they are source-specific and unharmonized.

Each row has one concentration-unit and one basis field, not separate raw and cooked unit fields. The ratio is computed following that shared row label, but source-level confirmation that paired raw/cooked values share analyte, unit, basis, extraction and assay is not established for every source. Analytical-definition text is missing in 451 rows and primary/supplementary tables were not reopened.

`cooked_yield_status`: NOT_REPORTED=638; TRUE_RETENTION_REPORTED_BUT_NOT_USED_FOR_APPARENT_RATIO=28; NOT_REPORTED_OR_NOT_COMPATIBLE=338; weight loss reported separately; not used for target=12. `total_mass_retention_status` is `NOT_ESTABLISHED` in 1016/1,016. No paired food-mass columns exist. ACR alone does not yield total-mass retention.

## Group coverage and distributions

Every observed category for `food_matrix`, `compound_class`, `compound`, and `cooking_method_normalized` is included in the group CSV with counts, DOI counts, ACR distribution, and support band.

| Group field | Categories | Missing category rows | Sparse <5 | Limited 5–9 | ≥10 (descriptive only) |
|---|---:|---:|---:|---:|---:|
| `food_matrix` | 66 | 0 | 11 | 31 | 24 |
| `compound_class` | 10 | 0 | 0 | 1 | 9 |
| `compound` | 51 | 0 | 18 | 4 | 29 |
| `cooking_method_normalized` | 41 | 0 | 8 | 14 | 19 |

The 1016 observations span 32 DOI families. Calculated ACR summary: min 0e+1%; Q1 56.619173%; median 88.377111%; Q3 120.198947%; max 6536.36363636%. Rows may share study source and are not necessarily independent. The ≥10 count band does not establish statistical sufficiency, and comparisons are not causal.

## Outlier review

Global Tukey fences are -38.750487% to 215.568607%. Flags: 0 low, 97 high. ACR >100%: 346; >1,000%: 22; cooked concentration zero: 2. These are review screens, not error thresholds.

| Observation | ACR (%) | Raw → cooked | Unit / basis | Assessment |
|---|---:|---|---|---|
| `LIT-ACITO2024-Commercial_RSP-CAFFEIC_ACID-PRESSURE_COOKING` | 6536.363636 | 0.44 → 28.76 | mg/kg fresh matter / fresh matter (FM) | Potential extreme; source review needed; no error established. |
| `LIT-KAYAHAN2021-ARTICHOKE_BAYRAMPASA_RECEPTACLE-CHLOROGENIC_ACID-MICROWAVE` | 5832.972441 | 1016.0 → 59263.0 | mg/kg / as reported (basis unspecified) | Potential extreme; source review needed; no error established. |
| `LIT-ACITO2024-Commercial_RSP-CAFFEIC_ACID-BOILING` | 4522.727273 | 0.44 → 19.9 | mg/kg fresh matter / fresh matter (FM) | Potential extreme; source review needed; no error established. |
| `LIT-KAYAHAN2021-ARTICHOKE_BAYRAMPASA_RECEPTACLE-CHLOROGENIC_ACID-BOILING` | 3946.456693 | 1016.0 → 40096.0 | mg/kg / as reported (basis unspecified) | Potential extreme; source review needed; no error established. |
| `LIT-OZBEK2024-TRACHYSTEMON_LEAF_STEM-CAFFEIC_ACID-STIR-FRYING-15MIN` | 3512.147161 | 31.53 → 1107.38 | mg/100 g dry weight / dry weight (DW) | Potential extreme; source review needed; no error established. |

No outlier was removed or altered. High values may be valid or may reflect denominator, basis, assay, or source issues. The outlier CSV preserves identifiers and relevant context.

## Reconstruction versus Batch021

Shared observation IDs: 1016/1,016; unmatched IDs are 0 in either direction. Shared columns: 38; Reconstruction-only columns: `verified_concentration_ratio_percent, target_verification_status, original_retention_final_provenance, calculated_ratio_percent, ratio_calculation_abs_difference`; Batch021-only: `none`. No merge was performed. Only `target_value_percent` differs: 15 serialized cells, maximum numeric difference 2.842170943040401e-14 percentage points. This is consistent with floating-point serialization; the other 37 shared fields match exactly. Dataset roles remain separate.

## Scientific interpretation

1. **Measures:** apparent change in concentration for a recorded analyte/food pair, `100 × C_cooked / C_raw`.
2. **Does not measure:** total-mass retention, nutrient preservation/loss, bioavailability, causal cooking effect, or a harmonized cross-study endpoint by itself.
3. **Can ACR alone establish total-mass retention?** No. Compatible paired food masses or validated yield are needed with compatible concentrations.
4. **Raw/cooked comparability?** Stored labels exist per row, but source-level paired measurement compatibility was not confirmed; not established across all sources.
5. **Units/bases sufficiently documented?** Populated, but heterogeneous/unharmonized; 6 explicitly unspecified-basis labels and 451 missing analytical definitions prevent broad harmonization.
6. **Groups with more descriptive support (n≥10):** 24/66 matrices; 29/51 compounds; 19/41 methods; 9/10 compound classes. This is not inferential adequacy.
7. **Unsupported claims:** total-mass retention from ACR; causation; nutrient preservation/loss; broad cross-study rankings without harmonization; declaring outliers erroneous without source review; canonical or independently validated status.
8. **Evidence needed:** primary-source paired values, precision, unit/basis, assay/analyte definition, detection limits and replicates; paired food masses/validated yield for total-mass retention; independent source replication for generalization.

## Status summary

| Check | Status | Reason |
|---|---|---|
| Approved hashes/dimensions | PASS | Both expected hashes and shapes match, rechecked after output. |
| Schema/observation IDs | PASS | Exact registry columns; unique nonblank IDs; no exact duplicate rows. |
| ACR arithmetic | PASS | All 1,016 rows assessable; stored calculation agrees within tolerance. |
| Stored target comparison | CONDITIONAL | 118 strict differences; all match at displayed precision, but raw source precision was not verified. |
| Source-level raw/cooked compatibility | BLOCKED | Primary sources/assays not checked; a single row label is insufficient confirmation. |
| Data quality/duplicates | PASS | Counts explicit; no missing concentration/target, duplicate IDs, or exact duplicate rows; metadata gaps remain. |
| Group distributions | CONDITIONAL | Descriptive only; sparse categories and DOI clustering limit inference. |
| Outlier interpretation | CONDITIONAL | Flags preserved; source review not performed; no rows removed. |
| Total-mass retention | BLOCKED | Not established for rows; no paired masses and ACR is not mass retention. |

## Limitations and checks not completed

- Primary papers, supplementary tables, and lab methods were not reopened; source locators were not used for adjudication.
- No unit harmonization, causal analysis, cross-source hypothesis test, or model evaluation was run.
- True-zero versus detection-limit semantics for two cooked zeros remain unknown.
- 118 strict target differences match target display precision, but source rounding rules and underlying unrounded values were not independently verified.
- Tukey flags are not confirmed errors.
- Historical `Retention_Final` source data were excluded; its meaning remains unresolved.
- No application tests were run because application code was unchanged; verification covered data, hashes, schema, calculations, and report integrity.

## Conclusion

The approved Reconstruction passes current file integrity, schema, ID, and arithmetic checks. Stored targets agree with the independent ratios at their displayed precision; strict numeric comparisons retain 118 differences and no source correction is justified. The evidence supports descriptive ACR exploration with unit, basis, source, and group-support limitations. It does not support total-mass retention, causal cooking effects, broad cross-study comparability, or independent scientific validation. Preserve all rows and historical evidence.
