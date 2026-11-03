"""Create a new immutable Phase 4 package and detached SHA-256 manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
INCLUDED = (
    "README.md",
    "PROPOSED_SCOPE.md",
    "requirements-dev.txt",
    "schemas",
    "data",
    "src",
    "tests",
    "reports",
    "scripts",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default="0.1.0", help="new version number; an existing package is never overwritten")
    args = parser.parse_args()
    release_id = f"Phase4-v{args.version}"
    release = HERE / "releases" / release_id
    if not release_id.replace("Phase4-v", "").replace(".", "").isdigit():
        raise SystemExit("version must contain only numeric dot-separated components")
    if release.exists():
        raise SystemExit(f"Refusing to overwrite existing versioned package: {release}")
    release.mkdir(parents=True)
    for relative in INCLUDED:
        source = HERE / relative
        destination = release / relative
        if source.is_dir():
            shutil.copytree(source, destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
    info = {
        "release_id": release_id,
        "status": "IN_PROGRESS",
        "created_on": "2026-11-03",
        "upstream_dependencies": [
            {"release_id": "Phase1B-v1.3.1", "manifest_sha256": "ad0d4a03e27022d8efade756c48ccd1d792d40608f9dd9674bc55190e1851da8", "usage": "version-scoped compound reference only; no identity adjudication is implied"},
            {"release_id": "Phase2-v0.3.0", "manifest_sha256": "2d1ca237cbf0f74233e48eddc0a0acea67b7797dffee33adc3ba723745842f65", "usage": "dependency boundary only; no Phase 2 records copied or reinterpreted"},
        ],
        "limitations": [
            "Phase 4 scope remains proposed pending project-owner approval.",
            "One primary human study and six condition-level/statistical records are a workflow demonstration, not a comprehensive evidence base.",
            "No evidence record is accepted for downstream use.",
            "First-pass full-text extraction is complete; independent extraction review, identity adjudication, and applicability review remain pending.",
            "The publication's abstract-versus-methods participant denominator discrepancy is unresolved.",
            "Formal Draft 2020-12 validation is not run unless the declared jsonschema development dependency is installed.",
        ],
        "validation_results": {
            "registry_application_checks": "see reports/validation_report.md and tests/test_phase4_registry.py",
            "source_unit_tests": "PASS: 12 source-level Phase 4 unit tests",
            "json_schema_draft_2020_12": "NOT_RUN: jsonschema dependency unavailable in build environment",
        },
        "data_counts": {"registered_sources": 1, "evidence_records": 6, "measured_numeric_records": 5,
                         "qualitative_records": 1, "accepted_records": 0, "pending_second_review": 6,
                         "name_only_identity": 6, "context_limited_applicability": 6},
    }
    (release / "release_info.json").write_text(json.dumps(info, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    files = []
    for path in sorted(release.rglob("*")):
        if path.is_file() and path.name not in {"release_manifest.json", "release_manifest.sha256"}:
            files.append({"path": path.relative_to(release).as_posix(), "sha256": sha256(path), "bytes": path.stat().st_size})
    manifest = {
        "manifest_schema": "cookrisk-phase4-release-manifest-v1",
        "release_id": release_id,
        "status": "IN_PROGRESS",
        "artifact_count": len(files),
        "files": files,
    }
    manifest_path = release / "release_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (release / "release_manifest.sha256").write_text(f"{sha256(manifest_path)}  release_manifest.json\n", encoding="ascii")
    print(json.dumps({"release": str(release), "artifact_count": len(files), "manifest_sha256": sha256(manifest_path)}, indent=2))


if __name__ == "__main__":
    main()
