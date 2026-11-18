# CookRisk Research Prototype — Research and Engineering Gaps

**Planning blueprint — 17 November 2026**  
Priorities reflect scientific impact and dependency order, not an official change to stage acceptance criteria.

## Critical scientific gaps

| Priority | Gap | Evidence in reviewed reports | Why it matters | Evidence/action needed |
|---|---|---|---|---|
| Critical | Stage A generalization | 11 Nov recovery log reports 0 strict protocol-identical cross-source replications and negative source-held-out R² across evaluated models. | A model can fit study-specific patterns and fail on a new laboratory or protocol. A high random-split score would not fix this. | Obtain independent protocol-matched observations; lock target and evaluation plan; report source-held-out and external results against baseline. |
| Critical | Training snapshot/model artifact lineage | Prior Stage A reports document historical/current discrepancies and no deployable serialized package. Exact approved snapshot and end-to-end artifact lineage were not reverified here. | Prediction cannot be reproduced or safely used for new records. | Owner supplies exact training bytes/hash, code/config, target construction, fold IDs, dependencies, preprocessing, estimator, artifact hash, and historical run metadata. |
| Critical | Phase 2 cooked-concentration evidence | Cited Phase 2 report records 117 observations and 0 accepted cooked-concentration outputs; unresolved basis/compatibility issues remain. | A cooked value cannot be calculated from incompatible bases or qualitative loss statements. | For each tuple obtain primary records stating identity, sample state, basis, units, method, conditions, measured cooked/raw values and mass/yield as required; qualified reviewer decides compatibility. |
| Critical | Stage B source truth and interface | Protected source not inspected; previously reported status is not freshly verified. | Integration status, completeness, and interaction claims cannot be confirmed from this review. | Stage B custodian audits and signs a versioned interface/export, access policy, identity crosswalk, evidence quality, conflicts, and approved test payload. |
| High | Human scientific review | Latest cited Stage D handoff says 342 pending, 0 decisions. | Machine extraction/readiness does not establish scientific approval. | Verify reviewer credentials/qualification; assign stable records; record signed rationale, evidence, date, and conflicts through approved workflow. |
| High | Independent uncertainty validation | Stage C reports describe deterministic/source-typed uncertainty; probability distributions or validated intervals are not established in the cited sources. | A precise-looking interval may misstate evidence. | Obtain empirically supported uncertainty inputs and validate coverage/calibration on locked independent cases; otherwise report uncertainty unavailable or bounded only by source evidence. |
| High | Stage D scientific benchmark | Case set and thresholds require owner approval; no benchmark result is claimed. | A benchmark without locked cases and prespecified acceptance can be tuned after seeing results. | Owner approves case-set hash, metric definitions, thresholds and exclusions before an independent run; preserve outputs and reviewer sign-off. |
| Medium | Ordinary-food vs ingredient/beverage transfer | Phase 2 evidence acquisition report notes context/basis issues, including source-specific spice records not transferable to ordinary-food records. | Category or matrix transfer could create invalid estimates. | Keep categories separate; require direct source evidence and explicit compatibility approval for each transfer. |

## Data and provenance gaps

- **Basis and sample state:** as-received, as-analyzed, dry-weight, lyophilized, cooked, and unknown cannot be collapsed. Moisture factors must come from the same relevant source or a validated documented conversion.
- **Cooking protocol:** method labels alone are insufficient. Need time, temperature, equipment, geometry, water/oil medium, draining, edible portion, and protocol/source detail as applicable.
- **Yield and mass:** concentration change and total analyte mass change differ. Need raw and cooked mass or measured yield to compute total-mass retention.
- **Unit semantics:** original units and denominator must be retained; convert only with a defined, testable conversion and explicit provenance.
- **Identity crosswalks:** food matrix, cultivar/part, analyte, salt/isomer/form, and drug formulation may materially change the interpretation. Ambiguity remains explicit.
- **Source completeness:** duplicate records, missing DOI/PMID, source family, study methods, and direct source locators need record-level reconciliation. Missing references should not be guessed.
- **Access boundary:** Stage B data needs custodian-owned provenance/access policy and a controlled interface. This planning pass cannot establish its content or counts.

