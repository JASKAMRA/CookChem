# Phase 4 source and extraction report — working registry v0.1.1

Status: **IN_PROGRESS**. Phase 4 scope is proposed; no source record is accepted for downstream use.

| Measure | Count | Meaning |
|---|---:|---|
| Registered primary sources | 1 | White et al. 2016 |
| Sources with bibliographic identifiers verified | 1 | PubMed record confirms title, authors, journal, year, DOI, PMID |
| Publisher full texts reviewed | 1 | Full text and Table 1 inspected |
| Evidence records | 6 | Five condition-level measured Cmax rows and one qualitative between-condition result |
| Measured numeric records | 5 | Means, SDs, ranges, units, condition labels, and source table locations retained |
| Qualitative records | 1 | Omnibus and pairwise statistical findings kept separate from arm-level estimates |
| Accepted records | 0 | Identity/applicability gates and independent review remain pending |

Source: White JR et al., *Clinical Toxicology* 2016;54(4):308–312. DOI 10.3109/15563650.2016.1146740; PMID 27100333. Bibliography: https://pubmed.ncbi.nlm.nih.gov/27100333/. Primary full text/Table 1: https://www.tandfonline.com/doi/pdf/10.3109/15563650.2016.1146740.

Table 1 reports mean ± SD (range) Cmax in µg/mL:

| Arm | Condition | Mean | SD | Range |
|---|---|---:|---:|---:|
| A | hot coffee, 20 min | 3.74 | 1.09 | 1.96–5.95 |
| B | cold coffee, 2 min | 3.64 | 1.36 | 1.81–8.17 |
| C | cold coffee, 20 min | 3.56 | 1.06 | 1.69–5.77 |
| D | sugar-free energy drink, 2 min | 3.36 | 1.20 | 1.40–5.78 |
| E | sugar-free energy drink, 20 min | 3.14 | 0.95 | 1.87–5.25 |

Each row is stored as a separate evidence record so conditions and denominators cannot be collapsed. Values are source-reported, not calculated by CookRisk. Conditions are 160 mg caffeine in 450 mL beverage. The source's abstract says 24 subjects completed, whereas Methods says 24 were recruited and two were excluded for poor venous access; Table 1 does not state condition-specific analyzed n. The discrepancy is recorded and not resolved by assumption.

The study reports an omnibus difference in mean Cmax (one-way repeated-measures ANOVA p=0.043) with no pairwise comparison statistically significant. This finding is separately recorded; it does not establish equivalence or a specific arm-to-arm difference. The article reports American Beverage Association funding and investigator consultancy disclosures, retained as limitations.

Identity remains `NAME_ONLY_MATCH` because the source does not cite a structure identifier, despite a Phase1B caffeine candidate (PubChem CID 2519). Applicability remains `CONTEXT_LIMITED`; none of these plasma concentrations are food concentrations, recipe-dose multipliers, cooking factors, safety thresholds, or clinical recommendations. All six records remain pending an independent second review.
