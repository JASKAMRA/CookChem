"""Validate V19-007 full-text outcomes for human caffeine and omeprazole probes."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

PMID = "21870106"
DOI = "10.1007/s00228-011-1108-2"
TITLE = "Repeated administration of berberine inhibits cytochromes P450 in humans."
URL = "https://pmc.ncbi.nlm.nih.gov/articles/PMC4898966/"
CACHE = "history/rebuild_artifacts/e6087e27abee52b102719512fdea5e34b85a2e0746eaea63037868f862944d8a_pmid_21870106.json"
TARGETS = {"SB-0187": "Caffeine", "SB-0188": "Omeprazole"}
MARKERS = {
    "SB-0187": ["33.98 ± 9.40", "29.80 ± 11.30", "85% (76–95%)", "4.48 ± 1.03", "4.16 ± 1.86", "88% (75–103%)", "1.51 ± 2.06", "0.94 ± 0.45", "no statistically significant", "80–125%", "not evidence of equivalence", "17"],
    "SB-0188": ["1.73 ± 1.86", "1.47 ± 1.48", "98% (81–120%)", "0.52 ± 0.45", "0.44 ± 0.25", "99% (84–117%)", "24.13 ± 17.40", "21.70 ± 12.29", "6.83 ± 9.94", "7.34 ± 9.61", "no statistically significant", "17"],
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
        errors.append("claim support must uniquely include both Batch 007 records")
    if len(rids) != len(set(rids)) or set(rids) != set(TARGETS):
        errors.append("Batch 007 review must cover exactly SB-0187 and SB-0188")

    by_e = {r.get("Evidence_ID", ""): r for r in evidence}
    by_a = {r.get("Evidence_ID", ""): r for r in audits}
    by_c = {r.get("Evidence_ID", ""): r for r in claims}
    by_r = {r.get("Evidence_ID", ""): r for r in review}
    pubs = {r.get("PMID", ""): r for r in bibliography}
    for eid, drug in TARGETS.items():
        e, a, c, r = by_e.get(eid, {}), by_a.get(eid, {}), by_c.get(eid, {}), by_r.get(eid, {})
        if not e or not a or not c or not r:
            errors.append(f"{eid}: evidence/source-audit/claim-support/review row missing")
            continue
        if any(row.get("PMID") != PMID for row in (e, a, c, r)):
            errors.append(f"{eid}: PMID mismatch")
        if any(row.get("DOI", "").lower() != DOI.lower() for row in (e, a, r)):
            errors.append(f"{eid}: DOI mismatch")
        if e.get("Drug") != drug or a.get("Drug_Probe") != drug or r.get("Drug_Probe") != drug:
            errors.append(f"{eid}: drug/probe assignment mismatch")
        if e.get("Evidence_Type") != "Human pharmacokinetic" or e.get("Evidence_Level") != "compound":
            errors.append(f"{eid}: evidence classification must remain human pharmacokinetic probe evidence")
        if a.get("Verification_Level") != "1" or "V19_TIER_1_FULL_TEXT_REVIEWED" not in a.get("Audit_Disposition", ""):
            errors.append(f"{eid}: source audit is not Tier 1 full-text reviewed")
        if a.get("Verification_Date") != "2026-11-03" or r.get("Review_Date") != "2026-11-03":
            errors.append(f"{eid}: actual review date missing or incorrect")
        if any(row.get("Source_URL") != URL for row in (e, a)) or r.get("Primary_Source_URL") != URL:
            errors.append(f"{eid}: primary PMC source URL mismatch")
        if any(row.get("Source_Cache") != CACHE for row in (e, a)) or r.get("Local_Metadata_Cache") != CACHE:
            errors.append(f"{eid}: local MED metadata locator mismatch")
        locator = e.get("Source_Locator", "")
        if not locator or any(row.get("Source_Locator") != locator for row in (a, c, r)):
            errors.append(f"{eid}: record-specific Methods/Table 1 locator is missing or inconsistent")
        outcome = e.get("Quantitative_Outcome", "")
        if not outcome.strip() or r.get("Verified_Outcome") != outcome:
            errors.append(f"{eid}: source-supported outcome is blank or differs from review ledger")
        for marker in MARKERS[eid]:
            if marker.lower() not in outcome.lower():
                errors.append(f"{eid}: primary-source estimate or interpretation missing: {marker}")
        if not e.get("Limitations", "").strip() or not r.get("Remaining_Limitation", "").strip():
            errors.append(f"{eid}: human study limitations missing")

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
    if pubs.get(PMID, {}).get("Source") != CACHE or pubs.get(PMID, {}).get("DOI", "").lower() != DOI.lower() or pubs.get(PMID, {}).get("Title") != TITLE:
        errors.append("bibliography title, DOI or source path is incorrect")

    baseline = {r.get("Evidence_ID", ""): r for r in baseline_evidence}
    blanks = {eid for eid, row in baseline.items() if not row.get("Quantitative_Outcome", "").strip()}
    if len(blanks) != 90 or not set(TARGETS) <= blanks:
        errors.append("Batch 007 targets must be inherited V18 blank outcomes")
    if sum(not r.get("Quantitative_Outcome", "").strip() for r in evidence) > 59:
        errors.append("expected no more than 59 blank outcome fields after Batch 007")

    wids = [r.get("Warning_ID", "") for r in warnings]
    waids = [r.get("Warning_ID", "") for r in warning_audit]
    base_wids = {r.get("Warning_ID", "") for r in baseline_warnings}
    if len(wids) < 83 or len(wids) != len(set(wids)):
        errors.append("warning ledger must preserve all 70 inherited and thirteen V19 warning IDs")
    if len(base_wids) != 70 or not base_wids <= set(wids):
        errors.append("all 70 inherited V18 warnings must remain present")
    if len(waids) != len(set(waids)) or set(wids) != set(waids):
        errors.append("warning ledger and V19 warning audit must match uniquely")
    by_w, by_wa = {r.get("Warning_ID", ""): r for r in warnings}, {r.get("Warning_ID", ""): r for r in warning_audit}
    for wid, row in by_w.items():
        if row.get("Audit_Status") != by_wa.get(wid, {}).get("V19_Status"):
            errors.append(f"{wid}: warning status mismatch")
    w10 = by_w.get("V19-W10", {})
    if w10.get("Audit_Status") != "RESOLVED" or "21870106" not in w10.get("Affected", "") or "21870106" not in w10.get("Audit_Verification_Reference", ""):
        errors.append("V19-W10 does not document and verify the Batch 007 cache repair")
    if "V19-007" not in by_wa.get("V19-W10", {}).get("V19_Recheck_Status", ""):
        errors.append("V19-W10 audit lost the Batch 007 repair history")
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
            rows(root, "validation/V19_batch_007_review.csv"),
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
        "release": release.resolve().name, "batch": "V19-007", "status": "PASS" if not errors else "FAIL",
        "reviewed_records": 2, "source_tier": 1, "human_probe_records": 2,
        "metadata_cache_repair_pmids": [PMID], "caffeine_null_equivalence_caution_retained": True,
        "errors": errors,
    }
    (release / "validation/V19_batch_007_integrity_results.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(bool(errors))
