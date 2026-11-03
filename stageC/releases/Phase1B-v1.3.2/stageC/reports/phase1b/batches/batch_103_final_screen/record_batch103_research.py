"""Finish first-pass quantitative food screening for the final five pending identities."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[5]
STAGE=ROOT/"stageC"
P=STAGE/"reports"/"phase1b"
BATCH=P/"batches"/"batch_103_final_screen"
FOOD=STAGE/"data"/"food_composition"/"food_composition.csv"
MAPPING=STAGE/"data"/"compound_food_mapping"/"compound_food_mapping.csv"
AUDIT=STAGE/"data"/"stage_b_snapshot_20261103"/"identity_structure_audit.csv"
COMPOUNDS=STAGE/"data"/"stage_b_snapshot_20261103"/"compound_registry.csv"
PENDING=P/"PENDING_IDENTITY_CANDIDATES.csv"
SEARCH=P/"SEARCH_LOG.csv"
CANDIDATES=P/"CANDIDATES.csv"
SOURCES=STAGE/"data"/"food_composition"/"source_registry.csv"
COVERAGE=P/"COMPOUND_COVERAGE_REGISTER_2026-11-03.csv"
CHECKPOINT=P/"CHECKPOINTS.json"

PENDING_FIELDS=["Candidate_Record_ID","Batch","Compound_ID","Canonical_Name","Analyte_as_Reported","Food_Name","Scientific_Name","Food_Part","Cultivar_or_Variety","Food_Geography","Original_Value","Original_Unit","Normalized_Value","Normalized_Unit","Measurement_Basis","Analytical_Method","Sample_and_Variability","Source_Title","DOI_or_Identifier","Source_URL","Source_Locator","Verification_Level","Disposition","Identity_Status","Mapping_Confidence","Limitations","Next_Action"]

def read(path):
    with path.open(encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
def write(path,fields,rows):
    with path.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore");w.writeheader();w.writerows(rows)
def append(path,fields,rows):
    if not rows:return
    with path.open("a",encoding="utf-8",newline="") as f:
        csv.DictWriter(f,fieldnames=fields,extrasaction="ignore",lineterminator="\r\n").writerows(rows)
def make(cid,name,sample,value,unit,norm,basis,method,study,doi,url,locator,level,limitation,action,foodpart="",species=""):
    return {"Candidate_Record_ID":f"CAND103-{cid}-{len(rows)+1:03d}","Batch":"103","Compound_ID":cid,"Canonical_Name":name,"Analyte_as_Reported":name,"Food_Name":sample,"Scientific_Name":species,"Food_Part":foodpart,"Cultivar_or_Variety":"","Food_Geography":"","Original_Value":value,"Original_Unit":unit,"Normalized_Value":norm,"Normalized_Unit":"mg/kg" if norm else "","Measurement_Basis":basis,"Analytical_Method":method,"Sample_and_Variability":"","Source_Title":study,"DOI_or_Identifier":doi,"Source_URL":url,"Source_Locator":locator,"Verification_Level":level,"Disposition":"PENDING_IDENTITY_REVIEW" if value else "QUALITATIVE_ONLY_NUMERIC_VALUE_NOT_ACCESSIBLE","Identity_Status":"Pending in Stage B snapshot","Mapping_Confidence":"Not active; identity pending","Limitations":limitation,"Next_Action":action}

rows=[]
def add(*args,**kwargs):
    row=make(*args,**kwargs);rows.append(row);return row

WILEY="https://onlinelibrary.wiley.com/doi/10.1155/2018/6486250"
WILEY_TITLE="Simultaneous Determination of Sunset Yellow FCF, Allura Red AC, Quinoline Yellow WS, and Tartrazine in Food Samples by RP-HPLC"
for sample,value in [("Gummy bears","38.4 ± 0.6"),("Red chewing gum","70.0 ± 0.9"),("Sweets candy 1","19.9 ± 0.2"),("Sweets candy 2","57.6 ± 0.3")]:
    add("MOL-V14-CID-33258","Allura Red AC (FD&C Red No. 40)",sample,value,"mg/kg product mass",value,"as-sold sample product mass; no moisture correction relevant/reported","RP-HPLC-UV; analyte standards from Sigma-Aldrich",WILEY_TITLE,"10.1155/2018/6486250",WILEY,"Table 2, E129; replicate n=3; Table values are mg/kg","primary full text verified","Stage B identity remains pending; tested dye salt/lot form not documented as equivalent to the exact Stage B salt.","Retain separately until formal Stage B identity review and exact tested-form adjudication.","confectionery")

BLUE_URL="https://www.fda.gov.tw/tc/includes/GetFile.ashx?id=7993&mID=148"
BLUE_TITLE="Identification and determination of seven synthetic dyes in foodstuffs and soft drinks on a monolithic C18 column by high performance liquid chromatography"
for sample,value in [("C candy, blue","36.4"),("C candy, green","13.0"),("Chocolate candy, green","31.1"),("Baked green pea, green","2.6")]:
    add("MOL-V15-CID-19700","Brilliant Blue FCF",sample,value,"mg/kg product mass",value,"as-sold product mass, mg/kg; moisture correction not reported","HPLC, monolithic C18 method; source Table 4",BLUE_TITLE,"Journal of Food and Drug Analysis 2008;16(5):77-82",BLUE_URL,"Table 4, concentration of synthetic dyes in food and soft-drink samples","primary full text verified from official Taiwan FDA-hosted journal PDF","Stage B identity is pending; salt form/lot equivalence is not specified in the accessible table.","Keep as candidate only until formal Stage B identity and salt-form review.","processed snack/candy")

AZ_URL="https://dergipark.org.tr/en/download/article-file/78146"
AZ_TITLE="Investigation of the Amounts of Synthetic Dyes Added to Some Foodstuffs (Bazı Gıda Maddelerine Katılan Sentetik Boyaların Miktarlarının Araştırılması)"
add("MOL-V15-CID-19118","Azorubine (carmoisine)","Candies (market samples)","181.22 ± 20.22","mg/kg","181.22 ± 20.22","as-sold candy sample mass; no moisture correction reported","C18 Sep-Pak extraction followed by spectrophotometry","GIDA 1998;23(3):195-199", "GIDA 1998;23(3):195-199; no DOI identified",AZ_URL,"Abstract/summary reports mean candy concentration; source page and PDF indexed","primary article PDF/abstract verified; full details limited","Accessible source summary does not provide sample n, individual candy values, exact salt form, or uncertainty definition; Stage B identity remains pending.","Obtain and inspect all paper tables/methods; keep pending until exact dye form and Stage B review are resolved.","confectionery")

for sample,value in [("Yellow chewing gum","127.5 ± 1.9"),("Ice pops","13.3 ± 0.2"),("Sweets candy 1","25.8 ± 0.3")]:
    add("MOL-V15-CID-164825","Tartrazine",sample,value,"mg/kg product mass",value,"as-sold sample product mass; no moisture correction reported","RP-HPLC-UV; analyte standards from Sigma-Aldrich",WILEY_TITLE,"10.1155/2018/6486250",WILEY,"Table 2, E102; replicate n=3; Table values are mg/kg","primary full text verified","Stage B identity pending; article does not state the tested salt form/lot in a way that resolves the exact Stage B form.","Retain as candidate; require formal Stage B identity and tested-form review.","confectionery")

NHDC_TITLE="Low-calorie sweeteners in food and food supplements on the Italian market"
NHDC_URL="https://pmc.ncbi.nlm.nih.gov/articles/PMC9669802/"
add("MOL-V15-CID-30231","Neohesperidin dihydrochalcone","Italian-market hard candies; NHDC detected in 3, quantifiable in 1","","","","No numeric food concentration available in accessible primary/EFSA tables","UPLC-MS/MS in primary study; analytical methods verified in the article","Janvier et al. 2015 Food Additives & Contaminants: Part B 8(4):298-308","10.1080/19393210.2015.1094829; PMID 26406785","https://pubmed.ncbi.nlm.nih.gov/26406785/","Primary paper §Confectionery says 3 detections, one quantifiable; accessible Table 4 reports no NHDC group average. EFSA 2022 review reports one quantified hard candy, LOQ 10 µg/kg.","Primary paper full-text excerpt and EFSA opinion reviewed","No exact sample concentration appears in accessible table; do not replace with LOQ, MPL, assumed use level, or exposure estimate. Stage B identity pending.","Seek the supplementary sample-level database or author dataset; otherwise preserve qualitative detection only and retain pending status.","hard candy")

EVENTS=[
 ("MOL-V14-CID-33258","Allura Red AC (FD&C Red No. 40)","Allura Red AC quantitative ordinary-food sample concentrations candy chewing gum HPLC Table 2","Alp et al. 2018; Wiley full text, DOI 10.1155/2018/6486250","Table 2 reports E129 in gummy bears 38.4±0.6, red gum 70.0±0.9, sweets candy 1 19.9±0.2, sweets candy 2 57.6±0.3 mg/kg; n=3","PENDING_IDENTITY_CANDIDATE_ONLY","Values are direct product-mass measurements; exact test salt/form remains unverified against Stage B identity review."),
 ("MOL-V15-CID-19700","Brilliant Blue FCF","Brilliant Blue FCF market candy baked pea quantitative HPLC food concentrations Table 4","Journal of Food and Drug Analysis 2008; official Taiwan FDA-hosted PDF","Table 4 reports 36.4 and 13.0 mg/kg in C candies, 31.1 mg/kg chocolate candy, and 2.6 mg/kg baked green pea","PENDING_IDENTITY_CANDIDATE_ONLY","Source table numeric; Stage B sodium-salt identity and tested lot equivalence unresolved."),
 ("MOL-V15-CID-19118","Azorubine (carmoisine)","azorubine candy mean concentration quantitative food sample C18 spectrophotometry","GIDA 1998;23(3):195-199; DergiPark full-article PDF","Source reports candy mean 181.22±20.22 mg/kg; sample n and individual values not accessible in index summary","PENDING_IDENTITY_CANDIDATE_ONLY","Keep the mean as a source-specific candidate; verify paper details and exact salt identity before use."),
 ("MOL-V15-CID-30231","Neohesperidin dihydrochalcone","neohesperidin dihydrochalcone measured foods Janvier 2015 hard candy table concentrations","Janvier et al. 2015 primary paper; EFSA 2022 opinion; PubMed/PMC","Primary study reports NHDC detection in 3 hard candies, quantifiable in one; Table 4 contains no NHDC mean, EFSA gives 10 µg/kg LOQ but no exact sample value","QUALITATIVE_ONLY_NO_NUMERIC_VALUE","Do not treat LOQ or permitted maximum as measured concentration; retrieve sample-level data if available."),
 ("MOL-V15-CID-164825","Tartrazine","tartrazine quantitative sample concentrations gummy candy ice pops HPLC Table 2","Alp et al. 2018; Wiley full text, DOI 10.1155/2018/6486250","Table 2 reports E102 in yellow gum 127.5±1.9, ice pops 13.3±0.2 and sweets candy 1 25.8±0.3 mg/kg; n=3","PENDING_IDENTITY_CANDIDATE_ONLY","Values are direct product-mass measurements; exact test salt/form remains unverified against Stage B identity review.")]

def main():
    cp=json.loads(CHECKPOINT.read_text(encoding="utf-8"))
    if cp.get("checkpoint_id")!="Phase1B-2026-11-03-batch-102-scientific-coverage": raise RuntimeError("Expected validated Batch 102 checkpoint.")
    if len(read(FOOD))!=541 or len(read(MAPPING))!=541: raise RuntimeError("Unexpected active data count; no B103 metadata written.")
    searched={r["Compound_ID"] for r in read(SEARCH)}
    target_ids={e[0] for e in EVENTS}
    if len(searched)!=138 or target_ids & searched: raise RuntimeError("Expected exactly five previously unlogged targets; inspect search history.")
    BATCH.mkdir(parents=True,exist_ok=True)
    (P/"batches"/"batch_102_scientific_coverage"/"CHECKPOINTS_BATCH102_FINAL.json").write_bytes(CHECKPOINT.read_bytes())

    audit={r["Compound_ID"]:r for r in read(AUDIT)}
    for cid in target_ids:
        if audit[cid]["Status"]=="Complete": raise RuntimeError(f"Pending identity expected for {cid}.")
    existing_pending=read(PENDING); existing_candidate_ids={r["Candidate_Record_ID"] for r in existing_pending}
    new_rows=[r for r in rows if r["Candidate_Record_ID"] not in existing_candidate_ids]
    append(PENDING,PENDING_FIELDS,new_rows)
    all_pending=read(PENDING)

    searches=read(SEARCH); search_fields=list(searches[0]); existing_queries={(r["Compound_ID"],r["search_query"]) for r in searches}
    new_search=[]
    for cid,name,query,source,findings,decision,reason in EVENTS:
        if (cid,query) not in existing_queries:
            new_search.append({"Compound_ID":cid,"canonical_name":name,"search_query":query,"database_or_search_source":source,"search_date":"2026-11-03","results_identified":findings,"candidate_publications":source,"screening_decision":decision,"reason":reason})
    append(SEARCH,search_fields,new_search)

    cands=read(CANDIDATES); cand_fields=list(cands[0]); known_cand={r["candidate_id"] for r in cands}
    groups=defaultdict(list)
    for r in rows: groups[r["Compound_ID"]].append(r)
    summaries=[]
    for cid,name,_,_,findings,decision,reason in EVENTS:
        rs=groups[cid]
        summaries.append({"candidate_id":f"CAND-B103-{cid.split('-')[-1]}","compound_id":cid,"compound_name":name,"food_name":"; ".join(dict.fromkeys(r["Food_Name"] for r in rs)),"food_database":"Primary analytical study / official scientific assessment","food_database_record_id":"; ".join(dict.fromkeys(r["Source_Locator"] for r in rs)),"candidate_concentration":"; ".join(f"{r['Food_Name']}: {r['Original_Value']} {r['Original_Unit']}" for r in rs if r["Original_Value"]),"candidate_unit":"; ".join(sorted({r["Original_Unit"] for r in rs if r["Original_Unit"]})),"verification_status":"QUALITATIVE_ONLY" if not any(r["Original_Value"] for r in rs) else "PENDING_IDENTITY_REVIEW","source_locator":"; ".join(dict.fromkeys(r["Source_Locator"] for r in rs)),"candidate_decision":reason})
    for r in summaries:
        if r["candidate_id"] not in known_cand: cands.append(r)
    write(CANDIDATES,cand_fields,cands)

    src=read(SOURCES); src_fields=list(src[0]); known_urls={r["source_url"] for r in src}
    additions=[
      (WILEY_TITLE,"Primary analytical measurement",WILEY,"RP-HPLC-UV survey of commercial confectionery","Full text and Table 2 verified; values held pending identity review","Do not promote pending Stage B dye forms."),
      (BLUE_TITLE,"Primary analytical measurement",BLUE_URL,"HPLC analysis; Table 4 in official journal PDF hosted by Taiwan FDA","Food sample values verified from Table 4; values held pending identity review","Do not promote pending Stage B salt-form and lot review."),
      (AZ_TITLE,"Primary analytical measurement",AZ_URL,"C18 Sep-Pak and spectrophotometric candy dye assay","Primary-paper result verified at source summary; full sample-level metadata limited","Confirm table, sample count and exact salt before ingestion."),
      (NHDC_TITLE,"Primary analytical measurement","https://pubmed.ncbi.nlm.nih.gov/26406785/","UPLC-MS/MS survey of 290 Italian-market foods","Primary abstract and accessible article text; 3 candy detections, 1 quantifiable, no sample-level value in accessible Table 4","No numeric substitution; retrieve supplementary/database if available."),
      ("Re-evaluation of neohesperidine dihydrochalcone (E 959) as a food additive","Authoritative scientific assessment","https://pmc.ncbi.nlm.nih.gov/articles/PMC9669802/","EFSA Journal 2022; DOI 10.2903/j.efsa.2022.7595","Official assessment confirms limited quantified detections and reports source LOQs","Do not treat LOQ or legal maximum as food measurement.")]
    for name,cls,url,typ,avail,req in additions:
        if url not in known_urls:
            src.append({"source_name":name,"source_classification":cls,"source_url":url,"source_type":typ,"availability_status":avail,"ingestion_requirement":req});known_urls.add(url)
    write(SOURCES,src_fields,src)

    # Recompute the 143-row cumulative status and all counts from current authoritative files.
    coverage=read(COVERAGE); logs=read(SEARCH); foods=read(FOOD); maps=read(MAPPING); identity_rows=read(AUDIT)
    complete_ids={r["Compound_ID"] for r in identity_rows if r["Status"]=="Complete"}
    pending_ids=set(audit)-complete_ids
    map_by_id=defaultdict(list)
    for m in maps:
        for cid in set(filter(None,[m.get("compound_id","")]+m.get("candidate_compound_ids","").split("|"))): map_by_id[cid].append(m)
    food_by_id=defaultdict(list)
    for f in foods:
        if f.get("compound_id"): food_by_id[f["compound_id"]].append(f)
    search_by=defaultdict(list)
    for r in logs: search_by[r["Compound_ID"]].append(r)
    pending_by=defaultdict(list)
    for r in all_pending: pending_by[r["Compound_ID"]].append(r)
    for c in coverage:
        cid=c["Compound_ID"]; relevant=map_by_id[cid]; search_rows=search_by[cid]; cand_rows=pending_by[cid]
        verified=[m for m in relevant if m["mapping_status"] in {"Exact identity match","Verified synonym match","Structure-supported match"} and m["quantitative_data_available"]=="true"]
        linked_ids={m["food_record_id"] for m in verified if any(f["food_record_id"]==m["food_record_id"] for f in foods)}
        linked=[f for f in foods if f["food_record_id"] in linked_ids]
        eligible=c["Identity_Audit_Status"]=="Complete" and bool(verified)
        c["Research_Status"]="Researched/screened" if search_rows else "Not yet screened"
        c["Any_Mapping"]="true" if relevant else "false"
        c["Quantitative_Mapping"]="true" if any(m["quantitative_data_available"]=="true" for m in relevant) else "false"
        c["Food_Record_Count"]=str(len(linked_ids))
        c["Mapping_Row_Count"]=str(len(relevant))
        c["Search_Log_Event_Count"]=str(len(search_rows))
        c["Identity_Complete_Quantitative_Eligible"]="true" if eligible else "false"
        c["Accepted_Quantitative_Coverage_Status"]="Covered" if eligible else "Not covered"
        c["Coverage_Status"]="Identity-complete quantitative coverage" if eligible else "Identity review pending; excluded from eligible coverage" if cid in pending_ids else "Identity-complete; no accepted quantitative measurement"
        if eligible or linked:
            c["Food_Composition_Evidence_Status"]="Accepted quantitative measurement(s)"
            c["Measurement_Basis"]="; ".join(sorted({r["moisture_basis"] for r in linked if r.get("moisture_basis")}))
        elif any(r["Original_Value"] for r in cand_rows):
            c["Food_Composition_Evidence_Status"]="Quantitative candidate(s) held outside accepted dataset"
            c["Measurement_Basis"]="; ".join(sorted({r["Measurement_Basis"] for r in cand_rows if r.get("Measurement_Basis")}))
        elif cand_rows:
            c["Food_Composition_Evidence_Status"]="Qualitative finding only; no accepted numerical value"
            c["Measurement_Basis"]=""
        else:
            c["Food_Composition_Evidence_Status"]="No qualifying quantitative ordinary-food measurement documented"
            c["Measurement_Basis"]=""
        refs=[]
        for r in linked: refs += (["DOI:"+r["doi"]] if r.get("doi") else [])+[r.get("source_url","")]
        for r in cand_rows: refs += [r.get("DOI_or_Identifier", ""),r.get("Source_URL","")]
        for r in search_rows: refs += [r.get("candidate_publications","")]
        c["Relevant_Source_References"]="; ".join(dict.fromkeys(x for x in refs if x))
        issues=[]
        if cid in pending_ids: issues.append(c["Identity_Audit_Status"])
        issues += [r["Limitations"] for r in cand_rows if r.get("Limitations")]
        c["Pending_Issues"]="; ".join(dict.fromkeys(issues))
        c["Next_Justified_Action"]=("Formal Stage B identity review required before any candidate can count; preserve candidate evidence separately." if cid in pending_ids else "Maintain accepted provenance; add data only with a distinct verified source lead." if eligible else "Resolve source limitations or search a meaningful new primary-source lead.")
    write(COVERAGE,list(coverage[0]),coverage)

    # Keep proposals synchronized to the full 36-ID snapshot; no status is changed or cleared.
    proposals=[]
    for r in identity_rows:
        if r["Status"]=="Complete": continue
        cr=pending_by[r["Compound_ID"]]
        refs=[r.get("Structure_Source","")]+[x.get("Source_URL","") for x in cr if x.get("Source_URL")]
        proposals.append({"Compound_ID":r["Compound_ID"],"Canonical_Name":r["Canonical_Name"],"PubChem_CID":r["PubChem_CID"],"Registry_InChIKey":r["Registry_InChIKey"],"Exact_Key_Match":r["Exact_Key_Match"],"Current_Identity_Status":r["Status"],"Current_Identity_Note":r["Note"],"Candidate_Chemical_Identity":"Unadjudicated Stage B registry identity: "+r["Canonical_Name"],"Source_Evidence_References":"; ".join(dict.fromkeys(x for x in refs if x)),"Evidence_Assessment":"Captured identifiers and source naming are candidate evidence only; they do not constitute independent structure parsing or prove tested-sample identity equivalence.","Remaining_Uncertainty":r["Note"]+ ("; target-specific food measurement and salt form need review." if cr else ""),"Recommended_Decision":"requires specialist review; no change proposed","Required_Formal_Action":"Separate authorized Stage B amendment/review only; retain Phase 1B pending status until the authoritative release is formally updated."})
    proposal_fields=list(proposals[0])
    write(P/"IDENTITY_ADJUDICATION_PROPOSALS_2026-11-03.csv",proposal_fields,proposals)

    with (BATCH/"screening_matrix.csv").open("w",encoding="utf-8-sig",newline="") as f:
        fields=["Compound_ID","Canonical_Name","Identity_Status","Screening_Result","Candidate_Records","Disposition","Next_Action"]
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for cid,name,query,source,findings,decision,reason in EVENTS:
            rs=groups[cid]
            w.writerow({"Compound_ID":cid,"Canonical_Name":name,"Identity_Status":audit[cid]["Status"],"Screening_Result":findings,"Candidate_Records":len(rs),"Disposition":decision,"Next_Action":reason})
    with (BATCH/"pending_identity_candidates.csv").open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=PENDING_FIELDS);w.writeheader();w.writerows(rows)

    foods=read(FOOD);maps=read(MAPPING);coverage=read(COVERAGE);logs=read(SEARCH);all_pending=read(PENDING)
    researched={r["Compound_ID"] for r in logs}
    eligible_ids={r["Compound_ID"] for r in coverage if r["Identity_Complete_Quantitative_Eligible"]=="true"}
    quantitative_ids={r["compound_id"] for r in maps if r.get("quantitative_data_available")=="true" and r.get("compound_id")}
    numeric_pending=sum(bool(r["Original_Value"]) for r in all_pending)
    no_orphans=sum(1 for m in maps if m["food_record_id"] not in {f["food_record_id"] for f in foods})
    source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [FOOD,MAPPING]}
    delta={"batch":"103","batch_date":"2026-11-03","screening_targets":5,"new_search_events":len(new_search),"research_coverage":f"{len(researched)}/143","accepted_records_added":0,"accepted_mappings_added":0,"candidate_detail_rows_added":len(new_rows),"pending_candidate_records_total":len(all_pending),"pending_candidate_numeric_rows":numeric_pending,"current":{"stage_b_compounds":len(coverage),"identity_complete":len(complete_ids),"identity_pending":len(pending_ids),"researched_unique_compounds":len(researched),"identity_complete_quantitative_compounds":len(eligible_ids),"identity_complete_uncovered":len(complete_ids)-len(eligible_ids),"unique_compounds_quantitatively_mapped_including_pending":len(quantitative_ids),"food_records":len(foods),"mapping_rows":len(maps),"blocked_mapping_rows":46,"orphan_mappings":no_orphans,"food_sha256":source_hashes[FOOD.name],"mapping_sha256":source_hashes[MAPPING.name]},"target":{"minimum":130,"stretch":143,"achieved":len(eligible_ids)>=130,"status":"PHASE1B_TARGET_NOT_ACHIEVED" if len(eligible_ids)<130 else "PHASE1B_TARGET_ACHIEVED","additional_eligible_compounds_needed":max(0,130-len(eligible_ids))},"limitations":["All five remaining previously unlogged IDs now have a documented first-pass screen; this is not an exhaustive-literature claim.","Four pending-identity compounds have numerical candidate findings; NHDC has qualitative source-confirmed detection but no accessible exact concentration.","Identity-pending findings are not accepted or counted.","130 minimum remains unreachable under the 107 complete-identity ceiling without separate Stage B adjudication."]}
    (BATCH/"coverage_delta.json").write_text(json.dumps(delta,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

    cp={"checkpoint_id":"Phase1B-2026-11-03-batch-103-all-143-screened","status":"PHASE1B_TARGET_NOT_ACHIEVED","scope":"Stage C Phase 1B only","previous_checkpoint":"Phase1B-2026-11-03-batch-102-scientific-coverage","source_stage_b_release":"StageB_FINALIZED (read-only)","phase1_foundation_dependency":"stageC/releases/Phase1-v1.3.0 (read-only)","stage_b_target_count":len(coverage),"stage_b_identity_complete":len(complete_ids),"stage_b_identity_pending":len(pending_ids),"research_screened":len(researched),"research_screened_fraction":f"{len(researched)}/143","active_food_records":len(foods),"active_mapping_rows":len(maps),"unique_compounds_quantitatively_mapped_including_pending":len(quantitative_ids),"identity_complete_quantitative_compounds":len(eligible_ids),"identity_complete_uncovered":len(complete_ids)-len(eligible_ids),"blocked_mapping_rows":46,"orphan_mappings":no_orphans,"pending_identity_candidate_records":len(all_pending),"pending_identity_candidate_numeric_rows":numeric_pending,"batch_103":{"screened_compounds":5,"new_search_events":len(new_search),"accepted_records":0,"accepted_mappings":0,"numeric_candidate_rows":sum(bool(r["Original_Value"]) for r in rows),"qualitative_only_rows":sum(not bool(r["Original_Value"]) for r in rows)},"target":{"minimum":130,"stretch":143,"achieved":len(eligible_ids)>=130,"additional_compounds_needed":max(0,130-len(eligible_ids)),"identity_complete_ceiling_without_formal_Stage_B_review":len(complete_ids),"pending_identity_reviews_needed_even_if_all_complete_identity_gaps_are_filled":max(0,130-len(eligible_ids)-max(0,len(complete_ids)-len(eligible_ids)))},"validation":{"phase1_validation":"PASS; Batch 102 validator checked 541 rows; re-run after final metadata","focused_tests":"PASS; Batch 102 unittest 16/16; final continuation regression pending","mapping_rebuild":"PENDING independent full-file reconstruction","snapshot_changes":0},"sha256":source_hashes,"reports":["batches/batch_103_final_screen/BATCH_103_SCREENING_REPORT.md","batches/batch_103_final_screen/screening_matrix.csv","PENDING_IDENTITY_CANDIDATES.csv","IDENTITY_ADJUDICATION_PROPOSALS_2026-11-03.csv","COMPOUND_COVERAGE_REGISTER_2026-11-03.csv"],"final_acquisition_state":"all 143 Stage B IDs screened at least once; no final release created; Stage B identity adjudication remains required."}
    CHECKPOINT.write_text(json.dumps(cp,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

    report=f'''# Batch 103 — final five first-pass screens\n\n**Status:** `PHASE1B_BATCH_COMPLETE`; the full 143-ID research screen is complete. No identity-pending value was ingested.\n\n## Targets and findings\n\nBatch 103 screened Allura Red AC, Brilliant Blue FCF, Azorubine, Neohesperidin dihydrochalcone, and Tartrazine. Four have quantitative candidates in confectionery/snacks; all remain outside accepted data because their Stage B identities are pending and exact tested salt/structure equivalence is not independently established. The fifth has qualitative detection evidence but no accessible exact concentration.\n\n- **Allura Red AC:** four Table 2 food values (gummy bears, red chewing gum, and two sweets candies), 19.9–70.0 mg/kg product mass, mean ± SD, n=3.\n- **Tartrazine:** three Table 2 values (yellow chewing gum, ice pops, sweets candy 1), 13.3–127.5 mg/kg product mass, mean ± SD, n=3.\n- **Brilliant Blue FCF:** four reported food values: 36.4 and 13.0 mg/kg in two candy products, 31.1 mg/kg chocolate candy, and 2.6 mg/kg baked green pea.\n- **Azorubine:** candy mean 181.22 ± 20.22 mg/kg reported in a 1998 food-dye study; sample count and individual values are not exposed in the accessible summary.\n- **Neohesperidin dihydrochalcone:** Janvier et al. reports detection in three hard candies, quantifiable in one, but accessible Table 4 does not expose that sample's amount. The reported 10 µg/kg LOQ is not substituted for a measurement.\n\nExact rows, source locators, methods, and limitations are in `pending_identity_candidates.csv` and the cumulative `PENDING_IDENTITY_CANDIDATES.csv`. No candidate was added to the accepted food table or mappings.\n\n## Coverage after Batch 103\n\n- Stage B universe screened: **{len(researched)}/143**.\n- Identity-complete quantitative coverage: **{len(eligible_ids)}/107**.\n- Pending identity reviews: **{len(pending_ids)}**; candidate measurement rows across Batches 102–103: **{numeric_pending} numeric** plus **{sum(not bool(r['Original_Value']) for r in all_pending)} nonnumeric/method-only rows**.\n- Active accepted records/mappings: **{len(foods)}/{len(maps)}**; unique quantitative mapping IDs including identity-pending records: **{len(quantitative_ids)}**; blocked legacy mapping rows: 46; orphan mappings: {no_orphans}.\n- The **130 minimum is not achieved**. At 99 accepted identity-complete compounds, 31 additional eligible compounds are needed. The current 107-identity ceiling leaves a maximum of eight additional complete-identity compounds; reaching 130 also requires at least 23 pending Stage B identities to be formally resolved and have qualifying food measurements.\n\n## Validation and next justified work\n\nBatch 102's focused tests passed 16/16 and `validate_phase1.py` passed. Final regression tests, independent mapping reconstruction, final Phase 1 validation, and snapshot integrity checks are being run after Batch 103. The 143 first-pass screens are complete; future acquisition should follow genuinely new source leads or formal Stage B identity adjudications, not repeat the same bounded searches. No release was created.\n'''
    (BATCH/"BATCH_103_SCREENING_REPORT.md").write_text(report,encoding="utf-8")
    with (P/"PROGRESS.md").open("a",encoding="utf-8") as f:
        f.write("\n\n## Batch 103 — final five first-pass screens — 2026-11-03\n\n")
        f.write(f"Research coverage reached {len(researched)}/143. Four target compounds have quantitative identity-pending candidate data; NHDC has qualitative detection evidence but no accessible sample concentration. Accepted identity-complete coverage remains {len(eligible_ids)}/107, below the 130 minimum. See `batches/batch_103_final_screen/BATCH_103_SCREENING_REPORT.md`.\n")
    (P/"NEXT_STEPS.md").write_text("""# Next steps — post Batch 103\n\nThe first-pass research screen now covers all 143 Stage B compounds. Phase 1B has 99 accepted identity-complete quantitative compounds out of 107; the 130 minimum is not achieved. The present identity ceiling is 107, leaving eight complete-identity gaps and requiring at least 23 pending identities to be formally resolved, plus qualifying food evidence, even if every complete-identity gap is filled.\n\n1. Obtain separate authorization for any formal Stage B amendment; do not change `StageB_FINALIZED` from Phase 1B.\n2. If identity decisions are formally updated in a future authorized Stage B release, re-screen only the newly eligible compounds with their source-specific leads and validate exact structures/mappings.\n3. Follow only new credible food-composition source leads or obtain the inaccessible primary data identified in the pending candidate ledger. Keep uncertainty and negative searches documented.\n4. Run the final Phase 1B regression checks and independent mapping reconstruction before considering any later release. No Phase 1B release has been created.\n""",encoding="utf-8")
    (P/"RESUME_INSTRUCTIONS.md").write_text("""# Resume instructions\n\nActive checkpoint: `Phase1B-2026-11-03-batch-103-all-143-screened`. The first-pass research screen includes all 143 Stage B IDs. Inspect `batches/batch_103_final_screen/BATCH_103_SCREENING_REPORT.md`, the cumulative pending candidate ledger, and the identity adjudication proposal register.\n\nCurrent accepted identity-complete quantitative coverage is 99/107; the 130 minimum remains unmet. Run the final test suite and independent mapping reconstruction, then update validation fields in `CHECKPOINTS.json`. Any next coverage increase beyond 107 requires formal Stage B identity review plus qualifying ordinary-food evidence. Do not modify Stage B, Phase 1-v1.3.0, Stage A or historical releases.\n""",encoding="utf-8")

    append_report="""

## Batch 103 continuation state — 2026-11-03

All 143 Stage B IDs have at least one documented research/screening event. Accepted identity-complete quantitative coverage is 99/107; the 130 minimum remains unmet. Four quantitative identity-pending dye candidates and one qualitative-only NHDC finding are recorded separately. No release was created. See `batches/batch_103_final_screen/BATCH_103_SCREENING_REPORT.md` and the active checkpoint.
"""
    for fn in ["FOOD_COMPOSITION_COVERAGE_REPORT.md","MAPPING_COVERAGE_REPORT.md","SEARCH_COVERAGE_REPORT.md","SOURCE_VERIFICATION_REPORT.md","ACCEPTED_REJECTED_RECORD_REPORT.md","PHASE1B_COMPLETION_REPORT.md"]:
        q=P/fn
        with q.open("a",encoding="utf-8") as f: f.write(append_report)
    print(json.dumps({"status":"BATCH103_PASS","new_search_events":len(new_search),"research_coverage":f"{len(researched)}/143","candidate_rows_added":len(new_rows),"candidate_numeric_total":numeric_pending,"eligible":len(eligible_ids),"pending_reviews":len(pending_ids),"food_records":len(foods),"mapping_rows":len(maps),"orphan_mappings":no_orphans,"source_registry_entries":len(src),"central_candidates":len(cands)},indent=2,ensure_ascii=False))

if __name__=="__main__": main()
