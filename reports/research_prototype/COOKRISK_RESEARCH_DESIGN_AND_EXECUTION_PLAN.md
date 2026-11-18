# CookRisk Research Design and Execution Plan

**Version:** 1.0 (planning document)  
**Date:** 17 November 2026  
**Status:** Proposed research and engineering blueprint; not an official stage register, scientific protocol approval, or authorization to modify protected project assets.

## 1. Executive summary

CookRisk is intended to be a research prototype for studying how food identity, bioactive-compound identity, cooking preparation, measured food composition, and food–drug evidence can be connected without losing source provenance or confusing different scientific quantities. It should let a researcher inspect what is known, see whether evidence is compatible for a calculation, and reproduce any supported calculation. It should communicate unavailable evidence just as clearly as available results.

The project has substantial documented implementation across Stages A, C, and D, but the evidence cited in current planning reports does not support a generalizable Stage A prediction service, an accepted Stage C cooked-concentration estimate from the reported Phase 2 boundary, or completed Stage D qualified review. Stage B was not accessed for this plan and remains unverified here. The prototype should therefore be built in gated increments: first an evidence-traceable research interface and safe calculation contracts, then integrations and prediction only when their independent scientific and operational acceptance gates pass.

This plan coordinates two work tracks:

- **Scientific research track:** validates observations, identities, target meanings, evidence compatibility, independent performance, and qualified review.
- **Prototype engineering track:** implements versioned data contracts, APIs, UI states, calculation traces, and reproducible integration behavior.

Engineering can proceed on synthetic, clearly labelled fixtures while scientific tasks are blocked, provided it neither changes official acceptance criteria nor makes synthetic fixtures appear to be scientific evidence.

## 2. Formal research design

### 2.1 Research problem

Experimental reports on bioactive-compound concentrations after cooking are heterogeneous in food matrix, compound identity, protocol, analytical method, sample state, denominator, and source. Concentration changes can be misread as total analyte retention, and measurements from different bases can be combined incorrectly. At the same time, a food–drug interaction report does not by itself establish ordinary dietary exposure or clinical risk. CookRisk investigates whether these evidence types can be represented and connected reproducibly, and whether a model can predict a precisely defined cooking-related concentration outcome across unseen source families.

### 2.2 Motivation

Researchers need a way to compare cooking observations while retaining the conditions and limitations that determine whether two measurements are comparable. A transparent tool can make missing basis, yield, identity, or protocol information visible and support reproducible calculations. A predictive model would be useful only if it generalizes beyond its source studies; current cited results show that this is not yet established.

### 2.3 Research objectives

1. Build a provenance-preserving representation of food, compound, analytical measurement, cooking protocol, and evidence source.
2. Define and enforce distinct endpoints for apparent concentration ratio, total-mass retention, cooked concentration, and related quantities.
3. Measure how well prespecified models predict a declared concentration endpoint under compound-grouped and source-held-out validation.
4. Investigate the effects of source, protocol, food-matrix, compound, feature family, and data quality on model error and generalization.
5. Determine which food–compound–preparation records meet explicit evidence-compatibility criteria for a cooked-concentration or recipe calculation.
6. Integrate food–drug evidence only through an authorized and reviewed Stage B interface, preserving study context and conflicts.
7. Provide a research UI that exposes provenance, uncertainty, review status, and unavailable states without turning research evidence into clinical advice.

### 2.4 Research questions

- **RQ1:** How much variation in the declared cooking outcome is associated with compound identity, food matrix, cooking protocol, analytical method, and source family?
- **RQ2:** Do molecular descriptors or fingerprints improve predictive performance over simple and non-molecular baselines under grouped validation, and does that improvement persist under source-held-out validation?
- **RQ3:** How large is the performance gap between molecular-grouped and source-held-out validation, and which source/protocol characteristics explain it?
- **RQ4:** Which apparent raw/cooked pairs are truly compatible for estimating a concentration ratio, cooked concentration, or total-mass retention, and what evidence fields most often prevent calculation?
- **RQ5:** Can the prototype trace every displayed evidence value and calculation to a versioned source record and return an explicit reason when an output is unavailable?
- **RQ6:** What does authorized food–drug evidence support about documented interactions, and which conclusions remain outside the evidence because exposure, bioavailability, or clinical outcomes are not established?

