# CookRisk Stage B

Start with [the report](reports/stageB_report.md) and [the data-source audit](reports/stageB_dataset_source_audit.md).

This release is an initial literature evidence layer. It contains no risk score and does not validate clinical food-drug outcomes or the original retention measurements.

## Core tables

- `outputs/stageB_compound_mapping.csv`: all 198 nonblank CookRisk molecular groups, including uncertain identities.
- `outputs/stageB_food_drug_interactions.csv`: 33 traceable evidence records, including 3 null controls.
- `outputs/stageB_literature_evidence.csv`: study-level audit view.
- `outputs/stageB_stageA_linkage.csv`: group-level linkage/counts.
- `outputs/stageB_stageA_observation_links.csv`: original individual selected-model OOF predictions, conditions and provenance flags.
- `outputs/stageB_food_compounds.csv`: inherited dataset associations, with source-record pointers.
- `outputs/stageB_interaction_compounds.csv`: anchor/co-intervention relationships, without duplicating combination study results.
- `outputs/stageB_processing_evidence.csv`: separate processing evidence.
- `outputs/stageB_conflict_synthesis.csv`: differing study findings retained explicitly.
- `outputs/stageB_dataset_source_audit.csv`: DOI metadata screening; not validation of measured concentrations.
- `outputs/stageB_unassigned_observations.csv`: 221 original blank-ID rows, preserved intact.
- `outputs/stageB_search_log.csv` and `stageB_standardized_search_log.csv`: exact searches and coverage limits.
- `outputs/stageB_identity_audit.csv`, `stageB_duplicate_standardized_identities.csv`, `stageB_exclusions.csv`: identity/candidate decisions.
- `outputs/stageB_foods.csv`, `stageB_drugs.csv`: local entity dictionaries. Unverified external drug fields are blank.
- `outputs/stageB_summary.json`, `stageB_qc_results.json`, `stageB_identity_missingness.json`: machine-readable counts/QC.

## Rebuild

From the repository root, run the existing virtual environment Python:

```powershell
.\.venv\Scripts\python.exe stageB/scripts/build_mapping.py
.\.venv\Scripts\python.exe stageB/scripts/build_stageB.py
```

A separate machine can install `requirements-stageB.txt` and use its Python executable for these same two scripts. Immutable copies of the four supplied inputs are in `inputs/`. Paths and hashes are in `audit/input_manifest.json`. Raw identity/literature/DOI response caches are in `sources/`. The offline builder does not require network or a Stage A model.

Reports explain methodology, every CSV field, references, reproducibility and limitations. Source collection scripts use read-only public database APIs. Manual scientific extraction is in `scripts/curated_evidence.py`; automatic data retrieval is not automatic literature qualification. Missing evidence is not proof of no interaction.

## Material restrictions

96 groups remain uncertain; 23 mapped groups establish connectivity/name/CID rather than complete chemical form. Literature screening is bounded and not exhaustive. The source audit flags 145/208 DOIs for author/year discrepancy, and confirms an unrelated DOI on five Persin rows. 115 OOF rows differ from current master eligibility flags. Historical files were preserved. These upstream problems prevent scientifically supported retained-dose or clinical extrapolation from this release.
