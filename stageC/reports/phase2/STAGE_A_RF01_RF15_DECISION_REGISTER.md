# Stage A RF-01–RF-15 owner decision register

**Status: OPEN — 0/15 approved.** This is a decision-preparation packet, not an approval or a scientific adjudication. No primary-source answer was invented. The recommendations below are conservative interim handling rules derived from the existing owner template and Stage C contracts. Confidence applies to the interim safety/process recommendation, not to the unknown scientific answer.

## Prepared decisions

| ID | Decision required | Options to adjudicate | Interim recommendation | Confidence / limitation | Approval needed |
|---|---|---|---|---|---|
| RF-01 | Target equation and source-family derivation | Cooked/raw concentration ratio; remaining mass ratio; transformed loss; source-specific index. | Keep target semantics unresolved and predictions blocked until every source family has an auditable row derivation. | High confidence in conservative hold; equation unknown. | Owner decision plus independent scientific review required. |
| RF-02 | Output scale, unit, and inverse log1p transformation | Fraction, percent, native index; `expm1` output versus any further scale conversion. | Do not publish numeric outputs or a unit until source-scale examples reproduce the original target exactly. | High on need for scale verification; actual scale unknown. | Owner decision required; reviewer confirms transformation. |
| RF-03 | Numerator, denominator, and measurement basis | Fresh mass, dry mass, cooked sample mass, extract mass/volume, total sample or another basis. | Record source-specific numerator and denominator; if unavailable, leave `UNKNOWN` and prohibit cross-basis use. | High on requirement; target basis unknown. | Owner decision and primary-source support required. |
| RF-04 | Raw/cooked pairing and replicate definition | Paired replicate, condition mean, independent raw/cooked samples, or another design. | Do not describe target values as paired retention until replicate unit and row-level pairing are documented. | High on interpretation risk; actual pairing unknown. | Owner decision and source-row map required. |
| RF-05 | Cooked yield and total-mass adjustment | Concentration-only target; analyte mass ratio with yield adjustment; yield unavailable. | Keep concentration and total-mass retention separate; no mass-retention output without measured paired yield. | High on dimensional distinction; target construction unknown. | Owner decision required. |
| RF-06 | Moisture basis and fresh/dry-weight handling | Fresh basis, dry basis, paired moisture correction, mixed basis, or unknown. | Do not convert bases without same-sample moisture or an explicit source-specific factor. | High on conversion requirement; target basis unknown. | Owner decision plus source support required. |
| RF-07 | Solid/liquid compartments under liquid-contact cooking | Solid only, retained liquid, discarded liquid, whole system, or method-specific scope. | Keep compartments explicit; do not transfer a solid-only factor to a whole recipe or vice versa. | High on leaching relevance; target scope unknown. | Owner decision required. |
| RF-08 | Analyte identity and chemical transformations | Same analyte, total equivalents, transformation products, cross-reactive assay signal, or unresolved. | Require source analyte and assay definition before interpreting signal change as retention. | High on identity requirement; affected target rows not adjudicated. | Owner decision and analytical review required. |
| RF-09 | Recovery, calibration, detection limits, and censoring | Source-specific correction; raw measured values; censored/missing value rules. | Do not harmonize or impute without assay QC, recovery, LOD/LOQ, and censoring provenance. | High on QA need; source-family coverage incomplete. | Owner decision and analytical review required. |
| RF-10 | Values above 100 and row-specific disposition | Valid increase/apparent concentration increase; total-mass ratio; measurement error; unresolved. | Do not clip values globally; preserve each value pending source-specific explanation. | High on preserving data; causes unknown. | Owner decision and source-row evidence required. |
| RF-11 | Loss encoding, zeros, negatives, missingness, sentinels | Remaining fraction/percent; loss value; transformed value; source-specific missing/sentinel rules. | Do not reinterpret signs or sentinels without the preprocessing lineage; keep missing distinct from zero. | High on data-integrity rule; encoding unresolved. | Owner decision required. |
| RF-12 | Target aggregation and supported domain | Single matrix/method/condition; grouped means; multiple conditions or source families. | Publish a supported domain only after a `Record_ID` to source/condition map is supplied. | High on scope requirement; target aggregation unknown. | Owner decision plus source map required. |
| RF-13 | Meaning of `Initial_Unit_Standardized` | Raw concentration only; both sides of a paired target; target itself; source-specific meaning. | Treat only as a raw input label until its implementation and target relationship are verified. | High on caution; actual field semantics unknown. | Owner decision required. |
| RF-14 | Imputation, normalization, clipping, or manual changes | No alteration; source-family normalization; imputation; clipping/winsorization; documented manual correction. | Require original-to-staged row reconciliation and change log; do not infer preprocessing from model metrics. | High on reproducibility need; lineage not supplied. | Owner decision and data-lineage review required. |
| RF-15 | `Apparent_Increase` provenance and leakage | Source annotation; post hoc derived flag; selection criterion; model feature; unknown. | Exclude from inference use until provenance and leakage analysis are documented. | High on leakage precaution; field role unknown. | Owner decision plus independent reviewer required. |

## Owner and reviewer gate

Every row requires the project owner’s response, supporting artifact, precise source locator, decision date, named scientific reviewer, approval state, and rationale. The owner must decide the scientific contract; a developer cannot approve on the owner’s behalf. Independent scientific/operational review and a verified package remain separate gates. The existing tracker stays unchanged at `OPEN`, with all 15 rows `PENDING`.

## Evidence consulted and limits

- `stageC/reports/phase2/RETENTION_FINAL_OWNER_RESPONSE_TEMPLATE.md` supplies the exact questions and existing Stage C evidence boundaries.
- `stageC/reports/phase2/PHASE2_STAGE_A_DEPLOYMENT_PACKAGE_SPEC.md` supplies package and release acceptance requirements.
- `stageC/data/phase2/owner_decision_tracker.json` has 15 rows and no owner responses.
- No Stage A code/model/input was read or executed for this decision packet. No external scientific source was used to fill missing target semantics.

## Resume rule

Do not run inference, assign target units, convert concentration to total-mass retention, or create predictions until the owner decisions, source derivations, serialized model/data package, dependency lock, and independent review gates are satisfied.
