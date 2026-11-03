"""Apply V19-005 full-text extraction for the six pterostilbene/AED records."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.apply_v19_batch02 import DATE, ROOT, read_csv, update_rows, write_csv

PMID = "30877660"
DOI = "10.1007/s12640-019-00021-1"
TITLE = "Effect of Pterostilbene, a Natural Analog of Resveratrol, on the Activity of some Antiepileptic Drugs in the Acute Seizure Tests in Mice."
SOURCE_URL = "https://ppm.edu.pl/seam/resource/rest/download/UJCM536e7697615544daaa562f5337c66f8e?cid=22058&entityId=UJCM5ae99c3d92b0406793f15c80dcaf9773&entityType=article"
CACHE = "history/rebuild_artifacts/99cec0f2d566d2068a7f35f8503f49ec51454c7470812ddf65dd9a540c13e9bd_pmid_30877660.json"
RECORDS = {
    "SB-0156": {
        "drug": "Clonazepam",
        "locator": "Primary full text: Methods—Drugs and iv PTZ test; Results—Influence of PTE on anticonvulsant activity of CZP and TGB; Figure 1(a–c); Table 2(A).",
        "effect": "Pterostilbene potentiated clonazepam anticonvulsant activity in the mouse iv PTZ threshold test; measured serum and brain clonazepam concentrations did not significantly change with PTE 100 mg/kg, supporting the authors' pharmacodynamic interpretation.",
        "direction": "Pharmacodynamic potentiation reported in an acute mouse seizure-threshold model; no concentration change detected at the measured PTE dose.",
        "outcome": "Clonazepam 0.04 mg/kg; pterostilbene (PTE) 25–100 mg/kg. In the iv PTZ test, PTE 50 and 100 mg/kg significantly potentiated the first-myoclonic-twitch threshold (p<0.01 and p<0.001 vs clonazepam alone); generalized-clonic thresholds also differed at PTE 50/100 (p<0.05), and PTE 100 mg/kg increased the tonic-seizure threshold (p<0.01). Table 2(A), n=10/group at PTE 100: serum 16.40 ± 2.12 vs 14.28 ± 1.20 ng/mL (p=0.1977); total-brain 4.45 ± 0.61 vs 4.40 ± 0.32 ng/g tissue (p=0.4705). Figure 1 seizure-threshold means are not transcribed from the plots.",
        "dose": "Clonazepam 0.04 mg/kg i.p.; PTE 25, 50 or 100 mg/kg i.p. 30 min before iv PTZ threshold testing. Separate Table 2 concentration comparison used PTE 100 mg/kg and n=10/group.",
        "design": "Controlled in-vivo acute iv PTZ seizure-threshold study in male Swiss mice; 9–13 animals per seizure group. PTE and clonazepam administered intraperitoneally; seizure thresholds measured for three sequential seizure endpoints. Separate serum/brain PK comparison, n=10/group.",
        "outcome_code": "pharmacodynamic_potentiation",
        "mechanism": "The authors classify the clonazepam interaction as pharmacodynamic because serum and total-brain clonazepam concentrations did not significantly differ with PTE 100 mg/kg; this does not establish a human mechanism.",
        "limitations": "Male-mouse acute seizure model only; no human epilepsy, chronic dosing or ordinary-food/supplement exposure equivalence. Concentration comparison was made at PTE 100 mg/kg only. Exact plotted seizure-threshold means were not digitized.",
        "notes": "Pterostilbene was obtained from Toronto Research Chemicals and administered i.p. in 5% Tween 80 saline. The paper reports n=10/group for concentration data and n=9–13 in iv PTZ tests. Lot, purity and tested isomeric form are not specified.",
        "endpoint": "Clonazepam-associated iv PTZ seizure thresholds and serum/total-brain clonazepam concentrations.",
        "numerical": "Primary text reports dose, significance direction and p-values; Table 2(A) reports serum/brain concentration means, units and tests. Figure 1 threshold means were not graph-estimated.",
    },
    "SB-0157": {
        "drug": "Tiagabine",
        "locator": "Primary full text: Methods—Drugs and iv PTZ test; Results—Influence of PTE on anticonvulsant activity of CZP and TGB; Figure 1(d–f).",
        "effect": "Pterostilbene did not significantly alter tiagabine anticonvulsant activity in the mouse iv PTZ threshold test at the tested PTE doses.",
        "direction": "No statistically significant PTE effect versus tiagabine alone detected under the tested acute mouse iv PTZ conditions.",
        "outcome": "Tiagabine 5 mg/kg; PTE 25–100 mg/kg. PTE/tiagabine combinations increased PTZ thresholds versus vehicle (first-myoclonic F(4,50)=15.13, p<0.0001; generalized-clonic F(4,52)=13.49, p<0.0001; tonic forelimb-extension F(4,47)=12.05, p<0.0001), but no tested combination differed significantly from tiagabine alone (p>0.05). Figure 1 threshold means were not graph-estimated; this is a tested-condition null, not proof of no interaction at other doses or endpoints.",
        "dose": "Tiagabine 5 mg/kg i.p.; PTE 25, 50 or 100 mg/kg i.p. TGB was administered 15 min and PTE 30 min before the iv PTZ test.",
        "design": "Controlled in-vivo acute iv PTZ seizure-threshold study in male Swiss mice; 9–13 animals per group; three seizure-onset thresholds measured during intravenous PTZ infusion.",
        "outcome_code": "no_significant_activity_change_under_tested_conditions",
        "mechanism": "No PTE-associated change in tiagabine anticonvulsant activity was detected in this test; pharmacokinetic mechanism was not assessed for tiagabine.",
        "limitations": "Male-mouse acute iv PTZ model only; a nonsignificant tested-condition result does not establish absence of interaction across other doses, seizure models, chronic use, humans or dietary exposure. Figure data were not digitized.",
        "notes": "PTE was obtained from Toronto Research Chemicals; all experimental suspensions were administered intraperitoneally at 10 mL/kg. PTE lot, purity and isomeric form were not specified.",
        "endpoint": "Tiagabine-associated PTZ thresholds for first myoclonic twitch, generalized clonus and forelimb tonic extension.",
        "numerical": "Primary full text reports tiagabine and PTE doses, overall ANOVA statistics and explicitly states pairwise TGB versus TGB+PTE comparisons were not significant (p>0.05); no means estimated from Figure 1.",
    },
    "SB-0158": {
        "drug": "Carbamazepine",
        "locator": "Primary full text: Methods—Drugs and MES test; Results—Influence of PTE on anticonvulsant activity of CBZ and TPM; Figure 2(a); Table 1(C); Table 2(B); Discussion.",
        "effect": "Pterostilbene enhanced carbamazepine anticonvulsant activity in mice and increased measured serum and total-brain carbamazepine concentrations; the CBZ+PTE 100 mg/kg group also showed reduced grip strength.",
        "direction": "Increased anticonvulsant activity and CBZ exposure in mice, with a measured muscle-strength reduction at the PTE 100 mg/kg combination.",
        "outcome": "In the MES test, CBZ ED50 was 11.66 ± 0.61 mg/kg alone and 7.83 ± 0.86 mg/kg with PTE 50 mg/kg (p<0.01); PTE 100 mg/kg reduced the CBZ ED50 by approximately 50% (p<0.0001; exact graph value not digitized). Table 2(B), n=10/group after CBZ 5.9 mg/kg ± PTE 100 mg/kg: serum CBZ 2.06 ± 0.10 vs 2.41 ± 0.06 μg/mL (p=0.0043); total brain 3.72 ± 0.45 vs 5.45 ± 0.36 μg/g tissue (p=0.0039). Table 1(C), n=10: grip strength 30.38 ± 1.1 mN/g with CBZ vs 26.72 ± 1.1 mN/g with CBZ+PTE 100 mg/kg; source reports the combination differed from CBZ (p<0.05); no chimney-test motor-coordination impairment was observed.",
        "dose": "PTE 25, 50 or 100 mg/kg i.p.; CBZ ED50 assessed in the MES test. Concentration and grip-strength assays used CBZ 5.9 mg/kg with or without PTE 100 mg/kg. PTE and CBZ were administered i.p. 30 min before the MES test.",
        "design": "Controlled in-vivo maximal-electroshock seizure dose-response study in male Swiss mice; MES groups used 8 animals per dose group. Separate serum/brain concentration and grip-strength/motor-coordination experiments used n=10/group.",
        "outcome_code": "exposure_increase_and_anticonvulsant_potentiation",
        "mechanism": "Increased serum and total-brain CBZ concentrations support a pharmacokinetic contribution; the data do not establish the mechanism in humans. Grip-strength reduction is an additional measured animal outcome.",
        "limitations": "Preclinical male-mouse acute MES model only; no human clinical or food-equivalence inference. PTE 100 mg/kg combination reduced grip strength in a separate test. Exact ED50 at PTE 100 mg/kg is figure-only and not estimated.",
        "notes": "PTE from Toronto Research Chemicals; suspensions in 5% Tween 80 saline, i.p. The paper does not specify reagent lot/purity/isomer. Concentration values are means ± SEM, as reported in Table 2; grip strength is mean ± SEM.",
        "endpoint": "CBZ MES ED50, serum and total-brain CBZ concentrations, grip strength and motor coordination.",
        "numerical": "Figure 2(a) and Results verify the ED50 contrast and p-values; Table 2(B) verifies serum/brain concentration values and units; Table 1(C) verifies grip-strength values, n and significance. No exact Figure 2 ED50 point is graph-estimated.",
    },
    "SB-0159": {
        "drug": "Topiramate",
        "locator": "Primary full text: Methods—Drugs and MES test; Results—Influence of PTE on anticonvulsant activity of CBZ and TPM; Figure 2(b); Table 1(D).",
        "effect": "Pterostilbene at 25–100 mg/kg did not significantly alter topiramate anticonvulsant activity in the mouse MES test.",
        "direction": "No statistically significant PTE effect on topiramate anticonvulsant activity detected under tested MES conditions.",
        "outcome": "Topiramate 29.4 mg/kg was used in the ancillary Table 1 motor test; PTE 25–100 mg/kg did not significantly influence topiramate anticonvulsant activity in the MES dose-response study (F(3,68)=1.16, p=0.333). Table 1(D), n=10/group: grip strength 30.45 ± 1.3 mN/g for TPM alone and 31.20 ± 1.0 mN/g for TPM+PTE 100 mg/kg (overall F(2,27)=0.93, p=0.409); no motor-coordination impairment was observed. Figure 2(b) ED50 means were not graph-estimated.",
        "dose": "PTE 25, 50 or 100 mg/kg i.p.; topiramate anticonvulsant activity assessed in the MES dose-response test. Table 1(D) uses topiramate 29.4 mg/kg with or without PTE 100 mg/kg; topiramate was administered 60 min before MES and PTE 30 min before.",
        "design": "Controlled in-vivo maximal-electroshock seizure dose-response study in male Swiss mice; MES groups used 8 animals per dose group. Separate grip-strength and motor-coordination experiment, n=10/group.",
        "outcome_code": "no_significant_activity_change_under_tested_conditions",
        "mechanism": "No significant activity effect was detected in the tested MES model; no pharmacokinetic mechanism was established for topiramate.",
        "limitations": "Preclinical male-mouse acute MES model only; nonsignificant results apply to tested doses and endpoints and do not establish absence of all interactions, human effects or ordinary-food exposure effects. Figure ED50 values were not digitized.",
        "notes": "PTE supplied by Toronto Research Chemicals; suspended in 5% Tween 80 saline and administered i.p. Lot, purity and isomeric form are not stated.",
        "endpoint": "Topiramate MES ED50 response, grip strength and motor coordination.",
        "numerical": "Primary Results report overall ANOVA F and p for topiramate anticonvulsant activity; Table 1(D) reports grip-strength means/SEM and the nonsignificant group test. Figure 2(b) values not graph-estimated.",
    },
    "SB-0160": {
        "drug": "Oxcarbazepine",
        "locator": "Primary full text: Methods—Drugs and 6-Hz test; Results—Influence of PTE on anticonvulsant activity of VPA and OXC; Figure 3(b); Table 1(F); Table 2(C).",
        "effect": "Pterostilbene 100 mg/kg enhanced oxcarbazepine anticonvulsant activity in the mouse 6-Hz test and increased measured serum and total-brain oxcarbazepine concentrations.",
        "direction": "Increased anticonvulsant effect and measured exposure in a preclinical mouse 6-Hz model.",
        "outcome": "In the 6-Hz psychomotor seizure test, OXC ED50 was 17.61 ± 1.36 mg/kg alone and 9.02 ± 1.54 mg/kg with PTE 100 mg/kg (approximately 49% reduction; one-way ANOVA F(3,68)=5.31, p=0.002). Table 2(C), n=10/group after OXC 9.02 mg/kg ± PTE 100 mg/kg: serum OXC 2.97 ± 0.19 vs 4.23 ± 0.46 μg/mL (p=0.0104); total brain 3.46 ± 0.27 vs 5.47 ± 0.58 μg/g tissue (p=0.0027). Table 1(F) did not find a significant motor-strength or motor-coordination change in the OXC+PTE group. Figure 3(b) ED50 values are transcribed only where explicitly stated in prose.",
        "dose": "PTE 25, 50 or 100 mg/kg i.p. in the 6-Hz dose-response test. Table 2(C) concentration comparison used OXC 9.02 mg/kg ± PTE 100 mg/kg, both i.p., 30 min before sampling; n=10/group.",
        "design": "Controlled in-vivo 6-Hz psychomotor seizure dose-response study in male Swiss mice; 8 animals/group in the test. Separate serum/brain concentration and grip-strength/motor-coordination experiments used n=10/group.",
        "outcome_code": "exposure_increase_and_anticonvulsant_potentiation",
        "mechanism": "Increased serum and total-brain OXC concentrations support a pharmacokinetic contribution in mice; this does not establish a human mechanism or clinical interaction.",
        "limitations": "Preclinical male-mouse acute 6-Hz model only; experimental intraperitoneal dosing does not establish human therapeutic or dietary exposure effects. PTE lot/purity/isomer were not stated.",
        "notes": "PTE was obtained from Toronto Research Chemicals and suspended in 5% Tween 80 saline. No food intake or ordinary supplement exposure was tested.",
        "endpoint": "OXC 6-Hz ED50, serum and total-brain concentrations, grip strength and motor coordination.",
        "numerical": "Primary Results provide ED50 means, dose and percentage contrast; Table 2(C) provides serum/brain concentration means, units, p-values and n; Table 1(F) reports no measured motor-test difference.",
    },
    "SB-0161": {
        "drug": "Valproate",
        "locator": "Primary full text: Methods—Drugs and 6-Hz test; Results—Influence of PTE on anticonvulsant activity of VPA and OXC; Figure 3(a); Table 1(E).",
        "effect": "Pterostilbene did not produce a statistically significant pairwise change in valproate anticonvulsant activity in the mouse 6-Hz test at the tested doses; the omnibus ANOVA was significant, but post hoc comparisons with VPA alone were not.",
        "direction": "No statistically significant pairwise PTE effect versus valproate alone detected under tested 6-Hz conditions; overall group ANOVA was significant.",
        "outcome": "Valproate (sodium salt) 93 mg/kg in Table 1(E); PTE tested at 25–100 mg/kg in the 6-Hz dose-response study. Overall one-way ANOVA was F(3,69)=4.43, p=0.007, but no individual PTE+VPA group differed significantly from VPA alone in post hoc testing. Table 1(E), n=10/group: grip strength 28.09 ± 1.7 mN/g (VPA) vs 26.20 ± 1.1 mN/g (VPA+PTE 100 mg/kg), overall F(2,27)=0.82, p=0.451; no motor-coordination impairment was observed. Figure 3(a) ED50 means were not graph-estimated.",
        "dose": "PTE 25, 50 or 100 mg/kg i.p. in the 6-Hz dose-response test. Table 1(E) uses valproate sodium 93 mg/kg with or without PTE 100 mg/kg; valproate was administered 15 min and PTE 30 min before the test.",
        "design": "Controlled in-vivo 6-Hz psychomotor seizure dose-response study in male Swiss mice; 8 animals/group in the test. Separate grip-strength and motor-coordination experiment, n=10/group.",
        "outcome_code": "no_significant_pairwise_activity_change_under_tested_conditions",
        "mechanism": "No specific pharmacokinetic or pharmacodynamic mechanism was established for the VPA result; the omnibus ANOVA and nonsignificant post hoc comparisons are both retained.",
        "limitations": "Preclinical male-mouse acute 6-Hz model only. Overall omnibus significance did not translate to significant pairwise differences from VPA alone; results do not establish absence of interactions in other models, humans or food/supplement exposure.",
        "notes": "Valproate was tested as sodium salt. PTE was obtained from Toronto Research Chemicals and administered i.p. in Tween saline. PTE reagent lot/purity/isomer were not stated.",
        "endpoint": "Valproate 6-Hz ED50 response, grip strength and motor coordination.",
        "numerical": "Primary Results report omnibus F(3,69)=4.43, p=0.007 and explicitly no significant post hoc differences versus VPA alone; Table 1(E) reports motor endpoint values and p-values. Figure 3(a) ED50 values were not graph-estimated.",
    },
}


def apply() -> dict[str, object]:
    parent = ROOT.parent / "StageB_V18_20261103"
    if not parent.is_dir():
        raise FileNotFoundError("immutable V18 parent release is required")
    cache_path = ROOT / CACHE
    payload = json.loads(cache_path.read_text(encoding="utf-8-sig"))
    items = payload.get("resultList", {}).get("result", [])
    if not any(str(item.get("pmid", item.get("id", ""))) == PMID for item in items):
        raise ValueError("archived MED metadata file does not identify PMID 30877660")
    if not any(str(item.get("doi", "")).lower() == DOI.lower() for item in items):
        raise ValueError("archived MED metadata file does not verify the DOI")

    baseline = {r["Evidence_ID"]: r for r in read_csv("../StageB_V18_20261103/data/interaction_evidence.csv")[1]}
    blank_ids = {eid for eid, row in baseline.items() if not row.get("Quantitative_Outcome", "").strip()}
    if len(blank_ids) != 90 or not set(RECORDS) <= blank_ids:
        raise ValueError("Batch 005 targets must be among the 90 blank outcomes in immutable V18")
    current = {r["Evidence_ID"]: r for r in read_csv("data/interaction_evidence.csv")[1]}
    if any(current[eid].get("Quantitative_Outcome", "").strip() for eid in RECORDS):
        raise ValueError("Batch 005 outcomes already populated; refusing overwrite")

    evidence_updates = {}
    for eid, spec in RECORDS.items():
        evidence_updates[eid] = {
            "Interaction_Effect": spec["effect"], "Mechanism": spec["mechanism"],
            "Evidence_Type": "Animal", "Evidence_Level": "compound", "Direction": spec["direction"],
            "Quantitative_Outcome": spec["outcome"], "Dose": spec["dose"],
            "Population": "Male Swiss mice (23–28 g) in acute iv PTZ, maximal electroshock (MES) or 6-Hz seizure tests; group size depends on assay (8 in MES/6-Hz dose groups; 9–13 in iv PTZ; n=10 for serum/brain concentration groups).",
            "Study_Design": spec["design"], "Source_Title": TITLE, "DOI": DOI, "PMID": PMID,
            "Limitations": spec["limitations"],
            "Confidence": "Primary full text and record-specific endpoints reviewed; remaining model and exposure limits are explicit.",
            "Notes": spec["notes"], "Study_ID": "PMID:" + PMID, "Source_URL": SOURCE_URL,
            "Source_Cache": CACHE, "Source_Locator": spec["locator"],
            "Preparation": "Pterostilbene from Toronto Research Chemicals, suspended in 5% Tween 80 in saline and administered intraperitoneally; tested compound lot, purity and isomeric form not stated.",
            "Outcome": spec["outcome_code"],
        }
    update_rows("data/interaction_evidence.csv", "Evidence_ID", evidence_updates)

    audit_updates = {}
    claim_updates = {}
    for eid, spec in RECORDS.items():
        audit_updates[eid] = {
            "PMID": PMID, "DOI": DOI, "Source_Title": TITLE, "Source_URL": SOURCE_URL,
            "Source_Cache": CACHE, "Source_Locator": spec["locator"],
            "Verification_Status": "Tier 1: primary full-text PDF and record-specific Methods/Results/Figure/Table directly reviewed in V19-005",
            "Fields_Audited": "compound preparation; drug/probe; experimental model; study design; dose/route/timing; outcome direction; primary numerical values, units and statistics; adverse motor endpoint where applicable; exposure limitations",
            "Limitations": spec["limitations"], "Source_Type": "Primary research",
            "Verification_Date": DATE,
            "Verification_Method": "Primary full-text article PDF accessed via the Polish Platform of Medical Research institutional repository; Methods, Results, figures and Tables 1–2 reviewed. PubMed MED bibliographic JSON retained in release history; PMC6831770 official record independently confirms article identity/PMID/DOI.",
            "Verification_Level": "1", "Audit_Disposition": "V19_TIER_1_FULL_TEXT_REVIEWED; NUMERICAL_OUTCOME_RECOVERED; PRECLINICAL_LIMITS_RETAINED",
            "Reviewer": "Codex AI-assisted primary-source curation; independent expert re-review not performed.",
            "Endpoint_Verified": spec["endpoint"], "Numerical_Outcome_Verified": spec["numerical"],
            "Study_ID": "PMID:" + PMID, "Compound_ID": current[eid]["Compound_ID"],
            "Drug_Probe": spec["drug"],
            "V18_Unresolved_Discrepancy": "V19-005 directly reviewed full text and recovered the tested-condition outcome. No participant cohort is involved; mouse-only results do not establish human clinical or food-exposure effects.",
            "Disposition_Date": DATE,
        }
        claim_updates[eid] = {
            "PMID": PMID, "Source_Locator": spec["locator"],
            "Verification_Status": "V19 Tier 1 primary full-text review completed in V19-005; record-specific extraction in validation/V19_batch_005_review.csv.",
            "Numerical_Use": spec["numerical"],
            "Attribution": "Pterostilbene / " + spec["drug"],
            "Limitations": spec["limitations"],
        }
    update_rows("provenance/source_audit.csv", "Evidence_ID", audit_updates)
    update_rows("provenance/claim_support_and_verification.csv", "Evidence_ID", claim_updates)
    update_rows("data/publication_bibliography.csv", "PMID", {PMID: {"Source": CACHE}})

    review_fields = ["Batch", "Evidence_ID", "Compound_ID", "Compound", "Drug_Probe", "Study_ID", "PMID", "DOI", "Primary_Source_URL", "Source_Access_Status", "Local_Metadata_Cache", "Source_Locator", "Verification_Tier", "Review_Date", "Correction_Made", "Verified_Outcome", "Remaining_Limitation"]
    review_rows = []
    for eid, spec in RECORDS.items():
        row = current[eid]
        review_rows.append({
            "Batch": "V19-005", "Evidence_ID": eid, "Compound_ID": row["Compound_ID"],
            "Compound": row["Compound"], "Drug_Probe": spec["drug"], "Study_ID": "PMID:" + PMID,
            "PMID": PMID, "DOI": DOI, "Primary_Source_URL": SOURCE_URL,
            "Source_Access_Status": "Full primary article PDF reviewed from Polish Platform of Medical Research institutional repository; PubMed/PMC bibliographic identity cross-checked.",
            "Local_Metadata_Cache": CACHE, "Source_Locator": spec["locator"], "Verification_Tier": "1",
            "Review_Date": DATE,
            "Correction_Made": "Replaced inherited abstract-only/pending disposition with a dose-, model-, endpoint- and source-specific full-text extraction; recorded positive and null tested-condition findings, PK results and the carbamazepine-associated grip-strength finding. Repaired the legacy MED JSON path and expanded V19-W10 scope to include this newly verified broken pointer.",
            "Verified_Outcome": spec["outcome"], "Remaining_Limitation": spec["limitations"],
        })
    with (ROOT / "validation/V19_batch_005_review.csv").open("w", encoding="utf-8", newline="") as handle:
        import csv
        writer = csv.DictWriter(handle, fieldnames=review_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(review_rows)

    update_rows("data/study_registry.csv", "Study_ID", {
        "PMID:" + PMID: {"Verification_Status": "V19-005: primary full-text PDF, Methods, Results, Figures 1–3 and Tables 1–2 reviewed for SB-0156–SB-0161. Positive and tested-condition null mouse seizure findings, concentration changes and carbamazepine grip-strength reduction recorded separately."},
    })

    # Expand the already-opened root-cause warning while preserving its ID and the
    # V19-004 resolution history; all affected local metadata pointers now validate.
    fields, warnings, bom = read_csv("data/warning_ledger.csv")
    warning = next((row for row in warnings if row["Warning_ID"] == "V19-W10"), None)
    if warning is None or warning.get("Audit_Status") != "RESOLVED":
        raise ValueError("V19-W10 must exist and carry its verified V19-004 closure before expansion")
    warning.update({
        "Description": "The metadata Source/Source_Cache paths for PMID 24276478, PMID 26396928 and PMID 30877660 pointed to absent legacy release locations in V19, even though matching PubMed MED JSON snapshots exist under history/rebuild_artifacts. This broke local metadata provenance locators for SB-0138/0139, SB-0182/0183 and SB-0156–SB-0161.",
        "Affected": "SB-0138 | SB-0139 | SB-0156–SB-0161 | SB-0182 | SB-0183 | bibliography PMIDs 24276478, 26396928, 30877660",
        "Action": warning["Action"] + " V19-005 scope expansion: repaired the same broken MED metadata locator root cause for PMID 30877660 by pointing all six affected evidence/source-audit rows and its bibliography row to the existing archived MED JSON; validated its PMID and DOI.",
        "After": "Resolved across all three audited publication metadata snapshots; each affected bibliography and evidence/source-audit row now points to a present matching MED JSON file. V19-004 repaired the first two PMIDs; V19-005 discovered and repaired the third instance.",
        "Resolution_Source": warning["Resolution_Source"] + "; V19_batch_005_review.csv; history/rebuild_artifacts/" + Path(CACHE).name,
        "Review_Date": DATE,
        "Audit_Rationale": "V19-004 repaired and verified the original two broken pointers. V19-005 extended the same warning after finding the identical root-cause defect in PMID 30877660; all three archived MED JSON files and affected local pointers now validate. No metadata snapshots were modified.",
        "Audit_Verification_Reference": warning["Audit_Verification_Reference"] + "; V19_batch_005_review.csv; archived MED metadata JSON for PMID 30877660.",
        "Audit_Dependencies": "None for the repaired local locator; all cached files contain bibliographic metadata only, not article full text.",
    })
    write_csv("data/warning_ledger.csv", fields, warnings, bom)
    update_rows("validation/V19_warning_audit.csv", "Warning_ID", {
        "V19-W10": {
            "V19_Status": "RESOLVED",
            "V19_Recheck_Status": "RESOLVED_IN_V19-004; SAME_ROOT_CAUSE_EXPANDED_AND_REPAIRED_IN_V19-005",
            "V19_Review_Work": "V19-004 repaired PMID 24276478 and 26396928 cache links. V19-005 found and repaired the same absent-legacy-path issue for PMID 30877660; six evidence rows and one bibliography source pointer now resolve to the archived MED JSON.",
            "V19_Evidence_or_Rationale": "V19-004 and V19-005 validate matching PubMed MED JSON files for PMIDs 24276478, 26396928 and 30877660 and update all affected Source/Source_Cache locators. Full-text verification is separately documented per evidence record.",
            "Remaining_Limitations": "The three cached JSON files contain bibliographic metadata, not full text; source full texts were independently reviewed and are recorded in their respective batch review files.",
        },
    })

    metadata_path = ROOT / "release_metadata.json"
    meta = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    meta["readiness"] = meta["release_status"] = "SCIENTIFIC_REMEDIATION_IN_PROGRESS"
    review_meta = meta["v19_primary_source_review"]
    review_meta.update({
        "batches_completed": ["V19-001", "V19-002", "V19-003", "V19-004", "V19-005"],
        "evidence_records_reviewed": 28, "tier_1_primary_full_text_records": 28,
        "records_corrected_or_reconstructed": 26, "source_review_remaining": 289,
        "warning_rows_preserved": 80,
        "warning_status_counts": {status: sum(row.get("Audit_Status") == status for row in warnings) for status in ["RESOLVED", "PARTIALLY_RESOLVED", "STILL_VALID", "NEEDS_MANUAL_REVIEW", "NOT_APPLICABLE"]},
        "new_warning_count": 10,
        "warning_ids_added": [f"V19-W{i:02d}" for i in range(1, 11)],
        "warning_rows_individually_reviewed_in_v19": 12,
    })
    meta["v19_quantitative_outcome_audit"].update({
        "quantitative_values_recovered": 20,
        "qualitative_outcomes_dispositioned": 5,
        "blank_fields_remaining": 65,
        "source_review_batch": "V19-005",
    })
    meta["v19_validation"].update({
        "batch04_integrity": "PASS_PENDING_FINAL_MANIFEST",
        "batch04_tests_passed": 12, "batch04_tests_failed": 0,
        "batch05_integrity": "PENDING_VALIDATION",
        "batch05_tests_passed": 0, "batch05_tests_failed": 0,
        "full_stageB_regression": "PENDING_FINAL_VALIDATION",
        "v19_exact_manifest": "PENDING_FINAL_PACKAGING",
        "v19_clean_copy_manifest": "PENDING_FINAL_PACKAGING",
    })
    metadata_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "batch": "V19-005", "records_updated": len(RECORDS),
        "quantitative_outcomes_recovered": len(RECORDS), "remaining_blank_outcomes": 65,
        "new_warning_rows": 0, "V19-W10": "RESOLVED; same-root-cause scope expanded and reverified",
        "status": "APPLIED_PENDING_VALIDATION",
    }


if __name__ == "__main__":
    print(json.dumps(apply(), indent=2, ensure_ascii=False))
