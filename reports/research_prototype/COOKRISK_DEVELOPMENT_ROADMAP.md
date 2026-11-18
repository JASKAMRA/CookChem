# CookRisk Research Prototype — Supplementary Development Roadmap

**Planning blueprint — 17 November 2026**  
This roadmap is supplementary and recommendation-only. The authoritative repository roadmap remains `COOKRISK_DEVELOPMENT_ROADMAP.md`, whose official sequence is Stage A → Stage B → Stage C → Stage D. This document does not create official Stage E–G or override registered task gates. `RP-*` IDs are planning labels only.

## Planning assumptions

- Effort is rough engineering/research person-days, excluding waiting for partners, owner review, data acquisition, and scientific review.
- File paths are likely touch points, not authorization to modify them. Obtain task authorization and inspect existing user changes before implementation.
- Do not move a blocked scientific task to “complete” because its software or synthetic test is ready.
- Current evidence is report-derived: latest Stage A log 11 Nov; cited Stage C/D closure and handoff evidence 5 Nov. Refresh status under the official task process before executing.
- Stage B was not inspected; all Stage B scope below requires its authorized custodian.

## Prioritized work packages

| ID | Stage / priority | Task and dependencies | Expected output | Acceptance criteria | Likely files / effort / risks |
|---|---|---|---|---|---|
| RP-00 | Cross-stage / P0 | Baseline official task register, approved releases, current hashes, and protected boundaries. Dependency: owner confirmation of controlling register. | Dated baseline and task-to-evidence map. | Versions and source reports cited; inaccessible inputs explicitly marked; no protected content copied. | Planning reports only; 1–2 days. Risk: old status reports may be stale. |
| RP-01 | Stage C / P0 | Define machine-readable evidence contract for identity, category, sample state, basis, units, method, conditions, yield, quantity type, source, and status. Depends on official Phase 1 and Phase 2 scope. | Contract and compatibility decision table. | Every accepted calculation has required fields; unknown values remain null/status-coded; synthetic valid/invalid cases pass. | Registered Stage C schema/code/tests only; 2–4 days. Risk: cannot make scientific basis assumptions. |
| RP-02 | Stage C / P0 | Compatibility gate regression set for food/compound/preparation combinations. Depends on RP-01 and authorized evidence only. | Tests for pass/reject/unresolved paths plus rejection reasons. | No unsupported estimate generated; existing accepted observation boundary unchanged unless official evidence and approval permit migration. | Phase 2 tests/fixtures; 2–3 days. Risk: fixture may be mistaken for scientific data; label synthetic. |
| RP-03 | Stage D / P0 | Provision identity provider and independent checkpoint service. Depends on owner/IT decisions, credentials, endpoint, trust policy. | Configured deployment and real integration evidence. | Authentication/qualification enforced; audit/checkpoint recovery and failure behavior verified against real service; no bypass. | Stage D adapter/config/test docs; 3–6 days plus IT lead time. Risk: credentials and service unavailable. |
| RP-04 | Stage D / P0 | Launch qualified review for evidence/mechanism worklists. Depends on RP-03 and reviewer qualification/assignment. | Traceable signed decisions and audit events. | Every decision tied to authorized qualified human, evidence, rationale, date, and verified signature; pending remains pending otherwise. | Stage D review workflow and controlled registers; 2–5 days plus review time. Risk: cannot automate scientific judgment. |
| RP-05 | Stage A / P1 | Reconcile exact training snapshot, target, feature pipeline, historical predictions, environment and artifact lineage. Depends on data/model owner provision. | Reproducibility package and discrepancy resolution record. | Snapshot hash and all preprocessing/config verified; repeated run and metrics reconciled or bounded; no OOF-as-inference. | Stage A reports/config/tests; 2–5 days. No model/data execution until explicitly authorized. Risk: original metadata/artifact may be missing. |
| RP-06 | Stage A / P1 | Independent experimental replication acquisition for selected domain. Depends on protocol and source-owner agreements. | Source-linked, protocol-matched independent case set. | Inclusion rules preregistered; independent lab/source; measurement bases and units compatible; blinded evaluation possible. | New authorized evidence records and analysis; 10+ days plus lab/review time. Risk: evidence may show poor generalization. |
| RP-07 | Stage A / P1 | Model evaluation refresh using grouped/source-held-out methods after RP-06. Depends on approved snapshot and RP-06. | Fold-level metrics, ablations, error and uncertainty analysis, model card. | Leakage checks pass; baselines included; performance and limits reported without target-driven selection; external acceptance threshold owner-approved. | Stage A experiment outputs only under authorization; 4–8 days. Risk: sample size and source confounding. |
| RP-08 | Stage B / P1 | Custodian-led identity/evidence contract and authorized integration export. Depends on Stage B owner/custodian access decision. | Versioned, access-controlled adapter schema and approved test fixture. | Identity, study provenance, interaction claim, contradictions and review status trace; access policy enforced; custodian signs release. | Stage B registered scope; estimate 3–6 days. No Stage B inspection by this plan; risk: protected source cannot be exported. |
| RP-09 | Stage C / P1 | Resolve Phase 2 unresolved rows through primary-source evidence review. Depends on evidence acquisition and qualified review. | Per-record compatibility decisions; accepted outputs only if all gates pass. | Source states basis, sample, conditions, method, unit and yield as needed; no inferred retention; full provenance/calculation reproducible. | Phase 2 evidence registry/reports as authorized; variable days per source. Risk: many rows remain unresolved. |
| RP-10 | Stage C / P1 | Recipe/meal integration verification against independently calculated cases. Depends on RP-01, compatible composition data, and supported cooked evidence where needed. | Deterministic meal calculation trace and tests. | Unit conversions, portions, consumed fraction, leftovers and mass/yield reconcile; unsupported inputs block total; partial values labelled. | Phase 3 engine and tests; 3–5 days. Risk: incorrect assumed yield. |
| RP-11 | Stage C / P1 | Phase 4/5 uncertainty and benchmarking acceptance. Depends on valid uncertainty inputs, owner-approved thresholds and independent benchmark cases. | Reproducible benchmark report and uncertainty validation. | No fabricated distribution/bounds; locked case set/hash; owner thresholds; independent benchmark; actual coverage/error reported. | Phase 4/5/7 registered files; 4–8 days plus review. Risk: uncertainty method may not be supportable. |
| RP-12 | Stage C/D / P2 | C1B-02 owner-reviewed archive and partner portability. Depends on owner designation, authorized creator/location, exact runtime inputs and partner availability. | Exact-byte manifest-verified archive and partner Windows/browser report. | Archive membership and hashes match approved manifest; protected inputs handled only by custodian; genuine partner commands/results returned. | Handoff docs/manifest are existing evidence; archive/partner work by authorized parties. Risk: designation/runtime inputs missing. |
| RP-13 | Integration / P2 | Read-only researcher UI and provenance export for accepted raw evidence and supported calculations. Depends on stable API contracts and RP-01/RP-10. | Demonstration path with evidence and unavailable states. | Each displayed value has source/version/unit/status; no fake cooked estimate, prediction, or risk score; degraded services visible. | Stage C app/API + integration tests; 4–7 days. Risk: existing app/data boundary requires careful gating. |
| RP-14 | Integration / P2 | Release candidate, reproducibility bundle, operator runbook and independent acceptance. Depends on all official stage gates. | Versioned research prototype candidate and validation record. | Clean supported environment setup; hashes, tests, scientific limits, review states and known issues documented; owner accepts. | New release artifacts only by explicit release task; 3–6 days. Risk: premature publishing or hidden unmet gate. |

