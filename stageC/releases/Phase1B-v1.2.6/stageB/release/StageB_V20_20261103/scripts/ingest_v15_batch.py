"""Controlled V15 batch ingestion from reviewed primary-source records."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-11-02"
PMID = "40773056"
DOI = "10.1021/acs.molpharmaceut.5c00705"
TITLE = "Food Additives Inhibit Intestinal Drug Transporters but Have Limited Effect on In Vitro Drug Permeability"
AUTHORS = "Suominen L, Stenberg E, Sjöstedt N, Kidron H"
URL = "https://pubmed.ncbi.nlm.nih.gov/40773056/"


def read(rel: str) -> tuple[list[str], list[dict[str, str]]]:
    with (ROOT / rel).open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write(rel: str, headers: list[str], rows: list[dict[str, str]]) -> None:
    with (ROOT / rel).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    compound_defs = [
        {
            "name": "all-trans-β-Carotene", "cid": "5280489", "aliases": "beta-carotene | β-carotene | all-trans-beta-carotene | provitamin A",
            "smiles": r"CC1=C(C(CCC1)(C)C)/C=C/C(=C/C=C/C(=C/C=C/C=C(/C=C/C=C(/C=C/C2=C(CCCC2(C)C)C)\C)\C)/C)/C",
            "inchi": "InChI=1S/C40H56/c1-31(19-13-21-33(3)25-27-37-35(5)23-15-29-39(37,7)8)17-11-12-18-32(2)20-14-22-34(4)26-28-38-36(6)24-16-30-40(38,9)10/h11-14,17-22,25-28H,15-16,23-24,29-30H2,1-10H3/b12-11+,19-13+,20-14+,27-25+,28-26+,31-17+,32-18+,33-21+,34-22+",
            "inchikey": "OENHQHLEOONYIE-JLTXGRSLSA-N", "context": "Food color and provitamin A carotenoid; isolated-compound transporter assays do not establish food-level clinical interaction.",
            "evidence": 4,
        },
        {
            "name": "Butylated hydroxytoluene", "cid": "31404", "aliases": "BHT | 2,6-di-tert-butyl-4-methylphenol | E321 | 2,6-di-tert-butyl-p-cresol",
            "smiles": "CC1=CC(=C(C(=C1)C(C)(C)C)O)C(C)(C)C",
            "inchi": "InChI=1S/C15H24O/c1-10-8-11(14(2,3)4)13(16)12(9-10)15(5,6)7/h8-9,16H,1-7H3",
            "inchikey": "NLZUEZXRPGMBCV-UHFFFAOYSA-N", "context": "Food antioxidant additive; assay concentration is not a dietary exposure estimate.",
            "evidence": 1,
        },
        {
            "name": "Dodecyl gallate", "cid": "14425", "aliases": "Lauryl gallate | E312 | dodecyl 3,4,5-trihydroxybenzoate",
            "smiles": "CCCCCCCCCCCCOC(=O)C1=CC(=C(C(=C1)O)O)O",
            "inchi": "InChI=1S/C19H30O5/c1-2-3-4-5-6-7-8-9-10-11-12-24-19(23)15-13-16(20)18(22)17(21)14-15/h13-14,20-22H,2-12H2,1H3",
            "inchikey": "RPWFJAMTCNSJKK-UHFFFAOYSA-N", "context": "Food antioxidant additive; EU approval was withdrawn in 2018, while use status varies by jurisdiction; no current dietary exposure inferred.",
            "evidence": 1,
        },
        {
            "name": "Octyl gallate", "cid": "61253", "aliases": "n-octyl gallate | octyl 3,4,5-trihydroxybenzoate | Progallin O",
            "smiles": "CCCCCCCCOC(=O)C1=CC(=C(C(=C1)O)O)O",
            "inchi": "InChI=1S/C15H22O5/c1-2-3-4-5-6-7-8-20-15(19)11-9-12(16)14(18)13(17)10-11/h9-10,16-18H,2-8H2,1H3",
            "inchikey": "NRPKURNSADTHLJ-UHFFFAOYSA-N", "context": "Food antioxidant additive; regulatory authorization varies and European authorization was withdrawn in 2018; no current dietary exposure inferred.",
            "evidence": 1,
        },
    ]
    compounds_h, compounds = read("data/compound_registry.csv")
    if any(r["PubChem_CID"] == d["cid"] or r["InChIKey"] == d["inchikey"] for r in compounds for d in compound_defs):
        raise SystemExit("Batch 6 candidate duplicates a registered CID or InChIKey")

    ids = {}
    for d in compound_defs:
        cid = f"MOL-V15-CID-{d['cid']}"
        ids[d["cid"]] = cid
        compounds.append({
            "Compound_ID": cid, "Canonical_Name": d["name"], "Aliases": d["aliases"], "PubChem_CID": d["cid"],
            "SMILES": d["smiles"], "InChI": d["inchi"], "InChIKey": d["inchikey"],
            "Identity_Status": "PubChem CID, SMILES, InChI and InChIKey cross-checked; manual structure review pending.",
            "Identity_Source": f"https://pubchem.ncbi.nlm.nih.gov/compound/{d['cid']}", "Origin": "v15_controlled_expansion",
            "Selection_Rationale": f"Exact food-additive entity tested in primary transporter study PMID {PMID}; limited to in-vitro evidence and relevant null/permeability findings.",
            "Selection_Source": "Primary research; food-additive context, not an ordinary-food clinical interaction claim.", "Selection_DOI": DOI,
            "Selection_PMID": PMID, "Selection_URL": URL, "Date_Added": DATE, "First_Documented_Release_Date": DATE,
            "Date_Status": "V15 curation date; no prior selection date claimed.", "Coverage_Status": "Controlled V15 addition; transporter evidence is in-vitro only.",
            "Provenance_Status": "v15_primary_source_reviewed", "Original_Molecular_Group": "V15 batch 6 food additive",
            "Retention_Status": "No cooking-retention evidence added.", "Food_Context": d["context"], "Evidence_Records": str(d["evidence"]),
            "Link_Restriction": "No Stage C exposure integration; no human clinical risk inference.", "Release_Reviewed": "v15_20261102",
            "Selection_Verification": "Primary article full text and PubChem identity records reviewed.", "Earliest_Verified_Selection_Date": DATE,
            "Selection_Temporality": "V15 evidence-led decision", "Remaining_Provenance_Gap": "No human clinical interaction; food intake and intestinal exposure not quantified here.",
        })
    write("data/compound_registry.csv", compounds_h, compounds)

    e_h, evidence = read("data/interaction_evidence.csv")
    evidence_specs = [
        ("beta", "BCRP-mediated Lucifer yellow efflux", "IC50 = 12.1 μM (95% CI 9.9–15.5)", "BCRP-mediated Lucifer yellow efflux", "Dose-response transporter inhibition; three independent experiments in triplicate", "Figure 2; transporter overexpression/vesicle assay"),
        ("beta", "P-glycoprotein-mediated N-methyl-quinidine efflux", "IC50 = 3.2 μM (95% CI 2.4–4.3)", "P-glycoprotein-mediated N-methyl-quinidine efflux", "Dose-response transporter inhibition; three independent experiments in triplicate", "Figure 2; transporter overexpression/vesicle assay"),
        ("beta", "OATP2B1-mediated 5-carboxyfluorescein uptake", "IC50 = 27.5 μM (95% CI 22.6–35.6)", "OATP2B1-mediated 5-carboxyfluorescein uptake", "Dose-response uptake inhibition in HEK293 cells overexpressing OATP2B1", "Figure 2; OATP2B1 overexpression-cell assay"),
        ("beta", "Sulfasalazine permeability in Caco-2 cells", "No effect detected at tested concentration(s); exact effect size not reported in abstract.", "Caco-2 apical-to-basolateral sulfasalazine permeability", "Caco-2 permeability experiment; food additive tested at up to 200 μM per article methods/figure caption", "Figure 3; null permeability finding"),
        ("bht", "MRP2-mediated carboxydichlorofluorescein transport", "IC50 = 49.0 μM (95% CI 43.1–55.4)", "MRP2-mediated carboxydichlorofluorescein transport", "Dose-response transporter inhibition; vesicle assay", "Table 1 and Figure 2; direct in-vitro assay"),
        ("dodecyl", "BCRP-mediated Lucifer yellow efflux", "IC50 = 22.5 μM (95% CI 16.4–31.2)", "BCRP-mediated Lucifer yellow efflux", "Dose-response transporter inhibition; vesicle assay", "Table 1 and Figure 2; direct in-vitro assay"),
        ("octyl", "OATP2B1-mediated 5-carboxyfluorescein uptake", "65% inhibition at 50 μM; no dose-response IC50 assigned.", "OATP2B1-mediated 5-carboxyfluorescein uptake", "Single-concentration screen; weak/near-threshold effect and no dose-response curve", "Results section; current-study result; no dose-response; conflicting earlier transporter findings are discussed by authors."),
    ]
    new_evidence_ids = []
    for idx, (key, probe, quant, mechanism, design, locator) in enumerate(evidence_specs, start=1):
        d = {"beta": compound_defs[0], "bht": compound_defs[1], "dodecyl": compound_defs[2], "octyl": compound_defs[3]}[key]
        cid = ids[d["cid"]]
        eid = f"SB-V15-{idx:03d}"
        new_evidence_ids.append(eid)
        is_null = key == "beta" and probe.startswith("Sulfasalazine")
        evidence.append({
            "Evidence_ID": eid, "Compound": d["name"], "Compound_ID": cid, "Drug": probe,
            "Interaction_Effect": "No change detected in the permeability endpoint under tested Caco-2 conditions." if is_null else f"{d['name']} inhibited {probe} transport in vitro under the reported assay conditions.",
            "Mechanism": mechanism, "Evidence_Type": "In vitro", "Evidence_Level": "compound", "Direction": "null/no effect detected" if is_null else "inhibition in vitro",
            "Quantitative_Outcome": quant, "Dose": "See source assay; concentrations and substrate conditions are retained in the source locator; no food serving dose inferred.",
            "Population": "Human transporter or Caco-2 in-vitro system; not human participants", "Study_Design": design,
            "Source_Title": TITLE, "Authors": AUTHORS, "Year": "2025", "DOI": DOI, "PMID": PMID, "Source_Type": "Primary research",
            "Limitations": "In-vitro additive/transporter findings; no demonstrated human pharmacokinetic interaction. Caco-2 permeability endpoint was null for beta-carotene; transporter inhibition must not be converted into clinical effect.",
            "Confidence": "Primary-source in-vitro evidence; clinical relevance unestablished.", "Notes": "Food-additive material; isolated-compound experimental results do not quantify exposure from a meal.",
            "Study_ID": f"PMID:{PMID}", "Source_URL": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12406256/", "Source_Cache": "",
            "Source_Locator": locator, "Preparation": "Food additive tested as specified by article; not a whole-food matrix.", "Co_Compounds": "",
            "Affected_Entity": "transport assay", "Perpetrator": "isolated food additive", "Outcome": "null_finding" if is_null else "observed_in_vitro_effect",
            "Conflict_Group": "V15-OCTYL-GALLATE-TRANSPORTER-CONFLICT" if key == "octyl" else "", "Identity_Status": "verified_exact",
            "Release_Origin": "v15_controlled_expansion", "Clinical_Extrapolation": "No clinical extrapolation",
            "CookRisk_Exposure_Link": "Identity and in-vitro outcome only; no Stage C integration",
        })
    write("data/interaction_evidence.csv", e_h, evidence)

    b_h, bibliography = read("data/publication_bibliography.csv")
    if PMID not in {r["PMID"] for r in bibliography}:
        bibliography.append({"PMID": PMID, "Title": TITLE, "Authors": AUTHORS, "Year": "2025", "DOI": DOI, "PMCID": "PMC12406256", "Source": "PubMed/PMC primary research; full text and displayed Table 1/Figures 2–3 reviewed", "Count_Unit": "Publication", "DOI_Status": "Cross-checked in PubMed record"})
    write("data/publication_bibliography.csv", b_h, bibliography)

    s_h, studies = read("data/study_registry.csv")
    studies.append({"Study_ID": f"PMID:{PMID}", "PMID": PMID, "DOI": DOI, "Title": TITLE, "Authors": AUTHORS, "Year": "2025", "Evidence_Record_IDs": "|".join(new_evidence_ids), "Evidence_Record_Count": str(len(new_evidence_ids)), "Evidence_Classes": "In vitro", "Verification_Status": "Primary full text; Table 1 and Figures 2–3; transporter inhibition and null permeability result distinguished", "Independence": "One publication; seven compound–assay records do not represent independent clinical cohorts"})
    write("data/study_registry.csv", s_h, studies)

    p_h, probes = read("data/drug_probe_registry.csv")
    labels = [
        ("BCRP-mediated Lucifer yellow efflux", 2), ("P-glycoprotein-mediated N-methyl-quinidine efflux", 1),
        ("OATP2B1-mediated 5-carboxyfluorescein uptake", 2), ("Sulfasalazine permeability in Caco-2 cells", 1),
        ("MRP2-mediated carboxydichlorofluorescein transport", 1),
    ]
    for j, (label, count) in enumerate(labels, start=1):
        probes.append({"Drug_ID": f"PROBE-V15-{128+j:03d}", "Drug_Probe": label, "Evidence_Records": str(count), "Primary_PMIDs": PMID, "Scope": "In-vitro transporter/substrate assay label; not a therapeutic-drug interaction record"})
    write("data/drug_probe_registry.csv", p_h, probes)

    i_h, identity = read("identity/identity_structure_audit.csv")
    for d in compound_defs:
        cid = ids[d["cid"]]
        identity.append({"Compound_ID": cid, "Canonical_Name": d["name"], "PubChem_CID": d["cid"], "Returned_InChIKey": d["inchikey"], "Registry_InChIKey": d["inchikey"], "Exact_Key_Match": "True", "SMILES": d["smiles"], "InChI": d["inchi"], "Structure_Source": f"https://pubchem.ncbi.nlm.nih.gov/compound/{d['cid']}", "Status": "PubChem name/CID and returned structure identifiers cross-checked; manual review pending", "Note": "Achiral gallates/BHT; all-trans carotene geometry represented by InChI stereolayers and isomeric SMILES.", "PubChem_Name_or_Alias_Match": "True", "PubChem_Synonyms": d["aliases"]})
    write("identity/identity_structure_audit.csv", i_h, identity)

    w_h, warnings = read("data/warning_ledger.csv")
    warnings.extend([
        {"Warning_ID": "V15-W01", "Code": "BATCH_6_IN_VITRO_LIMIT", "Description": "Batch 6 additions are isolated food-additive transporter findings; no human pharmacokinetic interaction is established.", "Affected": "Batch 6 (4 compounds)", "Classification": "scientific uncertainty", "Before": "Not in V14", "Action": "Retained assay-specific outcomes and evidence limitations; avoided dietary exposure inference.", "After": "Unresolved", "Remaining_Limitations": "Clinical relevance and food-level intestinal concentrations remain unestablished.", "Resolution_Source": f"PMID:{PMID}; PubChem CID records", "Review_Date": DATE},
        {"Warning_ID": "V15-W02", "Code": "OCTYL_GALLATE_CONFLICT", "Description": "The primary article discusses conflicting transporter findings for octyl gallate and presents only a single-concentration OATP2B1 result in this study.", "Affected": "MOL-V15-CID-61253; SB-V15-007", "Classification": "conflicting evidence", "Before": "No V15 evidence", "Action": "Recorded 65% inhibition at 50 μM without assigning an IC50; authors' conflicting findings remain visible.", "After": "Unresolved", "Remaining_Limitations": "No dose-response IC50 or demonstrated clinical interaction.", "Resolution_Source": f"PMID:{PMID}", "Review_Date": DATE},
    ])
    write("data/warning_ledger.csv", w_h, warnings)

    sr_h, source_register = read("provenance/source_register.csv")
    source_register.append({"PMID": PMID, "DOI": DOI, "Compound": "; ".join(d["name"] for d in compound_defs), "Chemical_record": "; ".join(f"https://pubchem.ncbi.nlm.nih.gov/compound/{d['cid']}" for d in compound_defs), "Primary_source": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12406256/", "Access_date": DATE, "Source_limit": "In-vitro additive/transporter assays only; Caco-2 permeability null for selected compounds; no clinical DDI established. Octyl gallate findings include conflict.", "Verification_scope": "Primary full text; Table 1 and Figures 2–3; exact PubChem structure identifiers"})
    write("provenance/source_register.csv", sr_h, source_register)

    sa_h, source_audit = read("provenance/source_audit.csv")
    for idx, (key, probe, quant, mechanism, design, locator) in enumerate(evidence_specs, start=1):
        source_audit.append({"Evidence_ID": f"SB-V15-{idx:03d}", "PMID": PMID, "DOI": DOI, "Source_Title": TITLE, "Source_URL": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12406256/", "Source_Cache": "", "Source_Locator": locator, "Verification_Status": "Primary full text viewed", "Fields_Audited": "compound identity; transporter/substrate; model; direction; quantitative value/unit or null outcome; limitations", "Limitations": "In-vitro only; no human interaction established; no serving-level exposure inference."})
    write("provenance/source_audit.csv", sa_h, source_audit)

    metadata = json.loads((ROOT / "release_metadata.json").read_text(encoding="utf-8"))
    metadata.update({"release": "StageB_V15_20261102", "baseline_release": "StageB_V14_20261102", "expected_compounds": len({r["Compound_ID"] for r in compounds}), "expected_evidence": len({r["Evidence_ID"] for r in evidence}), "warning_count": len(warnings), "readiness": "PARTIAL_NOT_READY_FOR_160", "last_completed_batch": 6, "drug_probe_rows": len(probes), "bibliography_rows": len(bibliography), "unique_nonblank_PMIDs": len({r["PMID"] for r in bibliography if r["PMID"]}), "study_rows": len(studies)})
    (ROOT / "release_metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    reviews = {
        "screened": 12,
        "accepted": [{"compound": d["name"], "CID": d["cid"], "reason": f"Directly tested in primary transporter study PMID {PMID}; exact PubChem identity cross-check; assay-level result retained."} for d in compound_defs],
        "held": [
            {"candidate": "GF-I-1", "reason": "Exact entity and primary tested-material linkage were not resolved in this batch."},
            {"candidate": "GF-I-4", "reason": "Exact entity and primary tested-material linkage were not resolved in this batch."},
            {"candidate": "Paradisin B", "reason": "No direct exact-identity/primary tested-compound linkage established."},
            {"candidate": "Imperatorin", "reason": "No newly verified compound-specific food–drug interaction primary record established in this batch."},
            {"candidate": "FD&C Yellow 6", "reason": "Primary paper verified as a tested inhibitor, but exact original SI row and structure form were not independently checked in this execution; held pending direct SI review."},
            {"candidate": "FD&C Blue 1", "reason": "Original primary SI row and tested material identity not directly verified; held."},
            {"candidate": "FD&C Red 3", "reason": "Original primary SI row and tested material identity not directly verified; held."},
            {"candidate": "Neohesperidin dihydrochalcone", "reason": "Original primary SI row and tested material identity not directly verified; held."},
        ],
        "rejected": [],
        "categories": {"xanthophylls": "lutein, zeaxanthin, astaxanthin, beta-cryptoxanthin and canthaxanthin already present; beta-carotene is distinct and accepted from direct primary assay evidence.", "red_clover_isoflavones": "biochanin A, formononetin, genistein, daidzein and glycitein already present; no duplicate added.", "flavonoid_aglycones": "many covered (including quercetin, kaempferol, naringenin, apigenin); no category-level placeholder admitted.", "phytosterols": "beta-sitosterol and stigmasterol present; campesterol not added absent directly verified interaction evidence."},
    }
    (ROOT / "validation" / "V15_batch_06_candidate_decisions.json").write_text(json.dumps(reviews, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    (ROOT / "validation" / "V15_batch_06_review.md").write_text(
        "# V15 Batch 6 review\n\n"
        f"Primary source: PMID {PMID}; DOI {DOI}; full text, Table 1, and Figures 2–3 reviewed.\n\n"
        "Accepted: all-trans-beta-carotene (CID 5280489), butylated hydroxytoluene (CID 31404), dodecyl gallate (CID 14425), and octyl gallate (CID 61253). The study reports transporter inhibition in in-vitro overexpression/vesicle systems. Beta-carotene's null Caco-2 sulfasalazine permeability result is retained. Octyl gallate has conflicting transporter results; only the current study's 65% OATP2B1 inhibition at 50 μM is recorded, with no IC50 assignment. The paper concludes effects on drug permeability were negligible in the selected Caco-2 test and does not establish clinical food–drug interactions.\n\n"
        "Held: GF-I-1, GF-I-4, Paradisin B, Imperatorin, FD&C Yellow 6, FD&C Blue 1, FD&C Red 3, and neohesperidin dihydrochalcone. Held decisions are not compound rejections. Exact reasons are in `V15_batch_06_candidate_decisions.json`. The original supplementary table from the earlier OATP2B1 excipient screen was not directly checked here; no Ki from it was entered.\n\n"
        "Gate: PASS for the four additions; no human or meal-level risk inference.\n", encoding="utf-8", newline="\n")
    (ROOT / "validation" / "V15_batch_06_gate.json").write_text(json.dumps({"batch": 6, "status": "PASS_PENDING_AUTOMATED_VALIDATION", "accepted_compounds": 4, "new_evidence": len(new_evidence_ids), "screened_candidates": 12}, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
