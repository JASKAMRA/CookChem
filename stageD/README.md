# Stage D foundation — evidence and exposure contracts

Status: **IN_PROGRESS**. This directory defines initial contracts for versioned Stage B interaction evidence and Stage C exposure handoff. It does not alter Stage B data, calculate a clinical risk score, or infer applicability from a compound name alone.

## Interfaces

- `schemas/normalized_evidence.schema.json` preserves Stage B source fields alongside explicit normalized study categories and findings. Normalization is a convenience for filtering; it is not evidence acceptance, identity adjudication, or a quality score.
- `schemas/exposure_comparison.schema.json` records the comparability checks needed before a person reviews exposure alongside a study. A complete set of positive checks yields `READY_FOR_REVIEW`, not a clinical conclusion or dose-equivalence claim.
- `src/stage_d/contracts.py` provides deterministic normalization and three-state comparability gating. Unknown or ambiguous evidence stays visible and requires review.
- `schemas/mechanism_evidence.schema.json` and `schemas/mechanism_registry.schema.json` define a provenance-preserving mechanism-candidate record with nonnumeric, explicit review criteria. Mechanism class and target labels are candidate descriptions, never accepted findings or canonical target identities.
- `data/mechanism_evidence_registry.json` is a bounded, reproducibly built set of 25 source-checked Stage B rows across seven primary studies. `scripts/build_mechanism_registry.py` reads a pinned Stage B release and copies those rows exactly; it does not edit Stage B. All 25 remain pending independent review. See `reports/phase45_mechanism_registry_report.md` for source checks, counts, caveats, and next action.
- `data/evidence_review_queue.json` preserves a record-level work queue for all 317 pinned Stage B rows. Machine triage is separate from `NOT_REVIEWED` human status; it creates no source verification or expert decision. See `reports/phase5/evidence_review_queue_report.md`.
- `src/stage_d/interpretation.py` provides a nonclinical categorical research workflow with no numerical risk score or patient-specific advice. Its categories and decision table are a design foundation, not an expert-approved policy. See `reports/phase6/INTERPRETATION_FRAMEWORK_DESIGN.md`.

Stage D consumes exact compound IDs and release provenance. It does not rewrite or copy the source Stage B registry. Dietary exposure and experimental study dose remain separate quantities. A comparison must preserve route, dose basis, time window, and population/model context; unsupported comparisons are rejected or left pending.

## Testing

Run the synthetic contract tests from the repository root:

```powershell
python -m pip install -r stageC/requirements-dev.txt
python -m unittest discover -s stageD/tests -v
```

The suite formally validates positive/negative schema fixtures against Draft 2020-12 using the pinned `jsonschema` development dependency.

## Reviewer identity and action submission

New review submissions require an injected `ReviewerIdentityProvider` that authenticates the request, returns an `AuthenticatedReviewer` with an authorized `reviewer` or `expert` role, and signs/verifies audit events. Stage D includes no local/self-registration identity provider; without an integration, action submission and named assignment fail closed. New audit events record the provider issuer and subject, carry a provider-verified signature, and enforce explicit state transitions. Legacy 1.0 events remain readable but cannot authorize later actions on the same record or count as verified review. Synthetic identity providers belong in tests only and do not grant real reviewer approval.

Production adapters must bind signatures to issuer-specific trusted keys and derive subject roles from an approved reviewer roster; user-provided keys and role claims are not trusted. Authentication returns an expiry and signing key ID, rejects expired credentials, and action history preserves the key ID and credential-validity window. The adapter must implement `resolve_reviewer()` and `authorize_assignment()` for roster-controlled reassignment, verify historical signatures through key rotation/revocation policy, and report its trusted key source, reviewer roster, rotation policy and revocation source. `reviewer_authorization_diagnostics()` reports the missing configuration and keeps production availability false until deployment-owner review. See [`reports/closure/identity_provider_deployment_checklist.md`](reports/closure/identity_provider_deployment_checklist.md).

`assignment_ledger` provides a durable append-only JSONL assignment record with stable record-scoped IDs, assignment/reassignment events, signed actor/target references, duplicate-active prevention, a cross-process exclusive lock, chain verification, and recovery diagnostics. Reassignment is denied unless the provider resolves the target from its current roster and explicitly authorizes the operation. `build_durable_assignment_workload()` joins verified assignment events to authenticated review states. Local chains remain unanchored until a deployment configures an independent checkpoint provider.

`audit_checkpoint` defines an independent checkpoint adapter for both action and assignment chains. It compares source release, event count, and head digest to the external checkpoint. Local chain verification detects edits, internal deletions, duplicates and reordering; only an independently trusted checkpoint detects trailing-event deletion or complete-history replacement. Action schema 1.2.0 requires expert decisions to include source-located supporting/contradicting findings, limitations, and an explicit exposure-comparability state; these annotations do not alter the preserved source record.

`build_assignment_workload_summary()` validates assignment-export references, flags duplicate active assignments, and separates pending, in-progress, and terminal decisions. These exports are snapshots; use the durable ledger for assignment lifecycle and reassignment history.

`schema_validation.validate_draft_2020_12()` reports `VALID`, `INVALID`, `INVALID_SCHEMA`, or `UNAVAILABLE`. JSON parsing and application-level contract checks remain separate from formal Draft 2020-12 validation. When `jsonschema` is absent, the result is `UNAVAILABLE` with the required dependency prerequisite; syntax parsing is never reported as schema validation.

The end-to-end synthetic workflow test connects assignment export, authenticated submission, audit verification, coverage, workload, and refreshed export. The mechanism packet pipeline validates the registry-level source pin, candidate uniqueness, each record contract, and the source reference before producing packets with explicit empty reviewer fields. These checks prepare the workflow but do not constitute real reviewer authorization or human decisions.

## Not implemented here

This foundation does not source-verify or approve all 317 Stage B evidence records, adjudicate compound or drug identities, evaluate all literature, infer mechanism automatically, compare actual Stage C amounts with experimental doses, or provide patient-specific guidance. The 25 mechanism candidates and 317 queue records remain pending human review; they do not establish ordinary-food exposure equivalence or clinical risk.

## Cross-stage linkage and application design

`build_cross_stage_comparison` binds a single Phase 3 recipe ingredient estimate to an exact Stage B `Evidence_ID` and `Compound_ID`. It checks matching source-record IDs and release hashes, explicit units and nonnegative bounds, and fails closed for incomplete, meal-aggregate, or mismatched inputs. Phase 3 manifest verification is supplied by the caller after verifying the manifest and artifact hashes; the helper records that verification assertion and does not itself read or hash a release directory. Dietary amount, raw concentration, and any supported cooked concentration remain separate from source-reported experimental dose text and experimental concentration. No dimensional conversion, dose ratio, clinical interpretation, or risk estimate is produced.

The extended comparison contract is schema version `1.1.0`; the schema continues to accept the original `1.0.0` checklist records. New cross-stage records include release references, exact estimate and source IDs, dietary quantities, cooked-evidence status, missing inputs, and experimental dose text as unparsed source text. See [`reports/cross_stage_contract_hardening.md`](reports/cross_stage_contract_hardening.md). Application workflows and the non-production API/export draft are documented in [`reports/phase8/APPLICATION_READINESS.md`](reports/phase8/APPLICATION_READINESS.md) and [`../stageC/reports/phase6/USER_WORKFLOWS_AND_REPORT_EXPORT.md`](../stageC/reports/phase6/USER_WORKFLOWS_AND_REPORT_EXPORT.md).
