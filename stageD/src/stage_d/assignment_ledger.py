"""Durable signed reviewer assignments with append-only history and locking."""
from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .reviewer_identity import (
    AuthenticatedReviewer,
    ReviewerAuthenticationError,
    ReviewerIdentityProvider,
    authenticate_reviewer,
)
from .evidence_review_workflow import (
    ReviewWorkflowError,
    _canonical,
    _event_hash,
    _identity_signing_payload,
    _latest_states,
    _record_maps,
    _safe_audit_path,
    validate_review_events,
    verify_review_action_log,
)


_ZERO_HASH = "0" * 64
_FIELDS = {
    "schema_version", "sequence", "event_id", "assignment_id", "event_type",
    "source_sha256", "review_id", "evidence_id", "actor", "reviewer",
    "previous_reviewer", "occurred_at", "reason", "identity_signature",
    "previous_event_sha256", "event_sha256",
}


class AssignmentLedgerError(ValueError):
    """Raised for an invalid assignment history or unauthorized operation."""


def stable_assignment_id(source_sha256: str, review_id: str) -> str:
    return "ASG-" + hashlib.sha256(f"{source_sha256}:{review_id}".encode("utf-8")).hexdigest()[:20].upper()


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise AssignmentLedgerError(f"Duplicate JSON key in assignment event: {key}")
        result[key] = value
    return result


def _actor_dict(reviewer: AuthenticatedReviewer, role: str) -> dict[str, str]:
    return {
        "subject_id": reviewer.subject_id,
        "display_name": reviewer.display_name,
        "issuer": reviewer.issuer,
        "key_id": reviewer.key_id or "",
        "credential_expires_at": reviewer.expires_at or "",
        "role": role,
    }


def _acquire_lock(path: Path, timeout_seconds: float = 30.0) -> tuple[Path, str]:
    lock = path.with_name(path.name + ".lock")
    token = str(uuid.uuid4())
    deadline = time.monotonic() + timeout_seconds
    lock.parent.mkdir(parents=True, exist_ok=True)
    while True:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            try:
                os.write(fd, token.encode("ascii"))
                os.fsync(fd)
            finally:
                os.close(fd)
            return lock, token
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise AssignmentLedgerError("Assignment ledger is locked; inspect and recover a stale lock explicitly") from None
            time.sleep(0.025)


def _release_lock(lock: Path, token: str) -> None:
    try:
        if lock.read_text(encoding="ascii") == token:
            lock.unlink()
    except FileNotFoundError:
        pass


def _append_event(path: Path, event: dict[str, Any], provider: ReviewerIdentityProvider, actor: AuthenticatedReviewer) -> dict[str, Any]:
    signer = getattr(provider, "sign_audit_event", None)
    if not callable(signer):
        raise AssignmentLedgerError("Assignment operations require provider-controlled event signing")
    try:
        signature = signer(actor, _identity_signing_payload(event))
    except Exception:
        raise AssignmentLedgerError("Identity provider could not sign the assignment event") from None
    if not isinstance(signature, str) or not signature.strip():
        raise AssignmentLedgerError("Identity provider returned an empty assignment signature")
    event["identity_signature"] = signature
    event["event_sha256"] = _event_hash(event)
    line = _canonical(event) + b"\n"
    fd = os.open(path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)
    try:
        offset = 0
        while offset < len(line):
            offset += os.write(fd, line[offset:])
        os.fsync(fd)
    finally:
        os.close(fd)
    return event


