# Appendix A — Evidence File Index

Paths are repository-relative from the CookChem root. `REPORTED` means the result exists in a saved artifact; it does not imply current regeneration.

## Historical Retention_Final benchmark
- `stageA/input/cookchem_molecular_retention_preprocessed.csv` — reported 1,124-row input snapshot.
- `stageA/outputs/stageA_benchmark_results.csv` — aggregate metrics.
- `stageA/outputs/stageA_fold_results.csv` — fold metrics.
- `stageA/outputs/stageA_oof_predictions.csv` — held-out predictions.
- `stageA/stageA_report.md`, `stageA/stageA_reproducibility.md`.
- `stageA/STAGE_A_REPRODUCTION_AUDIT_2026-11-04.md`, `stageA/STAGE_A_CLOSURE_AND_TRANSITION_2026-11-04.md`.
- `stageA/reports/STAGE_A_HISTORICAL_VS_REGENERATED_COMPARISON_2026-11-04.md`.

## Recovery v0.2–v0.6
- `stageA/recovery_v0_2_0_2026_11_10/target_definition_contract.md`, `dataset_quality_report.md`, `model_comparison.csv`, `stageA_model_comparison.md`.
- `stageA/recovery_v0_3_0_2026_11_10/dataset_expansion_report.md`, `model_comparison.csv`, `fold_results.csv`.
- `stageA/recovery_v0_4_0_2026_11_10/dataset_expansion_report.md`, `model_comparison.csv`, `fold_results.csv`.
- `stageA/recovery_v0_5_0_2026_11_10/FINAL_ITERATION_2_REPORT.md`, `model_comparison.csv`, `fold_results.csv`, `dataset_diversity_report.md`.
- `stageA/recovery_v0_6_0_2026_11_10/source_confounding_report.md`, `feature_ablation_comparison.csv`, `feature_ablation_fold_metrics.csv`, `full_fit_feature_importance.csv`.

## ACR final prototype family
- `stageA/recovery_v0_7_0_2026_11_10/matched_evidence_report.md`.
- `stageA/recovery_v0_8_0_2026_11_10/candidate_b_extraction_report.md`, `iteration_summary.md`.
- `stageA/recovery_v0_9_0_2026_11_10/complete_dataset_coverage_report.md`, `target_measurement_compatibility_report.md`, domain readiness and source-confounding reports.
- `stageA/recovery_v1_0_0_2026_11_10/iteration_summary.md`, `candidate_literature_investigation_report.md`, domain readiness reports.
- `stageA/final_prototype_2026_11_10/manifest.json`, `model_comparison_report.md`, `model_comparison.csv`, `ablation_study.csv`, `fold_metrics.csv`, `oof_predictions.csv` (where present).

## 1,016-row ACR families and evidence tiers
- `stageA/dataset_expansion_1000/batch_021/updated_master_dataset.csv`, `dataset_expansion_report.md`, `post1000_model_comparison.csv`, `post1000_fold_metrics.csv`, `post1000_validation_summary.json`.
- `stageA/verified_concentration_ratio_reconstruction/final_verified_master_dataset.csv`, `final_dataset_eda_report.md`, `model_evaluation_report.md`, `molecular_grouped_fold_metrics.csv`, `source_held_out_fold_metrics.csv`, split and target audits.
- `stageA/molecular_vs_source_validation_audit/validation_comparison_report.md`, `validation_summary.json`, `validation_summary_rows.csv`, `fold_metrics.csv`, OOF prediction table and figures.
- `stageA/dual_dataset_sensitivity_analysis/summary_metrics.csv` and fold/OOF outputs.
- `stageA/989_observation_recovery_audit/989_recovery_audit_report.md`, `molecular_grouped_model_metrics.csv`, source overlap and recovery/exclusion tables.

Full metrics catalog: `research/EXISTING_RESULTS_METRICS_CATALOG.csv`. Complete Stage A figure path inventory: `research/EXISTING_RESULTS_FIGURE_CATALOG.md`.
