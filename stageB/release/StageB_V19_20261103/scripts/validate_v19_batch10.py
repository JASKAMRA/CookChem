"""Validate V19-010 Table 1/2 full-text outcomes and open FICI-boundary warning."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

PMID = "38958374"
DOI = "10.4274/tpd.galenos.2024.91855"
TITLE = "Investigation of the Antitrichomonal Activity of Cinnamaldehyde, Carvacrol and Thymol and Synergy with Metronidazole."
URL = "https://www.turkiyeparazitolderg.org/articles/investigation-of-the-antitrichomonal-activity-of-cinnamaldehyde-carvacrol-and-thymol-and-synergy-with-metronidazole/doi/tpd.galenos.2024.91855"
CACHE = "history/rebuild_artifacts/bf25a8a45c2a8835e33aae42011ebeaa498124998e16f9a7cc6709d57a1e463b_pmid_38958374.json"
TARGETS = {
    "SB-0135": {"compound": "Cinnamaldehyde", "markers": ["3.9/31.25 µg/mL", "1.8/7.81 µg/mL", "3.9/15.62 µg/mL", "ΣFICI=0.374", "labeled “Synergy"]},
    "SB-0136": {"compound": "Carvacrol", "markers": ["15.62/125 µg/mL", "31.25/250 µg/mL", "62.5/250 µg/mL", "ΣFICI=0.187", "labeled “Synergy"]},
    "SB-0137": {"compound": "Thymol", "markers": ["62.5/500 µg/mL", "15.62/125 µg/mL", "125/500 µg/mL", "ΣFICI=0.750", "labeled “Partial synergy", "both stated intervals"]},
}


def rows(root: Path, rel: str) -> list[dict[str, str]]:
    with (root / rel).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_records(root: Path, evidence, audits, claims, warnings, warning_audit,
                     review, bibliography, baseline_evidence, baseline_warnings) -> list[str]:
    root = Path(root).resolve()
    errors: list[str] = []
    ids = [r.get("Evidence_ID", "") for r in evidence]
    audit_ids = [r.get("Evidence_ID", "") for r in audits]
    claim_ids = [r.get("Evidence_ID", "") for r in claims]
    review_ids = [r.get("Evidence_ID", "") for r in review]
    targets = set(TARGETS)
    if len(ids) != len(set(ids)):
        errors.append("duplicate evidence IDs")
    if len(audit_ids) != len(set(audit_ids)) or set(audit_ids) != set(ids):
        errors.append("source audit must uniquely cover all evidence records")
    if len(claim_ids) != len(set(claim_ids)) or not targets <= set(claim_ids):
        errors.append("claim support must uniquely include all Batch 010 records")
    if len(review_ids) != len(set(review_ids)) or set(review_ids) != targets:
        errors.append("Batch 010 review must cover exactly SB-0135 through SB-0137")

    ev = {r.get("Evidence_ID", ""): r for r in evidence}
    au = {r.get("Evidence_ID", ""): r for r in audits}
    cl = {r.get("Evidence_ID", ""): r for r in claims}
    rv = {r.get("Evidence_ID", ""): r for r in review}
    pubs = {r.get("PMID", ""): r for r in bibliography}
    for eid, spec in TARGETS.items():
        e, a, c, r = ev.get(eid, {}), au.get(eid, {}), cl.get(eid, {}), rv.get(eid, {})
        if not all((e, a, c, r)):
            errors.append(f"{eid}: evidence/source-audit/claim-support/review row missing")
            continue
        if e.get("Compound") != spec["compound"] or e.get("Drug") != "Metronidazole":
            errors.append(f"{eid}: compound/drug assignment mismatch")
        if any(row.get("PMID") != PMID for row in (e, a, c, r)):
            errors.append(f"{eid}: PMID mismatch")
        if any(row.get("DOI", "").lower() != DOI.lower() for row in (e, a, r)):
            errors.append(f"{eid}: DOI mismatch")
        if e.get("Evidence_Type") != "In vitro" or e.get("Evidence_Level") != "compound":
            errors.append(f"{eid}: evidence must remain in-vitro individual-compound evidence")
        if a.get("Verification_Level") != "1" or "V19_TIER_1_FULL_TEXT_REVIEWED" not in a.get("Audit_Disposition", ""):
            errors.append(f"{eid}: original publisher full text must remain Tier 1")
        if a.get("Verification_Date") != "2026-11-03" or r.get("Review_Date") != "2026-11-03":
            errors.append(f"{eid}: review date missing or incorrect")
        if any(row.get("Source_URL") != URL for row in (e, a)) or r.get("Primary_Source_URL") != URL:
            errors.append(f"{eid}: original publisher URL mismatch")
        if any(row.get("Source_Cache") != CACHE for row in (e, a)) or r.get("Local_Metadata_Cache") != CACHE:
            errors.append(f"{eid}: local MED metadata locator mismatch")
        locator = e.get("Source_Locator", "")
        if not locator or any(row.get("Source_Locator") != locator for row in (a, c, r)):
            errors.append(f"{eid}: table/source locator missing or inconsistent")
        outcome = e.get("Quantitative_Outcome", "")
        if not outcome.strip() or outcome != r.get("Verified_Outcome"):
            errors.append(f"{eid}: outcome is blank or differs from review record")
        for marker in spec["markers"]:
            if marker.lower() not in outcome.lower():
                errors.append(f"{eid}: source estimate or interpretation missing: {marker}")
        if "no human treatment" not in e.get("Limitations", "").lower() or e.get("Clinical_Extrapolation") != "No clinical extrapolation":
            errors.append(f"{eid}: in-vitro result has unsupported human extrapolation")
        if "no human participants were studied" not in e.get("Population", "").lower():
            errors.append(f"{eid}: isolate model is not distinguished from human-participant evidence")
        if eid == "SB-0137" and "SOURCE_THRESHOLD_LIMITATION_RETAINED" not in a.get("Audit_Disposition", ""):
            errors.append("SB-0137: exact 0.750 threshold conflict was not preserved in audit disposition")

    cache_path = root / CACHE
    if not cache_path.is_file():
        errors.append("archived MED metadata JSON is missing")
    else:
        try:
            payload = json.loads(cache_path.read_text(encoding="utf-8-sig"))
            items = payload.get("resultList", {}).get("result", [])
            if not any(str(item.get("pmid", item.get("id", ""))) == PMID and str(item.get("doi", "")).lower() == DOI.lower() for item in items):
                errors.append("archived MED JSON does not verify PMID and DOI")
        except (OSError, json.JSONDecodeError):
            errors.append("archived MED metadata JSON is unreadable")
    pub = pubs.get(PMID, {})
    if pub.get("Source") != CACHE or pub.get("DOI", "").lower() != DOI.lower() or pub.get("Title") != TITLE:
        errors.append("bibliography title, DOI or source path is incorrect")

    baseline = {r.get("Evidence_ID", ""): r for r in baseline_evidence}
    baseline_blank = {eid for eid, row in baseline.items() if not row.get("Quantitative_Outcome", "").strip()}
    if len(baseline_blank) != 90 or not targets <= baseline_blank:
        errors.append("Batch 010 targets must be inherited V18 blank outcomes")
    if any(not ev[eid].get("Quantitative_Outcome", "").strip() for eid in targets):
        errors.append("all three full-text outcomes must remain populated")
    current_blanks = sum(not row.get("Quantitative_Outcome", "").strip() for row in evidence)
    if current_blanks > 44:
        errors.append(f"expected no more than 44 quantitative blanks after Batch 010; found {current_blanks}")

    warning_ids = [r.get("Warning_ID", "") for r in warnings]
    audit_warning_ids = [r.get("Warning_ID", "") for r in warning_audit]
    inherited = {r.get("Warning_ID", "") for r in baseline_warnings}
    if len(warnings) < 86 or len(warning_ids) != len(set(warning_ids)):
        errors.append("warning ledger must retain all inherited warnings and V19-W01 through V19-W16 exactly once")
    if len(inherited) != 70 or not inherited <= set(warning_ids):
        errors.append("all 70 inherited V18 warning IDs must remain present")
    if len(audit_warning_ids) != len(set(audit_warning_ids)) or set(warning_ids) != set(audit_warning_ids):
        errors.append("warning ledger and V19 warning audit must match uniquely")
    if not {f"V19-W{i:02d}" for i in range(1, 17)} <= set(warning_ids):
        errors.append("one or more V19 warning IDs through V19-W16 are missing")
    by_w = {r.get("Warning_ID", ""): r for r in warnings}
    by_wa = {r.get("Warning_ID", ""): r for r in warning_audit}
    for wid, row in by_w.items():
        if row.get("Audit_Status") != by_wa.get(wid, {}).get("V19_Status"):
            errors.append(f"{wid}: warning status mismatch")
    w10 = by_w.get("V19-W10", {})
    if w10.get("Audit_Status") != "RESOLVED" or "38958374" not in w10.get("Affected", "") or "38958374" not in w10.get("Audit_Verification_Reference", ""):
        errors.append("V19-W10 does not document and verify the Batch 010 cache repair")
    if "V19-010" not in by_wa.get("V19-W10", {}).get("V19_Recheck_Status", ""):
        errors.append("V19-W10 audit lost the Batch 010 repair history")
    w16 = by_w.get("V19-W16", {})
    if w16.get("Audit_Status") != "NEEDS_MANUAL_REVIEW" or "SB-0137" not in w16.get("Affected", ""):
        errors.append("V19-W16 must remain open and point to the thymol boundary record")
    if "0.750" not in w16.get("Description", "") or not w16.get("Audit_Verification_Reference", "").strip():
        errors.append("V19-W16 lacks the exact boundary value or source verification reference")
    for wid in ("V19-W11", "V19-W12", "V19-W13", "V19-W15"):
        if by_w.get(wid, {}).get("Audit_Status") != "NEEDS_MANUAL_REVIEW":
            errors.append(f"{wid}: unresolved scientific issue must remain open")
    return sorted(set(errors))


def validate(root: Path) -> list[str]:
    root = Path(root).resolve()
    parent = root.parent / "StageB_V18_20261103"
    if not parent.is_dir():
        return ["immutable V18 parent release unavailable"]
    try:
        return validate_records(
            root,
            rows(root, "data/interaction_evidence.csv"),
            rows(root, "provenance/source_audit.csv"),
            rows(root, "provenance/claim_support_and_verification.csv"),
            rows(root, "data/warning_ledger.csv"),
            rows(root, "validation/V19_warning_audit.csv"),
            rows(root, "validation/V19_batch_010_review.csv"),
            rows(root, "data/publication_bibliography.csv"),
            rows(parent, "data/interaction_evidence.csv"),
            rows(parent, "data/warning_ledger.csv"),
        )
    except (OSError, csv.Error) as exc:
        return [f"validation input unreadable: {exc}"]


if __name__ == "__main__":
    release = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    errors = validate(release)
    result = {
        "release": release.resolve().name, "batch": "V19-010", "status": "PASS" if not errors else "FAIL",
        "reviewed_records": 3, "source_tier": 1, "quantitative_outcomes_recovered": 3,
        "blank_outcomes_remaining": sum(not r.get("Quantitative_Outcome", "").strip() for r in rows(release, "data/interaction_evidence.csv")),
        "metadata_cache_repair_pmids": [PMID], "open_warning_ids": ["V19-W16"], "errors": errors,
    }
    (release / "validation/V19_batch_010_integrity_results.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(bool(errors))
