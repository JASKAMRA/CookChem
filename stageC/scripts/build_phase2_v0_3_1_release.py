#!/usr/bin/env python3
"""Build/verify Phase2-v0.3.1, a scientifically bounded final-review successor."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tarfile
from collections import Counter
from pathlib import Path, PurePosixPath

SCRIPT = Path(__file__).resolve()
ROOT = SCRIPT.parents[2]
RELEASES = ROOT / "stageC/releases"
BASE_NAME = "Phase2-v0.3.0"
RELEASE_NAME = "Phase2-v0.3.1"
TARGET = RELEASES / RELEASE_NAME
PREFIX = f"stageC/releases/{BASE_NAME}/"
MANIFEST = "RELEASE_MANIFEST.json"
MANIFEST_DIGEST = "RELEASE_MANIFEST.sha256"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def archive_predecessor() -> None:
    if TARGET.exists():
        raise SystemExit(f"Refusing to overwrite {TARGET}")
    source = RELEASES / BASE_NAME
    if not source.is_dir():
        raise SystemExit(f"Missing immutable predecessor package: {source}")
    shutil.copytree(source, TARGET, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def verify_release(release: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = release / MANIFEST
    digest_path = release / MANIFEST_DIGEST
    if not manifest_path.is_file() or not digest_path.is_file():
        return ["release manifest or manifest digest is missing"]
    manifest_bytes = manifest_path.read_bytes()
    expected_manifest_digest = digest_path.read_text(encoding="utf-8").split()[0]
    if sha256(manifest_bytes) != expected_manifest_digest:
        errors.append("release manifest digest mismatch")
    manifest = json.loads(manifest_bytes)
    for rel, expected in manifest.get("file_hashes", {}).items():
        path = release / rel
        if not path.is_file():
            errors.append(f"missing file: {rel}")
        elif sha256(path.read_bytes()) != expected:
            errors.append(f"hash mismatch: {rel}")
    return errors


def verification_target() -> Path:
    """Locate this package when run either from the repo or from its copy."""
    packaged_root = SCRIPT.resolve().parent.parent
    if (packaged_root / MANIFEST).is_file():
        return packaged_root
    return TARGET


def classify_candidates(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    fields, rows = read_csv(path)
    for name in ("final_classification", "reviewed", "classification_reason", "evidence_reference", "source_verification_status", "yield_mass_balance_status", "numerical_use_allowed"):
        if name not in fields:
            fields.append(name)
    for row in rows:
        context = row["source_matrix_context"].casefold()
        if "turmeric alone" in context:
            classification = "PENDING_SOURCE_BASIS"
            reason = ("Primary source full text reports mg/g spice after cooked samples were cooled and lyophilized, but the exact cooked-table denominator and a validated denominator bridge to the Phase1B as-analyzed retail powder are not established. No cooked yield or total-mass balance is reported; apparent concentration ratio is not mass retention.")
        elif "tamarind" in context:
            classification = "PENDING_MATRIX_COMPATIBILITY"
            reason = ("The primary source cooks turmeric with 0.5 g tamarind in the test matrix, while the linked Phase1B food-composition record is turmeric-only commercial powder. Matrix compatibility and the source analytical denominator are unresolved; no cooked yield or total-mass balance is reported.")
        else:
            classification = "PENDING_MATRIX_COMPATIBILITY"
            reason = ("The primary source used locally purchased powdered pepper, cooked as a 1 g/100 mL water suspension, then freeze-dried; the linked Phase1B retail sample is as-received homogenized pepper with no moisture basis. State, basis, and matrix transfer are unresolved; no yield or total-mass balance is reported.")
        row["final_classification"] = classification
        row["reviewed"] = "true"
        row["classification_reason"] = reason
        row["evidence_reference"] = f"{row.get('source_full_text','')}; DOI:{row.get('source_doi','')}; {row.get('source_table','')}; five replicates as recorded in source ledger."
        row["source_verification_status"] = "PRIMARY_SOURCE_FULL_TEXT_VERIFIED"
        row["yield_mass_balance_status"] = "NOT_REPORTED"
        row["numerical_use_allowed"] = "false"
    if len(rows) != 63 or any(not r["evidence_reference"] or r["reviewed"] != "true" for r in rows):
        raise SystemExit("Retention-candidate review is incomplete or input count differs from frozen scope")
    return fields, rows


def classify_compatibility(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    fields, rows = read_csv(path)
    additions = ["yield_mass_balance_status", "final_status", "final_reason", "evidence_references", "numerical_application_allowed", "identity_review_status", "matrix_review_status", "conditions_review_status", "basis_review_status", "unit_review_status"]
    for name in additions:
        if name not in fields:
            fields.append(name)
    for row in rows:
        record = row["retention_record_id"]
        if record == "P2-RET-004":
            status = "QUALITATIVE_ONLY"
            reason = "The linked green-tea record reports qualitative total-catechin behavior and epimerization but no numerical EGCG retention interval; no numerical adjustment is permitted."
        elif record == "P2-RET-003":
            status = "PENDING_MATRIX_COMPATIBILITY"
            reason = "This source interval is for turmeric cooked with tamarind, but the Phase1B concentration is for turmeric-only powder; the matrix is not interchangeable. The analytical-basis bridge and cooking-condition selection also remain unresolved."
        elif record == "P2-RET-001":
            status = "PENDING_MATRIX_COMPATIBILITY"
            reason = "Source pepper was locally purchased powder cooked in aqueous suspension; Phase1B pepper is an as-received homogenized retail sample with no moisture basis. Matrix/state and basis compatibility remain unresolved."
        else:
            status = "PENDING_SOURCE_BASIS"
            reason = "Turmeric identity and broad spice matrix are compatible, but source cooked samples were lyophilized and reported as mg/g spice while Phase1B commercial powder is as-analyzed and no moisture/denominator bridge or cooking yield is available."
        row["yield_mass_balance_status"] = "NOT_REPORTED"
        row["final_status"] = status
        row["final_reason"] = reason
        row["evidence_references"] = f"{row.get('retention_source_doi','')}; {row.get('retention_record_id','')}; source_observed_retention_evidence.csv; source_condition_level_retention_candidates_2026-11-03.csv"
        row["numerical_application_allowed"] = "false"
        row["identity_review_status"] = row.get("compound_identity_assessment", "")
        row["matrix_review_status"] = row.get("food_matrix_identity_assessment", "")
        row["conditions_review_status"] = "SOURCE CONDITIONS TRANSCRIBED; TRANSFER TO FOOD RECORD NOT ESTABLISHED"
        row["basis_review_status"] = row.get("measurement_basis_assessment", "")
        row["unit_review_status"] = row.get("unit_compatibility", "")
    if len(rows) != 22:
        raise SystemExit("Compatibility matrix count differs from frozen 22 combinations")
    return fields, rows


def classify_applicability(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    fields, rows = read_csv(path)
    additions = ["retention_scope_reviewed", "final_status", "final_reason", "review_evidence_refs"]
    for name in additions:
        if name not in fields:
            fields.append(name)
    for row in rows:
        linked = row.get("candidate_retention_record_ids", "")
        if not linked:
            status = "NO_LINKED_RETENTION_EVIDENCE"
            reason = "No compound-specific quantitative or qualitative retention record is linked in the frozen Phase2 evidence ledger; cooked concentration remains unavailable."
            refs = "Phase2-v0.3.1 retention applicability review; current Stage B retention evidence snapshot"
        elif "P2-RET-004" in linked:
            status = "QUALITATIVE_ONLY"
            reason = "The linked tea evidence is qualitative and provides no numerical EGCG retention factor or compatible brew-specific concentration interval."
            refs = "P2-RET-004; DOI:10.3390/molecules24091735; source_observed_retention_evidence.csv"
        elif "P2-RET-001" in linked:
            status = "PENDING_MATRIX_COMPATIBILITY"
            reason = "Linked pepper source state/moisture basis does not match the as-received homogenized Phase1B retail record; no cooked yield is reported."
            refs = "P2-RET-001; DOI:10.1016/j.jfca.2006.10.002; retention_compatibility_matrix_2026-11-03.csv"
        else:
            status = "PENDING_SOURCE_BASIS_AND_MATRIX_COMPATIBILITY"
            reason = "The turmeric source includes turmeric-alone and turmeric+tamarind contexts; Phase1B is as-analyzed turmeric powder. Source denominator/moisture bridge, matrix selection, and cooked yield are unresolved."
            refs = "P2-RET-002; P2-RET-003; DOI:10.1016/j.jfca.2006.10.002; source_condition_level_retention_candidates_2026-11-03.csv"
        row["retention_scope_reviewed"] = "true"
        row["final_status"] = status
        row["final_reason"] = reason
        row["review_evidence_refs"] = refs
    if len(rows) != 584 or any(r["retention_scope_reviewed"] != "true" for r in rows):
        raise SystemExit("Applicability review must cover all 584 Phase1B records")
    return fields, rows


def review_crosswalk(source_path: Path, detail_path: Path, target_path: Path) -> tuple[list[str], list[dict[str, str]]]:
    _, details = read_csv(detail_path)
    detail_by_group = {r["stagea_group_id"]: r for r in details}
    fields, rows = read_csv(source_path)
    for name in ("final_review_status", "final_review_reason", "identity_evidence_reference", "join_allowed"):
        if name not in fields:
            fields.append(name)
    for row in rows:
        status = row["crosswalk_status"]
        detail = detail_by_group.get(row["stagea_group_id"])
        if detail:
            decision = detail["review_decision"]
            if decision == "PENDING_INTRA_GROUP_CID_CONFLICT":
                final = "NEEDS_MANUAL_SOURCE_ADJUDICATION"
                reason = detail["decision_basis"]
            elif decision == "PENDING_NAME_AND_STRUCTURE_REVIEW":
                final = "PENDING_NAME_AND_STRUCTURE_REVIEW"
                reason = detail["decision_basis"]
            else:
                final = "PENDING_STRUCTURE_EQUIVALENCE_REVIEW"
                reason = detail["decision_basis"]
        elif status == "STRICT_MATCH":
            final = "ACCEPTED_STRICT_MATCH"
            reason = "Existing Stage C crosswalk records an exact accepted identity match; no additional source-record adjudication was performed in this closeout."
        elif status == "STABLE_ID_STRUCTURE_MATCH_CID_DISCREPANCY":
            final = "ACCEPTED_MANUAL_MATCH_WITH_CID_WARNING"
            reason = "Curcumin stable identifier, name, and canonical structure were already manually adjudicated as matching; preserve the Stage A CID discrepancy warning."
        elif status == "NO_STAGEB_CID_MATCH":
            final = "NO_STAGEB_CID_MATCH"
            reason = "No Stage B compound with matching CID is present in the audited crosswalk; no name-only replacement or unsupported identity join was generated."
        elif status == "NO_CID":
            final = "NO_CID"
            reason = "No Stage A PubChem CID is present for this group; identity remains unresolved for cross-stage joining."
        elif status == "INTRA_GROUP_CID_CONFLICT":
            final = "NEEDS_MANUAL_SOURCE_ADJUDICATION"
            reason = "Multiple CIDs occur within a single Stage A group; underlying source rows and structures require adjudication."
        else:
            final = "PENDING_STRUCTURE_EQUIVALENCE_REVIEW"
            reason = "A CID/name candidate exists, but exact structure equivalence including stereochemistry has not been verified; CID alone is insufficient."
        row["final_review_status"] = final
        row["final_review_reason"] = reason
        row["identity_evidence_reference"] = "source_stagea_stageb_identity_crosswalk.csv; identity_candidate_review.csv; Phase2 identity audit dated 2026-11-03"
        row["join_allowed"] = str(final.startswith("ACCEPTED_")).lower()
    if len(rows) != 197:
        raise SystemExit("Identity crosswalk count differs from frozen 197-group scope")
    write_csv(target_path, fields, rows)
    return fields, rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="verify the packaged release manifest")
    args = parser.parse_args()
    if args.verify:
        errors = verify_release(verification_target())
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1
        print(f"PASS: {RELEASE_NAME} manifest and file hashes verified")
        return 0

    archive_predecessor()
    data = TARGET / "data"
    source_pairs = ROOT / "stageC/phase2/data/observed_cooking_pairs.csv"
    shutil.copyfile(source_pairs, data / "source_observed_cooking_pairs.csv")
    shutil.copyfile(ROOT / "stageC/phase2/generated/experimental_apparent_concentration_ratios.csv", data / "experimental_apparent_concentration_ratios.csv")
    shutil.copyfile(ROOT / "stageC/reports/phase2/source_pair_audit_2026-11-03.csv", data / "source_pair_audit_2026-11-03.csv")
    shutil.copyfile(ROOT / "stageC/scripts/audit_phase2_source_pairs.py", TARGET / "scripts/audit_phase2_source_pairs.py")
    shutil.copyfile(ROOT / "stageC/tests/test_phase2_final_review.py", TARGET / "tests/test_phase2_final_review.py")
    release_audit_test = TARGET / "tests/test_release_audit.py"
    release_audit_code = release_audit_test.read_text(encoding="utf-8")
    release_audit_code = release_audit_code.replace("tempfile.TemporaryDirectory() as temp", "tempfile.TemporaryDirectory(dir=RELEASE) as temp")
    release_audit_test.write_text(release_audit_code, encoding="utf-8")

    candidates_path = data / "source_condition_level_retention_candidates_2026-11-03.csv"
    candidate_fields, candidate_rows = classify_candidates(candidates_path)
    write_csv(candidates_path, candidate_fields, candidate_rows)
    compat_path = data / "retention_compatibility_matrix_2026-11-03.csv"
    compat_fields, compat_rows = classify_compatibility(compat_path)
    write_csv(compat_path, compat_fields, compat_rows)
    applicability_path = data / "retention_applicability_review.csv"
    applicability_fields, applicability_rows = classify_applicability(applicability_path)
    write_csv(applicability_path, applicability_fields, applicability_rows)
    crosswalk_fields, crosswalk_rows = review_crosswalk(
        data / "source_stagea_stageb_identity_crosswalk.csv",
        ROOT / "stageC/phase2/data/identity_candidate_review.csv",
        data / "identity_crosswalk_final_review.csv",
    )

    # Keep project working-tree review outputs in sync with the versioned release.
    for filename in ("source_condition_level_retention_candidates_2026-11-03.csv", "retention_compatibility_matrix_2026-11-03.csv"):
        shutil.copyfile(data / filename, ROOT / "stageC/reports/phase2" / filename)
    shutil.copyfile(applicability_path, ROOT / "stageC/phase2/generated/retention_applicability_review.csv")

    # The two v0.2.0 manifest entries were not recoverable from tracked, working-tree,
    # or release-history copies. Preserve that fact without fabricating logs.
    unavailable = [
        {"path": "reports/full_stagec_test_rerun_2026-11-03.log", "reason": "Referenced by Phase2-v0.2.0 manifest, but absent from predecessor package and recoverable project history; omitted rather than fabricated."},
        {"path": "validation/full_stagec_test_rerun_2026-11-03.log", "reason": "Referenced by Phase2-v0.2.0 manifest, but absent from predecessor package and recoverable project history; omitted rather than fabricated."},
    ]
    for artifact in unavailable:
        if (TARGET / artifact["path"]).exists():
            raise SystemExit(f"Unexpected recovered artifact requires provenance review: {artifact['path']}")

    summary_path = data / "phase2_integration_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary.update({
        "release": RELEASE_NAME,
        "phase2_exit_decision": "COMPLETE_WITH_DOCUMENTED_LIMITATIONS",
        "phase2_release": RELEASE_NAME,
        "source_phase1b_release": "Phase1B-v1.3.2",
        "source_phase1b_manifest_sha256": sha256((RELEASES / "Phase1B-v1.3.2/CHECKSUMS.json").read_bytes()),
        "observed_cooking_pairs_reviewed": 117,
        "retention_candidates_reviewed": len(candidate_rows),
        "retention_candidate_classifications": dict(Counter(r["final_classification"] for r in candidate_rows)),
        "compatibility_combinations_reviewed": len(compat_rows),
        "compatibility_final_statuses": dict(Counter(r["final_status"] for r in compat_rows)),
        "applicability_records_reviewed": len(applicability_rows),
        "applicability_final_statuses": dict(Counter(r["final_status"] for r in applicability_rows)),
        "identity_crosswalk_records_reviewed": len(crosswalk_rows),
        "identity_crosswalk_final_statuses": dict(Counter(r["final_review_status"] for r in crosswalk_rows)),
        "cooked_concentration_estimates": 0,
        "retention_applicability_status_counts": dict(Counter(r["final_status"] for r in applicability_rows)),
        "stageb_model_inference": "NOT PERFORMED; not required for the bounded Phase2 evidence closeout",
        "model_inference_performed": False,
    })
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    shutil.copyfile(summary_path, ROOT / "stageC/phase2/generated/phase2_integration_summary.json")

    # Rerun source-pair audit with the packaged corrected auditor and exact package inputs.
    subprocess.run([sys.executable, str(TARGET / "scripts/audit_phase2_source_pairs.py"),
                    "--input", str(data / "source_observed_cooking_pairs.csv"),
                    "--output", str(data / "source_pair_audit_2026-11-03.csv")], check=True, cwd=ROOT)

    phase1b_manifest_hash = sha256((RELEASES / "Phase1B-v1.3.2/CHECKSUMS.json").read_bytes())
    report = f"""# Phase 2 finalization report — {RELEASE_NAME}\n\n## Decision\n\n**COMPLETE_WITH_DOCUMENTED_LIMITATIONS.** The fixed Phase 2 scope was reviewed and validated. Completion means the bounded evidence review and software validation are complete; it does not mean every retention candidate is numerically usable. No cooked-concentration estimates met the required identity, matrix, conditions, basis, unit, and yield/mass-balance checks. The output remains zero rows by design.\n\n## Fixed observed-pair scope\n\n- 117 observed cooking pairs preserved: 33 turmeric and 84 pumpkin-leaf pairs; 24 analytes.\n- 117/117 ratios independently recomputed from reported group means; all source-audit error-code fields are empty.\n- The turmeric table-unit label was corrected from “mg/g fresh rhizome” to the source wording “mg/g plant material”. Fresh rhizome is the starting material; cooked-sample denominator and mass yield remain unavailable. No numeric values changed.\n- Ratios remain apparent concentration ratios, not total analyte-mass retention.\n\n## Retention evidence decisions\n\n- 63/63 source-condition candidates reviewed: {dict(Counter(r['final_classification'] for r in candidate_rows))}. No candidate was accepted for numerical use.\n- 22/22 food × evidence combinations finalized: {dict(Counter(r['final_status'] for r in compat_rows))}.\n- 584/584 Phase1B records received an applicability decision: {dict(Counter(r['final_status'] for r in applicability_rows))}.\n- 197/197 identity-crosswalk rows reviewed: {dict(Counter(r['final_review_status'] for r in crosswalk_rows))}. Twenty existing strict/manual matches remain usable; 177 remain no-match, pending, or manual-review outcomes. The Curcumin CID discrepancy remains visible.\n- Phase2 cooked concentration output: 0 estimates. No unsupported retention factor, cooked mass, moisture correction, yield, or uncertainty was generated.\n\n## Provenance and limits\n\nThe release depends on Phase1B-v1.3.2 with exact manifest SHA-256 `{phase1b_manifest_hash}`. The Stage A model was not accessed or run; model readiness is not required for this Phase 2 evidence closeout. Stage B remains a read-only dependency. Two historical test logs referenced by v0.2.0 were unavailable; exact paths and reasons are listed in `RELEASE_MANIFEST.json`.\n\nUnresolved scientific issues are explicitly retained: turmeric analytical denominator/moisture bridge and cooked yield; turmeric+tamarind versus turmeric-only matrix compatibility; pepper source state/moisture basis; qualitative-only green-tea evidence; and unresolved cross-stage chemical identity/structure cases. These are limitations, not failed validation.\n"""
    (TARGET / "PHASE2_COMPLETION_REPORT.md").write_text(report, encoding="utf-8")
    (TARGET / "reports/PHASE2_FINALIZATION_REPORT.md").write_text(report, encoding="utf-8")
    (TARGET / "README.md").write_text(f"""# CookRisk Stage C — Phase 2 v0.3.0\n\nStatus: **COMPLETE_WITH_DOCUMENTED_LIMITATIONS**. This release closes the fixed 117-observation Phase 2 scope after final review of 63 retention candidates, 22 compatibility combinations, 584 applicability records, and 197 identity crosswalk rows. It produces zero cooked-concentration estimates because the evidence does not establish the required denominator, matrix, condition, and yield compatibility.\n\nSuccessor of Phase2-v0.2.0. Upstream dependency: Phase1B-v1.3.2 (manifest SHA-256 `{phase1b_manifest_hash}`). The Stage A model was not run and Stage B remains read-only. See `reports/PHASE2_FINALIZATION_REPORT.md` for decisions and remaining scientific limitations.\n""", encoding="utf-8")
    validation_report = f"""# Phase 2 validation report — {RELEASE_NAME}\n\n- Pair audit: 117 rows, 0 audit errors; independently recomputed ratios.\n- Retention candidates: 63 of 63 reviewed with final classifications and evidence references.\n- Compatibility: 22 of 22 assigned a final status and reason.\n- Applicability: 584 of 584 reviewed; no row received an unsupported numeric adjustment.\n- Identity crosswalk: 197 of 197 reviewed; only the 19 strict matches and 1 preexisting manually adjudicated Curcumin link are allowed for joining.\n- Cooked concentration output: 0 records; header preserved.\n- Model inference: not performed.\n- Release integrity: all package files listed in `RELEASE_MANIFEST.json`; verify with `python scripts/build_phase2_v0_3_1_release.py --verify`.\n- Historical logs: the two missing artifacts remain documented as unavailable, not recreated.\n"""
    (TARGET / "reports/PHASE2_VALIDATION_REPORT.md").write_text(validation_report, encoding="utf-8")
    (TARGET / "reports/PHASE2_SCIENTIFIC_LIMITATIONS.md").write_text("""# Phase 2 scientific limitations\n\nNo numerical cooked-concentration output is supported by the current evidence. The 117 observed records are condition-level concentration pairs and their ratios are not total-mass retention. Turmeric source cooked samples were lyophilized and table denominators are not fully bridged to Phase1B as-analyzed retail powder; turmeric+tamarind evidence does not match turmeric-only foods; pepper source and Phase1B states/moisture bases differ; cooking yields/mass balances are not reported. Green-tea EGCG evidence is qualitative only. Several Stage A/Stage B identity candidates require structure/stereochemistry or source-level review. Missing scientific inputs remain unresolved rather than imputed.\n""", encoding="utf-8")

    # Preserve predecessor status as a traceable artifact in the successor package.
    predecessor_report = TARGET / "reports/PHASE2_V0_2_PREDECESSOR_STATUS.md"
    predecessor_report.write_text("Phase2-v0.2.0 is preserved byte-for-byte as a historical release. Its status and file hashes describe that predecessor snapshot; the v0.3.0 completion decision and final reviews are recorded in PHASE2_FINALIZATION_REPORT.md.\n", encoding="utf-8")

    (TARGET / "RELEASE.json").write_text(json.dumps({
        "release_id": RELEASE_NAME, "version": "0.3.1", "status": "COMPLETE_WITH_DOCUMENTED_LIMITATIONS",
        "successor_of": BASE_NAME, "created_on": "2026-11-03", "scope": "Fixed 117 observed cooking pairs; no additional study collection.",
        "source_phase1b_release": "Phase1B-v1.3.2", "source_phase1b_manifest_sha256": phase1b_manifest_hash,
        "stage_b_release": "StageB_V20_20261103", "stage_b_read_only": True,
        "stage_a_model_inference_performed": False, "observed_pairs": 117, "analytes": 24,
        "candidate_reviews": 63, "compatibility_reviews": 22, "applicability_reviews": 584,
        "identity_crosswalk_reviews": 197, "cooked_concentration_estimates": 0,
        "excluded_unavailable_artifacts": unavailable,
        "limitations_report": "reports/PHASE2_SCIENTIFIC_LIMITATIONS.md",
        "verification_command": "python scripts/build_phase2_v0_3_1_release.py --verify"
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    shutil.copyfile(SCRIPT, TARGET / "scripts/build_phase2_v0_3_1_release.py")
    # Copy the finalized data review to the working-tree reports only after its audit output exists.
    for name in ("source_condition_level_retention_candidates_2026-11-03.csv", "retention_compatibility_matrix_2026-11-03.csv", "source_pair_audit_2026-11-03.csv"):
        shutil.copyfile(data / name, ROOT / "stageC/reports/phase2" / name)

    files = sorted(p for p in TARGET.rglob("*") if p.is_file() and p.name not in {MANIFEST, MANIFEST_DIGEST} and "__pycache__" not in p.parts and p.suffix != ".pyc")
    file_hashes = {p.relative_to(TARGET).as_posix(): sha256(p.read_bytes()) for p in files}
    file_sizes = {p.relative_to(TARGET).as_posix(): p.stat().st_size for p in files}
    manifest = {
        "release": RELEASE_NAME, "algorithm": "SHA-256", "artifact_count": len(files),
        "file_hashes": file_hashes, "file_sizes": file_sizes,
        "excluded_unavailable_artifacts": unavailable,
        "historical_predecessor_package_bytes": "Copied from git archive HEAD; predecessor release remains unchanged.",
    }
    manifest_bytes = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    (TARGET / MANIFEST).write_bytes(manifest_bytes)
    (TARGET / MANIFEST_DIGEST).write_text(f"{sha256(manifest_bytes)}  {MANIFEST}\n", encoding="utf-8")
    errors = verify_release(TARGET)
    if errors:
        raise SystemExit("Release verification failed: " + "; ".join(errors))
    print(json.dumps({"release": str(TARGET), "status": RELEASE_NAME, "artifact_count": len(files),
                      "pair_count": 117, "candidate_count": len(candidate_rows), "compatibility_count": len(compat_rows),
                      "applicability_count": len(applicability_rows), "crosswalk_count": len(crosswalk_rows),
                      "cooked_estimates": 0, "manifest_sha256": sha256(manifest_bytes)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
