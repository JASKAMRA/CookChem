# Consolidation Execution Log

Date: 2026-11-20

## Preservation and scope

The final deliverables are confined to this new folder. A temporary helper was created under reports during generation and removed before final verification; it is absent from the final workspace state. No existing source, result, application, registry, data, dependency or historical artifact was modified. No model training, prediction generation, pooled metric recalculation, Git operation or package installation occurred. Only arithmetic means over saved fold R2 values were computed.

Not accessed: Stage B; restricted Stage C/D source/data; research/EXISTING_RESULTS_METRICS_CATALOG.csv; Retention_Final source CSV.

## Evidence inspected

- Demonstrator diagnostic audit, Phase 2 provenance report, Phase 3 ACR report, Phase 4 statistical review, metric/gap registers and execution log.
- Demonstrator app.py display selection/metric mapping.
- stageA/outputs benchmark result, fold, OOF, QA, tuning records.
- original_target_old_vs_new_reproduction report, fold/OOF/comparison records and sidecar.
- molecular_vs_source_validation_audit summary, fold/OOF/split/report records and sidecar.
- verified_concentration_ratio_reconstruction model report, fold/OOF records and manifest.
- 989_observation_recovery_audit report and molecular fold records.
- Batch021 post1000 component/aggregate comparison, fold, OOF, summary/report, and sidecar.

The Stage A benchmark PDF was not extracted: pdftotext, pypdf, and pdfplumber are unavailable locally. No dependency was installed; CSV/QA/text records were used.

## Checks and outcome

- Stage A: five models, five folds each; 1124 OOF rows/unique IDs per model; all five mean-fold arithmetic values match the saved result rows within 1e-12. No outputs sidecar.
- Tuned-XGBoost replay: pooled 0.275796345509, fold mean 0.394286907872; four selected replay outputs match sidecar. Input SHA absent; conflict remains.
- Batch021 fixed audit: both mean-fold values match summary; six targeted files match sidecar; saved input SHA matches Batch021.
- Reconstruction: five folds per evaluation; means 0.083503672605 and -0.253519411629; pooled rows exist; output sidecar absent.
- Strict subset: five saved folds average -2.462845086753; no pooled OOF found.
- Post1000: 21 component triplets match sidecars; summaries match; three aggregate hashes fail; nine rows agree and 12 conflict. No cause assigned.
- Deliverables: 33 result rows; 349 fold rows; 33 pooled-OOF evidence rows; 33 configuration rows; 17 conflict rows; 11 gap rows.

## Remaining evidence limits

Historical source bytes were not accessed; four baseline configurations are incomplete; tuned XGBoost conflicts; Reconstruction outputs lack digests; strict pooled R2 is absent; post1000 mean-fold/input linkage is unavailable; alternate writer is a hypothesis; friend claims lack supporting records; PDF extraction unavailable.

Consolidation is complete as an evidence record, not scientific adjudication. No conflicting value was selected.
