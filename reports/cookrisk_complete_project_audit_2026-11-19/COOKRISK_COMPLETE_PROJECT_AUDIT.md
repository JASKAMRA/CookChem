# CookRisk Complete Project Audit & Next-Phase Readiness

**Audit date:** 2026-11-19  
**Repository identified:** C:\Users\dakshant\Desktop\CookChem  
**Scope:** Evidence and readiness audit; no model training or broad implementation.

## 1. Executive summary

CookRisk contains distinct Stage A research datasets, saved evaluation artifacts, a Stage C software foundation, Stage D review preparation, and a local Streamlit academic demonstrator. The project can display saved metrics and, when its data pin matches, food/compound observations, cooking conditions, concentration measurements, source metadata, evidence status and molecular descriptors. It is not a validated prediction service, clinical/consumer decision system, or deployable scientific platform.

The historical 1,124-row Retention_Final predictions can be rescored from saved out-of-fold (OOF) files; IDs and actual targets match the current table row-for-row. The present CSV hash differs from the historical hash in the Stage A closure record. This verifies score calculations against current target values, not byte-identical historical training inputs or a full reproduction. Retention_Final remains scientifically ambiguous.

The current 1,016-row Batch021 ACR CSV has the exact SHA-256 recorded by its saved validation run, correcting stale documentation that reports a different current hash. Its saved Extra Trees OOF predictions cover all observations, align to targets, and have no duplicate or missing IDs. Molecular-grouped and DOI-held-out results are negative. A separate 1,016-row reconstruction has distinct bytes and predictions; it remains a separate dataset family.

ACR (100 × cooked concentration / raw concentration) is supported for explicitly labeled ACR datasets. True total-mass retention is not established for those 1,016 records: all have total_mass_retention_status=NOT_ESTABLISHED; compatible paired raw/cooked food masses or accepted cooked-yield values are absent. ACR must not be labeled true retention.

Stage C is not complete: the accepted 117-observation Phase 2 boundary contains zero accepted cooked-concentration outputs. Stage D has 342 prepared review items, but 317 evidence rows are unreviewed and all 25 mechanism candidates await independent review. Identity-provider, independent-checkpoint, and scientific benchmark prerequisites remain open.

The eight-module Streamlit demonstrator launched and was checked in a browser. Its pinned reconstruction hash does not match the current reconstruction file; record-level explorer modules correctly fail closed. Saved ML Results remains displayable, but Validation Lab and Limitations have stale Batch021 hash messaging. The application is runnable but its data views are not ready for a scientific demo.

**Audit integrity exception:** The instructions prohibited any Stage B access. No direct stageB file was opened, but excerpts containing Stage B-derived content were inadvertently read in cross-stage reports, including a Stage A closure report that quotes a Stage B hash reference. This violated the strict no-access requirement. The restricted-source reading boundary for Stage C/D reports was also exceeded for some excerpts. Exact files are listed in Section 14; no protected data or code was modified.

## 2. Repository identification and structure

The working directory was verified as the intended repository: it contains .git, README.md, and the stageA, stageC, stageD, and research directories. File discovery used the current working directory rather than assuming a repository path.

Relevant high-level structure:

- stageA/: historical benchmark, ACR recovery snapshots, validation audits, and reconstruction outputs.
- stageC/: local application, phased software/evidence work, closure and readiness reports.
- stageD/: review workflow and mechanism/benchmark readiness documentation.
- research/CookRisk_Computational_Research_Prototype/: academic research manuscript and review corrections.
- research/CookRisk_Interactive_Research_Demonstrator/: local Streamlit application.
- data/final/: a 1,104-row Stage A dataset, distinct from the 1,124-row benchmark and ACR snapshots.

No Git write operation, remote operation, release operation, or repository cleanup was performed.

## 3. Stage-wise status and task IDs