### 2.5 Testable hypotheses

These are proposed hypotheses for a future, pre-registered confirmatory analysis. They must be refined and approved before examining the confirmatory test set. If sample size or independence assumptions are inadequate, report the test as infeasible rather than changing the hypothesis after seeing results.

- **H1 (source generalization):** a prespecified model’s source-held-out error is lower than a prespecified baseline by a pre-approved practically meaningful margin. The current reported negative source-held-out R² makes this uncertain; it is a question, not an expected outcome.
- **H2 (feature contribution):** adding a prespecified molecular feature group improves error over the same pipeline without that group under grouped validation, with direction and practical margin defined before evaluation.
- **H3 (source shift):** source-held-out performance differs from compound-grouped performance by a predeclared margin, indicating measurable source dependence. The comparison must use compatible outcomes and report uncertainty; it cannot be interpreted as causal attribution to “source.”
- **H4 (compatibility completeness):** explicit identity, basis, unit, protocol, and yield gates reduce the number of computable pairs relative to a permissive unfiltered count while eliminating unsupported calculations in adjudicated test cases. This is a software/data-quality hypothesis, not evidence that the rejected values are scientifically false.

No hypothesis asserts that performance will improve, that a specific feature is predictive, or that any interaction is clinically consequential.

### 2.6 Scope and intended use

**In scope:** research observations of cooking-related bioactive-compound concentration outcomes; food and compound identity resolution; source-specific composition evidence; compatible cooking calculations; evidence review; recipe arithmetic when inputs are supported; model evaluation under grouped and source-held-out designs; reproducibility and provenance.

**Intended users:** project researchers, qualified evidence reviewers, and authorized technical maintainers in a controlled research environment.

**Out of scope:** clinical risk scores, individualized medical advice, dietary recommendations, safe/unsafe thresholds, drug dose adjustment, inference of bioavailability from food-composition data, consumer-facing health claims, and claims that a reported interaction is reached at ordinary food intake.

### 2.7 Expected contributions

1. A structured, traceable representation of cooking observations and the scientific basis of each quantity.
2. An empirical assessment of source-shift/generalization limits in the available data, including transparent negative findings.
3. A compatibility workflow that distinguishes calculable, rejected, and unresolved food–compound–preparation pairs.
4. A reproducible research prototype demonstrating how evidence, calculations, model status, and review status can be integrated safely.
5. A documented account of which scientific claims remain unsupported and what evidence would change that status.

### 2.8 Scientific limitations and non-claims

- Historical recovery reports are not equivalent to an independently validated dataset. The cited 1,016 observations/32 DOI families and model metrics must be tied to their exact snapshot and evaluation protocol before reuse.
- Source-family performance may be confounded with food, compound, analytical method, or protocol; observational associations do not establish causal effects of a cooking method.
- Small or uneven groups limit fold stability, subgroup analysis, uncertainty estimation, and conclusions about rare compounds or methods.
- A concentration ratio is not total-mass retention; a cooked concentration is not bioavailability; estimated human intake is not clinical risk.
- Missing primary-source details may make records unusable for a specific calculation even when they remain useful contextually.
- Stage B was not accessed for this plan. No claim about its current source contents, counts, or scientific conclusions is made.
- Stage C reports cited here state 117 observations and zero accepted cooked-concentration estimates. That boundary is not altered by this plan.
- Stage D reports cited here state 342 records pending and zero decisions. Human review is not inferred from readiness work.
- A technically successful application, test suite, or schema check is not a scientific validation result.

## 3. Research methodology

### 3.1 Literature and evidence acquisition

