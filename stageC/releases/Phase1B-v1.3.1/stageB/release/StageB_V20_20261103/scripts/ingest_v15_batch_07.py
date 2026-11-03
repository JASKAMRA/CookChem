"""Controlled ingestion of four directly tested Caco-2 null findings."""
from __future__ import annotations
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-11-02"
PMID = "40773056"
DOI = "10.1021/acs.molpharmaceut.5c00705"
TITLE = "Food Additives Inhibit Intestinal Drug Transporters but Have Limited Effect on In Vitro Drug Permeability"
AUTHORS = "Suominen L, Stenberg E, Sjöstedt N, Kidron H"
URL = "https://pmc.ncbi.nlm.nih.gov/articles/PMC12406256/"

def read(rel):
    with (ROOT / rel).open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f); return list(r.fieldnames), list(r)

def write(rel, headers, rows):
    with (ROOT / rel).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore", lineterminator="\n")
        w.writeheader(); w.writerows(rows)

def main():
    defs = [
      {"name":"Brilliant Blue FCF", "cid":"19700", "aliases":"FD&C Blue No. 1 | Erioglaucine disodium salt | Blue 1", "smiles":"CCN(CC1=CC(=CC=C1)S(=O)(=O)[O-])C2=CC=C(C=C2)C(=C3C=CC(=[N+](CC)CC4=CC(=CC=C4)S(=O)(=O)[O-])C=C3)C5=CC=CC=C5S(=O)(=O)[O-].[Na+].[Na+]", "inchi":"InChI=1S/C37H36N2O9S3.2Na/c1-3-38(25-27-9-7-11-33(23-27)49(40,41)42)31-19-15-29(16-20-31)37(35-13-5-6-14-36(35)51(46,47)48)30-17-21-32(22-18-30)39(4-2)26-28-10-8-12-34(24-28)50(43,44)45;;/h5-24H,3-4,25-26H2,1-2H3,(H2-,40,41,42,43,44,45,46,47,48);;/q;2*+1/p-2", "key":"SGHZXLIDFTYFHQ-UHFFFAOYSA-L", "ctx":"Food color additive; direct Caco-2 result only; tested at 200 μM."},
      {"name":"Azorubine (carmoisine)", "cid":"19118", "aliases":"Carmoisine | E122 | C.I. Food Red 3 | disodium azorubine", "smiles":"C1=CC=C2C(=C1)C(=CC=C2S(=O)(=O)[O-])N=NC3=C(C4=CC=CC=C4C(=C3)S(=O)(=O)[O-])O.[Na+].[Na+]", "inchi":"InChI=1S/C20H14N2O7S2.2Na/c23-20-15-8-4-3-7-14(15)19(31(27,28)29)11-17(20)22-21-16-9-10-18(30(24,25)26)13-6-2-1-5-12(13)16;;/h1-11,23H,(H,24,25,26)(H,27,28,29);;/q;2*+1/p-2", "key":"YSVBPNGJESBVRM-UHFFFAOYSA-L", "ctx":"Food color additive; direct Caco-2 result only; tested at 200 μM."},
      {"name":"Neohesperidin dihydrochalcone", "cid":"30231", "aliases":"NHDC | Neohesperidin DC | neohesperidin dihydrochalcone", "smiles":"C[C@H]1[C@@H]([C@H]([C@H]([C@@H](O1)O[C@@H]2[C@H]([C@@H]([C@H](O[C@H]2OC3=CC(=C(C(=C3)O)C(=O)CCC4=CC(=C(C=C4)OC)O)O)CO)O)O)O)O)O", "inchi":"InChI=1S/C28H36O15/c1-11-21(34)23(36)25(38)27(40-11)43-26-24(37)22(35)19(10-29)42-28(26)41-13-8-16(32)20(17(33)9-13)14(30)5-3-12-4-6-18(39-2)15(31)7-12/h4,6-9,11,19,21-29,31-38H,3,5,10H2,1-2H3/t11-,19+,21-,22+,23+,24-,25+,26+,27-,28+/m0/s1", "key":"ITVGXXMINPYUHD-CUVHLRMHSA-N", "ctx":"Food sweetener additive; distinguish NHDC from neohesperidin; direct Caco-2 result at 100 μM."},
      {"name":"Tartrazine", "cid":"164825", "aliases":"FD&C Yellow No. 5 | Yellow 5 | E102 | trisodium tartrazine", "smiles":"C1=CC(=CC=C1N=NC2C(=NN(C2=O)C3=CC=C(C=C3)S(=O)(=O)[O-])C(=O)[O-])S(=O)(=O)[O-].[Na+].[Na+].[Na+]", "inchi":"InChI=1S/C16H12N4O9S2.3Na/c21-15-13(18-17-9-1-5-11(6-2-9)30(24,25)26)14(16(22)23)19-20(15)10-3-7-12(8-4-10)31(27,28)29;;;/h1-8,13H,(H,22,23)(H,24,25,26)(H,27,28,29);;;/q;3*+1/p-3", "key":"UJMBCXLDXJUMFB-UHFFFAOYSA-K", "ctx":"Food color additive; direct Caco-2 result only; tested at 200 μM."},
    ]
    ch, compounds = read("data/compound_registry.csv")
    existing_cids={r["PubChem_CID"] for r in compounds}; existing_keys={r["InChIKey"] for r in compounds}
    for d in defs:
        if d["cid"] in existing_cids or d["key"] in existing_keys: raise SystemExit("Batch 7 contains an existing CID or structure key")
    ids={}
    for d in defs:
        cid=d["cid"]; mid=f"MOL-V15-CID-{cid}"; ids[cid]=mid
        compounds.append({"Compound_ID":mid,"Canonical_Name":d["name"],"Aliases":d["aliases"],"PubChem_CID":cid,"SMILES":d["smiles"],"InChI":d["inchi"],"InChIKey":d["key"],"Identity_Status":"PubChem CID, name, salt form, InChI, InChIKey and isomeric SMILES cross-checked; independent structure parser not available.","Identity_Source":f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}","Origin":"v15_controlled_expansion","Selection_Rationale":f"Directly included among the seven additives tested for sulfasalazine permeability in PMID {PMID}; the null result is retained without inferring clinical absence of interaction.","Selection_Source":"Primary research; food-additive context; Caco-2 permeability only.","Selection_DOI":DOI,"Selection_PMID":PMID,"Selection_URL":URL,"Date_Added":DATE,"First_Documented_Release_Date":DATE,"Date_Status":"V15 curation date; no prior selection date claimed.","Coverage_Status":"Controlled V15 addition; Caco-2 null finding only.","Provenance_Status":"v15_primary_source_reviewed","Original_Molecular_Group":"V15 batch 7 food additive","Retention_Status":"No cooking-retention evidence added.","Food_Context":d["ctx"],"Evidence_Records":"1","Link_Restriction":"No Stage C integration; no human clinical risk inference.","Release_Reviewed":"v15_20261102","Selection_Verification":"Primary full text and Figure 3 reviewed; PubChem identity record reviewed.","Earliest_Verified_Selection_Date":DATE,"Selection_Temporality":"V15 evidence-led decision","Remaining_Provenance_Gap":"Test formulation and food-level exposure are not quantified in this evidence record."})
    write("data/compound_registry.csv",ch,compounds)

    eh, ev = read("data/interaction_evidence.csv"); new=[]
    for idx,d in enumerate(defs,start=8):
        eid=f"SB-V15-{idx:03d}"; new.append(eid); dose="100 μM" if d["cid"]=="30231" else "200 μM"
        ev.append({"Evidence_ID":eid,"Compound":d["name"],"Compound_ID":ids[d["cid"]],"Drug":"Sulfasalazine permeability in Caco-2 cells","Interaction_Effect":"No effect on sulfasalazine permeability detected under the tested Caco-2 conditions.","Mechanism":"Permeability outcome after transporter-inhibitor candidate exposure; no mechanism inferred from the null result.","Evidence_Type":"In vitro","Evidence_Level":"compound","Direction":"null/no effect detected","Quantitative_Outcome":"No effect detected; exact effect size and p-value not reported in text; see Figure 3.","Dose":f"Additive {dose}; sulfasalazine 500 μM; apical-to-basolateral permeability measurement.","Population":"Caco-2 cell monolayer; not human participants","Study_Design":"In-vitro Caco-2 permeability experiment; three replicate wells from a representative study as described in Figure 3 caption.","Source_Title":TITLE,"Authors":AUTHORS,"Year":"2025","DOI":DOI,"PMID":PMID,"Source_Type":"Primary research","Limitations":"Null result is limited to this Caco-2 assay, concentration, substrate and endpoint; it does not establish no transporter effect, no interaction in humans, or safety at food exposures.","Confidence":"Primary full-text in-vitro null finding; effect-size precision limited.","Notes":"Food additive tested as an isolated material, not a meal; no clinical or dietary exposure inference.","Study_ID":f"PMID:{PMID}","Source_URL":URL,"Source_Cache":"","Source_Locator":"Figure 3 and caption; Figure 3 explicitly labels this additive; seven additives showed no effect on sulfasalazine permeability.","Preparation":"Food-additive material in Caco-2 apical compartment; exact commercial lot/form not reported here.","Co_Compounds":"Sulfasalazine","Affected_Entity":"sulfasalazine permeability","Perpetrator":"isolated food additive","Outcome":"null_finding","Conflict_Group":"","Identity_Status":"verified_exact_structure; tested lot equivalence not reported","Release_Origin":"v15_controlled_expansion","Clinical_Extrapolation":"No clinical extrapolation","CookRisk_Exposure_Link":"Identity and in-vitro null outcome only; no Stage C integration"})
    write("data/interaction_evidence.csv",eh,ev)
    ph,probes=read("data/drug_probe_registry.csv")
    for p in probes:
        if p["Drug_Probe"]=="Sulfasalazine permeability in Caco-2 cells": p["Evidence_Records"]=str(int(p["Evidence_Records"])+len(new))
    write("data/drug_probe_registry.csv",ph,probes)
    ih,identity=read("identity/identity_structure_audit.csv")
    for d in defs:
        identity.append({"Compound_ID":ids[d["cid"]],"Canonical_Name":d["name"],"PubChem_CID":d["cid"],"Returned_InChIKey":d["key"],"Registry_InChIKey":d["key"],"Exact_Key_Match":"True","SMILES":d["smiles"],"InChI":d["inchi"],"Structure_Source":f"https://pubchem.ncbi.nlm.nih.gov/compound/{d['cid']}","Status":"PubChem structure identifiers cross-checked; manual structure review pending","Note":"Sodium salt identity used where specified in PubChem; tested sample form/lot equivalence is not detailed in the article.","PubChem_Name_or_Alias_Match":"True","PubChem_Synonyms":d["aliases"]})
    write("identity/identity_structure_audit.csv",ih,identity)
    sh,studies=read("data/study_registry.csv"); study=next(r for r in studies if r["PMID"]==PMID)
    study["Evidence_Record_IDs"] += "|"+"|".join(new); study["Evidence_Record_Count"]=str(int(study["Evidence_Record_Count"])+len(new)); study["Verification_Status"] += "; Figure 3 Caco-2 null findings for four added food additives"
    write("data/study_registry.csv",sh,studies)
    ah,audit=read("provenance/source_audit.csv")
    for eid,d in zip(new,defs): audit.append({"Evidence_ID":eid,"PMID":PMID,"DOI":DOI,"Source_Title":TITLE,"Source_URL":URL,"Source_Cache":"","Source_Locator":"Figure 3 and caption; named Caco-2 condition; no effect on sulfasalazine permeability","Verification_Status":"Primary full text viewed","Fields_Audited":"tested additive name; Caco-2 substrate/model; dose; null outcome; limitations","Limitations":"Single in-vitro permeability endpoint; exact numerical effect size not reported; no clinical inference."})
    write("provenance/source_audit.csv",ah,audit)
    wh,warnings=read("data/warning_ledger.csv")
    warnings.append({"Warning_ID":"V15-W03","Code":"BATCH_7_NULL_ASSAY_LIMIT","Description":"Batch 7 records assay-specific Caco-2 null results; exact numerical effect sizes are not reported, and these results do not establish absence of human interactions.","Affected":"Batch 7; SB-V15-008 through SB-V15-011","Classification":"scientific uncertainty","Before":"No V15 batch 7 records","Action":"Retained null finding with tested concentration, model, endpoint, and limits; did not substitute zero.","After":"Unresolved","Remaining_Limitations":"One in-vitro model, exact effect sizes not reported, tested sample form not fully specified, and clinical relevance unknown.","Resolution_Source":f"PMID:{PMID}; PubChem CID records","Review_Date":DATE})
    write("data/warning_ledger.csv",wh,warnings)
    # Reconcile existing source-register entry instead of creating a duplicate PMID row.
    rh,reg=read("provenance/source_register.csv")
    for row in reg:
        if row.get("PMID")==PMID:
            row["Compound"] += "; "+"; ".join(d["name"] for d in defs)
            row["Chemical_record"] += "; "+"; ".join(f"https://pubchem.ncbi.nlm.nih.gov/compound/{d['cid']}" for d in defs)
            row["Verification_scope"] += "; Figure 3 null permeability findings; PubChem structure identifiers"
    write("provenance/source_register.csv",rh,reg)
    metadata=json.loads((ROOT/"release_metadata.json").read_text(encoding="utf-8"))
    metadata.update({"expected_compounds":len({r["Compound_ID"] for r in compounds}),"expected_evidence":len({r["Evidence_ID"] for r in ev}),"warning_count":len(warnings),"last_completed_batch":7,"drug_probe_rows":len(probes),"bibliography_rows":len(read("data/publication_bibliography.csv")[1]),"unique_nonblank_PMIDs":len({r["PMID"] for r in read("data/publication_bibliography.csv")[1] if r["PMID"]}),"study_rows":len(studies)})
    (ROOT/"release_metadata.json").write_text(json.dumps(metadata,indent=2,ensure_ascii=False)+"\n",encoding="utf-8",newline="\n")
    decisions={"screened":4,"accepted":[{"compound":d["name"],"PubChem_CID":d["cid"],"reason":"Named in Figure 3 and directly tested in the primary Caco-2 study; exact PubChem salt/structure identifiers cross-checked; null result retained."} for d in defs],"held":[{"candidate":"Sunset Yellow FCF","reason":"PubChem substance/component records surfaced conflicting/ambiguous CIDs for the tested food-color form; held pending exact sodium-salt structure/CID adjudication."}],"rejected":[],"source":f"PMID {PMID}; DOI {DOI}; primary full text Figure 3"}
    (ROOT/"validation/V15_batch_07_candidate_decisions.json").write_text(json.dumps(decisions,indent=2,ensure_ascii=False)+"\n",encoding="utf-8",newline="\n")
    (ROOT/"validation/V15_batch_07_review.md").write_text(f"# V15 Batch 7 review\n\nSource: PMID {PMID}; DOI {DOI}; full text and Figure 3 reviewed. Four additional named additives were directly tested in Caco-2 sulfasalazine permeability experiments and no effect was detected. Additives were applied apically at 200 μM, except neohesperidin dihydrochalcone at 100 μM; sulfasalazine was 500 μM. Figure 3 caption describes three replicate wells from a representative study. Exact effect sizes and p-values are not reported in text, so these are categorical null findings and are not converted to zero.\n\nAccepted: Brilliant Blue FCF (CID 19700), azorubine/carmoisine (CID 19118), neohesperidin dihydrochalcone (CID 30231), and tartrazine (CID 164825). The structure entries use PubChem's specified sodium-salt forms; sample lot identity was not detailed in the article. Sunset Yellow FCF remains held because PubChem surfaced conflicting/ambiguous CID and salt-form records; no identity was guessed. No clinical inference is made.\n\nGate: pending automated validation.\n",encoding="utf-8",newline="\n")
    (ROOT/"validation/V15_batch_07_gate.json").write_text(json.dumps({"batch":7,"status":"PENDING_AUTOMATED_VALIDATION","accepted_compounds":4,"new_evidence":len(new),"screened_candidates":5},indent=2)+"\n",encoding="utf-8",newline="\n")

if __name__ == "__main__": main()
