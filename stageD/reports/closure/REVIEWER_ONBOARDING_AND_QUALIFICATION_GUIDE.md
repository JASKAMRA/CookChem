# Stage D Qualified Reviewer Onboarding — Owner Package

**Purpose:** Onboard real qualified reviewers only after the project owner provisions the trusted identity and qualification services. This guide does not assign anyone, claim qualifications, or create review decisions.

## Worklist files

- `stageD/reports/closure/worklists_v1.0.0/evidence_unassigned.csv` — 317 records.
- `stageD/reports/closure/worklists_v1.0.0/mechanism_unassigned.csv` — 25 records.
- Source register: `qualified_review_readiness_register_v1.2.0.json` (exact-byte SHA-256: `9953d65d8733d45cf3efa9d62c08c8bb6579eb16c07051f504bc74ae46f603bb`).

Both worklists have empty reviewer, date, decision, rationale, evidence-reference, and sign-off fields. They are pools for assignment, not proof of assignment. Stable review IDs and Stage D source release/digest/locator references must remain attached when imported into the owner-controlled review system. Do not edit CSV rows to simulate assignments; create assignment events through the authenticated workflow.

## Owner-controlled qualification verification procedure

1. Approve a qualification policy before inviting reviewers. Define acceptable expertise and evidence for `evidence` and `mechanism` review separately; identify which dispositions require an expert or adjudicator. No policy is inferred from the machine triage or this software.
2. Verify the person's identity, relevant credentials/experience, current institutional or professional standing where applicable, conflict-of-interest disclosure, and scope-specific competence through the owner's approved process. Record the verification evidence in the owner's controlled roster system.
3. The identity-provider owner enrolls a stable issuer/subject identity, roles, expiry, key ID and revocation status. The user may not self-assert identity, role, qualifications, signing keys, or reviewer name.
4. The trusted provider's `qualification_attestation(issuer, subject_id, review_type)` must return an owner-verified attestation and `verify_qualification_attestation(...)` must validate it. The attestation reference and scope must be auditable. Do not place credentials or private keys in this repository.
5. A review coordinator with provider-authorized assignment permission allocates a record using `assign_reviewer(...)`. The target must be resolved from the provider roster and qualified for the record type. The output is a signed, append-only assignment event.
6. The assigned reviewer opens the cited source in the owner's authorized environment, confirms record/source identity and locator, preserves positive/negative/null/conflicting outcomes separately, records supporting and contradictory evidence, limitations, rationale, and unresolved questions, then advances through `in_review`.
7. Only the assigned, authenticated, qualified reviewer may submit a final disposition. `approved`/`rejected` require expert role, source-located evidence references, nonempty rationale, a sign-off record reference, and a provider signature. `needs_revision` must include a rationale and evidence reference; it can be reassigned. Approved/rejected are terminal in the current policy; corrections require a future governed policy.
8. The owner verifies the event chain and independent checkpoint receipt before counting a decision. Until identity and checkpoint services are deployed and owner-approved, no real assignment or decision may be accepted through this local preparation.

## Reviewer checklist per record

- [ ] Stable `review_id`, evidence ID, compound ID, study ID and source locator match the authorized source.
- [ ] Source access level and citation metadata are recorded accurately; missing DOI/PMID remains explicitly unresolved.
- [ ] Identity/analyte, study design, population/model, preparation, dose basis, timing, outcome and endpoint context are reviewed within source limits.
- [ ] Supporting and contradictory findings, uncertainty, missing evidence and limitations have source locators.
- [ ] Outcome is preserved as positive, negative, null, mixed/conflicting, unclear, or unreported as supported; no missing value is recoded as negative.
- [ ] Decision and rationale are entered under the authenticated reviewer; evidence references and sign-off reference are present for a final disposition.
- [ ] Assignment/action chain and independent checkpoint receipt verify successfully.

## Current readiness

The local progress snapshot reports 342 pending, zero assigned, zero decided, and zero reviewer-specific worklists because the trusted roster/provider is not provisioned. The worklists above are unassigned pools only. Owner/security provisioning checklist: `REVIEWER_IDENTITY_AND_CHECKPOINT_PROVISIONING_CHECKLIST.md`.

## Assignment and decision return procedure

1. The owner/coordinator provisions the identity provider, qualified roster, and policy first. A coordinator assigns a stable `review_id` through the authenticated review-operations service; do not fill the CSV reviewer columns by hand.
2. The reviewer receives the assignment-specific worklist from the authenticated service and confirms the `review_id`, evidence/study identifiers, source release/reference, locator, and source digest in the owner's authorized source environment. The register is an index; it is not itself proof that a source was inspected.
3. The reviewer submits `in_review`, then a final `approved`, `rejected`, or `needs_revision` disposition through the authenticated service. The submission must carry a nonempty rationale and source-located evidence references. A final approval/rejection also requires the authorized expert role and a sign-off reference. The provider supplies the identity signature and qualification attestation; the client must not supply or edit these fields.
4. The service appends the event to the versioned audit chain. The owner verifies the full chain, record provenance, reviewer qualification and signature, then publishes/verifies the external checkpoint. A failed check means the event is not counted.
5. For an offline review, return the completed rationale/evidence packet to the owner-controlled coordinator. The coordinator must authenticate the reviewer and enter/verify the decision through the provider workflow. A returned CSV, unsigned JSON, display name, or self-asserted sign-off is not importable evidence and must not change status. No separate bulk-import interface is currently authorized or implemented.
6. The owner exports a progress snapshot only from the verified event chain and preserves the checkpoint receipt. Update pending counts only after the verified service event exists. `needs_revision` remains nonfinal and requires a new governed assignment cycle.

Current authorized review pathway: the provider-injected `assign_reviewer` and `submit_review_status` operations in `stageD/src/stage_d/review_operations.py`, followed by `read_verified_review_operations` and owner checkpoint verification. This procedure does not create assignments or decisions in the current unprovisioned environment.
