# CookRisk / CookChem

CookRisk is an academic research project on cooking, food compounds, and evidence-linked interpretation. The repository contains data and modelling experiments, a local Stage C application, Stage B literature evidence, Stage D research contracts, and a separate interactive research demonstrator. None is a clinically validated or consumer-ready risk predictor.

## Current stage (reviewed 2026-11-22)

The project has reached a **working research-prototype and presentation stage**. Its application and evidence explorer are implemented and locally checked. Scientific validation, independent source transfer, expert review, and release hardening remain open. A positive molecular-grouped score does not establish performance on unseen studies.

| Area | Implemented work | Remaining boundary |
| --- | --- | --- |
| Data and molecular features | Conservative preprocessing, compound identity handling, PubChem/SMILES checks, and RDKit descriptors; historical outputs and audits are retained. | Ambiguous identities and source measurement bases require source-level adjudication. |
| Stage A | Historical model benchmarks, concentration-ratio reconstruction audits, and local validation outputs exist. A local 1,104-row canonical candidate is at [`data/final/stageA_final_dataset.csv`](data/final/stageA_final_dataset.csv). | Its provenance and latest local validation need independent review before a transferable or deployment claim. The demonstrator does not designate this file as its approved live dataset. |
| Stage B | An organized interaction-evidence workflow and selected experimental model are documented in [`stageB/README.md`](stageB/README.md) and [`stageB/final_model/README.md`](stageB/final_model/README.md). | Individual evidence and identity decisions still require expert review; outputs are not clinical advice. |
| Stage C | A local non-production application runs using [`stageC/app/README.md`](stageC/app/README.md). | Its pinned Phase 4 context has a documented integrity incident and fails closed. It is not a patient-specific risk service. |
| Stage D | Evidence, exposure-comparison, reviewer-workflow, and nonclinical interpretation contracts are implemented as a foundation; see [`stageD/README.md`](stageD/README.md). | Production reviewer identity, human adjudication, exposure comparability, and a validated clinical score are incomplete. |

## What the latest two commits delivered

- `ec3bb1b` (2026-11-18, **research prototype part 1**) added the research design, execution roadmap, academic review and corrections, evidence-map/report package, and initial local interactive demonstrator. It assembled existing results; it did not establish a new validated model.
- `03c90ef` (2026-11-20, **application building and scientific verification**) expanded the demonstrator into eight modules, added a pinned dataset registry and fail-closed loaders, consolidated model-result provenance and conflicts, documented scientific ACR and statistical limitations, and added browser/UI QA plus tests. Its Phase 6 report records 22 focused tests passing and desktop/tablet/mobile viewport checks. The interface is ready **with documented environment limitations**, not scientifically or clinically validated.

The demonstrator's ten sections are Research Overview, Evidence Explorer, ACR Distributions, Cooking & Compound Patterns, Existing ML Results, Validation & Generalization, Scientific Limitations, Reproducibility & Evidence, ML Error Analysis, and Stage B – Food–Drug Interaction Evidence Explorer. Start and test it using [`research/CookRisk_Interactive_Research_Demonstrator/README.md`](research/CookRisk_Interactive_Research_Demonstrator/README.md). It presents registered records and saved evidence, recalculates error summaries from saved Reconstruction predictions, and does not train models or generate new predictions.

## Stage A data and results

The intended apparent concentration ratio is `100 × C_cooked / C_raw`. It is distinct from total-mass retention, which needs compatible food-mass or cooking-yield evidence. The historical 1,124-row `Retention_Final` benchmark has unresolved target semantics and cannot be merged with concentration-ratio results into one leaderboard.

Local work after the two commits includes a 1,104-row dataset and validation outputs in [`experiments/stageA_final/`](experiments/stageA_final/). The dataset's recorded SHA-256 is `ff7d9cb7388b63d8602b1b26bc0530032b32b3816f6128315eb005a3ae2b78d4`. Its stored targets equal its calculated-ratio field, but this file lacks paired raw/cooked concentration columns, so that equality is not independent primary-paper verification.

The local fixed-XGBoost run reports molecular-grouped pooled OOF R² **0.3301** (mean fold **0.2990**) on 1,104 rows and DOI-held-out pooled OOF R² **−0.4264** (mean fold **−3.6437**) on 494 rows labelled primary-source verified. The other 610 rows were excluded from that DOI evaluation because their source metadata remains unresolved. These are **local run artifacts**, not metrics endorsed by the 2026-11-20 committed evidence consolidation, which marked then-unlocated `0.3301/0.2990` claims unverified. Inspect the [configuration](experiments/stageA_final/validation_config.json), [summary](experiments/stageA_final/final_validation_summary.csv), [molecular folds](experiments/stageA_final/molecular_grouped_fold_metrics.csv), [DOI folds](experiments/stageA_final/source_heldout_fold_metrics.csv), and [out-of-fold predictions](experiments/stageA_final/final_oof_predictions.csv) before citing them. The DOI holdout does not demonstrate unseen-source generalisation.

The committed demonstrator uses the 1,016-row Reconstruction for approved live exploration, with pinned shape/hash and explicit evidence labels. It keeps the historical 1,124-row benchmark, Batch021, Reconstruction, and strict-subset saved results separate. See its [data-selection guide](research/CookRisk_Interactive_Research_Demonstrator/docs/EVIDENCE_AND_DATA_SELECTION.md) and [model-evidence consolidation](research/CookRisk_Interactive_Research_Demonstrator/reports/final_model_r2_consolidation_2026-11-20/FINAL_MODEL_R2_EVIDENCE_CONSOLIDATION.md).

## Run the local applications

- Stage C application: follow [`stageC/app/README.md`](stageC/app/README.md). It uses pinned Stage B/C/D inputs and reports unavailable Phase 4 context.
- Interactive research demonstrator: follow [`research/CookRisk_Interactive_Research_Demonstrator/README.md`](research/CookRisk_Interactive_Research_Demonstrator/README.md) for its Streamlit environment, launch command, and tests.

Research plans and professor-facing report assembly are under [`research/CookRisk_Computational_Research_Prototype/`](research/CookRisk_Computational_Research_Prototype/). Historical Stage A experiments remain under [`stageA/`](stageA/). Preserve their evidence status and split definitions when comparing results.