def verify_assignment_ledger(
    path: str | Path,
    queue: dict[str, Any],
    *,
    identity_provider: ReviewerIdentityProvider | None,
) -> list[dict[str, Any]]:
    """Verify source links, event sequence, signatures, transitions, and hash chain."""
    if identity_provider is None or not callable(getattr(identity_provider, "verify_audit_event", None)):
        raise AssignmentLedgerError("Assignment history verification requires a trusted identity verifier")
    by_review, by_evidence = _record_maps(queue)
    ledger = _safe_audit_path(path)
    if not ledger.exists():
        return []
    data = ledger.read_bytes()
    if data and not data.endswith(b"\n"):
        raise AssignmentLedgerError("Assignment ledger is truncated; final event has no newline")
    try:
        lines = data.decode("utf-8").splitlines()
    except UnicodeDecodeError:
        raise AssignmentLedgerError("Assignment ledger must be UTF-8 JSONL") from None
    events: list[dict[str, Any]] = []
    latest: dict[str, dict[str, Any]] = {}
    seen_event_ids: set[str] = set()
    previous_hash = _ZERO_HASH
    for number, line in enumerate(lines, start=1):
        try:
            event = json.loads(line, object_pairs_hook=_unique_pairs)
        except json.JSONDecodeError:
            raise AssignmentLedgerError(f"Malformed assignment event at line {number}") from None
        except AssignmentLedgerError as exc:
            raise AssignmentLedgerError(f"Malformed assignment event at line {number}: {exc}") from None
        if not isinstance(event, dict) or set(event) != _FIELDS or event.get("schema_version") != "1.0.0":
            raise AssignmentLedgerError(f"Unexpected assignment event shape at line {number}")
        if type(event.get("sequence")) is not int or event["sequence"] != number:
            raise AssignmentLedgerError(f"Noncontiguous assignment sequence at line {number}")
        if not isinstance(event.get("event_id"), str) or event["event_id"] in seen_event_ids:
            raise AssignmentLedgerError(f"Missing or duplicate assignment event ID at line {number}")
        seen_event_ids.add(event["event_id"])
        review_id, evidence_id = event.get("review_id"), event.get("evidence_id")
        record = by_review.get(review_id) if isinstance(review_id, str) else None
        if (record is None or by_evidence.get(evidence_id) is not record
                or event.get("source_sha256") != queue["source"]["sha256"]
                or event.get("assignment_id") != stable_assignment_id(queue["source"]["sha256"], review_id)):
            raise AssignmentLedgerError(f"Assignment source reference mismatch at line {number}")
        if event.get("previous_event_sha256") != previous_hash or event.get("event_sha256") != _event_hash(event):
            raise AssignmentLedgerError(f"Assignment hash chain is invalid at line {number}")
        try:
            verified = identity_provider.verify_audit_event(event)
        except Exception:
            verified = False
        if verified is not True:
            raise AssignmentLedgerError(f"Assignment signature is invalid at line {number}")
        reviewer = event.get("reviewer")
        actor = event.get("actor")
        if not isinstance(reviewer, dict) or not isinstance(actor, dict):
            raise AssignmentLedgerError(f"Assignment actor or reviewer is missing at line {number}")
        prior = latest.get(review_id)
        if event["event_type"] == "ASSIGNED":
            if prior is not None or event.get("previous_reviewer") is not None:
                raise AssignmentLedgerError(f"Duplicate initial assignment at line {number}")
        elif event["event_type"] == "REASSIGNED":
            if prior is None or event.get("previous_reviewer") != prior["reviewer"] or reviewer == prior["reviewer"]:
                raise AssignmentLedgerError(f"Invalid reassignment transition at line {number}")
        else:
            raise AssignmentLedgerError(f"Unknown assignment event type at line {number}")
        for label, identity in (("actor", actor), ("reviewer", reviewer)):
            required_identity_fields = ("subject_id", "display_name", "issuer", "key_id", "credential_expires_at", "role")
            if not all(isinstance(identity.get(key), str) and identity[key].strip() for key in required_identity_fields):
                raise AssignmentLedgerError(f"Assignment {label} identity is incomplete at line {number}")
        if reviewer.get("role") != "reviewer" or actor.get("role") not in {"reviewer", "expert"}:
            raise AssignmentLedgerError(f"Assignment actor or target role is invalid at line {number}")
        try:
            timestamp = datetime.fromisoformat(str(event.get("occurred_at", "")).replace("Z", "+00:00"))
        except ValueError:
            raise AssignmentLedgerError(f"Assignment timestamp is invalid at line {number}") from None
        if timestamp.tzinfo is None:
            raise AssignmentLedgerError(f"Assignment timestamp has no timezone at line {number}")
        if not isinstance(event.get("reason"), str) or not event["reason"].strip():
            raise AssignmentLedgerError(f"Assignment rationale is missing at line {number}")
        for identity_label, identity in (("actor", actor), ("reviewer", reviewer)):
            try:
                expiry = datetime.fromisoformat(identity["credential_expires_at"].replace("Z", "+00:00"))
            except (KeyError, AttributeError, TypeError, ValueError):
                raise AssignmentLedgerError(f"{identity_label} credential expiry is invalid at line {number}") from None
            if expiry.tzinfo is None or expiry <= timestamp:
                raise AssignmentLedgerError(f"{identity_label} credential was expired at assignment time on line {number}")
        latest[review_id] = event
        previous_hash = event["event_sha256"]
        events.append(event)
    return events


