"""Build or verify the immutable Phase3-v0.1.2 successor package."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STAGE = ROOT / "stageC"
RELEASE_ID = "Phase3-v0.1.2"
TARGET = STAGE / "releases" / RELEASE_ID


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify() -> dict[str, object]:
    manifest_path = TARGET / "RELEASE_MANIFEST.json"
    digest_path = TARGET / "RELEASE_MANIFEST.sha256"
    if not manifest_path.is_file() or not digest_path.is_file():
        raise SystemExit("Phase 3 release manifest or detached digest is missing")
    manifest_hash = sha256(manifest_path)
    if manifest_hash != digest_path.read_text(encoding="ascii").split()[0]:
        raise SystemExit("Phase 3 release manifest digest mismatch")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("release_id") != RELEASE_ID or manifest.get("algorithm") != "SHA-256":
        raise SystemExit("Unexpected Phase 3 release metadata")
    expected_paths = set()
    for entry in manifest.get("files", []):
        relative = str(entry.get("path", ""))
        path = TARGET / relative
        try:
            path.resolve().relative_to(TARGET.resolve())
        except ValueError:
            raise SystemExit(f"Unsafe manifest path: {relative}") from None
        if path.is_symlink() or not path.is_file() or path.stat().st_size != entry.get("bytes") or sha256(path) != entry.get("sha256"):
            raise SystemExit(f"Release artifact verification failed: {relative}")
        if relative in expected_paths:
            raise SystemExit(f"Duplicate manifest path: {relative}")
        expected_paths.add(relative)
    actual_paths = {
        path.relative_to(TARGET).as_posix() for path in TARGET.rglob("*")
        if path.is_file() and path.name not in {"RELEASE_MANIFEST.json", "RELEASE_MANIFEST.sha256"}
        and "__pycache__" not in path.parts and path.suffix.casefold() != ".pyc"
    }
    if expected_paths != actual_paths or len(expected_paths) != manifest.get("artifact_count"):
        raise SystemExit("Phase 3 release artifact list is incomplete or inconsistent")
    return {"status": "PASS", "release_id": RELEASE_ID, "artifact_count": manifest["artifact_count"],
            "manifest_sha256": manifest_hash}


def _copy_file(relative: str) -> None:
    source = STAGE / relative
    destination = TARGET / "stageC" / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def build() -> dict[str, object]:
    if TARGET.exists():
        raise SystemExit(f"Refusing to overwrite immutable release package: {TARGET}")
    (TARGET / "stageC").mkdir(parents=True)
    shutil.copytree(STAGE / "src" / "stage_c", TARGET / "stageC" / "src" / "stage_c",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    for directory in ("schemas", "phase4/schemas"):
        shutil.copytree(STAGE / directory, TARGET / "stageC" / directory,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    for relative in (
        "examples/recipe_apples_epicatechin.json",
        "examples/meal_apple_and_cocoa.json",
        "reports/phase3/PHASE3_RECIPE_MEAL_ARCHITECTURE.md",
        "reports/phase3/PHASE3_USER_GUIDE.md",
        "reports/phase2/STAGE_A_INTEGRATION_READINESS.md",
        "reports/phase4/UNCERTAINTY_FOUNDATION.md",
        "reports/phase5/VALIDATION_FOUNDATION.md",
        "tests/test_recipe_engine.py",
        "tests/test_recipe_schema.py",
        "tests/test_recipe_cli.py",
        "tests/test_cooking_integration.py",
        "tests/test_phase4_phase5_foundations.py",
        "tests/test_validation.py",
        "requirements-dev.txt",
    ):
        _copy_file(relative)

    (TARGET / "README.md").write_text(f"""# CookRisk Phase 3 recipe and meal core — v0.1.2

Status: **COMPLETE_WITH_DOCUMENTED_LIMITATIONS**. This immutable successor hardens recipe and meal schemas, adds a provenance-gated Stage A output adapter, independent cooking-semantics checks, and Phase 4/5 uncertainty and validation foundations.

Run the isolated package tests from the repository root:

```powershell
python -m pip install -r stageC/releases/{RELEASE_ID}/stageC/requirements-dev.txt
$env:PYTHONPATH = 'stageC/releases/{RELEASE_ID}/stageC/src;stageC/releases/{RELEASE_ID}/stageC/tests'
python -m unittest discover -s stageC/releases/{RELEASE_ID}/stageC/tests -v
```

