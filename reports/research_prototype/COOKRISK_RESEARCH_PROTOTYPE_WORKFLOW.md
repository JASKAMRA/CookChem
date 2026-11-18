# CookRisk Research Prototype Workflow

**Planning blueprint — 17 November 2026**  
This document proposes how the existing CookChem work can be connected into a defensible research prototype. It is supplementary planning material; it does not amend the official roadmap or certify stage completion.

## 1. Purpose and scientific boundary

CookRisk should help a researcher trace a food, a bioactive compound, a cooking process, the available composition evidence, and any relevant documented food–drug interaction evidence. It should show calculations only when the source measurements and their units, sample states, preparation conditions, and denominators are compatible. Every displayed value should lead back to its source and validation status.

The prototype is a research and evidence-navigation tool. It is not a clinical decision system, dietary prescription, safety score, or substitute for clinical review. Software passing tests establishes technical behavior; it does not establish scientific validity.

## 2. Quantity definitions that must stay separate

1. **Apparent concentration ratio (ACR):** `100 × C_cooked / C_raw`, only for the same analyte and compatible measurement bases. It is a concentration ratio, not mass retention.
2. **Total-mass retention:** `100 × (C_cooked × M_cooked) / (C_raw × M_raw)`. It requires compatible concentrations and measured food masses (or a validated yield conversion) before and after cooking.
3. **Cooked concentration:** the analyte concentration in the prepared food, with its stated unit and as-eaten basis. It needs a compatible raw reference and a directly supported retention/ratio or direct cooked measurement.
4. **Bioavailability:** the fraction or amount absorbed by a person. Food-composition and cooking measurements alone do not establish it.
5. **Human exposure:** consumed concentration multiplied by the amount actually eaten, with serving, consumed fraction, and relevant unit conversions recorded. A body-weight-normalized dose additionally requires body weight and a defined exposure context.
6. **Documented food–drug interaction:** a traceable report or study of an interaction, including its population, formulation, dose, and evidence quality. It does not show that ordinary food intake reaches the study exposure.
7. **Clinical risk:** a clinical outcome or decision requiring a validated clinical model and context. CookRisk must not infer it from an ACR, composition value, or interaction mention.

No complement such as `100 − loss%` may be silently treated as a measured retention factor. Concentration ratio, yield, mass retention, and direct cooked concentration each retain separate fields and provenance.

## 3. Evidence-based current-state snapshot

The following is a planning snapshot from repository reports, not a fresh validation of every source dataset. Stage B was intentionally not accessed; its status and contents are therefore unverified in this pass.

| Area | Documented state | What it means for the prototype |
|---|---|---|
| Stage A | The recovery log dated 11 Nov reports 1,016 observations from 32 DOI families. Strict protocol-identical cross-source replications are reported as zero; source-held-out R² is negative for the evaluated models. No deployable serialized model is documented. | Model outputs are experimental and must not be presented as generalizable predictions. Keep inference disabled until an exact, reviewed training snapshot, artifact, preprocessing, and external validation are available. |
| Stage B | Protected source files were not inspected. Prior reported counts have not been freshly verified. | Integrate only through a documented, authorized custodian-provided interface. Do not mirror protected data in this planning work. |
| Stage C | The Phase 1B report documents 584 mappings; Phase 2 reports 117 observations and zero accepted cooked-concentration estimates. Recipe/meal and uncertainty software exists, with missing compatible evidence withheld. | The current demo can show raw-reference evidence, calculation status, and why estimates are unavailable. It must not manufacture a cooked result. |
| Stage D | Reports index 317 evidence records and 25 mechanism candidates (342 total), all pending, with zero decisions in the latest handoff. Identity and independent checkpoint services are not live; benchmark approval remains pending. | Show evidence and review status transparently. Do not display pending machine triage as human approval. |
| Official sequence | The official repository roadmap covers Stages A–D. It does not define official Stages E–G. | Follow official stage/task gates. Any integration tasks below use supplementary `RP-*` planning IDs only. |