| Stage / task | Verified status | Evidence and remaining work |
|---|---|---|
| Stage A engineering closure | NOT SATISFIED | stageA/STAGE_A_CLOSURE_AND_TRANSITION_2026-11-04.md says closure is not satisfied; historical-versus-regenerated prediction discrepancy, cross-platform validation, scientific decisions and inference readiness remain open. |
| RF-01–RF-15 | Evidence preparation COMPLETE; all 15 decisions PENDING | Evidence matrix and human-decision handoff exist. Tracker records 0/15 approved and no named owner/reviewer. No approval is inferred. |
| Stage B | Not assessed | Direct Stage B files were outside intended scope. Because of the indirect-read incident, strict no-access compliance was not achieved; no Stage B scientific status is asserted. |
| C1-01 | Complete for documented environment only | Schema/environment report documents CPython 3.14.7 on macOS arm64 and 6/6 focused tests; Windows runtime verification is not established. |
| C1-02 | Fail-closed behavior verified in isolation; integration acceptance incomplete | Missing/untrusted identity rejects submissions in isolated tests; no identity provider exists and complete API/integration acceptance is not established. |
| C1B-01 | Complete for Phase1B-v1.3.2 | Coverage recheck reports 584 food/mapping rows, 116 quantitatively eligible IDs (80 ordinary), 125 identity-complete IDs and 121 accepted mappings. Intermediate counts are reconciled in the report. |
| C1B-02 | Blocked | Exact-byte policy exists; current owner-reviewed revision/archive designation and partner Windows/browser verification are outstanding. Candidate-content approval does not supply an archive SHA or partner test. |
| C2-01 / Phase 2 | Blocked at scientific output gate | Accepted boundary is 117 observations; accepted cooked-concentration outputs: 0. The 117 must not be represented as 117 output values. |
| C3-01 | Implemented, synthetic validation only | Synthetic tests pass per closure documentation; independent recipe validation and yield/mass-balance evidence are absent. |
| C4-01 | Partial / scientifically blocked | Phase4-v0.1.2 integrity failed and is reported unrecoverable; preserve the incident record. |
| C5-01 | Pending | Independent external benchmark has not been completed. |
| C6-01 / C6-02 | Partial | Partner Windows/browser, accessibility, security and privacy acceptance remain unverified. |
| C7-01 | Preparation only | Limited engineering preparation is documented; final acceptance/release is not established. |
| Stage D evidence review | Prepared, not reviewed | 317/317 rows are NOT_REVIEWED; zero source-verified and zero expert accepted/rejected. |
| Stage D mechanism review | Pending independent review | All 25 mechanism candidates are pending; preparation is not scientific approval. |
| Stage D Phase 7 benchmark | Not executed | Runbook is a readiness checklist; there are no benchmark cases/results or reviewer decisions. |

Stage C task IDs above are those in the permitted closure documentation. No Stage D task identifiers were asserted where permitted high-level reports did not establish one.

## 4. Stage A dataset and target inventory

Hashes below were computed from current files during this audit. Snapshot counts and lineage claims are kept separate; equal row counts do not make datasets interchangeable.