def _append_operation(
    path: str | Path,
    queue: dict[str, Any],
    *,
    review_id: str,
    identity_provider: ReviewerIdentityProvider | None,
    credentials: Any,
    reason: str,
    operation: str,
    target_issuer: str | None = None,
    target_subject_id: str | None = None,
) -> dict[str, Any]:
    if identity_provider is None:
        raise AssignmentLedgerError("Assignment changes are disabled: no trusted identity provider is configured")
    try:
        actor = authenticate_reviewer(identity_provider, credentials)
    except ReviewerAuthenticationError as exc:
        raise AssignmentLedgerError(str(exc)) from None
    try:
        by_review, _ = _record_maps(queue)
    except Exception as exc:
        raise AssignmentLedgerError(f"Invalid evidence queue: {exc}") from None
    record = by_review.get(review_id) if isinstance(review_id, str) else None
    if record is None:
        raise AssignmentLedgerError("Assignment requires a valid queue review_id")
    if not isinstance(reason, str) or not reason.strip():
        raise AssignmentLedgerError("Assignment rationale/reassignment reason is required")
    ledger = _safe_audit_path(path)
    lock, token = _acquire_lock(ledger)
    try:
        events = verify_assignment_ledger(ledger, queue, identity_provider=identity_provider)
        latest = next((event for event in reversed(events) if event["review_id"] == review_id), None)
        authorizer = getattr(identity_provider, "authorize_assignment", None)
        if not callable(authorizer):
            raise AssignmentLedgerError("Provider lacks authoritative assignment authorization")
        if operation == "ASSIGNED":
            target = actor
            if "reviewer" not in actor.roles:
                raise AssignmentLedgerError("Only a roster-authorized reviewer may self-assign")
            if latest is not None:
                raise AssignmentLedgerError("Evidence record already has an active assignment")
            if authorizer(actor, "assign_self", target_issuer=actor.issuer, target_subject_id=actor.subject_id) is not True:
                raise AssignmentLedgerError("Provider denied reviewer assignment")
            old_target = None
        else:
            if latest is None:
                raise AssignmentLedgerError("Cannot reassign an evidence record that is not assigned")
            if not callable(getattr(identity_provider, "resolve_reviewer", None)):
                raise AssignmentLedgerError("Provider cannot resolve an assignment target from the authorized roster")
            if not isinstance(target_issuer, str) or not isinstance(target_subject_id, str):
                raise AssignmentLedgerError("Reassignment requires a target issuer and subject ID")
            if authorizer(actor, "reassign", target_issuer=target_issuer, target_subject_id=target_subject_id) is not True:
                raise AssignmentLedgerError("Provider denied reassignment under current authorization policy")
            try:
                target = identity_provider.resolve_reviewer(target_issuer, target_subject_id)
            except Exception:
                target = None
            if (not isinstance(target, AuthenticatedReviewer)
                    or target.issuer != target_issuer
                    or target.subject_id != target_subject_id
                    or "reviewer" not in target.roles):
                raise AssignmentLedgerError("Reassignment target is not an active roster-authorized reviewer")
            if not isinstance(target.expires_at, str) or not target.key_id:
                raise AssignmentLedgerError("Reassignment target lacks credential expiry or key identity")
            try:
                target_expiry = datetime.fromisoformat(target.expires_at.replace("Z", "+00:00"))
            except ValueError:
                raise AssignmentLedgerError("Reassignment target expiry is invalid") from None
            if target_expiry.tzinfo is None or target_expiry <= datetime.now(timezone.utc):
                raise AssignmentLedgerError("Reassignment target is expired or revoked")
            old_target = latest["reviewer"]
            if _actor_dict(target, "reviewer") == old_target:
                raise AssignmentLedgerError("Reassignment target is already the current reviewer")
        event = {
            "schema_version": "1.0.0",
            "sequence": len(events) + 1,
            "event_id": str(uuid.uuid4()),
            "assignment_id": stable_assignment_id(queue["source"]["sha256"], review_id),
            "event_type": operation,
            "source_sha256": queue["source"]["sha256"],
            "review_id": review_id,
            "evidence_id": record["source_reference"]["evidence_id"],
            "actor": _actor_dict(actor, "reviewer" if "reviewer" in actor.roles else "expert"),
            "reviewer": _actor_dict(target, "reviewer"),
            "previous_reviewer": old_target,
            "occurred_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
            "reason": reason.strip(),
            "previous_event_sha256": events[-1]["event_sha256"] if events else _ZERO_HASH,
        }
        return _append_event(ledger, event, identity_provider, actor)
    finally:
        _release_lock(lock, token)


def assign_to_self(path: str | Path, queue: dict[str, Any], *, review_id: str,
                   identity_provider: ReviewerIdentityProvider | None, credentials: Any,
                   reason: str) -> dict[str, Any]:
    return _append_operation(path, queue, review_id=review_id, identity_provider=identity_provider,
                             credentials=credentials, reason=reason, operation="ASSIGNED")


