"""Admit four directly quantified OATP2B1 flavonoid findings as V17 batch 8."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-11-03"
ASSAY_PMID = "37252098"
ASSAY_DOI = "10.1039/d3md00078h"
ASSAY_TITLE = "Investigating the interactions of flavonoids with human OATP2B1: inhibition assay, IC50 determination, and structure-activity relationship analysis"
ASSAY_AUTHORS = "Peng T, Liu S, Li Y, Zhang H, Hagenbuch B, Gui C"
ASSAY_URL = "https://pmc.ncbi.nlm.nih.gov/articles/PMC10211325/"


def read(rel: str):
    with (ROOT / rel).open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        return list(r.fieldnames), list(r)


def write(rel: str, headers, rows):
    with (ROOT / rel).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main():
    compounds_data = [
        {
            "name": "Apigetrin", "cid": "5280704", "cas": "578-74-5",
            "aliases": "Apigenin 7-O-glucoside | apigenin-7-O-beta-D-glucopyranoside | Cosmosiin",
            "smiles": "C1=CC(=CC=C1C2=CC(=O)C3=C(C=C(C=C3O2)O[C@H]4[C@@H]([C@H]([C@@H]([C@H](O4)CO)O)O)O)O)O",
            "inchi": "InChI=1S/C21H20O10/c22-8-16-18(26)19(27)20(28)21(31-16)29-11-5-12(24)17-13(25)7-14(30-15(17)6-11)9-1-3-10(23)4-2-9/h1-7,16,18-24,26-28H,8H2/t16-,18-,19+,20-,21-/m1/s1",
            "key": "KMOUJOKENFFTPU-QNDFHXLGSA-N", "ic50": "10.5 ± 1.5 μM",
            "food": "Apigenin 7-O-glucoside directly extracted and identified from Chrysanthemum morifolium ‘Huangju’ flowers (used for chrysanthemum tea); food-context study reports 16.04 mg/g in the extracted material, not dietary intake.",
            "food_doi": "10.3390/molecules23112933", "food_pmid": "30424020",
            "food_title": "Extraction, Purification, and Hydrolysis Behavior of Apigenin-7-O-Glucoside from Chrysanthemum Morifolium Tea",
            "food_authors": "Wang Y, Xu Z, Huang Y, Wen X, Wu Y, Zhao Y, Ni Y",
            "food_year": "2018", "food_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC6278536/",
        },
        {
            "name": "Myricitrin", "cid": "5281673", "cas": "17912-87-7",
            "aliases": "Myricetin 3-O-rhamnoside | Myricitroside | Myricitrine",
            "smiles": "C[C@H]1[C@@H]([C@H]([C@H]([C@@H](O1)OC2=C(OC3=CC(=CC(=C3C2=O)O)O)C4=CC(=C(C(=C4)O)O)O)O)O)O",
            "inchi": "InChI=1S/C21H20O12/c1-6-14(26)17(29)18(30)21(31-6)33-20-16(28)13-9(23)4-8(22)5-12(13)32-19(20)7-2-10(24)15(27)11(25)3-7/h2-6,14,17-18,21-27,29-30H,1H3/t6-,14-,17+,18+,21-/m0/s1",
            "key": "DCYOADKBABEMIQ-OWMUPTOHSA-N", "ic50": "46.2 ± 1.3 μM",
            "food": "Isolated and identified from Daebong persimmon peel; separate food-additive study describes myricitrin extracted from Chinese bayberry and used as a flavor modifier. No ordinary serving exposure is inferred.",
            "food_doi": "10.3746/pnf.2018.23.4.341", "food_pmid": "30675464",
            "food_title": "Isolation and Identification of Myricitrin, an Antioxidant Flavonoid, from Daebong Persimmon Peel",
            "food_authors": "Hwang IW, Chung SK", "food_year": "2018",
            "food_url": "https://pubmed.ncbi.nlm.nih.gov/30675464/",
        },
        {
            "name": "Prunin", "cid": "92794", "cas": "529-55-5",
            "aliases": "Naringenin 7-O-beta-D-glucoside | naringenin-7-glucoside",
            "smiles": "OC[C@H]1O[C@@H](Oc2cc(O)c3C(=O)C[C@H](Oc3c2)c2ccc(O)cc2)[C@H](O)[C@@H](O)[C@@H]1O",
            "inchi": "InChI=1S/C21H22O10/c22-8-16-18(26)19(27)20(28)21(31-16)29-11-5-12(24)17-13(25)7-14(30-15(17)6-11)9-1-3-10(23)4-2-9/h1-6,14,16,18-24,26-28H,7-8H2/t14-,16+,18+,19-,20+,21+/m0/s1",
            "key": "DLIKSSGEMUFQOK-SFTVRKLSSA-N", "ic50": "101.0 ± 1.6 μM",
            "food": "Detected in immature grapefruit peel; the primary biosynthesis study distinguishes prunin (naringenin 7-O-glucoside) from naringin and reports detection in immature peel.",
            "food_doi": "10.1016/S0031-9422(00)97813-0", "food_pmid": "",
            "food_title": "Biosynthesis of naringin and prunin in detached grapefruit",
            "food_authors": "Berhow MA, Vandercook CE", "food_year": "1989",
            "food_url": "https://doi.org/10.1016/S0031-9422(00)97813-0",
        },
        {
            "name": "Quercitrin", "cid": "5280459", "cas": "522-12-3",
            "aliases": "Quercetin 3-O-alpha-L-rhamnoside | Quercitroside | Quercetrin",
            "smiles": "C[C@@H]1O[C@@H](Oc2c(oc3cc(O)cc(O)c3c2=O)-c2ccc(O)c(O)c2)[C@@H](O)[C@H](O)[C@H]1O",
            "inchi": "InChI=1S/C21H20O11/c1-7-15(26)17(28)18(29)21(30-7)32-20-16(27)14-12(25)5-9(22)6-13(14)31-19(20)8-2-3-10(23)11(24)4-8/h2-7,15,17-18,21-26,28-29H,1H3/t7-,15-,17+,18-,21-/m1/s1",
            "key": "OXGUCUVFOIWWQJ-HQBVPOQASA-N", "ic50": "63.1 ± 1.3 μM",
            "food": "Quercetin 3-rhamnoside isolated and identified among the polyphenols in apple pomace from juice processing; this establishes apple-processing byproduct occurrence, not a serving-level exposure estimate.",
            "food_doi": "10.1016/S0308-8146(96)00287-7", "food_pmid": "",
            "food_title": "Identification and quantification of major polyphenols in apple pomace",
            "food_authors": "Lu Y, Foo LY", "food_year": "1997",
            "food_url": "https://www.sciencedirect.com/science/article/pii/S0308814696002877",
        },
    ]

    ch, compounds = read("data/compound_registry.csv")
    ih, identities = read("identity/identity_structure_audit.csv")
    eh, evidence = read("data/interaction_evidence.csv")
    bh, bibliography = read("data/publication_bibliography.csv")
    sh, studies = read("data/study_registry.csv")
    fch, food_audit = read("provenance/food_context_audit.csv")
    sah, source_audit = read("provenance/source_audit.csv")
    srh, source_register = read("provenance/source_register.csv")
    csh, claims = read("provenance/claim_support_and_verification.csv")
    sdh, selection = read("provenance/selection_decisions.csv")
    clh, screening = read("provenance/candidate_screening_log.csv")
    wh, warnings = read("data/warning_ledger.csv")
    ph, probes = read("data/drug_probe_registry.csv")

    old_cids = {r["PubChem_CID"] for r in compounds}
    old_keys = {r["InChIKey"] for r in compounds}
    old_pmids = {r["PMID"] for r in bibliography if r["PMID"]}
    old_eids = {r["Evidence_ID"] for r in evidence}
    if any(d["cid"] in old_cids or d["key"] in old_keys for d in compounds_data):
        raise SystemExit("Batch 8 candidate CID or structure already exists")
    if ASSAY_PMID in old_pmids:
        raise SystemExit("Batch 8 source PMID already exists; reconcile before ingestion")

    evidence_ids = []
    compound_ids = {}
    for n, d in enumerate(compounds_data, 1):
        cid = d["cid"]
        mid = f"MOL-V17-CID-{cid}"
        eid = f"SB-V17-{n:03d}"
        if eid in old_eids:
            raise SystemExit(f"Evidence ID already exists: {eid}")
        compound_ids[cid] = mid
        evidence_ids.append(eid)
        compounds.append({
            "Compound_ID": mid, "Canonical_Name": d["name"], "Aliases": f"{d['name']} | {d['aliases']} | CAS {d['cas']}",
            "PubChem_CID": cid, "SMILES": d["smiles"], "InChI": d["inchi"], "InChIKey": d["key"],
            "Identity_Status": "PubChem CID, synonym, isomeric structure, InChI, and InChIKey cross-checked; exact stereochemical entity retained.",
            "Identity_Source": f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}",
            "Origin": "v17_batch_08", "Selection_Rationale": f"Directly tested as {d['name']} in a primary human OATP2B1 DBF uptake inhibition study; Table 1 reports a compound-specific IC50. Distinct glycoside retained as separate entity.",
            "Selection_Source": f"Primary transporter study PMID:{ASSAY_PMID}; exact food occurrence separately documented in the cited food-context primary source.",
            "Selection_DOI": ASSAY_DOI, "Selection_PMID": ASSAY_PMID, "Selection_URL": ASSAY_URL,
            "Date_Added": DATE, "First_Documented_Release_Date": DATE, "Date_Status": "V17 curation date; historical selection date not claimed.",
            "Coverage_Status": "One direct in-vitro OATP2B1 DBF uptake assay; no clinical interaction or food-dose inference.",
            "Provenance_Status": "v17_primary_interaction_and_food_context_sources_reviewed",
            "Original_Molecular_Group": mid, "Retention_Status": "No cooking-retention evidence inferred.",
            "Food_Context": d["food"], "Evidence_Records": "1",
            "Link_Restriction": "Transporter assay evidence only; no Stage C exposure integration or human clinical classification.",
            "Release_Reviewed": "v17_20261103", "Selection_Verification": "Primary article full-text figures/table reviewed; PubChem exact entity checked; separate primary food occurrence study reviewed.",
            "Earliest_Verified_Selection_Date": DATE, "Selection_Temporality": "retrospective V17 selection; primary papers predate curation",
            "Remaining_Provenance_Gap": "No quantitative mapping from food intake to assay concentration; no human DDI evidence for these compounds.",
        })
        identities.append({
            "Compound_ID": mid, "Canonical_Name": d["name"], "PubChem_CID": cid,
            "Returned_InChIKey": d["key"], "Registry_InChIKey": d["key"], "Exact_Key_Match": "True",
            "SMILES": d["smiles"], "InChI": d["inchi"],
            "Structure_Source": f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}", "Status": "Complete",
            "Note": "PubChem stereospecific entity retained; separate from aglycone and other glycosides.",
            "PubChem_Name_or_Alias_Match": "True", "PubChem_Synonyms": f"{d['name']} | {d['aliases']} | {d['cas']}",
        })
        evidence.append({
            "Evidence_ID": eid, "Compound": d["name"], "Compound_ID": mid,
            "Drug": "OATP2B1-mediated DBF uptake",
            "Interaction_Effect": f"{d['name']} inhibited OATP2B1-mediated DBF uptake in vitro.",
            "Mechanism": "Transporter uptake inhibition; molecular binding mechanism not independently established.",
            "Evidence_Type": "In vitro", "Evidence_Level": "compound", "Direction": "reduced transporter uptake",
            "Quantitative_Outcome": f"IC50={d['ic50']} (Table 1; primary article).",
            "Dose": "Compound concentration-response determination; screen included 10 and 100 μM flavonoid conditions. Exact titration points are not reproduced here.",
            "Population": "CHO-OATP2B1 and CHO-WT cell assay; DBF uptake measured at 5 μM, 37 °C, 2 min.",
            "Study_Design": "Fluorescent DBF uptake inhibition assay with IC50 determination; Fig. 4 and Table 1.",
            "Source_Title": ASSAY_TITLE, "Authors": ASSAY_AUTHORS, "Year": "2023", "DOI": ASSAY_DOI, "PMID": ASSAY_PMID,
            "Source_Type": "Primary research", "Limitations": "In vitro transporter assay; DBF is an assay probe, not a therapeutic drug. Food occurrence is documented independently; no food exposure equivalence, human interaction, or clinical inference.",
            "Confidence": "Direct in-vitro compound-specific primary evidence; clinical relevance unknown.",
            "Notes": "IC50 reported as mean ± SD in Table 1; do not treat as a dietary threshold.",
            "Study_ID": f"PMID:{ASSAY_PMID}", "Source_URL": ASSAY_URL, "Source_Cache": "PMC10211325",
            "Source_Locator": "Results §§3.2–3.3; Fig. 4; Table 1",
            "Preparation": f"Isolated {d['name']} standard; detailed commercial lot/specification not established in the article table.",
            "Co_Compounds": "4',5'-dibromofluorescein (DBF)", "Affected_Entity": "transporter assay probe",
            "Perpetrator": "compound", "Outcome": "observed_effect", "Conflict_Group": "",
            "Identity_Status": "verified_exact_pubchem_entity", "Release_Origin": "v17_batch_08",
            "Clinical_Extrapolation": "No clinical extrapolation; in-vitro uptake assay only.",
            "CookRisk_Exposure_Link": "Food occurrence source recorded; quantitative food exposure and assay-concentration bridge not established.",
        })
        food_audit.append({
            "Compound_ID": mid, "Compound": d["name"], "Food_Context": d["food"],
            "Context_Class": "Direct food occurrence/food processing evidence; not dietary exposure quantification",
            "Review_Status": "Primary food-context paper inspected; source refers to plant/food sample or food additive as described.",
            "Context_Source": f"{d['food_url']} (DOI {d['food_doi']})",
        })
        screening.append({
            "Search_Date": DATE, "Database": "PubMed/PMC + PubChem",
            "Query_or_Candidate": d["name"], "Decision": "Included in V17 Batch 8",
            "Reason": f"New CID/key absent from inherited registry; exact PubChem structure verified; primary OATP2B1 assay Table 1 reports IC50 {d['ic50']}; separate primary food context verified.",
            "Full_Text_Availability": "Interaction and food-context primary full texts inspected",
            "Verification_Status": "Identity, primary endpoint, quantitative value, and food context reviewed",
            "Reviewer_Note": "No clinical DDI claim; exact glycoside entity preserved.",
        })
        selection.append({
            "Candidate": d["name"], "Decision": "Included in V17 Batch 8",
            "Identity": f"PubChem CID {cid}; InChIKey {d['key']}; exact isomeric entity recorded.",
            "Food_Context": d["food"],
            "Interaction_Rationale": f"Primary OATP2B1 DBF uptake assay reports IC50 {d['ic50']}.",
            "Primary_Source_PMID": ASSAY_PMID, "Primary_Source_DOI": ASSAY_DOI,
            "Verification": "Full-text Table 1/Fig. 4 and PubChem structure reviewed; food-context primary source separately reviewed.",
            "Date": DATE, "Residual_Limitation": "In vitro only; no clinical or intake-to-assay inference.",
        })
        claims.append({
            "Evidence_ID": eid, "Compound_ID": mid, "PMID": ASSAY_PMID,
            "Source_Locator": "Results §§3.2–3.3; Fig. 4; Table 1",
            "Verification_Status": "Primary full text inspected; compound-specific IC50 extracted",
            "Numerical_Use": "IC50 only; not a human exposure threshold",
            "Attribution": f"{d['name']} / OATP2B1-mediated DBF uptake",
            "Limitations": "In vitro transporter probe; no therapeutic drug or clinical interaction established.",
        })

        source_register.append({
            "PMID": d["food_pmid"], "DOI": d["food_doi"], "Compound": d["name"],
            "Chemical_record": f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}",
            "Primary_source": d["food_url"], "Access_date": DATE,
            "Source_limit": "Food context only; not interaction evidence and not a quantitative consumed-dose estimate.",
            "Verification_scope": "Primary food/plant/food-additive occurrence of the exact named glycoside.",
        })
        source_audit.append({
            "Evidence_ID": eid, "PMID": ASSAY_PMID, "Compound": d["name"],
            "Source_Title": ASSAY_TITLE, "Source_URL": ASSAY_URL,
            "Source_Locator": "Results §§3.2–3.3; Fig. 4; Table 1",
            "Verification_Status": "Primary full text inspected",
            "Fields_Audited": "Compound identity; OATP2B1 model; DBF probe; IC50 and SD; assay conditions; limits",
            "Limitations": "No human clinical interaction; DBF is a probe; no dietary exposure bridge.",
        })

    bibliography.append({
        "PMID": ASSAY_PMID, "Title": ASSAY_TITLE, "Authors": ASSAY_AUTHORS, "Year": "2023",
        "DOI": ASSAY_DOI, "PMCID": "PMC10211325", "Source": ASSAY_URL,
        "Count_Unit": "Unique PMID-indexed publication; not independent cohort",
        "DOI_Status": "Verified on PubMed record and primary publisher article",
    })
    studies.append({
        "Study_ID": f"PMID:{ASSAY_PMID}", "PMID": ASSAY_PMID, "DOI": ASSAY_DOI,
        "Title": ASSAY_TITLE, "Authors": ASSAY_AUTHORS, "Year": "2023",
        "Evidence_Record_IDs": "|".join(evidence_ids), "Evidence_Record_Count": str(len(evidence_ids)),
        "Evidence_Classes": "In vitro transporter uptake assay",
        "Verification_Status": "Primary full text inspected; Table 1 values extracted",
        "Independence": "Publication identifier only; no clinical cohort inferred",
    })
    warnings.append({
        "Warning_ID": "V17-W01", "Code": "V17_BATCH_08_IN_VITRO_EXPOSURE_LIMIT",
        "Description": "Four newly added flavonoid-glycoside findings are in-vitro OATP2B1/DBF uptake inhibition results; dietary exposure relevance and therapeutic-drug interaction are not established.",
        "Affected": "MOL-V17-CID-5280704 | MOL-V17-CID-5281673 | MOL-V17-CID-92794 | MOL-V17-CID-5280459 | " + " | ".join(evidence_ids),
        "Classification": "scientific uncertainty / in-vitro interpretation",
        "Before": "No V17 Batch 8 entries",
        "Action": "Added separate in-vitro results and independent food-context records; restricted interpretation and retained uncertainty.",
        "After": "Open; no clinical inference",
        "Remaining_Limitations": "No human drug interaction, consumed food dose, bioavailability bridge, or validated assay-to-food exposure relationship.",
        "Resolution_Source": f"PMID:{ASSAY_PMID}; {ASSAY_URL}", "Review_Date": DATE,
        "Audit_Status": "STILL_VALID", "Inherited_Severity": "NOT_RECORDED",
        "Audit_Rationale": "The assay supports uptake inhibition in a cell system only; no evidence justifies clearing the food-exposure/clinical uncertainty.",
        "Audit_Verification_Reference": f"{ASSAY_URL}; Table 1 and Fig. 4",
        "Audit_Dependencies": "Human exposure and clinical relevance have not been established.",
    })

    probe = next((r for r in probes if r["Drug_Probe"] == "OATP2B1-mediated DBF uptake"), None)
    if not probe:
        raise SystemExit("Expected existing OATP2B1/DBF probe row not found")
    probe["Evidence_Records"] = str(int(probe["Evidence_Records"]) + len(evidence_ids))
    if ASSAY_PMID not in probe["Primary_PMIDs"].split(";"):
        probe["Primary_PMIDs"] = (probe["Primary_PMIDs"] + ";" + ASSAY_PMID).strip(";")
    probe["Scope"] += "; V17 batch 8 flavonoid inhibition assay; DBF remains a transporter probe, not a therapeutic drug."

    write("data/compound_registry.csv", ch, compounds)
    write("identity/identity_structure_audit.csv", ih, identities)
    write("data/interaction_evidence.csv", eh, evidence)
    write("data/publication_bibliography.csv", bh, bibliography)
    write("data/study_registry.csv", sh, studies)
    write("data/drug_probe_registry.csv", ph, probes)
    write("data/warning_ledger.csv", wh, warnings)
    write("provenance/food_context_audit.csv", fch, food_audit)
    write("provenance/source_audit.csv", sah, source_audit)
    write("provenance/source_register.csv", srh, source_register)
    write("provenance/claim_support_and_verification.csv", csh, claims)
    write("provenance/selection_decisions.csv", sdh, selection)
    write("provenance/candidate_screening_log.csv", clh, screening)

    metadata = json.loads((ROOT / "release_metadata.json").read_text(encoding="utf-8"))
    metadata.update({
        "expected_compounds": len({r["Compound_ID"] for r in compounds}),
        "expected_evidence": len({r["Evidence_ID"] for r in evidence}),
        "warning_count": len(warnings), "drug_probe_rows": len(probes),
        "bibliography_rows": len(bibliography), "study_rows": len(studies),
        "unique_nonblank_PMIDs": len({r["PMID"] for r in bibliography if r["PMID"]}),
        "last_completed_batch": 8, "readiness": "PARTIAL_NOT_READY_FOR_150",
    })
    metadata["v17_validation"].update({
        "batch_08": "PENDING_FOCUSED_VALIDATION",
        "warning_rows_inherited_and_preserved": 66,
        "v17_new_warnings": 1,
    })
    (ROOT / "release_metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    decisions = {
        "batch": 8, "baseline_compounds": 136, "batch_start": 136, "batch_end": len({r["Compound_ID"] for r in compounds}),
        "accepted": [{"name": d["name"], "compound_id": compound_ids[d["cid"]], "pubchem_cid": d["cid"], "evidence_id": evidence_ids[i], "ic50": d["ic50"]} for i, d in enumerate(compounds_data)],
        "held": [
            {"candidate": "Eriodictyol", "reason": "The 2023 table reports eriodictyol, but study-test stereochemical form is not explicitly assigned; defer exact entity mapping."},
            {"candidate": "Eriodictyol-7-O-glucoside", "reason": "Study label does not settle flavanone aglycone stereochemistry; no PubChem stereospecific form asserted."},
        ],
        "rejected": [], "source": f"PMID {ASSAY_PMID}; DOI {ASSAY_DOI}; primary full-text Fig. 4/Table 1",
        "gate": "Pending focused tests and structural/provenance validators",
    }
    (ROOT / "validation/V17_batch_08_candidate_decisions.json").write_text(json.dumps(decisions, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    (ROOT / "validation/V17_batch_08_review.md").write_text(
        "# V17 Batch 8 review\n\n"
        f"Primary interaction source: PMID {ASSAY_PMID}; DOI {ASSAY_DOI}; full text, Figure 4, and Table 1 reviewed. "
        "The study measured OATP2B1-mediated uptake of 5 μM DBF in CHO-WT/CHO-OATP2B1 cells at 37 °C for 2 min. "
        "The selected glycosides have separate reported IC50 values; these are in-vitro probe-assay outcomes, not food-dose or human DDI thresholds.\n\n"
        "Accepted: Apigetrin (CID 5280704; IC50 10.5 ± 1.5 μM), Myricitrin (CID 5281673; 46.2 ± 1.3 μM), "
        "Prunin (CID 92794; 101.0 ± 1.6 μM), and Quercitrin (CID 5280459; 63.1 ± 1.3 μM). Exact PubChem structure keys were checked. "
        "Food-context evidence was inspected separately: chrysanthemum flowers/tea, persimmon peel/bayberry flavoring, immature grapefruit peel, and apple pomace, respectively.\n\n"
        "Held: eriodictyol and eriodictyol-7-O-glucoside pending exact tested stereochemical entity mapping. Glycosides remain distinct from aglycones. "
        "Batch warning V17-W01 records the assay-to-dietary-exposure limitation.\n\nGate: pending automated validation.\n",
        encoding="utf-8", newline="\n",
    )
    (ROOT / "validation/V17_batch_08_gate.json").write_text(json.dumps({
        "batch": 8, "status": "PENDING_AUTOMATED_VALIDATION", "start_compounds": 136,
        "end_compounds": len({r["Compound_ID"] for r in compounds}),
        "new_compounds": len(compounds_data), "new_evidence": len(evidence_ids),
        "new_warnings": 1, "accepted": [d["name"] for d in compounds_data],
    }, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