Useful report references: `stageA/CONTINUOUS_RECOVERY_LOG.md`; `stageA/final_prototype_2026_11_10/model_scope_and_limitations.md`; `stageA/diagnostics_v0_1_0_2026_11_10/FINAL_STAGE_A_DECISION.md`; `stageC/README.md`; `stageC/app/README.md`; `stageC/reports/phase2/PHASE2_RETENTION_EVIDENCE_ACQUISITION_REPORT_2026-11-05.md`; `stageD/README.md`; `stageD/reports/closure/QUALIFIED_REVIEW_READINESS_EXECUTION_2026-11-05.md`; and `stageD/reports/closure/COOKRISK_CYCLE4_FINAL_LOCAL_HARDENING_AND_HANDOFF_2026-11-05.md`.

## 4. Stage-wise research and engineering workflow

### Stage A — cooking-related concentration research

**Purpose:** investigate whether source-supported experimental data can predict an explicitly defined cooking outcome for a compound, food matrix, and protocol.

**Workflow:**

1. Freeze and identify each source snapshot by path, version, byte hash, retrieval/citation, and inclusion/exclusion log.
2. Validate analyte identity and chemical structure; preserve the source identifier and the standardized identifier as separate values. Record unresolved identity instead of guessing.
3. Normalize the target only after recording original value, unit, sample state, denominator, method, cooking conditions, and whether the outcome is ACR, total-mass retention, yield, or another quantity.
4. Produce a data-quality report for missingness, duplicated measurements, repeated study families, outliers, and source concentration. Do not delete outliers solely to improve metrics.
5. Build a simple baseline first. Add molecular descriptors, food-matrix/cooking features, and fingerprints only as documented feature groups. Fit all learned preprocessing inside each training fold.
6. Compare prespecified regressors and feature ablations. Tune only within training folds. Keep molecular grouped validation and source-held-out validation separate and report both.
7. Report fold-level MAE, RMSE, R², sample counts, group counts, and uncertainty. Add source-family leave-one-out evaluation, error analysis by food/method/compound, outlier sensitivity, and a leakage audit.
8. Require independent protocol-matched replication before claiming external scientific validation. Compare predictions with a direct baseline and state when the evidence cannot support a model.
9. Package inference only after data hash, code/configuration, environment, feature schema, preprocessing, estimator artifact, and prediction output contract all verify together.

**Current implementation/evidence:** reports describe benchmark and recovery work, but the latest recovery log reports negative source-held-out performance and no strict cross-source replication. This supports research-only exploration, not deployment. No retraining or Stage A data/model execution was performed for this blueprint.

**Inputs:** licensed/approved source observations; compound structures; food/matrix identity; protocol and measurement metadata. **Outputs:** immutable analysis snapshot, fold assignments, metrics, diagnostics, model card, and (only if gates pass) versioned inference package.

**Acceptance:** exact snapshot reproducible; no source/group leakage; fold-level metrics regenerated; target meaning is consistent; independent validation is reported; uncertainty and domain limits are explicit; package hashes and environment reproduce. Passing software tests alone is insufficient.

### Stage B — food–drug evidence and knowledge base

**Purpose:** identify foods, compounds, drugs, interaction claims, mechanisms, and source evidence with provenance and uncertainty.

**Workflow:** authorized custodian supplies a reviewed data contract; each entity and relationship has stable IDs; evidence passages/study metadata are traceable; interaction direction, study type, dose/formulation/population, and evidence quality are encoded; conflicting or absent evidence remains explicit; qualified review is recorded separately from extraction.

**Current status:** inaccessible in this planning pass by instruction. Do not infer a current count or completeness. **Next work:** Stage B owner/custodian validates the contract, approved export and identity rules in its authorized environment. **Acceptance:** source coverage and identifiers audited by the authorized custodian; conflicts and missing evidence represented; independent reviewer decisions recorded; exported integration payload signed/versioned. No Stage B file was read or inspected to prepare this plan.

### Stage C — composition, cooking, recipe and uncertainty