1. Define the research question, endpoint, population/matrix scope, and inclusion/exclusion criteria before source screening.
2. Search approved bibliographic and primary-source channels using a recorded strategy, date, and query. Maintain a screening log with included, excluded, duplicate, inaccessible, and awaiting-review states.
3. Prefer primary experimental articles, theses, or source datasets for measured values. Record full citation, DOI/PMID when present, page/table/figure/row locator, access date, source copy/version, and any reuse/license conditions.
4. Extract verbatim source labels and units separately from normalized fields. Record analytical method, sample preparation, food portion/state, cooking conditions, replicate/statistical summaries, and denominators. Double-check material extractions against the source; unresolved disagreements go to qualified review.
5. Keep evidence that is qualitative, incompatible, or insufficient in the evidence register with an explicit disposition. Do not infer numeric retention from percentage loss or reconcile contradictions by averaging without a justified protocol.
6. For Stage B evidence, use only an authorized custodian-controlled workflow. The current planning task did not access it.

### 3.2 Dataset provenance and curation

- Freeze an immutable versioned input snapshot for each analysis; record source record IDs, original locations, exact-byte SHA-256, acquisition and transformation log, license/provenance, and inclusion/exclusion reason.
- Retain raw source fields and create normalized columns alongside them. Never silently replace historical values.
- Check row/compound/source counts, duplicate records, missingness, repeated measurements, inconsistent units, source family, and cross-reference validity. Treat DOI family as a grouping key only after the source identity is verified.
- Document every transformation, including unit conversion, identity standardization, aggregation, or exclusion. Keep a record-level lineage from model row or application output back to original source locator.
- Partition related observations from the same study/source family together in source-held-out evaluation. Avoid leakage through replicated rows or derived features.

### 3.3 Molecular identity standardisation

1. Preserve source compound name, source identifier, and source structure as received.
2. Validate structure parsing and valence with a versioned cheminformatics toolchain; store canonicalization settings and software version.
3. Generate normalized structure identifiers (e.g. canonical isomeric SMILES/InChI where supported) and descriptors only as derived fields; do not overwrite source identifiers.
4. Review salts, mixtures, tautomers, stereochemistry, glycoside/aglycone, and uncertain structures with authoritative evidence. Keep unresolved identity pending.
5. Record food identity separately, including common/scientific name, species/cultivar where known, plant part, matrix, processing, and ordinary-food versus ingredient/beverage category.

### 3.4 Food and cooking-method classification

- Define versioned controlled vocabularies for food group/matrix, edible part, state (raw, fresh, dried, frozen, cooked), and preparation method.
- Preserve the source’s exact method term and map to a normalized label only with documented rules. Record time, temperature, equipment, medium, draining, peel/part, and sample handling where available.
- Represent absent protocol fields as missing/unknown, not as a default cooking condition. Record method equivalence as an adjudicated mapping, not a string-similarity assumption.

### 3.5 Target definition and compatibility

Each training/evaluation row must have exactly one primary target type and its calculation provenance:

- **ACR (%)** = `100 × C_cooked / C_raw` when both concentrations measure the same analyte on compatible bases and matched food/protocol conditions.
- **Total-mass retention (%)** = `100 × (C_cooked × M_cooked)/(C_raw × M_raw)` when concentration units and measured food masses (or validated yields) are compatible.
- **Cooked concentration** remains an absolute concentration with its unit and denominator; it may be directly measured or calculated only under a separately documented compatible method.
- **Yield** is a food-mass change quantity, not analyte retention.

Do not mix target types in one regression target. Log the original reported value, converted value, formula, basis, unit, and evidence reviewer. If required fields are unknown, classify the pair as unresolved or incompatible instead of imputing a scientific conversion.

### 3.6 Feature engineering and model development

1. Establish a constant/mean baseline and simple interpretable baseline before complex estimators.
2. Predefine feature families: molecular descriptors, fingerprints (only where sample size and identity quality justify them), food matrix, cooking protocol, analytical method, and source metadata. Source identifiers can diagnose shift but must not become a shortcut feature in a claim of biological generalization.
3. Fit imputation, scaling, selection, and other learned transformations within training folds only. Keep the pipeline and feature order/version serialized with the model package if a package is later justified.
4. Compare a small prespecified set of regression models, with tuning nested inside training data. Record seeds, package versions, hardware/runtime, estimator configuration, and failed runs.
5. Run feature ablation with identical outer folds and compare fold-level distributions; do not choose features from the held-out source results.
6. Preserve negative, unstable, or non-significant results. Do not optimize outliers away; run source-evidence review and a predeclared sensitivity analysis.

### 3.7 Validation strategy

