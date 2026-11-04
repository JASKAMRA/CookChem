# Official CookRisk Development Roadmap

**Document status:** Official project roadmap supplied by the project owner. This records planned work; it does not certify that any phase is implemented or complete.

# COOKRISK — DEVELOPMENT ROADMAP

## Stage C — Dietary Exposure Estimation

Objective: Estimate the quantity of bioactive compounds present in food, account for cooking-related retention, and calculate dietary exposure.

| Phase    | Name                               | Main Work                                                                                                                               |
| -------- | ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| Phase 1  | Software Foundation                | Stage B integration, database schemas, compound mapping, unit conversion, exposure calculation engine, CLI and testing.                 |
| Phase 1B | Scientific Food Data Acquisition   | Collect quantitative food-composition data from scientific literature and food databases, with source verification.                     |
| Phase 2  | Cooking-Retention Integration      | Integrate Stage A cooking-retention predictions with raw-food compound concentrations and calculate post-cooking amounts.               |
| Phase 3  | Recipe & Meal Exposure Engine      | Develop recipe-level calculations, multiple ingredient handling, serving sizes, consumed fractions and meal-level exposure aggregation. |
| Phase 4  | Uncertainty & Sensitivity Analysis | Account for measurement variability, missing data, prediction uncertainty and sensitivity analysis.                                     |
| Phase 5  | Exposure Validation & Benchmarking | Perform independent calculations, published-data comparisons, reproducibility testing and scientific validation.                        |
| Phase 6  | User-Facing Application            | Develop the website/dashboard with food selection, cooking inputs, exposure reports, source references and export functionality.        |
| Phase 7  | Stage C Finalization               | Complete integration, documentation, testing, versioned release and Stage D handoff.                                                    |

## Stage D — Food–Drug Interaction Risk Integration

Objective: Integrate interaction evidence with estimated dietary exposure to evaluate the potential relevance of food–drug interactions.

| Phase   | Name                                       | Main Work                                                                                                                                                      |
| ------- | ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Phase 1 | Evidence–Exposure Integration Architecture | Integrate Stage B interaction evidence with Stage C exposure estimates, compound/drug matching and source traceability.                                        |
| Phase 2 | Evidence Normalization & Classification    | Organize evidence into human pharmacokinetic, controlled clinical, animal and in-vitro categories. Preserve positive, negative, null and conflicting findings. |
| Phase 3 | Exposure–Evidence Comparability            | Compare dietary exposure with experimental concentrations and doses, normalize units, and account for routes and study conditions.                             |
| Phase 4 | Mechanism-Based Integration                | Integrate CYP enzyme interactions, drug transporters, metabolic pathways, absorption and metabolism mechanisms.                                                |
| Phase 5 | Uncertainty & Evidence Assessment           | Evaluate source quality, study limitations, conflicting findings, missing information and exposure uncertainty.                                                |
| Phase 6 | Risk Interpretation Framework               | Develop a transparent framework for interpreting potential interaction relevance, evidence strength, exposure comparability and limitations.                   |
| Phase 7 | Validation & Benchmarking                   | Validate the framework using published interaction case studies, independent scientific review and reproducibility testing.                                    |
| Phase 8 | Stage D Application & Reporting             | Develop interaction reports, exposure comparisons, mechanism visualizations, evidence tables and uncertainty reports.                                          |
| Phase 9 | Final Integration & Release                 | Integrate Stages B, C and D, perform regression testing, finalize documentation and prepare the reproducible release.                                           |

## Overall Development Sequence

1. Stage A: Cooking-Retention Prediction
2. Stage B: Food–Drug Interaction Evidence Database
3. Stage C: Dietary Exposure Estimation
4. Stage D: Food–Drug Interaction Risk Integration

Note: This is the proposed development roadmap. Phases marked as planned are not yet implemented.
