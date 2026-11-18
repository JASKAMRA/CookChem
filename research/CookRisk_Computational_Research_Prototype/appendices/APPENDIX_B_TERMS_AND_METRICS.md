# Appendix B — Terms and Metric Interpretation

- **ACR:** apparent concentration ratio, `100 × C_cooked / C_raw`, a concentration endpoint, not analyte mass retention.
- **Total-mass retention:** requires compatible concentration and food-mass/yield inputs and documented handling of moisture and cooking liquid. Not inferred from ACR.
- **Retention_Final:** historical Stage A target; original equation is unresolved in available historical contract.
- **Pooled OOF R²:** R² computed across all out-of-fold observations in that evaluation.
- **Mean fold R²:** arithmetic mean of fold-specific R². Not interchangeable with pooled OOF R².
- **MAE / RMSE:** errors are in the target scale and unit used by the specific package. For ACR, these are **ACR percentage points** (the target is reported on a percent scale); this is not relative percentage error. For historical `Retention_Final`, the original unit semantics remain unresolved. Never compare across different targets or incompatible measurement units.
- **Molecular-grouped validation:** no molecular identity overlaps train/test within a fold; DOI families may overlap.
- **Source-held-out / DOI LOSO:** no DOI overlap for held-out source, but DOI may not equal independent lab and compounds can appear across source groups.
- **REPORTED:** value appears in existing source file. **REPRODUCED:** prior independent reproduction is explicitly recorded. **PROPOSED:** future work. **BLOCKED/UNVERIFIED:** evidence gap or mismatch.
