# `Retention_Final` target adjudication register

Status: **OPEN — no Stage C model prediction can be interpreted or applied until resolved.** This is an audit of project documentation and the stored target column; it does not amend the target or Stage A files. A target name, `log1p` transform, model metric, or literature convention is not an operational definition.

## What current files establish

- `stageA/scripts/run_stage_a.py` names `Retention_Final` as the numeric model target; `stageA/outputs/stageA_qa.json` confirms the column name, 1,124 rows, 197 molecular groups and model-selection metric. The script applies a `log1p` target transformation in the reported model workflow.
- `stageA/stageA_report.md`, `stageA/stageA_model_selection.md`, and `stageA/stageA_reproducibility.md` describe a retention target but do not define its unit, numerator, denominator, or whether the values are concentration-based or total-mass-based.
- `stageA/input/cookchem_molecular_retention_preprocessed.csv` has `Initial_Concentration`, `Initial_Unit`, `Initial_Unit_Standardized`, `Sample_Weight_g`, process fields, `Apparent_Increase`, and `Retention_Final`. Column co-occurrence does not prove a formula or measurement basis.
- The Stage C Phase 2 evidence review separately warns that concentration ratios are not total-mass retention where cooked yield is unavailable. Stage A target values must not inherit a stronger semantic claim without source verification.

## Questions that must be answered from the originating studies and row derivation

| ID | Exact question | Required evidence for closure |
|---|---|---|
| RF-01 | What exact equation generated `Retention_Final` for each source record? Is it `100 × cooked concentration / raw concentration`, a complement of reported percent loss, a ratio of total analyte masses, or another formula? | Original paper method/table plus the preprocessing derivation for each source family. |
| RF-02 | What does the scale mean: percent, unitless fraction, or a source-native index? Is the model output on the same scale after inverse `log1p`? | Source units and checked row-level calculation examples with explicit conversion. |
| RF-03 | What is the numerator and denominator for every source type? Is concentration per fresh mass, dry mass, cooked mass, extract mass, volume, or another basis? | Source table headers/footnotes and the dataset's unit-normalization logic. |
| RF-04 | Does a source measure matched raw and cooked material from the same batch/replicate, condition-level means, or separately sampled foods? What is the replicate and aggregation unit? | Study methods, table notes and the row-to-source mapping. |
| RF-05 | Is cooked yield or paired raw/cooked sample mass known, and is `Retention_Final` adjusted for yield? If not, what prevents describing a concentration ratio as total-mass retention? | Raw and cooked sample-weight/yield records or an explicit source statement that yield was not measured. |
| RF-06 | What moisture basis is used before and after cooking? Are fresh-weight and dry-weight measures mixed, and is moisture correction part of the target derivation? | Source methods and exact unit/basis crosswalk, including moisture determination. |
| RF-07 | For boiling, steeping, or other liquid-contact methods, does the target cover the edible solid only, retained liquid, discarded liquid, or the complete food-plus-liquid system? | Sample collection and assay preparation description for each cooking method. |
| RF-08 | Are reported analytes chemically identical before and after cooking, or can conversion, degradation products, epimerization, hydrolysis, oxidation, or assay cross-reactivity alter the measured signal? | Analyte definition, chromatographic/analytical method, and any transformation handling. |
| RF-09 | How are analytical recovery, extraction efficiency, calibration, LOD/LOQ, censored values, and source-specific assay differences handled? | Assay protocol, recovery/quality-control data, censoring rules and preprocessing lineage. |
| RF-10 | Why can a value exceed 100 for a given record: concentration change from water loss, improved extractability, formation, unit conversion, measurement error, or another cause? Which values above 100 are retained and how are they labeled? | Source-specific discussion and row-level review. Do not globally cap or relabel such values. |
| RF-11 | Are losses ever directly recorded as `Retention_Final`, or is every value converted to remaining fraction/percent? How are zeros, negative values, missing values, and sentinel values handled? | Exact source-to-target mapping, transformations and validation rules. |
| RF-12 | Does each target correspond to one compound, matrix, food state, cooking method and condition, or are records averaged across any of these dimensions? | Record-ID-to-paper/table/row map and group/aggregation specification. |
| RF-13 | Does `Initial_Unit_Standardized` describe only the raw concentration, or does it also define the cooked result's unit and denominator? | Preprocessing implementation plus source-specific paired unit definitions. |
| RF-14 | Is any target imputed, normalized across papers, clipped, winsorized, or manually corrected before modeling? Were these actions applied before the current staged CSV? | Full data lineage, change log, and source-to-staged-value reconciliation. |
| RF-15 | Is `Apparent_Increase` a source annotation or a deterministic flag computed from the same target formula? Does it affect target inclusion or model features? | Field provenance and preprocessing/code definition. |

## Closure record template

For each source family, record: source DOI/PMID; exact page/table/figure/method locator; source row and `Record_ID`; original value/unit; normalized value/unit; equation; sample size; raw/cooked mass and moisture basis; included/excluded liquid; assay and analyte identity; transformation/censoring; independent reviewer; date; unresolved exceptions. The reviewed contract must have a stable ID and SHA-256 and be included in any deployment package.

Do not infer answers from ranges, model performance, the target column name, or a different paper. If a source cannot answer a question, preserve the uncertainty and block any output semantics that depend on it.