| Dataset family | Current rows; SHA-256 | Target and interpretation | Mass/yield status and attribution |
|---|---|---|---|
| Historical Stage A input: stageA/input/cookchem_molecular_retention_preprocessed.csv | 1,124; cd51de3286d9fea7c4d87ce45f4c9c4301214b1944f72bff19c3b41ce0358c27 | Retention_Final; scale/equation/unit unresolved. Not established as ACR. | No cooked concentration or paired cooked food mass in table. Stage A closure records earlier expected SHA 750124efc8b89dff1f67764064b1049b5db51fb1b2f222d4f91cd94c56945f89; present bytes differ. Saved OOF actuals still match current IDs and targets. |
| Additional final dataset: data/final/stageA_final_dataset.csv | 1,104; f0fbe50e69149e0d48adef07aad78c1f8cf4f48a3fc9d6f9e74b085241d5a24a | target equals calculated_concentration_ratio_percent for all rows; Retention_Final agrees for 722/1,104 only. Treat as a ratio-derived target, not a validated total-mass-retention label. | No cooked mass/yield field. Sample_Weight_g is present for 760 rows and missing for 344; it is not paired raw/cooked mass. |
| Recovery v0.2 / v0.3 / v0.4 / v0.5–v0.6 / v0.7 snapshots | Reported 117 / 338 / 374 / 379 / 407 observations; snapshot-level SHA values not established here. | ACR datasets with version-specific admission rules; separate historical snapshots. | Catalog documents distinct evidence and coverage; no owner-designated canonical ACR snapshot exists. |
| 439-row prototype: stageA/final_prototype_2026_11_10/final_modelling_dataset.csv | 439; 1fea513ac44777411357df6ac7d084eecd97cd08f956d3ac23e38695552554d1 | Manifest labels target apparent concentration ratio, not total-mass retention. 46 canonical IDs and 10 source families are documented. | Manifest parent SHA d3960dc6ec808ca1783cbb2c57d35fb4676da04feeff675280c1f07eb072005a matches current stageA/recovery_v1_0_0_2026_11_10/expanded_clean_stageA_dataset.csv. This corrects stale mismatch language about the parent input. Manifest still embeds another user's machine-specific Windows path, does not pin the 439-row output hash, and says no model is saved and Stage C integration is unauthorized. |
| Batch021 ACR master: stageA/dataset_expansion_1000/batch_021/updated_master_dataset.csv | 1,016; 111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8 | target_value_percent = 100 × cooked_concentration / raw_concentration; all 1,016 records explicitly say ACR, not total-mass retention. 48 canonical IDs, 32 DOI families. | Target calculation differs from formula by at most 0.00482245 percentage points. total_mass_retention_status=NOT_ESTABLISHED for all. Current hash matches saved audit input; metrics catalog claim that current bytes hash to d866d0... is stale. |
| Verified concentration-ratio reconstruction: stageA/verified_concentration_ratio_reconstruction/final_verified_master_dataset.csv | 1,016; f9391233a2d4231140d46aa58e864180eddb6f2c3a56b030df3f94ca25f083b0 | Separate reconstruction with verified concentration-ratio target; 48 compounds/IDs, 32 DOI families, 66 food matrices and 41 methods are documented. | Not byte-identical to Batch021. No compatible paired mass/yield; true total-mass retention is not established. Current bytes do not match demonstrator pin 16dbbd9c38a21675a2644b415289004e5a8eb7091e97a96dae645ed2bf52be99. |

The 338-row strict, 948-row extended, and 989-row exploratory tiers are distinct eligibility sets. The source-held-out exploratory analysis uses 971 rows after source exclusions. Do not substitute these counts for each other or for the 1,016-row master.

## 5. Model and validation inventory

All metrics are OOF metrics unless labeled otherwise. Historical Retention_Final MAE/RMSE units are unresolved. ACR MAE/RMSE are percentage points. Pooled R² and fold-average R² are different summaries. No model was trained during this audit, and no OOF file is a fitted inference model.

