"""Read-only integration with the checksum-verified StageB_Final package."""
from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path
from typing import Any

from .exceptions import SourceIntegrityError
from .provenance import project_root, sha256_file, utc_timestamp

RELEASE_ID = "StageB_Final"
SOURCE_FILES = {
    "compound_registry.csv": "data/compound_registry.csv",
    "identity_structure_audit.csv": "identity/identity_structure_audit.csv",
    "food_context_audit.csv": "provenance/food_context_audit.csv",
    "publication_bibliography.csv": "data/publication_bibliography.csv",
    "interaction_evidence.csv": "data/interaction_evidence.csv",
    "warning_ledger.csv": "data/warning_ledger.csv",
    "source_audit.csv": "provenance/source_audit.csv",
    "claim_support_and_verification.csv": "provenance/claim_support_and_verification.csv",
    "source_register.csv": "provenance/source_register.csv",
}


def default_release_path() -> Path:
    return project_root() / "stageB" / "release" / RELEASE_ID


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def verify_release(release: Path | None = None) -> dict[str, Any]:
    root = (release or default_release_path()).resolve()
    manifest_path = root / "manifests" / "SHA256SUMS.json"
    if not manifest_path.is_file():
        raise SourceIntegrityError(f"Stage B checksum manifest is missing: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    mismatches = []
    for relative, expected in manifest.items():
        path = root / relative
        if not path.is_file() or sha256_file(path) != expected:
            mismatches.append(relative)
    if mismatches:
        raise SourceIntegrityError(f"Stage B release checksum mismatch: {', '.join(mismatches[:8])}")
    return {"release_id": RELEASE_ID, "path": str(root), "manifest_entries": len(manifest), "manifest_sha256": sha256_file(manifest_path)}


def load_stage_b(release: Path | None = None) -> dict[str, Any]:
    root = (release or default_release_path()).resolve()
    release_info = verify_release(root)
    records = {name: read_csv(root / relative) for name, relative in SOURCE_FILES.items()}
    identity = {row.get("Compound_ID", ""): row.get("Status", "") for row in records["identity_structure_audit.csv"]}
    # Attach the full inherited warning ledger to compounds by exact Compound_ID or
    # canonical name. Preserve original source columns and add derived fields only in memory.
    warnings_by_compound: dict[str, list[str]] = {}
    for warning in records["warning_ledger.csv"]:
        affected = {part.strip() for part in warning.get("Affected", "").split("|") if part.strip()}
        for compound in records["compound_registry.csv"]:
            compound_id = compound.get("Compound_ID", "")
            compound_name = compound.get("Canonical_Name", "")
            if compound_id in affected or compound_name in affected:
                warnings_by_compound.setdefault(compound_id, []).append(warning.get("Warning_ID", ""))
    # Derived in-memory fields; all original source columns and identifiers remain verbatim.
    for compound in records["compound_registry.csv"]:
        compound["StageC_Identity_Verification_Status"] = identity.get(compound.get("Compound_ID", ""), "")
        compound["StageC_Warning_Identifiers"] = sorted(x for x in warnings_by_compound.get(compound.get("Compound_ID", ""), []) if x)
    return {"release": release_info, "source_files": records}


def create_snapshot(destination: Path, release: Path | None = None) -> dict[str, Any]:
    """Copy a small, explicit allowlist of Stage B files; source is never written."""
    root = (release or default_release_path()).resolve()
    release_info = verify_release(root)
    destination.mkdir(parents=True, exist_ok=True)
    old_manifest = destination / "import_manifest.json"
    if old_manifest.exists():
        changes = detect_source_changes(destination, root)
        if changes:
            raise SourceIntegrityError("Existing Stage B snapshot differs from its source manifest; create a new versioned snapshot instead of overwriting it")
        return json.loads(old_manifest.read_text(encoding="utf-8"))
    files = []
    for target_name, relative in SOURCE_FILES.items():
        source = root / relative
        target = destination / target_name
        shutil.copy2(source, target)
        records = read_csv(target)
        files.append({
            "source_file": relative,
            "source_path": f"stageB/release/{RELEASE_ID}/{relative}",
            "snapshot_file": target_name,
            "sha256": sha256_file(source),
            "snapshot_sha256": sha256_file(target),
            "record_count": len(records),
            "schema": list(records[0]) if records else _csv_header(target),
            "import_status": "IMPORTED_READ_ONLY",
        })
    manifest = {
        "source_release_id": RELEASE_ID,
        "source_release_path": f"stageB/release/{RELEASE_ID}",
        "source_manifest_sha256": release_info["manifest_sha256"],
        "imported_at_utc": utc_timestamp(),
        "files": files,
        "interaction_evidence_is_not_food_composition": True,
    }
    (destination / "import_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def _csv_header(path: Path) -> list[str]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return next(csv.reader(stream), [])


def detect_source_changes(snapshot: Path, release: Path | None = None) -> list[dict[str, str]]:
    """Report changed/missing source or snapshot files relative to import manifest."""
    source_root = (release or default_release_path()).resolve()
    manifest = json.loads((snapshot / "import_manifest.json").read_text(encoding="utf-8"))
    changes = []
    release_manifest = source_root / "manifests" / "SHA256SUMS.json"
    observed_manifest = sha256_file(release_manifest) if release_manifest.is_file() else "MISSING"
    if observed_manifest != manifest.get("source_manifest_sha256"):
        changes.append({"file": "manifests/SHA256SUMS.json", "side": "source_manifest", "expected": manifest.get("source_manifest_sha256", ""), "observed": observed_manifest})
    for entry in manifest["files"]:
        source = source_root / entry["source_file"]
        copied = snapshot / entry["snapshot_file"]
        for label, path, expected in (
            ("source", source, entry["sha256"]),
            ("snapshot", copied, entry["snapshot_sha256"]),
        ):
            observed = sha256_file(path) if path.is_file() else "MISSING"
            if observed != expected:
                changes.append({"file": entry["snapshot_file"], "side": label, "expected": expected, "observed": observed})
    return changes
