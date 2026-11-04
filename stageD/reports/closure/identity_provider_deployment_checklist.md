# Stage D identity-provider deployment checklist

Status: **BLOCKED — no production identity adapter, trusted keys, reviewer roster, or deployment-owner approval is configured.** This checklist defines the integration contract; it does not select a provider or grant access.

## Adapter contract

- `authenticate(credentials)` must validate the presented credential with an approved issuer, reject expired/revoked credentials, resolve the subject against the authorized roster, and return subject ID, issuer, display name, allowed roles, credential expiry and signing key ID.
- `sign_audit_event(principal, canonical_payload)` must use provider-controlled key material. Callers cannot supply a public or private key.
- `verify_audit_event(event)` must resolve `identity_issuer` and `identity_key_id` only through the trusted key source, verify the signature, apply key revocation/rotation policy, and confirm the subject had the recorded role at event time.
- `trusted_configuration()` must report `status=READY` only when issuer, trusted key source, reviewer roster source, key-rotation policy and revocation source are configured and verified.
- `resolve_reviewer(issuer, subject_id)` must resolve assignment targets from the authorized roster and return no result for unknown, inactive or revoked reviewers.
- `authorize_assignment(actor, operation, target_issuer, target_subject_id)` must authorize assignment creation/reassignment using current roster and policy. Reassignment is denied if this method is absent or returns anything other than literal `true`.

## Deployment-owner actions

1. Select and approve the identity service and issuer; record the owner and configuration version.
2. Configure issuer-bound key retrieval, trusted roots, key IDs, rotation overlap, historical verification and revocation handling.
3. Load the qualified reviewer roster and map roles from the authoritative source. Do not accept roles from form fields or user claims without roster verification.
4. Configure credential expiry enforcement and confirm each action rechecks authentication/authorization.
5. Configure an independently administered checkpoint destination for review and assignment chain heads.
6. Run adapter conformance tests for unknown issuer, forged/self-signed key, expired credential, revoked credential/key, role removal, role escalation, rotation and reassignment authorization.
7. Review the readiness diagnostic, approve deployment, and only then wire the adapter into the application.

No real reviewer or assignment is preconfigured in this repository. Until these actions are complete, production review authorization must remain disabled.