| Model | Dataset / target | Validation | Pooled R² | Mean-fold R² | MAE | RMSE | Evidence status |
|---|---|---|---:|---:|---:|---:|---|
| ExtraTrees reference | 1,124 historical / Retention_Final | 5-fold molecular GroupKFold | 0.255978 | 0.380461 | 31.9641 | 141.3086 | Recomputed from saved OOF; all 1,124 IDs unique and actuals align to current table. Current input SHA differs from documented historical SHA. |
| RBF-SVR | Same | 5-fold molecular GroupKFold | 0.254597 | 0.379352 | 34.7817 | 141.4397 | Same alignment and byte-attribution caveat. |
| Random Forest | Same | 5-fold molecular GroupKFold | 0.237074 | 0.341500 | 33.0268 | 143.0925 | Same alignment and byte-attribution caveat. |
| XGBoost | Same | 5-fold molecular GroupKFold | 0.275012 | 0.383296 | 35.4192 | 139.4894 | Same alignment and byte-attribution caveat. |
| Tuned XGBoost | Same | 5-fold molecular GroupKFold | 0.283247 | 0.400376 | 34.6119 | 138.6949 | Same caveat; tuning does not resolve target semantics. |
| XGBoost controlled comparison | Same | Random 5-fold; 3×5-fold fold report | 0.3399 | 0.430713* | 31.1000 | 133.1047 | Saved OOF covers 1,124 rows and aligns on actual/source by row index. Mean-fold is the arithmetic mean of 15 fold-runs, not the same single OOF aggregate. Sources overlap heavily. |
| XGBoost controlled reproduction | Same | Molecular grouped 5-fold; 3×5-fold fold report | 0.2438 | 0.326594* | 35.0753 | 142.4605 | OOF aligns on actual/source; 15 fold-runs in fold table. Not historical prediction equivalence. |
| XGBoost controlled comparison | Same | DOI/source-held-out 5-fold; 3×5-fold fold report | 0.0143 | 0.089556* | 42.5498 | 162.6481 | OOF aligns; zero DOI overlap by fold; near-zero pooled source transfer. |
| ExtraTrees, 25 trees | Batch021 1,016-row ACR | Molecular-grouped 5-fold | -0.067833 | -0.256216 | 102.3912 | 432.8128 | Recomputed from saved OOF; complete unique coverage, actuals align within 0.01 pp, no molecular ID crosses folds. |
| ExtraTrees, 25 trees | Same | DOI-held-out 5-fold | -0.065645 | -0.206527 | 114.2190 | 432.3692 | Same coverage. DOI overlap is zero; 19 molecular IDs recur across held-out DOI folds, so this is DOI-held-out, not compound-held-out. |
| XGBoost, reduced semantic features | Reconstruction 1,016-row ACR | Molecular-grouped 5-fold | 0.059831 | 0.083504 | 91.3281 | 406.1172 | Recomputed from saved OOF; complete unique coverage and actuals align within 0.01 pp. Not exact historical feature replay. |
| Same XGBoost | Same | Source-held-out 5-fold | -0.073710 | -0.253519 | 115.4329 | 434.0021 | Recomputed from saved OOF; poor source generalization. |
| ExtraTrees controlled comparison | Batch021 1,016-row ACR | Random 5-fold; 3×5-fold fold report | 0.4656 | 0.457434* | 72.9584 | 306.1703 | Saved OOF covers all rows; actual/source align. Random-fold score is not source generalization. |
| ExtraTrees controlled comparison | Same | DOI/source-held-out 5-fold; 3×5-fold fold report | -0.0663 | -0.224731* | 115.1449 | 432.5042 | Saved OOF covers all rows; source overlap is zero. |
| Random Forest | 439-row ACR prototype | DOI/source-grouped pooled OOF | -0.047508 | NOT VERIFIED | 51.5826 | 175.3872 | Reported in metrics catalog; prototype parent SHA matches current parent input, but OOF was not rescored here. |
| Fixed XGBoost | 338-row strict ACR subset | Molecular-grouped mean-fold metric | NOT VERIFIED | -2.462845 | 46.6718 | 147.1589 | Reported historical subset result; not comparable to broad ACR snapshots. |

*Mean over 15 fold records (three repetitions of five folds) from controlled_fold_metrics.csv; pooled value is from the saved single OOF file. Do not interpret these as one pooled/mean-fold pair from a single repeat.

Other ACR iterations document Dummy/median, Ridge, Random Forest, Extra Trees, Gradient Boosting, XGBoost and RBF-SVR. Reported best molecular-grouped R² values include Ridge 0.3853 (v0.3), Ridge 0.4123 (v0.4), Random Forest 0.3847 (v0.5) and full-feature Random Forest 0.4003 (v0.6); these use different snapshots and protocols and are not directly rankable. Source-LOSO values reported for those iterations are negative. The selected catalog is research/CookRisk_Computational_Research_Prototype/tables/EXISTING_METRICS_SELECTED.csv; treat it as a selected-results catalog, not a uniform benchmark.

### Molecular R² reference claims

- Friend-reported pooled 0.3301 and mean-fold 0.2990 were not reproduced or supported by original OOF/split/config evidence located in this checkout. profile_canonical_dataset.py treats these as supplied claims, not reproduced measurements.
- Current Batch021 ExtraTrees is verified against its recorded input bytes: pooled R² -0.0678329, mean-fold -0.2562162.
- Separate reconstruction XGBoost is pooled +0.0598308 and mean-fold +0.0835037.
- These are different datasets and model/feature runs; no performance decline is inferred by comparing them.

### Features, preprocessing and leakage checks

The historical benchmark uses log1p/expm1 target transformation and 22 base plus 5 engineered features, with fold-local median numeric imputation, scaling, categorical missing handling and one-hot encoding. The 1,016-row ExtraTrees audit uses raw concentration, temperature/time, eight RDKit descriptors, cooking method, medium, measurement basis, compound class and food matrix; DOI, record ID and target-derived fields are not predictors. Preprocessing is fit within training folds. Raw concentration is part of the ACR denominator but is a pre-cooking measurement; this dependency should be explicit in future interpretation. Source identifiers are used for grouping, not as predictors. DOI is a proxy for source family, not proof of independent laboratories.