Report validation designs separately:

- **Molecular-grouped validation:** all records for a canonical molecular identity remain in one fold. This evaluates transfer to unseen compounds under the sampled study/source mix.
- **Source-family-held-out validation:** all records from one DOI/study family remain out together (e.g. leave-one-source-family-out where feasible). This evaluates transport across study families, though source and protocol shifts may be entangled.
- **Nested tuning:** hyperparameter selection occurs inside training folds; outer folds estimate performance.
- **Independent external validation:** a later, locked set from an independent source/laboratory and comparable protocol, not used for feature/model selection. Predictions are frozen before outcome reveal where feasible.

For every fold report groups and records, MAE, RMSE, R² (including negative values), baseline metrics, target range, and prediction coverage. Report mean/median and fold distribution, not only pooled metrics. If folds contain too few independent sources or groups, state the analysis is descriptive/exploratory.

### 3.8 Error analysis and uncertainty

- Plot predicted versus observed with identity line and label fold/source; include residual versus fitted and residual distributions.
- Stratify errors by source family, compound, food matrix, cooking method, analytical method, and target range only when cell sizes are reported and interpretable.
- Review largest residuals against primary source records for extraction/identity/basis errors; do not delete cases solely because they are difficult.
- Quantify fold stability and sensitivity to prespecified outlier/exclusion decisions.
- Compare prediction intervals or other uncertainty estimates only when the method is selected and validated under the grouped design. Report calibration/coverage and sample counts. Otherwise state uncertainty is not established.
- For Stage C recipe calculations, propagate only measured/defensible input uncertainty. If no validated distribution or bounds exist, return unavailable uncertainty rather than a fabricated interval.

### 3.9 Independent validation and confirmatory analysis

Exploratory analyses may identify plausible features, target definitions, or domain subgroups. Confirmatory evaluation must use a protocol and model specification frozen before independent outcomes are examined. The validation source must be genuinely independent at the study-family level, use compatible measurement definitions, and have its own data-quality review. Compare against a prespecified baseline and owner-approved practical thresholds. A null, negative, or inconclusive result is a valid research finding.

### 3.10 Evidence integration and reproducibility

- Keep Stage B interaction evidence, Stage C composition/cooking evidence, Stage A predictions, and Stage D human decisions as distinct objects connected by stable identifiers and versioned APIs.
- Store source citation/locator, entity IDs, units/basis, method, transformations, compatibility decision, reviewer status, and hashes for every accepted calculation.
- Use typed unavailable/error statuses for missing identity, basis, source, authorization, incompatible units, absent yield, unverified model, failed integrity, and offline service.
- Re-run only with declared, approved snapshots and pinned environments. Record exact command, interpreter/dependency versions, configuration, input/output hashes, and test counts. Preserve historical outputs; emit new versioned outputs for new analyses.
- Distinguish software reproducibility from independent scientific replication.

### 3.11 Exploratory versus confirmatory work

| Exploratory | Confirmatory |
|---|---|
| Data profiling, candidate feature inspection, hypothesis formation, model family comparison on development data, compatibility-gap discovery | Frozen endpoint and inclusion rules, frozen feature/model/pipeline, preregistered split and metrics, locked independent case set, no tuning on held-out results |
| May evolve with documented versioning; results generate hypotheses | Changes after outcome access invalidate the confirmatory claim and require a new untouched test set |
| Used to decide whether evidence supports a study | Used to estimate performance or test a declared hypothesis |

## 4. Coordinated execution roadmap

The official Stage A→B→C→D sequence and each registered task’s dependencies remain authoritative. The two tracks below coordinate work but do not reorder or waive official gates. A blocked scientific claim may coexist with safe engineering work using synthetic fixtures and non-protected contracts.

### 4.1 Two tracks and their dependency joins