def reassign(path: str | Path, queue: dict[str, Any], *, review_id: str, target_issuer: str,
             target_subject_id: str, identity_provider: ReviewerIdentityProvider | None,
             credentials: Any, reason: str) -> dict[str, Any]:
    return _append_operation(path, queue, review_id=review_id, identity_provider=identity_provider,
                             credentials=credentials, reason=reason, operation="REASSIGNED",
                             target_issuer=target_issuer, target_subject_id=target_subject_id)


def assignment_ledger_diagnostics(path: str | Path, queue: dict[str, Any], *,
                                  identity_provider: ReviewerIdentityProvider | None) -> dict[str, Any]:
    """Return valid-local-chain status or a recovery-required diagnostic."""
    try:
        ledger_path = _safe_audit_path(path)
        events = verify_assignment_ledger(ledger_path, queue, identity_provider=identity_provider)
    except AssignmentLedgerError as exc:
        return {"status": "RECOVERY_REQUIRED", "event_count": None, "error": str(exc)}
    lock_path = ledger_path.with_name(ledger_path.name + ".lock")
    if lock_path.exists():
        return {
            "status": "LOCK_PRESENT_REVIEW_REQUIRED",
            "event_count": len(events),
            "active_assignment_count": len({event["review_id"] for event in events}),
            "error": "A writer lock remains; determine whether a writer is active before removing it.",
            "external_anchor_status": "NOT_CHECKED",
        }
    latest = {}
    for event in events:
        latest[event["review_id"]] = event
    return {
        "status": "VALID_LOCAL_CHAIN" if events else "EMPTY_VALID_LOCAL_CHAIN",
        "event_count": len(events),
        "active_assignment_count": len(latest),
        "audit_head_sha256": events[-1]["event_sha256"] if events else _ZERO_HASH,
        "external_anchor_status": "NOT_CONFIGURED",
        "note": "Local verification is not protection against replacement of the complete ledger without an independent checkpoint.",
    }


def build_durable_assignment_workload(
    queue: dict[str, Any],
    assignment_events: list[Mapping[str, Any]],
    review_events: list[Mapping[str, Any]],
    *,
    identity_provider: ReviewerIdentityProvider | None,
) -> dict[str, Any]:
    """Join previously verified assignment history to authenticated review states."""
    validate_review_events(queue, review_events, identity_provider=identity_provider)
    latest_assignment: dict[str, Mapping[str, Any]] = {}
    for event in assignment_events:
        latest_assignment[str(event["review_id"])] = event
    states = _latest_states(queue, review_events)
    workloads: dict[str, dict[str, int]] = {}
    for review_id, event in latest_assignment.items():
        owner = event["reviewer"]["display_name"]
        status = states.get(review_id, "NOT_REVIEWED")
        bucket = "completed" if status in {"EXPERT_ACCEPTED", "EXPERT_REJECTED"} else "in_progress" if status != "NOT_REVIEWED" else "pending"
        counters = workloads.setdefault(owner, {"pending": 0, "in_progress": 0, "completed": 0})
        counters[bucket] += 1
    assigned_ids = set(latest_assignment)
    return {
        "schema_version": "1.0.0",
        "record_count": len(queue["records"]),
        "assigned_record_count": len(assigned_ids),
        "unassigned_record_count": len(queue["records"]) - len(assigned_ids),
        "pending_count": sum(value["pending"] for value in workloads.values()),
        "in_progress_count": sum(value["in_progress"] for value in workloads.values()),
        "completed_count": sum(value["completed"] for value in workloads.values()),
        "reviewer_workloads": dict(sorted(workloads.items())),
        "assignment_event_count": len(assignment_events),
        "reassignment_event_count": sum(event["event_type"] == "REASSIGNED" for event in assignment_events),
        "assignment_head_sha256": assignment_events[-1]["event_sha256"] if assignment_events else _ZERO_HASH,
        "review_audit_head_sha256": review_events[-1]["event_sha256"] if review_events else _ZERO_HASH,
        "decision_and_approval_created": False,
    }


def build_verified_durable_assignment_workload(
    assignment_path: str | Path,
    review_log_path: str | Path,
    queue: dict[str, Any],
    *,
    identity_provider: ReviewerIdentityProvider | None,
) -> dict[str, Any]:
    """Verify both ledgers before deriving current reviewer workload."""
    assignments = verify_assignment_ledger(assignment_path, queue, identity_provider=identity_provider)
    try:
        reviews = verify_review_action_log(review_log_path, queue, identity_provider=identity_provider)
    except ReviewWorkflowError as exc:
        raise AssignmentLedgerError(f"Review action history failed local verification: {exc}") from None
    return build_durable_assignment_workload(queue, assignments, reviews, identity_provider=identity_provider)