**Purpose:** connect ordinary-food composition to cooking and meal calculations while refusing unsupported conversions.

**Workflow:**

1. Preserve the release-linked raw composition rows, source, food class, identity qualification, unit, sample state, moisture/basis, and acceptance category.
2. For each food–compound–preparation combination, assess identity, raw measurement basis, cooked measurement or valid retention evidence, units, cooking conditions, yield/mass, and uncertainty independently.
3. Compute cooked concentration only when each required compatibility gate passes. Preserve raw reference separately from cooked evidence and label ordinary-food versus ingredient/beverage contexts.
4. Calculate recipe/meal quantities with explicit ingredient mass, cooked yield, serving size, consumed fraction, and leftovers. Keep the arithmetic trace and source records in output.
5. Propagate only supported uncertainty inputs. If a distribution or bound is unavailable, report it unavailable; do not fabricate an interval.
6. Validate unit conversions, mass balance, state transitions, zero/missing inputs, and provenance with synthetic fixtures and independent hand calculations.

**Current evidence:** Phase 1B-v1.3.2 reports 584 rows and its own eligibility counts; Phase 2-v0.3.1 reports 117 observations and zero accepted cooked concentration estimates. Phase 3 software exists; Phase 4 has a documented integrity incident and fails closed for affected data. These statements reflect the named reports, not a fresh dataset audit.

**Next:** resolve only evidence-backed compatibility rows, preserve the Phase 2 accepted boundary until authorized evidence supports change, validate safe app degradation, and close official task gates in order. **Acceptance:** no unsupported estimate; every accepted estimate has source, formula, units, sample states, method, yield/mass basis, and reproducible calculation; raw-reference and cooked-supported outputs remain distinct.

### Stage D — evidence review and scientific quality control

**Purpose:** manage qualified review, identity decisions, evidence traceability, comparability, and the gated scientific benchmark.

**Workflow:** assign stable record IDs to authorized reviewers; verify reviewer qualification/authorization; capture source references, decision, rationale, date, signature/audit event; validate transitions and tamper detection; represent contradictions and missing evidence; require owner-approved locked benchmark cases and thresholds before scientific execution.

**Current evidence:** the latest cited handoff reports 342 indexed records (317 evidence +25 candidates), all pending and zero decisions; provider/checkpoint services and Phase 7 approval are absent. **Next:** owner provisions real identity/checkpoint services and qualified reviewers; reviewers return actual decisions. **Acceptance:** authorization works with real configuration; all records trace to source; genuine decisions have complete rationale and audit integrity; independent benchmark is reproducible and approved. Synthetic tests establish software behavior only.

### Research prototype integration (supplementary, not an official stage)

**Purpose:** expose the stages through a transparent researcher workflow only after their gates permit each output. Integration begins with read-only, source-linked evidence browsing and supported raw-reference recipe arithmetic. Prediction, cooked-concentration, or interaction interpretation panels remain disabled or clearly unavailable until corresponding scientific and human gates pass.

**Acceptance:** the UI never conflates availability with validation; every result has a provenance trail and status; protected inputs require authorized adapters; service outages fail closed; no arbitrary risk score or clinical recommendation appears.

## 5. Research evaluation and test plan

| Test layer | Examples | What a pass establishes | What it does not establish |
|---|---|---|---|
| Unit | Identity parsing, units, basis gates, formula arithmetic, missing values, recipe serving fractions, schema and state transitions | Local code behavior matches contract | Source measurements are scientifically valid |
| Data integrity | Snapshot byte hashes, schema, duplicate IDs, source links, allowed categories, null semantics | Packaged data conforms to documented contract | Completeness of inaccessible sources |
| Model validation | Molecular-group split, source-family split, fold leakage checks, baselines, ablation, fold metrics, calibration/sensitivity | Performance under named internal validation designs | Generalization to a new laboratory/protocol |
| Scientific validation | Protocol-matched independent replication, measurement comparability, blinded predictions, predefined acceptance thresholds | Evidence supports a specified claim/domain | Clinical effectiveness or safety |
| Integration | Raw evidence to recipe output; unavailable provider/data paths; timeouts and corrupt manifests | Services connect and degrade safely | Scientific correctness beyond supplied evidence |
| End-to-end | Supported raw reference; unsupported cooking scenario; conflicting source; pending interaction evidence; missing runtime service | User-visible states preserve the contract | Stage completion or owner approval |
| Reproducibility | Exact commands, environment lock, input hashes, config, output hashes, repeated execution | Same declared process can be rerun | Validity of the assumptions encoded in that process |

