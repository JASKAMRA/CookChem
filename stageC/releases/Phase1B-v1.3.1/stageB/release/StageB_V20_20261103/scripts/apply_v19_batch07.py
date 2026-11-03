"""Apply V19-007 human probe-study re-extraction for two blank outcome records."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.apply_v19_batch02 import DATE, ROOT, read_csv, update_rows, write_csv

PMID = "21870106"
DOI = "10.1007/s00228-011-1108-2"
TITLE = "Repeated administration of berberine inhibits cytochromes P450 in humans."
URL = "https://pmc.ncbi.nlm.nih.gov/articles/PMC4898966/"
CACHE = "history/rebuild_artifacts/e6087e27abee52b102719512fdea5e34b85a2e0746eaea63037868f862944d8a_pmid_21870106.json"
RECORDS = {
    "SB-0187": {
        "drug": "Caffeine",
        "locator": "PMC4898966 full text: Methods—randomized crossover study and probe-drug regimen; Results; Table 1—Caffeine (CYP1A2); Discussion—CYP1A2 interpretation.",
        "effect": "No statistically significant caffeine pharmacokinetic or caffeine/paraxanthine-ratio difference was detected after repeated berberine under this study's analysis. The reported AUC/Cmax confidence intervals do not establish equivalence, so this is not evidence that the effect is exactly zero.",
        "direction": "No statistically significant PK difference detected; caffeine AUC/Cmax estimates were lower with berberine, with confidence intervals crossing/breaching the 80% lower equivalence boundary.",
        "outcome": "Table 1 (n=17; mean ± SD; berberine/control geometric mean ratio and 90% CI): caffeine 93 mg probe. AUC0–∞ 33.98 ± 9.40 vs 29.80 ± 11.30 μg·h/mL; ratio 85% (76–95%). Cmax 4.48 ± 1.03 vs 4.16 ± 1.86 μg/mL; 88% (75–103%). Tmax 0.96 ± 0.45 vs 1.00 ± 0.41 h; 108% (86–135%). t1/2 5.41 ± 1.81 vs 4.75 ± 1.15 h; 89% (78–102%). Plasma caffeine/paraxanthine ratio at 6 h: 1.51 ± 2.06 vs 0.94 ± 0.45; 80% (59–108%). Results state there were no statistically significant PK differences; Table 1 shows no significance marker. The article notes caffeine AUC0–∞ and Cmax did not meet its 80–125% bioequivalence criterion, despite nonsignificance, and cites small sample size as a possible explanation. This result is not evidence of equivalence or absence of effect.",
        "dose": "Berberine capsules 300 mg orally three times daily for 14 days; caffeine 93 mg as a CYP1A2 probe before and at the end of each phase. The article describes 93 mg as the content of a standard cup of coffee; beverage composition is not otherwise characterized.",
        "population": "18 healthy Chinese male volunteers entered and 17 completed (one withdrew for a schedule conflict); age 21.6 ± 1.5 years and weight 61.35 ± 3.89 kg, mean ± SD.",
        "design": "Two-phase randomized crossover probe study with placebo and berberine periods, 4-week washout, and 14-day treatment per period. A five-drug cocktail was administered before and at the end of each period; plasma sampling continued through 12 h. Caffeine and its metabolite were measured as CYP1A2 indices.",
        "limitations": "One small study in healthy young Chinese men (17 completers), one 14-day berberine-capsule regimen and one 93-mg caffeine probe. Nonsignificance does not prove no effect; reported caffeine AUC/Cmax 90% CIs do not lie wholly within 80–125% equivalence bounds. Berberine capsule salt/content/excipients and coffee beverage matrix are not fully characterized. Not an ordinary dietary interaction study or dose-equivalence assessment.",
        "preparation": "Berberine capsules supplied by Yunnan Baiyao Group Dali Pharmaceutical; paper reports 300 mg per dose but does not specify salt, assayed berberine content or excipients. Caffeine probe reported as 93 mg, described as the content in a standard cup of coffee.",
        "endpoint": "Caffeine AUC0–∞, Cmax, Tmax, t1/2 and plasma caffeine/paraxanthine ratio at 6 h; CYP1A2 probe outcomes.",
        "numerical": "Primary Table 1 directly provides the caffeine means ± SD, geometric ratios and 90% CIs; Results state no significant parameter differences; Discussion distinguishes nonsignificance from failure to meet the stated equivalence bounds.",
    },
    "SB-0188": {
        "drug": "Omeprazole",
        "locator": "PMC4898966 full text: Methods—randomized crossover study and probe-drug regimen; Results; Table 1—Omeprazole (CYP2C19); Discussion.",
        "effect": "No statistically significant omeprazole pharmacokinetic or omeprazole/5-hydroxyomeprazole-ratio difference was detected after repeated berberine under the tested regimen; the small study does not establish absence of an effect.",
        "direction": "No statistically significant difference detected in the measured omeprazole PK or phenotypic ratio outcomes.",
        "outcome": "Table 1 (n=17; mean ± SD; berberine/control geometric mean ratio and 90% CI): omeprazole 20 mg probe. AUC0–∞ 1.73 ± 1.86 vs 1.47 ± 1.48 μg·h/mL; ratio 98% (81–120%). Cmax 0.52 ± 0.45 vs 0.44 ± 0.25 μg/mL; 99% (84–117%). Tmax 1.47 ± 0.82 vs 1.49 ± 0.54 h; 107% (90–128%). t1/2 4.00 ± 1.69 vs 3.41 ± 1.61 h; 85% (70–103%). CL/F 24.13 ± 17.40 vs 21.70 ± 12.29 L/h; 102% (84–124%). Plasma omeprazole/5-hydroxyomeprazole ratio at 4 h: 6.83 ± 9.94 vs 7.34 ± 9.61; 121% (82–179%). Results state there were no statistically significant differences; Table 1 shows no significance marker. Values are retained as reported and are not evidence that all CYP2C19 effects are absent.",
        "dose": "Berberine capsules 300 mg orally three times daily for 14 days; omeprazole 20 mg as a CYP2C19 probe before and at the end of each study period. Probe cocktail administered at 08:00; food was permitted 3 h later.",
        "population": "18 healthy Chinese male volunteers entered and 17 completed (one withdrew for a schedule conflict); age 21.6 ± 1.5 years and weight 61.35 ± 3.89 kg, mean ± SD.",
        "design": "Two-phase randomized crossover probe study with placebo and berberine periods, 4-week washout, and 14-day treatment per period. Omeprazole was one component of a five-drug cocktail administered before and at the end of each period; plasma sampling continued through 12 h.",
        "limitations": "One small study in healthy young Chinese men (17 completers), one 14-day berberine-capsule regimen and a single 20-mg omeprazole probe. Nonsignificance does not establish pharmacokinetic equivalence or absence of interaction. Berberine capsule salt/content/excipients were not fully characterized; no ordinary dietary exposure or clinical patient outcome was studied.",
        "preparation": "Berberine capsules supplied by Yunnan Baiyao Group Dali Pharmaceutical; paper reports 300 mg per dose but does not specify salt, assayed berberine content or excipients. Omeprazole 20 mg administered as a CYP2C19 probe.",
        "endpoint": "Omeprazole AUC0–∞, Cmax, Tmax, t1/2, CL/F and plasma omeprazole/5-hydroxyomeprazole ratio at 4 h; CYP2C19 probe outcomes.",
        "numerical": "Primary Table 1 directly provides the omeprazole means ± SD, geometric ratios and 90% CIs; Results state no significant parameter differences. No values were inferred from Figure 1.",
    },
}


def verify_cache(path: Path) -> None:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    items = payload.get("resultList", {}).get("result", [])
    if not any(str(item.get("pmid", item.get("id", ""))) == PMID and str(item.get("doi", "")).lower() == DOI.lower() for item in items):
        raise ValueError("archived MED metadata does not verify PMID 21870106 and its DOI")


def apply() -> dict[str, object]:
    parent = ROOT.parent / "StageB_V18_20261103"
    if not parent.is_dir():
        raise FileNotFoundError("immutable V18 parent release is required")
    verify_cache(ROOT / CACHE)
    baseline = {r["Evidence_ID"]: r for r in read_csv("../StageB_V18_20261103/data/interaction_evidence.csv")[1]}
    baseline_blank = {eid for eid, row in baseline.items() if not row.get("Quantitative_Outcome", "").strip()}
    if len(baseline_blank) != 90 or not set(RECORDS) <= baseline_blank:
        raise ValueError("Batch 007 targets must be among the original V18 blank outcomes")
    current = {r["Evidence_ID"]: r for r in read_csv("data/interaction_evidence.csv")[1]}
    if any(current[eid].get("Quantitative_Outcome", "").strip() for eid in RECORDS):
        raise ValueError("Batch 007 target outcome already populated; refusing duplicate application")

    evidence_updates, audit_updates, claim_updates = {}, {}, {}
    review_fields = ["Batch", "Evidence_ID", "Compound_ID", "Compound", "Drug_Probe", "Study_ID", "PMID", "DOI", "Primary_Source_URL", "Source_Access_Status", "Local_Metadata_Cache", "Source_Locator", "Verification_Tier", "Review_Date", "Correction_Made", "Verified_Outcome", "Remaining_Limitation"]
    review_rows = []
    authors = "Guo Y, Chen Y, Tan ZR, Klaassen CD, Zhou HH."
    for eid, spec in RECORDS.items():
        row = current[eid]
        evidence_updates[eid] = {
            "Interaction_Effect": spec["effect"],
            "Mechanism": "The outcomes are CYP1A2 (caffeine) or CYP2C19 (omeprazole) phenotyping-probe measurements; this small study found no statistically significant difference for these probes and does not establish the absence of an effect.",
            "Direction": spec["direction"], "Quantitative_Outcome": spec["outcome"],
            "Dose": spec["dose"], "Population": spec["population"], "Study_Design": spec["design"],
            "Limitations": spec["limitations"],
            "Confidence": "Primary full-text randomized human probe study reviewed; small single-study evidence with source-reported estimates retained; independent expert re-review not performed.",
            "Notes": "V19-007: Table 1 values and source interpretation were transcribed; no inference of equivalence or a true null effect from nonsignificance.",
            "Source_Title": TITLE, "Authors": authors, "Year": "2012", "DOI": DOI, "PMID": PMID,
            "Source_Type": "Primary research", "Study_ID": "PMID:" + PMID, "Source_URL": URL,
            "Source_Cache": CACHE, "Source_Locator": spec["locator"], "Preparation": spec["preparation"],
            "Identity_Status": "source-reported berberine capsules; exact salt, assay and excipient composition not specified",
            "Outcome": "no statistically significant PK change under tested conditions",
        }
        audit_updates[eid] = {
            "PMID": PMID, "DOI": DOI, "Source_Title": TITLE, "Source_URL": URL,
            "Source_Cache": CACHE, "Source_Locator": spec["locator"],
            "Verification_Status": "Tier 1: primary full text, Methods, Results and Table 1 directly reviewed in V19-007",
            "Fields_Audited": "berberine capsule preparation; probe identity/dose; population and crossover design; treatment duration/washout; sample flow; PK endpoints, units, ratios and confidence intervals; statistical test and limitations",
            "Limitations": spec["limitations"], "Source_Type": "Primary research", "Verification_Date": DATE,
            "Verification_Method": "Original PMC full text directly reviewed: Methods, Results, Table 1 and Discussion; PMID/DOI independently checked in PubMed MED JSON. Table values and 90% confidence intervals transcribed; no non-significant value treated as proof of equivalence.",
            "Verification_Level": "1", "Audit_Disposition": "V19_TIER_1_FULL_TEXT_REVIEWED; TABLE_1_NUMERICAL_OUTCOME_RECOVERED; NULL_INFERENCE_RESTRICTED",
            "Reviewer": "Codex AI-assisted primary-source curation; independent expert re-review not performed.",
            "Endpoint_Verified": spec["endpoint"], "Numerical_Outcome_Verified": spec["numerical"],
            "Study_ID": "PMID:" + PMID, "Compound_ID": row["Compound_ID"], "Drug_Probe": spec["drug"],
            "V18_Unresolved_Discrepancy": "V19-007 directly reviewed the primary source. Nonsignificant caffeine results are not interpreted as equivalence; the source's 80–125% equivalence-bound discussion is retained.",
        }
        claim_updates[eid] = {
            "Compound_ID": row["Compound_ID"], "PMID": PMID, "Source_Locator": spec["locator"],
            "Verification_Status": "Primary full-text human probe-study review completed in V19-007; Table 1 estimates and limits on null/equivalence interpretation recorded.",
            "Numerical_Use": spec["numerical"], "Attribution": "Berberine / " + spec["drug"], "Limitations": spec["limitations"],
        }
        review_rows.append({
            "Batch": "V19-007", "Evidence_ID": eid, "Compound_ID": row["Compound_ID"], "Compound": row["Compound"],
            "Drug_Probe": spec["drug"], "Study_ID": "PMID:" + PMID, "PMID": PMID, "DOI": DOI,
            "Primary_Source_URL": URL,
            "Source_Access_Status": "Primary PMC full-text article reviewed; Methods, Results, Table 1 and Discussion accessed. PubMed MED metadata independently verifies publication identity. No supplementary file was needed for the Table 1 outcomes.",
            "Local_Metadata_Cache": CACHE, "Source_Locator": spec["locator"], "Verification_Tier": 1,
            "Review_Date": DATE,
            "Correction_Made": "Replaced the inherited blank outcome and abstract-only/pending source disposition with exact Table 1 probe-drug estimates, units, 90% CIs, study design, sample flow and source-specific statistical limitations. Repaired the legacy PMID cache pointer under the existing V19-W10 root-cause warning.",
            "Verified_Outcome": spec["outcome"], "Remaining_Limitation": spec["limitations"],
        })

    update_rows("data/interaction_evidence.csv", "Evidence_ID", evidence_updates)
    update_rows("provenance/source_audit.csv", "Evidence_ID", audit_updates)
    update_rows("provenance/claim_support_and_verification.csv", "Evidence_ID", claim_updates)
    update_rows("data/publication_bibliography.csv", "PMID", {PMID: {"Source": CACHE}})
    with (ROOT / "validation/V19_batch_007_review.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=review_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(review_rows)
    update_rows("data/study_registry.csv", "Study_ID", {
        "PMID:" + PMID: {"Verification_Status": "V19-007: PMC primary full text, Methods, Results, Table 1 and Discussion independently reviewed for SB-0187/0188. Recorded the n=17 crossover, four-week washout, probe doses, caffeine/omeprazole PK values, 90% CIs and the limits of interpreting nonsignificance."},
    })

    fields, warnings, bom = read_csv("data/warning_ledger.csv")
    w10 = next((r for r in warnings if r["Warning_ID"] == "V19-W10"), None)
    if not w10 or w10.get("Audit_Status") != "RESOLVED":
        raise ValueError("V19-W10 must remain resolved before its verified scope expansion")
    w10.update({
        "Description": w10["Description"].replace("and PMID 27765854", ", PMID 27765854 and PMID 21870106"),
        "Affected": w10["Affected"] + " | SB-0187 | SB-0188 | bibliography PMID 21870106",
        "Action": w10["Action"] + " V19-007 scope expansion: repaired the missing legacy MED metadata locator for PMID 21870106 across both evidence/source-audit rows and its bibliography pointer; matching PMID/DOI in the archived JSON was verified.",
        "After": w10["After"] + " V19-007 also repairs PMID 21870106; all six audited PMID metadata snapshots now resolve within V19.",
        "Resolution_Source": w10["Resolution_Source"] + "; V19_batch_007_review.csv; " + CACHE,
        "Review_Date": DATE,
        "Audit_Rationale": w10["Audit_Rationale"] + " V19-007 verified the existing PMID 21870106 MED JSON DOI and repaired both evidence/source-audit references and the bibliography source path.",
        "Audit_Verification_Reference": w10["Audit_Verification_Reference"] + "; V19_batch_007_review.csv; archived PMID 21870106 MED metadata JSON.",
    })
    write_csv("data/warning_ledger.csv", fields, warnings, bom)
    update_rows("validation/V19_warning_audit.csv", "Warning_ID", {
        "V19-W10": {
            "V19_Recheck_Status": "RESOLVED_IN_V19-004; SAME_ROOT_CAUSE_EXPANDED_AND_REPAIRED_IN_V19-005; SAME_ROOT_CAUSE_EXPANDED_AND_REPAIRED_IN_V19-006; SAME_ROOT_CAUSE_EXPANDED_AND_REPAIRED_IN_V19-007",
            "V19_Review_Work": w10["Action"], "V19_Evidence_or_Rationale": w10["Audit_Verification_Reference"],
            "Remaining_Limitations": "All six local JSON snapshots are bibliographic metadata only; full-text scientific review is separately recorded per evidence record.",
        },
    })

    metadata_path = ROOT / "release_metadata.json"
    meta = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    review = meta["v19_primary_source_review"]
    batches = list(review.get("batches_completed", []))
    if "V19-007" not in batches:
        batches.append("V19-007")
    review.update({
        "batches_completed": batches, "evidence_records_reviewed": 34,
        "tier_1_primary_full_text_records": 34, "records_corrected_or_reconstructed": 32,
        "source_review_remaining": 283, "warning_rows_preserved": 83,
        "warning_status_counts": {s: sum(r.get("Audit_Status") == s for r in warnings) for s in ["RESOLVED", "PARTIALLY_RESOLVED", "STILL_VALID", "NEEDS_MANUAL_REVIEW", "NOT_APPLICABLE"]},
        "new_warning_count": 13, "warning_ids_added": [f"V19-W{i:02d}" for i in range(1, 14)],
        "warning_rows_individually_reviewed_in_v19": 15,
    })
    meta["warning_count"] = len(warnings)
    meta["v19_quantitative_outcome_audit"].update({
        "quantitative_values_recovered": 26, "qualitative_outcomes_dispositioned": 5,
        "blank_fields_remaining": 59, "source_review_batch": "V19-007",
    })
    meta["v19_validation"].update({
        "batch06_integrity": "PASS", "batch06_tests_passed": 12, "batch06_tests_failed": 0,
        "batch07_integrity": "PENDING_VALIDATION", "batch07_tests_passed": 0, "batch07_tests_failed": 0,
        "full_stageB_regression": "PENDING_FINAL_VALIDATION",
        "v19_exact_manifest": "PENDING_FINAL_PACKAGING", "v19_clean_copy_manifest": "PENDING_FINAL_PACKAGING",
    })
    meta["readiness"] = meta["release_status"] = "SCIENTIFIC_REMEDIATION_IN_PROGRESS"
    metadata_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"batch": "V19-007", "records_updated": 2, "tier_1_human_full_text_reviews": 2,
            "quantitative_outcomes_recovered": 2, "blank_outcomes_remaining": 59,
            "V19-W10": "RESOLVED; scope expanded to six verified MED metadata snapshots", "status": "APPLIED_PENDING_VALIDATION"}


if __name__ == "__main__":
    print(json.dumps(apply(), indent=2, ensure_ascii=False))