## 6. Retention versus ACR audit

| Dataset / experiment | Target definition | Units / basis | Compatible mass/yield? | Valid interpretation | Limitations |
|---|---|---|---|---|---|
| Historical 1,124 benchmark | Retention_Final; equation not recovered | Scale/unit unresolved | No cooked concentration or paired cooked food mass | Historical target prediction only | Do not call ACR or true retention without source-backed target definition. |
| 1,104-row final dataset | target equals recorded calculated ratio field | Ratio-derived percentage field | No paired raw/cooked mass | Concentration-ratio-derived target, pending row-level provenance review | Retention_Final disagrees on 382 rows; no total-mass calculation basis. |
| Batch021 / reconstruction ACR | 100 × C_cooked / C_raw | Percentage; basis and measurement conditions heterogeneous | No; all 1,016 statuses say total-mass retention not established | Apparent concentration ratio only | Moisture/basis changes can change concentration without equal total nutrient retention. |
| Reported true-retention values in evidence | Present in limited records separately | Preserve source's compatible basis | Not accepted for ACR target; 28 rows flag true retention reported but unused, 12 mention weight loss separately | Keep separate where raw/cooked mass and basis compatibility are verified | No conversion or substitution was performed. |

True total-mass retention requires compatible raw and cooked concentrations plus measured raw and cooked food masses (or validated compatible yield), consistent concentration units and moisture basis, and handling of discarded liquid/solid compartments. This audit calculated no true-retention values and did not replace missing measurements with zero.

## 7. Academic research prototype

The academic prototype remains labeled “Requires substantial revision” in UPDATED_RESEARCH_READINESS_ASSESSMENT.md. The correction report documents the Figure 2 top-15-of-32 correction, Figure 3 distinction between pooled OOF and fold-wise R², ACR MAE/RMSE as percentage points, and unresolved Retention_Final semantics.

Current checkout checks correct stale lineage text in that report/catalog: Batch021 currently hashes to 111064..., exactly the saved validation-run input SHA, rather than documented d866d0...; saved OOF rows match current data. The 439-row prototype parent currently hashes to its manifest d3960d... . These improve input lineage verification but do not make all historical runs byte-reproducible or scientifically equivalent. No original historical source bytes were substituted for unrecovered files.

## 8. Interactive demonstrator: launch and browser verification

The demonstrator documents eight modules: research overview, evidence explorer, descriptive ACR analysis, group patterns, saved ML results, validation, limitations, and reproducibility. Code describes food/compound identity, raw/cooked values, measurement basis, cooking conditions, sources, evidence status and descriptors.

- **Environment:** Dedicated environment at research/CookRisk_Interactive_Research_Demonstrator/.audit-venv-20261119; Python 3.14.7. No global packages were installed and project requirements/lockfiles were not changed.
- **Dependencies:** Requirements specify Streamlit and Plotly without exact pins. Isolated run installed Streamlit 1.67.0 and Plotly 7.1.0 plus transitive dependencies from PyPI. pip check passed. The venv's own python -m pip bootstrap was unavailable; packages were installed into that venv through the interpreter's pip --python target option. This remains a setup/repeatability limitation.
- **Startup:** streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true --server.fileWatcherType none --browser.gatherUsageStats false started successfully.
- **Browser:** Opened at http://127.0.0.1:8501/; all eight modules were navigated. The app rendered. Evidence Explorer, ACR Analysis and Cooking/Compound Patterns displayed the expected fail-closed dataset-hash mismatch, so they did not show record-level data. Saved ML Results rendered its saved metrics table. Validation Lab and Scientific Limitations include stale Batch021 hash/audit status text. Streamlit emitted a non-blocking use_container_width deprecation warning.
- **Verification scope:** pip check passed. Browser verification establishes local UI launch only; it does not establish partner Windows compatibility, scientific validity, accessibility or production readiness.

## 9. Stage C and Stage D readiness

