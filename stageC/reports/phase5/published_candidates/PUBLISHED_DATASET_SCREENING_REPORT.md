# Phase 5 published food-composition candidates

**Screen date:** 2026-11-04  
**Scope:** Workstream C literature screen only. No source datasets, Stage A/Stage B files, release packages, synthetic benchmark fixtures, or validation code were changed.

## Result

Seven primary onion/quercetin cooking studies were screened against Stage C food record `B011-HPLC-06` and the published-data comparison gate. **Zero of seven are eligible for a quantitative comparison in the current data model.** No quantitative fixture was created, and `compare_to_reference()` was not run.

The closest candidate is Watanabe et al. (2018): it has paired raw/sautéed onion, detailed cook endpoints and yield, a validated HPLC method, and triplicate preparations. Its reported measurand is **total quercetin aglycone-equivalent after hydrolysis of onion glycosides**. The current Stage C row measures quercetin directly as a distinct analyte, so substituting Watanabe's total-equivalent concentration would conflate free aglycone with conjugated quercetin. Cattivelli et al. (2021) is also unusually complete, but the methods state that flavonols are quantified as quercetin-3-O-glucoside equivalents. These two sources are therefore useful for future model extensions or source reconciliation, but their reported concentrations must not be passed off as direct free-quercetin measurements.

The existing `compare_to_reference()` implementation checks unit and measurement-basis equality and requires a reference ID and source citation. Those software gates do not establish identical measurands, analytical calibrations, cultivar, or cooking endpoint. Under the scientific screen applied here, no candidate clears the gates without an unsupported conversion or assumption.

## Candidate screen

The detailed, machine-readable source metadata are in [`source_registry.json`](source_registry.json), and the gate-by-gate summary is in [`comparability_matrix.csv`](comparability_matrix.csv).

