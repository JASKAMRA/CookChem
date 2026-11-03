"""Read-only integration with the checksum-verified StageB_FINALIZED release."""
from __future__ import annotations

import csv
import json
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
from typing import Any

from .exceptions import SourceIntegrityError
from .provenance import project_root, sha256_file, utc_timestamp

RELEASE_ID = "StageB_V20_20261103"
EXPECTED_COMPOUND_COUNT = 143
MANIFEST_RELATIVE_PATH = "manifests/SHA256SUMS.json"
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


def _authoritative_root(release: Path | None = None) -> Path:
    expected = default_release_path().resolve()
    if release is not None and release.resolve() != expected:
        raise SourceIntegrityError(
            f"Only the authoritative Stage B release is supported: {expected}"
        )
    return expected


def _no_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SourceIntegrityError(f"Duplicate key in Stage B manifest: {key}")
        result[key] = value
    return result


def _safe_manifest_path(value: Any) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise SourceIntegrityError(f"Invalid Stage B manifest path: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise SourceIntegrityError(f"Unsafe Stage B manifest path: {value!r}")
    if value != path.as_posix() or value == MANIFEST_RELATIVE_PATH:
        raise SourceIntegrityError(f"Non-portable Stage B manifest path: {value!r}")
    return value


def read_csv(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
                raise SourceIntegrityError(f"Missing or duplicate CSV headers: {path}")
            rows = list(reader)
    except (OSError, UnicodeError, csv.Error) as exc:
        raise SourceIntegrityError(f"Cannot read Stage B CSV {path}: {exc}") from exc
    if any(None in row for row in rows):
        raise SourceIntegrityError(f"Malformed Stage B CSV row has extra columns: {path}")
    return rows


def validate_registry_tables(records: dict[str, list[dict[str, str]]]) -> dict[str, Any]:
    """Validate the authoritative registry and identity audit without editing either."""
    registry = records.get("compound_registry.csv")
    identity = records.get("identity_structure_audit.csv")
    if registry is None or identity is None:
        raise SourceIntegrityError("Stage B registry and identity audit are required")
    if len(registry) != EXPECTED_COMPOUND_COUNT:
        raise SourceIntegrityError(
            f"Expected {EXPECTED_COMPOUND_COUNT} Stage B compounds; found {len(registry)}"
        )
    ids = [row.get("Compound_ID", "").strip() for row in registry]
    if any(not compound_id for compound_id in ids):
        raise SourceIntegrityError("Stage B compound registry contains a blank Compound_ID")
    duplicate_ids = sorted(key for key, count in Counter(ids).items() if count > 1)
    if duplicate_ids:
        raise SourceIntegrityError(f"Duplicate Stage B Compound_ID values: {duplicate_ids[:8]}")
    for row in registry:
        if not row.get("Canonical_Name", "").strip():
            raise SourceIntegrityError(f"Missing canonical name for {row['Compound_ID']}")

    identity_ids = [row.get("Compound_ID", "").strip() for row in identity]
    if any(not compound_id for compound_id in identity_ids):
        raise SourceIntegrityError("Stage B identity audit contains a blank Compound_ID")
    duplicate_identity_ids = sorted(
        key for key, count in Counter(identity_ids).items() if count > 1
    )
    if duplicate_identity_ids:
        raise SourceIntegrityError(
            f"Duplicate identity-audit Compound_ID values: {duplicate_identity_ids[:8]}"
        )
    if set(identity_ids) != set(ids):
        missing = sorted(set(ids) - set(identity_ids))
        extra = sorted(set(identity_ids) - set(ids))
        raise SourceIntegrityError(
            f"Registry/identity audit IDs differ; missing={missing[:8]}, extra={extra[:8]}"
        )

    registry_by_id = {row["Compound_ID"].strip(): row for row in registry}
    identity_by_id = {row["Compound_ID"].strip(): row for row in identity}
    aligned_fields = (
        ("Canonical_Name", "Canonical_Name"),
        ("PubChem_CID", "PubChem_CID"),
        ("SMILES", "SMILES"),
        ("InChI", "InChI"),
        ("InChIKey", "Registry_InChIKey"),
    )
    for compound_id in ids:
        compound = registry_by_id[compound_id]
        audit = identity_by_id[compound_id]
        for registry_field, audit_field in aligned_fields:
            if compound.get(registry_field, "").strip() != audit.get(audit_field, "").strip():
                raise SourceIntegrityError(
                    f"Registry and identity-audit {registry_field} disagree for {compound_id}"
                )

    for field in ("PubChem_CID", "InChIKey"):
        groups: dict[str, list[str]] = defaultdict(list)
        for row in registry:
            value = row.get(field, "").strip().casefold()
            if value:
                groups[value].append(row["Compound_ID"])
        duplicates = {value: ids for value, ids in groups.items() if len(ids) > 1}
        if duplicates:
            raise SourceIntegrityError(f"Duplicate Stage B {field} identifiers: {duplicates}")

    identity_status_counts = Counter(row.get("Status", "").strip() for row in identity)
    if any(not status for status in identity_status_counts):
        raise SourceIntegrityError("Stage B identity audit contains a blank status")

    # Unstereospecified SMILES can repeat for stereoisomers. Preserve these source
    # values; an exact InChIKey remains the identity check, and review stays open.
    smiles_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in registry:
        value = row.get("SMILES", "").strip()
        if value:
            smiles_groups[value].append(row)
    repeated_smiles = []
    for smiles, rows in smiles_groups.items():
        keys = {row.get("InChIKey", "").strip() for row in rows}
        if len(rows) > 1 and len(keys) > 1:
            repeated_smiles.append(
                {"compound_ids": sorted(row["Compound_ID"] for row in rows),
                 "canonical_names": sorted(row["Canonical_Name"] for row in rows)}
            )

    return {
        "compound_count": len(registry),
        "identity_record_count": len(identity),
        "identity_status_counts": dict(sorted(identity_status_counts.items())),
        "repeated_nonstereospecific_smiles_review_groups": repeated_smiles,
    }


def verify_release(release: Path | None = None) -> dict[str, Any]:
    root = _authoritative_root(release)
    manifest_path = root / MANIFEST_RELATIVE_PATH
    if not manifest_path.is_file():
        raise SourceIntegrityError(f"Stage B checksum manifest is missing: {manifest_path}")
    try:
        manifest = json.loads(
            manifest_path.read_text(encoding="utf-8-sig"),
            object_pairs_hook=_no_duplicate_json_keys,
        )
    except SourceIntegrityError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SourceIntegrityError(f"Cannot read Stage B checksum manifest: {exc}") from exc
    if not isinstance(manifest, dict) or not manifest:
        raise SourceIntegrityError("Stage B checksum manifest must be a non-empty JSON object")

    normalized: dict[str, str] = {}
    for relative, expected in manifest.items():
        relative = _safe_manifest_path(relative)
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise SourceIntegrityError(f"Invalid SHA-256 value for Stage B artifact {relative}")
        normalized[relative] = expected
    missing = []
    unexpected = []
    actual_paths: set[str] = set()
    for path in root.rglob("*"):
        if path.is_symlink():
            raise SourceIntegrityError(f"Symlinks are not allowed in Stage B release: {path}")
        if path.is_file():
            relative = path.relative_to(root).as_posix()
            if relative != MANIFEST_RELATIVE_PATH:
                actual_paths.add(relative)
    missing = sorted(set(normalized) - actual_paths)
    unexpected = sorted(actual_paths - set(normalized))
    mismatches = []
    for relative in sorted(set(normalized) & actual_paths):
        if sha256_file(root / PurePosixPath(relative)) != normalized[relative]:
            mismatches.append(relative)
    if missing or unexpected or mismatches:
        details = []
        if missing:
            details.append(f"missing={missing[:8]}")
        if unexpected:
            details.append(f"unexpected={unexpected[:8]}")
        if mismatches:
            details.append(f"hash_mismatch={mismatches[:8]}")
        raise SourceIntegrityError("Stage B exact manifest verification failed: " + "; ".join(details))

    metadata_path = root / "release_metadata.json"
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SourceIntegrityError(f"Cannot read Stage B release metadata: {exc}") from exc
    if metadata.get("release") != RELEASE_ID:
        raise SourceIntegrityError(
            f"Unexpected Stage B release identity: {metadata.get('release')!r}; expected {RELEASE_ID}"
        )
    for relative in SOURCE_FILES.values():
        if relative not in normalized:
            raise SourceIntegrityError(f"Required Stage B source file is not manifested: {relative}")

    records = {
        name: read_csv(root / relative)
        for name, relative in SOURCE_FILES.items()
    }
    registry_audit = validate_registry_tables(records)
    return {
        "release_id": RELEASE_ID,
        "path": str(root),
        "manifest_entries": len(normalized),
        "manifest_sha256": sha256_file(manifest_path),
        **registry_audit,
    }


def load_stage_b(release: Path | None = None) -> dict[str, Any]:
    root = _authoritative_root(release)
    release_info = verify_release(root)
    records = {name: read_csv(root / relative) for name, relative in SOURCE_FILES.items()}
    validate_registry_tables(records)
    identity = {
        row.get("Compound_ID", ""): row.get("Status", "")
        for row in records["identity_structure_audit.csv"]
    }
    compound_by_key: dict[str, str] = {}
    for compound in records["compound_registry.csv"]:
        compound_id = compound.get("Compound_ID", "")
        compound_by_key[compound_id] = compound_id
        compound_by_key[compound.get("Canonical_Name", "")] = compound_id
    warnings_by_compound: dict[str, list[str]] = defaultdict(list)
    for warning in records["warning_ledger.csv"]:
        affected = {
            part.strip()
            for part in warning.get("Affected", "").split("|")
            if part.strip()
        }
        for value in affected:
            compound_id = compound_by_key.get(value)
            if compound_id:
                warning_id = warning.get("Warning_ID", "")
                if warning_id:
                    warnings_by_compound[compound_id].append(warning_id)
    for compound in records["compound_registry.csv"]:
        compound_id = compound.get("Compound_ID", "")
        compound["StageC_Identity_Verification_Status"] = identity.get(compound_id, "")
        compound["StageC_Warning_Identifiers"] = sorted(set(warnings_by_compound[compound_id]))
    return {"release": release_info, "source_files": records}


def create_snapshot(destination: Path, release: Path | None = None) -> dict[str, Any]:
    """Copy a small, explicit allowlist of Stage B files; source is never written."""
    root = _authoritative_root(release)
    release_info = verify_release(root)
    destination.mkdir(parents=True, exist_ok=True)
    old_manifest = destination / "import_manifest.json"
    if old_manifest.exists():
        changes = detect_source_changes(destination, root)
        if changes:
            raise SourceIntegrityError(
                "Existing Stage B snapshot differs from its source; create a new versioned snapshot instead of overwriting it"
            )
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
        "compound_count": EXPECTED_COMPOUND_COUNT,
        "imported_at_utc": utc_timestamp(),
        "files": files,
        "interaction_evidence_is_not_food_composition": True,
    }
    (destination / "import_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return manifest


def _csv_header(path: Path) -> list[str]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return next(csv.reader(stream), [])


def detect_source_changes(snapshot: Path, release: Path | None = None) -> list[dict[str, str]]:
    """Report changed/missing source or snapshot files relative to the import manifest."""
    source_root = _authoritative_root(release)
    manifest_path = snapshot / "import_manifest.json"
    if not manifest_path.is_file():
        return [{"file": "import_manifest.json", "side": "snapshot", "expected": "present", "observed": "MISSING"}]
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [{"file": "import_manifest.json", "side": "snapshot", "expected": "valid JSON", "observed": str(exc)}]
    changes: list[dict[str, str]] = []
    if manifest.get("source_release_id") != RELEASE_ID:
        changes.append({"file": "import_manifest.json", "side": "source_release_id", "expected": RELEASE_ID, "observed": str(manifest.get("source_release_id", "MISSING"))})
    expected_release_path = f"stageB/release/{RELEASE_ID}"
    if manifest.get("source_release_path") != expected_release_path:
        changes.append({"file": "import_manifest.json", "side": "source_release_path", "expected": expected_release_path, "observed": str(manifest.get("source_release_path", "MISSING"))})
    if manifest.get("compound_count") != EXPECTED_COMPOUND_COUNT:
        changes.append({"file": "import_manifest.json", "side": "compound_count", "expected": str(EXPECTED_COMPOUND_COUNT), "observed": str(manifest.get("compound_count", "MISSING"))})
    release_manifest = source_root / MANIFEST_RELATIVE_PATH
    observed_manifest = sha256_file(release_manifest) if release_manifest.is_file() else "MISSING"
    if observed_manifest != manifest.get("source_manifest_sha256"):
        changes.append({"file": MANIFEST_RELATIVE_PATH, "side": "source_manifest", "expected": str(manifest.get("source_manifest_sha256", "")), "observed": observed_manifest})
    entries = manifest.get("files")
    if not isinstance(entries, list):
        return changes + [{"file": "import_manifest.json", "side": "files", "expected": "list", "observed": type(entries).__name__}]
    expected_names = set(SOURCE_FILES)
    observed_names = {entry.get("snapshot_file") for entry in entries if isinstance(entry, dict)}
    if observed_names != expected_names or len(entries) != len(expected_names):
        changes.append({"file": "import_manifest.json", "side": "allowlist", "expected": "|".join(sorted(expected_names)), "observed": "|".join(sorted(str(name) for name in observed_names))})
    for entry in entries:
        if not isinstance(entry, dict):
            changes.append({"file": "import_manifest.json", "side": "entry", "expected": "object", "observed": type(entry).__name__})
            continue
        name = entry.get("snapshot_file", "")
        expected_source = SOURCE_FILES.get(name)
        if not expected_source or entry.get("source_file") != expected_source:
            changes.append({"file": str(name), "side": "allowlist", "expected": str(expected_source or "not allowed"), "observed": str(entry.get("source_file", "MISSING"))})
            continue
        source = source_root / expected_source
        copied = snapshot / name
        expected_source_path = f"{expected_release_path}/{expected_source}"
        if entry.get("source_path") != expected_source_path:
            changes.append({"file": str(name), "side": "source_path", "expected": expected_source_path, "observed": str(entry.get("source_path", "MISSING"))})
        if entry.get("import_status") != "IMPORTED_READ_ONLY":
            changes.append({"file": str(name), "side": "import_status", "expected": "IMPORTED_READ_ONLY", "observed": str(entry.get("import_status", "MISSING"))})
        for label, path, expected in (
            ("source", source, entry.get("sha256", "")),
            ("snapshot", copied, entry.get("snapshot_sha256", "")),
        ):
            observed = sha256_file(path) if path.is_file() else "MISSING"
            if observed != expected:
                changes.append({"file": name, "side": label, "expected": str(expected), "observed": observed})
        if copied.is_file():
            try:
                copied_rows = read_csv(copied)
                observed_schema = _csv_header(copied)
                if entry.get("record_count") != len(copied_rows):
                    changes.append({"file": str(name), "side": "record_count", "expected": str(len(copied_rows)), "observed": str(entry.get("record_count", "MISSING"))})
                if entry.get("schema") != observed_schema:
                    changes.append({"file": str(name), "side": "schema", "expected": "|".join(observed_schema), "observed": "|".join(str(value) for value in entry.get("schema", []))})
            except (OSError, SourceIntegrityError) as exc:
                changes.append({"file": str(name), "side": "parse", "expected": "valid CSV", "observed": str(exc)})
    return changes