The package preserves Phase1B-v1.3.2, Phase2-v0.3.1, and Phase4-v0.1.2 as read-only upstream references. Phase2-v0.3.1 has zero quantitative cooked-concentration estimates. The inspected Stage A workspace has no serialized model artifact or defined `Retention_Final` denominator/measurement basis; no Stage A inference is run and model estimates remain blocked. Missing evidence, yield, or uncertainty remains explicit. This package makes no published-data or external-validation claim and performs no clinical interpretation.
""", encoding="utf-8")
    (TARGET / "CHANGELOG.md").write_text("""# Phase 3 changelog

## Phase3-v0.1.2 — 2026-11-04

- Formally validates every active Stage C Draft 2020-12 schema; fixes decimal-string bounds for recipe/meal quantities, counts, and fractions.
- Rejects malformed runtime recipe/meal identifiers and preserves unresolved mapping and missing batch-yield states.
- Adds a supplied Stage A output contract with pinned input/runner hashes, provenance, explicit semantics, eight compatibility gates, scientific review status, and blocked mock outputs.
- Separates apparent concentration ratio, concentration retention, total-mass retention, measured retention, and model-predicted retention; requires measured mass or volume yield for total-mass retention calculations.
- Adds bounded, non-probabilistic uncertainty propagation and independent arithmetic validation foundations.
- Stage A remains read-only and unexecuted; Phase2-v0.3.1 remains at zero quantitative cooked estimates.
""", encoding="utf-8")
    release = {
        "release_id": RELEASE_ID,
        "version": "0.1.2",
        "status": "COMPLETE_WITH_DOCUMENTED_LIMITATIONS",
        "created_on": "2026-11-04",
        "upstream_dependencies": [
            {"release_id": "Phase1B-v1.3.2", "manifest_sha256": "df3a95ae0957b68a89e38098c0824877196aa74ef7dd92573e6ab1f37e39b9b5", "use": "read-only food composition, compound mapping, and identity"},
            {"release_id": "Phase2-v0.3.1", "manifest_sha256": "2b72e4df095002952fcf2eef2af3381425384317d6ea259b81676ed8c243746e", "use": "read-only; zero quantitative cooked-concentration estimates"},
            {"release_id": "Phase4-v0.1.2", "manifest_sha256": "9d6a3a13d6567a872bfb890cf02ea118648a8572c92ebdd8e33b970d0f889fba", "use": "read-only approved contextual selector; no PK multiplier"},
        ],
        "validation_results": {
            "root_stage_c_suite": "199 passed, 0 failed, 0 skipped; see parent execution report",
            "package_core_suite": "Run from this package; see execution report",
            "draft_2020_12_active_schemas": "7 schemas formally checked with pinned jsonschema development dependencies",
        },
        "known_limitations": [
            "Phase2-v0.3.1 contains zero accepted quantitative cooked-concentration estimates.",
            "Stage A has no serialized estimator artifact or output manifest; its target measurement basis is undocumented, so supplied model estimates remain ineligible.",
            "Uncertainty intervals require explicit sourced bounds; current raw food-composition and recipe inputs often remain point-estimate-only.",
            "No published-data comparison or external scientific validation was conducted.",
            "No clinical risk interpretation or patient guidance is implemented.",
        ],
        "stage_a_modified_or_executed": False,
        "stage_b_source_modified": False,
        "historical_releases_modified": False,
    }
    (TARGET / "RELEASE.json").write_text(json.dumps(release, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    artifacts = []
    for path in sorted(TARGET.rglob("*")):
        if path.is_file() and path.name not in {"RELEASE_MANIFEST.json", "RELEASE_MANIFEST.sha256"}:
            artifacts.append({"path": path.relative_to(TARGET).as_posix(), "sha256": sha256(path), "bytes": path.stat().st_size})
    manifest = {"release_id": RELEASE_ID, "algorithm": "SHA-256", "artifact_count": len(artifacts), "files": artifacts}
    manifest_path = TARGET / "RELEASE_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (TARGET / "RELEASE_MANIFEST.sha256").write_text(f"{sha256(manifest_path)}  RELEASE_MANIFEST.json\n", encoding="ascii")
    return verify()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="verify the existing immutable package")
    args = parser.parse_args()
    print(json.dumps(verify() if args.verify else build(), indent=2))


if __name__ == "__main__":
    main()
