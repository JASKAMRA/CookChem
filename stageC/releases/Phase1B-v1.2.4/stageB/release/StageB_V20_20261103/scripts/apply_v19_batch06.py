"""Apply V19-006 primary-source re-extractions for four blank outcome records."""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.apply_v19_batch02 import DATE, ROOT, read_csv, update_rows, write_csv

UA_PMID = "27472952"
UA_DOI = "10.1007/s13238-016-0295-0"
UA_TITLE = "Ursolic acid synergistically enhances the therapeutic effects of oxaliplatin in colorectal cancer."
UA_URL = "https://pmc.ncbi.nlm.nih.gov/articles/PMC4980335/"
UA_CACHE = "history/rebuild_artifacts/b478b7288bba8a68c28e9731c805f0784d57fc975d4fd6a5e0f5f276260f037b_pmid_27472952.json"
UA_XML_NAME = "8b2c4c41d05937901a522d5b8c9a758798aa825013204cf85a4a8775de94c06e_PMC4980335.xml"
UA_XML_SHA256 = "8b2c4c41d05937901a522d5b8c9a758798aa825013204cf85a4a8775de94c06e"

F_PMID = "27765854"
F_DOI = "10.1158/1535-7163.MCT-16-0515"
F_TITLE = "Fisetin Enhances Chemotherapeutic Effect of Cabazitaxel against Human Prostate Cancer Cells."
F_URL = "https://pmc.ncbi.nlm.nih.gov/articles/PMC5136329/"
F_CACHE = "history/rebuild_artifacts/43f5cd1be33be51aefb62daa7638bf637a4ff46b4f0b30a3d5ab2aaf6ee1cd6a_pmid_27765854.json"

SOURCES = {
    UA_PMID: (UA_DOI, UA_TITLE, UA_URL, UA_CACHE),
    F_PMID: (F_DOI, F_TITLE, F_URL, F_CACHE),
}

