"""Apply V19-008 abstract-level dispositions for nine paclitaxel/microsome records."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.apply_v19_batch02 import DATE, ROOT, read_csv, update_rows, write_csv

PMID = "12920504"
DOI = "10.1007/s00210-003-0781-9"
TITLE = "Paclitaxel metabolism in rat and human liver microsomes is inhibited by phenolic antioxidants."
AUTHORS = "Václavíková R, Horský S, Šimek P, Gut I."
URL = "https://link.springer.com/article/10.1007/s00210-003-0781-9"
CACHE = "history/rebuild_artifacts/99a6f10462261b27f84002569a1224abbc0436e6783b7a59d8610ad40508f080_pmid_12920504.json"

RECORDS = {
    "SB-0113": ("Fisetin", "human and rat", "human potency rank 1", "Rat microsomes: inhibition reported, weaker than resveratrol. Human microsomes: highest inhibitory potency among the nine tested antioxidants. The abstract says human 6α-hydroxypaclitaxel formation (CYP2C8) was generally more inhibited than C3′-hydroxypaclitaxel (CYP3A4); inhibition was mostly mixed-type.", "Inhibition reported in rat and human liver microsomes; stronger relative activity in human microsomes. The abstract does not provide concentrations, IC50/Ki values, donor counts or compound-specific kinetic parameters."),
    "SB-0114": ("Quercetin", "human", "human potency rank 2", "Human microsomes: second in the source-reported inhibitory-potency order, after fisetin; no inhibition is reported in rat microsomes under the study conditions. The abstract says 6α-hydroxypaclitaxel formation was generally more inhibited than C3′-hydroxypaclitaxel and inhibition was mostly mixed-type.", "Human-microsome inhibition reported; no rat-microsome inhibition reported. The abstract provides no concentrations, IC50/Ki values, donor counts or compound-specific kinetic parameters."),
    "SB-0115": ("Resveratrol", "human and rat", "rat more inhibitory than fisetin; human potency rank 4", "Rat microsomes: more inhibitory than fisetin. Human microsomes: inhibitory, ranked after fisetin, quercetin and morin. The abstract says 6α-hydroxypaclitaxel formation was generally more inhibited than C3′-hydroxypaclitaxel and inhibition was mostly mixed-type.", "Inhibition reported in rat and human liver microsomes. Relative rank is source-reported; no exact concentrations, IC50/Ki values, donor counts or compound-specific kinetic parameters are available in the abstract."),
    "SB-0116": ("Myricetin", "neither species reported", "no inhibition reported", "The primary abstract lists myricetin among the tested phenolic antioxidants that were not inhibitory to paclitaxel metabolism in the reported microsomal results.", "No inhibition was reported in the abstract for the tested rat/human microsomal context; this is not proof of no interaction at other concentrations, models or in vivo. Exact assay conditions and concentrations are unavailable."),
    "SB-0117": ("Gallic acid", "neither species reported", "no inhibition reported", "The primary abstract lists gallic acid among the tested phenolic antioxidants that were not inhibitory to paclitaxel metabolism in the reported microsomal results.", "No inhibition was reported in the abstract for the tested rat/human microsomal context; this is not proof of no interaction at other concentrations, models or in vivo. Exact assay conditions and concentrations are unavailable."),
    "SB-0118": ("Naringenin", "neither species reported", "no inhibition reported", "The primary abstract lists naringenin among the tested phenolic antioxidants that were not inhibitory to paclitaxel metabolism in the reported microsomal results.", "No inhibition was reported in the abstract for the tested rat/human microsomal context; this is not proof of no interaction at other concentrations, models or in vivo. Exact assay conditions and concentrations are unavailable."),
    "SB-0119": ("(+)-Catechin", "neither species reported", "no inhibition reported", "The primary abstract lists (+)-catechin among the tested phenolic antioxidants that were not inhibitory to paclitaxel metabolism in the reported microsomal results.", "No inhibition was reported in the abstract for the tested rat/human microsomal context; this is not proof of no interaction at other concentrations, models or in vivo. Exact assay conditions and concentrations are unavailable."),
    "SB-0120": ("(-)-Epicatechin", "neither species reported", "no inhibition reported", "The primary abstract lists (-)-epicatechin among the tested phenolic antioxidants that were not inhibitory to paclitaxel metabolism in the reported microsomal results.", "No inhibition was reported in the abstract for the tested rat/human microsomal context; this is not proof of no interaction at other concentrations, models or in vivo. Exact assay conditions and concentrations are unavailable."),
    "SB-0121": ("Morin", "human", "human potency rank 3", "Human microsomes: third in the source-reported inhibitory-potency order, after fisetin and quercetin; no inhibition is reported in rat microsomes under the study conditions. The abstract says human 6α-hydroxypaclitaxel formation was generally more inhibited than C3′-hydroxypaclitaxel and inhibition was mostly mixed-type.", "Human-microsome inhibition reported; no rat-microsome inhibition reported. The abstract provides no concentrations, IC50/Ki values, donor counts or compound-specific kinetic parameters."),
}


def verify_cache(path: Path) -> None:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    items = payload.get("resultList", {}).get("result", [])
    if not any(str(item.get("pmid", item.get("id", ""))) == PMID and str(item.get("doi", "")).lower() == DOI.lower() for item in items):
        raise ValueError("archived MED metadata does not verify PMID 12920504 and DOI")


def apply() -> dict[str, object]:
    parent = ROOT.parent / "StageB_V18_20261103"
    if not parent.is_dir():
        raise FileNotFoundError("immutable V18 parent release is required")
    verify_cache(ROOT / CACHE)
    base = {r["Evidence_ID"]: r for r in read_csv("../StageB_V18_20261103/data/interaction_evidence.csv")[1]}
    blank = {eid for eid, row in base.items() if not row.get("Quantitative_Outcome", "").strip()}
    if len(blank) != 90 or not set(RECORDS) <= blank:
        raise ValueError("Batch 008 targets must be among the original V18 blank outcomes")
    current = {r["Evidence_ID"]: r for r in read_csv("data/interaction_evidence.csv")[1]}
    if any(current[eid].get("Quantitative_Outcome", "").strip() for eid in RECORDS):
        raise ValueError("Batch 008 target outcome already populated; refusing duplicate application")

    evidence_updates, audit_updates, claim_updates = {}, {}, {}
    review_fields = ["Batch", "Evidence_ID", "Compound_ID", "Compound", "Drug_Probe", "Study_ID", "PMID", "DOI", "Primary_Source_URL", "Source_Access_Status", "Local_Metadata_Cache", "Source_Locator", "Verification_Tier", "Review_Date", "Correction_Made", "Verified_Outcome", "Remaining_Limitation"]
    review_rows = []
    for eid, (compound, model, rank, abstract_finding, limitations) in RECORDS.items():
        row = current[eid]
        species_text = "rat and human liver microsomes" if "and rat" in model else ("human liver microsomes" if model == "human" else "rat and human liver microsomes")
        locator = "Publisher abstract and PubMed abstract: study model, nine named antioxidants, metabolite identities, species-specific inhibition order and mixed-type summary; full article not accessible."
        outcome = f"Tier 3 primary-abstract disposition: {abstract_finding} Quantitative assay concentrations, inhibition percentages and IC50/Ki estimates are not present in the accessible abstract and were not inferred."
        effect = f"{compound}: {abstract_finding}"
        direction = rank
        evidence_updates[eid] = {
            "Interaction_Effect": effect,
            "Mechanism": "Microsomal paclitaxel biotransformation is the assay endpoint. The abstract states inhibition was mostly mixed-type overall; compound-specific kinetic type is not reported in the accessible abstract.",
            "Evidence_Level": "compound", "Direction": direction, "Quantitative_Outcome": outcome,
            "Dose": "Paclitaxel and antioxidant concentrations, microsomal protein amounts and incubation conditions are not reported in the accessible abstract; values are not inferred.",
            "Population": "Rat and human liver microsomes; no intact human participants or animals were studied for the inhibitor outcomes.",
            "Study_Design": "In-vitro CYP-catalyzed paclitaxel-metabolism study in rat and human liver microsomes; Tier 3 abstract review only because the article full text was not accessible.",
            "Source_Title": TITLE, "Authors": AUTHORS, "Year": "2003", "DOI": DOI, "PMID": PMID,
            "Source_Type": "Primary research", "Limitations": limitations + " Full text was subscription-only in the publisher page; no legitimate author/repository full-text copy was located in this review. No clinical interaction or ordinary-food exposure conclusion follows.",
            "Confidence": "Primary abstract reviewed; Tier 3 only; concentration-level and full-method verification remain pending.",
            "Notes": "V19-008 records accessible abstract-level qualitative findings only. The source abstract does not support numerical potency values or exposure translation.",
            "Study_ID": "PMID:" + PMID, "Source_URL": URL, "Source_Cache": CACHE, "Source_Locator": locator,
            "Preparation": f"Individual named phenolic compound ({compound}); tested lot, purity and chemical form are not specified in the accessible abstract.",
            "Identity_Status": "named compound in primary abstract; reagent form/purity not verified from unavailable full text",
            "Outcome": "inhibition observed" if "reported" in rank and "no inhibition" not in rank else "no inhibition reported under tested microsomal conditions",
        }
        audit_updates[eid] = {
            "PMID": PMID, "DOI": DOI, "Source_Title": TITLE, "Source_URL": URL, "Source_Cache": CACHE,
            "Source_Locator": locator,
            "Verification_Status": "Tier 3: publisher and PubMed primary abstracts directly reviewed; full-text Methods/Results/tables unavailable",
            "Fields_Audited": "named phenolic compound; paclitaxel; rat/human microsomal model; source-reported direction and potency order; metabolite/CYP attribution at abstract level; source access and numerical limitations",
            "Limitations": evidence_updates[eid]["Limitations"], "Source_Type": "Primary research", "Verification_Date": DATE,
            "Verification_Method": "Springer publisher article page and PubMed primary record abstract reviewed and cross-checked. Springer page explicitly indicates subscription content; searches for a legitimate author or institutional full text did not locate the article. No full text, table values, numerical concentrations or assay procedures are claimed as reviewed.",
            "Verification_Level": "3", "Audit_Disposition": "V19_TIER_3_PRIMARY_ABSTRACT_REVIEWED; QUALITATIVE_OUTCOME_DISPOSITIONED; FULL_TEXT_REVIEW_PENDING",
            "Reviewer": "Codex AI-assisted primary-source curation; independent expert re-review not performed.",
            "Endpoint_Verified": "Abstract reports paclitaxel metabolism in rat and human liver microsomes, metabolites and species-specific inhibitor order; exact compound-level assay endpoint details await full text.",
            "Numerical_Outcome_Verified": "No inhibitor concentration, IC50/Ki, effect percentage, sample size or numeric assay outcome is stated in the accessible abstract; no numerical result inferred.",
            "Study_ID": "PMID:" + PMID, "Compound_ID": row["Compound_ID"], "Drug_Probe": row["Drug"],
            "V18_Unresolved_Discrepancy": "Full text and numerical assay parameters remain inaccessible; V19 disposition is abstract-only and does not certify the inherited claim beyond the abstract wording.",
        }
        claim_updates[eid] = {
            "Compound_ID": row["Compound_ID"], "PMID": PMID, "Source_Locator": locator,
            "Verification_Status": "Tier 3 source disposition: primary abstract reviewed; full text and numerical verification remain pending.",
            "Numerical_Use": "No quantitative potency or assay values used; abstract-level qualitative direction only.",
            "Attribution": f"{compound} / Paclitaxel", "Limitations": evidence_updates[eid]["Limitations"],
        }
        review_rows.append({
            "Batch": "V19-008", "Evidence_ID": eid, "Compound_ID": row["Compound_ID"], "Compound": row["Compound"],
            "Drug_Probe": "Paclitaxel", "Study_ID": "PMID:" + PMID, "PMID": PMID, "DOI": DOI,
            "Primary_Source_URL": URL,
            "Source_Access_Status": "Publisher page exposed the primary abstract and states full content is subscription-only; PubMed abstract cross-checked. Searched for an author or institutional full-text copy; none was found. Tier 3 only; full text remains unreviewed.",
            "Local_Metadata_Cache": CACHE, "Source_Locator": locator, "Verification_Tier": 3,
            "Review_Date": DATE,
            "Correction_Made": "Replaced abstract/pending text with compound-specific, primary-abstract-supported qualitative direction and an explicit statement that concentration-level values are unavailable. Corrected Evidence_Level from formulation to compound for named individual substances. Repaired the legacy local MED metadata cache path under V19-W10.",
            "Verified_Outcome": outcome, "Remaining_Limitation": evidence_updates[eid]["Limitations"],
        })

    update_rows("data/interaction_evidence.csv", "Evidence_ID", evidence_updates)
    update_rows("provenance/source_audit.csv", "Evidence_ID", audit_updates)
    update_rows("provenance/claim_support_and_verification.csv", "Evidence_ID", claim_updates)
    update_rows("data/publication_bibliography.csv", "PMID", {PMID: {"Source": CACHE}})
    with (ROOT / "validation/V19_batch_008_review.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=review_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(review_rows)
    update_rows("data/study_registry.csv", "Study_ID", {
        "PMID:" + PMID: {"Verification_Status": "V19-008: Springer publisher and PubMed primary abstracts reviewed for SB-0113–SB-0121; nine individual phenolic compounds, species-specific inhibition order and metabolite/CYP context dispositioned at Tier 3. The subscription full text was not located; numeric assay conditions remain pending."},
    })

    # The same compound-vs-formulation defect was resolved for fisetin in Batch 006.
    fields, warnings, bom = read_csv("data/warning_ledger.csv")
    existing = next((r for r in warnings if r["Warning_ID"] == "V19-W14"), None)
    if existing:
        raise ValueError("V19-W14 already exists; refusing duplicate warning creation")
    warning = {
        "Warning_ID": "V19-W14", "Code": "INDIVIDUAL_COMPOUND_MISLABELED_AS_FORMULATION",
        "Description": "Evidence_Level was set to “formulation” for individually tested named compound records SB-0110, SB-0111 and SB-0113–SB-0118. The primary articles identify fisetin or a single named phenolic antioxidant as the tested substance; no multi-ingredient formulation is described for those evidence rows.",
        "Affected": "SB-0110 | SB-0111 | SB-0113 | SB-0114 | SB-0115 | SB-0116 | SB-0117 | SB-0118",
        "Classification": "data-quality defect / evidence-level classification",
        "Before": "Evidence_Level=formulation for the listed individual-compound records.",
        "Action": "Corrected Evidence_Level to compound. Batch 006 verified and corrected the fisetin–cabazitaxel records; Batch 008 checked the nine named antioxidants in the paclitaxel abstract and corrected the six affected records. Preparation and source limitations remain explicit; no product purity is inferred.",
        "After": "Resolved; all eight listed records now classify the single named tested compound as compound.",
        "Remaining_Limitations": "The full paclitaxel article remains inaccessible, so reagent-specific form/purity and full methods are not verified. The classification correction concerns individual named test substances only.",
        "Resolution_Source": "V19_batch_006_review.csv (SB-0110, SB-0111); V19_batch_008_review.csv (SB-0113–SB-0118); primary full-text fisetin article and primary abstract for PMID 12920504.",
        "Review_Date": DATE, "Audit_Status": "RESOLVED", "Inherited_Severity": "NOT_RECORDED",
        "Audit_Rationale": "Direct source evidence identifies the tested interventions as individual named compounds rather than multi-ingredient preparations, and all eight underlying Evidence_Level fields were corrected and checked.",
        "Audit_Verification_Reference": "V19_batch_006_review.csv; V19_batch_008_review.csv; PMID 27765854 primary full text; PMID 12920504 publisher/PubMed primary abstracts.",
        "Audit_Dependencies": "None for the individual-compound versus formulation category; reagent lot/purity remain outside this verified correction.",
        "V17_Ledger_Audit_Status": "NOT_IN_V18",
    }
    warnings.append(warning)
    write_csv("data/warning_ledger.csv", fields, warnings, bom)
    af, wa, abom = read_csv("validation/V19_warning_audit.csv")
    wa.append({
        "Warning_ID": "V19-W14", "V18_Status": "NEW_IN_V19", "V19_Status": "RESOLVED",
        "V19_Recheck_Status": "RESOLVED_IN_V19-008; includes V19-006 fisetin correction",
        "V19_Review_Work": warning["Action"], "V19_Evidence_or_Rationale": warning["Audit_Verification_Reference"],
        "Remaining_Limitations": warning["Remaining_Limitations"],
    })
    write_csv("validation/V19_warning_audit.csv", af, wa, abom)

    # Expand the resolved metadata-locator warning to this seventh verified PMID.
    fields, warnings, bom = read_csv("data/warning_ledger.csv")
    w10 = next(r for r in warnings if r["Warning_ID"] == "V19-W10")
    if w10.get("Audit_Status") != "RESOLVED":
        raise ValueError("V19-W10 must remain resolved before its scope expansion")
    w10.update({
        "Description": w10["Description"].replace("and PMID 21870106", ", PMID 21870106 and PMID 12920504"),
        "Affected": w10["Affected"] + " | SB-0113–SB-0121 | bibliography PMID 12920504",
        "Action": w10["Action"] + " V19-008 scope expansion: repaired the broken MED metadata locator for PMID 12920504 across nine evidence/source-audit rows and the bibliography pointer; the archived JSON PMID/DOI was verified.",
        "After": w10["After"] + " V19-008 also repairs PMID 12920504; all seven audited PMID metadata snapshots now resolve within V19.",
        "Resolution_Source": w10["Resolution_Source"] + "; V19_batch_008_review.csv; " + CACHE,
        "Review_Date": DATE,
        "Audit_Rationale": w10["Audit_Rationale"] + " V19-008 verified PMID 12920504 and its DOI in the archived MED JSON, then repaired all nine evidence/source-audit references and the bibliography path.",
        "Audit_Verification_Reference": w10["Audit_Verification_Reference"] + "; V19_batch_008_review.csv; archived MED JSON for PMID 12920504.",
    })
    write_csv("data/warning_ledger.csv", fields, warnings, bom)
    update_rows("validation/V19_warning_audit.csv", "Warning_ID", {
        "V19-W10": {
            "V19_Recheck_Status": "RESOLVED_IN_V19-004; SAME_ROOT_CAUSE_EXPANDED_AND_REPAIRED_IN_V19-005; SAME_ROOT_CAUSE_EXPANDED_AND_REPAIRED_IN_V19-006; SAME_ROOT_CAUSE_EXPANDED_AND_REPAIRED_IN_V19-007; SAME_ROOT_CAUSE_EXPANDED_AND_REPAIRED_IN_V19-008",
            "V19_Review_Work": w10["Action"], "V19_Evidence_or_Rationale": w10["Audit_Verification_Reference"],
            "Remaining_Limitations": "All seven local JSON snapshots contain bibliographic metadata only; each scientific source's verification tier and full-text limitation are recorded per evidence record.",
        },
    })

    metadata_path = ROOT / "release_metadata.json"
    meta = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    review = meta["v19_primary_source_review"]
    batches = list(review.get("batches_completed", []))
    if "V19-008" not in batches:
        batches.append("V19-008")
    review.update({
        "batches_completed": batches, "evidence_records_reviewed": 43,
        "tier_1_primary_full_text_records": 34, "tier_3_primary_abstract_records": 9,
        "records_corrected_or_reconstructed": 41, "source_review_remaining": 274,
        "warning_rows_preserved": 84,
        "warning_status_counts": {s: sum(r.get("Audit_Status") == s for r in warnings) for s in ["RESOLVED", "PARTIALLY_RESOLVED", "STILL_VALID", "NEEDS_MANUAL_REVIEW", "NOT_APPLICABLE"]},
        "new_warning_count": 14, "warning_ids_added": [f"V19-W{i:02d}" for i in range(1, 15)],
        "warning_rows_individually_reviewed_in_v19": 16,
    })
    meta["warning_count"] = len(warnings)
    meta["v19_quantitative_outcome_audit"].update({
        "quantitative_values_recovered": 26, "qualitative_outcomes_dispositioned": 14,
        "blank_fields_remaining": 50, "source_review_batch": "V19-008",
    })
    meta["v19_validation"].update({
        "batch07_integrity": "PASS", "batch07_tests_passed": 11, "batch07_tests_failed": 0,
        "batch08_integrity": "PENDING_VALIDATION", "batch08_tests_passed": 0, "batch08_tests_failed": 0,
        "full_stageB_regression": "PENDING_FINAL_VALIDATION",
        "v19_exact_manifest": "PENDING_FINAL_PACKAGING", "v19_clean_copy_manifest": "PENDING_FINAL_PACKAGING",
    })
    meta["readiness"] = meta["release_status"] = "SCIENTIFIC_REMEDIATION_IN_PROGRESS"
    metadata_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"batch": "V19-008", "records_reviewed": 9, "verification_tier": 3,
            "qualitative_outcomes_dispositioned": 9, "quantitative_potencies_inferred": 0,
            "blank_outcomes_remaining": 50, "warnings_added": ["V19-W14 (resolved classification defect)"] ,
            "V19-W10": "RESOLVED; scope expanded to seven verified MED metadata snapshots", "status": "APPLIED_PENDING_VALIDATION"}


if __name__ == "__main__":
    print(json.dumps(apply(), indent=2, ensure_ascii=False))