## Recommended execution order and critical path

1. RP-00 baseline; continue official registered work in its prescribed order.
2. RP-01 → RP-02 for calculation contracts; in parallel, owners can provision RP-03, while no review decision is imported before it is live.
3. RP-04 requires actual qualified reviewers after provider readiness.
4. RP-05 requires the Stage A owner’s exact snapshot/artifact evidence; RP-06 must precede any external generalization claim; RP-07 follows a locked dataset and approved analysis plan.
5. RP-08 is custodian-controlled and must not be bypassed; connect only after a signed, permitted interface exists.
6. RP-09 → RP-10 and RP-11 for scientifically supported composition and meal outputs.
7. RP-12 is an external handoff gate; it does not justify weakening the registered acceptance criteria.
8. RP-13 follows accepted contracts and safe adapters. RP-14 comes only after all formal stage gates and owner acceptance.

Stage A prediction release and Stage C cooked concentration have distinct critical paths. Neither can be substituted for the other. Stage D reviewer readiness is not reviewer approval. The official Stage C phase order and Stage D nine-phase sequence remain controlling.

## Decisions before implementation

- Which official task register/release is current for each proposed work package?
- Who owns Stage A training snapshot/model artifact and can authorize controlled reproducibility work?
- Which custodian can authorize Stage B interface details and test payload?
- Which scientific owner defines accepted target quantity and independent benchmark thresholds?
- Which qualified reviewers and IT operator can provision genuine review/authentication/checkpoint services?
- Who may designate the current C1B-02 archive/revision and authorize the partner handoff?
- What deployment boundary is approved: local demonstration only or a controlled institutional environment?