RECORDS = {
    "SB-0110": {
        "pmid": F_PMID, "drug": "Cabazitaxel",
        "locator": "PMC5136329 full text: Materials; Cell Culture and Treatment; Results—cell viability/colony formation; Combination Index method; Table 1; Figure 1; Supplementary Figure S1 is cited in the paper but was not separately retrieved.",
        "effect": "Fisetin (20 μM) plus cabazitaxel (5 nM) reduced viability more than either agent alone in 22Rv1, PC-3M-luc-6 and C4-2 prostate cancer cells; the source-reported combination-index values indicate synergy for the measured combinations. Normal PrEC viability was minimally affected at these tested concentrations.",
        "mechanism": "Cell experiments report reduced proliferation/colony formation and apoptosis-associated marker changes. These preclinical observations do not establish a clinical interaction mechanism.",
        "direction": "Enhanced cell-viability inhibition under the tested in-vitro combination; combination-index classification is source/method specific.",
        "outcome": "At 20 μM fisetin + 5 nM cabazitaxel, reported viability reductions were approximately 79% (22Rv1), 53% (PC-3M-luc-6) and 78% (C4-2), compared with fisetin-alone reductions of 45%, 49% and 74% and cabazitaxel-alone reductions of 32%, 11% and 38%, respectively. Table 1 reports CI 0.45676 for 22Rv1, 0.74663 for a row labelled “PC-3” (the Methods/Results identify PC-3M-luc-6; exact cell-line attribution is unresolved under V19-W13), and 0.72226 for C4-2. Methods define CI<0.9 as synergy, CI=1.1 as additive and CI>1.1 as antagonism; the Results also describe synergy as CI<1 (V19-W12). All three table values are below 0.9. CI values are reported from Table 1, not recalculated.",
        "dose": "Fisetin 20 μM and cabazitaxel 5 nM for the reported cell-viability/CI combination; the Annexin V method describes 48 h fisetin followed by 24 h cabazitaxel. Do not assume that sequence applies to all assays.",
        "population": "Human prostate cancer cell lines 22Rv1, PC-3M-luc-6 and C4-2; normal human prostate epithelial PrEC cells used as a comparison.",
        "design": "Controlled in-vitro cell-viability and colony-formation experiments with a fixed-dose combination and CompuSyn combination-index analysis. The source reports minimal effects on normal PrEC viability at the tested doses.",
        "limitations": "In-vitro only; no human interaction or clinical efficacy established. The main article's Table 1 labels the CI=0.74663 cell line as PC-3, whereas Methods/Results name PC-3M-luc-6 (V19-W13); the CI terminology also uses different thresholds in Methods and Results (V19-W12). Supplementary Figure S1 is cited but was not separately retrieved. Reagent grade, lot and purity are not specified.",
        "preparation": "Fisetin reagent purchased from Sigma; cabazitaxel from LC Laboratory. Both are named reagents; grade, lot and purity are not stated in the reviewed article.",
        "endpoint": "Cell viability, colony formation and combination-index estimate for fisetin plus cabazitaxel; normal PrEC viability as comparator.",
        "numerical": "Primary full text Results and Table 1 directly report the single-agent and combination cell-viability reductions and CI values; the methods specify CompuSyn and the source's CI interpretation. No graph values were digitized.",
        "claims": "Primary PMC full text: Materials; Cell Culture and Treatment; Results—cell viability and colony formation; Table 1 and Figure 1. Combination-index method states CI<0.9 is synergistic; Results text gives CI<1. Table 1's PC-3 row label differs from the stated PC-3M-luc-6 model.",
        "verified": "Cell identities as stated by Methods and Results; fisetin/cabazitaxel concentrations; reported viability reductions; Table 1 CI values; normal PrEC comparison; in-vitro-only scope.",
        "audit_disposition": "V19_TIER_1_FULL_TEXT_REVIEWED; QUANTITATIVE_OUTCOME_RECOVERED; SOURCE_LABEL_DISCREPANCIES_OPEN",
    },
    "SB-0111": {
        "pmid": F_PMID, "drug": "Cabazitaxel",
        "locator": "PMC5136329 full text: In-vivo tumor xenograft study (Methods); Results—22Rv1 xenograft and metastatic PC-3M-luc-6 xenograft sections; Figures 3–6. Methods says treatment began two weeks after implantation; Results says three days for the PC-3M model (V19-W11).",
        "effect": "In two prostate-cancer xenograft mouse models, fisetin plus cabazitaxel inhibited tumor growth more than either single agent under the reported regimens. The PC-3M-luc-6 model also assessed metastatic and angiogenesis-related endpoints.",
        "mechanism": "Tumor marker findings include reduced proliferation/angiogenesis markers and apoptosis-associated changes; the article does not establish a human mechanism or clinical benefit.",
        "direction": "Enhanced preclinical tumor-growth inhibition in the tested xenograft models.",
        "outcome": "Two subcutaneous xenograft models used athymic nude male mice, four treatment groups and n=6/group; fisetin 20 mg/kg i.p. three times/week, cabazitaxel 5 mg/kg i.p. once/week, combination, or vehicle. In the 22Rv1 model, the article reports tumor-growth inhibition of 14% with fisetin, 36% with cabazitaxel and 53% with the combination versus control. In the PC-3M-luc-6 model, after the reported 7-week treatment course, tumor volume increased 9-fold with the combination, 22-fold with fisetin, 20-fold with cabazitaxel and 32-fold with control; combination versus control and single agents p=0.0001 in Results. Body-weight monitoring showed no apparent combination toxicity, but the data were not shown. Methods state treatment began 2 weeks after implantation; Results state 3 days for the PC-3M model (V19-W11).",
        "dose": "Fisetin 20 mg/kg i.p. three times/week; cabazitaxel 5 mg/kg i.p. once/week; combination at the same doses; vehicle control. Source timing conflict for PC-3M model is retained under V19-W11.",
        "population": "Two subcutaneous human prostate cancer xenografts in male athymic nude mice (6–8 weeks): 22Rv1 and metastatic PC-3M-luc-6; 24 mice per model, randomized into four groups of six.",
        "design": "Controlled in-vivo xenograft experiments with vehicle, fisetin, cabazitaxel and combination groups (n=6 each) and tumor-growth follow-up. Methods and Results conflict on treatment-start timing for the PC-3M-luc-6 model; see V19-W11.",
        "limitations": "Animal xenograft results only; no clinical efficacy, human safety or dietary-exposure equivalence established. PC-3M treatment-start timing conflicts between Methods (2 weeks after implantation) and Results (3 days). Body-weight toxicity data are stated to be not shown; plotted tumor measurements were not digitized.",
        "preparation": "Fisetin purchased from Sigma and cabazitaxel from LC Laboratory; intraperitoneal dosing. Article does not report reagent grade, lot or purity.",
        "endpoint": "Tumor growth/volume, tumor proliferation/apoptosis markers, metastasis and angiogenesis-related endpoints; body weight was monitored, but toxicity data were not shown.",
        "numerical": "Primary full text Results directly reports 22Rv1 tumor inhibition percentages and PC-3M-luc-6 fold-growth values and p-value; dose and group sizes are from Methods. Figure images were not digitized.",
        "claims": "Primary PMC full text: In-vivo tumor xenograft study (Methods), Results sections for 22Rv1 and PC-3M-luc-6 xenografts, and Figures 3–6. Timing conflict recorded as V19-W11.",
        "verified": "Two mouse models, sex/strain/age, group allocation, route/doses/frequency, reported tumor-growth outcomes, p-value, endpoints and source timing discrepancy.",
        "audit_disposition": "V19_TIER_1_FULL_TEXT_REVIEWED; QUANTITATIVE_OUTCOME_RECOVERED; ANIMAL_TIMING_DISCREPANCY_OPEN",
    },
    "SB-0163": {
        "pmid": UA_PMID, "drug": "Oxaliplatin",
        "locator": "PMC4980335 full text (archived XML; V19 copy hash 8b2c4c41d05937901a522d5b8c9a758798aa825013204cf85a4a8775de94c06e): Results—synergistic proliferation/apoptosis; Table 1; Figure 2; Materials and Methods—combination analysis.",
        "effect": "Ursolic acid and oxaliplatin synergistically inhibited proliferation across four colorectal-cancer cell lines under the tested fixed-ratio conditions; the combination also enhanced apoptosis in SW620 and RKO cells.",
        "mechanism": "The primary paper associates the cell findings with apoptosis and changes in MAPK, PI3K/AKT and NF-κB signaling markers; these are preclinical mechanistic observations, not established clinical mechanisms.",
        "direction": "Source-reported synergy in cell proliferation assays for all four tested colorectal-cancer cell lines.",
        "outcome": "Cells were exposed to ursolic acid and oxaliplatin alone or in fixed-ratio combinations for 48 h. Table 1 reports combination-index values: SW480 0.51, SW620 0.55, LoVo 0.54 and RKO 0.68; the article defines CI<1 as synergy. In SW620, 10 μmol/L ursolic acid plus 0.4 μmol/L oxaliplatin produced about 30% apoptosis versus <10% with either suboptimal dose alone; the authors state this cytotoxicity was comparable to 0.7 μmol/L oxaliplatin. Figure-derived values were not digitized.",
        "dose": "Fixed-ratio dose-response combinations over ursolic acid 0–100 μmol/L and oxaliplatin 0–10 μmol/L; MTT and CI analysis at 48 h. A separately described apoptosis comparison used ursolic acid 10 μmol/L plus oxaliplatin 0.4 μmol/L versus either alone and oxaliplatin 0.7 μmol/L.",
        "population": "Human colorectal-cancer cell lines SW480, SW620, LoVo and RKO; apoptosis experiments included SW620 and RKO.",
        "design": "Controlled in-vitro MTT proliferation and combination-index experiments plus apoptosis assays; the source says combination testing used fixed ratios and 48-h exposure. Source reports experiments repeated at least three times; no separate human or dietary exposure was tested.",
        "limitations": "Cell models only; no clinical or ordinary-food exposure inference. The authors' synergy interpretation is limited to tested ratios, concentrations and 48-h conditions. Figure values were not estimated. Tested compound lot/purity were not reported.",
        "preparation": "Ursolic acid purchased from Sigma and dissolved in DMSO; oxaliplatin purchased from Minsheng-Sanofi. Lot/purity were not stated.",
        "endpoint": "Cell proliferation/MTT, combination index and apoptosis in CRC cell lines.",
        "numerical": "Primary full-text Table 1 directly reports four CI values and single-agent/combination IC50 values; Results report the 10 μmol/L UA + 0.4 μmol/L OXA apoptosis comparison. No graph-derived values were used.",
        "claims": "Primary full-text Results—synergistic inhibition/apoptosis; Table 1; Figure 2 caption; Methods—combination effects of ursolic acid and oxaliplatin. Full text directly reviewed from the archived PMC XML.",
        "verified": "Cell lines; compounds and suppliers; dose ranges, 48-h duration, fixed-ratio CI method, four CI values, apoptosis comparison and nonclinical scope.",
        "audit_disposition": "V19_TIER_1_FULL_TEXT_REVIEWED; QUANTITATIVE_OUTCOME_RECOVERED; PRIMARY_TABLE_VALUES_TRANSCRIBED",
    },
    "SB-0164": {
        "pmid": UA_PMID, "drug": "Oxaliplatin",
        "locator": "PMC4980335 full text (archived XML; V19 copy hash 8b2c4c41d05937901a522d5b8c9a758798aa825013204cf85a4a8775de94c06e): Methods—SW620 xenograft nude mouse model; Results—xenograft tumor growth, body weight and serum ALT/AST; Figures 4–5.",
        "effect": "Ursolic acid plus oxaliplatin produced the greatest tumor-growth inhibition among the tested groups in a SW620 xenograft mouse model; the paper also reports improved body-weight trajectory and attenuation of oxaliplatin-associated ALT/AST elevation.",
        "mechanism": "Tumor-tissue marker assays showed reduced phosphorylation of ERK1/2, AKT and IKKα with combination treatment. This animal evidence does not establish a human mechanism or hepatoprotection.",
        "direction": "Combination enhanced preclinical tumor-growth inhibition and was associated with source-reported improvement in animal body weight and liver-enzyme measures.",
        "outcome": "Female nude mice (6–8 weeks) bearing subcutaneous SW620 tumors were randomized 5 days after inoculation to six groups (n=6/group). Ursolic acid 10 or 20 mg/kg i.p. was administered for five consecutive days; oxaliplatin was a single 10 mg/kg i.p. dose, alone or combined with ursolic acid. Tumor volume and body weight were monitored twice weekly; animals were sacrificed on day 50. Single agents reduced tumor weight versus vehicle (p<0.05); combination groups reduced it versus vehicle (p<0.01) and showed the strongest tumor inhibition. Oxaliplatin-associated serum ALT/AST elevations were reported as improved by ursolic acid; exact plotted values were not transcribed. Body weights were reported as maintained/improved, without exact figure values copied.",
        "dose": "Ursolic acid 10 or 20 mg/kg i.p. daily for five consecutive days; oxaliplatin 10 mg/kg i.p. as a single dose, alone or with ursolic acid. Tumor measurements followed twice weekly through day 50.",
        "population": "Female nude mice aged 6–8 weeks bearing subcutaneous SW620 human colorectal-cancer xenografts; six animals per group across six randomized treatment groups.",
        "design": "Controlled six-arm xenograft experiment: vehicle, two ursolic-acid doses, oxaliplatin alone, and two combinations. Tumor volume/body weight monitored twice weekly; serum ALT/AST measured at endpoint; tumors assessed by histology and signaling-marker assays.",
        "limitations": "Animal model with one xenograft cell line and six mice per group; oxaliplatin was a single intraperitoneal dose. ALT/AST and tumor outcomes are figure based and were not digitized; no patient hepatoprotection, efficacy or dietary-exposure inference is supported. Source's claim of improved body weight is not quantified in text.",
        "preparation": "Ursolic acid purchased from Sigma, dissolved in DMSO; oxaliplatin purchased from Minsheng-Sanofi. Lot/purity were not stated.",
        "endpoint": "Xenograft tumor volume/weight, body weight, serum ALT/AST, apoptosis/proliferation, and tumor signaling markers.",
        "numerical": "Primary full text Methods report group size, doses, route, schedule, measurement interval and day-50 endpoint. Results report tumor-weight significance (single agents p<0.05; combination p<0.01 vs control); exact figure values for tumor, body weight and ALT/AST were not digitized.",
        "claims": "Primary full-text Methods—SW620 xenograft nude mouse model; Results—xenograft antitumor activity and liver-function/body-weight observations; Figures 4–5 and captions. Full text directly reviewed from archived PMC XML.",
        "verified": "Cell-line-derived model, mouse sex/age, allocation and n, compound doses/routes/duration, oxaliplatin single dose, tumor/weight monitoring, endpoint, tumor-weight significance and ALT/AST direction.",
        "audit_disposition": "V19_TIER_1_FULL_TEXT_REVIEWED; QUANTITATIVE_OUTCOME_RECOVERED; FIGURE_VALUES_NOT_DIGITIZED",
    },
}


