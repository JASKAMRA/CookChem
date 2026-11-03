"""Validate V19-011 full-text extraction and the retained source discrepancy."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

PMID = "21870106"
DOI = "10.1007/s00228-011-1108-2"
URL = "https://pmc.ncbi.nlm.nih.gov/articles/PMC4898966/"
CACHE = "history/rebuild_artifacts/e6087e27abee52b102719512fdea5e34b85a2e0746eaea63037868f862944d8a_pmid_21870106.json"
TARGETS = {"SB-0003": "Midazolam", "SB-0004": "Dextromethorphan", "SB-0005": "Losartan"}


def rows(root: Path, rel: str) -> list[dict[str, str]]:
    with (root / rel).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_records(root: Path, evidence, audits, claims, warnings, warning_audit, review, bibliography, baseline_warnings) -> list[str]:
    root = Path(root).resolve()
    errors: list[str] = []
    eids = [r.get("Evidence_ID", "") for r in evidence]
    aids = [r.get("Evidence_ID", "") for r in audits]
    cids = [r.get("Evidence_ID", "") for r in claims]
    rids = [r.get("Evidence_ID", "") for r in review]
    if len(eids) != 317 or len(eids) != len(set(eids)):
        errors.append("evidence IDs must remain 317 and unique")
    if len(aids) != len(set(aids)) or set(aids) != set(eids):
        errors.append("source-audit coverage must uniquely match all evidence IDs")
    if len(cids) != len(set(cids)) or not set(TARGETS) <= set(cids):
        errors.append("claim-support IDs must remain unique and include the three target records")
    if len(rids) != len(set(rids)) or set(rids) != set(TARGETS):
        errors.append("V19-011 review must cover SB-0003 through SB-0005 exactly once")
    ev = {r.get("Evidence_ID", ""): r for r in evidence}
    au = {r.get("Evidence_ID", ""): r for r in audits}
    cl = {r.get("Evidence_ID", ""): r for r in claims}
    rv = {r.get("Evidence_ID", ""): r for r in review}
    pubs = {r.get("PMID", ""): r for r in bibliography}
    pub = pubs.get(PMID, {})
    if pub.get("Source") != CACHE or pub.get("DOI", "").lower() != DOI.lower():
        errors.append("bibliography cache pointer or PMID/DOI association is incorrect")
    try:
        payload = json.loads((root / CACHE).read_text(encoding="utf-8-sig"))
        cache_items = payload.get("resultList", {}).get("result", [])
        if not any(str(x.get("pmid", x.get("id", ""))) == PMID and str(x.get("doi", "")).lower() == DOI.lower() for x in cache_items):
            errors.append("archived MED metadata does not verify the target PMID/DOI")
    except (OSError, json.JSONDecodeError):
        errors.append("archived MED metadata cache is missing or unreadable")
    by_w = {r.get("Warning_ID", ""): r for r in warnings}
    by_wa = {r.get("Warning_ID", ""): r for r in warning_audit}
    warning_ids = [r.get("Warning_ID", "") for r in warnings]
    audit_warning_ids = [r.get("Warning_ID", "") for r in warning_audit]
    baseline_ids = {r.get("Warning_ID", "") for r in baseline_warnings}
    if len(warning_ids) < 87 or len(warning_ids) != len(set(warning_ids)):
        errors.append("warning ledger must preserve at least the 87 unique rows through V19-W17")
    if len(audit_warning_ids) != len(set(audit_warning_ids)) or set(audit_warning_ids) != set(warning_ids):
        errors.append("warning audit and warning ledger IDs must match uniquely")
    if not baseline_ids <= set(warning_ids) or len(baseline_ids) != 70:
        errors.append("all 70 inherited warning IDs must remain present")
    if not {f"V19-W{i:02d}" for i in range(1, 18)} <= set(warning_ids):
        errors.append("one or more V19 warning IDs through W17 are missing")
    for wid, row in by_w.items():
        if row.get("Audit_Status") != by_wa.get(wid, {}).get("V19_Status"):
            errors.append(f"{wid}: warning ledger/audit status mismatch")

    for eid, drug in TARGETS.items():
        e, a, c, r = ev.get(eid, {}), au.get(eid, {}), cl.get(eid, {}), rv.get(eid, {})
        if not all((e, a, c, r)):
            errors.append(f"{eid}: evidence, source audit, claim support or batch review missing")
            continue
        if e.get("Compound") != "Berberine" or e.get("Drug") != drug or e.get("PMID") != PMID or e.get("DOI", "").lower() != DOI.lower():
            errors.append(f"{eid}: compound, drug or publication attribution mismatch")
        if e.get("Evidence_Type") != "Human pharmacokinetic" or e.get("Outcome") != "observed_effect":
            errors.append(f"{eid}: human probe evidence scope was incorrectly changed")
        if e.get("Source_URL") != URL or e.get("Source_Cache") != CACHE:
            errors.append(f"{eid}: evidence source URL or repaired local cache pointer is incorrect")
        if not (root / CACHE).is_file() or a.get("Source_Cache") != CACHE or a.get("Source_URL") != URL:
            errors.append(f"{eid}: source-audit cache or URL is missing/broken")
        if a.get("Verification_Level") != "1" or a.get("Verification_Date") != "2026-11-03" or "V19_TIER_1_FULL_TEXT_REVIEWED" not in a.get("Audit_Disposition", ""):
            errors.append(f"{eid}: source tier/date/disposition is not supported")
        locator = a.get("Source_Locator", "")
        if "Table 1" not in locator or "Methods" not in locator or e.get("Source_Locator") != locator:
            errors.append(f"{eid}: primary full-text locator missing or inconsistent")
        if c.get("Source_Locator") != locator or r.get("Source_Locator") != locator:
            errors.append(f"{eid}: claim-support or review locator does not match")
        if r.get("Verification_Tier") != "1" or r.get("Review_Date") != "2026-11-03" or r.get("Local_Metadata_Cache") != CACHE:
            errors.append(f"{eid}: batch review provenance fields mismatch")
        if r.get("Primary_Source_URL") != URL or r.get("Verified_Outcome") != e.get("Quantitative_Outcome"):
            errors.append(f"{eid}: source URL or outcome does not match review record")
        if "17" not in e.get("Population", "") or "4-week washout" not in e.get("Study_Design", ""):
            errors.append(f"{eid}: participant flow or crossover washout is missing")
        if not e.get("Dose", "").strip() or drug.lower() not in e.get("Dose", "").lower():
            errors.append(f"{eid}: tested berberine/probe dose is missing")
        if "clinical outcome" not in e.get("Limitations", "").lower() and "clinical outcome" not in r.get("Remaining_Limitation", "").lower():
            errors.append(f"{eid}: probe endpoint limitation is missing")

    for eid, markers in {
        "SB-0003": ["AUC0–∞", "140% (117–168%)", "AUC0–12 h", "137% (112–167%)", "138% (107–177%)", "Tmax 0.66", "t1/2 3.03"],
        "SB-0004": ["0.04 ± 0.04", "0.40 ± 0.37", "979% (650–1,474%)", "p<0.01"],
        "SB-0005": ["0.22 ± 0.16", "0.46 ± 0.33", "202% (152–270%)", "CYP2C19", "CYP2C9"],
    }.items():
        text = ev.get(eid, {}).get("Quantitative_Outcome", "")
        for marker in markers:
            if marker.lower() not in text.lower():
                errors.append(f"{eid}: source-supported outcome marker absent: {marker}")
    if "swaps the Tmax and t1/2 labels" not in ev.get("SB-0003", {}).get("Quantitative_Outcome", ""):
        errors.append("SB-0003: abstract/Table 1 label discrepancy must remain visible")
    w10 = by_w.get("V19-W10", {})
    if w10.get("Audit_Status") != "RESOLVED" or not all(eid in w10.get("Affected", "") for eid in TARGETS):
        errors.append("V19-W10 must remain resolved and include all three repaired record pointers")
    if "V19-011" not in by_wa.get("V19-W10", {}).get("V19_Recheck_Status", ""):
        errors.append("V19-W10 audit does not document the V19-011 scope expansion")
    w17 = by_w.get("V19-W17", {})
    wa17 = by_wa.get("V19-W17", {})
    if w17.get("Audit_Status") != "NEEDS_MANUAL_REVIEW" or wa17.get("V19_Status") != "NEEDS_MANUAL_REVIEW":
        errors.append("V19-W17 source discrepancy must remain open for manual review")
    if "SB-0005" not in w17.get("Affected", "") or not all(x in w17.get("Description", "") for x in ("CYP2C19", "CYP2C9")):
        errors.append("V19-W17 must identify SB-0005 and both conflicting enzyme labels")
    if sum(not r.get("Quantitative_Outcome", "").strip() for r in evidence) > 44:
        errors.append("Batch 011 must not increase the 44 remaining blank quantitative outcomes")
    metadata = json.loads((root / "release_metadata.json").read_text(encoding="utf-8-sig"))
    review_meta = metadata.get("v19_primary_source_review", {})
    reviewed = review_meta.get("evidence_records_reviewed", 0)
    remaining = review_meta.get("source_review_remaining", -1)
    if metadata.get("warning_count") != len(warnings) or reviewed < 52 or reviewed + remaining != 317:
        errors.append("release metadata does not preserve the cumulative V19-011-or-later scope")
    return sorted(set(errors))


def validate(root: Path) -> list[str]:
    root = Path(root).resolve()
    parent = root.parent / "StageB_V18_20261103"
    if not parent.is_dir():
        return ["immutable V18 parent release unavailable"]
    try:
        return validate_records(
            root, rows(root, "data/interaction_evidence.csv"), rows(root, "provenance/source_audit.csv"),
            rows(root, "provenance/claim_support_and_verification.csv"), rows(root, "data/warning_ledger.csv"),
            rows(root, "validation/V19_warning_audit.csv"), rows(root, "validation/V19_batch_011_review.csv"),
            rows(root, "data/publication_bibliography.csv"), rows(parent, "data/warning_ledger.csv"),
        )
    except (OSError, csv.Error, json.JSONDecodeError) as exc:
        return [f"validation input unreadable: {exc}"]


if __name__ == "__main__":
    release = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    errors = validate(release)
    result = {"release": release.resolve().name, "batch": "V19-011", "status": "PASS" if not errors else "FAIL", "reviewed_records": 3, "source_tier": 1, "open_warning_ids": ["V19-W17"], "errors": errors}
    (release / "validation/V19_batch_011_integrity_results.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(bool(errors))
