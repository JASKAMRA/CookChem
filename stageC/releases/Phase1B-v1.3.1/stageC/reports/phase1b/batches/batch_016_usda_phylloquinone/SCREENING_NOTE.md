# Batch 016 — USDA phylloquinone screening

## Candidate result

- Target: Phylloquinone (`CHEM-PUBCHEM-5284607`), currently uncovered in the Stage C accepted mapping table.
- Food: raw spinach (*Spinacia oleracea*), ordinary food.
- USDA FoodData Central SR Legacy record: FDC 168462 (NDB 11457).
- Reported nutrient: Vitamin K (phylloquinone), 483 µg/100 g; equivalent to 4.83 mg/kg.
- Official record: https://fdc.nal.usda.gov/fdc-app.html#/food-details/168462/nutrients
- USDA National Agricultural Library Vitamin K fact sheet cross-reports 144.9 µg per one-cup measure for raw spinach: https://www.nal.usda.gov/sites/default/files/page-files/Vitamin%20K.pdf

The nutrient is explicitly phylloquinone, so it is chemically more specific than a generic vitamin K total. The SR Legacy summary does not expose underlying replicate count or analytical spread in the inspected record. Preserve this limitation if the candidate is accepted.

## Ingestion status: pending release integrity

The food-composition row has not been ingested. `stageC/scripts/build_compound_mapping.py` currently fails in the read-only Stage B connector because files in `stageB/release/StageB_Final` do not match its `manifests/SHA256SUMS.json`. Stage C's saved snapshot has the manifest hashes recorded at import time, but it represents the earlier Stage B snapshot. Do not bypass the connector or change the protected Stage B package to force ingestion.

## Verification needed before acceptance

1. Restore/rebuild the authoritative Stage B release so its manifest and package agree, or obtain an authorized current release manifest.
2. Re-run exact-name mapping against the verified Stage B compound registry.
3. Ingest the one-row candidate, rebuild mapping, refresh coverage and run Phase 1 validation.
4. If accepted, increment the distinct covered compound count by one; do not count multiple foods/records as multiple compounds.

## Additional exact nutrient candidate from the same USDA food record

- Target: Ascorbic acid (`CHEM-PUBCHEM-54670067`), currently uncovered in the Stage C accepted mapping table.
- Food: raw spinach (*Spinacia oleracea*), ordinary food; FDC 168462 / NDB 11457.
- USDA nutrient name: “Vitamin C, total ascorbic acid”; reported 28.1 mg/100 g (28.1 mg/kg).
- Candidate source: https://fdc.nal.usda.gov/fdc-app.html#/food-details/168462/nutrients

This is a source-level candidate, not yet ingested. The release-integrity condition above applies. Retain USDA's nutrient name verbatim and review whether the Stage B ascorbic-acid identity scope is compatible with FDC's total-ascorbic-acid value before acceptance.


## Current disposition (2026-11-02)
The exact USDA phylloquinone row was promoted from Batch 023 into active Stage C coverage after release reconciliation. The total-vitamin-C candidate remains held.
