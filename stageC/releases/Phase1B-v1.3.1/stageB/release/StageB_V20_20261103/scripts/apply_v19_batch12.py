"""Apply V19-012 primary-abstract review for SB-0013 / PMID 27981349."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.apply_v19_batch02 import DATE, ROOT, read_csv, write_csv

EID = "SB-0013"
PMID = "27981349"
DOI = "10.1007/s00228-016-2173-3"
TITLE = "The influence of piperine on the pharmacokinetics of fexofenadine, a P-glycoprotein substrate, in healthy volunteers."
PUBMED_URL = "https://pubmed.ncbi.nlm.nih.gov/27981349/"
PUBLISHER_URL = "https://link.springer.com/article/10.1007/s00228-016-2173-3"
CACHE = "history/rebuild_artifacts/fc2955e97491d07e530c79de0c2df8ae78ef5e48d845f659a4ff8a8c6ea20f3e_selected_32.json"
LOCATOR = "PubMed primary abstract: Methods and Results; Springer Nature publisher abstract; full text shown as subscription preview and not accessible."


def apply() -> dict:
    cache = json.loads((ROOT / CACHE).read_text(encoding="utf-8-sig"))
    items = cache.get("resultList", {}).get("result", [])
    if not any(str(x.get("pmid", x.get("id", ""))) == PMID and str(x.get("doi", "")).lower() == DOI.lower() for x in items):
        raise ValueError("local MED metadata does not verify PMID/DOI")

    def get_rows(rel):
        return read_csv(rel)

    ef, evidence, ebom = get_rows("data/interaction_evidence.csv")
    af, audits, abom = get_rows("provenance/source_audit.csv")
    cf, claims, cbom = get_rows("provenance/claim_support_and_verification.csv")
    bf, bibliography, bbom = get_rows("data/publication_bibliography.csv")
    wf, warnings, wbom = get_rows("data/warning_ledger.csv")
    waf, warning_audit, wabom = get_rows("validation/V19_warning_audit.csv")
    eid_rows = {r["Evidence_ID"]: r for r in evidence}
    audit_rows = {r["Evidence_ID"]: r for r in audits}
    claim_rows = {r["Evidence_ID"]: r for r in claims}
    target = eid_rows.get(EID)
    audit = audit_rows.get(EID)
    claim = claim_rows.get(EID)
    pub = next((r for r in bibliography if r.get("PMID") == PMID), None)
    if not all((target, audit, claim, pub)):
        raise ValueError("SB-0013 or its source/provenance rows are missing")
    if target.get("PMID") != PMID or target.get("DOI", "").lower() != DOI.lower():
        raise ValueError("SB-0013 publication identity mismatch")
    if audit.get("Verification_Date") == DATE and "V19-012" in audit.get("Verification_Status", ""):
        raise ValueError("V19-012 appears already applied")
    if any(r.get("Warning_ID") == "V19-W18" for r in warnings + warning_audit):
        raise ValueError("V19-W18 already exists")

    outcome = ("Official primary abstract (control vs after 10-day piperine treatment): fexofenadine Cmax 406.9 vs 767 ng/mL; AUC 3403.7 vs 5724.7 ng·h/mL; apparent oral clearance 35.4 vs 20.7 L/h. The abstract reports these changes as significant but provides no p values, dispersion or confidence intervals. It does not state the AUC interval; no AUC0–t or AUC0–∞ label is inferred. Half-life and renal clearance were reported as not significantly changed.")
    limitation = ("Tier 3: primary abstract only; publisher page identifies the full article as subscription content. The abstract does not state the AUC interval or report p values, dispersion or confidence intervals. Small open-label sequential study (n=12); P-gp inhibition is the authors' proposed attribution, not directly demonstrated in this human study. The 20-mg piperine dose is not an ordinary-food exposure equivalence.")
    target.update({
        "Interaction_Effect": "Piperine treatment significantly increased fexofenadine Cmax and AUC and reduced apparent oral clearance in the abstract-reported study.",
        "Mechanism": "P-glycoprotein efflux inhibition proposed by the authors; not directly demonstrated in this human study.",
        "Direction": "increased fexofenadine exposure; reduced apparent oral clearance",
        "Quantitative_Outcome": outcome,
        "Dose": "Piperine 20 mg orally once daily for 10 days; fexofenadine 120 mg as a single oral dose during control and after treatment.",
        "Population": "12 healthy volunteers; abstract does not report sex distribution.",
        "Study_Design": "Open-label, two-period sequential study; control phase followed by a 10-day once-daily piperine treatment phase and repeat single-dose fexofenadine.",
        "Limitations": limitation,
        "Confidence": "Primary human pharmacokinetic evidence; Tier 3 abstract only, small sequential study, and AUC interval is unspecified in accessible abstract.",
        "Notes": "V19-012: abstract confirms the direction, values, units, study design and doses. Exact AUC interval, p values, variance, and table-level detail remain unverified; see V19-W18.",
        "Source_URL": PUBMED_URL, "Source_Cache": CACHE, "Source_Locator": LOCATOR,
    })
    audit.update({
        "Source_URL": PUBMED_URL, "Source_Cache": CACHE, "Source_Locator": LOCATOR,
        "Verification_Status": "Tier 3: primary PubMed and publisher abstracts reviewed in V19-012; full article unavailable in accessible publisher preview",
        "Verification_Level": "3", "Verification_Date": DATE,
        "Verification_Method": "Official PubMed record and Springer publisher abstract reviewed and cross-checked; publisher page marks full text as subscription preview. Local MED JSON verifies bibliographic metadata only.",
        "Audit_Disposition": "V19_TIER_3_PRIMARY_ABSTRACT_REVIEWED; AUC_INTERVAL_UNSPECIFIED; FULL_TEXT_PENDING",
        "Reviewer": "Codex AI-assisted primary-source curation; full-text review remains pending",
        "Fields_Audited": "publication identity; abstract-level compound/drug attribution; study design/population; tested doses; reported endpoint direction, values and units; accessible-source limitations",
        "Endpoint_Verified": "Abstract reports fexofenadine Cmax, AUC (interval unspecified) and apparent oral clearance; half-life and renal clearance nonsignificant; no p values or variance in abstract.",
        "Numerical_Outcome_Verified": outcome,
        "V18_Unresolved_Discrepancy": "V18 source content was not reopened. V19-012 verified the primary abstract but full-text AUC interval and table statistics remain unverified under V19-W18.",
        "Disposition_Date": DATE,
    })
    claim.update({
        "Source_Locator": LOCATOR,
        "Verification_Status": "V19-012: primary PubMed and Springer abstracts reviewed; full text unavailable in accessible publisher preview.",
        "Numerical_Use": outcome,
        "Limitations": limitation,
    })
    pub["Source"] = CACHE

    review_fields = ["Batch", "Evidence_ID", "Compound_ID", "Compound", "Drug_Probe", "Study_ID", "PMID", "DOI", "Primary_Source_URL", "Source_Access_Status", "Local_Metadata_Cache", "Source_Locator", "Verification_Tier", "Review_Date", "Correction_Made", "Verified_Outcome", "Remaining_Limitation"]
    review = [{
        "Batch": "V19-012", "Evidence_ID": EID, "Compound_ID": target["Compound_ID"], "Compound": target["Compound"], "Drug_Probe": target["Drug"], "Study_ID": target["Study_ID"],
        "PMID": PMID, "DOI": DOI, "Primary_Source_URL": PUBMED_URL,
        "Source_Access_Status": "Official PubMed abstract and Springer publisher abstract accessed and cross-checked. Publisher page exposes abstract and states subscription content for full text; no full-text claim is made.",
        "Local_Metadata_Cache": CACHE, "Source_Locator": LOCATOR, "Verification_Tier": "3", "Review_Date": DATE,
        "Correction_Made": "Made control/treatment attribution explicit, retained all abstract values and units, recorded tested doses/design, repaired the missing local MED metadata pointers, and documented that the abstract omits the AUC interval. Opened V19-W18; no endpoint interval, p value, variance or CI was inferred.",
        "Verified_Outcome": outcome, "Remaining_Limitation": limitation,
    }]
    write_csv("data/interaction_evidence.csv", ef, evidence, ebom)
    write_csv("provenance/source_audit.csv", af, audits, abom)
    write_csv("provenance/claim_support_and_verification.csv", cf, claims, cbom)
    write_csv("data/publication_bibliography.csv", bf, bibliography, bbom)
    write_csv("validation/V19_batch_012_review.csv", review_fields, review, False)

    w10 = next(r for r in warnings if r.get("Warning_ID") == "V19-W10")
    w10.update({
        "Description": w10["Description"] + " V19-012 also found a broken legacy metadata path for PMID 27981349, affecting SB-0013 and its bibliography row.",
        "Affected": w10["Affected"] + " | SB-0013 | bibliography PMID 27981349",
        "Action": w10["Action"] + " V19-012 repaired the SB-0013 source-audit/evidence pointers and bibliography metadata path for PMID 27981349 after confirming the archived MED JSON PMID/DOI.",
        "After": w10["After"] + " V19-012 also repaired the local metadata pointers for PMID 27981349; all scoped pointer targets exist and match their publication identifiers.",
        "Resolution_Source": w10["Resolution_Source"] + "; V19_batch_012_review.csv; " + CACHE,
        "Audit_Rationale": w10["Audit_Rationale"] + " V19-012 repaired residual broken evidence, source-audit and bibliography pointers for PMID 27981349 after verifying the matching archived MED JSON.",
        "Audit_Verification_Reference": w10["Audit_Verification_Reference"] + "; V19_batch_012_review.csv; archived MED JSON PMID/DOI for 27981349.",
    })
    w18 = {
        "Warning_ID": "V19-W18", "Code": "ABSTRACT_AUC_INTERVAL_UNSPECIFIED",
        "Description": "For SB-0013 / PMID 27981349, the accessible primary abstract reports fexofenadine AUC increasing from 3403.7 to 5724.7 ng·h/mL but does not specify the AUC interval. The subscription-only full text and tables were not accessible, so the exact endpoint cannot be confirmed.",
        "Affected": "SB-0013; PMID 27981349", "Classification": "primary-source endpoint specification gap",
        "Before": "Outcome field stated AUC values without phase labels or the AUC interval; no new V19 abstract review recorded.",
        "Action": "V19-012 reviewed the PubMed and publisher abstracts; clarified control/treatment order and preserved the reported values/units, but retained an unspecified AUC interval and opened this warning. No interval or statistical detail was inferred.",
        "After": "Open pending legitimate full-text/table access or source clarification; AUC interval remains unspecified.",
        "Remaining_Limitations": "The abstract omits the AUC sampling interval and detailed statistics. Full article is subscription content in the accessible publisher view; no inference between AUC0–t and AUC0–∞ is justified.",
        "Resolution_Source": "V19_batch_012_review.csv; PubMed PMID 27981349 abstract; Springer Nature publisher abstract.",
        "Review_Date": DATE, "Audit_Status": "NEEDS_MANUAL_REVIEW", "Inherited_Severity": "NOT_RECORDED",
        "Audit_Rationale": "The numerical AUC values and unit are in the primary abstract, but endpoint interval is absent. Full text is not accessible in the current publisher view, so the endpoint remains underspecified and is not normalized.",
        "Audit_Verification_Reference": "V19_batch_012_review.csv; https://pubmed.ncbi.nlm.nih.gov/27981349/; https://link.springer.com/article/10.1007/s00228-016-2173-3.",
        "Audit_Dependencies": "Legitimate full-text/table access or author/source clarification of AUC interval.",
        "V17_Ledger_Audit_Status": "NOT_IN_V18",
    }
    warnings.append(w18)
    write_csv("data/warning_ledger.csv", wf, warnings, wbom)
    warning_audit.append({
        "Warning_ID": "V19-W18", "V18_Status": "NEW_IN_V19", "V19_Status": "NEEDS_MANUAL_REVIEW",
        "V19_Recheck_Status": "OPEN_IN_V19-012; accessible abstract omits AUC interval",
        "V19_Review_Work": w18["Action"], "V19_Evidence_or_Rationale": w18["Audit_Verification_Reference"],
        "Remaining_Limitations": w18["Remaining_Limitations"],
    })
    wa10 = next(r for r in warning_audit if r.get("Warning_ID") == "V19-W10")
    wa10.update({
        "V19_Recheck_Status": "RESOLVED_IN_V19-004; SAME_ROOT_CAUSE_EXPANDED_AND_REPAIRED_IN_V19-005; V19-006; V19-007; V19-008; V19-009; V19-010; V19-011; V19-012",
        "V19_Review_Work": w10["Action"], "V19_Evidence_or_Rationale": w10["Audit_Verification_Reference"],
        "Remaining_Limitations": "Repaired local JSON snapshots verify bibliographic metadata only; scientific source review is documented at its separate stated tier.",
    })
    write_csv("validation/V19_warning_audit.csv", waf, warning_audit, wabom)

    meta_path = ROOT / "release_metadata.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8-sig"))
    primary = meta["v19_primary_source_review"]
    batches = list(primary.get("batches_completed", []))
    if "V19-012" not in batches:
        batches.append("V19-012")
    statuses = ["RESOLVED", "PARTIALLY_RESOLVED", "STILL_VALID", "NEEDS_MANUAL_REVIEW", "NOT_APPLICABLE"]
    primary.update({
        "batches_completed": batches, "evidence_records_reviewed": 53,
        "tier_1_primary_full_text_records": 40, "tier_3_primary_abstract_records": 13,
        "records_corrected_or_reconstructed": 51, "source_review_remaining": 264,
        "warning_rows_preserved": len(warnings),
        "warning_status_counts": {s: sum(r.get("Audit_Status") == s for r in warnings) for s in statuses},
        "new_warning_count": 18, "warning_ids_added": [f"V19-W{i:02d}" for i in range(1, 19)],
        "warning_rows_individually_reviewed_in_v19": 20,
    })
    meta["warning_count"] = len(warnings)
    meta["last_completed_batch"] = 12
    meta["v19_validation"].update({
        "batch12_integrity": "PENDING_VALIDATION", "batch12_tests_passed": 0, "batch12_tests_failed": 0,
        "focused_v19_batch_tests": {"passed": 0, "failed": 0, "result": "PENDING_V19-012_TESTS"},
        "v19_exact_manifest": "PENDING_FINAL_PACKAGING", "v19_clean_copy_manifest": "PENDING_FINAL_PACKAGING",
    })
    meta["readiness"] = meta["release_status"] = "SCIENTIFIC_REMEDIATION_IN_PROGRESS"
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return {"batch": "V19-012", "records_reviewed": 1, "tier": 3, "warnings_added": ["V19-W18"], "warning_rows": len(warnings), "status": "APPLIED_PENDING_VALIDATION"}


if __name__ == "__main__":
    print(json.dumps(apply(), indent=2, ensure_ascii=False))
