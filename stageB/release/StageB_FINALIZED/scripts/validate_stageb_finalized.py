"""Validate the StageB_FINALIZED package and its canonical warning lifecycle."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


EXPECTED = {
    "compounds": 143,
    "evidence": 317,
    "drug_probe_rows": 133,
    "bibliography_rows": 163,
    "study_rows": 161,
    "source_audit_rows": 317,
    "warning_rows": 88,
    "inherited_warning_rows": 70,
    "new_v19_warning_rows": 18,
    "v19_review_rows": 53,
}
FINAL_STATUS_MAP = {
    "RESOLVED": "RESOLVED",
    "PARTIALLY_RESOLVED": "PARTIALLY_RESOLVED",
    "STILL_VALID": "VALID",
    "VALID": "VALID",
    "NEEDS_MANUAL_REVIEW": "NEEDS_MANUAL_REVIEW",
    "NOT_APPLICABLE": "NOT_APPLICABLE",
}
OPEN_V19_WARNINGS = {"V19-W01", *(f"V19-W{i:02d}" for i in range(2, 10)), *(f"V19-W{i:02d}" for i in range(11, 14)), *(f"V19-W{i:02d}" for i in range(15, 19))}
FINAL_COUNTS = {
    "RESOLVED": 5,
    "PARTIALLY_RESOLVED": 15,
    "VALID": 26,
    "NEEDS_MANUAL_REVIEW": 40,
    "NOT_APPLICABLE": 2,
}


def read_rows(root: Path, rel: str) -> list[dict[str, str]]:
    with (root / rel).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_records(
    root: Path,
    compounds: list[dict[str, str]],
    evidence: list[dict[str, str]],
    drugs: list[dict[str, str]],
    bibliography: list[dict[str, str]],
    studies: list[dict[str, str]],
    source_audit: list[dict[str, str]],
    claims: list[dict[str, str]],
    warnings: list[dict[str, str]],
    warning_audit: list[dict[str, str]],
    baseline_warnings: list[dict[str, str]],
    batch_reviews: list[dict[str, str]],
    metadata: dict,
) -> list[str]:
    root = Path(root)
    errors: list[str] = []

    def count(rows, expected: int, label: str) -> None:
        if len(rows) != expected:
            errors.append(f"{label} row count must be {expected}, got {len(rows)}")

    def unique(rows, field: str, label: str) -> set[str]:
        values = [r.get(field, "").strip() for r in rows]
        present = [v for v in values if v]
        if len(present) != len(set(present)):
            errors.append(f"{label} contains duplicate {field} values")
        return set(present)

    for rows, expected, label in (
        (compounds, EXPECTED["compounds"], "compound registry"),
        (evidence, EXPECTED["evidence"], "interaction evidence"),
        (drugs, EXPECTED["drug_probe_rows"], "drug/probe registry"),
        (bibliography, EXPECTED["bibliography_rows"], "bibliography"),
        (studies, EXPECTED["study_rows"], "study registry"),
        (source_audit, EXPECTED["source_audit_rows"], "source audit"),
        (warnings, EXPECTED["warning_rows"], "warning ledger"),
        (batch_reviews, EXPECTED["v19_review_rows"], "completed V19 batch reviews"),
    ):
        count(rows, expected, label)

    compound_ids = unique(compounds, "Compound_ID", "compound registry")
    evidence_ids = unique(evidence, "Evidence_ID", "interaction evidence")
    drug_labels = unique(drugs, "Drug_Probe", "drug/probe registry")
    study_ids = unique(studies, "Study_ID", "study registry")
    unique(bibliography, "PMID", "bibliography")
    audit_ids = unique(source_audit, "Evidence_ID", "source audit")
    claim_ids = unique(claims, "Evidence_ID", "claim support")
    warning_ids = unique(warnings, "Warning_ID", "warning ledger")
    warning_audit_ids = unique(warning_audit, "Warning_ID", "warning audit")
    baseline_ids = unique(baseline_warnings, "Warning_ID", "V18 warning baseline")
    review_ids = unique(batch_reviews, "Evidence_ID", "V19 batch review rows")

    if audit_ids != evidence_ids:
        errors.append("source-audit identifiers must exactly cover all evidence identifiers")
    if claim_ids != evidence_ids:
        errors.append("claim-support identifiers must exactly cover all evidence identifiers")
    if warning_audit_ids != warning_ids:
        errors.append("warning audit identifiers must exactly match the warning ledger")
    if len(baseline_ids) != EXPECTED["inherited_warning_rows"] or not baseline_ids <= warning_ids:
        errors.append("all 70 inherited V18 warning IDs must be preserved")
    new_v19_ids = {wid for wid in warning_ids if wid.startswith("V19-")}
    if len(new_v19_ids) != EXPECTED["new_v19_warning_rows"]:
        errors.append("all 18 completed V19 warning rows must be preserved")
    if len(review_ids) != EXPECTED["v19_review_rows"]:
        errors.append("completed V19 review records must be unique")

    for row in evidence:
        eid = row.get("Evidence_ID", "")
        if row.get("Compound_ID", "") not in compound_ids:
            errors.append(f"{eid}: compound reference does not resolve")
        if row.get("Drug", "") not in drug_labels:
            errors.append(f"{eid}: drug/probe reference does not resolve")
        if row.get("Study_ID", "") not in study_ids:
            errors.append(f"{eid}: study reference does not resolve")
        pmid = row.get("PMID", "").strip()
        if pmid and not any(p.get("PMID", "").strip() == pmid for p in bibliography):
            errors.append(f"{eid}: PMID does not resolve in bibliography")

    pubs_by_pmid = {r.get("PMID", "").strip(): r for r in bibliography if r.get("PMID", "").strip()}
    for row in studies:
        pmid = row.get("PMID", "").strip()
        if pmid and pmid not in pubs_by_pmid:
            errors.append(f"{row.get('Study_ID', '')}: study publication does not resolve")

    warning_by_id = {r.get("Warning_ID", ""): r for r in warnings}
    audit_by_id = {r.get("Warning_ID", ""): r for r in warning_audit}
    for wid, row in warning_by_id.items():
        legacy = row.get("Audit_Status", "")
        final = row.get("Final_Disposition", "")
        expected_final = FINAL_STATUS_MAP.get(legacy)
        if expected_final is None:
            errors.append(f"{wid}: unsupported historical audit status {legacy!r}")
        elif final != expected_final:
            errors.append(f"{wid}: final disposition does not preserve the V19 status meaning")
        if audit_by_id.get(wid, {}).get("V19_Status", "") != legacy:
            errors.append(f"{wid}: V19 warning audit does not match its preserved historical status")
        if not row.get("Description", "").strip() or not row.get("Affected", "").strip():
            errors.append(f"{wid}: warning description or affected-record reference is blank")

    for wid in OPEN_V19_WARNINGS & warning_ids:
        row = warning_by_id[wid]
        if row.get("Audit_Status") not in {"STILL_VALID", "NEEDS_MANUAL_REVIEW", "PARTIALLY_RESOLVED"}:
            errors.append(f"{wid}: documented scientific uncertainty must remain open")
        if row.get("Final_Disposition") not in {"VALID", "NEEDS_MANUAL_REVIEW", "PARTIALLY_RESOLVED"}:
            errors.append(f"{wid}: final disposition incorrectly closes an open scientific warning")

    observed_counts: dict[str, int] = {}
    for row in warnings:
        status = row.get("Final_Disposition", "")
        observed_counts[status] = observed_counts.get(status, 0) + 1
    if observed_counts != FINAL_COUNTS:
        errors.append(f"final warning disposition counts do not match the register: {observed_counts}")

    v19_review_ids = set()
    review_tiers: dict[str, int] = {}
    for row in batch_reviews:
        eid = row.get("Evidence_ID", "")
        if eid in v19_review_ids:
            errors.append(f"{eid}: appears in more than one V19 batch review")
        v19_review_ids.add(eid)
        try:
            tier = int(row.get("Verification_Tier", ""))
        except ValueError:
            errors.append(f"{eid}: V19 verification tier is not numeric")
            continue
        review_tiers[str(tier)] = review_tiers.get(str(tier), 0) + 1
        source = next((r for r in source_audit if r.get("Evidence_ID") == eid), {})
        if source.get("Verification_Level") != str(tier):
            errors.append(f"{eid}: batch review tier differs from source audit")
        if "V19" not in source.get("Verification_Status", "") and "V19" not in source.get("Audit_Disposition", ""):
            errors.append(f"{eid}: source audit does not identify its V19 review")
    if review_tiers != {"1": 40, "3": 13}:
        errors.append(f"V19 review tier totals differ from the completed batches: {review_tiers}")

    outcomes_blank = sum(not row.get("Quantitative_Outcome", "").strip() for row in evidence)
    if outcomes_blank != 44:
        errors.append(f"expected 44 remaining blank quantitative outcomes, got {outcomes_blank}")

    if metadata.get("release") != "StageB_FINALIZED":
        errors.append("release metadata does not identify StageB_FINALIZED")
    final_status = "FINALIZED_WITH_DOCUMENTED_SCIENTIFIC_LIMITATIONS"
    if metadata.get("release_status") != final_status or metadata.get("readiness") != final_status:
        errors.append("release metadata does not carry the required final status")
    if metadata.get("warning_count") != EXPECTED["warning_rows"]:
        errors.append("release metadata warning count does not match the final register")
    if metadata.get("final_warning_disposition_counts") != FINAL_COUNTS:
        errors.append("release metadata final warning disposition counts do not match the register")
    finalization = metadata.get("finalization", {})
    if finalization.get("selected_source") != "StageB_V19_20261103" or finalization.get("v19_batch_013_created") is not False:
        errors.append("finalization provenance is incomplete or includes an unapproved later batch")

    required = (
        "README.md",
        "RELEASE_STATUS.md",
        "release_metadata.json",
        "data/compound_registry.csv",
        "data/drug_probe_registry.csv",
        "data/interaction_evidence.csv",
        "data/publication_bibliography.csv",
        "data/study_registry.csv",
        "data/warning_ledger.csv",
        "provenance/source_audit.csv",
        "provenance/claim_support_and_verification.csv",
        "validation/V19_warning_audit.csv",
        "scripts/validate_final.py",
        "scripts/mutation_test_final.py",
        "manifests/SHA256SUMS.json",
    )
    for rel in required:
        if not (root / rel).is_file():
            errors.append(f"required release artifact is missing: {rel}")
    if (root / "NEXT_STEPS.md").exists():
        errors.append("stale open-ended research handoff must not ship in the finalized package")
    if any(root.glob("validation/V19_batch_013*")):
        errors.append("unapproved partial V19-013 artifacts must not ship")
    return sorted(set(errors))


def validate(root: Path) -> list[str]:
    root = Path(root).resolve()
    parent = root.parent / "StageB_V18_20261103"
    try:
        reviews = []
        for path in sorted((root / "validation").glob("V19_batch_*_review.csv")):
            reviews.extend(read_rows(root, path.relative_to(root).as_posix()))
        metadata = json.loads((root / "release_metadata.json").read_text(encoding="utf-8-sig"))
        return validate_records(
            root,
            read_rows(root, "data/compound_registry.csv"),
            read_rows(root, "data/interaction_evidence.csv"),
            read_rows(root, "data/drug_probe_registry.csv"),
            read_rows(root, "data/publication_bibliography.csv"),
            read_rows(root, "data/study_registry.csv"),
            read_rows(root, "provenance/source_audit.csv"),
            read_rows(root, "provenance/claim_support_and_verification.csv"),
            read_rows(root, "data/warning_ledger.csv"),
            read_rows(root, "validation/V19_warning_audit.csv"),
            read_rows(parent, "data/warning_ledger.csv"),
            reviews,
            metadata,
        )
    except (OSError, csv.Error, json.JSONDecodeError) as exc:
        return [f"validation input unreadable: {exc}"]


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    failures = validate(target)
    print(json.dumps({"release": target.resolve().name, "status": "PASS" if not failures else "FAIL", "errors": failures}, indent=2))
    raise SystemExit(bool(failures))