| Research milestone | Scientific research track | Prototype engineering track | Join / blocking rule |
|---|---|---|---|
| M0 — Baseline | Confirm exact official register/release, analysis target, report dates, and owner roles. Stage B remains custodian-only. | Map current APIs, schemas, tests, app startup/degraded states from authorized files. | Both tracks need a versioned baseline. Do not assume old reports are current. |
| M1 — Evidence contract | Define source, identity, sample state, basis, units, cooking method, target type, and evidence inclusion rules. | Define versioned schemas, null/status vocabulary, provenance object, validation errors. | Can build synthetic fixtures in parallel. Real dataset migration waits for task authorization and owner approval. |
| M2 — Measurement/model readiness | Reconcile Stage A target and snapshot lineage; audit Stage C compatibility; request primary-source evidence. | Implement validation, reason-coded compatibility service, deterministic formula traces, and contract tests. | Engineering may proceed with synthetic fixtures. Scientific outputs remain blocked until real records pass compatibility/review. |
| M3 — Evaluation and real review | Execute grouped/source-held-out exploratory analysis when exact snapshot authorized; arrange independent data. Stage D reviewers adjudicate evidence. | Implement experiment runner, immutable result bundle, review worklists/import gates and audit interfaces. | Never label a synthetic test or unreviewed record as scientific acceptance. Independent outcomes remain untouched until model/analysis frozen. |
| M4 — External services and integration | Stage B custodian approves interface and evidence access; Stage D reviewers and benchmark owners approve case set/thresholds. | Provision auth/checkpoint adapters; integrate accepted Stage B/C interfaces; exercise failures. | Live review writes require real identity/checkpoint services; Stage B data calls require custodian authorization. |
| M5 — Demonstration candidate | Independent validation and qualified evidence review determine which claims are eligible to display. | UI shows evidence, calculations, prediction status, uncertainty, and unavailable reasons; reproducibility export. | Prediction/cooked outputs shown as accepted only after their scientific gates; otherwise display explicit unavailable/experimental state. |
| M6 — Acceptance | Independent scientific review and Stage A–D task criteria met. | Clean environment reproduction, full permitted integration tests, security/deployment and partner portability evidence. | Owner records engineering, scientific, and external acceptance separately; no stage marked complete by this plan. |

### 4.2 Recommended milestone acceptance matrix

The table below defines measurable project-level evidence for the supplementary milestones. It does not replace official task acceptance criteria.

| Milestone | Implemented | Technically tested | Scientifically evaluated | Independently validated | Owner approved |
|---|---|---|---|---|---|
| M0 baseline | Source/task map created | Links/paths and scope checked | N/A | N/A | Owner confirms controlling versions |
| M1 contracts | Versioned schemas and field dictionary exist | Positive/negative fixtures, refs, units/null/status tests pass | Qualified reviewers confirm scientific field semantics | Independent schema/interface review | Owner approves contract/version |
| M2 compatibility + model readiness | Compatibility gates and reproducible analysis pipeline exist | Synthetic edge cases, leakage/fold/hash checks pass | Per-record source compatibility and endpoint meaning reviewed | Independent source/measurement or model review | Owner accepts analysis protocol and task scope |
| M3 research and review | Frozen analysis and real review workflow exist | Rerun, audit/signature integrity, and calculation tests pass | Results/reviews reported with uncertainty and limits | Independent matched source/qualified reviewers complete their scope | Owner approves reporting thresholds/review process |
| M4 service integration | Real authorized adapters configured | Auth, outage, retry, recovery, integrity and access tests pass | N/A for software alone | Service owner/partner verifies runtime | IT/owner accepts provisioning and operations |
| M5 demonstration | UI and provenance export integrate eligible components | End-to-end and unavailable-state tests pass | Displayed claims traced to accepted evidence | User/reviewer verifies outputs against sources | Owner approves intended-use text and demo boundary |
| M6 candidate acceptance | Versioned candidate and runbook exist | Approved environment tests/reproduction pass | Scientific criteria met or explicitly not accepted | Independent review/partner evidence returned | Formal stage/release owner signs acceptance |

Status dimensions must be reported separately: **Implemented**, **Technically tested**, **Scientifically evaluated**, **Independently validated**, **Owner approved**. One status never implies another. Use `BLOCKED` or `NOT APPLICABLE` with evidence and owner when appropriate.

## 5. Final research outputs

These are planned outputs only. Do not populate values until the underlying approved analysis actually runs. Each figure/table must state snapshot version/hash, target definition, unit, grouping, sample/group count, and whether exploratory or confirmatory.