| ID | Primary source / locator | Main evidence available | Decision and exact blocker |
|---|---|---|---|
| PUB-001 | Watanabe et al. 2018, [publisher PDF](https://www.jstage.jst.go.jp/article/nskkk/65/2/65_63/_pdf), DOI [10.3136/nskkk.65.63](https://doi.org/10.3136/nskkk.65.63); Table 1 and Methods §§1(1)-1(4), 2(1) | Quer-Gold and Kitamomiji 2000; raw and sautéed; 160°C and 20%/50% mass-loss endpoints; mg/100 g initial fresh onion weight; HPLC; three cooking preparations | **Not eligible.** Acid hydrolysis reports total quercetin aglycone-equivalent, not direct free aglycone; cultivars also differ from B011's unspecified retail onion. |
| PUB-002 | Cattivelli et al. 2021, [publisher full text](https://www.mdpi.com/2304-8158/10/5/1023), [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC8151956/), DOI [10.3390/foods10051023](https://doi.org/10.3390/foods10051023), PMID 34066759; Tables 1-3 and Figures 1/3 | Raw and cooked yellow/red onion; bake, boil, fry, grill; mass yields; table distinguishes cooked-mass and initial-fresh-weight bases; triplicate analytical work | **Not eligible.** The method quantifies flavonols in quercetin-3-O-glucoside equivalents rather than using the same authentic quercetin calibration as B011; no matching Stage C cooked prediction exists here. |
| PUB-003 | Nishimuro et al. 2015, [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC4425148/), [PubMed record](https://pubmed.ncbi.nlm.nih.gov/25849945/), DOI [10.3390/nu7042345](https://doi.org/10.3390/nu7042345), PMID 25849945; Table 1, Results §3.1, Methods §§2.1-2.2 | Seasonal market onion; sauté sample described; mg/100 g fresh weight; HCl hydrolysis and HPLC-PDA; 1-3 market purchases and triplicate analysis | **Not eligible.** Hydrolysis measures total quercetin aglycone-equivalent, and the inspected table/text do not provide a clear paired raw/cooked onion row plus cooked-yield mass balance. |
| PUB-004 | Németh et al. 2004, [publisher article](https://cjfs.agriculturejournals.cz/artkey/cjf-200410-0027_effect-of-boiling-on-yellow-onion-quercetin-glucosides.php), [publisher PDF](https://cjfs.agriculturejournals.cz/pdfs/cjf/2004/10/27.pdf), DOI [10.17221/10649-CJFS](https://doi.org/10.17221/10649-CJFS); pp. S170-S172, Figure 2 | Yellow onion; 30-minute reflux boil at three onion:water ratios; lyophilized soup and solids; HPLC-UV | **Not eligible.** Target is quercetin glycosides, and compatible fresh-weight concentration units and replication are not established by the inspected locator. |
| PUB-005 | Harris et al. 2015, [publisher preview](https://www.sciencedirect.com/science/article/abs/pii/S0308814615005816), [PubMed record](https://pubmed.ncbi.nlm.nih.gov/25977008/), DOI [10.1016/j.foodchem.2015.04.035](https://doi.org/10.1016/j.foodchem.2015.04.035), PMID 25977008; publisher preview Table 1 | Fresh/control and heated onion; quercetin glycosides; fry/bake/steam; n=3 noted in abstract | **Not eligible.** Target is glycosides and the quantitative table units, food basis, yield and replicate meaning could not be independently verified from accessible full text. |
| PUB-006 | Lombard et al. 2005, [publisher preview](https://www.sciencedirect.com/science/article/pii/S0889157504000675), DOI [10.1016/j.jfca.2004.03.027](https://doi.org/10.1016/j.jfca.2004.03.027); Table 1 cited in publisher preview | Five cultivars; raw control and sauté/bake/boil; publisher preview reports pooled treatment means and describes water-loss effects | **Not eligible.** Full quantitative table, free-quercetin-specific values, units/basis, assay calibration, yield and replicate details were not accessible for independent verification. |
| PUB-007 | Ioku et al. 2001, [PubMed record](https://pubmed.ncbi.nlm.nih.gov/11349895/), DOI [10.3177/jnsv.47.78](https://doi.org/10.3177/jnsv.47.78), PMID 11349895; PubMed abstract only | Onion; boiling, frying in oil/butter, microwave; quercetin conjugates; HPLC indexed | **Not eligible.** Glycoside measurand and absent accessible quantitative tables, units, basis, cook parameters and replication preclude direct comparison. |

## Why no fixture or numeric comparison was produced

The Phase 5 synthetic benchmark is explicitly test-only and invented. A published fixture would require a fully traceable source row with the same chemical measurand and denominator as the intended Stage C output. The available onion cooking studies report one or more of:

- quercetin conjugates rather than direct free quercetin;
- total hydrolysis-released quercetin expressed as aglycone-equivalent;
- flavonols calibrated as quercetin-3-O-glucoside equivalents;
- values per cooked mass versus initial raw fresh mass;
- incomplete or inaccessible unit, yield, or replication details.

No basis conversion, calibrant conversion, glycoside-to-aglycone conversion, or cultivar assumption was made. No missing values were set to zero. No value from an abstract was used as a quantitative reference. Therefore a numeric comparison would be scientifically misleading even if the code-level unit/basis gate accepted a manually assigned basis string.

## Validation performed

- Inspected the Stage C Phase 5 protocol and the current comparison-gate implementation; did not modify `validation.py` or synthetic fixtures.
- Verified study metadata and available quantitative locators against the primary publisher, PMC, PubMed, or publisher-recognized article metadata linked above.
- Cross-checked the target row's source, method, measurand and basis in the existing Stage C food-composition source record.
- Parsed the JSON registry and CSV matrix and verified candidate counts and unique IDs. No software test suite was run because this workstream adds research/report artifacts only and changes no executable code.
- **Published-data comparison:** not run; no scientifically commensurate reference passed the screen.
- **External scientific validation:** not claimed or conducted.

## Resume path

Revisit quantitative benchmarking if Stage C gains a total-quercetin-equivalent measurand that explicitly includes glycosides, or if a primary study supplies direct free-quercetin concentrations under a matched onion cultivar, cooking protocol, fresh/cooked basis and yield. The Watanabe 2018 and Cattivelli 2021 records are the best candidates to reassess after that data-model change.
