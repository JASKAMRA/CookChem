"""Validate V19-008 abstract-only paclitaxel dispositions and warning traceability."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

PMID = "12920504"
DOI = "10.1007/s00210-003-0781-9"
TITLE = "Paclitaxel metabolism in rat and human liver microsomes is inhibited by phenolic antioxidants."
URL = "https://link.springer.com/article/10.1007/s00210-003-0781-9"
CACHE = "history/rebuild_artifacts/99a6f10462261b27f84002569a1224abbc0436e6783b7a59d8610ad40508f080_pmid_12920504.json"
TARGETS = {f"SB-{i:04d}" for i in range(113, 122)}
CLASSIFICATION_FIXES = {f"SB-{i:04d}" for i in [110, 111, 113, 114, 115, 116, 117, 118]}
NO_INHIBITION = {"SB-0116", "SB-0117", "SB-0118", "SB-0119", "SB-0120"}
FINDINGS = {
    "SB-0113": ["highest inhibitory potency", "weaker than resveratrol", "not present in the accessible abstract"],
    "SB-0114": ["second in the source-reported inhibitory-potency order", "no inhibition is reported in rat microsomes"],
    "SB-0115": ["more inhibitory than fisetin", "ranked after fisetin, quercetin and morin"],
    **{eid: ["not inhibitory to paclitaxel metabolism"] for eid in NO_INHIBITION},
    "SB-0121": ["third in the source-reported inhibitory-potency order", "no inhibition is reported in rat microsomes"],
}
def rows(root: Path, rel: str) -> list[dict[str, str]]:
    with (root / rel).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_records(root: Path, evidence, audits, claims, warnings, warning_audit,
                     review, bibliography, baseline_evidence, baseline_warnings) -> list[str]:
    root = Path(root).resolve()
    errors: list[str] = []
    evidence_ids = [r.get("Evidence_ID", "") for r in evidence]
    audit_ids = [r.get("Evidence_ID", "") for r in audits]
    claim_ids = [r.get("Evidence_ID", "") for r in claims]
    review_ids = [r.get("Evidence_ID", "") for r in review]
    if len(evidence_ids) != len(set(evidence_ids)):
        errors.append("duplicate evidence IDs")
    if len(audit_ids) != len(set(audit_ids)) or set(audit_ids) != set(evidence_ids):
        errors.append("source audit must uniquely cover every evidence record")
    if len(claim_ids) != len(set(claim_ids)) or not TARGETS <= set(claim_ids):
        errors.append("claim support must uniquely include all nine Batch 008 records")
    if len(review_ids) != len(set(review_ids)) or set(review_ids) != TARGETS:
        errors.append("Batch 008 review must cover exactly SB-0113 through SB-0121")

    by_e = {r.get("Evidence_ID", ""): r for r in evidence}
    by_a = {r.get("Evidence_ID", ""): r for r in audits}
    by_c = {r.get("Evidence_ID", ""): r for r in claims}
    by_r = {r.get("Evidence_ID", ""): r for r in review}
    pubs = {r.get("PMID", ""): r for r in bibliography}
    for eid in sorted(TARGETS):
        e, a, c, r = by_e.get(eid, {}), by_a.get(eid, {}), by_c.get(eid, {}), by_r.get(eid, {})
        if not all((e, a, c, r)):
            errors.append(f"{eid}: evidence/source-audit/claim-support/review row missing")
            continue
        if any(row.get("PMID") != PMID for row in (e, a, c, r)):
            errors.append(f"{eid}: PMID mismatch")
        if any(row.get("DOI", "").lower() != DOI.lower() for row in (e, a, r)):
            errors.append(f"{eid}: DOI mismatch")
        if e.get("Drug") != "Paclitaxel" or a.get("Drug_Probe") != "Paclitaxel" or r.get("Drug_Probe") != "Paclitaxel":
            errors.append(f"{eid}: paclitaxel attribution mismatch")
        if e.get("Evidence_Type") != "In vitro":
            errors.append(f"{eid}: microsomal evidence must remain in-vitro")
        if e.get("Evidence_Level") != "compound" and eid in CLASSIFICATION_FIXES:
            errors.append(f"{eid}: individual compound was not reclassified from formulation")
        if a.get("Verification_Level") != "3" or "V19_TIER_3_PRIMARY_ABSTRACT_REVIEWED" not in a.get("Audit_Disposition", ""):
            errors.append(f"{eid}: abstract-only review must remain Tier 3")
        if a.get("Verification_Date") != "2026-11-03" or r.get("Review_Date") != "2026-11-03":
            errors.append(f"{eid}: actual review date missing or incorrect")
        if any(row.get("Source_URL") != URL for row in (e, a)) or r.get("Primary_Source_URL") != URL:
            errors.append(f"{eid}: publisher primary-source URL mismatch")
        if any(row.get("Source_Cache") != CACHE for row in (e, a)) or r.get("Local_Metadata_Cache") != CACHE:
            errors.append(f"{eid}: local MED metadata locator mismatch")
        locator = e.get("Source_Locator", "")
        if not locator or any(row.get("Source_Locator") != locator for row in (a, c, r)):
            errors.append(f"{eid}: abstract source locator missing or inconsistent")
        outcome = e.get("Quantitative_Outcome", "")
        if not outcome.strip() or r.get("Verified_Outcome") != outcome:
            errors.append(f"{eid}: qualitative disposition is blank or differs from review ledger")
        for marker in FINDINGS[eid]:
            if marker.lower() not in outcome.lower():
                errors.append(f"{eid}: source-supported finding or limitation missing: {marker}")
        if eid in NO_INHIBITION and "not proof of no interaction" not in e.get("Limitations", "").lower():
            errors.append(f"{eid}: null finding is overstated without its scope limitation")
        if any(token.lower() in outcome.lower() for token in ["ic50 =", "ki =", "inhibition =", "% inhibition"]):
            errors.append(f"{eid}: unsupported quantitative potency appears in abstract-only outcome")
        if "no inhibitor concentration" not in a.get("Numerical_Outcome_Verified", "").lower():
            errors.append(f"{eid}: absence of abstract-level quantitative data is not documented")
        if "full text" not in a.get("Limitations", "").lower() or "no clinical interaction" not in e.get("Limitations", "").lower():
            errors.append(f"{eid}: source-access and clinical-extrapolation limitations missing")

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
    inherited_blanks = {eid for eid, row in baseline.items() if not row.get("Quantitative_Outcome", "").strip()}
    if len(inherited_blanks) != 90 or not TARGETS <= inherited_blanks:
        errors.append("Batch 008 targets must be inherited V18 blank outcomes")
    if sum(not r.get("Quantitative_Outcome", "").strip() for r in evidence) > 50:
        errors.append("expected no more than 50 quantitative blanks after Batch 008; qualitative text is not numeric recovery")

    warning_ids = [r.get("Warning_ID", "") for r in warnings]
    audit_warning_ids = [r.get("Warning_ID", "") for r in warning_audit]
    inherited_ids = {r.get("Warning_ID", "") for r in baseline_warnings}
    if len(warnings) < 84 or len(warning_ids) != len(set(warning_ids)):
        errors.append("warning ledger must contain 70 inherited rows and V19-W01 through V19-W14 exactly once")
    if len(inherited_ids) != 70 or not inherited_ids <= set(warning_ids):
        errors.append("all 70 inherited V18 warning IDs must remain present")
    if len(audit_warning_ids) != len(set(audit_warning_ids)) or set(warning_ids) != set(audit_warning_ids):
        errors.append("warning ledger and V19 warning audit must match uniquely")
    if not {f"V19-W{i:02d}" for i in range(1, 15)} <= set(warning_ids):
        errors.append("one or more V19 warnings through V19-W14 are missing")
    by_w = {r.get("Warning_ID", ""): r for r in warnings}
    by_wa = {r.get("Warning_ID", ""): r for r in warning_audit}
    for wid, row in by_w.items():
        if row.get("Audit_Status") != by_wa.get(wid, {}).get("V19_Status"):
            errors.append(f"{wid}: warning status mismatch")
    w10 = by_w.get("V19-W10", {})
    if w10.get("Audit_Status") != "RESOLVED" or "12920504" not in w10.get("Affected", "") or "12920504" not in w10.get("Audit_Verification_Reference", ""):
        errors.append("V19-W10 does not document and verify the Batch 008 cache repair")
    if "V19-008" not in by_wa.get("V19-W10", {}).get("V19_Recheck_Status", ""):
        errors.append("V19-W10 audit lost the Batch 008 repair history")
    w14 = by_w.get("V19-W14", {})
    if w14.get("Audit_Status") != "RESOLVED" or not CLASSIFICATION_FIXES <= set(w14.get("Affected", "").split(" | ")):
        errors.append("V19-W14 must resolve only after all eight named compound classifications are corrected")
    for wid in ("V19-W11", "V19-W12", "V19-W13"):
        if by_w.get(wid, {}).get("Audit_Status") != "NEEDS_MANUAL_REVIEW":
            errors.append(f"{wid}: unresolved scientific discrepancy must remain open for manual review")
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
            rows(root, "validation/V19_batch_008_review.csv"),
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
        "release": release.resolve().name, "batch": "V19-008", "status": "PASS" if not errors else "FAIL",
        "reviewed_records": 9, "source_tier": 3, "qualitative_outcomes_dispositioned": 9,
        "quantitative_potencies_inferred": 0, "blank_outcomes_remaining": 50,
        "metadata_cache_repair_pmids": [PMID], "warning_ids": ["V19-W14"], "errors": errors,
    }
    (release / "validation/V19_batch_008_integrity_results.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(bool(errors))
