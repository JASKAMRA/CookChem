"""Validate V19-012 abstract review and the unresolved AUC interval."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

EID, PMID, DOI = "SB-0013", "27981349", "10.1007/s00228-016-2173-3"
CACHE = "history/rebuild_artifacts/fc2955e97491d07e530c79de0c2df8ae78ef5e48d845f659a4ff8a8c6ea20f3e_selected_32.json"
TARGETS = {EID}


def rows(root: Path, rel: str) -> list[dict[str, str]]:
    with (root / rel).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_records(root: Path, evidence, audits, claims, bibliography, warnings, warning_audit, review, baseline_warnings) -> list[str]:
    root = Path(root).resolve()
    errors: list[str] = []
    eids = [r.get("Evidence_ID", "") for r in evidence]
    aids = [r.get("Evidence_ID", "") for r in audits]
    cids = [r.get("Evidence_ID", "") for r in claims]
    rids = [r.get("Evidence_ID", "") for r in review]
    if len(eids) != 317 or len(eids) != len(set(eids)):
        errors.append("evidence IDs must remain 317 and unique")
    if len(aids) != len(set(aids)) or set(aids) != set(eids):
        errors.append("source audit must uniquely cover all 317 evidence IDs")
    if len(cids) != len(set(cids)) or not TARGETS <= set(cids):
        errors.append("claim-support IDs must be unique and include SB-0013")
    if len(rids) != 1 or set(rids) != TARGETS:
        errors.append("V19-012 must contain exactly one review row for SB-0013")
    ev = {r.get("Evidence_ID", ""): r for r in evidence}
    au = {r.get("Evidence_ID", ""): r for r in audits}
    cl = {r.get("Evidence_ID", ""): r for r in claims}
    rv = {r.get("Evidence_ID", ""): r for r in review}
    pubs = {r.get("PMID", ""): r for r in bibliography}
    by_w = {r.get("Warning_ID", ""): r for r in warnings}
    by_wa = {r.get("Warning_ID", ""): r for r in warning_audit}
    warning_ids = [r.get("Warning_ID", "") for r in warnings]
    audit_warning_ids = [r.get("Warning_ID", "") for r in warning_audit]
    inherited = {r.get("Warning_ID", "") for r in baseline_warnings}
    if len(warning_ids) != 88 or len(warning_ids) != len(set(warning_ids)):
        errors.append("warning ledger must contain 88 unique rows after V19-W18")
    if len(audit_warning_ids) != len(set(audit_warning_ids)) or set(audit_warning_ids) != set(warning_ids):
        errors.append("warning audit and ledger must match uniquely")
    if len(inherited) != 70 or not inherited <= set(warning_ids):
        errors.append("all 70 inherited warnings must remain present")
    if not {f"V19-W{i:02d}" for i in range(1, 19)} <= set(warning_ids):
        errors.append("one or more V19 warning IDs through W18 are missing")
    for wid, row in by_w.items():
        if row.get("Audit_Status") != by_wa.get(wid, {}).get("V19_Status"):
            errors.append(f"{wid}: warning ledger/audit status mismatch")

    e, a, c, r = ev.get(EID, {}), au.get(EID, {}), cl.get(EID, {}), rv.get(EID, {})
    if not all((e, a, c, r)):
        errors.append("SB-0013 evidence, audit, claim support or batch review row missing")
    else:
        if e.get("PMID") != PMID or e.get("DOI", "").lower() != DOI.lower() or e.get("Compound") != "Piperine" or e.get("Drug") != "Fexofenadine":
            errors.append("SB-0013 compound/drug/publication attribution mismatch")
        if e.get("Evidence_Type") != "Human pharmacokinetic" or e.get("Outcome") != "observed_effect":
            errors.append("SB-0013 evidence classification changed incorrectly")
        if e.get("Source_Cache") != CACHE or a.get("Source_Cache") != CACHE or pubs.get(PMID, {}).get("Source") != CACHE:
            errors.append("SB-0013 or bibliography metadata cache pointer is broken")
        if e.get("Source_URL") != "https://pubmed.ncbi.nlm.nih.gov/27981349/" or a.get("Source_URL") != e.get("Source_URL"):
            errors.append("SB-0013 primary abstract URL is missing or inconsistent")
        if a.get("Verification_Level") != "3" or "V19_TIER_3_PRIMARY_ABSTRACT_REVIEWED" not in a.get("Audit_Disposition", ""):
            errors.append("SB-0013 must remain Tier 3 abstract-level evidence")
        if a.get("Verification_Date") != "2026-11-03" or r.get("Verification_Tier") != "3" or r.get("Review_Date") != "2026-11-03":
            errors.append("SB-0013 review tier/date is incomplete")
        locator = a.get("Source_Locator", "")
        if "PubMed" not in locator or "abstract" not in locator.lower() or e.get("Source_Locator") != locator or c.get("Source_Locator") != locator or r.get("Source_Locator") != locator:
            errors.append("SB-0013 source locator is missing or inconsistent")
        if r.get("Primary_Source_URL") != e.get("Source_URL") or r.get("Local_Metadata_Cache") != CACHE or r.get("Verified_Outcome") != e.get("Quantitative_Outcome"):
            errors.append("SB-0013 batch review provenance/outcome mismatch")
        outcome = e.get("Quantitative_Outcome", "")
        for marker in ("406.9 vs 767 ng/mL", "3403.7 vs 5724.7 ng·h/mL", "35.4 vs 20.7 L/h", "does not state the AUC interval"):
            if marker.lower() not in outcome.lower():
                errors.append(f"SB-0013 abstract outcome marker missing: {marker}")
        if "does not state the AUC interval" not in outcome or "no AUC0–t or AUC0–∞ label is inferred" not in outcome:
            errors.append("SB-0013 must not infer an AUC interval")
        if "subscription" not in e.get("Limitations", "").lower() or "not directly demonstrated" not in e.get("Limitations", "").lower():
            errors.append("SB-0013 abstract access/mechanism limitations are incomplete")

    try:
        payload = json.loads((root / CACHE).read_text(encoding="utf-8-sig"))
        cache_items = payload.get("resultList", {}).get("result", [])
        if not any(str(x.get("pmid", x.get("id", ""))) == PMID and str(x.get("doi", "")).lower() == DOI.lower() for x in cache_items):
            errors.append("local metadata JSON does not verify PMID and DOI")
    except (OSError, json.JSONDecodeError):
        errors.append("local metadata JSON is missing or unreadable")
    w10 = by_w.get("V19-W10", {})
    if w10.get("Audit_Status") != "RESOLVED" or EID not in w10.get("Affected", "") or "27981349" not in w10.get("Affected", ""):
        errors.append("V19-W10 must remain resolved and include the repaired PMID 27981349 pointers")
    if "V19-012" not in by_wa.get("V19-W10", {}).get("V19_Recheck_Status", ""):
        errors.append("V19-W10 audit lacks V19-012 scope expansion")
    w18 = by_w.get("V19-W18", {})
    if w18.get("Audit_Status") != "NEEDS_MANUAL_REVIEW" or by_wa.get("V19-W18", {}).get("V19_Status") != "NEEDS_MANUAL_REVIEW":
        errors.append("V19-W18 AUC interval warning must remain open")
    if EID not in w18.get("Affected", "") or "AUC interval" not in w18.get("Description", ""):
        errors.append("V19-W18 must point to SB-0013 and the unspecified AUC interval")
    if sum(not r.get("Quantitative_Outcome", "").strip() for r in evidence) != 44:
        errors.append("Batch 012 must preserve the 44 remaining blank quantitative outcomes")
    meta = json.loads((root / "release_metadata.json").read_text(encoding="utf-8-sig"))
    scope = meta.get("v19_primary_source_review", {})
    if meta.get("warning_count") != 88 or scope.get("evidence_records_reviewed") != 53 or scope.get("source_review_remaining") != 264:
        errors.append("release metadata does not reflect V19-012 scope")
    return sorted(set(errors))


def validate(root: Path) -> list[str]:
    root = Path(root).resolve()
    parent = root.parent / "StageB_V18_20261103"
    if not parent.is_dir():
        return ["immutable V18 parent release unavailable"]
    try:
        return validate_records(
            root, rows(root, "data/interaction_evidence.csv"), rows(root, "provenance/source_audit.csv"),
            rows(root, "provenance/claim_support_and_verification.csv"), rows(root, "data/publication_bibliography.csv"),
            rows(root, "data/warning_ledger.csv"), rows(root, "validation/V19_warning_audit.csv"),
            rows(root, "validation/V19_batch_012_review.csv"), rows(parent, "data/warning_ledger.csv"),
        )
    except (OSError, csv.Error, json.JSONDecodeError) as exc:
        return [f"validation input unreadable: {exc}"]


if __name__ == "__main__":
    release = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    errors = validate(release)
    result = {"release": release.resolve().name, "batch": "V19-012", "status": "PASS" if not errors else "FAIL", "reviewed_records": 1, "source_tier": 3, "open_warning_ids": ["V19-W18"], "errors": errors}
    (release / "validation/V19_batch_012_integrity_results.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(bool(errors))
