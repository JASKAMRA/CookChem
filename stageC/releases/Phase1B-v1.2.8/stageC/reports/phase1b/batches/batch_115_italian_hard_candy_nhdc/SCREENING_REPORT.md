# Batch 115 — Italian-market hard-candy NHDC measurement

## Decision

Add one quantitative food-composition summary for Neohesperidin dihydrochalcone (NHDC), raising identity-complete coverage from 119 to **120 / 130**. The source’s Table 4 reports 11 ± 10 mg/kg for three NHDC detections in Italian hard candies. The paper states only one of those three was above the quantification limit; its table note says values below LOQ were replaced by LOQ/2 when calculating means. The accepted record therefore preserves the published group summary (11 mg/kg central estimate, SD 10 mg/kg) and explicitly flags censoring/imputation. It is not an exact result for an individual candy.

The compound is already identity-complete in Stage B V20 (PubChem CID 30231; InChIKey ITVGXXMINPYUHD-CUVHLRMHSA-N). Mapping is by exact CID. The matrix is processed hard candy sold in Italy, an ordinary food. This is a measured retail-food concentration summary, not a natural phytochemical abundance claim.

## Source and quantitative trace

- Janvier S, Goscinny S, Le Donne C, Van Loco J. “Low-calorie sweeteners in food and food supplements on the Italian market.” *Food Additives & Contaminants: Part B* (2015), 8(4):298–308. DOI: 10.1080/19393210.2015.1094829; PMID 26406785. Table 4, hard-candy row, reports NHDC 11 ± 10 mg/kg; the paper’s text reports 3 detections, of which only 1 was quantified above LOQ. The study used an in-house validated UPLC-MS/MS method.
- EFSA’s 2022 reevaluation independently summarizes the Italian study and reports its LOQ as 10 µg/kg. LOQ is retained as method context, not substituted for a measured food concentration.

## Limitations

The average is partly censored because two positives were below LOQ and were represented as LOQ/2 in the published mean calculation. The exact above-LOQ sample value cannot be recovered from the accessible table. Coverage increments once for this compound; no estimate of individual candy concentration, dietary exposure, or health risk is made.

## Validation

The successor release’s phase1 validator accepts the record and exact mapping with zero food errors, zero mapping errors, and zero Stage B snapshot changes.
