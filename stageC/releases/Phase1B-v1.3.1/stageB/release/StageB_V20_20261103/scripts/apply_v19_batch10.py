"""Apply V19-010 full-text reconstruction for three Trichomonas assay records."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.apply_v19_batch02 import DATE, ROOT, read_csv, update_rows, write_csv

PMID = "38958374"
DOI = "10.4274/tpd.galenos.2024.91855"
TITLE = "Investigation of the Antitrichomonal Activity of Cinnamaldehyde, Carvacrol and Thymol and Synergy with Metronidazole."
AUTHORS = "Özel Y, Çavuş İ, Ünlü G, Ünlü M, Özbilgin A."
URL = "https://www.turkiyeparazitolderg.org/articles/investigation-of-the-antitrichomonal-activity-of-cinnamaldehyde-carvacrol-and-thymol-and-synergy-with-metronidazole/doi/tpd.galenos.2024.91855"
CACHE = "history/rebuild_artifacts/bf25a8a45c2a8835e33aae42011ebeaa498124998e16f9a7cc6709d57a1e463b_pmid_38958374.json"
RECORDS = {
    "SB-0135": {
        "compound": "Cinnamaldehyde", "mic": "BAUN-TV1 3.9/31.25; BAUN-TV2 1.8/7.81; ATCC 50143 (metronidazole-resistant) 3.9/15.62 µg/mL",
        "fici": "ΣFICI=0.374 (Table 2; labeled synergy)",
        "effect": "In-vitro antitrichomonal activity; Table 2 reports synergy with metronidazole against metronidazole-resistant T. vaginalis ATCC 50143.",
        "direction": "MIC₅₀/MLC values reported across three isolates; synergy with metronidazole in ATCC 50143 checkerboard assay",
        "outcome": "Primary full-text results: Table 1 reports cinnamaldehyde MIC₅₀/MLC values of 3.9/31.25 µg/mL for clinical isolate BAUN-TV1, 1.8/7.81 µg/mL for BAUN-TV2, and 3.9/15.62 µg/mL for metronidazole-resistant reference strain ATCC 50143. Table 2 reports ΣFICI=0.374 for cinnamaldehyde plus metronidazole against ATCC 50143, labeled “Synergy.” MIC₅₀/MLC measurements used broth microdilution; the combination result used checkerboard assay.",
        "locator": "Primary full text, Methods—In vitro Drug Screening Test and Checkerboard Combination Test; Results; Table 1, BAUN-TV1/BAUN-TV2/ATCC 50143 rows; Table 2, cinnamaldehyde/metronidazole row.",
        "limitations": "In-vitro T. vaginalis assay only: two clinical isolates and one metronidazole-resistant reference strain. Combination FICI was tested against ATCC 50143, not patients; assay was repeated on three independent days. No human treatment, food exposure or clinical dose relationship was studied. Article reports no statistical analysis; FICI classification is assay-specific.",
    },
    "SB-0136": {
        "compound": "Carvacrol", "mic": "BAUN-TV1 15.62/125; BAUN-TV2 31.25/250; ATCC 50143 (metronidazole-resistant) 62.5/250 µg/mL",
        "fici": "ΣFICI=0.187 (Table 2; labeled synergy)",
        "effect": "In-vitro antitrichomonal activity; Table 2 reports synergy with metronidazole against metronidazole-resistant T. vaginalis ATCC 50143.",
        "direction": "MIC₅₀/MLC values reported across three isolates; synergy with metronidazole in ATCC 50143 checkerboard assay",
        "outcome": "Primary full-text results: Table 1 reports carvacrol MIC₅₀/MLC values of 15.62/125 µg/mL for clinical isolate BAUN-TV1, 31.25/250 µg/mL for BAUN-TV2, and 62.5/250 µg/mL for metronidazole-resistant reference strain ATCC 50143. Table 2 reports ΣFICI=0.187 for carvacrol plus metronidazole against ATCC 50143, labeled “Synergy.” MIC₅₀/MLC measurements used broth microdilution; the combination result used checkerboard assay.",
        "locator": "Primary full text, Methods—In vitro Drug Screening Test and Checkerboard Combination Test; Results; Table 1, BAUN-TV1/BAUN-TV2/ATCC 50143 rows; Table 2, carvacrol/metronidazole row.",
        "limitations": "In-vitro T. vaginalis assay only: two clinical isolates and one metronidazole-resistant reference strain. Combination FICI was tested against ATCC 50143, not patients; assay was repeated on three independent days. No human treatment, food exposure or clinical dose relationship was studied. Article reports no statistical analysis; FICI classification is assay-specific.",
    },
    "SB-0137": {
        "compound": "Thymol", "mic": "BAUN-TV1 62.5/500; BAUN-TV2 15.62/125; ATCC 50143 (metronidazole-resistant) 125/500 µg/mL",
        "fici": "ΣFICI=0.750 (Table 2; source labels “Partial synergy”; method categories overlap at 0.75)",
        "effect": "In-vitro antitrichomonal activity; Table 2 labels the thymol/metronidazole ATCC 50143 combination as partial synergy, with an unresolved exact-boundary overlap in the Methods criteria.",
        "direction": "MIC₅₀/MLC values reported across three isolates; source-labeled partial synergy with metronidazole in ATCC 50143 checkerboard assay",
        "outcome": "Primary full-text results: Table 1 reports thymol MIC₅₀/MLC values of 62.5/500 µg/mL for clinical isolate BAUN-TV1, 15.62/125 µg/mL for BAUN-TV2, and 125/500 µg/mL for metronidazole-resistant reference strain ATCC 50143. Table 2 reports ΣFICI=0.750 for thymol plus metronidazole against ATCC 50143, labeled “Partial synergy.” Methods define partial synergy as between 0.5–0.75 and additive as 0.75–1, so exact 0.75 is in both stated intervals; the table label is preserved without independently resolving this threshold overlap.",
        "locator": "Primary full text, Methods—Checkerboard Combination Test (FICI interpretation); Results; Table 1, BAUN-TV1/BAUN-TV2/ATCC 50143 rows; Table 2, thymol/metronidazole row.",
        "limitations": "In-vitro T. vaginalis assay only: two clinical isolates and one metronidazole-resistant reference strain. Combination FICI was tested against ATCC 50143, not patients; assay was repeated on three independent days. No human treatment, food exposure or clinical dose relationship was studied. The exact FICI=0.750 category remains ambiguous because Methods intervals overlap; Table 2's partial-synergy label is reported as printed.",
    },
}


def apply() -> dict:
    parent = ROOT.parent / "StageB_V18_20261103"
    with (ROOT / "data/interaction_evidence.csv").open(encoding="utf-8-sig", newline="") as handle:
        evidence = list(csv.DictReader(handle))
    with (parent / "data/interaction_evidence.csv").open(encoding="utf-8-sig", newline="") as handle:
        baseline = list(csv.DictReader(handle))
    current = {r["Evidence_ID"]: r for r in evidence}
    original = {r["Evidence_ID"]: r for r in baseline}
    if not set(RECORDS) <= set(current) or not set(RECORDS) <= set(original):
        raise ValueError("one or more Batch 010 evidence IDs are absent")
    if any(current[eid].get("Quantitative_Outcome", "").strip() for eid in RECORDS):
        raise ValueError("Batch 010 targets must remain blank before application; refusing overwrite")
    if any(original[eid].get("Quantitative_Outcome", "").strip() for eid in RECORDS):
        raise ValueError("Batch 010 targets must be inherited V18 blanks")

    evidence_updates, audit_updates, claim_updates, review_rows = {}, {}, {}, []
    review_fields = ["Batch", "Evidence_ID", "Compound_ID", "Compound", "Drug_Probe", "Study_ID", "PMID", "DOI", "Primary_Source_URL", "Source_Access_Status", "Local_Metadata_Cache", "Source_Locator", "Verification_Tier", "Review_Date", "Correction_Made", "Verified_Outcome", "Remaining_Limitation"]
    for eid, spec in RECORDS.items():
        row = current[eid]
        if row.get("Compound") != spec["compound"] or row.get("Drug") != "Metronidazole":
            raise ValueError(f"unexpected inherited attribution for {eid}")
        evidence_updates[eid] = {
            "Interaction_Effect": spec["effect"], "Mechanism": "Broth-microdilution MIC₅₀/MLC and checkerboard interaction assays; the study does not establish a molecular mechanism.",
            "Evidence_Type": "In vitro", "Evidence_Level": "compound", "Direction": spec["direction"],
            "Quantitative_Outcome": spec["outcome"],
            "Dose": "Commercial pure forms from Sigma; broth-microdilution phytochemical range 1600–0.9 µg/mL (metronidazole range 12500–3 µM); 5×10³ T. vaginalis trophozoites/mL; 37 °C for 48 h. Checkerboard combinations were tested against metronidazole-resistant ATCC 50143 only; all studies repeated on three independent days.",
            "Population": "Two clinical T. vaginalis isolates (BAUN-TV1 and BAUN-TV2) and metronidazole-resistant reference strain ATCC 50143; no human participants were studied.",
            "Study_Design": "Experimental in-vitro broth-microdilution MIC₅₀/MLC assay plus checkerboard interaction assay against metronidazole-resistant T. vaginalis ATCC 50143; three independent-day repeats.",
            "Source_Title": TITLE, "Authors": AUTHORS, "Year": "2024", "DOI": DOI, "PMID": PMID,
            "Source_Type": "Primary research", "Limitations": spec["limitations"],
            "Confidence": "Primary full-text article, Methods, Results and Tables 1–2 reviewed; assay is in-vitro and the source's thymol boundary classification remains open for manual review.",
            "Notes": "V19-010: Table 1 and Table 2 values transcribed as printed; no conversion to human dose or clinical inference made.",
            "Study_ID": "PMID:" + PMID, "Source_URL": URL, "Source_Cache": CACHE, "Source_Locator": spec["locator"],
            "Preparation": "Commercial pure compound obtained from Sigma, as reported in Methods; the tested lot was not independently assayed.",
            "Identity_Status": "named pure compound identified in primary full text; tested lot equivalence not independently verified",
            "Outcome": "in_vitro_antitrichomonal_synergy" if eid != "SB-0137" else "in_vitro_antitrichomonal_partial_synergy_source_labeled_threshold_open",
            "Clinical_Extrapolation": "No clinical extrapolation",
        }
        audit_updates[eid] = {
            "PMID": PMID, "DOI": DOI, "Source_Title": TITLE, "Source_URL": URL, "Source_Cache": CACHE,
            "Source_Locator": spec["locator"],
            "Verification_Status": "Tier 1: original open-access publisher full text, Methods, Results and Tables 1–2 directly reviewed",
            "Fields_Audited": "compound/drug attribution; pure-compound preparation; protozoal isolates; MIC₅₀ and MLC values/units; checkerboard FICI; assay methods, repeat description and threshold interpretation; limits on clinical inference",
            "Limitations": spec["limitations"], "Source_Type": "Primary research", "Verification_Date": DATE,
            "Verification_Method": "Original Turkish Journal of Parasitology publisher article HTML and issue PDF directly reviewed: Methods—In vitro Drug Screening and Checkerboard Combination; Results; Tables 1 and 2. PubMed MED metadata independently verifies PMID/DOI/title. Table 1 values were transcribed by isolate and Table 2 FICI values cross-checked against Results prose.",
            "Verification_Level": "1", "Audit_Disposition": "V19_TIER_1_FULL_TEXT_REVIEWED; TABLE_1_AND_2_NUMERICAL_OUTCOMES_RECOVERED; SOURCE_THRESHOLD_LIMITATION_RETAINED",
            "Reviewer": "Codex AI-assisted primary-source curation; independent expert re-review not performed.",
            "Endpoint_Verified": "Table 1 MIC₅₀ and MLC values for three T. vaginalis isolates; Table 2 ΣFICI and source interaction label for each compound/metronidazole combination against resistant ATCC 50143.",
            "Numerical_Outcome_Verified": spec["mic"] + "; " + spec["fici"] + "; Table 1 header identifies phytochemical units as µg/mL; Table 2 reports unitless ΣFICI. Methods: 48 h, 5×10³ trophozoites/mL, three independent-day repeats.",
            "Study_ID": "PMID:" + PMID, "Compound_ID": row["Compound_ID"], "Drug_Probe": "Metronidazole",
            "V18_Unresolved_Discrepancy": "V19-010 verified numerical outcomes from the publisher full text. The FICI threshold intervals overlap at exactly 0.75; for thymol, the Table 2 source label is preserved and the overlap remains flagged in V19-W16.",
        }
        claim_updates[eid] = {
            "Compound_ID": row["Compound_ID"], "PMID": PMID, "Source_Locator": spec["locator"],
            "Verification_Status": "Primary publisher full-text review completed in V19-010; Table 1 MIC₅₀/MLC and Table 2 FICI values/labels recorded.",
            "Numerical_Use": spec["mic"] + "; " + spec["fici"],
            "Attribution": spec["compound"] + " / Metronidazole / T. vaginalis isolate or ATCC 50143 assay", "Limitations": spec["limitations"],
        }
        review_rows.append({
            "Batch": "V19-010", "Evidence_ID": eid, "Compound_ID": row["Compound_ID"], "Compound": row["Compound"],
            "Drug_Probe": "Metronidazole", "Study_ID": "PMID:" + PMID, "PMID": PMID, "DOI": DOI,
            "Primary_Source_URL": URL,
            "Source_Access_Status": "Original publisher full-text article and issue PDF accessed; Methods, Results, Table 1 and Table 2 reviewed. Full-text source is openly available under CC BY-NC-ND 4.0. PubMed MED metadata cross-checked for bibliographic identifiers.",
            "Local_Metadata_Cache": CACHE, "Source_Locator": spec["locator"], "Verification_Tier": 1,
            "Review_Date": DATE,
            "Correction_Made": "Replaced the inherited blank and abstract-only disposition with isolate-specific Table 1 MIC₅₀/MLC values and Table 2 FICI values, units, model, assay conditions and explicit in-vitro limitations. Repaired the legacy local MED cache pointer under V19-W10. Added an open warning for the exact thymol FICI threshold boundary overlap.",
            "Verified_Outcome": spec["outcome"], "Remaining_Limitation": spec["limitations"],
        })

    update_rows("data/interaction_evidence.csv", "Evidence_ID", evidence_updates)
    update_rows("provenance/source_audit.csv", "Evidence_ID", audit_updates)
    update_rows("provenance/claim_support_and_verification.csv", "Evidence_ID", claim_updates)
    update_rows("data/publication_bibliography.csv", "PMID", {PMID: {"Source": CACHE}})
    with (ROOT / "validation/V19_batch_010_review.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=review_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(review_rows)
    update_rows("data/study_registry.csv", "Study_ID", {
        "PMID:" + PMID: {"Verification_Status": "V19-010: original publisher full text, Methods, Results, Table 1 and Table 2 reviewed for SB-0135–SB-0137. Recovered three-isolate MIC₅₀/MLC and ATCC 50143 checkerboard FICI outcomes; thymol FICI threshold overlap is retained as open V19-W16."},
    })

    fields, warnings, bom = read_csv("data/warning_ledger.csv")
    if any(r["Warning_ID"] == "V19-W16" for r in warnings):
        raise ValueError("V19-W16 already exists; refusing duplicate warning creation")
    warning = {
        "Warning_ID": "V19-W16", "Code": "FICI_CLASSIFICATION_BOUNDARY_OVERLAP",
        "Description": "For SB-0137 (PMID 38958374), Methods define partial synergy as FICI between 0.5–0.75 and additive as 0.75–1, so the reported thymol/metronidazole ΣFICI=0.750 lies in both stated intervals. Table 2 labels it “Partial synergy.” Preserve the numeric value and table label; the exact boundary rule is unresolved.",
        "Affected": "SB-0137 | PMID:38958374 | Table 2 and Checkerboard Combination Test criteria",
        "Classification": "primary-source threshold ambiguity / categorical outcome",
        "Before": "Inherited blank quantitative outcome and Tier 3 abstract-only disposition; threshold text had not been rechecked in V19.",
        "Action": "Reviewed Methods threshold criteria, Results and Table 2. Recorded ΣFICI=0.750 and the table's “Partial synergy” label; did not reclassify the boundary value or silently select one interval.",
        "After": "Numerical FICI and source label verified. Exact classification at 0.750 remains unresolved because both stated intervals include that boundary.",
        "Remaining_Limitations": "The publication does not clarify whether the 0.75 boundary belongs to partial synergy or additive interaction. Author/source clarification or expert adjudication is required for a unique threshold rule.",
        "Resolution_Source": "V19_batch_010_review.csv; publisher full text, Methods—Checkerboard Combination Test and Table 2 for PMID 38958374.",
        "Review_Date": DATE, "Audit_Status": "NEEDS_MANUAL_REVIEW", "Inherited_Severity": "NOT_RECORDED",
        "Audit_Rationale": "The source's two adjacent FICI intervals overlap exactly at 0.75. Table 2's category is retained as source-reported; resolving the threshold would require author clarification or expert adjudication.",
        "Audit_Verification_Reference": "V19_batch_010_review.csv; PMID 38958374 publisher full text, Methods lines 949–952 and Table 2.",
        "Audit_Dependencies": "Author/source clarification or expert decision on inclusive/exclusive boundary definitions.",
        "V17_Ledger_Audit_Status": "NOT_IN_V18",
    }
    warnings.append(warning)
    write_csv("data/warning_ledger.csv", fields, warnings, bom)
    af, warning_audit, abom = read_csv("validation/V19_warning_audit.csv")
    warning_audit.append({
        "Warning_ID": "V19-W16", "V18_Status": "NEW_IN_V19", "V19_Status": "NEEDS_MANUAL_REVIEW",
        "V19_Recheck_Status": "OPEN_IN_V19-010; FICI=0.750 lies in both source-defined adjacent intervals",
        "V19_Review_Work": warning["Action"], "V19_Evidence_or_Rationale": warning["Audit_Verification_Reference"],
        "Remaining_Limitations": warning["Remaining_Limitations"],
    })
    write_csv("validation/V19_warning_audit.csv", af, warning_audit, abom)

    fields, warnings, bom = read_csv("data/warning_ledger.csv")
    w10 = next(r for r in warnings if r["Warning_ID"] == "V19-W10")
    if w10.get("Audit_Status") != "RESOLVED":
        raise ValueError("V19-W10 must remain resolved before scope expansion")
    w10.update({
        "Description": w10["Description"] + " V19-010 also identified this same absent legacy metadata pointer for PMID 38958374; its archive path is repaired below.",
        "Affected": w10["Affected"] + " | SB-0135 | SB-0136 | SB-0137 | bibliography PMID 38958374",
        "Action": w10["Action"] + " V19-010 scope expansion: repaired all three evidence/source-audit cache paths and bibliography pointer for PMID 38958374 after checking the archived MED JSON PMID/DOI.",
        "After": w10["After"] + " V19-010 also repairs PMID 38958374; all nine audited MED metadata snapshots now resolve within V19.",
        "Resolution_Source": w10["Resolution_Source"] + "; V19_batch_010_review.csv; " + CACHE,
        "Review_Date": DATE,
        "Audit_Rationale": w10["Audit_Rationale"] + " V19-010 verified the archived MED JSON PMID/DOI and repaired three evidence/source-audit references plus the PMID 38958374 bibliography pointer.",
        "Audit_Verification_Reference": w10["Audit_Verification_Reference"] + "; V19_batch_010_review.csv; archived MED JSON for PMID 38958374.",
    })
    write_csv("data/warning_ledger.csv", fields, warnings, bom)
    update_rows("validation/V19_warning_audit.csv", "Warning_ID", {
        "V19-W10": {
            "V19_Recheck_Status": "RESOLVED_IN_V19-004; SAME_ROOT_CAUSE_EXPANDED_AND_REPAIRED_IN_V19-005; SAME_ROOT_CAUSE_EXPANDED_AND_REPAIRED_IN_V19-006; SAME_ROOT_CAUSE_EXPANDED_AND_REPAIRED_IN_V19-007; SAME_ROOT_CAUSE_EXPANDED_AND_REPAIRED_IN_V19-008; SAME_ROOT_CAUSE_EXPANDED_AND_REPAIRED_IN_V19-009; SAME_ROOT_CAUSE_EXPANDED_AND_REPAIRED_IN_V19-010",
            "V19_Review_Work": w10["Action"], "V19_Evidence_or_Rationale": w10["Audit_Verification_Reference"],
            "Remaining_Limitations": "All nine local JSON snapshots verify publication metadata only; scientific content was separately reviewed at the stated per-record source tier.",
        },
    })

    metadata_path = ROOT / "release_metadata.json"
    meta = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    review = meta["v19_primary_source_review"]
    batches = list(review.get("batches_completed", []))
    if "V19-010" not in batches:
        batches.append("V19-010")
    review.update({
        "batches_completed": batches, "evidence_records_reviewed": 49,
        "tier_1_primary_full_text_records": 37, "tier_3_primary_abstract_records": 12,
        "records_corrected_or_reconstructed": 47, "source_review_remaining": 268,
        "warning_rows_preserved": 86,
        "warning_status_counts": {s: sum(r.get("Audit_Status") == s for r in warnings) for s in ["RESOLVED", "PARTIALLY_RESOLVED", "STILL_VALID", "NEEDS_MANUAL_REVIEW", "NOT_APPLICABLE"]},
        "new_warning_count": 16, "warning_ids_added": [f"V19-W{i:02d}" for i in range(1, 17)],
        "warning_rows_individually_reviewed_in_v19": 18,
    })
    meta["warning_count"] = len(warnings)
    meta["v19_quantitative_outcome_audit"].update({
        "quantitative_values_recovered": 29, "qualitative_outcomes_dispositioned": 17,
        "blank_fields_remaining": 44, "source_review_batch": "V19-010",
    })
    meta["v19_validation"].update({
        "batch09_integrity": "PASS", "batch09_tests_passed": 10, "batch09_tests_failed": 0,
        "batch10_integrity": "PENDING_VALIDATION", "batch10_tests_passed": 0, "batch10_tests_failed": 0,
        "full_stageB_regression": "PENDING_FINAL_VALIDATION",
        "v19_exact_manifest": "PENDING_FINAL_PACKAGING", "v19_clean_copy_manifest": "PENDING_FINAL_PACKAGING",
    })
    meta["readiness"] = meta["release_status"] = "SCIENTIFIC_REMEDIATION_IN_PROGRESS"
    metadata_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "batch": "V19-010", "records_reviewed": 3, "verification_tier": 1,
        "quantitative_outcomes_recovered": 3, "blank_outcomes_remaining": 44,
        "warnings_added": ["V19-W16 (open thymol FICI boundary ambiguity)"],
        "V19-W10": "RESOLVED; scope expanded to nine verified MED metadata snapshots",
        "status": "APPLIED_PENDING_VALIDATION",
    }


if __name__ == "__main__":
    print(json.dumps(apply(), indent=2, ensure_ascii=False))
