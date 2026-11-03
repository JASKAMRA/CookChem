"""Build or verify the immutable, core-testable Phase3-v0.1.1 package."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STAGE = ROOT / "stageC"
RELEASE_ID = "Phase3-v0.1.1"
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
    for entry in manifest.get("files", []):
        relative = str(entry.get("path", ""))
        path = TARGET / relative
        try:
            path.resolve().relative_to(TARGET.resolve())
        except ValueError:
            raise SystemExit(f"Unsafe manifest path: {relative}") from None
        if path.is_symlink() or not path.is_file() or path.stat().st_size != entry.get("bytes") or sha256(path) != entry.get("sha256"):
            raise SystemExit(f"Release artifact verification failed: {relative}")
    if len(manifest.get("files", [])) != manifest.get("artifact_count"):
        raise SystemExit("Phase 3 release artifact count mismatch")
    return {"status": "PASS", "release_id": RELEASE_ID, "artifact_count": manifest["artifact_count"],
            "manifest_sha256": manifest_hash}


def build() -> dict[str, object]:
    if TARGET.exists():
        raise SystemExit(f"Refusing to overwrite immutable release package: {TARGET}")
    stage_package = TARGET / "stageC"
    for relative in (
        "src/stage_c", "schemas/recipe.schema.json", "schemas/meal.schema.json",
        "examples/recipe_apples_epicatechin.json", "examples/meal_apple_and_cocoa.json",
        "reports/phase3/PHASE3_RECIPE_MEAL_ARCHITECTURE.md",
        "reports/phase3/PHASE3_USER_GUIDE.md",
        "tests/test_recipe_engine.py", "tests/test_recipe_cli.py", "tests/test_recipe_schema.py",
        "requirements-dev.txt",
    ):
        source = STAGE / relative
        destination = stage_package / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        else:
            shutil.copy2(source, destination)
    (TARGET / "README.md").write_text("""# CookRisk Phase 3 recipe and meal core — v0.1.0

Status: **COMPLETE_WITH_DOCUMENTED_LIMITATIONS**. This versioned package contains the source-traceable recipe/meal core, schemas, realistic pinned-release examples, and focused synthetic tests. The tests run from this directory without network access or external release data.

Run the package's isolated core tests from the repository root:

```powershell
python -m unittest discover -s stageC/releases/Phase3-v0.1.1/stageC/tests -v
```

The calculation CLI in the working source uses the pinned Phase1B, Phase2, and Phase4 packages in the repository. The core package's independent tests use synthetic fixtures; live CLI calculations are verified in the project working tree against Phase1B-v1.3.2, Phase2-v0.3.1, and Phase4-v0.1.2. No Phase 1B, Phase 2, Stage B, or Phase 4 data is copied into this Phase 3 package.

Measured mass/volume remain distinct. Missing inputs stay missing. The release contains no cooking-retention factors; Phase2-v0.3.1 has zero quantitative cooked-concentration estimates. Clinical interpretation is outside scope.
""", encoding="utf-8")
    (TARGET / "CHANGELOG.md").write_text("""# Phase 3 changelog

## Phase3-v0.1.1 — 2026-11-03

- Adds JSON recipe and meal validation/storage and an existing-project CLI workflow.
- Adds explicit raw/cooked/serving/leftover mass accounting and separate beverage-volume accounting.
- Adds Phase1B exposure reuse, raw-reference totals, multi-recipe/direct-food aggregation, partial servings, and explicit leftover serving equivalents.
- Adds a read-only, checksum-verified adapter for Phase1B-v1.3.2, Phase2-v0.3.1, and Phase4-v0.1.2. Phase 4 numerical PK is not exposed to calculations.
- Cooked estimates remain unavailable when the versioned Phase 2 package has no eligible quantitative records.
""", encoding="utf-8")
    release = {
        "release_id": RELEASE_ID,
        "version": "0.1.1",
        "status": "COMPLETE_WITH_DOCUMENTED_LIMITATIONS",
        "created_on": "2026-11-03",
        "upstream_dependencies": [
            {"release_id": "Phase1B-v1.3.2", "manifest_sha256": "df3a95ae0957b68a89e38098c0824877196aa74ef7dd92573e6ab1f37e39b9b5", "use": "read-only food composition, compound mapping, identity; not quantitative eligibility inference"},
            {"release_id": "Phase2-v0.3.1", "manifest_sha256": "2b72e4df095002952fcf2eef2af3381425384317d6ea259b81676ed8c243746e", "use": "read-only; zero quantitative cooked-concentration estimates"},
            {"release_id": "Phase4-v0.1.2", "manifest_sha256": "9d6a3a13d6567a872bfb890cf02ea118648a8572c92ebdd8e33b970d0f889fba", "use": "read-only qualitative-context selector; numerical PK excluded"},
        ],
        "validation_results": {"core_tests": "run independently from package; see test output", "json_schema_draft_2020_12": "NOT_RUN: jsonschema development dependency absent in build environment"},
        "known_limitations": [
            "Phase2-v0.3.1 contains no quantitative cooked-concentration estimate; cooked exposure remains unavailable unless a later pinned Phase 2 release passes every gate.",
            "Formal Draft 2020-12 schema validation was not run; stageC/requirements-dev.txt declares jsonschema>=4.18,<5.",
            "Phase 3 reports food-compound exposure and performs no clinical interpretation.",
            "Live CLI calculation resolves pinned upstream releases from the repository workspace; this core package's included tests use synthetic data and run independently.",
        ],
        "stage_a_touched": False,
        "stage_b_modified": False,
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
