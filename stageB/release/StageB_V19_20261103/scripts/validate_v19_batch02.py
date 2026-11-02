"""Record-level integrity checks for the V19-002 source-review batch."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

BATCH2 = {
    "SB-0018": ("22725836", "10.1111/j.1365-2125.2012.04364.x"),
    "SB-0019": ("22725836", "10.1111/j.1365-2125.2012.04364.x"),
    "SB-0020": ("22725836", "10.1111/j.1365-2125.2012.04364.x"),
    "SB-0090": ("33435470", "10.3390/pharmaceutics13010083"),
    "SB-0091": ("33435470", "10.3390/pharmaceutics13010083"),
    "SB-0092": ("33435470", "10.3390/pharmaceutics13010083"),
    "SB-0101": ("22114872", "10.1111/j.1365-2125.2011.04150.x"),
    "SB-0147": ("29908072", "10.1111/bph.14393"),
}
NEW_WARNINGS = {"V19-W02", "V19-W03", "V19-W04"}
REQUIRED_MARKERS = {
    "SB-0018": ["10.1 ± 6.1", "0.97 (90% CI 0.79–1.20)", "1′-OH-midazolam", "p=0.03"],
    "SB-0019": ["75.4 ± 21.7", "0.97 (90% CI 0.93–1.00)", "4-OH-flurbiprofen", "p=0.05"],
    "SB-0020": ["3.4 ± 0.8", "4.0 ± 1.2", "0.98 (90% CI 0.91–1.05)", "V19-W02"],
    "SB-0090": ["1.51 ± 0.11", "3.30 ± 0.06"],
    "SB-0091": ["17.8 ± 1.3", "25.8 ± 4.5", "V19-W03"],
    "SB-0092": ["7.74 ± 0.73", "15.6 ± 4.7", "3.17 ± 0.95"],
    "SB-0101": ["354.6 ± 89.6", "437.8 ± 118.6", "82% (95% CI 75–89)", "V19-W04"],
    "SB-0147": ["41.3 ± 10.4", "151.8 ± 14.8", "3.7-fold"],
}
REQUIRED_DOSE_MARKERS = {
    "SB-0090": ["0.2 mg/kg", "10 mg/kg"],
    "SB-0091": ["3 mg/kg", "10 mg/kg"],
    "SB-0092": ["1 mg/kg", "10 mg/kg"],
    "SB-0147": ["2.6 mg/kg", "20 mg/kg"],
}


def read(root: Path, rel: str) -> list[dict[str, str]]:
    with (root / rel).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_records(
    root: Path,
    evidence: list[dict[str, str]],
    audits: list[dict[str, str]],
    warnings: list[dict[str, str]],
    warning_audit: list[dict[str, str]],
    review: list[dict[str, str]],
    baseline_evidence: list[dict[str, str]],
    baseline_warnings: list[dict[str, str]],
) -> list[str]:
    root = Path(root).resolve()
    errors: list[str] = []
    eids = [r.get("Evidence_ID", "") for r in evidence]
    aids = [r.get("Evidence_ID", "") for r in audits]
    rids = [r.get("Evidence_ID", "") for r in review]
    if len(eids) != len(set(eids)):
        errors.append("duplicate evidence IDs")
    if set(eids) != set(aids):
        errors.append("source-audit coverage does not exactly match evidence")
    if set(rids) != set(BATCH2) or len(rids) != len(set(rids)):
        errors.append("V19-002 review rows must exactly cover the eight batch records once")
    evidence_by_id = {r["Evidence_ID"]: r for r in evidence}
    audits_by_id = {r["Evidence_ID"]: r for r in audits}
    reviews_by_id = {r["Evidence_ID"]: r for r in review}
    for evidence_id, (pmid, doi) in BATCH2.items():
        e = evidence_by_id.get(evidence_id, {})
        a = audits_by_id.get(evidence_id, {})
        v = reviews_by_id.get(evidence_id, {})
        if not e:
            errors.append(f"{evidence_id}: evidence record missing")
            continue
        if a.get("PMID") != pmid or a.get("DOI", "").lower() != doi.lower():
            errors.append(f"{evidence_id}: primary-source PMID/DOI mismatch")
        if a.get("Verification_Level") != "1" or "V19_TIER_1_FULL_TEXT_REVIEWED" not in a.get("Audit_Disposition", ""):
            errors.append(f"{evidence_id}: full-text verification tier/disposition missing")
        if not a.get("Verification_Date") or a.get("Verification_Date") != "2026-11-03":
            errors.append(f"{evidence_id}: source-review date missing or incorrect")
        if not a.get("Source_URL") or a.get("Source_URL") != e.get("Source_URL"):
            errors.append(f"{evidence_id}: primary-source URL is missing or inconsistent")
        if not a.get("Source_Locator") or a.get("Source_Locator") != e.get("Source_Locator"):
            errors.append(f"{evidence_id}: record-level source locator is missing or inconsistent")
        if not e.get("Quantitative_Outcome", "").strip():
            errors.append(f"{evidence_id}: inherited blank quantitative outcome was not adjudicated")
        for marker in REQUIRED_MARKERS[evidence_id]:
            if marker not in e.get("Quantitative_Outcome", ""):
                errors.append(f"{evidence_id}: required source-supported value/limitation missing: {marker}")
        for marker in REQUIRED_DOSE_MARKERS.get(evidence_id, []):
            if marker not in e.get("Dose", ""):
                errors.append(f"{evidence_id}: required source-supported dose missing from Dose field: {marker}")
        if not v:
            errors.append(f"{evidence_id}: batch review disposition missing")
            continue
        if v.get("PMID") != pmid or v.get("DOI", "").lower() != doi.lower():
            errors.append(f"{evidence_id}: batch-review citation mismatch")
        if v.get("Verification_Tier") != "1" or v.get("Review_Date") != "2026-11-03":
            errors.append(f"{evidence_id}: batch-review tier/date mismatch")
        if v.get("Primary_Source_URL") != e.get("Source_URL") or v.get("Source_Locator") != e.get("Source_Locator"):
            errors.append(f"{evidence_id}: batch review does not point to the evidence source and locator")
        if v.get("Verified_Outcome") != e.get("Quantitative_Outcome"):
            errors.append(f"{evidence_id}: batch review and evidence outcome differ")
        if not any(marker in v.get("Source_Access_Status", "").lower() for marker in ("full text", "full-text")):
            errors.append(f"{evidence_id}: full-text access method is not documented")
        cache_rel = a.get("Source_Cache", "")
        cache_file = root / "provenance" / cache_rel
        if not cache_rel or not cache_file.is_file():
            errors.append(f"{evidence_id}: local bibliographic metadata cache unavailable")
        else:
            cache = cache_file.read_text(encoding="utf-8", errors="replace").lower()
            if pmid not in cache or doi.lower() not in cache:
                errors.append(f"{evidence_id}: metadata cache does not contain the asserted PMID/DOI")
        if not a.get("Endpoint_Verified") or not a.get("Numerical_Outcome_Verified"):
            errors.append(f"{evidence_id}: record-level endpoint/outcome verification trail incomplete")

    baseline_blank = {r.get("Evidence_ID", "") for r in baseline_evidence if not r.get("Quantitative_Outcome", "").strip()}
    if len(baseline_blank) != 90:
        errors.append(f"V18 baseline blank outcomes expected 90, found {len(baseline_blank)}")
    if not set(BATCH2) <= baseline_blank:
        errors.append("V19-002 includes records that were not blank outcomes in V18 or omitted a source-supported recovery")
    current_blank = sum(not r.get("Quantitative_Outcome", "").strip() for r in evidence)
    if current_blank > 65:
        errors.append(f"after V19-001 through V19-005, blank outcomes must be no more than 65, found {current_blank}")

    warning_ids = [r.get("Warning_ID", "") for r in warnings]
    audit_ids = [r.get("Warning_ID", "") for r in warning_audit]
    if len(warning_ids) != len(set(warning_ids)):
        errors.append("duplicate warning IDs")
    if len(audit_ids) != len(set(audit_ids)) or set(warning_ids) != set(audit_ids):
        errors.append("warning audit coverage does not exactly match warning ledger")
    baseline_ids = {r.get("Warning_ID", "") for r in baseline_warnings}
    if not baseline_ids <= set(warning_ids) or len(baseline_ids) != 70:
        errors.append("V18 warning history is incomplete or has an unexpected baseline count")
    if len(warning_ids) < 80 or not {f"V19-W{i:02d}" for i in range(1, 11)} <= set(warning_ids):
        errors.append("V19 warning ledger must preserve 70 inherited rows and V19-W01 through V19-W10")
    ledger = {r["Warning_ID"]: r for r in warnings}
    audit = {r["Warning_ID"]: r for r in warning_audit}
    for wid, row in ledger.items():
        if row.get("Audit_Status") != audit[wid].get("V19_Status"):
            errors.append(f"{wid}: warning ledger and V19 audit status differ")
    for wid in NEW_WARNINGS | {"V19-W05", "V19-W06"}:
        if ledger.get(wid, {}).get("Audit_Status") != "NEEDS_MANUAL_REVIEW":
            errors.append(f"{wid}: unsupported closure or downgrade of an open scientific reporting warning")
        if not ledger.get(wid, {}).get("Remaining_Limitations"):
            errors.append(f"{wid}: open warning lacks a documented limitation")
    if ledger.get("V5-source_reporting_units", {}).get("Audit_Status") != "PARTIALLY_RESOLVED":
        errors.append("V5-source_reporting_units must remain partially resolved with two affected pairs outstanding")
    if ledger.get("V19-W01", {}).get("Audit_Status") != "STILL_VALID":
        errors.append("V19-W01 scientific uncertainty must remain open")
    for wid in ("V19-W07", "V19-W08", "V19-W09"):
        if ledger.get(wid, {}).get("Audit_Status") != "NEEDS_MANUAL_REVIEW":
            errors.append(f"{wid}: source discrepancy must remain open")
    if ledger.get("V19-W10", {}).get("Audit_Status") != "RESOLVED":
        errors.append("V19-W10: repaired metadata locator warning must be resolved")
    return sorted(set(errors))


def validate(root: Path) -> list[str]:
    root = Path(root).resolve()
    parent = root.parent / "StageB_V18_20261103"
    if not parent.is_dir():
        return ["immutable V18 parent release unavailable for warning/outcome preservation checks"]
    return validate_records(
        root,
        read(root, "data/interaction_evidence.csv"),
        read(root, "provenance/source_audit.csv"),
        read(root, "data/warning_ledger.csv"),
        read(root, "validation/V19_warning_audit.csv"),
        read(root, "validation/V19_batch_002_review.csv"),
        read(parent, "data/interaction_evidence.csv"),
        read(parent, "data/warning_ledger.csv"),
    )


if __name__ == "__main__":
    release = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    errors = validate(release)
    result = {"release": release.name, "batch": "V19-002", "status": "PASS" if not errors else "FAIL", "reviewed_records": len(BATCH2), "new_blank_outcomes_recovered": len(BATCH2), "errors": errors}
    output = release / "validation/V19_batch_002_integrity_results.json"
    output.write_text(__import__("json").dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(__import__("json").dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(bool(errors))