Scientific evaluation must include unseen-source performance and a predeclared comparison baseline. Negative or unstable metrics must be reported as such. Missing cases must be tested explicitly: unresolved identity, dry-weight versus as-received basis, incompatible units, absent yield, qualitative-only evidence, contradictory sources, novel cooking method, unseen DOI family, and unavailable auth/checkpoint/data services.

## 6. Minimum defensible demonstration

1. Search/select a food and compound only from identity-qualified records.
2. Show the raw composition value with source, unit, food category, state/basis, and acceptance status.
3. Select a preparation scenario and see each compatibility gate and its evidence.
4. If cooked evidence is unsupported, show “No scientifically compatible cooked estimate available” and the missing evidence; do not display a placeholder prediction as fact.
5. For supported recipe arithmetic, enter ingredient mass, cooked yield, serving amount, consumed fraction, and leftovers; display the calculation and provenance.
6. Show interaction evidence as a source-linked evidence summary with study context and review state, not as an individualized risk score.
7. Export a reproducibility bundle containing input IDs, source citations/IDs, calculation trace, software/data version, and unavailable-field explanations.

The Stage A prediction panel should be hidden or labelled experimental and unavailable for decision use until the model gate is met. With current documented Stage C evidence, cooked concentration is unavailable for the accepted Phase 2 boundary.

## 7. Critical dependencies and required decisions

- **Owner:** confirm which official task register/release is authoritative for execution; approve scientific target definitions and Stage D benchmark thresholds; designate archive/revision for C1B-02 without changing its original acceptance criteria.
- **Stage A data/model owner:** provide exact approved snapshot, target and preprocessing lineage; resolve RF decisions and obtain independent protocol-matched data before inference release.
- **Stage B custodian:** decide and provision an authorized, least-privilege contract/export; no Stage B content was accessed for this plan.
- **Scientific reviewers:** resolve measurement basis and cooking compatibility; approve only evidence-backed claims.
- **IT/service owner:** provision trusted identity and independent checkpoint services, secrets management, monitoring, and supported deployment runtime.
- **Partner:** execute genuine Windows/browser portability check against owner-reviewed artifact and return hashes, environment, commands, logs, and screenshots/results.
- **Project owner:** approve case set and thresholds for Phase 7; qualified reviewers remain separate from owner’s project authorization.

## 8. First five recommended tasks

These are recommendations, not registered official tasks; see the supplementary `RP-*` IDs in the roadmap.

1. `RP-00` — Baseline and scope freeze: confirm current official task registers, exact versions, and safe boundaries.
2. `RP-01` — Stage C evidence contract: make identity, unit, food state, concentration basis, method, yield, provenance, and estimate eligibility machine-readable.
3. `RP-02` — Compatibility gate tests: synthetic positive/negative cases for every reason an estimate must be withheld; preserve current accepted records.
4. `RP-03` — Stage D real-service provisioning: owner/IT supply the identity and independent checkpoint services, then run authorized integration checks.
5. `RP-04` — Qualified review launch: verify reviewer qualification, issue assignment-ready worklists, and import only genuine signed decisions.

The critical path for a defensible predictive demonstration remains: verified source/target contract → compatible independent experimental data → source-held-out and external validation → model packaging/reproducibility approval → gated UI integration. In parallel, composition calculations depend on compatible raw/cooked evidence and measured yield; interaction review depends on authorized Stage B access and qualified review.
