# Batch 077 — verified food records promoted to active coverage

## Promotion

After Stage B release reconciliation and exact ID/CID/InChIKey checks, 33 food records were promoted from existing candidate batches into the active Stage C food-composition dataset:

| Compound | Records added | Source batch | Basis preserved |
|---|---:|---|---|
| Folic acid | 12 | Batch 017 | As-sold cereal, µg/100 g |
| Allyl isothiocyanate | 8 | Batch 073 | Prepared mustard, fresh-weight basis |
| Oleuropein | 7 | Batch 019 | Freeze-dried olive fruit, mg/kg |
| Thymoquinone | 5 | Batch 020 | Commercial oil, mg/100 g |
| Phylloquinone | 1 | Batch 023 | Raw spinach, µg/100 g |

The values remain sample-specific and retain their original food state, basis, source locator, sample size, and uncertainty notes. The 12 folic-acid records are four regional composites per anonymized cereal product. The eight mustard and five oil records each describe one retail product with analytical replicates; these do not represent population-level market means. Oleuropein values remain on the study's freeze-dried basis. The USDA spinach phylloquinone record is retained as one database observation without implying lot-level precision.

Thymoquinone oil sample 6 was excluded because the ingredient list contains rosemary extract and tocopherols. The USDA total-vitamin-C spinach row remains held because its analyte scope is not an exact match to reduced ascorbic acid.

## Identity and release provenance

All five promoted target IDs, PubChem CIDs, and InChIKeys resolve against the reconciled, checksum-verified StageB_Final. The active Stage C snapshot is `stage_b_snapshot_20261102`; its import manifest records the release SHA-256. The prior snapshot was preserved separately.

The persistent combined ingestion input is `stageC/reports/ingestion/phase1b_food_composition_import_2026-11-02.csv`; the official ingestion manifest and mapping report record the resulting active dataset.
