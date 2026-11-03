#!/usr/bin/env python3
"""Build or clean-copy verify additive Phase 2 v0.2.0 evidence release."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve()
if SCRIPT_PATH.parents[1].name == "Phase2-v0.2.0":
    # The packaged copy can verify itself when run from within the release.
    TARGET = SCRIPT_PATH.parents[1]
    RELEASES = TARGET.parent
    ROOT = RELEASES.parent.parent
    BASE = RELEASES / "Phase2-v0.1.0"
else:
    ROOT = SCRIPT_PATH.parents[2]
    RELEASES = ROOT / "stageC/releases"
    BASE = RELEASES / "Phase2-v0.1.0"
    TARGET = RELEASES / "Phase2-v0.2.0"

REPORTS = [
    "PHASE2_FINAL_COMPLETION_REPORT.md",
    "PHASE2_SCIENTIFIC_METHODS.md",
    "PHASE2_DATA_DICTIONARY.md",
    "PHASE2_SCIENTIFIC_LIMITATIONS.md",
    "PHASE2_REPRODUCIBILITY.md",
    "PHASE2_VALIDATION_REPORT.md",
    "PHASE2_NEXT_PHASE_HANDOFF.md",
    "PHASE2_REPOSITORY_AUDIT_2026-11-03.md",
    "PHASE2_IDENTITY_RESOLUTION_AUDIT_2026-11-03.md",
]
REPORT_CSVS = [
    "source_pair_audit_2026-11-03.csv",
    "identity_resolution_audit_2026-11-03.csv",
    "retention_compatibility_matrix_2026-11-03.csv",
    "source_condition_level_retention_candidates_2026-11-03.csv",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def inventory(root: Path) -> dict[str, str]:
    return {
        str(p.relative_to(root)): sha256(p)
        for p in sorted(root.rglob("*"))
        if p.is_file() and p.name != "RELEASE_MANIFEST.json" and "__pycache__" not in p.parts and p.suffix != ".pyc"
    }


def verify_base() -> dict:
    manifest = json.loads((BASE / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
    bad = []
    for rel, expected in manifest["file_hashes"].items():
        p = BASE / rel
        if not p.exists() or sha256(p) != expected:
            bad.append(rel)
    if bad:
        raise SystemExit("Frozen v0.1.0 integrity failure; refusing to build: " + ", ".join(bad))
    return manifest


def assemble(target: Path, source_bundle: Path, source_scripts: Path, source_schemas: Path) -> None:
    if target.exists():
        raise SystemExit(f"Refusing to overwrite existing release: {target}")
    base_manifest = verify_base()
    shutil.copytree(BASE, target)

    report_dir = source_bundle
    target_reports = target / "reports"
    target_reports.mkdir(parents=True, exist_ok=True)
    (target / "schemas").mkdir(parents=True, exist_ok=True)
    (target / "tests").mkdir(parents=True, exist_ok=True)
    for name in REPORTS:
        shutil.copy2(report_dir / name, target_reports / name)
    for name in REPORT_CSVS:
        shutil.copy2(report_dir / name, target_reports / name)
        shutil.copy2(report_dir / name, target / "data" / name)
    shutil.copy2(report_dir / "model_inference_readiness_2026-11-03.json", target_reports / "model_inference_readiness_2026-11-03.json")
    shutil.copy2(report_dir / "full_stagec_test_rerun_2026-11-03.log", target_reports / "full_stagec_test_rerun_2026-11-03.log")
    shutil.copy2(report_dir / "model_inference_readiness_2026-11-03.json", target / "data" / "model_inference_readiness_2026-11-03.json")
    shutil.copy2(report_dir / "full_stagec_test_rerun_2026-11-03.log", target / "validation" / "full_stagec_test_rerun_2026-11-03.log")
    shutil.copy2(source_scripts / "audit_phase2_source_pairs.py", target / "scripts/audit_phase2_source_pairs.py")
    shutil.copy2(source_scripts / "build_phase2_v0_2_release.py", target / "scripts/build_phase2_v0_2_release.py")
    shutil.copy2(source_schemas / "phase2_source_pair_audit.schema.json", target / "schemas/phase2_source_pair_audit.schema.json")
    shutil.copy2(source_schemas / "phase2_cooked_concentration.schema.json", target / "schemas/phase2_cooked_concentration.schema.json")
    release_test = '''from __future__ import annotations\nimport csv\nimport hashlib\nimport json\nimport subprocess\nimport sys\nimport tempfile\nimport unittest\nfrom pathlib import Path\n\nRELEASE = Path(__file__).resolve().parents[1]\n\nclass ReleaseAuditTests(unittest.TestCase):\n    def test_source_audit_rebuilds_byte_identically_and_release_manifest_matches(self):\n        with tempfile.TemporaryDirectory() as temp:\n            out = Path(temp) / "source_audit.csv"\n            subprocess.run([sys.executable, str(RELEASE / "scripts/audit_phase2_source_pairs.py"), "--input", str(RELEASE / "data/source_observed_cooking_pairs.csv"), "--output", str(out)], check=True, capture_output=True, text=True)\n            self.assertEqual(out.read_bytes(), (RELEASE / "data/source_pair_audit_2026-11-03.csv").read_bytes())\n        manifest = json.loads((RELEASE / "RELEASE_MANIFEST.json").read_text())\n        for rel, expected in manifest["file_hashes"].items():\n            self.assertEqual(hashlib.sha256((RELEASE / rel).read_bytes()).hexdigest(), expected, rel)\n        with (RELEASE / "data/cooked_concentration_estimates.csv").open(newline="") as f:\n            self.assertEqual(list(csv.DictReader(f)), [])\n\nif __name__ == "__main__":\n    unittest.main()\n'''
    (target / "tests/test_release_audit.py").write_text(release_test, encoding="utf-8")

    source_pairs = target / "data/source_observed_cooking_pairs.csv"
    audited = target / "data/source_pair_audit_2026-11-03.csv"
    subprocess.run([
        sys.executable, str(target / "scripts/audit_phase2_source_pairs.py"),
        "--input", str(source_pairs), "--output", str(audited),
    ], check=True, cwd=target, capture_output=True, text=True)
    with audited.open(encoding="utf-8-sig", newline="") as f:
        audit_rows = list(csv.DictReader(f))
    if len(audit_rows) != 117 or any(r["audit_error_codes"] for r in audit_rows):
        raise SystemExit("v0.2.0 source audit validation failed")

    readme = """# CookRisk Stage C Phase 2 v0.2.0\n\nStatus: **NOT COMPLETE — source-audit successor.**\n\nThis additive release preserves Phase2-v0.1.0 and adds the 117-row primary-table verification matrix, all record-level compatibility and identity audits, data/method/limitation/reproducibility/validation/handoff documentation, and two Phase 2 JSON schemas. It reports zero scientifically valid cooked-concentration outputs. The frozen Stage B model remains blocked by its missing exact training snapshot.\n\nRebuild from repository root: `python3 stageC/scripts/build_phase2_v0_2_release.py`. Clean-copy verification: `python3 stageC/scripts/build_phase2_v0_2_release.py --verify`. Source-pair audit uses only the Python standard library. Tests: `python3 -m unittest discover -s stageC/tests -p 'test_phase2*.py' -v`; the full Stage C suite retains three legacy Phase 1B checkpoint/count failures documented in `reports/PHASE2_VALIDATION_REPORT.md`.\n"""
    (target / "README.md").write_text(readme, encoding="utf-8")
    shutil.copy2(report_dir / "PHASE2_FINAL_COMPLETION_REPORT.md", target / "PHASE2_COMPLETION_REPORT.md")

    validation = {
        "release": "Phase2-v0.2.0",
        "status": "NOT COMPLETE",
        "source_pair_audit": {
            "records": 117,
            "primary_table_values_verified": 117,
            "basis_limited_turmeric_records": 33,
            "independent_ratio_formula": "cooked group mean / raw group mean",
            "cooked_concentration_outputs": 0,
        },
        "phase2_tests": {"command": "python3 -m unittest discover -s stageC/tests -p 'test_phase2*.py' -v", "total": 15, "passed": 15, "failed": 0},
        "full_stagec_tests": {
            "command": "python3 -m unittest discover -s stageC/tests -v",
            "total": 114, "passed": 111, "failed": 3,
            "failures": [
                {"test": "test_current_coverage_register_reconciles_all_143_stage_b_ids", "detail": "legacy expected 100; observed 101"},
                {"test": "test_checkpoint_preserves_active_data_and_records_batch_totals", "detail": "legacy expected 62 source rows; observed 63"},
                {"test": "test_all_stage_b_ids_screened_and_coverage_is_identity_gated", "detail": "legacy expected 100; observed 101"},
            ],
        },
        "reproducibility": {
            "v0_1_clean_copy_build": "PASS",
            "v0_2_builder": "scripts/build_phase2_v0_2_release.py",
            "clean_copy_verification_command": "python3 stageC/scripts/build_phase2_v0_2_release.py --verify",
            "full_git_clone": False,
        },
        "model_inference": {"status": "BLOCKED", "reason": "Exact training snapshot SHA-256 is unavailable; inference was not attempted."},
        "phase1b_v1_3_hashes": {"verified_artifacts": 1321, "mismatches": 0},
        "phase2_v0_1_hashes": {"verified_files": 19, "mismatches": 0},
        "v0_1_manifest_sha256": sha256(BASE / "RELEASE_MANIFEST.json"),
        "cooked_output_rows": 0,
    }
    (target / "validation/validation_summary.json").write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")

    source_manifest_hash = sha256(BASE / "RELEASE_MANIFEST.json")
    manifest = {
        "release": "Phase2-v0.2.0",
        "status": "NOT COMPLETE — source-audit successor",
        "successor_of": "Phase2-v0.1.0",
        "source_phase1b_release": "Phase1B-v1.3.0",
        "build_command": "python3 stageC/scripts/build_phase2_v0_2_release.py",
        "clean_copy_verify_command": "python3 stageC/scripts/build_phase2_v0_2_release.py --verify",
        "preserved_source_release_manifest_sha256": source_manifest_hash,
        "cooked_concentration_output_count": 0,
        "model_inference_performed": False,
        "file_hashes": inventory(target),
    }
    (target / "RELEASE_MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def verify() -> None:
    if not TARGET.exists():
        raise SystemExit(f"No release to verify at {TARGET}")
    with tempfile.TemporaryDirectory(prefix="cookrisk-phase2-v020-verify-") as tmp:
        expected = Path(tmp) / "Phase2-v0.2.0"
        assemble(expected, TARGET / "reports", TARGET / "scripts", TARGET / "schemas")
        expected_files = inventory(expected)
        actual_files = inventory(TARGET)
        if expected_files != actual_files:
            missing = sorted(set(expected_files) - set(actual_files))
            extra = sorted(set(actual_files) - set(expected_files))
            changed = sorted(k for k in set(expected_files) & set(actual_files) if expected_files[k] != actual_files[k])
            raise SystemExit(f"Clean-copy mismatch: missing={missing}; extra={extra}; changed={changed}")
        manifest = json.loads((TARGET / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
        mismatches = [rel for rel, expected_hash in manifest["file_hashes"].items() if not (TARGET / rel).exists() or sha256(TARGET / rel) != expected_hash]
        if mismatches:
            raise SystemExit("Release manifest mismatch: " + ", ".join(mismatches))
        print(f"Clean-copy rebuild matched all {len(actual_files)} release-file hashes; manifest verified.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="rebuild in a disposable clean copy and compare all release files")
    args = parser.parse_args()
    if args.verify:
        verify()
    else:
        assemble(TARGET, ROOT / "stageC/reports/phase2", ROOT / "stageC/scripts", ROOT / "stageC/schemas")
        manifest = json.loads((TARGET / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
        print(f"Created {manifest['release']} with {len(manifest['file_hashes'])} hashed files at {TARGET}")


if __name__ == "__main__":
    main()
