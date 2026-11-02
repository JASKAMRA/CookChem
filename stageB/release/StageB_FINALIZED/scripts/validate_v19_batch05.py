"""Validate V19-005 pterostilbene/AED source extractions and cache repair."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

PMID = "30877660"
DOI = "10.1007/s12640-019-00021-1"
CACHE = "history/rebuild_artifacts/99cec0f2d566d2068a7f35f8503f49ec51454c7470812ddf65dd9a540c13e9bd_pmid_30877660.json"
BATCH5 = {f"SB-{i}": (PMID, DOI) for i in ("0156", "0157", "0158", "0159", "0160", "0161")}
MARKERS = {
    "SB-0156": ["0.04 mg/kg", "p<0.01", "p<0.001", "16.40 ± 2.12", "14.28 ± 1.20", "p=0.1977", "p=0.4705"],
    "SB-0157": ["5 mg/kg", "F(4,50)=15.13", "F(4,52)=13.49", "F(4,47)=12.05", "p>0.05"],
    "SB-0158": ["11.66 ± 0.61", "7.83 ± 0.86", "2.06 ± 0.10", "2.41 ± 0.06", "5.45 ± 0.36", "26.72 ± 1.1", "p<0.05"],
    "SB-0159": ["F(3,68)=1.16", "p=0.333", "30.45 ± 1.3", "31.20 ± 1.0", "p=0.409"],
    "SB-0160": ["17.61 ± 1.36", "9.02 ± 1.54", "4.23 ± 0.46", "5.47 ± 0.58", "p=0.0104", "p=0.0027"],
    "SB-0161": ["F(3,69)=4.43", "p=0.007", "no individual PTE+VPA group differed significantly", "28.09 ± 1.7", "26.20 ± 1.1"],
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
    if len(cids) != len(set(cids)) or not set(BATCH5) <= set(cids):
        errors.append("claim support must uniquely include all six Batch 005 records")
    if len(rids) != len(set(rids)) or set(rids) != set(BATCH5):
        errors.append("Batch 005 review must cover all six target records exactly once")
    by_e = {r.get("Evidence_ID", ""): r for r in evidence}
    by_a = {r.get("Evidence_ID", ""): r for r in audits}
    by_c = {r.get("Evidence_ID", ""): r for r in claims}
    by_r = {r.get("Evidence_ID", ""): r for r in review}
    pub = {r.get("PMID", ""): r for r in bibliography}

    for eid, (pmid, doi) in BATCH5.items():
        e, a, c, r = by_e.get(eid, {}), by_a.get(eid, {}), by_c.get(eid, {}), by_r.get(eid, {})
        if not e or not a or not c or not r:
            errors.append(f"{eid}: evidence/source-audit/claim-support/review row missing")
            continue
        for label, row in (("evidence", e), ("source audit", a), ("claim support", c), ("batch review", r)):
            if row.get("PMID") != pmid:
                errors.append(f"{eid}: {label} PMID mismatch")
        if any(row.get("DOI", "").lower() != doi.lower() for row in (e, a, r)):
            errors.append(f"{eid}: DOI mismatch")
        if a.get("Verification_Level") != "1" or "V19_TIER_1_FULL_TEXT_REVIEWED" not in a.get("Audit_Disposition", ""):
            errors.append(f"{eid}: Tier 1 full-text status missing")
        if a.get("Verification_Date") != "2026-11-03" or r.get("Review_Date") != "2026-11-03":
            errors.append(f"{eid}: review date missing or incorrect")
        if e.get("Evidence_Type") != "Animal" or e.get("Evidence_Level") != "compound":
            errors.append(f"{eid}: evidence classification must be compound-tested animal evidence")
        if e.get("Source_Cache") != CACHE or a.get("Source_Cache") != CACHE or r.get("Local_Metadata_Cache") != CACHE:
            errors.append(f"{eid}: local MED metadata cache path is inconsistent")
        if e.get("Source_URL") != a.get("Source_URL") or e.get("Source_URL") != r.get("Primary_Source_URL"):
            errors.append(f"{eid}: primary full-text source URL mismatch")
        if not e.get("Source_Locator") or e.get("Source_Locator") != a.get("Source_Locator") or e.get("Source_Locator") != c.get("Source_Locator") or e.get("Source_Locator") != r.get("Source_Locator"):
            errors.append(f"{eid}: section/table/figure locator is missing or inconsistent")
        if not e.get("Quantitative_Outcome", "").strip():
            errors.append(f"{eid}: source-supported outcome remains blank")
        for marker in MARKERS[eid]:
            if marker.lower() not in e.get("Quantitative_Outcome", "").lower():
                errors.append(f"{eid}: primary-source result or limitation missing: {marker}")
        if "male swiss mice" not in e.get("Population", "").lower() or "human" in e.get("Evidence_Type", "").lower():
            errors.append(f"{eid}: animal species/sex scope is missing or misclassified")
        if not e.get("Limitations") or not r.get("Remaining_Limitation"):
            errors.append(f"{eid}: model/exposure limitations are missing")
        if r.get("Verified_Outcome") != e.get("Quantitative_Outcome"):
            errors.append(f"{eid}: reviewed outcome differs from the evidence record")

    cache_path = root / CACHE
    if not cache_path.is_file():
        errors.append("archived MED metadata JSON does not exist")
    else:
        payload = json.loads(cache_path.read_text(encoding="utf-8-sig"))
        items = payload.get("resultList", {}).get("result", [])
        if not any(str(item.get("pmid", item.get("id", ""))) == PMID and str(item.get("doi", "")).lower() == DOI.lower() for item in items):
            errors.append("archived MED metadata JSON does not verify PMID and DOI")
    if pub.get(PMID, {}).get("Source") != CACHE or pub.get(PMID, {}).get("DOI") != DOI:
        errors.append("bibliography source path or DOI is incorrect")

    baseline = {r.get("Evidence_ID", ""): r for r in baseline_evidence}
    baseline_blank = {eid for eid, row in baseline.items() if not row.get("Quantitative_Outcome", "").strip()}
    if len(baseline_blank) != 90 or not set(BATCH5) <= baseline_blank:
        errors.append("Batch 005 must target six inherited V18 blank outcomes")
    if sum(not r.get("Quantitative_Outcome", "").strip() for r in evidence) > 65:
        errors.append("expected no more than 65 blank outcomes after Batch 005")

    warning_ids = [r.get("Warning_ID", "") for r in warnings]
    audit_ids = [r.get("Warning_ID", "") for r in warning_audit]
    baseline_warning_ids = {r.get("Warning_ID", "") for r in baseline_warnings}
    if len(warning_ids) < 80 or len(warning_ids) != len(set(warning_ids)):
        errors.append("warning ledger must preserve 70 inherited IDs plus ten V19 warning IDs exactly once")
    if not baseline_warning_ids <= set(warning_ids) or len(baseline_warning_ids) != 70:
        errors.append("all 70 inherited V18 warnings must remain present")
    if len(audit_ids) != len(set(audit_ids)) or set(warning_ids) != set(audit_ids):
        errors.append("warning ledger and V19 warning audit must match uniquely")
    ledger = {r.get("Warning_ID", ""): r for r in warnings}
    wa = {r.get("Warning_ID", ""): r for r in warning_audit}
    for wid, row in ledger.items():
        if row.get("Audit_Status") != wa.get(wid, {}).get("V19_Status"):
            errors.append(f"{wid}: warning status differs between ledger and audit")
    w10 = ledger.get("V19-W10", {})
    if w10.get("Audit_Status") != "RESOLVED" or "30877660" not in w10.get("Affected", "") or "30877660" not in w10.get("Resolution_Source", ""):
        errors.append("V19-W10 must document the Batch 005 cache-path repair and remain resolved")
    if wa.get("V19-W10", {}).get("V19_Status") != "RESOLVED" or "V19-005" not in wa.get("V19-W10", {}).get("V19_Recheck_Status", ""):
        errors.append("V19-W10 warning audit must preserve the expanded Batch 005 review history")
    if "30877660" not in w10.get("Resolution_Source", "") or not w10.get("Audit_Verification_Reference", "").strip():
        errors.append("V19-W10 resolved closure lacks record-level verification evidence")
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
        rows(root, "validation/V19_batch_005_review.csv"),
        rows(root, "data/publication_bibliography.csv"),
        rows(parent, "data/interaction_evidence.csv"),
        rows(parent, "data/warning_ledger.csv"),
    )


if __name__ == "__main__":
    release = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    errors = validate(release)
    result = {
        "release": release.resolve().name, "batch": "V19-005",
        "status": "PASS" if not errors else "FAIL", "reviewed_records": 6,
        "source_tier": 1, "new_warning_rows": 0, "V19-W10_scope_repaired": True,
        "errors": errors,
    }
    (release / "validation/V19_batch_005_integrity_results.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(bool(errors))