def verify_med_cache(path: Path, pmid: str, doi: str) -> None:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    items = payload.get("resultList", {}).get("result", [])
    if not any(str(item.get("pmid", item.get("id", ""))) == pmid and str(item.get("doi", "")).lower() == doi.lower() for item in items):
        raise ValueError(f"archived MED metadata does not verify PMID and DOI: {pmid}")


def apply() -> dict[str, object]:
    parent = ROOT.parent / "StageB_V18_20261103"
    if not parent.is_dir():
        raise FileNotFoundError("immutable V18 parent release is required")

    # Preserve the primary PMC XML as an exact, hash-identified V19 artifact.
    parent_xml = parent / "history/rebuild_artifacts" / UA_XML_NAME
    if not parent_xml.is_file() or hashlib.sha256(parent_xml.read_bytes()).hexdigest() != UA_XML_SHA256:
        raise ValueError("immutable V18 PMC4980335 XML source is absent or does not match its content hash")
    v19_xml = ROOT / "history/rebuild_artifacts" / UA_XML_NAME
    if v19_xml.exists() and hashlib.sha256(v19_xml.read_bytes()).hexdigest() != UA_XML_SHA256:
        raise ValueError("existing V19 copy of PMC4980335 XML has unexpected content")
    if not v19_xml.exists():
        shutil.copyfile(parent_xml, v19_xml)

    for pmid, (doi, _title, _url, cache) in SOURCES.items():
        verify_med_cache(ROOT / cache, pmid, doi)

    baseline = {r["Evidence_ID"]: r for r in read_csv("../StageB_V18_20261103/data/interaction_evidence.csv")[1]}
    blank_ids = {eid for eid, row in baseline.items() if not row.get("Quantitative_Outcome", "").strip()}
    if len(blank_ids) != 90 or not set(RECORDS) <= blank_ids:
        raise ValueError("Batch 006 targets must be among the 90 blank outcomes in immutable V18")
    current = {r["Evidence_ID"]: r for r in read_csv("data/interaction_evidence.csv")[1]}
    if any(current[eid].get("Quantitative_Outcome", "").strip() for eid in RECORDS):
        raise ValueError("Batch 006 target outcome already populated; refusing a duplicate application")

    evidence_updates = {}
    audit_updates = {}
    claim_updates = {}
    review_fields = ["Batch", "Evidence_ID", "Compound_ID", "Compound", "Drug_Probe", "Study_ID", "PMID", "DOI", "Primary_Source_URL", "Source_Access_Status", "Local_Metadata_Cache", "Source_Locator", "Verification_Tier", "Review_Date", "Correction_Made", "Verified_Outcome", "Remaining_Limitation"]
    review_rows = []
    for eid, spec in RECORDS.items():
        pmid = spec["pmid"]
        doi, title, url, cache = SOURCES[pmid]
        row = current[eid]
        exact_locator = spec["locator"]
        level = "compound"
        evidence_updates[eid] = {
            "Interaction_Effect": spec["effect"], "Mechanism": spec["mechanism"],
            "Evidence_Level": level, "Direction": spec["direction"],
            "Quantitative_Outcome": spec["outcome"], "Dose": spec["dose"],
            "Population": spec["population"], "Study_Design": spec["design"],
            "Source_Title": title, "Authors": "Mukhtar E, Adhami VM, Siddiqui IA, Verma AK, Mukhtar H." if pmid == F_PMID else "Shan J, Xuan Y, Zhang Q, Zhu C, Liu Z, Zhang S.",
            "Year": "2016", "DOI": doi, "PMID": pmid, "Source_Type": "Primary research",
            "Limitations": spec["limitations"],
            "Confidence": "Primary full-text source reviewed; source-specific and preclinical; independent expert re-review not performed.",
            "Notes": f"V19-006 primary-source extraction. Source limitations and open discrepancies are recorded in V19_batch_006_review.csv and warning ledger.",
            "Study_ID": "PMID:" + pmid, "Source_URL": url, "Source_Cache": cache,
            "Source_Locator": exact_locator, "Preparation": spec["preparation"],
            "Identity_Status": "source-designated named compound; reagent lot/purity not independently verified",
            "Outcome": "synergy observed" if eid in {"SB-0110", "SB-0163"} else "preclinical combination effect",
        }
        audit_updates[eid] = {
            "PMID": pmid, "DOI": doi, "Source_Title": title, "Source_URL": url,
            "Source_Cache": cache, "Source_Locator": exact_locator,
            "Verification_Status": "Tier 1: primary full text and record-specific methods/results/table/figure directly reviewed in V19-006",
            "Fields_Audited": "compound and preparation; drug/probe; source identity; model and design; dose, route, frequency and timing; endpoint and direction; primary numerical values, units and statistics; source discrepancy and exposure limitations",
            "Limitations": spec["limitations"], "Source_Type": "Primary research",
            "Verification_Date": DATE,
            "Verification_Method": "Original PMC full text reviewed. PMID 27472952: full PMC JATS XML archived in V19 history and copied byte-exactly from immutable V18 (SHA-256 recorded in batch integrity output). PMID 27765854: full PMC article page reviewed; PubMed MED metadata independently cross-checked; supplementary Figure S1 is referenced but was not separately retrieved.",
            "Verification_Level": "1",
            "Audit_Disposition": spec["audit_disposition"],
            "Reviewer": "Codex AI-assisted primary-source curation; independent expert re-review not performed.",
            "Endpoint_Verified": spec["endpoint"], "Numerical_Outcome_Verified": spec["numerical"],
            "Study_ID": "PMID:" + pmid, "Compound_ID": row["Compound_ID"], "Drug_Probe": spec["drug"],
            "V18_Unresolved_Discrepancy": "V19-006 independently reviewed source content. See batch-specific open warning(s) for source-internal model-label, timing or CI-definition inconsistency; no unsupported adjudication was made.",
        }
        claim_updates[eid] = {
            "Compound_ID": row["Compound_ID"], "PMID": pmid, "Source_Locator": exact_locator,
            "Verification_Status": "Primary full-text record-specific review completed in V19-006; source-supported findings entered; source discrepancy retained where applicable.",
            "Numerical_Use": spec["numerical"], "Attribution": row["Compound"] + " / " + spec["drug"],
            "Limitations": spec["limitations"],
        }
        if pmid == UA_PMID:
            access = f"Primary PMC full-text XML reviewed from immutable V18 archive and copied into V19 byte-exactly as history/rebuild_artifacts/{UA_XML_NAME}; publisher/PMC full text cross-checked."
        else:
            access = "Primary full article reviewed from PMC full-text page; PubMed metadata cross-checked. Supplementary Figure S1 was referenced but not separately downloaded; Table 1 supplies the reported CI values."
        review_rows.append({
            "Batch": "V19-006", "Evidence_ID": eid, "Compound_ID": row["Compound_ID"],
            "Compound": row["Compound"], "Drug_Probe": spec["drug"], "Study_ID": "PMID:" + pmid,
            "PMID": pmid, "DOI": doi, "Primary_Source_URL": url, "Source_Access_Status": access,
            "Local_Metadata_Cache": cache, "Source_Locator": exact_locator, "Verification_Tier": 1,
            "Review_Date": DATE,
            "Correction_Made": "Replaced inherited blank outcome and abstract/pending source disposition with a source-specific extraction of models, treatment conditions, outcomes, units, statistics and limitations. Corrected SB-0110/SB-0111 Evidence_Level from formulation to compound because pure named fisetin reagent was tested. Repaired legacy MED metadata cache locators for both PMIDs. Added open source-discrepancy warnings where article text is internally inconsistent.",
            "Verified_Outcome": spec["outcome"], "Remaining_Limitation": spec["limitations"],
        })

    update_rows("data/interaction_evidence.csv", "Evidence_ID", evidence_updates)
    update_rows("provenance/source_audit.csv", "Evidence_ID", audit_updates)
    update_rows("provenance/claim_support_and_verification.csv", "Evidence_ID", claim_updates)
    update_rows("data/publication_bibliography.csv", "PMID", {pmid: {"Source": cache} for pmid, (_doi, _title, _url, cache) in SOURCES.items()})

    with (ROOT / "validation/V19_batch_006_review.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=review_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(review_rows)

    study_updates = {
        "PMID:" + pmid: {"Verification_Status": status}
        for pmid, status in {
            UA_PMID: "V19-006: PMC full-text XML and Methods/Results, Table 1 and Figures 2/4–5 reviewed for SB-0163/0164; in-vitro CI/apoptosis and SW620 xenograft findings transcribed; no graph values digitized.",
            F_PMID: "V19-006: PMC full text, Methods, Results, Table 1 and Figures 1/3–6 reviewed for SB-0110/0111; cell-line label, CI-threshold and PC-3M treatment-start discrepancies preserved as V19-W11–W13.",
        }.items()
    }
    update_rows("data/study_registry.csv", "Study_ID", study_updates)

    # Extend the already-resolved metadata-locator warning after validating both caches.
    fields, warnings, bom = read_csv("data/warning_ledger.csv")
    warning = next((r for r in warnings if r["Warning_ID"] == "V19-W10"), None)
    if not warning or warning.get("Audit_Status") != "RESOLVED":
        raise ValueError("V19-W10 must remain resolved before its verified scope expansion")
    warning.update({
        "Description": warning["Description"].replace("and PMID 30877660", ", PMID 30877660, PMID 27472952 and PMID 27765854"),
        "Affected": warning["Affected"] + " | SB-0110 | SB-0111 | SB-0163 | SB-0164 | bibliography PMIDs 27472952, 27765854",
        "Action": warning["Action"] + " V19-006 scope expansion: repaired both remaining legacy MED metadata locators (PMID 27472952 and 27765854) for evidence/source-audit records and bibliography rows; validated the PMID/DOI pair in each archived JSON.",
        "After": warning["After"] + " V19-006 also repairs both PMID 27472952 and 27765854 cache locators; all five audited PMID snapshots now resolve within V19.",
        "Resolution_Source": warning["Resolution_Source"] + "; V19_batch_006_review.csv; " + UA_CACHE + "; " + F_CACHE,
        "Review_Date": DATE,
        "Audit_Rationale": warning["Audit_Rationale"] + " V19-006 revalidated archived MED JSON snapshots for PMIDs 27472952 and 27765854, confirmed each PMID and DOI, and updated all four evidence/source-audit rows plus the two bibliography source paths.",
        "Audit_Verification_Reference": warning["Audit_Verification_Reference"] + "; V19_batch_006_review.csv; archived MED JSON metadata for PMIDs 27472952 and 27765854.",
    })
    write_csv("data/warning_ledger.csv", fields, warnings, bom)
    update_rows("validation/V19_warning_audit.csv", "Warning_ID", {
        "V19-W10": {
            "V19_Recheck_Status": "RESOLVED_IN_V19-004; SAME_ROOT_CAUSE_EXPANDED_AND_REPAIRED_IN_V19-005; SAME_ROOT_CAUSE_EXPANDED_AND_REPAIRED_IN_V19-006",
            "V19_Review_Work": warning["Action"],
            "V19_Evidence_or_Rationale": warning["Audit_Verification_Reference"],
            "Remaining_Limitations": "All five referenced files are PubMed bibliographic metadata only; source full text is separately cited and reviewed per evidence record.",
        },
    })

    new_warnings = [
        {
            "Warning_ID": "V19-W11", "Code": "PC3M_XENOGRAFT_TREATMENT_START_TIME_CONFLICT",
            "Description": "For SB-0111 (PMID 27765854), the Methods state that treatment began two weeks after implantation in the xenograft models, while the Results section for the PC-3M-luc-6 model states that mice were divided into groups three days after implantation. The initiation timing for the PC-3M-luc-6 experiment is internally inconsistent.",
            "Affected": "SB-0111 | PMID:27765854 | Methods—In-vivo tumor xenograft study; Results—PC-3M-luc-6 xenograft",
            "Classification": "scientific source discrepancy / animal study timing",
            "Before": "Inherited animal record lacked independently verified treatment-start timing.",
            "Action": "Compared the primary full-text Methods and model-specific Results. Preserved both statements in SB-0111 and did not choose a timing by assumption.",
            "After": "Open; Methods state two weeks after implantation; Results state three days for the PC-3M-luc-6 model.",
            "Remaining_Limitations": "The primary paper does not reconcile the conflicting initiation time; no erratum/author clarification was verified.",
            "Resolution_Source": "V19_batch_006_review.csv; PMC5136329 full text, In-vivo tumor xenograft study Methods and PC-3M-luc-6 Results.",
            "Review_Date": DATE, "Audit_Status": "NEEDS_MANUAL_REVIEW", "Inherited_Severity": "NOT_RECORDED",
            "Audit_Rationale": "This changes a reproducibility-relevant animal study design detail. Both source statements are retained; neither is preferred without external adjudication.",
            "Audit_Verification_Reference": "V19_batch_006_review.csv, SB-0111; https://pmc.ncbi.nlm.nih.gov/articles/PMC5136329/",
            "Audit_Dependencies": "Author clarification, erratum or independent expert/source adjudication.", "V17_Ledger_Audit_Status": "NOT_IN_V18",
        },
        {
            "Warning_ID": "V19-W12", "Code": "FISETIN_CABAZITAXEL_CI_THRESHOLD_DEFINITION_CONFLICT",
            "Description": "For SB-0110 (PMID 27765854), the Methods define CI<0.9 as synergy, CI=1.1 as additive and CI>1.1 as antagonism; the Results text describes synergy as CI<1. The boundary interval and terminology are therefore not consistently defined in the article. All three Table 1 CI values are below 0.9, so this does not change their source-defined classification.",
            "Affected": "SB-0110 | PMID:27765854 | Combination Index method; Results; Table 1",
            "Classification": "scientific source discrepancy / combination-index interpretation",
            "Before": "Inherited cell record did not contain independently rechecked source CI method or values.",
            "Action": "Transcribed Table 1 CI values and both threshold statements; retained the article's stated conclusion only for values below 0.9, where the two cutoffs agree.",
            "After": "Open boundary-definition discrepancy; observed CI values 0.45676, 0.74663 and 0.72226 are each <0.9. The result classification is not ambiguous for those values.",
            "Remaining_Limitations": "The article does not explain the difference between its <0.9 and <1 descriptions or define the 0.9–1.1 interval consistently.",
            "Resolution_Source": "V19_batch_006_review.csv; PMC5136329 full text, Combination Index method, Results and Table 1.",
            "Review_Date": DATE, "Audit_Status": "NEEDS_MANUAL_REVIEW", "Inherited_Severity": "NOT_RECORDED",
            "Audit_Rationale": "Exact table estimates and methods/results wording were checked. The observed values lie below both proposed synergy cutoffs, so the known discrepancy is documented without changing their classification.",
            "Audit_Verification_Reference": "V19_batch_006_review.csv, SB-0110; https://pmc.ncbi.nlm.nih.gov/articles/PMC5136329/",
            "Audit_Dependencies": "Author clarification or expert adjudication of the intended CI decision boundary, if future records approach the interval.", "V17_Ledger_Audit_Status": "NOT_IN_V18",
        },
        {
            "Warning_ID": "V19-W13", "Code": "FISETIN_CABAZITAXEL_CI_CELL_LINE_LABEL_MISMATCH",
            "Description": "For SB-0110 (PMID 27765854), Table 1 labels the CI=0.74663 row as “PC-3,” while the article's Methods and Results identify the tested metastatic line as PC-3M-luc-6/PC3M. PC-3 and PC-3M-luc-6 are not interchangeable cell-line identifiers; the precise model associated with this table value remains uncertain from the article wording reviewed.",
            "Affected": "SB-0110 | PMID:27765854 | Table 1 versus Cell Culture and Treatment Methods and Results",
            "Classification": "scientific source discrepancy / experimental model identity",
            "Before": "Inherited record described PC-3M-luc-6 but had no full-text table audit.",
            "Action": "Preserved the Table 1 label and the Methods/Results cell-line name separately; flagged the CI attribution instead of normalizing PC-3 to PC-3M-luc-6.",
            "After": "Open; CI 0.74663 is attributed to a Table 1 row labelled PC-3; article prose identifies PC-3M-luc-6 for the study.",
            "Remaining_Limitations": "No source correction, author clarification or supplement resolving the Table 1 row label was obtained; Supplementary Figure S1 was not separately retrieved.",
            "Resolution_Source": "V19_batch_006_review.csv; PMC5136329 full text, Methods, Results and Table 1.",
            "Review_Date": DATE, "Audit_Status": "NEEDS_MANUAL_REVIEW", "Inherited_Severity": "NOT_RECORDED",
            "Audit_Rationale": "The distinct cell-line names were retained as printed. No presumed typographical correction was applied to experimental model identity.",
            "Audit_Verification_Reference": "V19_batch_006_review.csv, SB-0110; https://pmc.ncbi.nlm.nih.gov/articles/PMC5136329/",
            "Audit_Dependencies": "Author clarification or an authoritative corrected table/supplement explicitly identifying the Table 1 model.", "V17_Ledger_Audit_Status": "NOT_IN_V18",
        },
    ]
    fields, warnings, bom = read_csv("data/warning_ledger.csv")
    if any(r["Warning_ID"] in {w["Warning_ID"] for w in new_warnings} for r in warnings):
        raise ValueError("V19-006 warning IDs already exist; refusing duplicate warning creation")
    warnings.extend(new_warnings)
    write_csv("data/warning_ledger.csv", fields, warnings, bom)
    audit_fields, warning_audit, audit_bom = read_csv("validation/V19_warning_audit.csv")
    for w in new_warnings:
        warning_audit.append({
            "Warning_ID": w["Warning_ID"], "V18_Status": "NEW_IN_V19", "V19_Status": w["Audit_Status"],
            "V19_Recheck_Status": "NEEDS_MANUAL_REVIEW_IN_V19-006",
            "V19_Review_Work": w["Action"], "V19_Evidence_or_Rationale": w["Audit_Verification_Reference"],
            "Remaining_Limitations": w["Remaining_Limitations"],
        })
    write_csv("validation/V19_warning_audit.csv", audit_fields, warning_audit, audit_bom)

    metadata_path = ROOT / "release_metadata.json"
    meta = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    review_meta = meta["v19_primary_source_review"]
    batches = list(review_meta.get("batches_completed", []))
    if "V19-006" not in batches:
        batches.append("V19-006")
    review_meta.update({
        "batches_completed": batches, "evidence_records_reviewed": 32,
        "tier_1_primary_full_text_records": 32, "records_corrected_or_reconstructed": 30,
        "source_review_remaining": 285, "warning_rows_preserved": 83,
        "warning_status_counts": {status: sum(r.get("Audit_Status") == status for r in warnings) for status in ["RESOLVED", "PARTIALLY_RESOLVED", "STILL_VALID", "NEEDS_MANUAL_REVIEW", "NOT_APPLICABLE"]},
        "new_warning_count": 13, "warning_ids_added": [f"V19-W{i:02d}" for i in range(1, 14)],
        "warning_rows_individually_reviewed_in_v19": 15,
    })
    meta["warning_count"] = len(warnings)
    meta["v19_quantitative_outcome_audit"].update({
        "quantitative_values_recovered": 24, "qualitative_outcomes_dispositioned": 5,
        "blank_fields_remaining": 61, "source_review_batch": "V19-006",
    })
    meta["v19_validation"].update({
        "batch05_integrity": "PASS_PENDING_FINAL_MANIFEST", "batch05_tests_passed": 10, "batch05_tests_failed": 0,
        "batch06_integrity": "PENDING_VALIDATION", "batch06_tests_passed": 0, "batch06_tests_failed": 0,
        "full_stageB_regression": "PENDING_FINAL_VALIDATION",
        "v19_exact_manifest": "PENDING_FINAL_PACKAGING", "v19_clean_copy_manifest": "PENDING_FINAL_PACKAGING",
    })
    meta["readiness"] = meta["release_status"] = "SCIENTIFIC_REMEDIATION_IN_PROGRESS"
    metadata_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return {
        "batch": "V19-006", "records_updated": len(RECORDS),
        "tier_1_full_text_reviews": len(RECORDS), "quantitative_outcomes_populated": len(RECORDS),
        "blank_outcomes_remaining": 61, "warnings_added": ["V19-W11", "V19-W12", "V19-W13"],
        "warnings_status": "all three open pending expert/source clarification",
        "V19-W10": "RESOLVED; scope expanded to five verified PubMed metadata caches",
        "status": "APPLIED_PENDING_VALIDATION",
    }


if __name__ == "__main__":
    print(json.dumps(apply(), indent=2, ensure_ascii=False))