### 5.1 Dataset and evidence tables

1. **Dataset flow table:** records identified, screened, excluded, included; reasons; unique compounds, food matrices, methods, DOI families; missingness by field.
2. **Measurement/target table:** endpoint type (ACR, mass retention, cooked concentration, yield), original and normalized units, sample state/basis, method, denominator, source availability, compatibility status.
3. **Source coverage table:** records and unique compounds/matrices by source family; concentration of observations in largest studies; replication/independence counts.
4. **Compatibility table:** eligible, rejected, unresolved combinations by gate/reason; ordinary-food and ingredient/beverage categories separated.
5. **Evidence review table:** reviewed/pending/needs-revision/rejected counts by record class and source, only after genuine reviewer decisions exist.

### 5.2 Model figures and tables

- Target distribution, stratified by source family and target range; report transformations and outliers without hiding them.
- Model comparison table: prespecified models and baseline, molecular-grouped metrics, source-held-out metrics, fold/group counts, uncertainty, and tuning scope.
- Feature ablation table/plot using identical outer folds for molecular descriptors, fingerprints, cooking, food-matrix, and combined feature sets where scientifically justified.
- Fold stability plots for MAE/RMSE/R², with negative R² visible.
- Predicted-versus-observed plots for each evaluation design with source/fold labels and identity line.
- Residual distribution and residual-versus-fitted plots; stratified error plots only with adequate cell counts.
- Feature importance/interpretability summaries with method, fold variation, and known limitations; do not interpret association as causation.
- External validation table only after an independent locked set is genuinely available and predictions are frozen.

### 5.3 Prototype and reproducibility reports

- Interface/data-contract coverage report; schema and API test results.
- Calculation trace examples showing formula, inputs, units, conversions, provenance, and gate outcomes.
- End-to-end scenario matrix including available, unavailable, unauthorized, incompatible, and degraded states.
- Reproducibility manifest: code/config/environment version, data/model hash, commands, outputs, and test results.
- Model card and intended-use statement if an experimental model is eventually packaged.
- Scientific limitations and decision log, including unanswered questions and blocked acceptance.

No figure/table should be filled with synthetic values as if observed. Synthetic fixtures may appear only in clearly labelled software-test examples, separated from research findings.

## 6. Demonstration scenario and expected user-visible states

### Scenario

A researcher opens the local research prototype, selects an ordinary food and a compound from identity-qualified catalog entries, chooses a cooking method, and inspects a raw composition record. The researcher asks whether an experimental concentration prediction, accepted cooked concentration, and relevant interaction evidence are available, then exports the record’s provenance and calculation trace.

This scenario does not depend on a particular food–compound value being accepted. The demonstration should select a real record only after confirming it exists in an authorized, current Stage C release. If no record meets the chosen conditions, the UI should demonstrate the blocked path rather than substitute another value silently.

### Screen flow and current documented expectation

1. **Food/compound selection:** show stable identifiers, common/source names, identity status, food category, and ambiguity. Unresolved identities cannot proceed as if confirmed.
2. **Cooking-method selection:** show source-supported normalized method and conditions; mark absent temperature/time/equipment/medium as unknown. Do not fill defaults invisibly.
3. **Raw composition evidence:** show measured value, original unit and denominator, as-received/as-analyzed/dry-weight/other basis, sample state, source locator, and acceptance status. If source or basis is missing, label it.
4. **Experimental prediction panel:** current documented Stage A readiness is not deployment-validated. Show `EXPERIMENTAL / NOT AVAILABLE FOR DECISION USE` or disable inference until the model artifact, snapshot, preprocessing, domain, and external validation gates pass. Never show OOF predictions as new-record predictions.
5. **Cooked concentration:** current cited Stage C Phase 2 boundary reports 117 observations and 0 accepted cooked-concentration estimates. Show `NO ACCEPTED COMPATIBLE COOKED ESTIMATE` and the exact missing compatibility fields; do not show a numeric placeholder.
6. **Food–drug interaction evidence:** use only an authorized Stage B adapter. Since Stage B was not accessed for this plan, current content is not verified. If the source is unavailable or authorization missing, display `INTERACTION EVIDENCE UNAVAILABLE — SOURCE NOT VERIFIED/PROVISIONED`, not “no interaction.”
7. **Recipe/exposure calculation:** allow only arithmetic whose input concentrations, food quantities, cooked yield and consumed fraction are supported. Distinguish a partial ingredient result from a complete meal total. Do not compute bioavailability or clinical risk.
8. **Provenance/uncertainty:** show source IDs and locators, release, formulas, assumptions, validation/review status, and uncertainty method. If uncertainty is not supported, say so plainly.
9. **Export:** generate a research trace with input IDs, versioned sources, calculation steps, status and limitations; omit restricted fields the user is not authorized to export.

