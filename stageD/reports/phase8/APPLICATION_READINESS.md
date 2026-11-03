# Stage D Phase 8 — application readiness

**Status: LOCAL RESEARCH PROTOTYPE — NOT A PRODUCTION APPLICATION**  
The Cycle 5 prototype is implemented in [`stageC/app`](../../../stageC/app/) and its setup/workflows are documented in [`stageC/app/README.md`](../../../stageC/app/README.md). It implements the Stage C food/compound recipe and meal workflow plus the Stage D evidence queue, source detail, mechanism candidate display, review assignment export, reviewer action form, coverage and audit history. The earlier shared interface/export contract remains available in [`stageC/reports/phase6/USER_WORKFLOWS_AND_REPORT_EXPORT.md`](../../../stageC/reports/phase6/USER_WORKFLOWS_AND_REPORT_EXPORT.md) and [`stageC/reports/phase6/API_CONTRACT_DRAFT.json`](../../../stageC/reports/phase6/API_CONTRACT_DRAFT.json).

The user workflow is: select a Stage C estimate and an exact Stage B Evidence_ID; inspect both records and their release/hash provenance; review dietary exposure separately from the study's reported dose or concentration; adjudicate the six comparability gates with source notes; then export the review state. Incomplete source or exposure data must remain pending or blocked.

The local API is implemented and binds only to loopback. It reads the pinned Stage B queue and Stage C releases, validates inputs, keeps machine triage separate from human decisions, and appends explicitly entered reviewer actions to a separate hash-chained Stage D log with versioned backup snapshots. It does not write Stage B source data or create automatic human decisions. Comparability remains a six-gate research workflow; it does not mean clinical equivalence, clinical significance, or risk. No dose ratio or patient-specific interpretation is provided. Browser source parsing passed `node --check`; application API tests passed **8/8** as part of the verified Stage C suite.

## Production prerequisites

- Stable, reviewed Stage C and Stage D schemas with compatibility tests.
- Completed Phase 2 deployment/scientific prerequisites and Phase 4/5 validation work.
- Authentication, role-based access, audit logs, privacy/security review, input hardening, accessibility review, incident monitoring, and immutable export integrity checks.
- A source-citation review path and clearly assigned human reviewers for unresolved evidence.
- API implementation tests proving the deployed service conforms to the draft contract.

The prototype has no authentication, role-based access control, multi-user coordination, privacy/security qualification, accessibility review, incident monitoring, production deployment, or expert-approved interpretation policy. Those remain production prerequisites. Passing software tests does not establish scientific validation.
