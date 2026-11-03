# Batch 109 — V20 food measurement recheck

## Decision

Two previously uncovered, identity-complete Stage B compounds receive source-backed quantitative ordinary-food/food-ingredient measurements in the isolated StageB_V20_20261103 connector probe: **vanillic acid** and **sinensetin**. All source values, units, study sample basis, analytical uncertainty, and food-use context are retained in `accepted_measurements.csv`. Reported mean concentrations are numeric; source SD values remain in `uncertainty_notes`.

- **Vanillic acid, rosehip fruit:** 76.1 ± 1.6 µg/g FW, Table 6 of the 2025 validated HPLC-DAD study. The fruit is an edible food matrix.
- **Sinensetin, clementine peel:** 15 Table 7 measurements, 19.56–37.99 mg/100 g FW. The authors analyzed fresh peels via solvent-extraction procedures and propose reusing peel extracts to enrich a clementine functional drink. Records therefore use `food ingredient`, retain the fresh-peel denominator, and explicitly state that these are experimental peel-extract/starting-peel values, not retail extract or finished-juice concentrations.

The source-confirmed sinensetin analyte is matched against its own Stage B CID and InChIKey; vanillic acid likewise maps by exact CID/name in the V20 registry. No analogues, conversions from extracts to finished beverages, or unreported concentrations were inferred.

## Validation and scope

The isolated V20 probe ingested **562 food records** and rebuilt **562 mappings**. Phase 1 validation **PASS**: 143 compounds, **113 identity-complete quantitative compounds**, 13 pending identities, 9 legacy mapping rows blocked by identity review, zero food/mapping errors, and zero Stage B snapshot changes. This is a successor-probe result only. The active project root still uses StageB_FINALIZED and has not received these records; no release package was created by this batch. Phase1-v1.3.0 remains unchanged.

## Primary sources

1. Ștefănescu et al. “Simultaneous Determination of 16 Phenolic Compounds in Edible Fruits from Spontaneous Species Using HPLC-DAD.” *Molecules* 30(15), 3071 (2025), DOI: 10.3390/molecules30153071. Table 6; method validation Tables 2–5. https://doi.org/10.3390/molecules30153071
2. Leporini et al. “Citrus × Clementina Hort. Juice Enriched with Its By-Products (Peels and Leaves): Chemical Composition, In Vitro Bioactivity, and Impact of Processing.” *Antioxidants* 9(4), 298 (2020), DOI: 10.3390/antiox9040298. Plant material and food-use context §§2.2–2.3; standard/calibration methods §2.8; sinensetin values Table 7. https://pmc.ncbi.nlm.nih.gov/articles/PMC7222210/
