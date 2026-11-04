"""Read-only adapters for the pinned Phase1B-v1.3.2 and Phase2-v0.3.1 releases."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

from .exceptions import SourceIntegrityError
from .food_composition import load_food_data
from .compound_mapping import load_mappings
from .provenance import project_root

PHASE1B_RELEASE = "Phase1B-v1.3.2"
PHASE1B_MANIFEST_SHA256 = "df3a95ae0957b68a89e38098c0824877196aa74ef7dd92573e6ab1f37e39b9b5"
PHASE2_RELEASE = "Phase2-v0.3.1"
PHASE2_MANIFEST_SHA256 = "2b72e4df095002952fcf2eef2af3381425384317d6ea259b81676ed8c243746e"
PHASE4_RELEASE = "Phase4-v0.1.2"
PHASE4_MANIFEST_SHA256 = "9d6a3a13d6567a872bfb890cf02ea118648a8572c92ebdd8e33b970d0f889fba"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _safe_package_file(root: Path, relative: str) -> Path:
    candidate = root / relative
    try:
        candidate.resolve().relative_to(root.resolve())
    except ValueError:
        raise SourceIntegrityError(f"Unsafe package path in release manifest: {relative}") from None
    if candidate.is_symlink():
        raise SourceIntegrityError(f"Symlinks are not permitted in pinned release packages: {relative}")
    return candidate


def _verify_phase1b(root: Path) -> dict[str, Any]:
    manifest_path = root / "CHECKSUMS.json"
    digest_path = root / "CHECKSUMS.sha256"
    if not manifest_path.is_file() or not digest_path.is_file():
        raise SourceIntegrityError("Phase1B-v1.3.2 checksum files are missing")
    manifest_hash = _sha256(manifest_path)
    expected = digest_path.read_text(encoding="utf-8").split()[0]
    if manifest_hash != expected or manifest_hash != PHASE1B_MANIFEST_SHA256:
        raise SourceIntegrityError("Phase1B-v1.3.2 manifest digest does not match its pinned release hash")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("release_id") != PHASE1B_RELEASE:
        raise SourceIntegrityError("Unexpected Phase1B package identity")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != manifest.get("artifact_count"):
        raise SourceIntegrityError("Phase1B package artifact list is inconsistent")
    for item in artifacts:
        path = _safe_package_file(root, str(item.get("path", "")))
        if not path.is_file() or _sha256(path) != item.get("sha256") or path.stat().st_size != item.get("bytes"):
            raise SourceIntegrityError(f"Phase1B package artifact failed checksum/size verification: {item.get('path', '')}")
    return {"release_id": PHASE1B_RELEASE, "manifest_sha256": manifest_hash,
            "artifact_count": len(artifacts)}


def _verify_phase2(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest_path = root / "RELEASE_MANIFEST.json"
    digest_path = root / "RELEASE_MANIFEST.sha256"
    release_path = root / "RELEASE.json"
    if not manifest_path.is_file() or not digest_path.is_file() or not release_path.is_file():
        raise SourceIntegrityError("Phase2-v0.3.1 release metadata or checksum files are missing")
    manifest_hash = _sha256(manifest_path)
    expected = digest_path.read_text(encoding="utf-8").split()[0]
    if manifest_hash != expected or manifest_hash != PHASE2_MANIFEST_SHA256:
        raise SourceIntegrityError("Phase2-v0.3.1 manifest digest does not match its pinned release hash")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    metadata = json.loads(release_path.read_text(encoding="utf-8"))
    files = manifest.get("file_hashes", {})
    if manifest.get("release") != PHASE2_RELEASE or len(files) != manifest.get("artifact_count"):
        raise SourceIntegrityError("Phase2 package identity or artifact count is inconsistent")
    for relative, expected_hash in files.items():
        path = _safe_package_file(root, relative)
        if not path.is_file() or _sha256(path) != expected_hash:
            raise SourceIntegrityError(f"Phase2 package artifact failed checksum verification: {relative}")
    if metadata.get("release_id") != PHASE2_RELEASE or metadata.get("status") != "COMPLETE_WITH_DOCUMENTED_LIMITATIONS":
        raise SourceIntegrityError("Phase2 release status is not the expected reviewed version")
    return ({"release_id": PHASE2_RELEASE, "manifest_sha256": manifest_hash,
             "artifact_count": len(files), "status": metadata["status"]}, metadata)


def load_phase1b_v131_inputs() -> tuple[dict[str, dict[str, str]], list[dict[str, str]], dict[str, dict[str, str]], dict[str, Any]]:
    """Load verified quantitative food inputs and compound identities from Phase1B-v1.3.2."""
    root = project_root() / "stageC" / "releases" / PHASE1B_RELEASE
    release = _verify_phase1b(root)
    package_stage = root / "stageC"
    foods = load_food_data(package_stage / "data" / "food_composition" / "food_composition.csv")
    mappings = load_mappings(package_stage / "data" / "compound_food_mapping" / "compound_food_mapping.csv")
    snapshot = package_stage / "data" / "stage_b_snapshot_v20_20261103"
    snapshot_manifest = json.loads((snapshot / "import_manifest.json").read_text(encoding="utf-8"))
    if snapshot_manifest.get("source_manifest_sha256") != "db630b3134126df723494c7ebb58db64e1c61099660b0c6391a4602c3e7deec2":
        raise SourceIntegrityError("Phase1B Stage B snapshot does not match the pinned V20 source hash")
    with (snapshot / "compound_registry.csv").open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    compounds: dict[str, dict[str, str]] = {}
    for row in rows:
        status = row.get("Identity_Status", "")
        compounds[row["Compound_ID"]] = {
            **row,
            "StageC_Identity_Verification_Status": "Pending review" if status.startswith("Identity pending") else "Complete",
        }
    if len(compounds) != 143 or len(foods) != 584 or len(mappings) != 584:
        raise SourceIntegrityError("Pinned Phase1B package counts do not match the reviewed release")
    release["stage_b_release"] = snapshot_manifest["source_release_id"]
    release["stage_b_manifest_sha256"] = snapshot_manifest["source_manifest_sha256"]
    release["food_records"] = len(foods)
    release["mapping_records"] = len(mappings)
    release["compounds"] = len(compounds)
    release["identity_pending"] = sum(row["StageC_Identity_Verification_Status"] != "Complete" for row in compounds.values())
    return ({row["food_record_id"]: row for row in foods}, mappings, compounds, release)


def load_phase2_v030_evidence() -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    """Load only fully gated estimates from the immutable Phase2 package.

    Current v0.3.0 contains zero cooked concentration estimates. Future records
    must carry all four compatibility gates in structured source provenance;
    incomplete records remain excluded and counted as blocked.
    """
    root = project_root() / "stageC" / "releases" / PHASE2_RELEASE
    release, metadata = _verify_phase2(root)
    csv_path = root / "data" / "cooked_concentration_estimates.csv"
    with csv_path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    gates = ("exact_compound_match", "food_matrix_match", "cooking_condition_match", "measurement_basis_compatible")
    evidence: dict[str, dict[str, Any]] = {}
    blocked: list[str] = []
    for row in rows:
        record_id = row.get("output_record_id", "")
        try:
            provenance = json.loads(row.get("source_provenance", ""))
        except (json.JSONDecodeError, TypeError):
            provenance = {}
        compatible = all(provenance.get("compatibility_gates", {}).get(gate) is True for gate in gates)
        identity_ok = str(row.get("identity_confidence", "")).casefold() in {"strict", "strict_match", "strict identity match"}
        valid = str(row.get("validation_status", "")).casefold() in {"pass", "validated", "complete"}
        try:
            low, high = row.get("retention_low", ""), row.get("retention_high", "")
            if not low or not high:
                raise ValueError("retention bounds missing")
            if not compatible or not identity_ok or not valid or not record_id or not row.get("retention_source"):
                raise ValueError("identity, source, validation, or compatibility gates not explicit and accepted")
            evidence[f"{row['food_record_id']}|{row['compound_id']}"] = {
                "retention_low_percent": low, "retention_high_percent": high,
                "evidence_id": record_id,
                "source_reference": f"{row['retention_source']}; {provenance.get('source_reference', '')}".strip("; "),
                **{gate: True for gate in gates},
            }
        except (KeyError, ValueError) as exc:
            blocked.append(f"{record_id or '<missing evidence id>'}: {exc}")
    release.update({"numeric_records": len(rows), "accepted_cooking_evidence": len(evidence),
                    "blocked_records": len(blocked), "blocked_reasons": blocked,
                    "source_phase1b_release": metadata.get("source_phase1b_release"),
                    "source_phase1b_manifest_sha256": metadata.get("source_phase1b_manifest_sha256")})
    return evidence, release


def load_phase4_context_evidence() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Verify and query the Phase 4 package through its read-only context selector."""
    root = project_root() / "stageC" / "phase4" / "releases" / PHASE4_RELEASE
    manifest_path = root / "release_manifest.json"
    digest_path = root / "release_manifest.sha256"
    if not manifest_path.is_file() or not digest_path.is_file():
        raise SourceIntegrityError("Pinned Phase 4 package manifest is missing")
    manifest_hash = _sha256(manifest_path)
    expected = digest_path.read_text(encoding="ascii").split()[0]
    if manifest_hash != expected or manifest_hash != PHASE4_MANIFEST_SHA256:
        raise SourceIntegrityError("Phase 4 manifest digest does not match its pinned release hash")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("release_id") != PHASE4_RELEASE or manifest.get("status") != "IN_PROGRESS":
        raise SourceIntegrityError("Unexpected Phase 4 release identity or status")
    artifacts = manifest.get("files", [])
    if len(artifacts) != manifest.get("artifact_count"):
        raise SourceIntegrityError("Phase 4 package artifact count is inconsistent")
    for entry in artifacts:
        path = _safe_package_file(root, str(entry.get("path", "")))
        if not path.is_file() or path.stat().st_size != entry.get("bytes") or _sha256(path) != entry.get("sha256"):
            raise SourceIntegrityError(f"Phase 4 artifact failed checksum/size verification: {entry.get('path', '')}")
    sources = json.loads((root / "data" / "source_registry.json").read_text(encoding="utf-8"))
    evidence = json.loads((root / "data" / "evidence_registry.json").read_text(encoding="utf-8"))
    module_path = root / "src" / "phase4_registry.py"
    spec = importlib.util.spec_from_file_location("cookrisk_phase4_v011_registry", module_path)
    if spec is None or spec.loader is None:
        raise SourceIntegrityError("Cannot load Phase 4 read-only selector")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    validation_errors = module.validate_registry(sources, evidence)
    if validation_errors:
        raise SourceIntegrityError("Phase 4 registry validation failed: " + "; ".join(validation_errors))
    selected = [dict(row) for row in module.phase3_context_records(evidence)]
    metadata = {
        "release_id": PHASE4_RELEASE,
        "manifest_sha256": manifest_hash,
        "manifest_verified": True,
        "status": manifest["status"],
        "source_count": len(sources),
        "evidence_record_count": len(evidence),
        "selected_context_record_count": len(selected),
        "selector_contract": "read-only accepted contextual records only; quantitative PK is not exposed to Phase 3 calculations",
    }
    return selected, metadata
