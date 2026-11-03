"""Apply V19-009 Tier 3 dispositions for three midazolam/flavonoid records."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.apply_v19_batch02 import DATE, ROOT, read_csv, update_rows, write_csv

PMID = "18191104"
DOI = "10.1016/j.bcp.2007.11.012"
TITLE = "Flavonoids diosmetin and luteolin inhibit midazolam metabolism by human liver microsomes and recombinant CYP 3A4 and CYP3A5 enzymes."
AUTHORS = "Quintieri L, Palatini P, Nassi A, Ruzza P, Floreani M."
URL = "https://pubmed.ncbi.nlm.nih.gov/18191104/"
CACHE = "history/rebuild_artifacts/4bcf7ef9bb102769124c952b66b3e4c8bf0f2d43c65c8e92cddd1a34268a6be8_pmid_18191104.json"
RECORDS = {
    "SB-0149": {
        "compound": "Diosmetin",
        "outcome": "Tier 3 primary-abstract disposition: Diosmetin inhibited formation of both 1′- and 4-hydroxymidazolam in human liver microsomes in a concentration-dependent manner. The abstract gives apparent Ki values in a jointly reported 30–50 μmol range for diosmetin and luteolin, but does not assign an individual value or state a denominator in the accessible display; this range is retained as source wording and is not assigned to diosmetin alone. Recombinant CYP3A4, but not CYP3A5, showed decreased 1′-hydroxymidazolam formation; both recombinant enzymes showed decreased 4-hydroxymidazolam formation.",
        "effect": "Diosmetin concentration-dependently inhibited formation of both measured hydroxymidazolam metabolites in human liver microsomes; recombinant CYP3A effects differed by metabolite and isoform.",
        "direction": "concentration-dependent inhibition of both hydroxymidazolam products in human liver microsomes",
        "mechanism": "In-vitro CYP3A-mediated metabolite formation. The abstract reports reduced 1′-hydroxymidazolam formation by CYP3A4 but not CYP3A5, and reduced 4-hydroxymidazolam formation by both; this is an assay-specific enzyme result, not a demonstrated clinical mechanism.",
        "locator": "PubMed/ScienceDirect primary abstract: study model and CYP3A metabolites (opening sentences); diosmetin and luteolin inhibition, joint apparent Ki range and recombinant CYP3A4/CYP3A5 findings (results sentences).",
        "endpoint": "Abstract reports concentration-dependent inhibition of human-liver-microsomal formation of 1′-OH-midazolam and 4-OH-midazolam; recombinant CYP3A4/CYP3A5 effects are reported by metabolite. Exact assay conditions and per-compound kinetic estimates require full text.",
        "limitations": "Tier 3 abstract-only review. The apparent Ki range is jointly reported for diosmetin and luteolin, not assigned individually; the accessible abstract display gives μmol without an explicit denominator. Full-text assay conditions, individual Ki estimates, sample details and tested lot/purity remain unverified. No human administration or ordinary-food exposure was studied; no clinical interaction magnitude can be inferred.",
    },
    "SB-0150": {
        "compound": "Luteolin",
        "outcome": "Tier 3 primary-abstract disposition: Luteolin inhibited formation of both 1′- and 4-hydroxymidazolam in human liver microsomes in a concentration-dependent manner. The abstract gives apparent Ki values in a jointly reported 30–50 μmol range for diosmetin and luteolin, but does not assign an individual value or state a denominator in the accessible display; this range is retained as source wording and is not assigned to luteolin alone. Recombinant CYP3A4, but not CYP3A5, showed decreased 1′-hydroxymidazolam formation; both recombinant enzymes showed decreased 4-hydroxymidazolam formation.",
        "effect": "Luteolin concentration-dependently inhibited formation of both measured hydroxymidazolam metabolites in human liver microsomes; recombinant CYP3A effects differed by metabolite and isoform.",
        "direction": "concentration-dependent inhibition of both hydroxymidazolam products in human liver microsomes",
        "mechanism": "In-vitro CYP3A-mediated metabolite formation. The abstract reports reduced 1′-hydroxymidazolam formation by CYP3A4 but not CYP3A5, and reduced 4-hydroxymidazolam formation by both; this is an assay-specific enzyme result, not a demonstrated clinical mechanism.",
        "locator": "PubMed/ScienceDirect primary abstract: study model and CYP3A metabolites (opening sentences); diosmetin and luteolin inhibition, joint apparent Ki range and recombinant CYP3A4/CYP3A5 findings (results sentences).",
        "endpoint": "Abstract reports concentration-dependent inhibition of human-liver-microsomal formation of 1′-OH-midazolam and 4-OH-midazolam; recombinant CYP3A4/CYP3A5 effects are reported by metabolite. Exact assay conditions and per-compound kinetic estimates require full text.",
        "limitations": "Tier 3 abstract-only review. The apparent Ki range is jointly reported for diosmetin and luteolin, not assigned individually; the accessible abstract display gives μmol without an explicit denominator. Full-text assay conditions, individual Ki estimates, sample details and tested lot/purity remain unverified. No human administration or ordinary-food exposure was studied; no clinical interaction magnitude can be inferred.",
    },
    "SB-0173": {
        "compound": "Tangeretin",
        "outcome": "Tier 3 primary-abstract disposition: Tangeretin stimulated midazolam metabolism in human liver microsomes under the in-vitro conditions studied. The accessible abstract gives no tangeretin concentration, metabolite-specific magnitude or numerical stimulation estimate; none was inferred. This source-reported microsomal stimulation is not a human clinical effect.",
        "effect": "Tangeretin stimulated midazolam metabolism in the human liver-microsome assay, as reported in the abstract.",
        "direction": "stimulation of midazolam metabolism in human liver microsomes",
        "mechanism": "In-vitro midazolam metabolite-formation response. No specific CYP3A isoform attribution for tangeretin is stated in the accessible abstract.",
        "locator": "PubMed/ScienceDirect primary abstract: comparison flavones paragraph; tangeretin is named among flavones that stimulated midazolam metabolism; full-text dose and metabolite-specific values unavailable.",
        "endpoint": "The abstract reports stimulation of midazolam metabolism by tangeretin in human liver microsomes; it does not report tangeretin-specific concentrations or numeric metabolite-formation effects.",
        "limitations": "Tier 3 abstract-only review. No tangeretin-specific concentration, endpoint magnitude, kinetic parameter, donor/sample detail or full assay method was accessible. No human administration or ordinary-food exposure was studied; the microsomal stimulation is not evidence of a clinical interaction or effect size.",
    },
}


def apply() -> dict:
    parent = ROOT.parent / "StageB_V18_20261103"
    with (ROOT / "data/interaction_evidence.csv").open(encoding="utf-8-sig", newline="") as handle:
        evidence = list(csv.DictReader(handle))
    with (parent / "data/interaction_evidence.csv").open(encoding="utf-8-sig", newline="") as handle:
        baseline = list(csv.DictReader(handle))
    by_current = {r["Evidence_ID"]: r for r in evidence}
    by_base = {r["Evidence_ID"]: r for r in baseline}
    if not set(RECORDS) <= set(by_current) or not set(RECORDS) <= set(by_base):
        raise ValueError("one or more Batch 009 evidence IDs are absent")
    if any(by_current[eid].get("Quantitative_Outcome", "").strip() for eid in RECORDS):
        raise ValueError("Batch 009 targets must still be blank; refusing to overwrite prior evidence")
    if any(by_base[eid].get("Quantitative_Outcome", "").strip() for eid in RECORDS):
        raise ValueError("Batch 009 targets must be inherited V18 blanks")

    evidence_updates, audit_updates, claim_updates, review_rows = {}, {}, {}, []
    review_fields = ["Batch", "Evidence_ID", "Compound_ID", "Compound", "Drug_Probe", "Study_ID", "PMID", "DOI", "Primary_Source_URL", "Source_Access_Status", "Local_Metadata_Cache", "Source_Locator", "Verification_Tier", "Review_Date", "Correction_Made", "Verified_Outcome", "Remaining_Limitation"]
    for eid, spec in RECORDS.items():
        row = by_current[eid]
        if row.get("Compound") != spec["compound"] or row.get("Drug") != "Midazolam":
            raise ValueError(f"unexpected inherited attribution for {eid}")
        evidence_updates[eid] = {
            "Interaction_Effect": spec["effect"], "Mechanism": spec["mechanism"],
            "Evidence_Type": "In vitro", "Evidence_Level": "compound", "Direction": spec["direction"],
            "Quantitative_Outcome": spec["outcome"],
            "Dose": "Concentrations and assay conditions are not available in the accessible abstract; no values inferred.",
            "Population": "Human liver microsomes; recombinant human CYP3A4/CYP3A5 additionally reported for diosmetin and luteolin; no intact-human treatment study.",
            "Study_Design": "Experimental in-vitro study of midazolam metabolism in human liver microsomes with recombinant CYP3A4/CYP3A5 assays for diosmetin and luteolin; Tier 3 abstract review only.",
            "Source_Title": TITLE, "Authors": AUTHORS, "Year": "2008", "DOI": DOI, "PMID": PMID,
            "Source_Type": "Primary research", "Limitations": spec["limitations"],
            "Confidence": "Primary PubMed and publisher abstracts reviewed; Tier 3 only; full-text assay verification and independent expert re-review remain pending.",
            "Notes": "V19-009: abstract-level endpoints transcribed; no full-text numerical reconstruction, food-dose conversion or clinical interpretation made.",
            "Study_ID": "PMID:" + PMID, "Source_URL": URL, "Source_Cache": CACHE, "Source_Locator": spec["locator"],
            "Preparation": "Named compound as identified in the abstract; tested reagent form and purity not verified because full text is restricted.",
            "Identity_Status": "compound name verified in the primary abstract; tested reagent form/purity unverified",
            "Outcome": "abstract-reported microsomal inhibition" if eid in {"SB-0149", "SB-0150"} else "abstract-reported microsomal stimulation",
            "Clinical_Extrapolation": "No clinical extrapolation",
        }
        audit_updates[eid] = {
            "PMID": PMID, "DOI": DOI, "Source_Title": TITLE, "Source_URL": URL, "Source_Cache": CACHE,
            "Source_Locator": spec["locator"],
            "Verification_Status": "Tier 3: official PubMed and ScienceDirect primary abstracts directly reviewed; full-text methods/results unavailable",
            "Fields_Audited": "named compound and drug attribution; human liver microsome model; metabolite endpoints; abstract-reported inhibition/stimulation; recombinant CYP isoform findings where stated; source access and numeric limitations",
            "Limitations": spec["limitations"], "Source_Type": "Primary research", "Verification_Date": DATE,
            "Verification_Method": "Official PubMed and ScienceDirect primary abstracts reviewed and cross-checked; University of Padua repository record identifies the version-of-record PDF as restricted and offers a request-copy route. The full text was not retrieved or claimed as reviewed. PubMed MED metadata verified PMID/DOI/title.",
            "Verification_Level": "3", "Audit_Disposition": "V19_TIER_3_PRIMARY_ABSTRACT_REVIEWED; QUALITATIVE_OUTCOME_DISPOSITIONED; FULL_TEXT_REVIEW_PENDING",
            "Reviewer": "Codex AI-assisted primary-source curation; independent expert re-review not performed.",
            "Endpoint_Verified": spec["endpoint"],
            "Numerical_Outcome_Verified": "No compound-specific Ki or numeric stimulation value assigned. The abstract jointly reports apparent Ki values in a 30–50 μmol range for diosmetin and luteolin without an explicit denominator in the accessible display; exact individual values remain unavailable. No numerical tangeretin stimulation was inferred.",
            "Study_ID": "PMID:" + PMID, "Compound_ID": row["Compound_ID"], "Drug_Probe": "Midazolam",
            "V18_Unresolved_Discrepancy": "V19-009 directly checked the primary abstracts. Full-text assay conditions remain unreviewed; joint Ki range cannot be individually attributed or normalized from the available abstract.",
        }
        claim_updates[eid] = {
            "Compound_ID": row["Compound_ID"], "PMID": PMID, "Source_Locator": spec["locator"],
            "Verification_Status": "Tier 3 primary-abstract review completed; full text and compound-specific numeric verification remain pending.",
            "Numerical_Use": "No per-compound quantitative value assigned; joint abstract Ki range is documented only as an unresolved group-level source statement." if eid in {"SB-0149", "SB-0150"} else "No numeric stimulation estimate used; abstract-level qualitative direction only.",
            "Attribution": spec["compound"] + " / Midazolam", "Limitations": spec["limitations"],
        }
        review_rows.append({
            "Batch": "V19-009", "Evidence_ID": eid, "Compound_ID": row["Compound_ID"], "Compound": row["Compound"],
            "Drug_Probe": "Midazolam", "Study_ID": "PMID:" + PMID, "PMID": PMID, "DOI": DOI,
            "Primary_Source_URL": URL,
            "Source_Access_Status": "Official PubMed and ScienceDirect primary abstracts reviewed. University of Padua repository marks the published PDF as restricted and provides a request-copy option; no full text was retrieved. Tier 3 only.",
            "Local_Metadata_Cache": CACHE, "Source_Locator": spec["locator"], "Verification_Tier": 3,
            "Review_Date": DATE,
            "Correction_Made": "Replaced inherited blank/pending outcomes with primary-abstract-supported direction and assay context. Preserved the jointly stated Ki range without assigning it to an individual compound or inferring a denominator. Repaired the local MED metadata path under V19-W10.",
            "Verified_Outcome": spec["outcome"], "Remaining_Limitation": spec["limitations"],
        })

    update_rows("data/interaction_evidence.csv", "Evidence_ID", evidence_updates)
    update_rows("provenance/source_audit.csv", "Evidence_ID", audit_updates)
    update_rows("provenance/claim_support_and_verification.csv", "Evidence_ID", claim_updates)
    update_rows("data/publication_bibliography.csv", "PMID", {PMID: {"Source": CACHE}})
    with (ROOT / "validation/V19_batch_009_review.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=review_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(review_rows)
    update_rows("data/study_registry.csv", "Study_ID", {
        "PMID:" + PMID: {"Verification_Status": "V19-009: official PubMed/ScienceDirect primary abstracts reviewed for SB-0149, SB-0150 and SB-0173; inhibition, joint Ki-range limitation and tangeretin stimulation dispositioned at Tier 3. Version-of-record PDF remains restricted; numeric and method details pending."},
    })

    fields, warnings, bom = read_csv("data/warning_ledger.csv")
    if any(r["Warning_ID"] == "V19-W15" for r in warnings):
        raise ValueError("V19-W15 already exists; refusing duplicate warning creation")
    warning = {
        "Warning_ID": "V19-W15", "Code": "ABSTRACT_KI_RANGE_UNIT_AND_COMPOUND_ATTRIBUTION_UNRESOLVED",
        "Description": "The PMID 18191104 abstract gives apparent Ki values in a shared 30–50 μmol range for diosmetin and luteolin but does not assign an individual value to either compound; the accessible abstract display does not state an explicit denominator. Do not record this range as a compound-specific Ki or normalize its unit without full-text verification.",
        "Affected": "SB-0149 | SB-0150 | PMID:18191104 | abstract Ki range",
        "Classification": "scientific source ambiguity / quantitative outcome attribution",
        "Before": "The inherited evidence rows had blank quantitative outcomes and a pending source review.",
        "Action": "Reviewed PubMed and ScienceDirect primary abstracts; documented the joint range in the review record and retained it in each outcome only with explicit non-attribution. No per-compound value or normalized unit was assigned.",
        "After": "Tier 3 abstract-level findings recorded; individual Ki values and unit denominator remain unresolved pending legitimate full-text review.",
        "Remaining_Limitations": "The published version-of-record PDF is marked restricted in the University of Padua repository. Individual kinetic values, exact unit notation/denominator and assay conditions require full-text/source adjudication.",
        "Resolution_Source": "V19_batch_009_review.csv; PubMed and ScienceDirect primary abstracts for PMID 18191104; University of Padua repository handle 11577/2450042.",
        "Review_Date": DATE, "Audit_Status": "NEEDS_MANUAL_REVIEW", "Inherited_Severity": "NOT_RECORDED",
        "Audit_Rationale": "The primary abstract supports a group-level range but not compound-specific Ki estimates; the available text does not state an explicit concentration denominator. Preserving the source wording avoids an unsupported attribution or unit conversion.",
        "Audit_Verification_Reference": "V19_batch_009_review.csv; PMID 18191104 PubMed/ScienceDirect abstracts; https://www.research.unipd.it/handle/11577/2450042",
        "Audit_Dependencies": "Legitimate full-text retrieval and review, or author/source clarification, before assigning individual Ki values or normalizing units.",
        "V17_Ledger_Audit_Status": "NOT_IN_V18",
    }
    warnings.append(warning)
    write_csv("data/warning_ledger.csv", fields, warnings, bom)
    af, warning_audit, abom = read_csv("validation/V19_warning_audit.csv")
    warning_audit.append({
        "Warning_ID": "V19-W15", "V18_Status": "NEW_IN_V19", "V19_Status": "NEEDS_MANUAL_REVIEW",
        "V19_Recheck_Status": "OPEN_IN_V19-009; source abstract does not permit compound-specific Ki assignment or unit normalization",
        "V19_Review_Work": warning["Action"], "V19_Evidence_or_Rationale": warning["Audit_Verification_Reference"],
        "Remaining_Limitations": warning["Remaining_Limitations"],
    })
    write_csv("validation/V19_warning_audit.csv", af, warning_audit, abom)

    fields, warnings, bom = read_csv("data/warning_ledger.csv")
    w10 = next(r for r in warnings if r["Warning_ID"] == "V19-W10")
    if w10.get("Audit_Status") != "RESOLVED":
        raise ValueError("V19-W10 must remain resolved before scope expansion")
    w10.update({
        "Description": w10["Description"] + " V19-009 also found the same absent legacy path for PMID 18191104; its local pointer is repaired below.",
        "Affected": w10["Affected"] + " | SB-0149 | SB-0150 | SB-0173 | bibliography PMID 18191104",
        "Action": w10["Action"] + " V19-009 scope expansion: repaired all three evidence/source-audit cache paths and bibliography pointer for PMID 18191104 after validating the archived MED JSON PMID/DOI.",
        "After": w10["After"] + " V19-009 also repairs PMID 18191104; all eight audited MED metadata snapshots now resolve within V19.",
        "Resolution_Source": w10["Resolution_Source"] + "; V19_batch_009_review.csv; " + CACHE,
        "Review_Date": DATE,
        "Audit_Rationale": w10["Audit_Rationale"] + " V19-009 verified the archived PMID 18191104 MED JSON PMID/DOI and repaired three evidence/source-audit references plus its bibliography source pointer.",
        "Audit_Verification_Reference": w10["Audit_Verification_Reference"] + "; V19_batch_009_review.csv; archived MED JSON for PMID 18191104.",
    })
    write_csv("data/warning_ledger.csv", fields, warnings, bom)
    update_rows("validation/V19_warning_audit.csv", "Warning_ID", {
        "V19-W10": {
            "V19_Recheck_Status": "RESOLVED_IN_V19-004; SAME_ROOT_CAUSE_EXPANDED_AND_REPAIRED_IN_V19-005; SAME_ROOT_CAUSE_EXPANDED_AND_REPAIRED_IN_V19-006; SAME_ROOT_CAUSE_EXPANDED_AND_REPAIRED_IN_V19-007; SAME_ROOT_CAUSE_EXPANDED_AND_REPAIRED_IN_V19-008; SAME_ROOT_CAUSE_EXPANDED_AND_REPAIRED_IN_V19-009",
            "V19_Review_Work": w10["Action"], "V19_Evidence_or_Rationale": w10["Audit_Verification_Reference"],
            "Remaining_Limitations": "All eight local JSON snapshots verify publication metadata only; per-record source tiers and primary-text access limitations remain explicit.",
        },
    })

    metadata_path = ROOT / "release_metadata.json"
    meta = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    review = meta["v19_primary_source_review"]
    batches = list(review.get("batches_completed", []))
    if "V19-009" not in batches:
        batches.append("V19-009")
    review.update({
        "batches_completed": batches, "evidence_records_reviewed": 46,
        "tier_1_primary_full_text_records": 34, "tier_3_primary_abstract_records": 12,
        "records_corrected_or_reconstructed": 44, "source_review_remaining": 271,
        "warning_rows_preserved": 85,
        "warning_status_counts": {s: sum(r.get("Audit_Status") == s for r in warnings) for s in ["RESOLVED", "PARTIALLY_RESOLVED", "STILL_VALID", "NEEDS_MANUAL_REVIEW", "NOT_APPLICABLE"]},
        "new_warning_count": 15, "warning_ids_added": [f"V19-W{i:02d}" for i in range(1, 16)],
        "warning_rows_individually_reviewed_in_v19": 17,
    })
    meta["warning_count"] = len(warnings)
    meta["v19_quantitative_outcome_audit"].update({
        "quantitative_values_recovered": 26, "qualitative_outcomes_dispositioned": 17,
        "blank_fields_remaining": 47, "source_review_batch": "V19-009",
    })
    meta["v19_validation"].update({
        "batch08_integrity": "PASS", "batch08_tests_passed": 10, "batch08_tests_failed": 0,
        "batch09_integrity": "PENDING_VALIDATION", "batch09_tests_passed": 0, "batch09_tests_failed": 0,
        "full_stageB_regression": "PENDING_FINAL_VALIDATION",
        "v19_exact_manifest": "PENDING_FINAL_PACKAGING", "v19_clean_copy_manifest": "PENDING_FINAL_PACKAGING",
    })
    meta["readiness"] = meta["release_status"] = "SCIENTIFIC_REMEDIATION_IN_PROGRESS"
    metadata_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "batch": "V19-009", "records_reviewed": 3, "verification_tier": 3,
        "qualitative_outcomes_dispositioned": 3, "per_compound_Ki_values_assigned": 0,
        "blank_outcomes_remaining": 47, "warnings_added": ["V19-W15 (open source-attribution/unit limitation)"],
        "V19-W10": "RESOLVED; scope expanded to eight verified MED metadata snapshots",
        "status": "APPLIED_PENDING_VALIDATION",
    }


if __name__ == "__main__":
    print(json.dumps(apply(), indent=2, ensure_ascii=False))
