# Phase 2 Retention Evidence Acquisition Report

**Status: EVIDENCE ACQUIRED; SCIENTIFIC COMPATIBILITY AND OWNER DECISIONS PENDING.**  
**Scope:** Stage C `Phase2-v0.3.1` evidence records and the sources explicitly cited by those records. No Stage A/B files, outputs, or embedded snapshots were accessed. No release data, code, or accepted observations were changed.

## Executive result

The primary sources provide more detail than the original aggregate summaries:

- The Suresh et al. cooking paper and its author thesis report separate measured raw and cooked curcumin/piperine concentrations for the specified experimental conditions. These are source-specific measured concentration observations. This report does **not** convert their reported loss percentages into retention factors and does not transfer the source results to Phase 1B records.
- Paudel et al. report the Phase 1B commercial turmeric samples and curcumin concentrations, but do not report sample moisture or a dry-matter correction for those commercial samples. These were market powder samples, distinct from the locally purchased spice used in the cooking study.
- The tea evidence is not purely qualitative: Park et al. quantitatively measured EGCG in a different green tea under controlled brewing conditions. The USDA-linked Phase 1B record is a decaffeinated infusion sourced to unpublished 2002 data, and its brewing time and source analytical method are unavailable. The different tea/source and protocol prevent a validated transfer.

Release disposition remains: **10 `PENDING_SOURCE_BASIS`, 11 `PENDING_MATRIX_COMPATIBILITY`, 1 `QUALITATIVE_ONLY`; 0 numerical applications allowed**. The single `QUALITATIVE_ONLY` label understates the existence of quantitative EGCG data in an unrelated experimental tea study, but that finding does not establish compatibility for the USDA decaffeinated tea record. No release classification is changed here.

## Authoritative records and what they establish

### Curcumin/piperine cooking study

