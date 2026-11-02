"""Validate V19-009 Tier 3 midazolam/flavonoid dispositions and warnings."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

PMID = "18191104"
DOI = "10.1016/j.bcp.2007.11.012"
TITLE = "Flavonoids diosmetin and luteolin inhibit midazolam metabolism by human liver microsomes and recombinant CYP 3A4 and CYP3A5 enzymes."
URL = "https://pubmed.ncbi.nlm.nih.gov/18191104/"
CACHE = "history/rebuild_artifacts/4bcf7ef9bb102769124c952b66b3e4c8bf0f2d43c65c8e92cddd1a34268a6be8_pmid_18191104.json"
TARGETS = {"SB-0149": "Diosmetin", "SB-0150": "Luteolin", "SB-0173": "Tangeretin"}
INHIBITORS = {"SB-0149", "SB-0150"}


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
    if len(ids) != len(set(ids)):
        errors.append("duplicate evidence IDs")
    if len(audit_ids) != len(set(audit_ids)) or set(audit_ids) != set(ids):
        errors.append("source audit must uniquely cover all evidence records")
    if len(claim_ids) != len(set(claim_ids)) or not set(TARGETS) <= set(claim_ids):
        errors.append("claim support must uniquely include all Batch 009 records")
    if len(review_ids) != len(set(review_ids)) or set(review_ids) != set(TARGETS):
        errors.append("Batch 009 review must cover exactly SB-0149, SB-0150 and SB-0173")

    ev = {r.get("Evidence_ID", ""): r for r in evidence}
    au = {r.get("Evidence_ID", ""): r for r in audits}
    cl = {r.get("Evidence_ID", ""): r for r in claims}
    rv = {r.get("Evidence_ID", ""): r for r in review}
    pubs = {r.get("PMID", ""): r for r in bibliography}
    for eid, compound in TARGETS.items():
        e, a, c, r = ev.get(eid, {}), au.get(eid, {}), cl.get(eid, {}), rv.get(eid, {})
        if not all((e, a, c, r)):
            errors.append(f"{eid}: evidence/source-audit/claim-support/review row missing")
            continue
        if e.get("Compound") != compound or e.get("Drug") != "Midazolam":
            errors.append(f"{eid}: compound or midazolam attribution mismatch")
        if any(row.get("PMID") != PMID for row in (e, a, c, r)):
            errors.append(f"{eid}: PMID mismatch")
        if any(row.get("DOI", "").lower() != DOI.lower() for row in (e, a, r)):
            errors.append(f"{eid}: DOI mismatch")
        if e.get("Evidence_Type") != "In vitro" or e.get("Evidence_Level") != "compound":
            errors.append(f"{eid}: human microsome evidence must remain in-vitro single-compound evidence")
        if a.get("Verification_Level") != "3" or "V19_TIER_3_PRIMARY_ABSTRACT_REVIEWED" not in a.get("Audit_Disposition", ""):
            errors.append(f"{eid}: inaccessible full text must not be promoted beyond Tier 3")
        if a.get("Verification_Date") != "2026-11-03" or r.get("Review_Date") != "2026-11-03":
            errors.append(f"{eid}: review date missing or incorrect")
        if any(row.get("Source_URL") != URL for row in (e, a)) or r.get("Primary_Source_URL") != URL:
            errors.append(f"{eid}: PubMed primary abstract URL mismatch")
        if any(row.get("Source_Cache") != CACHE for row in (e, a)) or r.get("Local_Metadata_Cache") != CACHE:
            errors.append(f"{eid}: local MED metadata locator mismatch")
        locator = e.get("Source_Locator", "")
        if not locator or any(row.get("Source_Locator") != locator for row in (a, c, r)):
            errors.append(f"{eid}: abstract locator missing or inconsistent")
        outcome = e.get("Quantitative_Outcome", "")
        if not outcome.strip() or outcome != r.get("Verified_Outcome"):
            errors.append(f"{eid}: abstract disposition is blank or differs from review record")
        if "Tier 3" not in outcome or (eid == "SB-0173" and "none was inferred" not in outcome.lower()):
            errors.append(f"{eid}: abstract-only limitation or non-inference statement missing")
        if eid in INHIBITORS:
            for marker in ["concentration-dependent", "1′- and 4-hydroxymidazolam", "30–50 μmol", "not assigned"]:
                if marker.lower() not in outcome.lower():
                    errors.append(f"{eid}: group-level source finding or non-attribution missing: {marker}")
            if "not assigned to " + compound.lower() + " alone" not in outcome.lower():
                errors.append(f"{eid}: shared Ki range is improperly assignable to this compound")
            lower = outcome.lower()
            if "30–50 μmol/l" in lower or "30–50 μm " in lower or "ki=" in lower:
                errors.append(f"{eid}: unsupported Ki unit normalization or compound-specific value")
        elif "30–50" in outcome or "ki=" in outcome.lower():
            errors.append("SB-0173: a group Ki range or individual kinetic estimate was incorrectly assigned to tangeretin")
        elif "stimulated midazolam metabolism" not in outcome.lower() or "not a human clinical effect" not in outcome.lower():
            errors.append("SB-0173: abstract-reported tangeretin stimulation or in-vitro limitation missing")
        if "no intact-human treatment study" not in e.get("Population", ""):
            errors.append(f"{eid}: in-vitro model must be distinguished from human treatment evidence")
        if "full-text" not in a.get("Verification_Method", "").lower() and "full text" not in a.get("Verification_Method", "").lower():
            errors.append(f"{eid}: full-text access limitation is not documented")

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
    blank_ids = {eid for eid, row in baseline.items() if not row.get("Quantitative_Outcome", "").strip()}
    if len(blank_ids) != 90 or not set(TARGETS) <= blank_ids:
        errors.append("Batch 009 targets must be inherited V18 blank outcomes")
    if any(not ev[eid].get("Quantitative_Outcome", "").strip() for eid in TARGETS):
        errors.append("all three abstract findings must have an explicit disposition")
    current_blanks = sum(not row.get("Quantitative_Outcome", "").strip() for row in evidence)
    if current_blanks > 47:
        errors.append(f"expected no more than 47 quantitative blanks after Batch 009; found {current_blanks}")

    warning_ids = [r.get("Warning_ID", "") for r in warnings]
    audit_warning_ids = [r.get("Warning_ID", "") for r in warning_audit]
    inherited = {r.get("Warning_ID", "") for r in baseline_warnings}
    if len(warnings) < 85 or len(warning_ids) != len(set(warning_ids)):
        errors.append("warning ledger must retain all inherited warnings and V19-W01 through V19-W15 exactly once")
    if len(inherited) != 70 or not inherited <= set(warning_ids):
        errors.append("all 70 inherited V18 warning IDs must remain present")
    if len(audit_warning_ids) != len(set(audit_warning_ids)) or set(warning_ids) != set(audit_warning_ids):
        errors.append("warning ledger and V19 warning audit must match uniquely")
    if not {f"V19-W{i:02d}" for i in range(1, 16)} <= set(warning_ids):
        errors.append("one or more V19 warnings through V19-W15 are missing")
    by_w = {r.get("Warning_ID", ""): r for r in warnings}
    by_wa = {r.get("Warning_ID", ""): r for r in warning_audit}
    for wid, row in by_w.items():
        if row.get("Audit_Status") != by_wa.get(wid, {}).get("V19_Status"):
            errors.append(f"{wid}: warning status mismatch")
    w10 = by_w.get("V19-W10", {})
    if w10.get("Audit_Status") != "RESOLVED" or "18191104" not in w10.get("Affected", "") or "18191104" not in w10.get("Audit_Verification_Reference", ""):
        errors.append("V19-W10 does not document and verify the Batch 009 cache repair")
    if "V19-009" not in by_wa.get("V19-W10", {}).get("V19_Recheck_Status", ""):
        errors.append("V19-W10 audit lost the Batch 009 repair history")
    w15 = by_w.get("V19-W15", {})
    if w15.get("Audit_Status") != "NEEDS_MANUAL_REVIEW" or not all(eid in w15.get("Affected", "") for eid in INHIBITORS):
        errors.append("V19-W15 must remain open and identify both affected inhibitor records")
    if (not w15.get("Remaining_Limitations", "").strip()
            or not w15.get("Audit_Verification_Reference", "").strip()
            or not by_wa.get("V19-W15", {}).get("V19_Evidence_or_Rationale", "").strip()):
        errors.append("V19-W15 requires traceable open-warning rationale and limitation")
    for wid in ("V19-W11", "V19-W12", "V19-W13"):
        if by_w.get(wid, {}).get("Audit_Status") != "NEEDS_MANUAL_REVIEW":
            errors.append(f"{wid}: unresolved source discrepancy must remain open")
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
            rows(root, "validation/V19_batch_009_review.csv"),
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
        "release": release.resolve().name, "batch": "V19-009", "status": "PASS" if not errors else "FAIL",
        "reviewed_records": 3, "source_tier": 3, "qualitative_outcomes_dispositioned": 3,
        "per_compound_Ki_values_assigned": 0, "blank_outcomes_remaining": sum(not r.get("Quantitative_Outcome", "").strip() for r in rows(release, "data/interaction_evidence.csv")),
        "metadata_cache_repair_pmids": [PMID], "open_warning_ids": ["V19-W15"], "errors": errors,
    }
    (release / "validation/V19_batch_009_integrity_results.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(bool(errors))
