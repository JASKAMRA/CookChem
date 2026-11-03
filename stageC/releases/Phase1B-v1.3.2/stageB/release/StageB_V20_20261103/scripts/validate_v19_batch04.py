"""Validate V19-004 full-text evidence, source locators, and warning lifecycle."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

BATCH4 = {
    "SB-0138": ("24276478", "10.3892/mmr.2013.1830"),
    "SB-0139": ("24276478", "10.3892/mmr.2013.1830"),
    "SB-0182": ("26396928", ""),
    "SB-0183": ("26396928", ""),
}
EXPECTED_CACHES = {
    "24276478": "history/rebuild_artifacts/56800bfd89cb785cadf533fc8887c7a4f29bc1b233333f1ad2c10102b6720893_pmid_24276478.json",
    "26396928": "history/rebuild_artifacts/306d5b6e6fb6056adf5a6a03f3d32e5d7e48dfd1c6dfe73c63cfb76522f43506_pmid_26396928.json",
}
MARKERS = {
    "SB-0138": ["Qualitative outcome only", "HT-29", "LoVo", "antagonism", "not estimated"],
    "SB-0139": ["Qualitative outcome only", "HT-29", "LoVo", "antagonism", "not estimated"],
    "SB-0182": ["CI ≤1", "CI <1", "10–20 μM", "8–16 μM", "72 h", "V19-W09"],
    "SB-0183": ["94.3 ± 4.8%", ">24 days", "46.4 ± 18.3%", "46.6 ± 18.3%", "V19-W07", "V19-W08"],
}
NEW_WARNINGS = {"V19-W07", "V19-W08", "V19-W09", "V19-W10"}


def read_rows(root: Path, rel: str) -> list[dict[str, str]]:
    with (root / rel).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_records(
    root: Path,
    evidence: list[dict[str, str]],
    source_audit: list[dict[str, str]],
    claims: list[dict[str, str]],
    warnings: list[dict[str, str]],
    warning_audit: list[dict[str, str]],
    review: list[dict[str, str]],
    bibliography: list[dict[str, str]],
    baseline_evidence: list[dict[str, str]],
    baseline_warnings: list[dict[str, str]],
) -> list[str]:
    root = Path(root).resolve()
    errors: list[str] = []
    ids = [r.get("Evidence_ID", "") for r in evidence]
    audit_ids = [r.get("Evidence_ID", "") for r in source_audit]
    claim_ids = [r.get("Evidence_ID", "") for r in claims]
    review_ids = [r.get("Evidence_ID", "") for r in review]
    if len(ids) != len(set(ids)):
        errors.append("duplicate evidence IDs")
    if len(audit_ids) != len(set(audit_ids)) or set(audit_ids) != set(ids):
        errors.append("source audit must uniquely cover every evidence record")
    if len(claim_ids) != len(set(claim_ids)) or not set(BATCH4) <= set(claim_ids):
        errors.append("claim support must uniquely include each Batch 004 evidence record")
    if len(review_ids) != len(set(review_ids)) or set(review_ids) != set(BATCH4):
        errors.append("Batch 004 review must cover all four target records exactly once")

    by_e = {r.get("Evidence_ID", ""): r for r in evidence}
    by_a = {r.get("Evidence_ID", ""): r for r in source_audit}
    by_c = {r.get("Evidence_ID", ""): r for r in claims}
    by_r = {r.get("Evidence_ID", ""): r for r in review}
    pub_by_pmid = {r.get("PMID", ""): r for r in bibliography}
    for evidence_id, (pmid, doi) in BATCH4.items():
        e, a, c, r = (by_e.get(evidence_id, {}), by_a.get(evidence_id, {}),
                      by_c.get(evidence_id, {}), by_r.get(evidence_id, {}))
        if not e:
            errors.append(f"{evidence_id}: evidence row missing")
            continue
        if not a or not c or not r:
            errors.append(f"{evidence_id}: source audit, claim support, or batch review missing")
            continue
        if e.get("PMID") != pmid or a.get("PMID") != pmid or c.get("PMID") != pmid or r.get("PMID") != pmid:
            errors.append(f"{evidence_id}: PMID references disagree")
        if any(row.get("DOI", "").lower() != doi.lower() for row in (e, a, r)):
            errors.append(f"{evidence_id}: DOI references disagree with verified metadata")
        if a.get("Verification_Level") != "1" or "V19_TIER_1_FULL_TEXT_REVIEWED" not in a.get("Audit_Disposition", ""):
            errors.append(f"{evidence_id}: Tier 1 full-text verification is missing")
        if a.get("Verification_Date") != "2026-11-03" or r.get("Review_Date") != "2026-11-03":
            errors.append(f"{evidence_id}: source review date missing or incorrect")
        if not e.get("Source_URL", "").startswith("https://") or e.get("Source_URL") != a.get("Source_URL") or e.get("Source_URL") != r.get("Primary_Source_URL"):
            errors.append(f"{evidence_id}: primary source URL missing or inconsistent")
        if not e.get("Source_Locator") or e.get("Source_Locator") != a.get("Source_Locator") or e.get("Source_Locator") != c.get("Source_Locator") or e.get("Source_Locator") != r.get("Source_Locator"):
            errors.append(f"{evidence_id}: source locator missing or inconsistent")
        if e.get("Source_Cache") != EXPECTED_CACHES[pmid] or a.get("Source_Cache") != EXPECTED_CACHES[pmid] or r.get("Local_Metadata_Cache") != EXPECTED_CACHES[pmid]:
            errors.append(f"{evidence_id}: local metadata-cache locator is not repaired or consistent")
        cache_path = root / EXPECTED_CACHES[pmid]
        if not cache_path.is_file():
            errors.append(f"{evidence_id}: archived MED metadata cache does not exist")
        else:
            payload = json.loads(cache_path.read_text(encoding="utf-8-sig"))
            results = payload.get("resultList", {}).get("result", [])
            if not any(str(item.get("pmid", item.get("id", ""))) == pmid for item in results):
                errors.append(f"{evidence_id}: archived MED metadata cache does not identify its PMID")
        if not a.get("Endpoint_Verified") or not a.get("Numerical_Outcome_Verified"):
            errors.append(f"{evidence_id}: record-specific source verification is incomplete")
        if r.get("Verified_Outcome") != e.get("Quantitative_Outcome"):
            errors.append(f"{evidence_id}: reviewed outcome differs from evidence record")
        for marker in MARKERS[evidence_id]:
            if marker.lower() not in e.get("Quantitative_Outcome", "").lower():
                errors.append(f"{evidence_id}: source outcome or limitation marker missing: {marker}")
        if not e.get("Limitations") or not r.get("Remaining_Limitation"):
            errors.append(f"{evidence_id}: source limitations are missing")
        if evidence_id in {"SB-0138", "SB-0139"}:
            if not e.get("Quantitative_Outcome", "").startswith("Qualitative outcome only"):
                errors.append(f"{evidence_id}: graph-only CI must not be presented as exact numeric data")
            if e.get("Outcome") != "context_dependent_synergy_and_antagonism_reported":
                errors.append(f"{evidence_id}: LoVo concentration-dependent antagonism must remain explicit")
        if evidence_id == "SB-0183" and "V19-W07" not in e.get("Dose", ""):
            errors.append("SB-0183: conflicting dosing frequency and start time must remain visible in the regimen")

    for pmid, rel in EXPECTED_CACHES.items():
        row = pub_by_pmid.get(pmid, {})
        if not row or row.get("Source") != rel:
            errors.append(f"PMID {pmid}: bibliography metadata source path is not repaired")
        if pmid == "26396928" and (row.get("DOI") or row.get("DOI_Status") != "Not supplied in current MED; not invented"):
            errors.append("PMID 26396928: unsupported DOI must remain blank and documented")

    baseline = {r.get("Evidence_ID", ""): r for r in baseline_evidence}
    baseline_blanks = {eid for eid, row in baseline.items() if not row.get("Quantitative_Outcome", "").strip()}
    if len(baseline_blanks) != 90 or not set(BATCH4) <= baseline_blanks:
        errors.append("Batch 004 must target four of the 90 immutable V18 blank outcomes")
    if sum(not r.get("Quantitative_Outcome", "").strip() for r in evidence) > 65:
        errors.append("expected no more than 65 blank outcome fields after Batch 005")

    warning_ids = [r.get("Warning_ID", "") for r in warnings]
    warning_audit_ids = [r.get("Warning_ID", "") for r in warning_audit]
    baseline_warning_ids = {r.get("Warning_ID", "") for r in baseline_warnings}
    if len(warning_ids) != len(set(warning_ids)):
        errors.append("duplicate warning IDs")
    if len(warning_audit_ids) != len(set(warning_audit_ids)) or set(warning_ids) != set(warning_audit_ids):
        errors.append("warning audit and ledger must match uniquely")
    if len(baseline_warning_ids) != 70 or not baseline_warning_ids <= set(warning_ids):
        errors.append("all 70 inherited V18 warnings must be preserved")
    if len(warning_ids) < 80 or not NEW_WARNINGS <= set(warning_ids) or not {f"V19-W{i:02d}" for i in range(1, 11)} <= set(warning_ids):
        errors.append("warning ledger must preserve 70 inherited and V19-W01 through V19-W10")
    ledger_by_id = {r.get("Warning_ID", ""): r for r in warnings}
    audit_by_id = {r.get("Warning_ID", ""): r for r in warning_audit}
    for wid, row in ledger_by_id.items():
        if row.get("Audit_Status") != audit_by_id[wid].get("V19_Status"):
            errors.append(f"{wid}: warning ledger and warning audit status differ")
    for wid in {"V19-W07", "V19-W08", "V19-W09"}:
        row = ledger_by_id.get(wid, {})
        if row.get("Audit_Status") != "NEEDS_MANUAL_REVIEW" or not row.get("Remaining_Limitations") or not row.get("Audit_Verification_Reference"):
            errors.append(f"{wid}: scientific source discrepancy must remain open with evidence")
    resolved = ledger_by_id.get("V19-W10", {})
    if resolved.get("Audit_Status") != "RESOLVED":
        errors.append("V19-W10: demonstrably repaired cache locator warning must remain resolved")
    for col in ("After", "Resolution_Source", "Audit_Rationale", "Audit_Verification_Reference"):
        if not resolved.get(col, "").strip():
            errors.append(f"V19-W10: resolved warning lacks {col}")
    if resolved.get("Audit_Dependencies", "").startswith("Source/author clarification"):
        errors.append("V19-W10: resolved cache warning cannot claim unresolved source dependency")
    return sorted(set(errors))


def validate(root: Path) -> list[str]:
    root = Path(root).resolve()
    parent = root.parent / "StageB_V18_20261103"
    if not parent.is_dir():
        return ["immutable V18 parent release unavailable"]
    return validate_records(
        root,
        read_rows(root, "data/interaction_evidence.csv"),
        read_rows(root, "provenance/source_audit.csv"),
        read_rows(root, "provenance/claim_support_and_verification.csv"),
        read_rows(root, "data/warning_ledger.csv"),
        read_rows(root, "validation/V19_warning_audit.csv"),
        read_rows(root, "validation/V19_batch_004_review.csv"),
        read_rows(root, "data/publication_bibliography.csv"),
        read_rows(parent, "data/interaction_evidence.csv"),
        read_rows(parent, "data/warning_ledger.csv"),
    )


if __name__ == "__main__":
    release = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    errors = validate(release)
    result = {
        "release": release.resolve().name, "batch": "V19-004",
        "status": "PASS" if not errors else "FAIL", "reviewed_records": 4,
        "qualitative_only_outcomes": 2, "source_supported_quantitative_outcomes": 2,
        "new_warnings": 4, "resolved_locator_warning": "V19-W10",
        "errors": errors,
    }
    (release / "validation/V19_batch_004_integrity_results.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(bool(errors))
