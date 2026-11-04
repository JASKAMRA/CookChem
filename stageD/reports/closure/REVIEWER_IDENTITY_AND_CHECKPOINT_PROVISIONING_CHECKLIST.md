# Stage D — Identity and Independent Checkpoint Provisioning Checklist

**State:** Owner provisioning required. No production service or credential is configured by this document.

## Identity provider and qualified reviewer roster

- [ ] Name the system owner and approving security owner.
- [ ] Select the approved identity provider and immutable issuer identifier.
- [ ] Define credential transport, authentication flow, expiry, session handling, and emergency revocation.
- [ ] Provision issuer-bound signing keys through an approved key-management service; document key IDs, rotation schedule, revocation feed, and verification method.
- [ ] Provision an authoritative reviewer roster. Store stable issuer/subject IDs; do not use display names as identity keys.
- [ ] Define the qualification taxonomy and evidence source for evidence review and mechanism review. Require a provider-verifiable qualification attestation per reviewer and review type; display-name or self-asserted qualification is not accepted.
- [ ] Define who may assign/reassign, who may submit `in_review`, and which qualification/role combination may submit `approved`, `rejected`, or `needs_revision`.
- [ ] Approve conflict-of-interest declarations, separation-of-duty policy, assignment visibility, reassignment reasons, and review recusal procedure.
- [ ] Verify provider contract methods: `authenticate`, `sign_audit_event`, `verify_audit_event`, `trusted_configuration`, `resolve_reviewer`, `authorize_assignment`, `qualification_attestation`, and `verify_qualification_attestation`.
- [ ] Run security review and synthetic integration tests; approve deployment only after configuration, roster, key trust, and revocation are independently checked.
- [ ] Record the deployment approval, provider version/config digest, roster version/digest, qualification policy version, test evidence, and accountable owner.

## Independent checkpoint service

- [ ] Name an owner and select a service administered outside the local audit-log storage trust domain.
- [ ] Specify immutable append/retention behavior, availability, access control, backup/restore, service identity, and incident recovery.
- [ ] Define how the service authenticates its receipt (signature/attestation), its verification key source, key rotation, and revocation.
- [ ] Define endpoint/configuration version, payload format, receipt/reference format, retry/idempotency behavior, and timeout/failure policy.
- [ ] Provision test and production endpoints through the authorized operator; keep credentials outside the repository.
- [ ] Execute synthetic publish/verify, tampering, truncation, retry, outage, and recovery checks; preserve outputs and service version.
- [ ] Obtain owner security/deployment approval and an independently verifiable test receipt before claiming operational status.

## Fail-closed condition

Until every applicable approval and provisioning item is recorded, review assignment and final-decision submissions must remain disabled for real users; a missing provider or checkpoint service must not be represented as approved or externally anchored. Synthetic provider tests demonstrate software behavior only.

## Adapter wiring and retry policy

The approved deployment must inject concrete owner-provisioned adapters into the Stage D workflow. The identity adapter must implement `authenticate`, `sign_audit_event`, `verify_audit_event`, `trusted_configuration`, `resolve_reviewer`, `authorize_assignment`, `qualification_attestation`, and `verify_qualification_attestation`. The exact issuer/key/roster/qualification configuration is deployed by the service owner; no credential values belong in repository files.

For checkpointing, construct the owner-approved `ExternalCheckpointProvider` and wrap it only if bounded retries are desired:

```python
from stage_d.checkpoint_retry import RetryingCheckpointProvider
from stage_d.audit_checkpoint import create_external_checkpoint

checkpoint_adapter = OwnerProvisionedCheckpointAdapter()  # supplied by deployment owner
retrying_checkpoint = RetryingCheckpointProvider(
    checkpoint_adapter,
    attempts=3,
    backoff_seconds=0.25,
)
receipt = create_external_checkpoint(
    audit_path,
    verified_queue,
    identity_provider=owner_approved_identity_adapter,
    checkpoint_provider=retrying_checkpoint,
)
```

The snippet is an interface example; `OwnerProvisionedCheckpointAdapter`, `audit_path`, `verified_queue`, and the identity adapter must come from the authorized deployment. The wrapper retries read-only verification on timeout/connection errors. It retries publication only when the concrete adapter explicitly sets `supports_idempotent_publish = True`; otherwise publication is attempted once to avoid duplicate checkpoints after an ambiguous network timeout. Configure endpoint, credentials, trust roots, and retention using the owner's secret-management/deployment controls, then preserve service version, receipt, digest, and verification output in the controlled audit record.
