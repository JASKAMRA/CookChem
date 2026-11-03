# Batch 021 — cinnamaldehyde in Korintje cinnamon

## Screening decision

One exact-named primary quantitative candidate was found for Stage B Cinnamaldehyde (`CHEM-PUBCHEM-637511`). Li et al. report 36.66 mg cinnamaldehyde per gram of ground Korintje cassia-bark cinnamon, equivalent by unit conversion to 36,660 mg/kg. The source identifies cinnamaldehyde by retention time and compares peak area with a commercial standard. It does not explicitly specify geometric isomer purity, so mapping to the Stage B trans-(E) structure remains a review point.

## Source and sample scope

Li, Z. et al. (2020). “Acute Effects of Cinnamon Spice on Post-prandial Glucose and Insulin in Normal Weight and Overweight/Obese Subjects: A Pilot Study.” *Frontiers in Nutrition*, 7, 619782. DOI: 10.3389/fnut.2020.619782; PMID: 33330215. Full text: https://www.frontiersin.org/journals/nutrition/articles/10.3389/fnut.2020.619782/full. The cinnamon was Korintje cinnamon ground from cassia bark and purchased at a local grocery store. HPLC-PDA identification used retention time at 280 nm, with concentrations calculated by comparison to commercial standard peak area.

## Uncertainty

The paper reports one powder sample, with no replicate count, moisture basis, extraction recovery, or analytical uncertainty in the reviewed text. The reported analyte label is cinnamaldehyde; explicit E/Z identity is not given. This candidate therefore preserves an analyte-identity review flag and is not generalized across cinnamon species or batches.

## Pipeline gate

Candidate CSV only. No cumulative food data or accepted mapping was changed; ingestion remains gated on Stage B release checksum reconciliation.

## Additional primary-source screen (2026-11-02)

Friedman, Kozukue and Harden (2000), “Cinnamaldehyde content in foods determined by gas chromatography-mass spectrometry,” *Journal of Agricultural and Food Chemistry* 48(11):5702–5709, DOI 10.1021/jf000585g (PMID 11087542), explicitly identifies **trans-cinnamaldehyde** and analyzes commercial cinnamon-containing foods. The PubMed abstract gives food-specific values for apple-cinnamon cereal (12.2 mg/100 g) and cinnamon-swirl bread (31.1 mg/100 g, the highest reported); other product values are not exposed in the abstract. Two candidate rows have now been recorded at 122 and 311 mg/kg respectively (unit conversion ×10). They remain candidates pending full-text method/sample details and Stage B checksum reconciliation. The separate Korintje powder value remains held because its source does not specify geometric isomer.
