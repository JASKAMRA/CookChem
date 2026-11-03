# Batch 106 — prunin source follow-up

**Outcome:** no new accepted food records. The active data remain at 546 records and 546 mappings, covering 100/107 identity-complete compounds; seven complete-identity gaps remain. Nine new prunin values are preserved as held candidates. A potentially eligible, authentic-standard-calibrated apple-pulp source was identified, but its numeric Supplementary Table S1 could not be retrieved and no value was guessed. No release was created.

## Research scope and baseline

This bounded follow-up targeted the remaining identity-complete prunin gap after Batch 105. It added three primary-source investigations and three search-log events. The verified starting point was checkpoint Phase1B-2026-11-03-batch-105-targeted-source-followup: 143/143 IDs screened; 546 food records / 546 mappings; 100/107 identity-complete quantitative compounds; 36 pending identities; 46 blocked legacy mappings; 459 search events; 59 source-registry rows; zero orphans.

## New primary evidence

### Potentially eligible apple-pulp study — not yet promotable

Ceci et al., “Metabolomic Characterization of Commercial, Old, and Red-Fleshed Apple Varieties,” *Metabolites* 11(6):378 (2021), DOI [10.3390/metabo11060378](https://doi.org/10.3390/metabo11060378), [open full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC8230845/), [official supplementary-material page](https://www.mdpi.com/article/10.3390/metabo11060378/s1). The methods name purchased naringenin-7-glucoside (prunin) as a reagent, identify compounds by reference standards and SRM, state that each compound was quantified with its own external calibration curve, and normalize pulp values to mg/100 g fresh weight. The paper describes 22 apple cultivars and 10 biological fruit replicates per cultivar; Supplementary Table S1 contains the cultivar means ± SD.

This is the strongest new lead and appears to meet the analyte, matrix, calibration, and basis gates. The paper lists a 51 KB supplementary ZIP containing Table S1, with values in mg/100 g fresh weight and mean ± SD for n=10. The PMC file endpoint returned a cache-miss retrieval error and the MDPI supplement page was inaccessible through the available research viewer, so no numeric value could be transcribed or independently checked. Since no S1 number could be read directly, no candidate value or accepted food record was fabricated. Batch 107 should retrieve the supplement using an accessible repository/download path, verify the exact Prunin column and cultivar cells, and then ingest eligible values through the existing pipeline.

### Orange-processing by-product values — held

Two open primary studies report exact table values but do not provide an analyte-specific prunin calibration assignment and study orange juice-processing by-products under specialized processing/extraction conditions. Their values are therefore retained in `candidate_measurements.csv` and the central `CANDIDATES.csv`, outside active food data:

| Source / condition | Prunin value as reported | Decision |
|---|---:|---|
| Razola-Díaz et al., *Foods* 2024, Table 3; *Levilactobacillus brevis* CECT 5354, 24 h | 149.44 ± 1.35 µg/g d.w. | Hold: no prunin-specific calibration/response factor stated; supplemented, fermented by-product |
| Same, *L. brevis*, 48 h | 141.97 ± 2.65 µg/g d.w. | Hold for the same reasons |
| Same, *Lactiplantibacillus plantarum* CECT 748T, 24 h | 138.38 ± 2.75 µg/g d.w. | Hold for the same reasons |
| Same, *L. plantarum* CECT 748T, 48 h | 120.88 ± 1.30 µg/g d.w. | Hold for the same reasons |
| Same, *L. plantarum* CECT 9567, 24 h | 124.48 ± 1.71 µg/g d.w. | Hold for the same reasons |
| Same, *L. plantarum* CECT 9567, 48 h | 137.31 ± 0.14 µg/g d.w. | Hold for the same reasons |
| Same, non-fermented control | 123.74 ± 2.72 µg/g d.w. | Hold for the same calibration and matrix reasons |
| Razola-Díaz et al., *LWT* 2024, Table 4; PEF-pretreated orange peel | 176.0 ± 0.8 µg/g d.w. | Hold: five proxy standards are listed, but no prunin curve/assignment is stated; PEF/ultrasound recovery context |
| Same, control orange peel | 102.7 ± 0.6 µg/g d.w. | Hold for the same reasons |

Primary sources: [Razola-Díaz et al., *Foods* 2024, DOI 10.3390/foods13081212](https://doi.org/10.3390/foods13081212), Table 3 and Methods §§2.1–2.5; [Razola-Díaz et al., *LWT* 2024, DOI 10.1016/j.lwt.2024.115950](https://doi.org/10.1016/j.lwt.2024.115950), Table 4 and Methods §2.5. The *LWT* methods list calibration standards for vanillic acid, chlorogenic acid, ferulic acid, quercetin, and rutin, not prunin, and do not state which curve was applied to prunin. The *Foods* paper likewise does not document a prunin-specific curve in its methods. Do not label these as fully quantitative prunin composition without the missing response-factor evidence.

## Coverage and decisions

- New accepted food records: **0**.
- Newly covered unique compounds: **0**.
- Held numeric candidate rows added: **9** (7 fermented orange-peel conditions; 2 PEF/control orange-peel conditions).
- High-priority eligible-source leads: **1** (apple pulp; values wait on direct Table S1 retrieval).
- Identity-complete quantitative coverage: **100/107**, unchanged.
- Complete-identity gaps: **7**, unchanged.
- Pending identities: **36**, unchanged; no Stage B edits.
- Research screening coverage: **143/143**; this establishes recorded screening, not exhaustive absence.
- Active food records / mappings: **546 / 546**, unchanged; orphan mappings: **0**.
- Minimum target 130 remains unmet by **30**; no Phase 1B release was created.

## Validation and integrity

All source values remain in candidate-only registers. No active food record or mapping was changed, and no Stage B or Phase 1 release file was edited. Phase 1 validation passed with 546 food records and 546 mappings, zero errors or orphans, and zero Stage B snapshot changes. The independent mapping rebuild matched all 546 active mapping rows in exact order. Batch 106 focused tests passed 5/5, and the full Stage C regression suite passed 99/99. Hashes and test results are recorded in `validation_and_test_results.json`.

## Batch 107 next action

Retrieve and directly inspect the apple-pulp supplement `metabolites-11-00378-s001.zip` or its equivalent source-hosted file. Transcribe only exact prunin values and SDs from Table S1, confirm the reported sample/cultivar basis, and apply the existing ingestion validator. Keep the nine orange by-product values held unless source-specific calibration and eligibility are established. Continue the six other identity-complete gaps and pending-identity food research without modifying Stage B.