Suresh, Manjunatha, and Srinivasan, “Effect of heat processing of spices on the concentrations of their bioactive principles,” *Journal of Food Composition and Analysis* 20 (2007), 346–351, [DOI 10.1016/j.jfca.2006.10.002](https://doi.org/10.1016/j.jfca.2006.10.002). The publisher record and accessible article copy identify the study as measuring curcumin in turmeric and piperine in black pepper; the abstract describes boiling 10/20 min and pressure cooking 10 min, with cooked samples freeze-dried before HPLC quantitation. The full-text methods specify 1 g powdered spice in 100 mL water, with 0.5 g tamarind in tamarind conditions; boil volume was maintained near 100 mL by water addition. The cooking treatments include spice alone and spice with red gram/tamarind. The tables report condition-level means ± SEM for five independent determinations in mg/g spice. The article does not provide cooked mass yield or a mass-balance equation that establishes total analyte mass retained. [Full article copy](https://citeseerx.ist.psu.edu/document?doi=7ad3981f42ed2ffa6023b5b5c6297d40d355bf53&repid=rep1&type=pdf), [author thesis, CFTRI repository](https://ir.cftri.res.in/1533/1/SureshD.pdf).

The article's methods and tables support the conditions and values below. They do not establish that these results transfer to the different Phase 1B retail samples. The cooking paper's table reports concentrations “mg/g spice”; the cooked samples were lyophilized food samples. The record does not resolve a conversion between that denominator and the Phase 1B as-analyzed commercial powder basis, nor report yield/mass balance.

| Experimental source matrix | Raw source mean ± SEM (mg/g spice) | Boil 10 min | Boil 20 min | Pressure cook 10 min, 15 psi | Method/source status |
|---|---:|---:|---:|---:|---|
| Turmeric alone, curcumin | 25.7 ± 1.44 | 18.8 ± 1.74 | 17.3 ± 1.26 | 12.1 ± 1.74 | Direct source table measurements; n=5; HPLC at 425 nm. |
| Turmeric + 0.5 g tamarind, curcumin | 21.7 ± 0.15 | 18.5 ± 1.45 | 17.0 ± 1.65 | 14.3 ± 2.41 | Direct source table measurements; n=5; HPLC at 425 nm. Separate matrix; not turmeric-only. |
| Black pepper alone, piperine | 55.8 ± 3.40 | 40.8 ± 2.76 | 40.3 ± 3.26 | 36.9 ± 2.74 | Direct source table measurements; n=5; HPLC at 345 nm. |

No derived retention factor is calculated in this report. The article's source-reported parenthetical loss values are not used as factors or converted to complements.

### Phase 1B turmeric concentration records

Paudel et al., “Optimization and Validation of a New HPLC Method for the Comparative Analysis of Curcumin in Fresh Rhizome Across Gandaki Province, Nepal, and Marketed Turmeric Powder,” *Journal of Food Quality* (2025), [DOI 10.1155/jfq/8925770](https://doi.org/10.1155/jfq/8925770). The paper identifies ten market powders and publishes their Curcumin I results in mg/g, with triplicate analysis. The paper describes a methanol extraction and HPLC-UV quantitation at 425 nm; the commercial samples were transported to the laboratory for preparation/analysis. The article does not report moisture measurement or state that these commercial-powder values were dry-weight corrected. [Full article](https://onlinelibrary.wiley.com/doi/10.1155/jfq/8925770).

The records below are ingredient/powder concentrations; the release labels them `food ingredient` and `ordinary_dietary_eligible=false`. The cooking-study samples were separately locally purchased and powdered, so shared species and nominal units do not establish sample-level equivalence.

### Piperine Phase 1B concentration record

Lee et al., “Determination and risk characterisation of bio-active piperine in black pepper and selected food containing black pepper consumed in Korea,” *Food Science and Biotechnology* 30 (2021), 209–215, [DOI 10.1007/s10068-020-00860-1](https://doi.org/10.1007/s10068-020-00860-1), [full text in PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7914320/). The study sampled 71 black pepper retail products in Seoul in 2019 (part of 208 total foods), homogenized samples, extracted approximately 0.1 g pepper with methanol and quantified piperine with HPLC-DAD at 340 nm; the reported mean was 4,418 mg/100 g sample. The article does not specify whether these black pepper retail products were whole, cracked, or powdered, and does not report a moisture correction in the inspected method. This is not the same sample as the CFTRI cooking study's locally purchased dry pepper seeds powdered through a No. 50 sieve.

### Tea/EGCG records

The Phase 1B record is USDA NDB 99069, “Tea, green, brewed, decaffeinated,” from [USDA Flavonoid Database Release 3.3](https://www.ars.usda.gov/ARSUserFiles/80400535/Data/Flav/Flav3.3.pdf), table printed p.105/PDF p.107. It reports (-)-EGCG at 26.05 mg/100 g (mean of two individual data values; source 272). USDA documentation says tea values are standardized to a 1% infusion (1 g leaves/100 mL boiling water), reported as consumed, and that brew-time adjustment was not undertaken. Its cited underlying source is Unilever Bestfoods North America, *Summary Flavonoid Content of Teas in the U.S. Market* (unpublished data, 2002); the source-level sample and analytical method are unavailable in the USDA document.

The linked retention evidence is Park et al., “Comprehensive Investigation of the Effects of Brewing Conditions in Sample Preparation of Green Tea Infusions,” *Molecules* 24 (2019), 1735, [DOI 10.3390/molecules24091735](https://doi.org/10.3390/molecules24091735), [full text in PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC6539062/). It uses powdered Osulloc green tea (not identified as decaffeinated), 2 g in 200 mL doubly distilled water, brewed at 60 or 95 °C for 5–300 minutes. It quantifies eight catechins including EGCG using validated UHPLC-QqQ/MS. The paper reports quantitative EGCG concentration curves and documents temperature/time-dependent changes and epimerization. It is not a matched raw/cooked experiment for USDA's decaffeinated tea identity, source, or specified brewing time; its measurements cannot be treated as a retention factor for NDB 99069. The evidence remains insufficient for a numeric Phase 1B adjustment.

## Record-by-record compatibility disposition

The following is the complete set of the 22 compatibility IDs in `Phase2-v0.3.1/data/retention_compatibility_matrix_2026-11-03.csv`. Each row is assessed independently. For turmeric records, the published concentration and matrix are common for the paired `P2-RET-002`/`P2-RET-003` combinations, but the linked Phase 1B value differs by sample as listed in the release matrix. No combination passes for numeric application.

| Combination ID | Verified food/compound and concentration evidence | Source preparation/evidence | Compatibility assessment and decision needed |
|---|---|---|---|
| `PAUDEL2025-002-Co-T-1-CURCUMIN__P2-RET-002` | Commercial turmeric powder, Curcumin I, 20.38 mg/g (20,380 mg/kg); as-analyzed sample basis; moisture correction not stated. | Suresh turmeric alone; 1 g powder/100 mL water; boil 10 or 20 min, or pressure cook 10 min at 15 psi; cooked material lyophilized; condition-level source means above; HPLC. | `PENDING_SOURCE_BASIS`: separate source sample, moisture and cooked denominator/yield unbridged. Owner/reviewer must decide whether an explicitly bounded cross-study concentration transfer is scientifically acceptable; no default transfer. |
| `PAUDEL2025-002-Co-T-1-CURCUMIN__P2-RET-003` | Same turmeric-only concentration record. | Suresh turmeric + 0.5 g tamarind / 1 g spice / 100 mL water; condition-level means above. | `PENDING_MATRIX_COMPATIBILITY`: tamarind matrix differs. Keep ingredient context; no transfer absent separately justified, qualified review. |
| `PAUDEL2025-002-Co-T-2-CURCUMIN__P2-RET-002` | Commercial turmeric powder, Curcumin I, 22.40 mg/g; as-analyzed, moisture correction unstated. | Suresh turmeric-alone conditions and source-specific basis described above. | `PENDING_SOURCE_BASIS`; separate study sample and denominator/yield unresolved. |
| `PAUDEL2025-002-Co-T-2-CURCUMIN__P2-RET-003` | Same turmeric-only concentration record. | Suresh turmeric+tamarind conditions. | `PENDING_MATRIX_COMPATIBILITY`; turmeric+tamarind evidence does not match the linked turmeric-only food record. |
| `PAUDEL2025-002-Co-T-3-CURCUMIN__P2-RET-002` | Commercial turmeric powder, Curcumin I, 16.63 mg/g; as-analyzed, moisture correction unstated. | Suresh turmeric-alone conditions and source-specific basis described above. | `PENDING_SOURCE_BASIS`; separate study sample and denominator/yield unresolved. |
| `PAUDEL2025-002-Co-T-3-CURCUMIN__P2-RET-003` | Same turmeric-only concentration record. | Suresh turmeric+tamarind conditions. | `PENDING_MATRIX_COMPATIBILITY`; turmeric-only and tamarind-containing matrices differ. |
| `PAUDEL2025-002-Co-T-4-CURCUMIN__P2-RET-002` | Commercial turmeric powder, Curcumin I, 16.54 mg/g; as-analyzed, moisture correction unstated. | Suresh turmeric-alone conditions and source-specific basis described above. | `PENDING_SOURCE_BASIS`; separate study sample and denominator/yield unresolved. |
| `PAUDEL2025-002-Co-T-4-CURCUMIN__P2-RET-003` | Same turmeric-only concentration record. | Suresh turmeric+tamarind conditions. | `PENDING_MATRIX_COMPATIBILITY`; turmeric-only and tamarind-containing matrices differ. |
| `PAUDEL2025-002-Co-T-5-CURCUMIN__P2-RET-002` | Commercial turmeric powder, Curcumin I, 15.11 mg/g; as-analyzed, moisture correction unstated. | Suresh turmeric-alone conditions and source-specific basis described above. | `PENDING_SOURCE_BASIS`; separate study sample and denominator/yield unresolved. |
| `PAUDEL2025-002-Co-T-5-CURCUMIN__P2-RET-003` | Same turmeric-only concentration record. | Suresh turmeric+tamarind conditions. | `PENDING_MATRIX_COMPATIBILITY`; turmeric-only and tamarind-containing matrices differ. |
| `PAUDEL2025-002-Co-T-6-CURCUMIN__P2-RET-002` | Commercial turmeric powder, Curcumin I, 18.25 mg/g; as-analyzed, moisture correction unstated. | Suresh turmeric-alone conditions and source-specific basis described above. | `PENDING_SOURCE_BASIS`; separate study sample and denominator/yield unresolved. |
| `PAUDEL2025-002-Co-T-6-CURCUMIN__P2-RET-003` | Same turmeric-only concentration record. | Suresh turmeric+tamarind conditions. | `PENDING_MATRIX_COMPATIBILITY`; turmeric-only and tamarind-containing matrices differ. |
| `PAUDEL2025-002-Co-T-7-CURCUMIN__P2-RET-002` | Commercial turmeric powder, Curcumin I, 17.71 mg/g; as-analyzed, moisture correction unstated. | Suresh turmeric-alone conditions and source-specific basis described above. | `PENDING_SOURCE_BASIS`; separate study sample and denominator/yield unresolved. |
| `PAUDEL2025-002-Co-T-7-CURCUMIN__P2-RET-003` | Same turmeric-only concentration record. | Suresh turmeric+tamarind conditions. | `PENDING_MATRIX_COMPATIBILITY`; turmeric-only and tamarind-containing matrices differ. |
| `PAUDEL2025-002-Co-T-8-CURCUMIN__P2-RET-002` | Commercial turmeric powder, Curcumin I, 21.07 mg/g; as-analyzed, moisture correction unstated. | Suresh turmeric-alone conditions and source-specific basis described above. | `PENDING_SOURCE_BASIS`; separate study sample and denominator/yield unresolved. |
| `PAUDEL2025-002-Co-T-8-CURCUMIN__P2-RET-003` | Same turmeric-only concentration record. | Suresh turmeric+tamarind conditions. | `PENDING_MATRIX_COMPATIBILITY`; turmeric-only and tamarind-containing matrices differ. |
| `PAUDEL2025-002-Co-T-9-CURCUMIN__P2-RET-002` | Commercial turmeric powder, Curcumin I, 15.46 mg/g; as-analyzed, moisture correction unstated. | Suresh turmeric-alone conditions and source-specific basis described above. | `PENDING_SOURCE_BASIS`; separate study sample and denominator/yield unresolved. |
| `PAUDEL2025-002-Co-T-9-CURCUMIN__P2-RET-003` | Same turmeric-only concentration record. | Suresh turmeric+tamarind conditions. | `PENDING_MATRIX_COMPATIBILITY`; turmeric-only and tamarind-containing matrices differ. |
| `PAUDEL2025-002-Co-T-10-CURCUMIN__P2-RET-002` | Commercial turmeric powder, Curcumin I, 20.34 mg/g; as-analyzed, moisture correction unstated. | Suresh turmeric-alone conditions and source-specific basis described above. | `PENDING_SOURCE_BASIS`; separate study sample and denominator/yield unresolved. |
| `PAUDEL2025-002-Co-T-10-CURCUMIN__P2-RET-003` | Same turmeric-only concentration record. | Suresh turmeric+tamarind conditions. | `PENDING_MATRIX_COMPATIBILITY`; turmeric-only and tamarind-containing matrices differ. |
| `KOREA-PEPPER-2021-PIPERINE__P2-RET-001` | Korean retail black pepper aggregate; piperine 4,418 mg/100 g (44.18 mg/g; release normalizes to 44,180 mg/kg); as-received/homogenized per release, but moisture basis and whole/ground condition are not stated by Lee et al. | Suresh locally sourced dry seeds, powdered through No. 50 sieve; 1 g/100 mL aqueous suspension; three separate conditions: boil 10 min, boil 20 min, pressure cook 10 min at 15 psi; lyophilized cooked food sample; source-specific HPLC means above. | `PENDING_MATRIX_COMPATIBILITY`: species matches, but sample state, source sample, basis and yield do not. Owner/reviewer must decide whether any cross-study transfer is defensible and select a condition only if the intended preparation matches. |
| `USDA-FLAV33-NDB99069-EGCG__P2-RET-004` | Decaffeinated brewed green tea; EGCG 26.05 mg/100 g (release-normalized 260.50 mg/kg), mean n=2, USDA standardized 1% infusion; underlying source #272 unpublished. | Park et al. quantify EGCG for Osulloc green tea powder brewed 2 g/200 mL at 60/95 °C for 5–300 min using UHPLC-QqQ/MS; quantitative concentrations exist, but this is another tea product and protocol. | `QUALITATIVE_ONLY` remains a no-numeric-application disposition for this linked combination, not a claim that no quantitative EGCG literature exists. Decaf source method/time and matched reference brewing experiment are unavailable; do not transfer the Park curves. |

## Evidence found / unavailable / owner review

### Found in authoritative sources

- Distinct condition-level raw/cooked analyte concentrations and five-replicate SEMs for Suresh's turmeric-alone, turmeric+tamarind, and black-pepper-alone experiments; experimental food identity, 1 g spice per 100 mL water, tamarind amount where applicable, cooking durations, and 15 psi pressure condition.
- The cooking article's chromatographic method: curcumin HPLC UV at 425 nm, piperine reverse-phase HPLC UV at 345 nm; cooked samples lyophilized before assay.
- Paudel's sample codes and Curcumin I mg/g values for the ten commercial turmeric powders; a methanolic extraction/HPLC-UV method and triplicate analysis.
- Lee's 71 Korean retail pepper samples and HPLC-DAD method, including piperine reported per 100 g sample.
- USDA's decaffeinated tea item, EGCG mean, 1% infusion standardization, explicit absence of brew-time adjustment, and unpublished source citation.
- Park et al.'s separate quantitative EGCG brewing study, tea product, brew ratio, condition range, and targeted LC-MS/MS method.

### Not established in available sources

- Moisture percentage or dry-weight conversion for the exact Paudel commercial powder samples or Lee retail pepper aggregate.
- Whether Lee's black pepper samples were whole, cracked, or powder.
- A source-defined conversion connecting Suresh's cooked lyophilized-food “mg/g spice” denominator with Paudel's as-analyzed commercial powder or Lee's retail pepper denominator.
- Cooking yield or paired initial/final edible mass for the Suresh experiments; a whole-system analyte mass balance; precise disposition/recovery of analyte in cooking liquid.
- For USDA NDB 99069, the unpublished Unilever #272 sample identities, analytical method, and brewing time/temperature details beyond the USDA 1% boiling-water normalization.
- A matched brewing time/reference baseline between USDA decaffeinated tea and the Park et al. Osulloc tea study.

### Decisions requiring owner and qualified scientific reviewer

1. Authorize and identify the custodian/source document for any Suresh original worksheets or additional method details on sample mass, lyophilized denominator, cooking yield, and liquid recovery. If those records do not exist, mark the fields unavailable.
2. Decide whether evidence from the separately sourced Suresh spices may ever be transferred to the Paudel/Lee concentration records. Require a qualified reviewer to justify the population/matrix and measurement-basis scope; owner sign-off alone is not scientific validation.
3. For the ten turmeric records, retain `food ingredient` classification unless the owner explicitly authorizes a separate ordinary-food classification review. Do not treat the turmeric+tamarind study as turmeric-only evidence.
4. For pepper, determine whether the intended use is a powdered ingredient and select which tested condition corresponds to the target preparation; no scenario can be chosen by this audit.
5. For tea, decide whether to seek the unpublished Unilever #272 underlying record or keep the linked combination unavailable. Any future use of Park et al. requires an explicit product/protocol compatibility review.
6. Define whether the intended output is a concentration ratio / concentration-retention calculation or total-mass retention. The latter requires compatible measured yield or an explicit source-reported mass-balance endpoint.

## Preservation and completion

No calculation, model prediction, or new cooked concentration was generated. The `117` accepted Phase 2 observed cooking-pair boundary was not modified. All release records still prohibit numerical application for these combinations. This report supplements, and does not overwrite, [`PHASE2_RETENTION_EVIDENCE_ACQUISITION_REQUEST_2026-11-05.md`](PHASE2_RETENTION_EVIDENCE_ACQUISITION_REQUEST_2026-11-05.md).
