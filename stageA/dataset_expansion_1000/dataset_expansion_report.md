# Scientific dataset expansion — controlled batch 001

## Result

The target of 1,000–1,200 is **not reached in this batch**. The defensible master dataset is **451 observations** from **11 DOI families**: 12 verified additions from one independent primary paper. The 439-row v1 parent is preserved verbatim.

## Admission

Zhao et al. (2024), DOI `10.1007/s10068-024-01623-y`, Table 2, provides raw and cooked HPLC-PDA ascorbic-acid concentrations in `mg/g dry weight` for red bell pepper. There are three methods × four temperatures, each 15 minutes: 12 condition means. The raw value is 19.38 ± 1.48 mg/g DW; cooked means and SDs are retained in `verified_observations.csv`. These are apparent concentration ratios only and not total-mass retention.

## Deliberate exclusions

Already-admitted DOI families were not duplicated. Total-isothiocyanate yield was excluded because it is an aggregate assay outcome without a single canonical molecular identity for descriptor-dependent modelling. Wet-basis carrot data remain separate rather than being silently relabelled FW.

## Evidence effect

The batch adds one food matrix, three method labels, one independent DOI family, and a new dry-weight Vitamin-C protocol cluster. It creates **zero strict cross-source protocol-identical replications**. It increases source diversity, but does not yet justify rerunning the frozen final prototype or claiming improved source generalisation.
