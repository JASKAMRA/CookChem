# Cycle 5 Workstream C — Broad Published-Benchmark Screen

**Screen date:** 2026-11-04  
**Scope:** Expand the Phase 5 literature screen beyond the prior seven-onion/quercetin workstream to multiple Phase1B food/analyte pairs. Artifacts are additive under `cycle5_broad_search/`; no Stage A/B records, Phase1B catalog, Phase 3 engine, release package, or prior onion-screen result was changed.

## Result

The screen reviewed nine candidate combinations spanning spinach, broccoli, green tea, basil, and the prior onion boundary. Candidate identifiers and quantitative reference values were checked against the immutable, checksum-verified Phase1B-v1.3.2 release rather than the mutable Stage C working copy. Two independent primary studies provided traceable quantitative datasets that match a Phase1B analyte closely enough for **raw concentration source-to-source reconciliation**:

- spinach / lutein — Chang et al. (2013), with raw, stir-fried, and boiled observations;
- broccoli / ascorbic acid — Lee et al. (2018), with raw, boiled, blanched, steamed, and microwaved observations.

The machine-readable dataset contains 10 reported observations. The two raw pairs normalize to the same mass denominator, but both show material between-study differences. They are therefore recorded as **context-limited descriptive contrasts**, not agreement scores or model-validation results. No Phase 3 predicted values were compared, and no external scientific validation was conducted.

## Ranked candidate matrix

The complete candidate list, exact source locators, decisions, and exclusion reasons are in [`candidate_matrix.csv`](cycle5_broad_search/candidate_matrix.csv).