### Demonstration acceptance

- At least one authorized raw-reference record can be traced to its source and identity/basis fields.
- A compatible synthetic fixture proves software arithmetic, but is labelled synthetic and never presented as scientific evidence.
- An unsupported real cooking scenario returns a reason-coded unavailable response and no cooked numeric result.
- Missing Stage A, Stage B, authentication, checkpoint, or Phase 4 inputs appear as distinct degraded states.
- Every displayed number has unit, quantity type, source/provenance and status.
- No clinical risk score, safety threshold, or individualized recommendation is produced.

## 7. Milestone acceptance evidence and governance

For each milestone, retain a dated record with task/register reference, scope, files touched, exact command/environment, input/output hashes, tests with passed/failed/skipped counts, reviewer/owner decisions, and unresolved items. Preserve earlier evidence; new runs create versioned records.

| Acceptance dimension | Minimum evidence |
|---|---|
| Implemented | Code/config or approved data contract exists at a versioned revision; scope and interfaces documented. |
| Technically tested | Exact tests ran in declared environment; results include skips/failures; failure paths and negative cases covered. |
| Scientifically evaluated | Defined scientific endpoint and source evidence assessed; analysis protocol and result interpretation documented. |
| Independently validated | Independent source, qualified reviewer, partner, or service owner completed the relevant review and returned traceable evidence. The type of independence must be named. |
| Owner approved | Authorized owner records the specific decision and scope. Owner approval does not replace scientific review. |

Never call a task “complete” without identifying which dimensions passed and which remain pending. Do not alter official stage acceptance criteria through this supplementary blueprint.

## 8. First implementation milestone recommendation

**Start with M1: the versioned evidence and quantity contract, paired with a small synthetic compatibility test suite under the next officially authorized Stage C task.** Do not create a parallel official task or bypass a predecessor gate.

This is the best first implementation milestone because it addresses the central risk shared by every later component: treating unlike measurements as comparable. It is locally actionable without fabricating scientific results, supports fail-closed behavior immediately, provides a stable boundary for the API and UI, and lets engineering progress with explicitly synthetic fixtures while primary-source review, Stage B custodian work, independent experiments, and external services remain blocked. It also improves future data acquisition by making missing identity, basis, method, unit, and yield requirements concrete at the point of entry.

Before implementation begins, the project owner/task owner should confirm the controlling official task ID and authorize its exact file scope. The Stage C owner/scientific lead should approve the scientific semantics of the contract; a qualified reviewer should resolve contested measurement interpretations. Once M1 is accepted, the next task should follow official dependency order rather than jumping to model integration or a polished demo.

## 9. Relationship to existing planning documents

This document consolidates formal research design and milestone acceptance details. The companion documents retain their focused roles:

- `COOKRISK_RESEARCH_PROTOTYPE_WORKFLOW.md` — stage-wise workflow and scientific quantity distinctions.
- `COOKRISK_SYSTEM_ARCHITECTURE.md` — logical components, data contracts, unavailable states, and integration boundaries.
- `COOKRISK_DEVELOPMENT_ROADMAP.md` — supplementary `RP-*` work packages, priorities, dependencies, effort, and risks; official roadmap remains controlling.
- `COOKRISK_EXECUTION_TRACKER.md` — report-derived status snapshot and evidence discipline.
- `COOKRISK_RESEARCH_GAPS.md` — scientific, provenance, model, workflow, and governance gaps.

These companion files were reviewed together for this plan and were not changed. The current-state statements here are report-derived, dated, and explicitly not a fresh audit of source datasets or protected Stage B content.
