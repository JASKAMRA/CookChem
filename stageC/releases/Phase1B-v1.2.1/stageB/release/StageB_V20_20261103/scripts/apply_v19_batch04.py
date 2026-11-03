"""Apply V19-004 primary-source review of four inherited blank outcomes."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.apply_v19_batch02 import DATE, ROOT, read_csv, update_rows, write_csv

CACHES = {
    "24276478": "history/rebuild_artifacts/56800bfd89cb785cadf533fc8887c7a4f29bc1b233333f1ad2c10102b6720893_pmid_24276478.json",
    "26396928": "history/rebuild_artifacts/306d5b6e6fb6056adf5a6a03f3d32e5d7e48dfd1c6dfe73c63cfb76522f43506_pmid_26396928.json",
}

SOURCES = {
    "24276478": {
        "doi": "10.3892/mmr.2013.1830",
        "title": "Cinnamaldehyde/chemotherapeutic agents interaction and drug-metabolizing genes in colorectal cancer.",
        "url": "https://www.spandidos-publications.com/10.3892/mmr.2013.1830",
        "access": "Primary Spandidos publisher article page and full-text PDF reviewed; Methods, Results, Table I, Figure 2 and Discussion accessed. Local PubMed MED metadata is retained in the release history archive.",
    },
    "26396928": {
        "doi": "",
        "title": "Synergistic effect of allyl isothiocyanate (AITC) on cisplatin efficacy in vitro and in vivo.",
        "url": "https://e-century.us/files/ajcr/5/8/ajcr0010340.pdf",
        "access": "Primary journal full-text PDF reviewed directly; Methods, CI analysis, Results, Figure 5 and Table 1 accessed. PubMed MED record confirms PMID/PMCID but supplies no DOI; no DOI is present in the accessed PDF. Local MED metadata is retained in the release history archive.",
    },
}

BATCH4 = {
    "SB-0138": {
        "pmid": "24276478", "drug": "5-Fluorouracil",
        "locator": "Spandidos full text: Materials and Methods—Drugs, Cell culture, Measurement of IC50 and Determination of synergism and antagonism; Results—combined treatment; Table I; Figure 2; Discussion.",
        "effect": "Cinnamaldehyde plus 5-fluorouracil showed synergy in HT-29 cells and concentration-dependent synergy/antagonism across the tested colorectal cell models; LoVo antagonism occurred at some concentrations.",
        "direction": "Context-dependent in-vitro synergy and antagonism reported; exact CI values are plotted, not tabulated or graph-digitized.",
        "outcome": "Qualitative outcome only. The article reports cinnamaldehyde/5-fluorouracil synergy in HT-29 and synergy in LoVo only over certain concentration ranges, with antagonism at other LoVo ranges. Figure 2C (HT-29) and 2A (LoVo) show CI-versus-fraction-affected plots; exact CI values are not tabulated and were not estimated from the graph.",
        "dose": "Cinnamaldehyde (98.6% purity) plus 5-fluorouracil tested as fixed-ratio combinations based on individual-agent IC50 values for 48 h; at least three independent experiments. Individual IC50 mean ± SD (μg/mL): HT-29 cinnamaldehyde 9.12 ± 0.46 and 5-FU 8.16 ± 0.30; LoVo cinnamaldehyde 9.48 ± 0.10 and 5-FU 2.91 ± 0.46. Pair-specific combination concentrations are not tabulated.",
        "population": "In-vitro human colon adenocarcinoma cell lines: well-differentiated HT-29 and poorly differentiated LoVo.",
        "design": "Experimental in-vitro cell study; fixed-ratio drug combinations based on single-agent IC50 values; 48-h exposure; Chou–Talalay combination-index analysis; at least three independent experiments.",
        "limitations": "In-vitro colorectal cancer cell lines only. LoVo response varies by concentration, with antagonism at some ranges. Exact combination-index values are only shown graphically and were not digitized. The study does not establish human clinical or ordinary-food exposure effects. Cinnamaldehyde purity is given, but geometric-isomer composition is not specified.",
        "notes": "The paper reports cinnamaldehyde powder purity 98.6% (National Institutes for Food and Drug Control). Individual-agent Table I IC50 values are included for context, not misrepresented as pair-specific outcome values. No plotted CI values were estimated.",
        "claim": "Primary Methods verify tested compound and 48-h fixed-ratio Chou–Talalay design; Table I verifies single-agent IC50 values; Figure 2 and Discussion support HT-29 synergy and concentration-dependent LoVo synergy/antagonism. Figure 2 exact CI values were not transcribed or estimated.",
        "remaining": "No tabulated pair-specific CI values or pair concentrations; the paper describes concentration-dependent antagonism in LoVo. Cinnamaldehyde geometric form is not specified.",
        "endpoint": "Cinnamaldehyde/5-FU combination-index interaction by colorectal cell line and concentration range; single-agent IC50 table verified separately.",
        "numerical": "Table I single-agent IC50 means/SD and units verified. Figure 2C and 2A qualitative CI plots reviewed; exact pairwise CI values are not tabulated, so the pair outcome is recorded qualitatively without graph digitization.",
        "disposition": "V19_TIER_1_FULL_TEXT_REVIEWED; QUALITATIVE_OUTCOME_ONLY; PLOT_VALUES_NOT_ESTIMATED",
    },
    "SB-0139": {
        "pmid": "24276478", "drug": "Oxaliplatin",
        "locator": "Spandidos full text: Materials and Methods—Drugs, Cell culture, Measurement of IC50 and Determination of synergism and antagonism; Results—combined treatment; Table I; Figure 2; Discussion.",
        "effect": "Cinnamaldehyde plus oxaliplatin showed synergy in HT-29 cells and concentration-dependent synergy/antagonism across the tested colorectal cell models; LoVo antagonism occurred at some concentrations.",
        "direction": "Context-dependent in-vitro synergy and antagonism reported; exact CI values are plotted, not tabulated or graph-digitized.",
        "outcome": "Qualitative outcome only. The article reports cinnamaldehyde/oxaliplatin synergy in HT-29 and synergy in LoVo only over certain concentration ranges, with antagonism at other LoVo ranges. Figure 2D (HT-29) and 2B (LoVo) show CI-versus-fraction-affected plots; exact CI values are not tabulated and were not estimated from the graph.",
        "dose": "Cinnamaldehyde (98.6% purity) plus oxaliplatin tested as fixed-ratio combinations based on individual-agent IC50 values for 48 h; at least three independent experiments. Individual IC50 mean ± SD (μg/mL): HT-29 cinnamaldehyde 9.12 ± 0.46 and OXA 6.63 ± 1.86; LoVo cinnamaldehyde 9.48 ± 0.10 and OXA 7.05 ± 0.67. Pair-specific combination concentrations are not tabulated.",
        "population": "In-vitro human colon adenocarcinoma cell lines: well-differentiated HT-29 and poorly differentiated LoVo.",
        "design": "Experimental in-vitro cell study; fixed-ratio drug combinations based on single-agent IC50 values; 48-h exposure; Chou–Talalay combination-index analysis; at least three independent experiments.",
        "limitations": "In-vitro colorectal cancer cell lines only. LoVo response varies by concentration, with antagonism at some ranges. Exact combination-index values are only shown graphically and were not digitized. The study does not establish human clinical or ordinary-food exposure effects. Cinnamaldehyde purity is given, but geometric-isomer composition is not specified.",
        "notes": "The paper reports cinnamaldehyde powder purity 98.6% (National Institutes for Food and Drug Control). Individual-agent Table I IC50 values are included for context, not misrepresented as pair-specific outcome values. No plotted CI values were estimated.",
        "claim": "Primary Methods verify tested compound and 48-h fixed-ratio Chou–Talalay design; Table I verifies single-agent IC50 values; Figure 2 and Discussion support HT-29 synergy and concentration-dependent LoVo synergy/antagonism. Figure 2 exact CI values were not transcribed or estimated.",
        "remaining": "No tabulated pair-specific CI values or pair concentrations; the paper describes concentration-dependent antagonism in LoVo. Cinnamaldehyde geometric form is not specified.",
        "endpoint": "Cinnamaldehyde/oxaliplatin combination-index interaction by colorectal cell line and concentration range; single-agent IC50 table verified separately.",
        "numerical": "Table I single-agent IC50 means/SD and units verified. Figure 2D and 2B qualitative CI plots reviewed; exact pairwise CI values are not tabulated, so the pair outcome is recorded qualitatively without graph digitization.",
        "disposition": "V19_TIER_1_FULL_TEXT_REVIEWED; QUALITATIVE_OUTCOME_ONLY; PLOT_VALUES_NOT_ESTIMATED",
    },
    "SB-0182": {
        "pmid": "26396928", "drug": "Cisplatin",
        "locator": "AJCR full-text PDF: Materials and Methods—MTT cell viability, CI analysis and cell models; Results—synergistic interaction; Figure 1 and Figure 5; Discussion.",
        "effect": "AITC/cisplatin combination-index analysis reported CI ≤1 across tested combinations in A549 and HOP62 lung cancer cells; most were <1, and CI was much smaller than 0.5 for AITC 10–20 μM with cisplatin 8–16 μM.",
        "direction": "In-vitro synergy reported for specified cell models and dose ranges; not evidence of clinical food–drug interaction.",
        "outcome": "Combination-index analysis (Figure 5; 72 h) in A549 and HOP62 lung cancer cells: source reports CI ≤1 for all tested dose ranges, most combinations CI <1, and CI much smaller than 0.5 for AITC 10–20 μM plus cisplatin 8–16 μM. Exact pointwise CI values are graphical and are not transcribed or estimated. Separate MTT/colony experiments report increased growth inhibition with the combination. The MTT treatment duration is inconsistent within the source (Methods/Figure 1 caption: 96 h; Results prose: 72 h; V19-W09).",
        "dose": "CI analysis: AITC 10–20 μM with cisplatin 8–16 μM produced CI values described as much smaller than 0.5; Figure 5 assays at 72 h. CI-tested lung cancer cell lines: A549 and HOP62. MTT methods/Figure 1 specify 96 h, while Results prose states 72 h (V19-W09). Exact graph point values are not estimated.",
        "population": "In-vitro cancer cell models. MTT and colony assays: 2008 human ovarian and HOP62 human lung cancer cells; CI analysis: A549 and HOP62 human lung cancer cells.",
        "design": "Experimental in-vitro study using MTT growth assay, colony formation and Chou–Talalay combination-index analysis. CI analysis was conducted for 72 h in A549/HOP62 cells; MTT timing conflicts between Methods/Figure 1 and Results text (V19-W09).",
        "limitations": "Cell-line preclinical evidence only. Exact CI values are presented graphically and were not digitized. MTT duration is inconsistent in the paper (Methods/Figure 1: 96 h; Results: 72 h), tracked as V19-W09. No human clinical effect or equivalence to dietary AITC exposure is established.",
        "notes": "Primary article reports cell growth/colony and apoptosis endpoints; mechanism statements are author-proposed, not clinical proof. No numerical CI points were graph-estimated. Bibliographic MED record and publisher PDF provide no DOI; PMID 26396928 and PMCID PMC4568788 are retained.",
        "claim": "Figure 5 and Results verify CI≤1 across tested ranges, most CI<1 and very strong synergy for AITC 10–20 μM plus cisplatin 8–16 μM in A549/HOP62 cells at 72 h. Figure 1/Methods verify growth/colony model; MTT duration conflict with Results is retained under V19-W09.",
        "remaining": "No pointwise CI values were tabulated; MTT exposure duration conflicts between Methods/Figure caption and Results text; no food-dose or human clinical inference.",
        "endpoint": "In-vitro cell growth/colony inhibition and combination-index response; CI model and dose range verified.",
        "numerical": "Primary full text states CI≤1 for all tested combinations, most <1, and CI much smaller than 0.5 at AITC 10–20 μM plus cisplatin 8–16 μM; Figure 5 reviewed. No exact CI points were digitized. Cell assay time conflict recorded.",
        "disposition": "V19_TIER_1_FULL_TEXT_REVIEWED; CI_RANGE_REPORTED; MTT_DURATION_CONFLICT_OPEN",
    },
    "SB-0183": {
        "pmid": "26396928", "drug": "Cisplatin",
        "locator": "AJCR full-text PDF: Materials and Methods—Human tumor xenograft mouse model and treatment; Results—xenograft efficacy; Figure 6; Table 1; Discussion.",
        "effect": "In A549 human lung cancer xenograft-bearing athymic nude mice, AITC plus cisplatin increased tumor growth inhibition versus either single agent; the paper reports no significant increase in systemic toxicity/body-weight loss.",
        "direction": "Enhanced antitumor response in a preclinical A549 xenograft model; does not establish a human therapeutic or food–drug effect.",
        "outcome": "Table 1 (A549 human lung xenografts; 5 mice/group): combination maximum tumor growth inhibition 94.3 ± 4.8%; tumor doubling time >24 days; partial response 60%; complete response 20%; maximum body-weight loss 6.1 ± 3.1%; lethality 0. Comparator cisplatin alone: 30.2 ± 10.1% maximum tumor growth inhibition and 9.7 ± 1.2 days doubling time. The AITC-alone maximum tumor growth inhibition differs between Table 1 (46.4 ± 18.3%) and Results prose (46.6 ± 18.3%); both source values are retained under V19-W08. The source's AITC schedule/timing statements conflict (V19-W07).",
        "dose": "Twenty female athymic nude mice bearing A549 human lung cancer xenografts randomized to four groups (n=5/group). Methods: AITC 50 mg/kg orally in vegetable oil every other day for 2 weeks, starting at tumor tissue implantation; cisplatin 6 mg/kg IV once when tumors reached approximately 200–250 mm³, about 7 days after implantation. Table 1 lists AITC every 2 days ×8 and notes treatment initiation 6 days after transplantation; Discussion describes daily oral AITC (V19-W07).",
        "population": "Female athymic nude mice bearing subcutaneous A549 human lung cancer xenografts; 20 mice, four groups, n=5/group.",
        "design": "Controlled in-vivo human tumor xenograft experiment; randomized four-arm comparison (vehicle, AITC, cisplatin, combination); tumor volume followed through day 28; combination treatment versus single agents.",
        "limitations": "Single preclinical xenograft model, n=5/group. High experimental AITC dose and parenteral cisplatin regimen do not establish food exposure or clinical benefit. Source schedule/timing discrepancy (V19-W07) and AITC-alone MTGI numerical mismatch (V19-W08) remain open. Body-weight loss alone is not a comprehensive safety assessment.",
        "notes": "Article reports AITC in vegetable oil and cisplatin in a clinically used formulation. Combination weight loss was 6.1 ± 3.1% (Table 1) and no deaths; source claims no significant additional toxicity. Do not interpret as comprehensive safety or human evidence.",
        "claim": "Methods and Table 1 verify mouse sex, model, group sizes, routes, doses, schedule and tumor endpoints; Figure 6 and Table 1 verify combination tumor inhibition and weight-loss endpoints. Methods/Table and Discussion differ on AITC schedule/timing (V19-W07); Table 1 and Results prose differ on AITC-alone MTGI (V19-W08).",
        "remaining": "Source dose/timing conflict needs source/expert adjudication; AITC-alone MTGI is 46.4 in Table 1 versus 46.6 in Results prose; n=5/group and a single mouse xenograft model limit inference.",
        "endpoint": "A549 xenograft maximum tumor growth inhibition, tumor doubling time, partial/complete response, maximum body-weight loss and lethality.",
        "numerical": "Table 1 values transcribed as printed with units and n; Methods and Table 1 dose regimen retained separately from conflicting Discussion and table-footnote wording. Results prose/Table 1 AITC-alone MTGI mismatch is not reconciled by assumption.",
        "disposition": "V19_TIER_1_FULL_TEXT_REVIEWED; ANIMAL_OUTCOME_RECOVERED; SOURCE_DOSING_AND_MTG_DISCREPANCIES_OPEN",
    },
}


def append_warning(warning_id: str, code: str, description: str, affected: str,
                   classification: str, before: str, action: str, after: str,
                   limitations: str, resolution_source: str, status: str,
                   rationale: str, verification_reference: str, dependencies: str) -> dict[str, str]:
    return {
        "Warning_ID": warning_id, "Code": code, "Description": description, "Affected": affected,
        "Classification": classification, "Before": before, "Action": action, "After": after,
        "Remaining_Limitations": limitations, "Resolution_Source": resolution_source,
        "Review_Date": DATE, "Audit_Status": status, "Inherited_Severity": "NOT_RECORDED",
        "Audit_Rationale": rationale, "Audit_Verification_Reference": verification_reference,
        "Audit_Dependencies": dependencies, "V17_Ledger_Audit_Status": "NOT_IN_V18",
    }


def apply() -> dict[str, object]:
    parent = ROOT.parent / "StageB_V18_20261103"
    if not parent.is_dir():
        raise FileNotFoundError("immutable V18 baseline is required")
    for pmid, rel in CACHES.items():
        path = ROOT / rel
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        items = payload.get("resultList", {}).get("result", [])
        if not path.is_file() or not any(str(item.get("pmid", item.get("id", ""))) == pmid for item in items):
            raise ValueError(f"metadata cache does not validate PMID {pmid}: {rel}")

    baseline_evidence = {row["Evidence_ID"]: row for row in read_csv("../StageB_V18_20261103/data/interaction_evidence.csv")[1]}
    blank_ids = {eid for eid, row in baseline_evidence.items() if not row.get("Quantitative_Outcome", "").strip()}
    if len(blank_ids) != 90 or not set(BATCH4) <= blank_ids:
        raise ValueError("Batch 004 must target four inherited V18 blank outcomes")

    current_evidence = {row["Evidence_ID"]: row for row in read_csv("data/interaction_evidence.csv")[1]}
    if any(current_evidence[eid].get("Quantitative_Outcome", "").strip() for eid in BATCH4):
        raise ValueError("Batch 004 records have already been applied; refusing overwrite")

    evidence_updates: dict[str, dict[str, str]] = {}
    for evidence_id, spec in BATCH4.items():
        source = SOURCES[spec["pmid"]]
        evidence_updates[evidence_id] = {
            "Interaction_Effect": spec["effect"], "Direction": spec["direction"],
            "Quantitative_Outcome": spec["outcome"], "Dose": spec["dose"],
            "Population": spec["population"], "Study_Design": spec["design"],
            "Source_Title": source["title"], "DOI": source["doi"], "PMID": spec["pmid"],
            "Limitations": spec["limitations"], "Confidence": "Primary full-text source reviewed; record-specific evidence and limitations documented in V19_batch_004_review.csv.",
            "Notes": spec["notes"], "Source_URL": source["url"], "Source_Cache": CACHES[spec["pmid"]],
            "Source_Locator": spec["locator"], "Study_ID": "PMID:" + spec["pmid"],
            "Outcome": "context_dependent_synergy_and_antagonism_reported" if evidence_id in {"SB-0138", "SB-0139"} else "synergy_detected" if evidence_id == "SB-0182" else "enhanced_antitumor_response",
        }
    update_rows("data/interaction_evidence.csv", "Evidence_ID", evidence_updates)

    audit_updates: dict[str, dict[str, str]] = {}
    claim_updates: dict[str, dict[str, str]] = {}
    for evidence_id, spec in BATCH4.items():
        source = SOURCES[spec["pmid"]]
        source_cache = CACHES[spec["pmid"]]
        audit_updates[evidence_id] = {
            "PMID": spec["pmid"], "DOI": source["doi"], "Source_Title": source["title"],
            "Source_URL": source["url"], "Source_Cache": source_cache, "Source_Locator": spec["locator"],
            "Verification_Status": "Tier 1: primary full text and relevant methods/results/figure/table directly reviewed in V19-004",
            "Fields_Audited": "tested compound/form; source identity and citation; model and design; outcome direction; dose/regimen; endpoint; numerical values/units or explicit qualitative-only status; source limitations/discrepancies",
            "Limitations": spec["limitations"], "Source_Type": "Primary research", "Verification_Date": DATE,
            "Verification_Method": source["access"], "Verification_Level": "1",
            "Audit_Disposition": spec["disposition"],
            "Reviewer": "Codex AI-assisted primary-source curation; source limitations are stated per record. Independent expert adjudication remains open where identified in the record-specific review.",
            "Endpoint_Verified": spec["endpoint"], "Numerical_Outcome_Verified": spec["numerical"],
            "Study_ID": "PMID:" + spec["pmid"], "Compound_ID": current_evidence[evidence_id]["Compound_ID"],
            "Drug_Probe": spec["drug"],
            "V18_Unresolved_Discrepancy": "V19-004 directly reviewed primary full text. " + spec["remaining"],
            "Disposition_Date": DATE,
        }
        claim_updates[evidence_id] = {
            "PMID": spec["pmid"], "Source_Locator": spec["locator"],
            "Verification_Status": "V19 Tier 1 primary full-text review completed in V19-004; record-specific review available in validation/V19_batch_004_review.csv.",
            "Numerical_Use": spec["claim"],
            "Attribution": current_evidence[evidence_id]["Compound"] + " / " + spec["drug"],
            "Limitations": spec["limitations"],
        }
    update_rows("provenance/source_audit.csv", "Evidence_ID", audit_updates)
    update_rows("provenance/claim_support_and_verification.csv", "Evidence_ID", claim_updates)

    bibliography_updates = {pmid: {"Source": rel} for pmid, rel in CACHES.items()}
    update_rows("data/publication_bibliography.csv", "PMID", bibliography_updates)

    review_fields = ["Batch", "Evidence_ID", "Compound_ID", "Compound", "Drug_Probe", "Study_ID", "PMID", "DOI", "Primary_Source_URL", "Source_Access_Status", "Local_Metadata_Cache", "Source_Locator", "Verification_Tier", "Review_Date", "Correction_Made", "Verified_Outcome", "Remaining_Limitation"]
    review_rows = []
    for evidence_id, spec in BATCH4.items():
        row = current_evidence[evidence_id]
        source = SOURCES[spec["pmid"]]
        review_rows.append({
            "Batch": "V19-004", "Evidence_ID": evidence_id, "Compound_ID": row["Compound_ID"],
            "Compound": row["Compound"], "Drug_Probe": spec["drug"], "Study_ID": row["Study_ID"],
            "PMID": spec["pmid"], "DOI": source["doi"], "Primary_Source_URL": source["url"],
            "Source_Access_Status": source["access"], "Local_Metadata_Cache": CACHES[spec["pmid"]],
            "Source_Locator": spec["locator"], "Verification_Tier": "1", "Review_Date": DATE,
            "Correction_Made": "Replaced inherited pending/abstract-only source status with direct primary full-text review; recorded the source-supported outcome and model. Cinnamaldehyde CI plots were not digitized; AITC animal regimen and quantitative discrepancies are preserved without assumption. Repaired the two PMID metadata-cache locators to the existing archived MED JSON files.",
            "Verified_Outcome": spec["outcome"], "Remaining_Limitation": spec["remaining"],
        })
    with (ROOT / "validation/V19_batch_004_review.csv").open("w", encoding="utf-8", newline="") as handle:
        import csv
        writer = csv.DictWriter(handle, fieldnames=review_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(review_rows)

    update_rows("data/study_registry.csv", "Study_ID", {
        "PMID:24276478": {"Verification_Status": "V19-004: Spandidos primary publisher full-text PDF; methods, Table I, Figure 2 and Discussion reviewed for SB-0138/0139. HT-29 synergy and concentration-dependent LoVo synergy/antagonism verified; exact CI points not graph-digitized."},
        "PMID:26396928": {"Verification_Status": "V19-004: primary AJCR full-text PDF; in-vitro methods/Figure 5 and A549 xenograft Methods/Figure 6/Table 1 reviewed for SB-0182/0183. CI ranges and animal outcomes extracted; source timing, regimen and MTGI discrepancies remain open."},
    })

    ref = "Primary article full text and V19_batch_004_review.csv"
    new_warnings = [
        append_warning("V19-W07", "AITC_XENOGRAFT_REGIMEN_AND_START_TIME_CONFLICT",
            "For SB-0183 (PMID 26396928), the source describes AITC 50 mg/kg orally every other day for two weeks starting at tumor-tissue implantation in Methods, Table 1 lists every 2 days ×8 and a footnote says treatment began 6 days after transplantation, while Discussion calls AITC administration daily. Preserve the protocol statements separately; a single start time/frequency cannot be selected without source adjudication.",
            "SB-0183 | PMID:26396928 | Methods, Discussion and Table 1", "scientific source discrepancy / animal regimen",
            "The inherited record reported an animal xenograft result but did not include its regimen.",
            "Reviewed full-text Methods, Results, Figure 6, Table 1 and Discussion; recorded dose, route and all conflicting frequency/start-time statements in SB-0183 without normalizing them.",
            "Open; methods and table support alternate-day ×8 AITC, while Discussion says daily and treatment-start timing differs between Methods and table note.",
            "Author/source clarification is needed to resolve the timing/frequency language; animal result remains specific to this A549 xenograft protocol.",
            ref + "; AJCR full-text PDF, Methods—Human tumor xenograft mouse model and treatment; Discussion; Table 1.", "NEEDS_MANUAL_REVIEW",
            "Conflicting administration frequency and start-time statements appear in the primary source. Methods and table are retained in the record, but the paper's discussion/footnote prevents a fully reconciled regimen.",
            ref + "; PMID 26396928, source locators in SB-0183.", "Source/author clarification or independent expert adjudication."),
        append_warning("V19-W08", "AITC_ALONE_TUMOR_GROWTH_INHIBITION_TABLE_PROSE_MISMATCH",
            "For SB-0183 (PMID 26396928), AITC-alone maximum tumor growth inhibition is 46.4 ± 18.3% in Table 1 but 46.6 ± 18.3% in Results prose. The combination value is 94.3 ± 4.8% in Table 1. Preserve both AITC-alone values; do not silently choose or average them.",
            "SB-0183 | PMID:26396928 | Results and Table 1", "scientific source discrepancy / numerical outcome",
            "The inherited record had no re-extracted quantitative outcome.",
            "Transcribed combination and cisplatin comparator values from Table 1; recorded both differing AITC-alone values in the outcome and review ledger.",
            "Open; source reports 46.4 ± 18.3% in Table 1 and 46.6 ± 18.3% in Results prose.",
            "The primary article does not explain the 0.2-percentage-point difference; preserve source values pending author/source clarification.",
            ref + "; AJCR full-text PDF, Results text and Table 1.", "NEEDS_MANUAL_REVIEW",
            "The exact AITC-alone estimate differs between prose and table; no rounding, averaging or preferred value is assumed.",
            ref + "; PMID 26396928, source locators in SB-0183.", "Author/source clarification or independent expert review."),
        append_warning("V19-W09", "AITC_IN_VITRO_MTT_EXPOSURE_DURATION_CONFLICT",
            "For SB-0182 (PMID 26396928), the MTT assay duration is stated as 96 h in Methods and the Figure 1 caption, but the Results text says the MTT assay was carried out 72 h after treatment. The separate combination-index Figure 5 explicitly uses 72 h. Keep MTT timing qualified and do not conflate it with the CI assay duration.",
            "SB-0182 | PMID:26396928 | Methods, Results and Figure 1/Figure 5", "scientific source discrepancy / assay design",
            "Inherited record did not contain independently verified assay timing.",
            "Reviewed the full-text Methods, Results and figures; separated the 72-h CI analysis from the conflicting MTT duration statements in SB-0182.",
            "Open; MTT duration is 96 h in Methods/Figure 1 caption and 72 h in Results text; CI analysis is 72 h.",
            "No erratum or author explanation was located during this review; CI result remains attributable to its explicit 72-h figure caption.",
            ref + "; AJCR full-text PDF, MTT Methods, Results and Figures 1 and 5.", "NEEDS_MANUAL_REVIEW",
            "The source contains conflicting MTT timing statements; no unsupported selection was made. The distinct 72-h CI endpoint is explicitly documented.",
            ref + "; PMID 26396928, source locators in SB-0182.", "Author/source clarification or expert adjudication if MTT timing is needed for reuse."),
        append_warning("V19-W10", "BROKEN_PUBMED_METADATA_CACHE_LOCATOR",
            "The metadata Source/Source_Cache paths for PMID 24276478 and PMID 26396928 pointed to absent legacy release locations in V19, even though the matching PubMed MED JSON snapshots exist under history/rebuild_artifacts. This broke local metadata provenance locators for SB-0138/0139 and SB-0182/0183.",
            "SB-0138 | SB-0139 | SB-0182 | SB-0183 | bibliography PMIDs 24276478 and 26396928", "provenance locator / local metadata integrity",
            "Evidence and source-audit rows referenced non-existent prior-release cache paths; bibliography Source fields also referenced non-existent sources/ paths.",
            "Updated the bibliography Source and evidence/source-audit Source_Cache paths to the matching archived MED JSON files; validated each file's PMID and preserved the original snapshots unchanged.",
            "Resolved; all four evidence rows, source-audit rows and bibliography rows now point to present JSON files containing the corresponding PMID.",
            "These local JSON files contain bibliographic metadata, not article full text; full-text review is separately documented.",
            ref + "; history/rebuild_artifacts/56800bfd89cb785cadf533fc8887c7a4f29bc1b233333f1ad2c10102b6720893_pmid_24276478.json; history/rebuild_artifacts/306d5b6e6fb6056adf5a6a03f3d32e5d7e48dfd1c6dfe73c63cfb76522f43506_pmid_26396928.json.", "RESOLVED",
            "Both archived JSON files were present and their PMID values were checked; all affected local metadata pointers were updated and will be asserted by the Batch 004 validator.",
            ref + "; validated archived PubMed MED JSON metadata snapshots.", "None for the repaired locator; the cache remains bibliographic metadata only."),
    ]

    fields, warnings, bom = read_csv("data/warning_ledger.csv")
    existing_warning_ids = {row["Warning_ID"] for row in warnings}
    if existing_warning_ids & {row["Warning_ID"] for row in new_warnings}:
        raise ValueError("Batch 004 warning IDs already exist; refusing duplicate insertion")
    warnings.extend(new_warnings)
    write_csv("data/warning_ledger.csv", fields, warnings, bom)

    audit_fields, warning_audit, audit_bom = read_csv("validation/V19_warning_audit.csv")
    warning_audit.extend({
        "Warning_ID": row["Warning_ID"], "V18_Status": "NEW_IN_V19",
        "V19_Status": row["Audit_Status"], "V19_Recheck_Status": "NEW_WARNING_IN_BATCH_004",
        "V19_Review_Work": row["Action"], "V19_Evidence_or_Rationale": row["Audit_Rationale"],
        "Remaining_Limitations": row["Remaining_Limitations"],
    } for row in new_warnings)
    write_csv("validation/V19_warning_audit.csv", audit_fields, warning_audit, audit_bom)

    metadata_path = ROOT / "release_metadata.json"
    meta = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    meta["readiness"] = meta["release_status"] = "SCIENTIFIC_REMEDIATION_IN_PROGRESS"
    review_meta = meta["v19_primary_source_review"]
    review_meta.update({
        "batches_completed": ["V19-001", "V19-002", "V19-003", "V19-004"],
        "evidence_records_reviewed": 22, "tier_1_primary_full_text_records": 22,
        "records_corrected_or_reconstructed": 20, "source_review_remaining": 295,
        "warning_rows_preserved": len(warnings),
        "warning_status_counts": {status: sum(row.get("Audit_Status") == status for row in warnings) for status in ["RESOLVED", "PARTIALLY_RESOLVED", "STILL_VALID", "NEEDS_MANUAL_REVIEW", "NOT_APPLICABLE"]},
        "new_warning_count": len(warnings) - 70,
        "warning_ids_added": ["V19-W01", "V19-W02", "V19-W03", "V19-W04", "V19-W05", "V19-W06", "V19-W07", "V19-W08", "V19-W09", "V19-W10"],
        "warning_rows_individually_reviewed_in_v19": 12,
    })
    meta["warning_count"] = len(warnings)
    outcome_meta = meta["v19_quantitative_outcome_audit"]
    outcome_meta.update({
        "quantitative_values_recovered": 14,
        "qualitative_outcomes_dispositioned": 5,
        "blank_fields_remaining": 71,
        "source_review_batch": "V19-004",
    })
    meta["v19_validation"].update({
        "batch03_integrity": "PENDING_REVALIDATION_AFTER_BATCH_004",
        "batch04_integrity": "PENDING_VALIDATION",
        "batch04_tests_passed": 0, "batch04_tests_failed": 0,
        "full_stageB_regression": "PENDING_FINAL_VALIDATION",
        "v19_exact_manifest": "PENDING_FINAL_PACKAGING",
        "v19_clean_copy_manifest": "PENDING_FINAL_PACKAGING",
    })
    metadata_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "batch": "V19-004", "records_updated": len(BATCH4), "new_warnings": [row["Warning_ID"] for row in new_warnings],
        "new_warning_statuses": {row["Warning_ID"]: row["Audit_Status"] for row in new_warnings},
        "quantitative_outcomes_recovered": 2, "qualitative_outcomes_dispositioned": 2,
        "remaining_blank_outcomes": 71, "status": "APPLIED_PENDING_VALIDATION",
    }


if __name__ == "__main__":
    print(json.dumps(apply(), indent=2, ensure_ascii=False))