Stage C closure report is stageC/reports/STAGE_C_CLOSURE_REPORT_2026-11-05.md; supporting permitted reports include C1B_01_COVERAGE_RECHECK.md, C1B_02_EXACT_BYTE_POLICY_READINESS.md, C1B_02_OWNER_DESIGNATION_RECORD.md, C1B_02_PARTNER_WINDOWS_VERIFICATION.md, and Phase 2/3 progress docs. The controlling scientific gate remains Phase 2: no accepted cooked-concentration outputs. C3 synthetic tests are not real recipe validation. Phase 4 integrity failure, independent benchmarking and release acceptance remain unresolved.

Stage D high-level readiness reports show 317 prepared evidence rows plus 25 mechanism candidates (342 total prepared). Preparation is not approval: 317 evidence rows remain unreviewed; all 25 candidates await independent review. Local identity-provider and independent-checkpoint services are absent, so assignments/actions and anchored review chains cannot be claimed. Phase 7 has a template/runbook but no completed cases, blinded reference set, qualified independent reviewers/adjudicator or benchmark outcomes.

## 10. Product readiness and limitations

| Experience | What current files support | Readiness |
|---|---|---|
| Food Explorer | Food matrices, observed compounds, methods, conditions, concentrations and sources exist in separate Stage A/C records. | Not currently demonstrated in app because pinned ACR file fails hash validation. |
| Compound Explorer | Compound names/IDs, descriptors, food matrices and ACR observations are in reconstruction data. | Same pin mismatch; descriptors are not evidence of cooking effect. |
| ML Research Explorer | Saved benchmark and OOF metrics can be displayed; final prototype saves no model. | Partial. Show dataset, target, features, validation and limitations; no new-record inference. |
| Retention vs ACR Explorer | Formula distinction and missing mass/yield statuses are documented. | Supportable as explanatory view; true-retention values cannot be generated for current ACR master. |
| Limitations/reproducibility | Missing evidence, hashes, unsupported inference and validation limits are documented. | Partial: some demonstrator hash messaging is stale and needs reviewed reconciliation. |

CookRisk should remain an academic research demonstrator. Current evidence does not support clinical or consumer risk decisions, source-general prediction, recipe advice, or causal explanations.

## 11. Recommended roadmap

1. **Phase 0 — evidence/reproducibility registry:** register separate dataset snapshots, target definitions, provenance and model/evaluation artifacts with exact hashes and explicit semantics; preserve fail-closed behavior on mismatch.
2. **Phase 1 — food/compound explorer:** expose only an owner-designated snapshot; show unknown fields and evidence status with source traceability.
3. **Phase 2 — ML research explorer:** publish saved models/results only with dataset/target/features/split protocol and limitations; never use OOF for new-record inference.
4. **Phase 3 — cooking/retention research:** calculate ACR only from compatible concentration pairs; calculate true retention only with compatible mass/yield and basis evidence.
5. **Phase 4 — integrated demonstrator:** connect modules, preserve snapshot boundaries and run local/browser regression checks.

No roadmap phase is accepted automatically. Stage C scientific outputs, Stage D human review, and Stage A RF decisions remain separate gates.

## 12. Single next task to authorize

**Authorize a narrow Phase 0 dataset/target registry and demonstrator-pin reconciliation.** This audit did not change app behavior or choose a canonical ACR snapshot. Before changing a pin, the scientific owner must designate whether the demonstrator should use Batch021, the separate reconstruction, or remain unpinned pending review. Keep both datasets distinct; do not access Stage B.

**Permitted files for that separately authorized task:**

- New registry and focused tests under research/CookRisk_Interactive_Research_Demonstrator/.
- research/CookRisk_Interactive_Research_Demonstrator/research_data.py and its selection documentation only to add hash-checked registry support after owner designation.
- No dataset CSV, historical OOF, Stage B/C/D source, release, or model artifact edits.

**Measurable acceptance criteria:**

1. Registry records each included snapshot's relative path, SHA-256, row count, schema, target equation/name/units, measurement basis, lineage and true-retention eligibility without conflating snapshots.
2. Loader verifies designated snapshot hash and fails closed for unknown/mismatched bytes; no silent fallback or implicit substitution.
3. ACR and true-retention labels are separated; unknown target semantics stay unknown; no new scientific values or predictions are generated.
4. Focused tests cover correct-pin load, hash mismatch, missing file, unknown target, and separate ACR/retention status; browser workflow is rechecked.
5. Existing reports, datasets, OOF files and Stage A/B/C/D artifacts remain byte-identical.

