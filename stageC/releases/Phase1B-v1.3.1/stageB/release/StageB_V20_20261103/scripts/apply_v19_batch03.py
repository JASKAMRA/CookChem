"""Apply V19-003 full-text re-extractions for seven inherited blank outcomes."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.apply_v19_batch02 import DATE, ROOT, read_csv, update_rows, write_csv

CACHE = "source_archive/8ef165a5494528bddeeff5990461fc72e52601f9d6e50b7e183b7bba16b2a307_pubmed_esummary_all_v10pmids.json"
SOURCES = {
    "26360766": {
        "doi": "10.1371/journal.pone.0137751",
        "title": "Synergistic Effect of Oleanolic Acid on Aminoglycoside Antibiotics against Acinetobacter baumannii.",
        "url": "https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0137751",
        "access": "Primary PLOS full text and PMC full-text rendering reviewed online; local source archive contains PubMed bibliographic metadata only.",
    },
    "26884726": {
        "doi": "10.1186/s12935-016-0288-3",
        "title": "Paclitaxel and the dietary flavonoid fisetin: a synergistic combination that induces mitotic catastrophe and autophagic cell death in A549 non-small cell lung cancer cells.",
        "url": "https://link.springer.com/article/10.1186/s12935-016-0288-3",
        "access": "Open-access Springer Nature full text and Additional file 1 (Figure S1) reviewed online; local source archive contains PubMed bibliographic metadata only.",
    },
}

RECORDS = {
    "SB-0165": {
        "pmid": "26360766", "drug": "Gentamicin",
        "locator": "PLOS/PMC full text: Materials and Methods—Measurement of fractional inhibitory concentrations; Results—Evaluation of synergistic effects; Table 1; S1 Fig.",
        "dose": "Checkerboard ranges: oleanolic acid 4–256 μg/mL and gentamicin 0.01–2 μg/mL; A. baumannii ATCC17978 inoculum 10^6 CFU/mL, 200 μL/well, 37°C for 24 h. Separate time-kill comparison used gentamicin 0.13 μg/mL plus oleanolic acid 64 μg/mL versus gentamicin 0.25 μg/mL alone.",
        "population": "In vitro A. baumannii ATCC17978 strain; checkerboard replicate count not stated in the reviewed article.",
        "design": "Controlled in-vitro broth microdilution checkerboard FIC/FICI assay; separate gentamicin/oleanolic-acid time-kill assay.",
        "effect": "Oleanolic acid and gentamicin were classified as synergistic against A. baumannii ATCC17978; table and prose disagree on the FICI value/bound (V19-W05).",
        "outcome": "Table 1 (A. baumannii ATCC17978): gentamicin MIC 2.00 μg/mL alone vs 0.50 μg/mL in combination with oleanolic acid 32 μg/mL; gentamicin FIC 0.250 and oleanolic-acid FIC 0.063; table reports FICI <0.313 and synergy. Results prose instead assigns gentamicin FICI 0.375. Preserve this table/prose mismatch under V19-W05. Separate time-kill text reports greater bactericidal effect with gentamicin 0.13 μg/mL + oleanolic acid 64 μg/mL than gentamicin 0.25 μg/mL alone; no effect size is reported.",
        "limitations": "Single bacterial strain in vitro; no human, clinical antibiotic regimen, or ordinary-food exposure equivalence. Exact checkerboard replicate count is not stated. Table 1 gives an upper-bound FICI that conflicts with the prose value; both remain visible under V19-W05.",
        "notes": "Oleanolic acid was purchased from Wako, dissolved in ethanol as a 5 mg/mL stock, and stored at 4°C; purity/lot is not specified. The table reports an upper bound because the oleanolic-acid MIC alone was >512 μg/mL. No clinical use inference is made.",
        "direction": "In-vitro synergy detected in A. baumannii ATCC17978 under the tested checkerboard/time-kill conditions.",
        "claims": "Methods report checkerboard concentration ranges and FICI criteria. Table 1 reports gentamicin MIC/FIC values, FICI <0.313 and synergy; Results prose assigns 0.375 to gentamicin. S1 Fig and Results support the qualitative time-kill comparison.",
        "remaining": "V19-W05: Table 1 reports gentamicin FICI <0.313 while prose reports 0.375; exact replicate count is not given, and the findings are strain- and in-vitro-specific.",
        "verified": "Oleanolic acid/gentamicin identity as named by source; strain; checkerboard methods and ranges; MIC/FIC/FICI; source table/prose conflict; separate time-kill concentrations and qualitative direction.",
        "disposition": "V19_TIER_1_FULL_TEXT_REVIEWED; QUANTITATIVE_OUTCOME_RECOVERED; FICI_REPORTING_CONFLICT_OPEN",
    },
    "SB-0166": {
        "pmid": "26360766", "drug": "Kanamycin",
        "locator": "PLOS/PMC full text: Materials and Methods—Measurement of fractional inhibitory concentrations; Results—Evaluation of synergistic effects; Table 1.",
        "dose": "Checkerboard ranges: oleanolic acid 4–256 μg/mL and kanamycin 0.06–16 μg/mL; A. baumannii ATCC17978 inoculum 10^6 CFU/mL, 200 μL/well, 37°C for 24 h.",
        "population": "In vitro A. baumannii ATCC17978 strain; checkerboard replicate count not stated in the reviewed article.",
        "design": "Controlled in-vitro broth microdilution checkerboard FIC/FICI assay.",
        "effect": "Oleanolic acid and kanamycin were classified as synergistic against A. baumannii ATCC17978; table and prose disagree on the FICI value/bound (V19-W05).",
        "outcome": "Table 1 (A. baumannii ATCC17978): kanamycin MIC 16.00 μg/mL alone vs 4.00 μg/mL in combination with oleanolic acid 64 μg/mL; kanamycin FIC 0.250 and oleanolic-acid FIC 0.125; table reports FICI <0.375 and synergy. Results prose instead assigns kanamycin FICI 0.313. Preserve this table/prose mismatch under V19-W05.",
        "limitations": "Single bacterial strain in vitro; no human, clinical antibiotic regimen, or ordinary-food exposure equivalence. Exact checkerboard replicate count is not stated. Table 1 gives an upper-bound FICI that conflicts with the prose value; both remain visible under V19-W05.",
        "notes": "Oleanolic acid was purchased from Wako, dissolved in ethanol as a 5 mg/mL stock, and stored at 4°C; purity/lot is not specified. The table reports an upper bound because the oleanolic-acid MIC alone was >512 μg/mL. No clinical use inference is made.",
        "direction": "In-vitro synergy detected in A. baumannii ATCC17978 under the tested checkerboard conditions.",
        "claims": "Methods report checkerboard concentration ranges and FICI criteria. Table 1 reports kanamycin MIC/FIC values and FICI <0.375; Results prose assigns 0.313 to kanamycin. Both classify the combination as synergistic.",
        "remaining": "V19-W05: Table 1 reports kanamycin FICI <0.375 while prose reports 0.313; exact replicate count is not given, and findings are strain- and in-vitro-specific.",
        "verified": "Oleanolic acid/kanamycin identity as named by source; strain; checkerboard methods and ranges; MIC/FIC/FICI; source table/prose conflict.",
        "disposition": "V19_TIER_1_FULL_TEXT_REVIEWED; QUANTITATIVE_OUTCOME_RECOVERED; FICI_REPORTING_CONFLICT_OPEN",
    },
    "SB-0167": {
        "pmid": "26360766", "drug": "Ampicillin",
        "locator": "PLOS/PMC full text: Materials and Methods—Measurement of fractional inhibitory concentrations; Results—Evaluation of synergistic effects; Table 1.",
        "dose": "Checkerboard ranges: oleanolic acid 4–256 μg/mL and ampicillin 2–512 μg/mL; A. baumannii ATCC17978 inoculum 10^6 CFU/mL, 200 μL/well, 37°C for 24 h.",
        "population": "In vitro A. baumannii ATCC17978 strain; checkerboard replicate count not stated in the reviewed article.",
        "design": "Controlled in-vitro broth microdilution checkerboard FIC/FICI assay.",
        "effect": "The source labels the oleanolic-acid/ampicillin pair as no interaction, but its FICI upper bound does not establish which side of the stated synergy cutoff the exact value falls on (V19-W06).",
        "outcome": "Table 1 (A. baumannii ATCC17978): ampicillin MIC 512.00 μg/mL alone vs 128.00 μg/mL with oleanolic acid 256 μg/mL; ampicillin FIC 0.250, oleanolic-acid FIC 0.500, reported FICI <0.750; source classifies the pair as no interaction. The less-than sign is retained; the exact FICI is not stated.",
        "limitations": "Single bacterial strain in vitro; no human, clinical antibiotic regimen, or ordinary-food exposure equivalence. Exact checkerboard replicate count is not stated; reported FICI is an upper bound rather than an exact value.",
        "notes": "Oleanolic acid was purchased from Wako and tested from an ethanol stock; source does not report purity/lot. A checkerboard no-interaction classification is specific to this strain and assay.",
        "direction": "Source-reported no-interaction classification; the FICI upper bound does not independently establish the cutoff category (V19-W06).",
        "claims": "Table 1 supports the ampicillin MIC values, combination concentration, FIC components, reported FICI <0.750, and no-interaction classification.",
        "remaining": "The exact FICI is not available beyond the table's upper bound, which does not resolve whether the FICI is above or at/below the article's 0.5 synergy cutoff (V19-W06); no broader bacterial or clinical inference is warranted.",
        "verified": "Strain; checkerboard methods/range; ampicillin MIC, combination concentration, FIC, upper-bound FICI, and source classification.",
        "disposition": "V19_TIER_1_FULL_TEXT_REVIEWED; QUANTITATIVE_OUTCOME_RECOVERED",
    },
    "SB-0168": {
        "pmid": "26360766", "drug": "Norfloxacin",
        "locator": "PLOS/PMC full text: Materials and Methods—Measurement of fractional inhibitory concentrations; Results—Evaluation of synergistic effects; Table 1.",
        "dose": "Checkerboard ranges: oleanolic acid 4–256 μg/mL and norfloxacin 0.03–8 μg/mL; A. baumannii ATCC17978 inoculum 10^6 CFU/mL, 200 μL/well, 37°C for 24 h.",
        "population": "In vitro A. baumannii ATCC17978 strain; checkerboard replicate count not stated in the reviewed article.",
        "design": "Controlled in-vitro broth microdilution checkerboard FIC/FICI assay.",
        "effect": "The source labels the oleanolic-acid/norfloxacin pair as no interaction, but its FICI upper bound does not establish which side of the stated synergy cutoff the exact value falls on (V19-W06).",
        "outcome": "Table 1 (A. baumannii ATCC17978): norfloxacin MIC 8.00 μg/mL alone vs 1.00 μg/mL with oleanolic acid 256 μg/mL; norfloxacin FIC 0.125, oleanolic-acid FIC 0.500, reported FICI <0.625; source classifies the pair as no interaction. The less-than sign is retained; the exact FICI is not stated.",
        "limitations": "Single bacterial strain in vitro; no human, clinical antibiotic regimen, or ordinary-food exposure equivalence. Exact checkerboard replicate count is not stated; reported FICI is an upper bound rather than an exact value.",
        "notes": "Oleanolic acid was purchased from Wako and tested from an ethanol stock; source does not report purity/lot. A checkerboard no-interaction classification is specific to this strain and assay.",
        "direction": "Source-reported no-interaction classification; the FICI upper bound does not independently establish the cutoff category (V19-W06).",
        "claims": "Table 1 supports the norfloxacin MIC values, combination concentration, FIC components, reported FICI <0.625, and no-interaction classification.",
        "remaining": "The exact FICI is not available beyond the table's upper bound, which does not resolve whether the FICI is above or at/below the article's 0.5 synergy cutoff (V19-W06); no broader bacterial or clinical inference is warranted.",
        "verified": "Strain; checkerboard methods/range; norfloxacin MIC, combination concentration, FIC, upper-bound FICI, and source classification.",
        "disposition": "V19_TIER_1_FULL_TEXT_REVIEWED; QUANTITATIVE_OUTCOME_RECOVERED",
    },
    "SB-0107": {
        "pmid": "26884726", "drug": "Arsenic trioxide",
        "locator": "Springer Nature full text: Materials and Methods—Cell treatment/MTT assay; Results—preliminary fisetin combination experiments; Additional file 1, Figure S1(c).",
        "dose": "Exact fisetin and arsenic-trioxide concentrations for the preliminary combination experiment are not reported in the article or Additional file 1; the Methods concentration range is for the main fisetin–paclitaxel experiment and is not attributed to this pair.",
        "population": "A549 human non-small-cell lung cancer cell line; preliminary in-vitro combination experiment.",
        "design": "In-vitro cell-viability/combination-index analysis; the combination is shown in Additional file 1, Figure S1(c).",
        "effect": "The authors report that fisetin synergized with arsenic trioxide in A549 cells; this is a preclinical cell-line finding.",
        "outcome": "Qualitative outcome only: authors report synergy for fisetin plus arsenic trioxide in A549 cells and show a combination-index plot in Additional file 1, Figure S1(c). Exact CI values at the experimental points and the pair-specific concentrations are not tabulated in the article/supplement; no values have been estimated from the graph.",
        "limitations": "In-vitro A549-cell result only. Pair-specific doses and exact CI values are not reported in text/table; graph points were not digitized. No human treatment or food-exposure inference is supported.",
        "notes": "The paper identifies fisetin reagent from Sigma-Aldrich. Its main fisetin–paclitaxel regimen is not transferred to this separate preliminary combination.",
        "direction": "Synergy reported for this cell-line combination only; no clinical effect established.",
        "claims": "Full-text abstract/results state synergy with arsenic trioxide in A549; Additional file 1 Figure S1(c) displays CI versus fractional inhibition. Exact numeric CI and pair dose are not reported.",
        "remaining": "Pair-specific dose and numerical CI remain unavailable in article/supplement; the source's cell-line result cannot establish patient or dietary exposure effects.",
        "verified": "Tested reagent identity as named; cell model; source qualitative synergy statement; supplementary figure and absence of tabulated pair-specific CI/dose.",
        "disposition": "V19_TIER_1_FULL_TEXT_REVIEWED; QUALITATIVE_OUTCOME_ONLY; DOSE_AND_NUMERIC_CI_NOT_REPORTED",
    },
    "SB-0108": {
        "pmid": "26884726", "drug": "Mitoxantrone",
        "locator": "Springer Nature full text: Materials and Methods—Cell treatment/MTT assay; Results—preliminary fisetin combination experiments; Additional file 1, Figure S1(a).",
        "dose": "Exact fisetin and mitoxantrone concentrations for the preliminary combination experiment are not reported in the article or Additional file 1; the Methods concentration range is for the main fisetin–paclitaxel experiment and is not attributed to this pair.",
        "population": "A549 human non-small-cell lung cancer cell line; preliminary in-vitro combination experiment.",
        "design": "In-vitro cell-viability/combination-index analysis; the combination is shown in Additional file 1, Figure S1(a).",
        "effect": "The authors report that fisetin did not synergize with mitoxantrone in A549 cells; this is not a general no-interaction finding.",
        "outcome": "Qualitative outcome only: authors report no synergy for fisetin plus mitoxantrone in A549 cells and show a log(CI) plot in Additional file 1, Figure S1(a). Exact CI values at experimental points and pair-specific concentrations are not tabulated in the article/supplement; no values have been estimated from the graph.",
        "limitations": "In-vitro A549-cell result only. No-synergy under the tested conditions is not equivalent to no pharmacological interaction. Pair-specific doses and exact CI values are not reported; no human or food-exposure inference is supported.",
        "notes": "The paper identifies fisetin reagent from Sigma-Aldrich. Its main fisetin–paclitaxel regimen is not transferred to this separate preliminary combination.",
        "direction": "No synergy reported for this cell-line combination only; no broader interaction conclusion is assigned.",
        "claims": "Full-text abstract/results state no synergy with mitoxantrone in A549; Additional file 1 Figure S1(a) displays log(CI) versus fractional inhibition. Exact numeric CI and pair dose are not reported.",
        "remaining": "Pair-specific dose and numerical CI remain unavailable in article/supplement; source is limited to a cell-line result.",
        "verified": "Tested reagent identity as named; cell model; source qualitative result; supplementary figure and absence of tabulated pair-specific CI/dose.",
        "disposition": "V19_TIER_1_FULL_TEXT_REVIEWED; QUALITATIVE_OUTCOME_ONLY; DOSE_AND_NUMERIC_CI_NOT_REPORTED",
    },
    "SB-0109": {
        "pmid": "26884726", "drug": "Methotrexate",
        "locator": "Springer Nature full text: Materials and Methods—Cell treatment/MTT assay; Results—preliminary fisetin combination experiments; Additional file 1, Figure S1(b).",
        "dose": "Exact fisetin and methotrexate concentrations for the preliminary combination experiment are not reported in the article or Additional file 1; the Methods concentration range is for the main fisetin–paclitaxel experiment and is not attributed to this pair.",
        "population": "A549 human non-small-cell lung cancer cell line; preliminary in-vitro combination experiment.",
        "design": "In-vitro cell-viability/combination-index analysis; the combination is shown in Additional file 1, Figure S1(b).",
        "effect": "The authors report that fisetin did not synergize with methotrexate in A549 cells; this is not a general no-interaction finding.",
        "outcome": "Qualitative outcome only: authors report no synergy for fisetin plus methotrexate in A549 cells and show a log(CI) plot in Additional file 1, Figure S1(b). Exact CI values at experimental points and pair-specific concentrations are not tabulated in the article/supplement; no values have been estimated from the graph.",
        "limitations": "In-vitro A549-cell result only. No-synergy under the tested conditions is not equivalent to no pharmacological interaction. Pair-specific doses and exact CI values are not reported; no human or food-exposure inference is supported.",
        "notes": "The paper identifies fisetin reagent from Sigma-Aldrich. Its main fisetin–paclitaxel regimen is not transferred to this separate preliminary combination.",
        "direction": "No synergy reported for this cell-line combination only; no broader interaction conclusion is assigned.",
        "claims": "Full-text abstract/results state no synergy with methotrexate in A549; Additional file 1 Figure S1(b) displays log(CI) versus fractional inhibition. Exact numeric CI and pair dose are not reported.",
        "remaining": "Pair-specific dose and numerical CI remain unavailable in article/supplement; source is limited to a cell-line result.",
        "verified": "Tested reagent identity as named; cell model; source qualitative result; supplementary figure and absence of tabulated pair-specific CI/dose.",
        "disposition": "V19_TIER_1_FULL_TEXT_REVIEWED; QUALITATIVE_OUTCOME_ONLY; DOSE_AND_NUMERIC_CI_NOT_REPORTED",
    },
}


def apply() -> dict[str, object]:
    if not (ROOT / "release_metadata.json").is_file():
        raise SystemExit(f"Not a V19 release tree: {ROOT}")
    evidence_updates = {}
    audit_updates = {}
    claim_updates = {}
    for evidence_id, spec in RECORDS.items():
        source = SOURCES[spec["pmid"]]
        level = "compound"
        evidence_updates[evidence_id] = {
            "Interaction_Effect": spec["effect"], "Evidence_Level": level,
            "Direction": spec["direction"], "Quantitative_Outcome": spec["outcome"],
            "Dose": spec["dose"], "Population": spec["population"], "Study_Design": spec["design"],
            "Source_URL": source["url"], "Source_Cache": "provenance/" + CACHE,
            "Source_Locator": spec["locator"], "Preparation": spec["dose"],
            "Identity_Status": ("Oleanolic acid reagent named in the source (Wako); source does not report lot or purity." if spec["pmid"] == "26360766" else "Fisetin reagent named in the source (Sigma-Aldrich); source does not report lot or purity."),
            "Limitations": spec["limitations"], "Notes": spec["notes"],
            "Outcome": "source_reporting_discrepancy_pending_adjudication" if evidence_id in {"SB-0165", "SB-0166"} else ("source_reported_no_interaction_threshold_uncertain" if evidence_id in {"SB-0167", "SB-0168"} else ("synergy observed in vitro" if evidence_id == "SB-0107" else ("no synergy detected in vitro" if evidence_id in {"SB-0108", "SB-0109"} else "qualitative_outcome_only"))),
        }
        audit_updates[evidence_id] = {
            "PMID": spec["pmid"], "DOI": source["doi"], "Source_Title": source["title"],
            "Source_URL": source["url"], "Source_Cache": CACHE, "Source_Locator": spec["locator"],
            "Verification_Status": "Tier 1: primary full text and relevant methods/results/table or supplementary figure directly reviewed in V19-003",
            "Fields_Audited": "tested compound/form; comparator; dose or explicit source omission; study model/design; endpoints; reported numerical values and bounds or qualitative-only result; source limitations and discrepancies",
            "Limitations": spec["limitations"], "Source_Type": "Primary research", "Verification_Date": DATE,
            "Verification_Method": source["access"] + " Record-specific extractions and remaining limitations are in validation/V19_batch_003_review.csv.",
            "Verification_Level": "1", "Audit_Disposition": spec["disposition"],
            "Reviewer": "Codex AI-assisted primary-source curation; expert adjudication remains open for V19-W05",
            "Endpoint_Verified": spec["verified"], "Numerical_Outcome_Verified": spec["claims"],
            "Study_ID": "PMID:" + spec["pmid"], "Compound_ID": "CHEM-PUBCHEM-10494" if spec["pmid"] == "26360766" else "CHEM-PUBCHEM-5281614",
            "Drug_Probe": spec["drug"],
            "V18_Unresolved_Discrepancy": "V18 carried forward this record without a V19 source-content review. V19-003 directly reviewed the primary full text; " + spec["remaining"],
            "Disposition_Date": DATE,
        }
        claim_updates[evidence_id] = {
            "Source_Locator": spec["locator"],
            "Verification_Status": "V19 Tier 1 primary full-text review completed in V19-003; see batch-level review.",
            "Numerical_Use": spec["claims"], "Limitations": spec["limitations"],
        }
    update_rows("data/interaction_evidence.csv", "Evidence_ID", evidence_updates)
    update_rows("provenance/source_audit.csv", "Evidence_ID", audit_updates)
    update_rows("provenance/claim_support_and_verification.csv", "Evidence_ID", claim_updates)

    fields, rows, bom = read_csv("data/warning_ledger.csv")
    if any(row["Warning_ID"] == "V19-W05" for row in rows):
        raise ValueError("V19-W05 already exists; refusing duplicate warning insertion")
    reference = "Primary PLOS/PMC full text, Table 1 and Results for PMID 26360766; V19_batch_003_review.csv."
    rows.append({
        "Warning_ID": "V19-W05", "Code": "FICI_PROSE_TABLE_VALUE_PAIRING_DISCREPANCY",
        "Description": "For SB-0165 and SB-0166 (PMID 26360766), Results prose assigns FICI values 0.375 to gentamicin and 0.313 to kanamycin, while Table 1 reports gentamicin <0.313 and kanamycin <0.375. Both components remain classed as synergy, but the pair-specific values/bounds conflict and must not be silently swapped or normalized.",
        "Affected": "SB-0165 | SB-0166 | PMID:26360766 | Table 1 FICI reporting",
        "Classification": "scientific source discrepancy / numerical outcome",
        "Before": "Inherited blank outcomes; source-level FICI detail had not been re-extracted in V19.",
        "Action": "Reviewed the publisher/PMC primary full text, Methods, Results and Table 1; transcribed each table bound and the conflicting prose assignment separately. Preserved both without selecting one as correct.",
        "After": "Open; synergy classification is consistent, but exact pair-specific FICI reporting remains discordant.",
        "Remaining_Limitations": "No source explanation is provided for the swapped prose values versus table upper bounds. Expert/source adjudication is required before assigning a single pair-specific FICI value.",
        "Resolution_Source": reference, "Review_Date": DATE, "Audit_Status": "NEEDS_MANUAL_REVIEW",
        "Inherited_Severity": "NOT_RECORDED",
        "Audit_Rationale": "The discrepancy is directly present in the primary article. The upper-bound symbols and prose values are retained; no assumption is used to reconcile them.",
        "Audit_Verification_Reference": reference,
        "Audit_Dependencies": "Author/source clarification or expert review of the table calculations and prose assignment.",
        "V17_Ledger_Audit_Status": "NOT_IN_V18",
    })
    rows.append({
        "Warning_ID": "V19-W06", "Code": "FICI_UPPER_BOUND_DOES_NOT_RESOLVE_CLASSIFICATION",
        "Description": "For SB-0167 (ampicillin) and SB-0168 (norfloxacin; PMID 26360766), Table 1 reports FICI upper bounds <0.750 and <0.625 while classifying both as no interaction. Because the article defines synergy as FICI ≤0.5, neither upper bound alone establishes whether the exact value is above or at/below that cutoff. Preserve the source label but do not treat the numeric classification as independently resolved.",
        "Affected": "SB-0167 | SB-0168 | PMID:26360766 | Table 1 FICI bounds",
        "Classification": "scientific source limitation / threshold classification",
        "Before": "Inherited blank outcomes; source-level FICI detail had not been re-extracted in V19.",
        "Action": "Reviewed the primary article's checkerboard methods, stated FICI thresholds, Results and Table 1; recorded each table upper bound and the source's no-interaction label without inferring an exact value.",
        "After": "Open; source classification is preserved, but the upper-bound values do not independently determine whether the FICI exceeds the 0.5 synergy cutoff.",
        "Remaining_Limitations": "The oleanolic-acid MIC alone is reported as >512 μg/mL, preventing an exact FICI from the reported table inputs; source does not provide a lower bound that resolves the classification.",
        "Resolution_Source": "Primary PLOS/PMC full text, Methods—Measurement of fractional inhibitory concentrations and Table 1 for PMID 26360766; V19_batch_003_review.csv.",
        "Review_Date": DATE, "Audit_Status": "NEEDS_MANUAL_REVIEW", "Inherited_Severity": "NOT_RECORDED",
        "Audit_Rationale": "The source reports an upper bound and a categorical label, but the reported bound straddles the study's cutoff. The label is retained as source-reported and not strengthened into an independent numerical conclusion.",
        "Audit_Verification_Reference": "Primary PLOS/PMC full text, Methods and Table 1, PMID 26360766; V19_batch_003_review.csv.",
        "Audit_Dependencies": "Author/source clarification or exact oleanolic-acid-alone MIC sufficient to evaluate the FICI category.",
        "V17_Ledger_Audit_Status": "NOT_IN_V18",
    })
    write_csv("data/warning_ledger.csv", fields, rows, bom)

    fields, rows, bom = read_csv("validation/V19_warning_audit.csv")
    if any(row["Warning_ID"] == "V19-W05" for row in rows):
        raise ValueError("V19-W05 already exists in the warning audit")
    rows.append({
        "Warning_ID": "V19-W05", "V18_Status": "NEW_IN_V19", "V19_Status": "NEEDS_MANUAL_REVIEW",
        "V19_Recheck_Status": "NEW_WARNING_IN_BATCH_003",
        "V19_Review_Work": "Reviewed primary PLOS/PMC full text, checkerboard methods, Results and Table 1 for SB-0165 and SB-0166.",
        "V19_Evidence_or_Rationale": "Results prose gives gentamicin 0.375 and kanamycin 0.313; Table 1 gives gentamicin <0.313 and kanamycin <0.375. Both are labeled synergy; exact pair-level values/bounds conflict.",
        "Remaining_Limitations": "No source explanation for the prose/table mismatch; retain both until author/source clarification or expert adjudication.",
    })
    rows.append({
        "Warning_ID": "V19-W06", "V18_Status": "NEW_IN_V19", "V19_Status": "NEEDS_MANUAL_REVIEW",
        "V19_Recheck_Status": "NEW_WARNING_IN_BATCH_003",
        "V19_Review_Work": "Reviewed primary PLOS/PMC checkerboard methods, FICI definition, Results and Table 1 for SB-0167 and SB-0168.",
        "V19_Evidence_or_Rationale": "Source cutoff defines synergy at FICI ≤0.5. Ampicillin and norfloxacin rows give only <0.750 and <0.625 and are labeled no interaction; upper bounds do not establish that exact FICIs exceed 0.5.",
        "Remaining_Limitations": "Exact OA-alone MIC beyond >512 μg/mL and exact FICIs are unavailable; source/author clarification or expert adjudication is required.",
    })
    write_csv("validation/V19_warning_audit.csv", fields, rows, bom)

    fields = ["Batch", "Evidence_ID", "Compound_ID", "Compound", "Drug_Probe", "Study_ID", "PMID", "DOI", "Primary_Source_URL", "Source_Access_Status", "Local_Metadata_Cache", "Source_Locator", "Verification_Tier", "Review_Date", "Correction_Made", "Verified_Outcome", "Remaining_Limitation"]
    evidence = {row["Evidence_ID"]: row for row in read_csv("data/interaction_evidence.csv")[1]}
    review = []
    for evidence_id, spec in RECORDS.items():
        row = evidence[evidence_id]
        source = SOURCES[spec["pmid"]]
        correction = "Recovered primary-source evidence and replaced abstract-only audit disposition; "
        if evidence_id in {"SB-0165", "SB-0166"}:
            correction += "recorded table values and prose/table discrepancy V19-W05 without choosing a preferred FICI."
        elif evidence_id in {"SB-0167", "SB-0168"}:
            correction += "recorded table MIC/FIC upper bounds and preserved the source no-interaction label with open threshold-classification warning V19-W06."
        else:
            correction += "reclassified Evidence_Level from formulation to compound and recorded qualitative-only outcome, unreported pair-specific dose/CI, and no graph-derived estimates."
        review.append({
            "Batch": "V19-003", "Evidence_ID": evidence_id, "Compound_ID": row["Compound_ID"], "Compound": row["Compound"],
            "Drug_Probe": row["Drug"], "Study_ID": row["Study_ID"], "PMID": spec["pmid"], "DOI": source["doi"],
            "Primary_Source_URL": source["url"], "Source_Access_Status": source["access"],
            "Local_Metadata_Cache": "provenance/" + CACHE, "Source_Locator": spec["locator"],
            "Verification_Tier": "1", "Review_Date": DATE, "Correction_Made": correction,
            "Verified_Outcome": spec["outcome"], "Remaining_Limitation": spec["remaining"],
        })
    with (ROOT / "validation/V19_batch_003_review.csv").open("w", encoding="utf-8", newline="") as handle:
        import csv
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(review)

    update_rows("data/study_registry.csv", "Study_ID", {
        "PMID:26360766": {"Verification_Status": "V19-003: PLOS/PMC primary full text; Methods, Results and Table 1 reviewed for SB-0165–SB-0168, including FICI prose/table discrepancy and strain-specific outcomes."},
        "PMID:26884726": {"Verification_Status": "V19-003: Springer Nature open-access full text and Additional file 1 Figure S1 reviewed for SB-0107–SB-0109; qualitative outcomes verified, exact doses/CI values not reported for these preliminary combinations."},
    })

    metadata_path = ROOT / "release_metadata.json"
    meta = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    meta["readiness"] = meta["release_status"] = "SCIENTIFIC_REMEDIATION_IN_PROGRESS"
    meta["warning_count"] = 76
    review_meta = meta["v19_primary_source_review"]
    review_meta.update({
        "batches_completed": ["V19-001", "V19-002", "V19-003"],
        "evidence_records_reviewed": 18, "tier_1_primary_full_text_records": 18,
        "records_corrected_or_reconstructed": 16, "source_review_remaining": 299,
        "warning_rows_preserved": 76,
        "warning_status_counts": {"RESOLVED": 3, "PARTIALLY_RESOLVED": 15, "STILL_VALID": 26, "NEEDS_MANUAL_REVIEW": 30, "NOT_APPLICABLE": 2},
        "new_warning_count": 6,
        "warning_ids_added": ["V19-W01", "V19-W02", "V19-W03", "V19-W04", "V19-W05", "V19-W06"],
        "warning_rows_individually_reviewed_in_v19": 8,
    })
    meta["v19_quantitative_outcome_audit"] = {
        "original_blank_fields": 90, "quantitative_values_recovered": 12,
        "qualitative_outcomes_dispositioned": 3, "blank_fields_remaining": 75,
        "source_review_batch": "V19-003",
    }
    meta["v19_validation"].update({
        "batch02_integrity": "PASS_PENDING_FINAL_MANIFEST", "batch03_integrity": "PENDING_VALIDATION",
        "batch03_tests_passed": 0, "batch03_tests_failed": 0,
        "full_stageB_regression": "PENDING_FINAL_VALIDATION",
        "v19_exact_manifest": "PENDING_FINAL_PACKAGING", "v19_clean_copy_manifest": "PENDING_FINAL_PACKAGING",
    })
    metadata_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"batch": "V19-003", "records_updated": len(RECORDS), "quantitative_values_recovered": 4, "qualitative_outcomes_dispositioned": 3, "new_warnings": 2, "status": "APPLIED_PENDING_VALIDATION"}


if __name__ == "__main__":
    print(json.dumps(apply(), indent=2, ensure_ascii=False))
