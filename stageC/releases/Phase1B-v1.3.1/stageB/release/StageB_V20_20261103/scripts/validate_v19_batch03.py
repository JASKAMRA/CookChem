"""Validate V19-003 source review, extracted outcomes, and warning lifecycle."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

BATCH3 = {
    "SB-0165": ("26360766", "10.1371/journal.pone.0137751"),
    "SB-0166": ("26360766", "10.1371/journal.pone.0137751"),
    "SB-0167": ("26360766", "10.1371/journal.pone.0137751"),
    "SB-0168": ("26360766", "10.1371/journal.pone.0137751"),
    "SB-0107": ("26884726", "10.1186/s12935-016-0288-3"),
    "SB-0108": ("26884726", "10.1186/s12935-016-0288-3"),
    "SB-0109": ("26884726", "10.1186/s12935-016-0288-3"),
}
OUTCOME_MARKERS = {
    "SB-0165": ["2.00 μg/mL", "0.50 μg/mL", "<0.313", "0.375", "V19-W05"],
    "SB-0166": ["16.00 μg/mL", "4.00 μg/mL", "<0.375", "0.313", "V19-W05"],
    "SB-0167": ["512.00 μg/mL", "128.00 μg/mL", "<0.750", "no interaction"],
    "SB-0168": ["8.00 μg/mL", "1.00 μg/mL", "<0.625", "no interaction"],
    "SB-0107": ["Qualitative outcome only", "Figure S1(c)", "no values have been estimated"],
    "SB-0108": ["Qualitative outcome only", "Figure S1(a)", "no values have been estimated"],
    "SB-0109": ["Qualitative outcome only", "Figure S1(b)", "no values have been estimated"],
}
CACHE = "source_archive/8ef165a5494528bddeeff5990461fc72e52601f9d6e50b7e183b7bba16b2a307_pubmed_esummary_all_v10pmids.json"


def rows(root: Path, rel: str) -> list[dict[str, str]]:
    with (root / rel).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_records(
    root: Path,
    evidence: list[dict[str, str]],
    audits: list[dict[str, str]],
    claims: list[dict[str, str]],
    warnings: list[dict[str, str]],
    warning_audit: list[dict[str, str]],
    review: list[dict[str, str]],
    baseline_evidence: list[dict[str, str]],
    baseline_warnings: list[dict[str, str]],
) -> list[str]:
    root = Path(root).resolve()
    errors: list[str] = []
    evidence_ids = [r.get("Evidence_ID", "") for r in evidence]
    audit_ids = [r.get("Evidence_ID", "") for r in audits]
    claim_ids = [r.get("Evidence_ID", "") for r in claims]
    review_ids = [r.get("Evidence_ID", "") for r in review]
    if len(evidence_ids) != len(set(evidence_ids)):
        errors.append("duplicate evidence IDs")
    if len(audit_ids) != len(set(audit_ids)) or set(audit_ids) != set(evidence_ids):
        errors.append("source-audit rows must uniquely cover all evidence records")
    if len(claim_ids) != len(set(claim_ids)) or not set(BATCH3) <= set(claim_ids):
        errors.append("claim-support rows must uniquely include every Batch 003 evidence record")
    if len(review_ids) != len(set(review_ids)) or set(review_ids) != set(BATCH3):
        errors.append("Batch 003 review must cover all seven records exactly once")

    by_e = {r["Evidence_ID"]: r for r in evidence}
    by_a = {r["Evidence_ID"]: r for r in audits}
    by_c = {r["Evidence_ID"]: r for r in claims}
    by_r = {r["Evidence_ID"]: r for r in review}
    cache_file = root / "provenance" / CACHE
    if not cache_file.is_file():
        errors.append("inherited PubMed metadata cache for both studies is missing")
        cache_text = ""
    else:
        cache_text = cache_file.read_text(encoding="utf-8", errors="replace").lower()

    for evidence_id, (pmid, doi) in BATCH3.items():
        e, a, c, v = by_e.get(evidence_id, {}), by_a.get(evidence_id, {}), by_c.get(evidence_id, {}), by_r.get(evidence_id, {})
        if not e:
            errors.append(f"{evidence_id}: evidence record missing")
            continue
        for label, row in (("source audit", a), ("claim support", c), ("batch review", v)):
            if not row:
                errors.append(f"{evidence_id}: {label} record missing")
        if a.get("PMID") != pmid or a.get("DOI", "").lower() != doi.lower():
            errors.append(f"{evidence_id}: primary source PMID/DOI mismatch")
        if a.get("Verification_Level") != "1" or "V19_TIER_1_FULL_TEXT_REVIEWED" not in a.get("Audit_Disposition", ""):
            errors.append(f"{evidence_id}: full-text source tier/disposition missing")
        if a.get("Verification_Date") != "2026-11-03":
            errors.append(f"{evidence_id}: source review date missing or wrong")
        if a.get("Source_URL") != e.get("Source_URL") or a.get("Source_Locator") != e.get("Source_Locator"):
            errors.append(f"{evidence_id}: evidence and source-audit locator/URL differ")
        if e.get("Source_Cache") != "provenance/" + CACHE or a.get("Source_Cache") != CACHE:
            errors.append(f"{evidence_id}: local metadata-cache paths are inconsistent")
        if pmid.lower() not in cache_text or doi.lower() not in cache_text:
            errors.append(f"{evidence_id}: local metadata cache lacks PMID/DOI")
        if not a.get("Endpoint_Verified") or not a.get("Numerical_Outcome_Verified"):
            errors.append(f"{evidence_id}: record-specific verification evidence is incomplete")
        if v.get("Verification_Tier") != "1" or v.get("Review_Date") != "2026-11-03":
            errors.append(f"{evidence_id}: batch-review tier/date mismatch")
        if v.get("PMID") != pmid or v.get("DOI", "").lower() != doi.lower():
            errors.append(f"{evidence_id}: batch-review citation mismatch")
        if v.get("Primary_Source_URL") != e.get("Source_URL") or v.get("Source_Locator") != e.get("Source_Locator"):
            errors.append(f"{evidence_id}: batch review source locator/URL drift")
        if v.get("Verified_Outcome") != e.get("Quantitative_Outcome"):
            errors.append(f"{evidence_id}: review and evidence outcome differ")
        if "full text" not in v.get("Source_Access_Status", "").lower() and "full-text" not in v.get("Source_Access_Status", "").lower():
            errors.append(f"{evidence_id}: source access method not documented")
        if c.get("Source_Locator") != e.get("Source_Locator") or not c.get("Numerical_Use"):
            errors.append(f"{evidence_id}: claim-support locator/use is missing or inconsistent")
        outcome = e.get("Quantitative_Outcome", "")
        for marker in OUTCOME_MARKERS[evidence_id]:
            if marker.lower() not in outcome.lower():
                errors.append(f"{evidence_id}: required source finding or limitation missing: {marker}")
        if evidence_id in {"SB-0107", "SB-0108", "SB-0109"}:
            if e.get("Evidence_Level") != "compound":
                errors.append(f"{evidence_id}: pure named fisetin reagent must not be classified as formulation")
            if "not reported" not in e.get("Dose", "").lower():
                errors.append(f"{evidence_id}: unsupported pair-specific dose must remain explicitly unreported")
            if e.get("Outcome") == "no_interaction_detected_under_tested_conditions":
                errors.append(f"{evidence_id}: no-synergy must not be encoded as no interaction")
        if evidence_id in {"SB-0165", "SB-0166"} and e.get("Outcome") != "source_reporting_discrepancy_pending_adjudication":
            errors.append(f"{evidence_id}: table/prose FICI conflict must remain flagged")
        if evidence_id in {"SB-0167", "SB-0168"} and e.get("Outcome") != "source_reported_no_interaction_threshold_uncertain":
            errors.append(f"{evidence_id}: reported no-interaction label must remain qualified by FICI upper-bound uncertainty")

    baseline_blanks = {r.get("Evidence_ID", "") for r in baseline_evidence if not r.get("Quantitative_Outcome", "").strip()}
    if len(baseline_blanks) != 90:
        errors.append(f"V18 baseline must have 90 blank outcomes; found {len(baseline_blanks)}")
    if not set(BATCH3) <= baseline_blanks:
        errors.append("Batch 003 includes a record that was not blank in the immutable V18 baseline")
    blank_count = sum(not r.get("Quantitative_Outcome", "").strip() for r in evidence)
    if blank_count > 65:
        errors.append(f"after Batch 005, blank outcome fields must be no more than 65; found {blank_count}")

    warning_ids = [r.get("Warning_ID", "") for r in warnings]
    audit_warning_ids = [r.get("Warning_ID", "") for r in warning_audit]
    baseline_warning_ids = {r.get("Warning_ID", "") for r in baseline_warnings}
    if len(warning_ids) != len(set(warning_ids)):
        errors.append("duplicate warning IDs")
    if len(audit_warning_ids) != len(set(audit_warning_ids)) or set(warning_ids) != set(audit_warning_ids):
        errors.append("warning audit must uniquely match every ledger warning")
    if len(baseline_warning_ids) != 70 or not baseline_warning_ids <= set(warning_ids):
        errors.append("all 70 inherited V18 warning IDs must be preserved")
    if len(warning_ids) < 80 or not {f"V19-W{i:02d}" for i in range(1, 11)} <= set(warning_ids):
        errors.append("warning ledger must contain 70 inherited IDs and V19-W01 through V19-W10")
    ledger = {r["Warning_ID"]: r for r in warnings}
    audit = {r["Warning_ID"]: r for r in warning_audit}
    for wid, row in ledger.items():
        if row.get("Audit_Status") != audit[wid].get("V19_Status"):
            errors.append(f"{wid}: warning ledger and V19 audit statuses differ")
    for wid in ("V19-W02", "V19-W03", "V19-W04", "V19-W05", "V19-W06"):
        if ledger.get(wid, {}).get("Audit_Status") != "NEEDS_MANUAL_REVIEW":
            errors.append(f"{wid}: scientific reporting discrepancy was unsupportedly closed or downgraded")
        if not ledger.get(wid, {}).get("Remaining_Limitations"):
            errors.append(f"{wid}: open warning lacks documented limitations")
    if ledger.get("V19-W05", {}).get("Affected") != "SB-0165 | SB-0166 | PMID:26360766 | Table 1 FICI reporting":
        errors.append("V19-W05 affected-record references are incorrect")
    if ledger.get("V19-W06", {}).get("Affected") != "SB-0167 | SB-0168 | PMID:26360766 | Table 1 FICI bounds":
        errors.append("V19-W06 affected-record references are incorrect")
    if ledger.get("V5-source_reporting_units", {}).get("Audit_Status") != "PARTIALLY_RESOLVED":
        errors.append("the rechecked aggregate V5 warning must remain partially resolved")
    return sorted(set(errors))


def validate(root: Path) -> list[str]:
    root = Path(root).resolve()
    parent = root.parent / "StageB_V18_20261103"
    if not parent.is_dir():
        return ["immutable V18 parent release unavailable"]
    return validate_records(
        root,
        rows(root, "data/interaction_evidence.csv"),
        rows(root, "provenance/source_audit.csv"),
        rows(root, "provenance/claim_support_and_verification.csv"),
        rows(root, "data/warning_ledger.csv"),
        rows(root, "validation/V19_warning_audit.csv"),
        rows(root, "validation/V19_batch_003_review.csv"),
        rows(parent, "data/interaction_evidence.csv"),
        rows(parent, "data/warning_ledger.csv"),
    )


if __name__ == "__main__":
    release = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    errors = validate(release)
    result = {
        "release": release.resolve().name, "batch": "V19-003",
        "status": "PASS" if not errors else "FAIL", "reviewed_records": len(BATCH3),
        "quantitative_values_recovered": 4, "qualitative_outcomes_dispositioned": 3,
        "errors": errors,
    }
    out = release / "validation/V19_batch_003_integrity_results.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(bool(errors))