| Rank | Food / compound | Source | Disposition |
|---:|---|---|---|
| 1 | Spinach / lutein | Chang et al., 2013; Table 2, pp. 460–461; [official journal PDF](https://ifrj.upm.edu.my/20%20%2801%29%202013/63%20IFRJ%2020%20%2801%29%202013%20Amin%20%28251%29.pdf) | Dataset included; raw pair only is context-limited. Direct lutein HPLC-DAD, raw and four cooking endpoints, weight yield and true retention, triplicate experiments. |
| 2 | Broccoli / ascorbic acid | Lee et al., 2018; Table 2; [primary full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC6049644/), DOI [10.1007/s10068-017-0281-1](https://doi.org/10.1007/s10068-017-0281-1) | Dataset included; raw pair only is context-limited. HPLC-UV quantified against an ascorbic acid standard; raw and four cooked endpoints. |
| 3 | Spinach / lutein | Fratianni et al., 2021; Tables 1 and 5; [primary full text](https://www.mdpi.com/2304-8158/10/5/960), DOI [10.3390/foods10050960](https://doi.org/10.3390/foods10050960) | Not paired: dry-matter values cannot be converted to the Phase1B wet-weight sample basis without same-sample moisture. |
| 4 | Green tea / EGCG | Saklar et al., 2015; [primary full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC4573099/), DOI [10.1007/s13197-015-1746-y](https://doi.org/10.1007/s13197-015-1746-y) | Not paired: Turkish tea at 1.45 g/100 mL and variable steeping conditions cannot be equated to USDA's decaffeinated, standardized 1% boiling infusion. The USDA aggregate cites an unpublished source with no source-level method. |
| 5 | Spinach / zeaxanthin | Lim, 2007; Korean primary bibliographic record and [AGRIS record](https://agris.fao.org/search/en/providers/122646/records/6472487253aa8c896304dae7) | Plausible exact analyte candidate, but not transcribed: accessible records reviewed here do not expose verifiable zeaxanthin table cells, units, uncertainty, and sample basis. No concentration was inferred from percentages or figures. |
| 6 | Broccoli / sulforaphane | Celik et al., 2014; [RSC article record](https://pubs.rsc.org/en/content/articlelanding/2014/ay/c4ay00112e), DOI [10.1039/C4AY00112E](https://doi.org/10.1039/C4AY00112E) | Not paired: Phase1B values are operational hydrolysis-released sulforaphane from lyophilized Beneforté on a dry-weight basis. Equivalence of hydrolysis protocol and basis was not established from the candidate record. |
| 7 | Broccoli / quercetin glycoside | Wu et al., 2019; [USDA-hosted primary paper](https://www.ars.usda.gov/ARSUSERFILES/80400535/DATA/PUBLICATIONS/AMR/EFFECTS%20OF%20DOMESTIC%20COOKING%20ON%20FLAVONOIDS.PDF), DOI [10.1016/j.heliyon.2019.e01310](https://doi.org/10.1016/j.heliyon.2019.e01310) | Not a StageC pair: measured named quercetin glycoside is not free quercetin aglycone; food matrix also differs from Phase1B's onion/quercetin row. |
| 8 | Basil / rosmarinic acid | Trakoontivakorn et al., 2012; [JIRCAS primary PDF](https://www.jircas.go.jp/sites/default/files/publication/jarq/46-04-09_0.pdf), DOI [10.6090/jarq.46.347](https://doi.org/10.6090/jarq.46.347) | Not quantitative: HPLC chromatograms describe presence/intensity and leaching, but provide no calibrated numeric compound concentrations. Fresh leaves also differ from the Phase1B dried-herb record. |
| 9 | Onion / quercetin | Existing Phase1B record `B011-HPLC-06` | Scope boundary only. The earlier seven-onion screen is preserved as prior work and was not repeated or counted as new Cycle 5 coverage. |

## Included measurements and arithmetic

### Spinach / lutein

Chang et al. identify spinach as *Spinacia oleracea*. Fresh edible portions came from two retail stalls in Selangor. Their modified AOAC extraction and C30 reverse-phase HPLC-DAD used retention time and authentic-standard spiking to identify lutein; reported recovery for spinach lutein was 85.6%. Table 2 reports mean ± SD, with experiments repeated three times. The cooking endpoints are 4 and 8 minute boiling (100 g spinach in 500 mL water) and 4 and 8 minute stir-frying; the paper also reports weight yields and true retention adjusted for weight change.

Reported lutein concentrations were 495 ± 1.4, 154 ± 2.8, 124 ± 1.9, 428 ± 0.5, and 140 ± 2.4 μg/100 g edible portion for raw, stir-fried 4 min, stir-fried 8 min, boiled 4 min, and boiled 8 min, respectively. Values were converted arithmetically from μg/100 g to mg/100 g by dividing by 1,000; no moisture or yield adjustment was applied to the reported concentrations. True-retention percentages remain as reported by the study.

The Phase1B raw record is 6.89 mg/100 g wet weight; Chang's separate fresh-market raw sample is 0.495 mg/100 g. The catalog value is 13.919 times Chang's value (difference −6.395 mg/100 g; Chang relative to catalog −92.816%). This discrepancy is too large to treat as agreement and cannot identify which study better represents the current food lot. The records remain separate because lot, origin, source-food handling, and study context are not matched.

### Broccoli / ascorbic acid

Lee et al. purchased vegetables at a retail market in Chungbuk, Korea and analyzed ascorbic acid by HPLC-UV at 254 nm against an external ascorbic acid calibration. No DHA reduction step is described. Table 2 reports fresh/cooked weight concentrations and true retention. The results are means from duplicate cooking trials and duplicate analyses; the source table does not provide a numeric SD for these entries.

Broccoli values were 668.04, 370.04, 615.42, 761.48, and 836.15 mg/kg of the respective raw or cooked sample for raw, boiled 5 min, blanched 1 min, steamed 10 min, and microwaved 2 min. Division by 10 converts the mass concentration to mg/100 g; raw becomes 66.804 mg/100 g. The Phase1B Watada row is 131 mg/100 g fresh weight under the source's specified HPO3 extraction condition (pH 1.38). The catalog value is 1.961 times the Lee raw value (difference −64.196 mg/100 g; Lee relative to catalog −49.005%). Market lot, geography, plant-part detail, extraction conditions, and analytical protocol differ, so this is a source-to-source discrepancy, not a benchmark pass/fail.

### Cooking observations are not model checks

The 8 cooked spinach and broccoli observations are preserved as primary-source measurements, but no matching Phase1B cooked estimate or Phase3 model prediction was supplied to this workstream. They are not used to fit retention factors, infer missing values, or claim prediction performance. Missing or unavailable data were not replaced with zero.

## Reproducibility and integrity

- [`benchmark_observations.csv`](cycle5_broad_search/benchmark_observations.csv) stores the 10 study observations with source, table locator, method, replicate description, reported unit, explicit normalized value, and Phase1B comparator where one exists.
- [`compare_cycle5_benchmarks.py`](cycle5_broad_search/compare_cycle5_benchmarks.py) recomputes unit conversions, checks citation and record linkage, and emits only raw-to-raw descriptive comparisons.
- [`descriptive_comparison.csv`](cycle5_broad_search/descriptive_comparison.csv) contains the two context-limited contrasts above.
- [`manifest.json`](cycle5_broad_search/manifest.json) records input/output hashes, row counts, unit rules, and checks performed.
- Focused tests: **5 passed**. They verify conversions, citation/linkage fields, the two allowed raw comparisons, rejection of duplicate observation IDs, and rejection of a mutated unit conversion.

This work adds a broader multi-food evidence screen after the previous seven-onion screen. It does not revise that prior report, modify validation functions, update the dataset release, or claim that published food-composition values validate a Stage C model.
