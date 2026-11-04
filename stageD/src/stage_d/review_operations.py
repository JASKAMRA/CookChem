"""Qualified reviewer assignment and decision workflow for the Stage D index.

This provider-injected service has no production identity implementation. It
uses only an explicitly supplied readiness-register object and Stage D audit
path; without a trusted provider, every write fails closed.
"""
from __future__ import annotations

import hashlib
import json
import os
from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Protocol

from .reviewer_identity import AuthenticatedReviewer, ReviewerAuthenticationError, authenticate_reviewer

STATUSES = {"pending", "assigned", "in_review", "approved", "rejected", "needs_revision"}
FINAL_STATUSES = {"approved", "rejected"}
ZERO_HASH = "0" * 64


class ReviewOperationsError(ValueError):
    """Invalid review operation, provider authorization, or audit history."""


class QualifiedIdentityProvider(Protocol):
    def authenticate(self, credentials: Any) -> AuthenticatedReviewer: ...
    def sign_audit_event(self, reviewer: AuthenticatedReviewer, payload: bytes) -> str: ...
    def verify_audit_event(self, event: dict[str, Any]) -> bool: ...
    def resolve_reviewer(self, issuer: str, subject_id: str) -> AuthenticatedReviewer | None: ...
    def authorize_assignment(self, actor: AuthenticatedReviewer, operation: str, *, target_issuer: str, target_subject_id: str) -> bool: ...
    def qualification_attestation(self, issuer: str, subject_id: str, review_type: str) -> Mapping[str, Any] | None: ...
    def verify_qualification_attestation(self, issuer: str, subject_id: str, review_type: str, attestation: Mapping[str, Any]) -> bool: ...


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _hash_event(event: Mapping[str, Any]) -> str:
    payload = dict(event)
    payload.pop("event_sha256", None)
    return hashlib.sha256(_canonical(payload)).hexdigest()


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ReviewOperationsError(f"Duplicate JSON key in review operations audit: {key}")
        result[key] = value
    return result


