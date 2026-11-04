"""Identity-provider boundary for human review submissions.

Stage D intentionally ships no local-password or self-registration provider.
The application must inject a trusted provider that authenticates a subject
against an external or administrator-managed identity source.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Protocol


class ReviewerAuthenticationError(ValueError):
    """Raised when no trusted identity provider authorizes a review action."""


@dataclass(frozen=True)
class AuthenticatedReviewer:
    subject_id: str
    display_name: str
    roles: frozenset[str]
    issuer: str
    expires_at: str | None = None
    key_id: str | None = None


class ReviewerIdentityProvider(Protocol):
    """Trusted adapter contract; credentials are interpreted by the provider.

    Production adapters must authenticate against an administrator-approved
    identity source, derive roles from an authorized reviewer roster, and
    verify signatures using issuer-bound keys from a trusted key source. They
    must never accept user-supplied public keys or self-asserted role claims.
    """

    def authenticate(self, credentials: Any) -> AuthenticatedReviewer:
        """Return a verified principal or raise ReviewerAuthenticationError."""

    def sign_audit_event(self, reviewer: AuthenticatedReviewer, payload: bytes) -> str:
        """Sign the canonical event payload using provider-controlled key material."""

    def verify_audit_event(self, event: dict[str, Any]) -> bool:
        """Verify issuer-bound signature and the subject's role at event time."""

    def trusted_configuration(self) -> dict[str, Any]:
        """Describe issuer, trusted keys, roster, rotation policy, and revocation source."""

    def resolve_reviewer(self, issuer: str, subject_id: str) -> AuthenticatedReviewer | None:
        """Resolve an assignment target from the authoritative reviewer roster."""

    def authorize_assignment(self, actor: AuthenticatedReviewer, operation: str, *, target_issuer: str, target_subject_id: str) -> bool:
        """Authorize assignment creation/reassignment under current policy."""

    def qualification_attestation(self, issuer: str, subject_id: str, review_type: str) -> dict[str, Any] | None:
        """Return the authoritative qualification record for this review scope."""

    def verify_qualification_attestation(self, issuer: str, subject_id: str, review_type: str,
                                         attestation: dict[str, Any]) -> bool:
        """Verify the qualification claim and its validity at action time."""


def authenticate_reviewer(provider: ReviewerIdentityProvider | None, credentials: Any) -> AuthenticatedReviewer:
    if provider is None:
        raise ReviewerAuthenticationError("Review submission is disabled: no trusted identity provider is configured")
    authenticate = getattr(provider, "authenticate", None)
    if not callable(authenticate):
        raise ReviewerAuthenticationError("Configured reviewer identity provider has no authenticate() method")
    try:
        reviewer = authenticate(credentials)
    except ReviewerAuthenticationError:
        raise
    except Exception as exc:
        raise ReviewerAuthenticationError(f"Reviewer authentication failed: {exc}") from None
    if not isinstance(reviewer, AuthenticatedReviewer):
        raise ReviewerAuthenticationError("Identity provider did not return an authenticated reviewer principal")
    if any(not isinstance(value, str) or not value.strip() for value in (
        reviewer.subject_id, reviewer.display_name, reviewer.issuer,
    )):
        raise ReviewerAuthenticationError("Authenticated reviewer identity is incomplete")
    if not isinstance(reviewer.expires_at, str) or not isinstance(reviewer.key_id, str) or not reviewer.key_id.strip():
        raise ReviewerAuthenticationError("Authenticated reviewer must include credential expiry and signing key ID")
    try:
        expiry = datetime.fromisoformat(reviewer.expires_at.replace("Z", "+00:00"))
    except ValueError:
        raise ReviewerAuthenticationError("Credential expiry must be an ISO-8601 timestamp") from None
    if expiry.tzinfo is None or expiry <= datetime.now(timezone.utc):
        raise ReviewerAuthenticationError("Reviewer credential is expired or has no timezone")
    if (not isinstance(reviewer.roles, (set, frozenset)) or not reviewer.roles
            or any(not isinstance(role, str) or role not in {"reviewer", "expert"} for role in reviewer.roles)):
        raise ReviewerAuthenticationError("Authenticated reviewer has no supported review role")
    return reviewer


def reviewer_authorization_diagnostics(provider: ReviewerIdentityProvider | None) -> dict[str, Any]:
    """Report production authorization readiness without treating test providers as trusted."""
    required_methods = (
        "authenticate", "sign_audit_event", "verify_audit_event", "trusted_configuration",
        "resolve_reviewer", "authorize_assignment", "qualification_attestation",
        "verify_qualification_attestation",
    )
    if provider is None:
        return {
            "status": "BLOCKED",
            "production_authorization_available": False,
            "reason_codes": ["identity_provider_not_configured", "authorized_reviewer_roster_not_configured"],
            "message": "Configure an approved identity adapter, issuer-bound trusted keys, and reviewer-role roster before accepting real reviews.",
        }
    missing = [name for name in required_methods if not callable(getattr(provider, name, None))]
    if missing:
        return {
            "status": "BLOCKED",
            "production_authorization_available": False,
            "reason_codes": ["identity_provider_contract_incomplete"],
            "missing_provider_methods": missing,
            "message": "The adapter lacks required authentication, signature, or trusted-configuration capabilities.",
        }
    try:
        configuration = provider.trusted_configuration()
    except Exception:
        configuration = None
    required_values = (
        "issuer", "trusted_key_source", "reviewer_roster_source",
        "key_rotation_policy", "revocation_source",
    )
    if (not isinstance(configuration, dict)
            or configuration.get("status") != "READY"
            or any(not isinstance(configuration.get(key), str) or not configuration[key].strip()
                   for key in required_values)):
        return {
            "status": "BLOCKED",
            "production_authorization_available": False,
            "reason_codes": ["trusted_key_source_or_reviewer_roster_unverified"],
            "message": "The adapter has not attested an approved issuer, trusted key source, and authorized reviewer roster.",
        }
    return {
        "status": "CONFIGURED_REQUIRES_DEPLOYMENT_REVIEW",
        "production_authorization_available": False,
        "reason_codes": ["deployment_owner_approval_required"],
        "message": "Configuration is present; a deployment owner must verify the adapter and roster before production authorization is enabled.",
    }
