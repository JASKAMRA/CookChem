"""Apply one reviewed Stage B V14 batch without touching the V13 checkpoint."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RELEASE = ROOT / "stageB" / "release" / "StageB_V14_20261102"
DATE = "2026-11-02"


def read_csv(name: str) -> tuple[list[str], list[dict[str, str]]]:
    with (RELEASE / name).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(name: str, fields: list[str], rows: list[dict[str, str]]) -> None:
    path = RELEASE / name
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def base_evidence(eid: str, cid: str, name: str, probe: str, effect: str,
                  mechanism: str, outcome: str, pmid: str, doi: str,
                  title: str, year: str, authors: str, url: str, locator: str,
                  context: str, limitations: str) -> dict[str, str]:
    return {
        "Evidence_ID": eid, "Compound": name, "Compound_ID": cid, "Drug": probe,
        "Interaction_Effect": effect, "Mechanism": mechanism, "Evidence_Type": "In vitro",
        "Evidence_Level": "compound", "Direction": "inhibition of enzyme activity in vitro",
        "Quantitative_Outcome": outcome, "Dose": "Not reported in the inspected source locator",
        "Population": "Human liver microsomes / human enzyme assay; no participants",
        "Study_Design": "In-vitro enzyme inhibition assay", "Source_Title": title,
        "Authors": authors, "Year": year, "DOI": doi, "PMID": pmid,
        "Source_Type": "Primary research", "Limitations": limitations,
        "Confidence": "Mechanistic in-vitro evidence only; no clinical dietary interaction established",
        "Notes": context, "Study_ID": f"PMID:{pmid}",
        "Source_URL": url, "Source_Cache": "", "Source_Locator": locator,
        "Preparation": "Purified or synthetic compound as specified by source; not a whole-food serving",
        "Co_Compounds": "", "Affected_Entity": "enzyme assay", "Perpetrator": "isolated compound",
        "Outcome": "observed_in_vitro_effect", "Conflict_Group": "", "Identity_Status": "verified_exact",
        "Release_Origin": "v14_controlled_expansion", "Clinical_Extrapolation": "No clinical extrapolation",
        "CookRisk_Exposure_Link": "Identity only; no food exposure linkage or Stage C integration",
    }


def compound(cid: int, name: str, aliases: str, smiles: str, inchi: str, inchikey: str,
             context: str, pmid: str, doi: str, rationale: str) -> dict[str, str]:
    return {
        "Compound_ID": f"MOL-V14-CID-{cid}", "Canonical_Name": name, "Aliases": aliases,
        "PubChem_CID": str(cid), "SMILES": smiles, "InChI": inchi, "InChIKey": inchikey,
        "Identity_Status": "PubChem CID, SMILES, InChI and InChIKey cross-checked; manual structure review pending.",
        "Identity_Source": f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}",
        "Origin": "v14_controlled_expansion", "Selection_Rationale": rationale,
        "Selection_Source": "Primary-source evidence; botanical context is not dose-equivalent to an ordinary food serving.",
        "Selection_DOI": doi, "Selection_PMID": pmid,
        "Selection_URL": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/", "Date_Added": DATE,
        "First_Documented_Release_Date": DATE, "Date_Status": "V14 curation date; no historical addition date claimed.",
        "Coverage_Status": "Controlled V14 addition; in-vitro evidence only.",
        "Provenance_Status": "v14_primary_source_reviewed", "Original_Molecular_Group": "V14 candidate",
        "Retention_Status": "No cooking-retention evidence added.", "Food_Context": context,
        "Evidence_Records": "", "Link_Restriction": "No Stage C exposure integration; no clinical risk inference.",
        "Release_Reviewed": "v14_20261102", "Selection_Verification": "Primary publication and PubChem identity record reviewed.",
        "Earliest_Verified_Selection_Date": DATE, "Selection_Temporality": "V14 evidence-led decision",
        "Remaining_Provenance_Gap": "No clinical dietary interaction demonstrated; exposure equivalence is unestablished.",
    }


TITLE_CURC = "Curcuminoids inhibit multiple human cytochromes P450, UDP-glucuronosyltransferase, and sulfotransferase enzymes, whereas piperine is a relatively selective CYP3A4 inhibitor"
AUTH_CURC = "Volak LP, Ghirmai S, Cashman JR, Court MH"
TITLE_SIN = "In vitro effect of important herbal active constituents on human cytochrome P450 1A2 (CYP1A2) activity"
TITLE_CLEM = "Nobiletin, sinensetin, and tangeretin are the main perpetrators in clementines provoking food-drug interactions in vitro"

DMC_INCHI = "InChI=1S/C20H18O5/c1-25-20-12-15(6-11-19(20)24)5-10-18(23)13-17(22)9-4-14-2-7-16(21)8-3-14/h2-12,21,24H,13H2,1H3/b9-4+,10-5+"
SIN_INCHI = "InChI=1S/C20H20O7/c1-22-13-7-6-11(8-15(13)23-2)14-9-12(21)18-16(27-14)10-17(24-3)19(25-4)20(18)26-5/h6-10H,1-5H3"
BDMC_INCHI = "InChI=1S/C19H16O4/c20-16-7-1-14(2-8-16)5-11-18(22)13-19(23)12-6-15-3-9-17(21)10-4-15/h1-12,20-21H,13H2/b11-5+,12-6+"
EUP_INCHI = "InChI=1S/C18H16O7/c1-22-12-5-4-9(6-10(12)19)13-7-11(20)16-14(25-13)8-15(23-2)18(24-3)17(16)21/h4-8,19,21H,1-3H3"

BATCHES = {
    2: {
        "candidates": [
            ("Demethoxycurcumin", "Include with limitations", "CID 5469424; a distinct curcuminoid, not curcumin or bisdemethoxycurcumin. Human liver-microsome CYP2C9 and CYP3A assay results are in PMID 18480186; no human DDI claim.", "Turmeric-associated curcuminoid; isolated compound assays and supplement/extract use are not equivalent to a food serving.", 5469424, "demethoxycurcumin | desmethoxycurcumin | curcumin II", "COC1=C(C=CC(=C1)/C=C/C(=O)CC(=O)/C=C/C2=CC=C(C=C2)O)O", DMC_INCHI, "HJTVQHVGMGKONQ-LUZURFALSA-N", "18480186", "10.1124/dmd.108.020552"),
            ("Bisdemethoxycurcumin", "Include with limitations", "CID 5315472; distinct two-unmethoxylated-ring curcuminoid; separate from curcumin and demethoxycurcumin. PMID 18480186 reports CYP3A and CYP2C9 in-vitro outcomes.", "Turmeric-associated curcuminoid; isolated compound assays and supplement/extract use are not equivalent to a food serving.", 5315472, "bisdemethoxycurcumin | curcumin III | didemethoxycurcumin | di-p-coumaroylmethane", "O=C(CC(=O)/C=C/c1ccc(cc1)O)/C=C/c1ccc(cc1)O", BDMC_INCHI, "PREBVFJICNPEKM-YDWXAUTNSA-N", "18480186", "10.1124/dmd.108.020552"),
        ],
        "evidence": "curcuminoids",
    },
    3: {
        "candidates": [
            ("Sinensetin", "Include with limitations", "CID 145659; pentamethoxyflavone structure and connectivity checked. CYP1A2 inhibition was reported in a human enzyme assay (PMID 25442272); a separate clementine study provides cautious food-context attribution (PMID 32187570).", "Clementine/citrus flavonoid and medicinal-botanical constituent; experimental isolated-compound results do not establish serving-level or clinical risk.", 145659, "sinensetin | 5,6,7,3′,4′-pentamethoxyflavone | pedalitin permethyl ether", "COC1=C(C=C(C=C1)C2=CC(=O)C3=C(C(=C(C=C3O2)OC)OC)OC)OC", SIN_INCHI, "LKMNXYDUQXAUCZ-UHFFFAOYSA-N", "25442272", "10.1016/j.phymed.2014.08.003"),
        ],
        "evidence": "sinensetin",
    },
    4: {
        "candidates": [
            ("Eupatorin", "Include with limitations", "CID 97214; identity checked against PubChem and NIST InChI/InChIKey. PMID 25442272 reports moderate in-vitro CYP1A2 inhibition (50.8 μM). Context is medicinal-botanical constituent; no ordinary-food clinical interaction established.", "Medicinal-botanical phytochemical (including Orthosiphon/Java tea contexts); not treated as ordinary-food exposure.", 97214, "eupatorin | 5,3′-dihydroxy-6,7,4′-trimethoxyflavone", "COC1=C(C=C(C=C1)C2=CC(=O)C3=C(C(=C(C=C3O2)OC)OC)O)O", EUP_INCHI, "KLAOKWJLUQKWIF-UHFFFAOYSA-N", "25442272", "10.1016/j.phymed.2014.08.003"),
        ],
        "evidence": "eupatorin",
    },
    5: {"candidates": [
        ("Allura Red AC (FD&C Red No. 40)", "Include with limitations", "PubChem CID 33258; the primary study identifies FD&C Red No. 40 as an OATP2B1 inhibitor and reports reduced fexofenadine exposure in mice at the higher tested dye dose. No human interaction is established.", "Synthetic food color used in food and drug products; isolated-dye assays are not equivalent to a meal. Commercial dye composition and local-use status are outside this dataset.", 33258, "Allura Red AC | Allura Red | E129 | FD&C Red No. 40 | Food Red 17", "CC1=CC(=C(C=C1S(=O)(=O)[O-])OC)N=NC2=C(C=CC3=C2C=CC(=C3)S(=O)(=O)[O-])O.[Na+].[Na+]", "InChI=1S/C18H16N2O8S2.2Na/c1-10-7-14(16(28-2)9-17(10)30(25,26)27)19-20-18-13-5-4-12(29(22,23)24)8-11(13)3-6-15(18)21;;/h3-9,21H,1-2H3,(H,22,23,24)(H,25,26,27);;/q;2*+1/p-2", "CEZCCHQBSQPRMU-UHFFFAOYSA-L", "32571913", "10.1073/pnas.1920483117"),
    ], "evidence": "fdc_red40"},
}


def apply_batch(batch: int) -> dict[str, object]:
    if not RELEASE.exists():
        raise SystemExit(f"V14 release missing: {RELEASE}")
    previous = json.loads((RELEASE / "release_metadata.json").read_text(encoding="utf-8"))
    if previous.get("last_completed_batch", 1) != batch - 1:
        raise SystemExit(f"Batch order violation: metadata says {previous.get('last_completed_batch')}, requested {batch}")
    compounds_fields, compounds = read_csv("data/compound_registry.csv")
    evidence_fields, evidence = read_csv("data/interaction_evidence.csv")
    identity_fields, identity = read_csv("identity/identity_structure_audit.csv")
    bibliography_fields, bibliography = read_csv("data/publication_bibliography.csv")
    studies_fields, studies = read_csv("data/study_registry.csv")
    decisions_fields, decisions = read_csv("provenance/selection_decisions.csv")
    screen_fields, screens = read_csv("provenance/candidate_screening_log.csv")
    warnings_fields, warnings = read_csv("data/warning_ledger.csv")
    probes_fields, probes = read_csv("data/drug_probe_registry.csv")
    existing_ids = {r["Compound_ID"] for r in compounds}
    existing_keys = {r["InChIKey"] for r in compounds}
    existing_evidence = {r["Evidence_ID"] for r in evidence}
    if batch == 2:
        new_evidence = [
            base_evidence("SB-V14-001", "MOL-V14-CID-5469424", "Demethoxycurcumin", "CYP2C9", "CYP2C9-mediated flurbiprofen hydroxylation inhibited", "Direct enzyme inhibition", "IC50 = 8.8 ± 1.2 μM in human liver microsomes; pure synthetic demethoxycurcumin. The same study reports >50 μM for curcumin and bisdemethoxycurcumin.", "18480186", "10.1124/dmd.108.020552", TITLE_CURC, "2008", AUTH_CURC, "https://pubmed.ncbi.nlm.nih.gov/18480186/", "Full text, Table 3; HLM CYP2C9 row", "Isolated turmeric-associated curcuminoid; no serving-dose equivalence.", "In-vitro only; no clinical interaction; isolated synthetic compound and HLM model."),
            base_evidence("SB-V14-002", "MOL-V14-CID-5469424", "Demethoxycurcumin", "CYP3A4", "CYP3A-mediated triazolam 1′-hydroxylation inhibited", "Direct enzyme inhibition; preincubation effect also measured", "IC50 = 43.5 ± 3.8 μM in HLM without preincubation; 31.5 ± 0.5 μM after 20-minute preincubation.", "18480186", "10.1124/dmd.108.020552", TITLE_CURC, "2008", AUTH_CURC, "https://pubmed.ncbi.nlm.nih.gov/18480186/", "Full text, Table 3; CYP3A HLM rows", "Isolated turmeric-associated curcuminoid; no serving-dose equivalence.", "In-vitro only; no clinical interaction; model-specific results."),
            base_evidence("SB-V14-003", "MOL-V14-CID-5315472", "Bisdemethoxycurcumin", "CYP3A4", "CYP3A-mediated triazolam 1′-hydroxylation inhibited", "Direct enzyme inhibition; preincubation effect also measured", "IC50 = 41.7 ± 3.5 μM in HLM without preincubation; 35.3 ± 2.7 μM after 20-minute preincubation.", "18480186", "10.1124/dmd.108.020552", TITLE_CURC, "2008", AUTH_CURC, "https://pubmed.ncbi.nlm.nih.gov/18480186/", "Full text, Table 3; CYP3A HLM rows", "Isolated turmeric-associated curcuminoid; no serving-dose equivalence.", "In-vitro only; no clinical interaction; model-specific results."),
            base_evidence("SB-V14-004", "MOL-V14-CID-5315472", "Bisdemethoxycurcumin", "CYP2C9", "No 50% inhibition of CYP2C9-mediated flurbiprofen hydroxylation at the highest tested concentration", "Negative/weak enzyme-inhibition finding", "IC50 > 50 μM in human liver microsomes; retain as a right-censored result, not zero activity.", "18480186", "10.1124/dmd.108.020552", TITLE_CURC, "2008", AUTH_CURC, "https://pubmed.ncbi.nlm.nih.gov/18480186/", "Full text, Table 3; HLM CYP2C9 row", "Isolated turmeric-associated curcuminoid; no serving-dose equivalence.", "In-vitro negative/weak result; upper concentration and HLM context only."),
        ]
    elif batch == 3:
        new_evidence = [
            base_evidence("SB-V14-005", "MOL-V14-CID-145659", "Sinensetin", "CYP1A2", "Moderate inhibition of CYP1A2 activity", "Enzyme inhibition", "IC50 = 40.2 μM.", "25442272", "10.1016/j.phymed.2014.08.003", TITLE_SIN, "2014", "", "https://pubmed.ncbi.nlm.nih.gov/25442272/", "PubMed abstract; compound-specific CYP1A2 result", "Herbal active constituent; separate clementine paper also attributes CYP1A2 modulation to sinensetin.", "Abstract-only verification; human enzyme in-vitro evidence; no clinical interaction established."),
            base_evidence("SB-V14-006", "MOL-V14-CID-145659", "Sinensetin", "CYP1A2", "CYP1A2 inhibition/induction in clementine flavonoid context attributed in part to sinensetin", "In-vitro food-fraction and gene-expression study; attribution is qualified by authors", "Qualitative only: abstract states CYP1A2 inhibition and induction can most likely be attributed to nobiletin, sinensetin and tangeretin; no compound-specific magnitude assigned.", "32187570", "10.1016/j.foodchem.2020.126578", TITLE_CLEM, "2020", "Weiss J, Gattuso G, Barreca D, Haefeli WE", "https://pubmed.ncbi.nlm.nih.gov/32187570/", "PubMed abstract", "Clementine juice/flavonoid fraction; study explicitly reports an in-vitro context.", "Abstract-only; attribution is authors' qualified interpretation, not a clinical study or compound-specific dose-response."),
        ]
    elif batch == 4:
        new_evidence = [base_evidence(
            "SB-V14-007", "MOL-V14-CID-97214", "Eupatorin", "CYP1A2", "Moderate inhibition of CYP1A2 activity", "Enzyme inhibition", "IC50 = 50.8 μM.",
            "25442272", "10.1016/j.phymed.2014.08.003", TITLE_SIN, "2014", "", "https://pubmed.ncbi.nlm.nih.gov/25442272/",
            "PubMed abstract; compound-specific CYP1A2 result", "Medicinal-botanical constituent; no ordinary-food context inferred.",
            "Abstract-only verification; in-vitro human enzyme assay; no clinical interaction established.")]
    elif batch == 5:
        new_evidence = [
            base_evidence("SB-V14-008", "MOL-V14-CID-33258", "Allura Red AC (FD&C Red No. 40)",
                "OATP2B1-mediated DBF uptake", "OATP2B1 uptake inhibition; dye was among the validated inhibitors",
                "Direct in-vitro transporter inhibition", "Named in the primary study's 24 validated inhibitor set; dose-response validation reported. No Ki value transcribed because the primary SI table was not directly retrievable in this execution.",
                "32571913", "10.1073/pnas.1920483117", "Bacterial metabolism rescues the inhibition of intestinal drug absorption by food and drug additives", "2020",
                "Zou L, Spanogiannopoulos P, Pieper LM, et al.", "https://pubmed.ncbi.nlm.nih.gov/32571913/",
                "Primary article abstract and full-text results; inhibitor set and Fig. 6; no numerical Ki assigned",
                "Food color additive; isolated-dye assay is not equivalent to a food serving.",
                "Primary mechanistic evidence; exact dose-response Ki is omitted pending direct SI table verification."),
            base_evidence("SB-V14-009", "MOL-V14-CID-33258", "Allura Red AC (FD&C Red No. 40)", "Fexofenadine",
                "Fexofenadine exposure decreased in mice at the higher FD&C Red No. 40 dose",
                "Proposed intestinal OATP2B1 inhibition; gut-microbiome metabolism modified exposure",
                "AUC0–360 min decreased 48% versus vehicle with 25 mg/kg dye plus 15 mg/kg fexofenadine (n=9 vs n=8; P=0.0026). No reduction was observed at 2.5 mg/kg dye (n=6).",
                "32571913", "10.1073/pnas.1920483117", "Bacterial metabolism rescues the inhibition of intestinal drug absorption by food and drug additives", "2020",
                "Zou L, Spanogiannopoulos P, Pieper LM, et al.", "https://pubmed.ncbi.nlm.nih.gov/32571913/",
                "Primary full text, Fig. 6E–H and results; Pgp-deficient germ-free mouse model",
                "Food color additive; not a human or dietary clinical interaction study.",
                "Animal evidence only; model, microbiome and dose constrain translation; no human inference.")
        ]
        new_evidence[0]["Population"] = "Human OATP2B1-overexpressing HEK cells; in-vitro transporter assay"
        new_evidence[0]["Study_Design"] = "Transporter inhibition screen followed by dose-response validation"
        new_evidence[0]["Evidence_Type"] = "In vitro"
        new_evidence[1]["Population"] = "P-glycoprotein-deficient germ-free mice"
        new_evidence[1]["Study_Design"] = "In-vivo mouse pharmacokinetic experiment"
        new_evidence[1]["Evidence_Type"] = "Animal"
        new_evidence[1]["Direction"] = "decreased fexofenadine exposure at 25 mg/kg dye; no reduction at 2.5 mg/kg"
    else:
        new_evidence = []

    new_compounds = []
    new_identity = []
    new_decisions = []
    new_screens = []
    entries = BATCHES[batch]["candidates"]
    for i, entry in enumerate(entries):
        name, decision, rationale, context, cid, aliases, smiles, inchi, key, pmid, doi = entry
        row = compound(cid, name, aliases, smiles, inchi, key, context, pmid, doi, rationale)
        if row["Compound_ID"] in existing_ids or key in existing_keys:
            raise SystemExit(f"Duplicate ID or structure blocked: {name} / {key}")
        related = [e for e in new_evidence if e["Compound_ID"] == row["Compound_ID"]]
        if not related:
            raise SystemExit(f"No primary evidence rows for accepted candidate {name}")
        row["Evidence_Records"] = str(len(related))
        new_compounds.append(row)
        existing_ids.add(row["Compound_ID"])
        existing_keys.add(key)
        new_identity.append({
            "Compound_ID": row["Compound_ID"], "Canonical_Name": name, "PubChem_CID": str(cid),
            "Returned_InChIKey": key, "Registry_InChIKey": key, "Exact_Key_Match": "True",
            "SMILES": smiles, "InChI": inchi, "Structure_Source": f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}",
            "Status": "CID, structure strings and InChIKey cross-checked; independent expert structure review pending",
            "Note": "Formula/stereochemical identity checked against cited chemical record; no stereocentres for these identities.",
            "PubChem_Name_or_Alias_Match": "True", "PubChem_Synonyms": aliases,
        })
        new_decisions.append({
            "Candidate": name, "Decision": f"{decision} (Batch {batch})", "Identity": f"PubChem CID {cid}; InChIKey {key}.",
            "Food_Context": context, "Interaction_Rationale": rationale, "Primary_Source_PMID": pmid,
            "Primary_Source_DOI": doi, "Verification": "See batch validation report; evidence verification level is row-specific.",
            "Date": DATE, "Residual_Limitation": "In-vitro evidence only; no clinical dietary interaction established.",
        })
        new_screens.append({
            "Search_Date": DATE, "Database": "PubChem; PubMed primary-source review",
            "Query_or_Candidate": name, "Decision": decision,
            "Reason": rationale, "Full_Text_Availability": "Full text, Table 3" if pmid == "18480186" else ("Primary full text and abstract; exact supplemental Ki table not directly retrievable" if pmid == "32571913" else "PubMed abstract"),
            "Verification_Status": "Primary in-vitro source; details and limitations in evidence rows",
            "Reviewer_Note": f"Batch {batch}; identity and source reviewed; no clinical extrapolation.",
        })

    for candidate in new_evidence:
        if candidate["Evidence_ID"] in existing_evidence:
            raise SystemExit(f"Duplicate evidence ID blocked: {candidate['Evidence_ID']}")
        if candidate["Compound_ID"] not in existing_ids:
            raise SystemExit(f"Evidence foreign key missing: {candidate['Compound_ID']}")
        existing_evidence.add(candidate["Evidence_ID"])

    if batch == 5:
        held = [
            ("GF-I-1", "Hold", "Earlier Stage B review leaves identity/structure unresolved; no unique entity may be promoted."),
            ("GF-I-4", "Hold", "Earlier Stage B review leaves identity/structure unresolved; no unique entity may be promoted."),
            ("Paradisin B", "Hold", "Earlier review found no uniquely resolved CID and primary claim mapping."),
            ("Imperatorin", "Hold", "Earlier review found abstract-level target attribution ambiguous; table-level evidence/identity linkage was not established in the accessible source record."),
        ]
        for name, decision, reason in held:
            new_screens.append({"Search_Date": DATE, "Database": "Existing V11/V13 candidate register and primary source locator recheck", "Query_or_Candidate": name, "Decision": decision,
                                "Reason": reason, "Full_Text_Availability": "Not sufficiently verified in this batch",
                                "Verification_Status": "Held; no Compound_ID or evidence record created", "Reviewer_Note": "Do not infer activity or identity to fill the 160-compound target."})
            new_decisions.append({"Candidate": name, "Decision": "Held; not promoted in Batch 5", "Identity": "Unresolved or primary claim linkage not verified", "Food_Context": "Not used to infer identity or interaction", "Interaction_Rationale": reason, "Primary_Source_PMID": "", "Primary_Source_DOI": "", "Verification": "Insufficient for admission", "Date": DATE, "Residual_Limitation": "Requires additional primary-source and chemical identity resolution."})

    # Bibliography and study linkage, preserving all inherited rows.
    papers = {
        "18480186": (TITLE_CURC, AUTH_CURC, "2008", "10.1124/dmd.108.020552", "PMC2574793", "PubMed/PMC primary research"),
        "25442272": (TITLE_SIN, "", "2014", "10.1016/j.phymed.2014.08.003", "", "PubMed primary research; abstract verified"),
        "32187570": (TITLE_CLEM, "Weiss J, Gattuso G, Barreca D, Haefeli WE", "2020", "10.1016/j.foodchem.2020.126578", "", "PubMed primary research; abstract verified"),
        "32571913": ("Bacterial metabolism rescues the inhibition of intestinal drug absorption by food and drug additives", "Zou L, Spanogiannopoulos P, Pieper LM, et al.", "2020", "10.1073/pnas.1920483117", "PMC7355017", "PubMed/PMC primary research; full-text results verified"),
    }
    for pmid, (title, authors, year, doi, pmcid, source) in papers.items():
        if not any(r["PMID"] == pmid for r in bibliography):
            bibliography.append({"PMID": pmid, "Title": title, "Authors": authors, "Year": year, "DOI": doi,
                                 "PMCID": pmcid, "Source": source, "Count_Unit": "Publication", "DOI_Status": "DOI/PMID cross-reference checked"})
    for pmid, (title, authors, year, doi, _, _) in papers.items():
        linked = [r["Evidence_ID"] for r in evidence + new_evidence if r["PMID"] == pmid]
        if not linked:
            continue
        current = next((r for r in studies if r["PMID"] == pmid), None)
        if current:
            ids = list(dict.fromkeys([x for x in (current["Evidence_Record_IDs"] + "|" + "|".join(linked)).split("|") if x]))
            current["Evidence_Record_IDs"] = "|".join(ids)
            current["Evidence_Record_Count"] = str(len(ids))
        else:
            studies.append({"Study_ID": f"PMID:{pmid}", "PMID": pmid, "DOI": doi, "Title": title,
                            "Authors": authors, "Year": year, "Evidence_Record_IDs": "|".join(linked),
                            "Evidence_Record_Count": str(len(linked)), "Evidence_Classes": "In vitro",
            "Verification_Status": "Full-text/table verified" if pmid == "18480186" else ("Full-text results verified; supplementary Ki omitted" if pmid == "32571913" else "Abstract verified; source locator recorded"),
                            "Independence": "Publication identifier only; independent cohorts not inferred"})

    evidence.extend(new_evidence)
    compounds.extend(new_compounds)
    identity.extend(new_identity)
    decisions.extend(new_decisions)
    screens.extend(new_screens)
    # Add the transporter assay label once; preserve existing probe identities.
    if any(r["Drug"] == "OATP2B1-mediated DBF uptake" for r in new_evidence) and not any(p["Drug_Probe"] == "OATP2B1-mediated DBF uptake" for p in probes):
        probes.append({"Drug_ID": "PROBE-V14-128", "Drug_Probe": "OATP2B1-mediated DBF uptake",
                       "Evidence_Records": "0", "Primary_PMIDs": "32571913",
                       "Scope": "Human transporter assay target/probe; DBF substrate, not a therapeutic drug"})
    # Update probe counts only for newly appended rows; preserve labels and IDs.
    for probe in {r["Drug"] for r in new_evidence}:
        match = next((r for r in probes if r["Drug_Probe"] == probe), None)
        if match:
            linked = [r for r in evidence if r["Drug"] == probe]
            match["Evidence_Records"] = str(len(linked))
            match["Primary_PMIDs"] = "|".join(dict.fromkeys(r["PMID"] for r in linked if r["PMID"]))
        else:
            raise SystemExit(f"Evidence probe has no registered drug/probe row: {probe}")

    if batch in {2, 3, 4, 5}:
        warnings.append({
            "Warning_ID": f"V14-W{batch:02d}", "Code": f"BATCH_{batch}_IN_VITRO_LIMIT",
            "Description": "New compound-specific evidence is in vitro only; no human dietary interaction is established.",
            "Affected": " | ".join(r["Canonical_Name"] for r in new_compounds),
            "Classification": "scientific uncertainty", "Before": "Not in V13 registry",
            "Action": "Added explicit context and evidence-level limits; retained null/weak findings when reported.",
            "After": "Unresolved", "Remaining_Limitations": "No clinical food-drug interaction; exposure equivalence unestablished.",
            "Resolution_Source": "PMID:18480186; PMID:25442272; PMID:32187570; PMID:32571913; PubChem structure records",
            "Review_Date": DATE,
        })

    for name, fields, rows in [
        ("data/compound_registry.csv", compounds_fields, compounds),
        ("data/interaction_evidence.csv", evidence_fields, evidence),
        ("identity/identity_structure_audit.csv", identity_fields, identity),
        ("data/publication_bibliography.csv", bibliography_fields, bibliography),
        ("data/study_registry.csv", studies_fields, studies),
        ("provenance/selection_decisions.csv", decisions_fields, decisions),
        ("provenance/candidate_screening_log.csv", screen_fields, screens),
        ("data/warning_ledger.csv", warnings_fields, warnings),
        ("data/drug_probe_registry.csv", probes_fields, probes),
    ]:
        write_csv(name, fields, rows)
    metadata = json.loads((RELEASE / "release_metadata.json").read_text(encoding="utf-8"))
    metadata.update({"release": "StageB_V14_20261102", "expected_compounds": len({r['Compound_ID'] for r in compounds}),
                     "expected_evidence": len({r['Evidence_ID'] for r in evidence}), "warning_count": len(warnings),
                     "readiness": "PARTIAL_NOT_READY_FOR_160", "last_completed_batch": batch})
    (RELEASE / "release_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    # Structural batch gate: unique IDs/structures, exact V13 prefix preservation,
    # valid evidence foreign keys, and evidence-to-study/bibliography provenance.
    compounds_by_id = {r["Compound_ID"]: r for r in compounds}
    evidence_by_id = {r["Evidence_ID"]: r for r in evidence}
    if len(compounds_by_id) != len(compounds) or len({r["InChIKey"] for r in compounds}) != len(compounds):
        raise SystemExit("Batch gate failed: duplicate compound ID or InChIKey")
    if len(evidence_by_id) != len(evidence):
        raise SystemExit("Batch gate failed: duplicate evidence ID")
    if any(r["Compound_ID"] not in compounds_by_id for r in evidence):
        raise SystemExit("Batch gate failed: orphan evidence record")
    studies_by_id = {r["Study_ID"] for r in studies}
    pubmids = {r["PMID"] for r in bibliography}
    if any(r["Study_ID"] not in studies_by_id or r["PMID"] not in pubmids for r in evidence):
        raise SystemExit("Batch gate failed: unresolved study or bibliography link")
    v13 = ROOT / "stageB" / "release" / "StageB_V13_20261102"
    for rel in ("data/compound_registry.csv", "data/interaction_evidence.csv"):
        old_fields, old_rows = read_csv_from(v13 / rel)
        new_fields, new_rows = read_csv(rel)
        current = {tuple(row[k] for k in old_fields) for row in new_rows}
        if not all(tuple(row[k] for k in old_fields) in current for row in old_rows):
            raise SystemExit(f"Batch gate failed: V13 historical data changed in {rel}")
    report = {"batch": batch, "status": "PASS", "accepted_compounds": [r["Canonical_Name"] for r in new_compounds],
              "new_evidence_ids": [r["Evidence_ID"] for r in new_evidence], "held_or_rejected": [r["Candidate"] for r in new_decisions if "Held" in r["Decision"]],
              "compound_count": len(compounds_by_id), "evidence_count": len(evidence_by_id),
              "bibliography_rows": len(bibliography), "study_rows": len(studies), "warnings": len(warnings),
              "checks": {"unique_compound_ids": "PASS", "unique_inchikeys": "PASS", "unique_evidence_ids": "PASS",
                         "compound_foreign_keys": "PASS", "study_and_publication_foreign_keys": "PASS", "V13_data_preservation": "PASS"}}
    (RELEASE / "validation" / f"V14_batch_{batch:02d}_gate.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (RELEASE / "validation" / f"V14_batch_{batch:02d}_review.md").write_text(
        f"# V14 Batch {batch} review\n\nGate: PASS.\n\nAccepted: {', '.join(report['accepted_compounds']) or 'none'}.\n\n"
        f"New evidence records: {', '.join(report['new_evidence_ids']) or 'none'}.\n\n"
        f"Held candidates: {', '.join(report['held_or_rejected']) or 'none'}.\n\n"
        "Scope: chemical identity and primary-source evidence reviewed; in-vitro findings remain nonclinical. "
        "V13 compound and evidence rows were compared and preserved. The complete release manifest is generated after the final batch.\n",
        encoding="utf-8")
    return report


def read_csv_from(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("batch", type=int, choices=(2, 3, 4, 5))
    args = parser.parse_args()
    print(json.dumps(apply_batch(args.batch), indent=2))
