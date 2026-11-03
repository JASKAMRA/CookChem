"""Validate the V19-006 primary-source batch and its unresolved source warnings."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

TARGETS = {
    "SB-0110": ("27765854", "10.1158/1535-7163.MCT-16-0515", "in vitro", "0.45676", "0.74663", "0.72226"),
    "SB-0111": ("27765854", "10.1158/1535-7163.MCT-16-0515", "animal", "53%", "9 fold", "p=0.0001"),
    "SB-0163": ("27472952", "10.1007/s13238-016-0295-0", "in vitro", "0.51", "0.55", "0.54", "0.68"),
    "SB-0164": ("27472952", "10.1007/s13238-016-0295-0", "animal", "six mice per group", "p<0.01", "ALT", "AST"),
}
SOURCES = {
    "27765854": (
        "10.1158/1535-7163.MCT-16-0515",
        "Fisetin Enhances Chemotherapeutic Effect of Cabazitaxel against Human Prostate Cancer Cells.",
        "https://pmc.ncbi.nlm.nih.gov/articles/PMC5136329/",
        "history/rebuild_artifacts/43f5cd1be33be51aefb62daa7638bf637a4ff46b4f0b30a3d5ab2aaf6ee1cd6a_pmid_27765854.json",
    ),
    "27472952": (
        "10.1007/s13238-016-0295-0",
        "Ursolic acid synergistically enhances the therapeutic effects of oxaliplatin in colorectal cancer.",
        "https://pmc.ncbi.nlm.nih.gov/articles/PMC4980335/",
        "history/rebuild_artifacts/b478b7288bba8a68c28e9731c805f0784d57fc975d4fd6a5e0f5f276260f037b_pmid_27472952.json",
    ),
}
UA_XML = "history/rebuild_artifacts/8b2c4c41d05937901a522d5b8c9a758798aa825013204cf85a4a8775de94c06e_PMC4980335.xml"
UA_XML_SHA256 = "8b2c4c41d05937901a522d5b8c9a758798aa825013204cf85a4a8775de94c06e"
NEW_WARNINGS = {"V19-W11", "V19-W12", "V19-W13"}
MARKERS = {
    "SB-0110": ["79%", "53%", "78%", "0.45676", "0.74663", "0.72226", "0.9", "PC-3"],
    "SB-0111": ["14%", "36%", "53%", "9-fold", "22-fold", "20-fold", "32-fold", "2 weeks", "3 days"],
    "SB-0163": ["0.51", "0.55", "0.54", "0.68", "48 h", "10 μmol/L", "0.4 μmol/L", "about 30%"],
    "SB-0164": ["female", "n=6/group", "single 10 mg/kg", "day 50", "p<0.01", "ALT", "AST"],
}


def rows(root: Path, rel: str) -> list[dict[str, str]]:
    with (root / rel).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_records(root: Path, evidence, audits, claims, warnings, warning_audit,
                     review, bibliography, baseline_evidence, baseline_warnings) -> list[str]:
    root = Path(root).resolve()
    errors: list[str] = []
    eids = [r.get("Evidence_ID", "") for r in evidence]
    aids = [r.get("Evidence_ID", "") for r in audits]
    cids = [r.get("Evidence_ID", "") for r in claims]
    rids = [r.get("Evidence_ID", "") for r in review]
    if len(eids) != len(set(eids)):
        errors.append("duplicate evidence IDs")
    if len(aids) != len(set(aids)) or set(aids) != set(eids):
        errors.append("source audit must uniquely cover every evidence record")
    if len(cids) != len(set(cids)) or not set(TARGETS) <= set(cids):
        errors.append("claim support must uniquely include all four Batch 006 records")
    if len(rids) != len(set(rids)) or set(rids) != set(TARGETS):
        errors.append("Batch 006 review must cover exactly the four target records")

    by_e = {r.get("Evidence_ID", ""): r for r in evidence}
    by_a = {r.get("Evidence_ID", ""): r for r in audits}
    by_c = {r.get("Evidence_ID", ""): r for r in claims}
    by_r = {r.get("Evidence_ID", ""): r for r in review}
    pubs = {r.get("PMID", ""): r for r in bibliography}

    for eid, expected in TARGETS.items():
        pmid, doi, kind, *markers = expected
        e, a, c, r = by_e.get(eid, {}), by_a.get(eid, {}), by_c.get(eid, {}), by_r.get(eid, {})
        if not e or not a or not c or not r:
            errors.append(f"{eid}: evidence/source-audit/claim-support/review row missing")
            continue
        for label, row in (("evidence", e), ("source audit", a), ("claim support", c), ("batch review", r)):
            if row.get("PMID") != pmid:
                errors.append(f"{eid}: {label} PMID mismatch")
        if any(row.get("DOI", "").lower() != doi.lower() for row in (e, a, r)):
            errors.append(f"{eid}: DOI mismatch")
        url = SOURCES[pmid][2]
        cache = SOURCES[pmid][3]
        if a.get("Verification_Level") != "1" or "V19_TIER_1_FULL_TEXT_REVIEWED" not in a.get("Audit_Disposition", ""):
            errors.append(f"{eid}: source-audit is not Tier 1 full-text reviewed")
        if a.get("Verification_Date") != "2026-11-03" or r.get("Review_Date") != "2026-11-03":
            errors.append(f"{eid}: actual review date missing or incorrect")
        if e.get("Evidence_Type", "").lower() != kind or e.get("Evidence_Level") != "compound":
            errors.append(f"{eid}: evidence type/level does not match source model and named compound")
        if e.get("Source_URL") != url or a.get("Source_URL") != url or r.get("Primary_Source_URL") != url:
            errors.append(f"{eid}: primary full-text source URL mismatch")
        if e.get("Source_Cache") != cache or a.get("Source_Cache") != cache or r.get("Local_Metadata_Cache") != cache:
            errors.append(f"{eid}: local metadata-cache locator mismatch")
        locator = e.get("Source_Locator", "")
        if not locator or any(row.get("Source_Locator") != locator for row in (a, c, r)):
            errors.append(f"{eid}: full-text section/table/figure locator is missing or inconsistent")
        outcome = e.get("Quantitative_Outcome", "")
        if not outcome.strip() or r.get("Verified_Outcome") != outcome:
            errors.append(f"{eid}: source-supported outcome is blank or disagrees with batch review")
        for marker in MARKERS[eid]:
            if marker.lower() not in outcome.lower():
                errors.append(f"{eid}: primary-source result or limitation missing: {marker}")
        if not e.get("Limitations", "").strip() or not r.get("Remaining_Limitation", "").strip():
            errors.append(f"{eid}: preclinical/source limitations are missing")
        if "human" in e.get("Evidence_Type", "").lower():
            errors.append(f"{eid}: human classification is prohibited for these models")

    for pmid, (doi, title, _url, cache) in SOURCES.items():
        cache_path = root / cache
        if not cache_path.is_file():
            errors.append(f"PMID {pmid}: archived MED metadata JSON is missing")
        else:
            try:
                payload = json.loads(cache_path.read_text(encoding="utf-8-sig"))
                items = payload.get("resultList", {}).get("result", [])
                if not any(str(item.get("pmid", item.get("id", ""))) == pmid and str(item.get("doi", "")).lower() == doi.lower() for item in items):
                    errors.append(f"PMID {pmid}: metadata cache does not verify DOI")
            except (OSError, json.JSONDecodeError):
                errors.append(f"PMID {pmid}: metadata cache is unreadable")
        if pubs.get(pmid, {}).get("Source") != cache or pubs.get(pmid, {}).get("DOI", "").lower() != doi.lower():
            errors.append(f"PMID {pmid}: bibliography locator or DOI is incorrect")
        if pubs.get(pmid, {}).get("Title") != title:
            errors.append(f"PMID {pmid}: bibliography title does not match primary record")

    v19_xml = root / UA_XML
    if not v19_xml.is_file() or hashlib.sha256(v19_xml.read_bytes()).hexdigest() != UA_XML_SHA256:
        errors.append("PMC4980335 primary XML artifact is missing or its bytes differ from the hash-identified source")

    baseline = {r.get("Evidence_ID", ""): r for r in baseline_evidence}
    baseline_blank = {eid for eid, row in baseline.items() if not row.get("Quantitative_Outcome", "").strip()}
    if len(baseline_blank) != 90 or not set(TARGETS) <= baseline_blank:
        errors.append("Batch 006 targets must be four of the 90 inherited V18 blank outcomes")
    if sum(not r.get("Quantitative_Outcome", "").strip() for r in evidence) > 61:
        errors.append("expected no more than 61 blank outcomes after Batch 006")

    warning_ids = [r.get("Warning_ID", "") for r in warnings]
    audit_ids = [r.get("Warning_ID", "") for r in warning_audit]
    baseline_warning_ids = {r.get("Warning_ID", "") for r in baseline_warnings}
    if len(warning_ids) < 83 or len(warning_ids) != len(set(warning_ids)):
        errors.append("warning ledger must preserve 70 inherited IDs plus thirteen documented V19 IDs exactly once")
    if not baseline_warning_ids <= set(warning_ids) or len(baseline_warning_ids) != 70:
        errors.append("all 70 inherited V18 warnings must remain present")
    if len(audit_ids) != len(set(audit_ids)) or set(warning_ids) != set(audit_ids):
        errors.append("warning ledger and warning audit must match uniquely")
    ledger = {r.get("Warning_ID", ""): r for r in warnings}
    wa = {r.get("Warning_ID", ""): r for r in warning_audit}
    for wid, row in ledger.items():
        if row.get("Audit_Status") != wa.get(wid, {}).get("V19_Status"):
            errors.append(f"{wid}: ledger and warning-audit statuses disagree")
    for wid in NEW_WARNINGS:
        if ledger.get(wid, {}).get("Audit_Status") != "NEEDS_MANUAL_REVIEW":
            errors.append(f"{wid}: source uncertainty must remain open for manual review")
        if wa.get(wid, {}).get("V19_Status") != "NEEDS_MANUAL_REVIEW" or "V19-006" not in wa.get(wid, {}).get("V19_Recheck_Status", ""):
            errors.append(f"{wid}: warning audit lacks the V19-006 open review history")
    w10 = ledger.get("V19-W10", {})
    for target in ("SB-0110", "SB-0111", "SB-0163", "SB-0164", "27472952", "27765854"):
        if target not in w10.get("Affected", ""):
            errors.append(f"V19-W10: affected record/PMID list omits {target}")
    if w10.get("Audit_Status") != "RESOLVED" or "V19-006" not in w10.get("Audit_Rationale", ""):
        errors.append("V19-W10 must remain resolved with its Batch 006 verification history")

    if len(review) == 4 and len({r.get("Source_Locator", "") for r in review}) != 4:
        errors.append("each evidence record must have a record-specific source locator")
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
            rows(root, "validation/V19_batch_006_review.csv"),
            rows(root, "data/publication_bibliography.csv"),
            rows(parent, "data/interaction_evidence.csv"),
            rows(parent, "data/warning_ledger.csv"),
        )
    except (OSError, csv.Error) as exc:
        return [f"validation input unreadable: {exc}"]


if __name__ == "__main__":
    release = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    errors = validate(release)
    xml_path = release / UA_XML
    result = {
        "release": release.resolve().name, "batch": "V19-006",
        "status": "PASS" if not errors else "FAIL", "reviewed_records": 4,
        "source_tier": 1, "quantitative_outcomes_populated": 4,
        "open_source_warnings": sorted(NEW_WARNINGS),
        "metadata_cache_repair_pmids": sorted(SOURCES),
        "primary_xml_sha256": hashlib.sha256(xml_path.read_bytes()).hexdigest() if xml_path.is_file() else None,
        "errors": errors,
    }
    (release / "validation/V19_batch_006_integrity_results.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(bool(errors))