def _register_map(register: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    rows = register.get("reviews")
    if not isinstance(rows, list):
        raise ReviewOperationsError("Readiness register must contain a reviews array")
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ReviewOperationsError("Readiness register contains a malformed review row")
        record_id, kind = row.get("review_id"), row.get("review_type")
        if not isinstance(record_id, str) or not record_id or kind not in {"evidence", "mechanism"}:
            raise ReviewOperationsError("Readiness register contains an invalid stable ID or review type")
        if record_id in result:
            raise ReviewOperationsError(f"Duplicate stable review ID: {record_id}")
        if row.get("review_status") != "PENDING_HUMAN_REVIEW":
            raise ReviewOperationsError("Base readiness register must preserve its pending-only state")
        result[record_id] = row
    return result


def _safe_log_path(path: str | Path) -> Path:
    root = (Path(__file__).resolve().parents[2]).resolve(strict=True)
    target = Path(os.path.abspath(Path(path) if Path(path).is_absolute() else root / path))
    try:
        relative = target.relative_to(root)
    except ValueError:
        raise ReviewOperationsError("Review operations audit must remain inside Stage D") from None
    cursor = root
    for part in relative.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ReviewOperationsError("Review operations audit path cannot traverse symbolic links")
    if target.exists() and not target.is_file():
        raise ReviewOperationsError("Review operations audit path must be a regular file")
    return target


def _qualification(provider: QualifiedIdentityProvider, reviewer: AuthenticatedReviewer, review_type: str) -> dict[str, Any]:
    get_attestation = getattr(provider, "qualification_attestation", None)
    verify_attestation = getattr(provider, "verify_qualification_attestation", None)
    if not callable(get_attestation) or not callable(verify_attestation):
        raise ReviewOperationsError("Review submission is disabled: trusted qualification attestation is unavailable")
    try:
        attestation = get_attestation(reviewer.issuer, reviewer.subject_id, review_type)
        valid = isinstance(attestation, Mapping) and verify_attestation(
            reviewer.issuer, reviewer.subject_id, review_type, attestation
        )
    except Exception:
        raise ReviewOperationsError("Review submission is disabled: qualification could not be verified") from None
    if (not valid or attestation.get("status") != "VERIFIED"
            or attestation.get("review_type") != review_type
            or not isinstance(attestation.get("qualification_reference"), str)
            or not attestation["qualification_reference"].strip()):
        raise ReviewOperationsError("Reviewer lacks verified qualifications for this review type")
    return dict(attestation)


def _valid_attestation_shape(attestation: Any, review_type: str) -> bool:
    return (isinstance(attestation, Mapping) and attestation.get("status") == "VERIFIED"
            and attestation.get("review_type") == review_type
            and isinstance(attestation.get("qualification_reference"), str)
            and bool(attestation["qualification_reference"].strip()))


def _validate_roster_principal(reviewer: AuthenticatedReviewer) -> None:
    if (not reviewer.subject_id.strip() or not reviewer.issuer.strip() or not reviewer.display_name.strip()
            or not reviewer.key_id or not reviewer.key_id.strip() or not isinstance(reviewer.expires_at, str)):
        raise ReviewOperationsError("Reviewer roster entry lacks identity, signing key, or credential expiry")
    try:
        expiry = datetime.fromisoformat(reviewer.expires_at.replace("Z", "+00:00"))
    except ValueError:
        raise ReviewOperationsError("Reviewer roster credential expiry is invalid") from None
    if expiry.tzinfo is None or expiry <= datetime.now(timezone.utc):
        raise ReviewOperationsError("Reviewer roster credential is expired or has no timezone")


def _replay(path: Path, records: Mapping[str, Mapping[str, Any]], provider: QualifiedIdentityProvider | None) -> tuple[list[dict[str, Any]], dict[str, str], dict[str, dict[str, Any]]]:
    states = {record_id: "pending" for record_id in records}
    assigned: dict[str, dict[str, Any]] = {}
    events: list[dict[str, Any]] = []
    if not path.exists():
        return events, states, assigned
    if provider is None:
        raise ReviewOperationsError("Audit verification is unavailable: trusted identity provider is not configured")
    previous = ZERO_HASH
    raw = path.read_bytes()
    if raw and not raw.endswith(b"\n"):
        raise ReviewOperationsError("Review operations audit is truncated")
    for line_no, line in enumerate(raw.decode("utf-8").splitlines(), 1):
        try:
            event = json.loads(line, object_pairs_hook=_reject_duplicate_keys)
        except (json.JSONDecodeError, ReviewOperationsError) as exc:
            raise ReviewOperationsError(f"Malformed review operations event at line {line_no}: {exc}") from None
        if (not isinstance(event, dict) or isinstance(event.get("sequence"), bool)
                or not isinstance(event.get("sequence"), int) or event["sequence"] != line_no):
            raise ReviewOperationsError(f"Invalid review operations sequence at event {line_no}")
        if event.get("previous_event_sha256") != previous or event.get("event_sha256") != _hash_event(event):
            raise ReviewOperationsError(f"Invalid review operations hash chain at event {line_no}")
        signature = event.get("identity_signature")
        if event.get("actor_subject_id") is None or not isinstance(signature, str):
            raise ReviewOperationsError(f"Missing authenticated actor at event {line_no}")
        try:
            valid_signature = provider.verify_audit_event(event)
        except Exception:
            valid_signature = False
        if not valid_signature:
            raise ReviewOperationsError(f"Invalid identity signature at event {line_no}")
        record_id = event.get("review_id")
        if (not isinstance(record_id, str) or record_id not in records
                or event.get("review_type") != records[record_id].get("review_type")):
            raise ReviewOperationsError(f"Unlinked review record at event {line_no}")
        provenance = records[record_id].get("identity_and_evidence", {})
        if (event.get("readiness_register_version") not in {"1.1.0", "1.2.0"}
                or event.get("source_release_id") != provenance.get("release_id")
                or event.get("source_sha256") != provenance.get("source_sha256")
                or event.get("evidence_id") != provenance.get("evidence_id")):
            raise ReviewOperationsError(f"Review event provenance does not match its versioned record at event {line_no}")
        if (not isinstance(event.get("review_date"), str) or not event["review_date"].strip()
                or not isinstance(event.get("rationale"), str) or not event["rationale"].strip()):
            raise ReviewOperationsError(f"Review date or rationale is incomplete at event {line_no}")
        try:
            parsed_date = date.fromisoformat(event["review_date"])
        except ValueError:
            raise ReviewOperationsError(f"Review date is invalid at event {line_no}") from None
        if parsed_date.isoformat() != event["review_date"]:
            raise ReviewOperationsError(f"Review date must use YYYY-MM-DD at event {line_no}")
        old, new = states[record_id], event.get("new_status")
        if not isinstance(new, str) or new not in STATUSES or event.get("previous_status") != old:
            raise ReviewOperationsError(f"Invalid status transition at event {line_no}")
        action = event.get("action")
        target = event.get("assigned_reviewer")
        if action == "ASSIGN":
            if new != "assigned" or old not in {"pending", "needs_revision"} or not isinstance(target, dict):
                raise ReviewOperationsError(f"Invalid assignment event at event {line_no}")
            actor = provider.resolve_reviewer(event.get("actor_issuer"), event.get("actor_subject_id"))
            if (not isinstance(actor, AuthenticatedReviewer) or "expert" not in actor.roles
                    or not provider.authorize_assignment(actor, "assign", target_issuer=target.get("issuer"),
                                                         target_subject_id=target.get("subject_id"))):
                raise ReviewOperationsError(f"Assignment authorization cannot be verified at event {line_no}")
            target_principal = provider.resolve_reviewer(target.get("issuer"), target.get("subject_id"))
            if (not isinstance(target_principal, AuthenticatedReviewer) or "reviewer" not in target_principal.roles
                    or target_principal.display_name != target.get("display_name")):
                raise ReviewOperationsError(f"Assignment target cannot be verified at event {line_no}")
            _validate_roster_principal(target_principal)
            attestation = target.get("qualification")
            try:
                valid_qualification = (_valid_attestation_shape(attestation, event["review_type"])
                    and provider.verify_qualification_attestation(
                    target.get("issuer"), target.get("subject_id"), event["review_type"], attestation
                ))
            except Exception:
                valid_qualification = False
            if not valid_qualification:
                raise ReviewOperationsError(f"Unverifiable assignment qualification at event {line_no}")
            assigned[record_id] = target
        elif action == "STATUS":
            allowed = {"assigned": {"in_review"}, "in_review": {"approved", "rejected", "needs_revision"}}
            if new not in allowed.get(old, set()):
                raise ReviewOperationsError(f"Invalid status transition at event {line_no}")
            actor_key = (event.get("actor_issuer"), event.get("actor_subject_id"))
            assigned_key = (assigned.get(record_id, {}).get("issuer"), assigned.get(record_id, {}).get("subject_id"))
            if actor_key != assigned_key:
                raise ReviewOperationsError(f"Review event actor does not hold the assignment at event {line_no}")
            actor = provider.resolve_reviewer(event.get("actor_issuer"), event.get("actor_subject_id"))
            if not isinstance(actor, AuthenticatedReviewer) or actor.display_name != event.get("actor_name"):
                raise ReviewOperationsError(f"Review actor cannot be verified at event {line_no}")
            _validate_roster_principal(actor)
            if new in FINAL_STATUSES and "expert" not in actor.roles:
                raise ReviewOperationsError(f"Final decision actor is not an expert at event {line_no}")
            try:
                attestation = event.get("qualification")
                valid_qualification = (_valid_attestation_shape(attestation, event["review_type"])
                    and provider.verify_qualification_attestation(
                    event.get("actor_issuer"), event.get("actor_subject_id"), event["review_type"],
                    attestation,
                ))
            except Exception:
                valid_qualification = False
            if not valid_qualification:
                raise ReviewOperationsError(f"Unverifiable reviewer qualification at event {line_no}")
            refs = event.get("evidence_references")
            if not isinstance(refs, list) or not refs or any(not isinstance(ref, str) or not ref.strip() for ref in refs):
                raise ReviewOperationsError(f"Evidence references are incomplete at event {line_no}")
        else:
            raise ReviewOperationsError(f"Unsupported review action at event {line_no}")
        if new in FINAL_STATUSES and (not event.get("rationale") or not event.get("evidence_references")
                                      or not isinstance(event.get("signoff_reference"), str)
                                      or not event["signoff_reference"].strip()):
            raise ReviewOperationsError(f"Final decision evidence is incomplete at event {line_no}")
        states[record_id] = new
        events.append(event)
        previous = event["event_sha256"]
    return events, states, assigned


def _append(path: Path, event: dict[str, Any], provider: QualifiedIdentityProvider, actor: AuthenticatedReviewer) -> dict[str, Any]:
    signer = getattr(provider, "sign_audit_event", None)
    if not callable(signer):
        raise ReviewOperationsError("Review submission is disabled: trusted provider cannot sign actions")
    try:
        signature = signer(actor, _canonical(event))
    except Exception:
        raise ReviewOperationsError("Trusted provider failed to sign review operation") from None
    if not isinstance(signature, str) or not signature.strip():
        raise ReviewOperationsError("Trusted provider returned no review operation signature")
    event["identity_signature"] = signature
    event["event_sha256"] = _hash_event(event)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("ab") as stream:
        stream.write(_canonical(event) + b"\n")
        stream.flush()
        os.fsync(stream.fileno())
    return event


def _actor(provider: QualifiedIdentityProvider | None, credentials: Any) -> AuthenticatedReviewer:
    try:
        actor = authenticate_reviewer(provider, credentials)
    except ReviewerAuthenticationError as exc:
        raise ReviewOperationsError(str(exc)) from None
    if provider is None or not callable(getattr(provider, "verify_audit_event", None)):
        raise ReviewOperationsError("Review submission is disabled: trusted identity verification is unavailable")
    return actor


def assign_reviewer(path: str | Path, register: Mapping[str, Any], *, review_id: str,
                    target_issuer: str, target_subject_id: str, review_date: str,
                    rationale: str, identity_provider: QualifiedIdentityProvider | None,
                    credentials: Any) -> dict[str, Any]:
    records = _register_map(register)
    if review_id not in records:
        raise ReviewOperationsError("Unknown review ID")
    actor = _actor(identity_provider, credentials)
    provider = identity_provider
    assert provider is not None
    if "expert" not in actor.roles:
        raise ReviewOperationsError("Only an authorized review coordinator/expert may assign reviews")
    target = provider.resolve_reviewer(target_issuer, target_subject_id)
    if not isinstance(target, AuthenticatedReviewer) or "reviewer" not in target.roles:
        raise ReviewOperationsError("Assignment target is not in the trusted reviewer roster")
    _validate_roster_principal(target)
    record_type = records[review_id]["review_type"]
    qualification = _qualification(provider, target, record_type)
    if not provider.authorize_assignment(actor, "assign", target_issuer=target.issuer, target_subject_id=target.subject_id):
        raise ReviewOperationsError("Identity provider denied reviewer assignment")
    log = _safe_log_path(path)
    events, states, _ = _replay(log, records, provider)
    old = states[review_id]
    if old not in {"pending", "needs_revision"}:
        raise ReviewOperationsError(f"Cannot assign record currently in {old} state")
    try:
        parsed = date.fromisoformat(review_date)
    except (TypeError, ValueError):
        raise ReviewOperationsError("review_date must use YYYY-MM-DD") from None
    if parsed.isoformat() != review_date or not rationale.strip():
        raise ReviewOperationsError("Assignment requires a valid date and rationale")
    event = {
        "schema_version": "1.0.0", "sequence": len(events) + 1, "action": "ASSIGN",
        "review_id": review_id, "review_type": record_type, "previous_status": old,
        "readiness_register_version": register.get("register_version"),
        "evidence_id": records[review_id].get("identity_and_evidence", {}).get("evidence_id"),
        "source_release_id": records[review_id].get("identity_and_evidence", {}).get("release_id"),
        "source_sha256": records[review_id].get("identity_and_evidence", {}).get("source_sha256"),
        "new_status": "assigned", "assigned_reviewer": {"issuer": target.issuer, "subject_id": target.subject_id,
        "display_name": target.display_name, "qualification": qualification},
        "actor_issuer": actor.issuer, "actor_subject_id": actor.subject_id,
        "actor_name": actor.display_name, "actor_role": sorted(actor.roles),
        "review_date": review_date, "rationale": rationale,
        "evidence_references": [], "signoff_reference": None,
        "previous_event_sha256": events[-1]["event_sha256"] if events else ZERO_HASH,
    }
    return _append(log, event, provider, actor)


def submit_review_status(path: str | Path, register: Mapping[str, Any], *, review_id: str,
                         new_status: str, review_date: str, rationale: str,
                         evidence_references: Sequence[str] = (), signoff_reference: str | None = None,
                         identity_provider: QualifiedIdentityProvider | None,
                         credentials: Any) -> dict[str, Any]:
    if new_status not in {"in_review", "approved", "rejected", "needs_revision"}:
        raise ReviewOperationsError("Unsupported review status submission")
    records = _register_map(register)
    if review_id not in records:
        raise ReviewOperationsError("Unknown review ID")
    actor = _actor(identity_provider, credentials)
    provider = identity_provider
    assert provider is not None
    record_type = records[review_id]["review_type"]
    qualification = _qualification(provider, actor, record_type)
    log = _safe_log_path(path)
    events, states, assigned = _replay(log, records, provider)
    old = states[review_id]
    allowed = {"assigned": {"in_review"}, "in_review": {"approved", "rejected", "needs_revision"}}
    if new_status not in allowed.get(old, set()):
        raise ReviewOperationsError(f"Invalid status transition: {old} -> {new_status}")
    target = assigned.get(review_id, {})
    if (target.get("issuer"), target.get("subject_id")) != (actor.issuer, actor.subject_id):
        raise ReviewOperationsError("Only the assigned reviewer may submit this review status")
    if new_status in FINAL_STATUSES and "expert" not in actor.roles:
        raise ReviewOperationsError("Final decisions require an authorized expert reviewer")
    if not isinstance(rationale, str) or not rationale.strip():
        raise ReviewOperationsError("Review status requires a nonempty rationale")
    if new_status in FINAL_STATUSES and (not evidence_references or not isinstance(signoff_reference, str)
                                         or not signoff_reference.strip()):
        raise ReviewOperationsError("Final decision requires evidence references and sign-off reference")
    try:
        parsed = date.fromisoformat(review_date)
    except (TypeError, ValueError):
        raise ReviewOperationsError("review_date must use YYYY-MM-DD") from None
    if parsed.isoformat() != review_date:
        raise ReviewOperationsError("review_date must use YYYY-MM-DD")
    refs = [ref.strip() for ref in evidence_references if isinstance(ref, str) and ref.strip()]
    if not refs:
        raise ReviewOperationsError("Review status requires at least one nonempty evidence reference")
    event = {
        "schema_version": "1.0.0", "sequence": len(events) + 1, "action": "STATUS",
        "review_id": review_id, "review_type": record_type, "previous_status": old,
        "readiness_register_version": register.get("register_version"),
        "evidence_id": records[review_id].get("identity_and_evidence", {}).get("evidence_id"),
        "source_release_id": records[review_id].get("identity_and_evidence", {}).get("release_id"),
        "source_sha256": records[review_id].get("identity_and_evidence", {}).get("source_sha256"),
        "new_status": new_status, "assigned_reviewer": target,
        "actor_issuer": actor.issuer, "actor_subject_id": actor.subject_id,
        "actor_name": actor.display_name, "actor_role": sorted(actor.roles),
        "qualification": qualification, "review_date": review_date,
        "rationale": rationale, "evidence_references": refs,
        "signoff_reference": signoff_reference,
        "previous_event_sha256": events[-1]["event_sha256"] if events else ZERO_HASH,
    }
    return _append(log, event, provider, actor)


def review_progress(register: Mapping[str, Any], events: Sequence[Mapping[str, Any]] = ()) -> dict[str, Any]:
    records = _register_map(register)
    states = {record_id: "pending" for record_id in records}
    for event in events:
        record_id = event.get("review_id")
        if record_id not in states or event.get("previous_status") != states[record_id] or event.get("new_status") not in STATUSES:
            raise ReviewOperationsError("Progress input contains an invalid or unlinked event")
        states[record_id] = event["new_status"]
    counts = Counter(states.values())
    by_type = {}
    for kind in ("evidence", "mechanism"):
        ids = [record_id for record_id, row in records.items() if row["review_type"] == kind]
        by_type[kind] = {status: sum(states[record_id] == status for record_id in ids) for status in sorted(STATUSES)}
    return {
        "schema_version": "1.0.0", "source_register_version": register.get("register_version"),
        "indexed_records": len(records), "event_count": len(events),
        "status_counts": {status: counts.get(status, 0) for status in sorted(STATUSES)},
        "by_review_type": by_type,
        "decisions_created": sum(counts[s] for s in FINAL_STATUSES),
        "review_coverage": (sum(counts[s] for s in FINAL_STATUSES) / len(records)) if records else 0.0,
    }


def read_verified_review_operations(path: str | Path, register: Mapping[str, Any],
                                    identity_provider: QualifiedIdentityProvider | None) -> list[dict[str, Any]]:
    """Return only events that pass identity, qualification, provenance, and hash-chain checks."""
    records = _register_map(register)
    log = _safe_log_path(path)
    events, _, _ = _replay(log, records, identity_provider)
    return events


def reviewer_worklist(register: Mapping[str, Any], events: Sequence[Mapping[str, Any]], *, issuer: str, subject_id: str) -> dict[str, Any]:
    records = _register_map(register)
    states = {record_id: "pending" for record_id in records}
    owners: dict[str, dict[str, Any]] = {}
    for event in events:
        record_id = event["review_id"]
        states[record_id] = event["new_status"]
        if event["action"] == "ASSIGN":
            owners[record_id] = event["assigned_reviewer"]
    assigned_rows = []
    for record_id, owner in owners.items():
        if (owner.get("issuer"), owner.get("subject_id")) != (issuer, subject_id):
            continue
        if states[record_id] in {"assigned", "in_review", "needs_revision"}:
            row = records[record_id]
            assigned_rows.append({"review_id": record_id, "review_type": row["review_type"],
                                  "status": states[record_id], "identity_and_evidence": row["identity_and_evidence"],
                                  "reviewer_requirement": row["reviewer_requirement"],
                                  "unresolved_questions": row["unresolved_questions"]})
    return {"schema_version": "1.0.0", "reviewer": {"issuer": issuer, "subject_id": subject_id},
            "record_count": len(assigned_rows), "records": sorted(assigned_rows, key=lambda row: row["review_id"])}