## Model and evaluation gaps

1. Define one target at a time (ACR, mass retention, cooked concentration, or another endpoint) and exclude semantically incompatible observations.
2. Resolve historical/current benchmark discrepancy from exact original inputs and run metadata before selecting a “best” result.
3. Establish source and compound group separation with fixed reproducible folds; report both, not only one convenient split.
4. Run leakage-safe feature engineering and ablations; learned imputers/scalers/feature selection belong inside training folds.
5. Quantify errors by source family, food matrix, cooking method, compound, and domain coverage; investigate outliers using source evidence rather than metric optimization.
6. Compare to constant/simple baselines; report negative metrics and uncertainty honestly.
7. Require external protocol-matched validation and a declared intended-use domain before any inference adapter is enabled.
8. Package the estimator, preprocessing, schema, environment, training hash, and validation report atomically; refuse OOF predictions for new-record inference.

## Software, workflow, and operational gaps

- **Formal schema validation:** cited Stage D evidence has one skipped formal `jsonschema` check in a documented environment. JSON parsing or synthetic business-rule tests are not a substitute for Draft 2020-12 validation.
- **Identity provider:** review writes must remain disabled until a trusted provider and qualification mapping are provisioned and tested.
- **Independent checkpoint:** operational review history needs a separately provisioned service, integrity verification, retry/recovery behavior, and monitored failure mode.
- **C1B-02 portability:** exact-byte policy is approved, but current owner-reviewed archive/revision, authorized creator/location/runtime inputs, and partner Windows/browser results remain missing per cited handoff records.
- **Phase 4 integrity:** v0.1.2 is documented unrecoverable in investigated sources and must remain unchanged; application should expose degraded/unavailable state without implying restored uncertainty bounds.
- **Application availability:** UI health, scientific source availability, identity service, checkpoint service, and model readiness are separate statuses. A homepage loading does not mean scientific outputs are available.
- **Release reproducibility:** final clean-copy setup, dependency provenance, manifest/archive hash, permitted input scope, end-to-end output trace, and partner/institutional acceptance remain to be demonstrated where required.

## Governance and interpretation risks

- Project-owner authorization cannot replace a qualified scientific decision.
- No benchmark thresholds should be chosen after observing benchmark outcomes.
- Raw references, experimental predictions, cooked measurements, recipe arithmetic, interaction evidence, human exposure, and clinical decisions require separate UI labels and records.
- “No evidence found” is not equivalent to evidence of no interaction, particularly when a source is inaccessible or unreviewed.
- A source-derived food–drug interaction report does not show ordinary consumption reaches the experimental exposure or imply an individual clinical outcome.
- No arbitrary clinical risk score, safe/unsafe threshold, dose recommendation, or inferred bioavailability should be exposed.

## Minimum evidence before a public-facing research demonstration

1. Owner-approved and reproducible software/data snapshot with a scoped deployment environment.
2. Accepted identity and measurement-basis contracts for every displayed datum.
3. End-to-end trace for each result, including formula, units, source, version, and limitations.
4. Unsupported scenarios demonstrably fail closed with reason-coded messages.
5. Prediction feature unavailable until Stage A artifact and external scientific gate pass.
6. Interaction evidence only via authorized Stage B adapter with human review status visible.
7. Stage D workflow requires real identity, reviewer qualification, and checkpoint infrastructure before accepting decisions.
8. Security/privacy review of authorization, exports, logs, and deployment exposure.
9. Clear notice: research prototype; not clinical advice or an individual risk assessment.

## Explicit non-claims in this blueprint

- No claim that Stage B data or counts were verified.
- No claim that Stage A has a scientifically generalizable or deployable model.
- No claim that Stage C produces an accepted cooked concentration from its 117 Phase 2 observations.
- No claim that the 342 Stage D records have been source-verified or reviewed; latest cited status is pending.
- No claim that any live identity/checkpoint service, Windows partner run, benchmark, or release was completed in this planning task.