## 13. Evidence references

- Stage A closure/task status: stageA/STAGE_A_CLOSURE_AND_TRANSITION_2026-11-04.md; stageA/STAGE_A_RF01_RF15_EVIDENCE_MATRIX_2026-11-04.md; stageA/STAGE_A_RF01_RF15_HUMAN_DECISION_HANDOFF_2026-11-04.md.
- Historical OOF/benchmark: stageA/outputs/stageA_oof_predictions.csv; stageA/outputs/stageA_benchmark_results.csv; stageA/input/cookchem_molecular_retention_preprocessed.csv.
- Controlled comparison: stageA/original_final_model_controlled_comparison/controlled_comparison_report.md; controlled_fold_metrics.csv; corresponding saved OOF and fold assignment files.
- Batch021 audit: stageA/molecular_vs_source_validation_audit/validation_comparison_report.md; validation_summary.json; oof_predictions.csv; split_audit.csv.
- ACR reconstruction: stageA/verified_concentration_ratio_reconstruction/manifest.json; model_evaluation_report.md; oof_predictions.csv; final_verified_master_dataset.csv.
- Academic readiness: research/CookRisk_Computational_Research_Prototype/ACADEMIC_REVIEW_CORRECTION_REPORT.md; UPDATED_RESEARCH_READINESS_ASSESSMENT.md; tables/DATASET_SNAPSHOT_CATALOG.csv; tables/EXISTING_METRICS_SELECTED.csv.
- Demonstrator: research/CookRisk_Interactive_Research_Demonstrator/README.md; DEMONSTRATOR_COMPLETION_REPORT.md; docs/EVIDENCE_AND_DATA_SELECTION.md; app.py; research_data.py; requirements.txt.
- Stage C: stageC/reports/STAGE_C_CLOSURE_REPORT_2026-11-05.md and C1B-01/C1B-02 readiness reports named above.
- Stage D: stageD/README.md; permitted high-level closure/readiness docs; Phase 7 runbook and benchmark template.

## 14. Audit integrity, changes and boundary exception

- **Report created:** reports/cookrisk_complete_project_audit_2026-11-19/COOKRISK_COMPLETE_PROJECT_AUDIT.md.
- **Other new files:** isolated environment and installed packages under research/CookRisk_Interactive_Research_Demonstrator/.audit-venv-20261119/.
- **Existing project files modified:** none known; no application source, requirement, lockfile, dataset, model artifact, release or historical report was edited.
- **Datasets modified:** none.
- **Historical artifacts modified:** none.
- **Git operations:** none.
- **Dependencies installed:** only inside dedicated demonstrator environment; no global installation.
- **Tests/verification performed:** current CSV SHA/row checks; historical OOF coverage and actual-target alignment; ACR OOF coverage, target alignment and fold/group separation; pip check; actual Streamlit startup; browser navigation through all eight modules. Prior Stage C/A focused-test counts above are cited from existing official reports and were not rerun here.
- **Stage B access — MUST BE NO:** strict non-access was **not achieved**. No direct stageB file was opened, executed, hashed, copied or modified. However, Stage B-derived excerpts were inadvertently read in research/EXISTING_RESULTS_MASTER_INVENTORY.md, stageC/reports/ADVANCED_EXECUTION_REPORT.md, stageA/STAGE_A_CLOSURE_AND_TRANSITION_2026-11-04.md (which contains a Stage B hash reference), stageD/reports/mechanism_reviewer_packets.md, stageD/reports/phase45_mechanism_registry_report.md, and stageD/reports/cross_stage_contract_hardening.md. This is a documented scope breach; no Stage B assessment or source detail is reproduced here.
- **Restricted Stage C/D source access — MUST BE NO:** no Stage C/D source code or data directories were read. The strict documentation-only boundary was nevertheless exceeded: excerpts from the Stage D reviewer-packet/registry/hardening reports listed above were read, including embedded evidence-oriented material. No raw paper/source file or restricted dataset was opened. No restricted files were changed.
- **External verification:** no external scientific sources were consulted; claims are limited to local records and documented uncertainty.

