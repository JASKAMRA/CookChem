"""External checkpoint adapter boundary for authenticated audit-chain heads."""
from __future__ import annotations

from typing import Any, Protocol
import hashlib
from collections.abc import Mapping, Sequence

from .evidence_review_workflow import (
    ReviewWorkflowError,
    _ZERO_HASH,
    _canonical,
    _event_hash,
    verify_review_action_log,
)
from .reviewer_identity import ReviewerIdentityProvider


class AuditCheckpointError(ValueError):
    """Raised when a checkpoint cannot be created or verified."""


class ExternalCheckpointProvider(Protocol):
    """Trusted independent store/signature service; must not share local trust domain."""

    def publish_checkpoint(self, payload: bytes) -> str:
        """Durably publish immutable bytes and return an independently verifiable reference."""

    def verify_checkpoint(self, payload: bytes, external_reference: str) -> bool:
        """Verify the external reference binds to this exact payload and trusted signer."""


def _payload(queue: Mapping[str, Any], events: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    expected_previous = _ZERO_HASH
    for index, event in enumerate(events, start=1):
        if type(event.get("sequence")) is not int or event.get("sequence") != index:
            raise AuditCheckpointError(f"Cannot checkpoint invalid audit sequence at event {index}")
        if event.get("previous_event_sha256") != expected_previous or event.get("event_sha256") != _event_hash(event):
            raise AuditCheckpointError(f"Cannot checkpoint invalid audit chain at event {index}")
        expected_previous = str(event["event_sha256"])
    return {
        "format": "cookrisk-audit-head-v1",
        "source_release_id": queue["source"]["release_id"],
        "source_sha256": queue["source"]["sha256"],
        "event_count": len(events),
        "head_sha256": expected_previous,
    }


def _assignment_payload(queue: Mapping[str, Any], events: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    previous = _ZERO_HASH
    for index, event in enumerate(events, start=1):
        if type(event.get("sequence")) is not int or event.get("sequence") != index:
            raise AuditCheckpointError(f"Cannot checkpoint invalid assignment sequence at event {index}")
        if event.get("previous_event_sha256") != previous or event.get("event_sha256") != _event_hash(event):
            raise AuditCheckpointError(f"Cannot checkpoint invalid assignment chain at event {index}")
        previous = str(event["event_sha256"])
    return {
        "format": "cookrisk-assignment-head-v1",
        "source_release_id": queue["source"]["release_id"],
        "source_sha256": queue["source"]["sha256"],
        "event_count": len(events),
        "head_sha256": previous,
    }


def create_external_checkpoint(
    path: str,
    queue: dict[str, Any],
    *,
    identity_provider: ReviewerIdentityProvider | None,
    checkpoint_provider: ExternalCheckpointProvider | None,
) -> dict[str, Any]:
    if checkpoint_provider is None:
        raise AuditCheckpointError("External checkpoint creation is unavailable: no independent checkpoint provider is configured")
    try:
        events = verify_review_action_log(path, queue, identity_provider=identity_provider)
    except ReviewWorkflowError as exc:
        raise AuditCheckpointError(f"Audit log failed local verification: {exc}") from None
    payload = _payload(queue, events)
    serialized = _canonical(payload)
    try:
        reference = checkpoint_provider.publish_checkpoint(serialized)
    except Exception:
        raise AuditCheckpointError("External checkpoint provider failed to publish the audit head") from None
    if not isinstance(reference, str) or not reference.strip():
        raise AuditCheckpointError("External checkpoint provider returned no reference")
    return {
        "payload": payload,
        "payload_sha256": hashlib.sha256(serialized).hexdigest(),
        "external_reference": reference,
        "status": "EXTERNALLY_ANCHORED",
    }


def verify_external_checkpoint(
    path: str,
    queue: dict[str, Any],
    checkpoint: Mapping[str, Any],
    *,
    identity_provider: ReviewerIdentityProvider | None,
    checkpoint_provider: ExternalCheckpointProvider | None,
) -> dict[str, Any]:
    if checkpoint_provider is None:
        return {"status": "UNAVAILABLE", "reason": "external_checkpoint_provider_not_configured"}
    try:
        events = verify_review_action_log(path, queue, identity_provider=identity_provider)
    except ReviewWorkflowError as exc:
        return {"status": "LOCAL_CHAIN_INVALID", "reason": str(exc)}
    expected = _payload(queue, events)
    supplied = checkpoint.get("payload")
    if not isinstance(supplied, Mapping) or dict(supplied) != expected:
        return {"status": "CHECKPOINT_MISMATCH", "reason": "checkpoint_payload_does_not_match_current_chain_head"}
    serialized = _canonical(expected)
    if checkpoint.get("payload_sha256") != hashlib.sha256(serialized).hexdigest():
        return {"status": "CHECKPOINT_MISMATCH", "reason": "checkpoint_payload_digest_is_invalid"}
    reference = checkpoint.get("external_reference")
    if not isinstance(reference, str) or not reference.strip():
        return {"status": "CHECKPOINT_MISMATCH", "reason": "external_reference_is_missing"}
    try:
        valid = checkpoint_provider.verify_checkpoint(serialized, reference)
    except Exception:
        valid = False
    return {
        "status": "EXTERNALLY_ANCHORED" if valid is True else "EXTERNAL_CHECKPOINT_INVALID",
        "event_count": len(events),
        "head_sha256": expected["head_sha256"],
        "external_reference": reference,
    }


def audit_history_diagnostics(
    path: str,
    queue: dict[str, Any],
    *,
    identity_provider: ReviewerIdentityProvider | None,
    checkpoint: Mapping[str, Any] | None = None,
    checkpoint_provider: ExternalCheckpointProvider | None = None,
) -> dict[str, Any]:
    try:
        events = verify_review_action_log(path, queue, identity_provider=identity_provider)
    except ReviewWorkflowError as exc:
        return {"local_integrity_status": "INVALID", "error": str(exc), "external_integrity_status": "NOT_CHECKED"}
    result = {
        "local_integrity_status": "VALID_LOCAL_CHAIN",
        "event_count": len(events),
        "head_sha256": events[-1]["event_sha256"] if events else _ZERO_HASH,
        "external_integrity_status": "NOT_CONFIGURED" if checkpoint is None else "NOT_CHECKED",
        "note": "A locally valid hash chain does not detect removal of trailing events or replacement of the complete history without an independent checkpoint.",
    }
    if checkpoint is not None:
        result["external_integrity"] = verify_external_checkpoint(
            path, queue, checkpoint,
            identity_provider=identity_provider,
            checkpoint_provider=checkpoint_provider,
        )
        result["external_integrity_status"] = result["external_integrity"]["status"]
    return result


def create_assignment_checkpoint(
    path: str,
    queue: dict[str, Any],
    *,
    identity_provider: ReviewerIdentityProvider | None,
    checkpoint_provider: ExternalCheckpointProvider | None,
) -> dict[str, Any]:
    if checkpoint_provider is None:
        raise AuditCheckpointError("External assignment checkpoint provider is not configured")
    from .assignment_ledger import AssignmentLedgerError, verify_assignment_ledger
    try:
        events = verify_assignment_ledger(path, queue, identity_provider=identity_provider)
    except AssignmentLedgerError as exc:
        raise AuditCheckpointError(f"Assignment ledger failed local verification: {exc}") from None
    payload = _assignment_payload(queue, events)
    serialized = _canonical(payload)
    try:
        reference = checkpoint_provider.publish_checkpoint(serialized)
    except Exception:
        raise AuditCheckpointError("External checkpoint provider failed to publish the assignment head") from None
    if not isinstance(reference, str) or not reference.strip():
        raise AuditCheckpointError("External assignment checkpoint provider returned no reference")
    return {
        "payload": payload,
        "payload_sha256": hashlib.sha256(serialized).hexdigest(),
        "external_reference": reference,
        "status": "EXTERNALLY_ANCHORED",
    }


def verify_assignment_checkpoint(
    path: str,
    queue: dict[str, Any],
    checkpoint: Mapping[str, Any],
    *,
    identity_provider: ReviewerIdentityProvider | None,
    checkpoint_provider: ExternalCheckpointProvider | None,
) -> dict[str, Any]:
    if checkpoint_provider is None:
        return {"status": "UNAVAILABLE", "reason": "external_checkpoint_provider_not_configured"}
    from .assignment_ledger import AssignmentLedgerError, verify_assignment_ledger
    try:
        events = verify_assignment_ledger(path, queue, identity_provider=identity_provider)
    except AssignmentLedgerError as exc:
        return {"status": "LOCAL_CHAIN_INVALID", "reason": str(exc)}
    expected = _assignment_payload(queue, events)
    if checkpoint.get("payload") != expected:
        return {"status": "CHECKPOINT_MISMATCH", "reason": "assignment_checkpoint_does_not_match_current_ledger"}
    serialized = _canonical(expected)
    if checkpoint.get("payload_sha256") != hashlib.sha256(serialized).hexdigest():
        return {"status": "CHECKPOINT_MISMATCH", "reason": "assignment_checkpoint_digest_is_invalid"}
    reference = checkpoint.get("external_reference")
    try:
        valid = isinstance(reference, str) and checkpoint_provider.verify_checkpoint(serialized, reference)
    except Exception:
        valid = False
    return {"status": "EXTERNALLY_ANCHORED" if valid is True else "EXTERNAL_CHECKPOINT_INVALID"}
