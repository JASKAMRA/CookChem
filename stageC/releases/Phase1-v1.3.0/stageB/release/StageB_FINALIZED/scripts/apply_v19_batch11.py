"""Apply the V19-011 PMC full-text extraction for PMID 21870106."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.apply_v19_batch02 import DATE, ROOT, read_csv, write_csv

PMID = "21870106"
DOI = "10.1007/s00228-011-1108-2"
TITLE = "Repeated administration of berberine inhibits cytochromes P450 in humans."
URL = "https://pmc.ncbi.nlm.nih.gov/articles/PMC4898966/"
CACHE = "history/rebuild_artifacts/e6087e27abee52b102719512fdea5e34b85a2e0746eaea63037868f862944d8a_pmid_21870106.json"
LOCATOR = "PMC4898966 full text: Methods—Subjects and Study Design; probe-drug doses and sampling; Results; Table 1 and footnotes."
TARGETS = {
    "SB-0003": {
        "drug": "Midazolam", "probe_dose": "2 mg", "effect": "Repeated berberine increased midazolam exposure and reduced apparent oral clearance in the tested healthy-male probe study.",
        "direction": "increased midazolam exposure; reduced apparent oral clearance",
        "outcome": "Table 1 (n=17; mean ± SD; berberine/control GMR and 90% CI): AUC0–∞ 45.08 ± 34.84 vs 65.18 ± 55.13 ng·h/mL; GMR 140% (117–168%), p<0.01. AUC0–12 h 39.79 ± 27.87 vs 57.71 ± 46.96 ng·h/mL; GMR 137% (112–167%), p<0.05. Cmax 15.30 ± 10.31 vs 20.88 ± 14.18 ng/mL; GMR 138% (107–177%), p<0.05. CL/F 70.25 ± 40.32 vs 53.35 ± 32.70 L/h; GMR 73% (60–89%), p<0.05. Midazolam/1′-hydroxymidazolam ratio at 1 h 6.91 ± 3.50 vs 10.34 ± 3.50; GMR 159% (130–194%), p<0.01. Table 1 Tmax 0.66 ± 0.33 vs 0.99 ± 0.37 h; GMR 152% (120–192%), p<0.05; t1/2 3.03 ± 1.11 vs 3.66 ± 1.53 h; GMR 119% (101–139%), p<0.05. The abstract prose swaps the Tmax and t1/2 labels; the Table 1 labels and values are retained, with the discrepancy disclosed.",
        "endpoint": "Midazolam AUC0–∞, AUC0–12 h, Cmax, Tmax, t1/2, CL/F and 1-h midazolam/1′-hydroxymidazolam ratio; Table 1 values, units, GMRs, 90% CIs and significance markers verified.",
        "verified": "Table 1 reports n=17; AUC0–∞ GMR 140% (90% CI 117–168%), AUC0–12 h 137% (112–167%), Cmax 138% (107–177%), CL/F 73% (60–89%), Tmax 152% (120–192%) and t1/2 119% (101–139%). Table labels conflict with the abstract prose for Tmax and t1/2; the table labels are transcribed and the source discrepancy retained.",
        "limitation": "Small healthy Chinese male sample (17 completers) and a 14-day capsule regimen; probe pharmacokinetics do not establish a clinical outcome or ordinary-food exposure equivalence. The abstract prose swaps the Tmax/t1/2 values relative to Table 1; Table 1 is transcribed and the discrepancy remains visible.",
    },
    "SB-0004": {
        "drug": "Dextromethorphan", "probe_dose": "30 mg", "effect": "Repeated berberine increased the 0–8 h urinary dextromethorphan/dextrorphan ratio, indicating reduced CYP2D6 activity in this probe study.",
        "direction": "increased urinary parent/metabolite ratio; reduced CYP2D6 activity",
        "outcome": "Table 1 (n=17; mean ± SD; berberine/control GMR and 90% CI): 0–8 h urinary dextromethorphan/dextrorphan ratio 0.04 ± 0.04 vs 0.40 ± 0.37; GMR 979% (650–1,474%), p<0.01. Abstract describes the ratio as increased ninefold. This is a urinary metabolic ratio, not a measured dextromethorphan AUC or clinical outcome.",
        "endpoint": "0–8 h urinary dextromethorphan/dextrorphan metabolic ratio; Table 1 values, dimensionless ratio, GMR, 90% CI and significance marker verified.",
        "verified": "Table 1 reports 0–8 h urinary ratio 0.04 ± 0.04 in placebo and 0.40 ± 0.37 after berberine; GMR 979% (90% CI 650–1,474%), p<0.01; abstract reports a ninefold increase.",
        "limitation": "Small healthy Chinese male sample (17 completers) and a 14-day capsule regimen. Urinary metabolic ratio is a CYP2D6 phenotyping marker, not drug AUC or a clinical outcome; no ordinary-food exposure equivalence was tested.",
    },
    "SB-0005": {
        "drug": "Losartan", "probe_dose": "30 mg", "effect": "Repeated berberine increased the 0–8 h urinary losartan/E-3174 ratio; abstract, Results and Table 1 interpret this as reduced CYP2C9 activity. The Methods section inconsistently labels losartan as a CYP2C19 probe; see V19-W17.",
        "direction": "increased urinary parent/metabolite ratio; source interpretation is reduced CYP2C9 activity, with an internal target-label discrepancy",
        "outcome": "Table 1 (n=17; mean ± SD; berberine/control GMR and 90% CI): 0–8 h urinary losartan/E-3174 ratio 0.22 ± 0.16 vs 0.46 ± 0.33; GMR 202% (152–270%), p<0.01. Abstract and Results describe a doubled ratio and decreased CYP2C9 activity; the Methods probe list instead says CYP2C19. This is a urinary metabolic ratio, not a losartan AUC or clinical outcome.",
        "endpoint": "0–8 h urinary losartan/E-3174 metabolic ratio; Table 1 values, dimensionless ratio, GMR, 90% CI and significance marker verified. Source target labels conflict between Methods and abstract/Results/Table 1.",
        "verified": "Table 1 reports 0–8 h urinary ratio 0.22 ± 0.16 in placebo and 0.46 ± 0.33 after berberine; GMR 202% (90% CI 152–270%), p<0.01. Abstract, Results and Table 1 attribute the result to CYP2C9; Methods labels losartan CYP2C19, retained as an open source discrepancy under V19-W17.",
        "limitation": "Small healthy Chinese male sample (17 completers) and a 14-day capsule regimen. Urinary ratio is a phenotyping marker, not a clinical outcome. Methods mislabels the losartan probe target as CYP2C19, while abstract, Results and Table 1 say CYP2C9; source/expert adjudication remains open under V19-W17. No ordinary-food exposure equivalence was tested.",
    },
}


def apply() -> dict:
    cache_path = ROOT / CACHE
    payload = json.loads(cache_path.read_text(encoding="utf-8-sig"))
    items = payload.get("resultList", {}).get("result", [])
    if not any(str(x.get("pmid", x.get("id", ""))) == PMID and str(x.get("doi", "")).lower() == DOI.lower() for x in items):
        raise ValueError("archived MED JSON does not verify the PMID/DOI")

    ef, evidence, ebom = read_csv("data/interaction_evidence.csv")
    af, audits, abom = read_csv("provenance/source_audit.csv")
    cf, claims, cbom = read_csv("provenance/claim_support_and_verification.csv")
    baseline_path = ROOT.parent / "StageB_V18_20261103/data/interaction_evidence.csv"
    with baseline_path.open(encoding="utf-8-sig", newline="") as handle:
        baseline = {r["Evidence_ID"]: r for r in csv.DictReader(handle)}
    ev_by = {r["Evidence_ID"]: r for r in evidence}
    au_by = {r["Evidence_ID"]: r for r in audits}
    cl_by = {r["Evidence_ID"]: r for r in claims}
    if set(TARGETS) - ev_by.keys() or set(TARGETS) - au_by.keys() or set(TARGETS) - cl_by.keys():
        raise ValueError("one or more Batch 011 records are absent from evidence/audit/claim tables")
    if any(au_by[eid].get("Verification_Date") == DATE and "V19-011" in au_by[eid].get("Verification_Status", "") for eid in TARGETS):
        raise ValueError("Batch 011 appears already applied; refusing to duplicate the disposition")
    if any(ev_by[eid].get("PMID") != PMID or ev_by[eid].get("DOI", "").lower() != DOI.lower() for eid in TARGETS):
        raise ValueError("Batch 011 inherited publication mapping does not match PMID/DOI")

    review_fields = ["Batch", "Evidence_ID", "Compound_ID", "Compound", "Drug_Probe", "Study_ID", "PMID", "DOI", "Primary_Source_URL", "Source_Access_Status", "Local_Metadata_Cache", "Source_Locator", "Verification_Tier", "Review_Date", "Correction_Made", "Verified_Outcome", "Remaining_Limitation"]
    review_rows = []
    for eid, spec in TARGETS.items():
        row = ev_by[eid]
        if row.get("Compound") != "Berberine" or row.get("Drug") != spec["drug"]:
            raise ValueError(f"unexpected compound/drug attribution for {eid}")
        updates = {
            "Interaction_Effect": spec["effect"], "Mechanism": "Source-interpreted reduced CYP activity based on probe-drug pharmacokinetic or urinary parent/metabolite endpoints; not a demonstrated clinical outcome.",
            "Direction": spec["direction"], "Quantitative_Outcome": spec["outcome"],
            "Dose": f"Berberine capsules 300 mg orally three times daily (08:00, 16:00, 23:00) for 14 days; {spec['drug'].lower()} probe {spec['probe_dose']} administered before and at the end of each phase; 4-week washout.",
            "Population": "18 healthy Chinese men entered; 17 completed (one withdrew because of a schedule conflict); age 21.6 ± 1.5 years and weight 61.35 ± 3.89 kg.",
            "Study_Design": "Two-phase randomized crossover; 14-day placebo and berberine phases separated by a 4-week washout; probe administered before and after each phase.",
            "Limitations": spec["limitation"],
            "Confidence": "Primary PMC full-text Methods, Results and Table 1 reviewed; small study of healthy male participants, with source-level limitations recorded.",
            "Notes": "V19-011: Table 1 values, units, GMRs, 90% CIs and significance markers transcribed as reported. See per-record review; no clinical or ordinary-food inference made.",
            "Source_URL": URL, "Source_Cache": CACHE, "Source_Locator": LOCATOR,
        }
        if eid == "SB-0003":
            updates["Notes"] += " The abstract prose swaps Tmax/t1/2 labels relative to Table 1; table labels are retained and discrepancy disclosed."
        if eid == "SB-0005":
            updates["Notes"] += " Methods labels losartan as CYP2C19, while abstract/Results/Table 1 identify CYP2C9; V19-W17 remains open."
        row.update(updates)

        audit = au_by[eid]
        audit.update({
            "Source_URL": URL, "Source_Cache": CACHE, "Source_Locator": LOCATOR,
            "Verification_Status": "Tier 1: primary PMC full-text Methods, Results and Table 1 reviewed in V19-011",
            "Verification_Method": "Official PMC full-text indexed article content reviewed for Methods, Results, Table 1 and footnotes; PubMed bibliographic record and Springer abstract cross-checked. Direct PMC HTML rendering presented an anti-bot check; article content was accessed through official PMC indexed full-text text. Local cache retains PubMed metadata only.",
            "Verification_Level": "1", "Audit_Disposition": "V19_TIER_1_FULL_TEXT_REVIEWED; TABLE_1_NUMERICAL_REEXTRACTION; SOURCE_DISCREPANCY_RETAINED" if eid != "SB-0005" else "V19_TIER_1_FULL_TEXT_REVIEWED; TABLE_1_NUMERICAL_REEXTRACTION; V19-W17_OPEN_SOURCE_TARGET_LABEL_DISCREPANCY",
            "Reviewer": "Codex AI-assisted primary-source curation; expert adjudication remains open for flagged conflicts",
            "Verification_Date": DATE, "Disposition_Date": DATE, "Fields_Audited": "compound/drug attribution; tested capsule preparation; probe dose; study design/population; endpoints; original values/units/statistics; source discrepancies and limits",
            "Endpoint_Verified": spec["endpoint"], "Numerical_Outcome_Verified": spec["verified"],
            "Drug_Probe": spec["drug"],
            "V18_Unresolved_Discrepancy": (audit.get("V18_Unresolved_Discrepancy", "") + " V19-011 independently re-reviewed the PMC primary full-text article and Table 1; source-specific discrepancies are recorded in V19_batch_011_review.csv."),
        })
        claim = cl_by[eid]
        claim.update({
            "Source_Locator": LOCATOR,
            "Verification_Status": "V19-011: PMID 21870106 primary PMC full-text Methods, Results and Table 1 reviewed; source caveats retained.",
            "Numerical_Use": spec["verified"],
            "Limitations": spec["limitation"],
        })
        review_rows.append({
            "Batch": "V19-011", "Evidence_ID": eid, "Compound_ID": row["Compound_ID"], "Compound": "Berberine", "Drug_Probe": spec["drug"], "Study_ID": "PMID:" + PMID,
            "PMID": PMID, "DOI": DOI, "Primary_Source_URL": URL,
            "Source_Access_Status": "Primary PMC full-text indexed content reviewed, including Methods, Results, Table 1 and footnotes; PubMed record and Springer abstract cross-checked. Direct PMC page rendering challenged; content was accessed via official PMC indexed article text. Local archive stores bibliographic MED metadata only.",
            "Local_Metadata_Cache": CACHE, "Source_Locator": LOCATOR, "Verification_Tier": "1", "Review_Date": DATE,
            "Correction_Made": "Expanded the inherited abstract-level result with source-reported Table 1 values, units, GMRs, 90% CIs, significance markers, probe dose and participant flow; corrected the broken local metadata-cache pointer. Preserved the abstract/Table 1 Tmax/t1/2 label conflict for SB-0003 and opened V19-W17 for the losartan CYP2C19 versus CYP2C9 source-label discrepancy in SB-0005.",
            "Verified_Outcome": row["Quantitative_Outcome"], "Remaining_Limitation": spec["limitation"],
        })

    write_csv("data/interaction_evidence.csv", ef, evidence, ebom)
    write_csv("provenance/source_audit.csv", af, audits, abom)
    write_csv("provenance/claim_support_and_verification.csv", cf, claims, cbom)

    rf, reviews, rbom = read_csv("validation/V19_batch_011_review.csv") if (ROOT / "validation/V19_batch_011_review.csv").exists() else (review_fields, [], False)
    if reviews:
        raise ValueError("Batch 011 review artifact already exists")
    write_csv("validation/V19_batch_011_review.csv", review_fields, review_rows, rbom)

    wf, warnings, wbom = read_csv("data/warning_ledger.csv")
    waf, warning_audit, wabom = read_csv("validation/V19_warning_audit.csv")
    if any(r.get("Warning_ID") == "V19-W17" for r in warnings) or any(r.get("Warning_ID") == "V19-W17" for r in warning_audit):
        raise ValueError("V19-W17 already exists")
    w10 = next(r for r in warnings if r.get("Warning_ID") == "V19-W10")
    if w10.get("Audit_Status") != "RESOLVED":
        raise ValueError("V19-W10 must remain resolved after pointer repair")
    w10.update({
        "Description": w10["Description"] + " V19-011 found three additional evidence/source-audit rows for PMID 21870106 that still used the broken legacy sources/selected_21.json path.",
        "Affected": w10["Affected"] + " | SB-0003 | SB-0004 | SB-0005",
        "Action": w10["Action"] + " V19-011 scope expansion: repaired the remaining three evidence/source-audit pointers for PMID 21870106 to the existing matching MED JSON; revalidated PMID/DOI. The local metadata cache remains distinct from full-text review.",
        "After": w10["After"] + " V19-011 also repairs three residual row-level pointers for PMID 21870106; all affected evidence, source-audit and bibliography locators now resolve to the matching archived MED JSON.",
        "Resolution_Source": w10["Resolution_Source"] + "; V19_batch_011_review.csv; " + CACHE,
        "Audit_Rationale": w10["Audit_Rationale"] + " V19-011 identified and repaired residual broken evidence/source-audit cache pointers for SB-0003–SB-0005 after verifying the archived MED JSON PMID/DOI.",
        "Audit_Verification_Reference": w10["Audit_Verification_Reference"] + "; V19_batch_011_review.csv; archived MED JSON PMID/DOI for 21870106.",
    })
    w17 = {
        "Warning_ID": "V19-W17", "Code": "SOURCE_INTERNAL_PROBE_ENZYME_LABEL_CONFLICT",
        "Description": "For SB-0005 / PMID 21870106, Methods labels the 30 mg losartan probe as CYP2C19, but the abstract, Results and Table 1 label the losartan/E-3174 endpoint as CYP2C9. The same paper assigns omeprazole to CYP2C19. The source-internal target-label discrepancy is unresolved.",
        "Affected": "SB-0005; PMID 21870106",
        "Classification": "primary-source methodological discrepancy",
        "Before": "No V19 warning; inherited row attributes losartan/E-3174 to CYP2C9 based on the abstract-level interpretation.",
        "Action": "V19-011 reviewed PMC full-text Methods, Results and Table 1. Retained the Table 1/abstract/Results CYP2C9 interpretation with the exact urinary ratio and added this warning; did not infer an author correction or erase the inconsistent Methods label.",
        "After": "Open pending expert or source adjudication; CYP2C9 result attribution is explicitly caveated in SB-0005.",
        "Remaining_Limitations": "The paper does not reconcile the Methods CYP2C19 label with the abstract/Results/Table 1 CYP2C9 label. Source or independent pharmacology adjudication is required before removing this caveat.",
        "Resolution_Source": "V19_batch_011_review.csv; PMID 21870106, PMC4898966 Methods, Results and Table 1.",
        "Review_Date": DATE, "Audit_Status": "NEEDS_MANUAL_REVIEW", "Inherited_Severity": "NOT_RECORDED",
        "Audit_Rationale": "Methods names losartan as a CYP2C19 probe; the abstract, Results and Table 1 identify the same urinary losartan/E-3174 endpoint as CYP2C9. The primary source itself is internally inconsistent. The database preserves the table/abstract outcome and keeps the discrepancy visible for manual adjudication.",
        "Audit_Verification_Reference": "V19_batch_011_review.csv; https://pmc.ncbi.nlm.nih.gov/articles/PMC4898966/; Methods probe list; Results; Table 1 Losartan (CYP2C9).",
        "Audit_Dependencies": "Author/source clarification or independent pharmacology expert adjudication of the source-internal probe target label.",
        "V17_Ledger_Audit_Status": "NOT_IN_V18",
    }
    warnings.append(w17)
    write_csv("data/warning_ledger.csv", wf, warnings, wbom)
    warning_audit.append({
        "Warning_ID": "V19-W17", "V18_Status": "NEW_IN_V19", "V19_Status": "NEEDS_MANUAL_REVIEW",
        "V19_Recheck_Status": "OPEN_IN_V19-011; Methods and abstract/Results/Table 1 disagree on losartan CYP target",
        "V19_Review_Work": w17["Action"], "V19_Evidence_or_Rationale": w17["Audit_Verification_Reference"],
        "Remaining_Limitations": w17["Remaining_Limitations"],
    })
    wa10 = next(r for r in warning_audit if r.get("Warning_ID") == "V19-W10")
    wa10.update({
        "V19_Recheck_Status": "RESOLVED_IN_V19-004; SAME_ROOT_CAUSE_EXPANDED_AND_REPAIRED_IN_V19-005; V19-006; V19-007; V19-008; V19-009; V19-010; V19-011",
        "V19_Review_Work": w10["Action"], "V19_Evidence_or_Rationale": w10["Audit_Verification_Reference"],
        "Remaining_Limitations": "All repaired local JSON snapshots verify bibliographic metadata only; full-text scientific review is separately documented at the stated tier.",
    })
    write_csv("validation/V19_warning_audit.csv", waf, warning_audit, wabom)

    meta_path = ROOT / "release_metadata.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8-sig"))
    primary = meta["v19_primary_source_review"]
    batches = list(primary.get("batches_completed", []))
    if "V19-011" not in batches:
        batches.append("V19-011")
    statuses = ["RESOLVED", "PARTIALLY_RESOLVED", "STILL_VALID", "NEEDS_MANUAL_REVIEW", "NOT_APPLICABLE"]
    primary.update({
        "batches_completed": batches, "evidence_records_reviewed": 52,
        "tier_1_primary_full_text_records": 40, "tier_3_primary_abstract_records": 12,
        "records_corrected_or_reconstructed": 50, "source_review_remaining": 265,
        "warning_rows_preserved": len(warnings),
        "warning_status_counts": {s: sum(r.get("Audit_Status") == s for r in warnings) for s in statuses},
        "new_warning_count": 17, "warning_ids_added": [f"V19-W{i:02d}" for i in range(1, 18)],
        "warning_rows_individually_reviewed_in_v19": 19,
    })
    meta["last_completed_batch"] = 11
    meta["warning_count"] = len(warnings)
    meta["v19_validation"].update({
        "batch11_integrity": "PENDING_VALIDATION", "batch11_tests_passed": 0, "batch11_tests_failed": 0,
        "focused_v19_batch_tests": {"passed": 0, "failed": 0, "result": "PENDING_V19-011_TESTS"},
        "v19_exact_manifest": "PENDING_FINAL_PACKAGING", "v19_clean_copy_manifest": "PENDING_FINAL_PACKAGING",
    })
    meta["readiness"] = meta["release_status"] = "SCIENTIFIC_REMEDIATION_IN_PROGRESS"
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return {"batch": "V19-011", "records_reviewed": 3, "tier": 1, "warnings_added": ["V19-W17"], "warning_rows": len(warnings), "status": "APPLIED_PENDING_VALIDATION"}


if __name__ == "__main__":
    print(json.dumps(apply(), indent=2, ensure_ascii=False))
