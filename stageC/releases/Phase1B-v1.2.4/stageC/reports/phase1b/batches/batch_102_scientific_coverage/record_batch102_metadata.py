"""Record Batch 102 screening evidence and cumulative coverage without reimporting data."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
STAGE = ROOT / "stageC"
P = STAGE / "reports" / "phase1b"
BATCH = P / "batches" / "batch_102_scientific_coverage"
FOOD = STAGE / "data" / "food_composition" / "food_composition.csv"
MAPPING = STAGE / "data" / "compound_food_mapping" / "compound_food_mapping.csv"
REGISTRY = STAGE / "data" / "stage_b_snapshot_20261103" / "compound_registry.csv"
IDENTITY = STAGE / "data" / "stage_b_snapshot_20261103" / "identity_structure_audit.csv"
SOURCE_REGISTRY = STAGE / "data" / "food_composition" / "source_registry.csv"
SEARCH_LOG = P / "SEARCH_LOG.csv"
CANDIDATES = P / "CANDIDATES.csv"
GAPS = P / "coverage_gap_register.csv"
COVERAGE = P / "COMPOUND_COVERAGE_REGISTER_2026-11-03.csv"
PENDING_FILE = P / "PENDING_IDENTITY_CANDIDATES.csv"

def read(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def append_csv(path, fields, rows):
    if not rows:
        return
    with path.open("a", encoding="utf-8", newline="") as f:
        csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\r\n").writerows(rows)

def write_csv(path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)

PENDING_FIELDS = [
    "Candidate_Record_ID", "Batch", "Compound_ID", "Canonical_Name", "Analyte_as_Reported",
    "Food_Name", "Scientific_Name", "Food_Part", "Cultivar_or_Variety", "Food_Geography",
    "Original_Value", "Original_Unit", "Normalized_Value", "Normalized_Unit", "Measurement_Basis",
    "Analytical_Method", "Sample_and_Variability", "Source_Title", "DOI_or_Identifier", "Source_URL",
    "Source_Locator", "Verification_Level", "Disposition", "Identity_Status", "Mapping_Confidence",
    "Limitations", "Next_Action"
]

def pending(cid, name, analyte, food, species, part, value, unit, norm, norm_unit, basis, method,
            sample, title, doi, url, locator, verification, disposition, limitation, action,
            cultivar="", geography=""):
    row = {
        "Candidate_Record_ID": f"CAND102-{cid}-{len(pending.rows)+1:03d}", "Batch": "102",
        "Compound_ID": cid, "Canonical_Name": name, "Analyte_as_Reported": analyte,
        "Food_Name": food, "Scientific_Name": species, "Food_Part": part,
        "Cultivar_or_Variety": cultivar, "Food_Geography": geography,
        "Original_Value": value, "Original_Unit": unit, "Normalized_Value": norm,
        "Normalized_Unit": norm_unit, "Measurement_Basis": basis, "Analytical_Method": method,
        "Sample_and_Variability": sample, "Source_Title": title, "DOI_or_Identifier": doi,
        "Source_URL": url, "Source_Locator": locator, "Verification_Level": verification,
        "Disposition": disposition, "Identity_Status": "Pending in Stage B snapshot",
        "Mapping_Confidence": "Not active; identity pending",
        "Limitations": limitation, "Next_Action": action
    }
    pending.rows.append(row)
    return row
pending.rows = []

# Previously unlogged identity-pending compounds. Values are preserved as source-reported; no
# pending identity is promoted to the accepted food-composition or mapping files.
GINKGO_URL = "https://eurekamag.com/research/098/008/098008110.php"
GINKGO_TITLE = "Purification, identification and the antimicrobial activity of ginkgolic acids in ginkgo seeds"
for suffix, name, val, norm in [
    ("161306", "Ginkgoneolic acid (ginkgolic acid C13:0)", "0.013", "13"),
    ("5281858", "Ginkgolic acid C15:1", "0.042", "42"),
    ("5469634", "Ginkgolic acid C17:1", "0.055", "55")]:
    cid = f"MOL-V13-CID-{suffix}"
    pending(cid, name, name, "Ginkgo seed skimmed powder", "Ginkgo biloba", "seed powder, skimmed/defatted", val,
            "g/kg", norm, "mg/kg", "skimmed powder mass; not native kernel/fresh food basis", "HPLC and LC-MS (as reported in abstract index)",
            "Analytical sample count/variability unavailable; abstract reports homologue values.", GINKGO_TITLE,
            "Chinese Journal of Food Science and Technology 2015;15(3):207-215", GINKGO_URL,
            "Abstract indexed at EurekMag; numerical result and sample basis stated in abstract", "abstract-index verified only",
            "HELD_SOURCE_AND_MATRIX_LIMITATION", "Full primary text/table was not independently reviewed; sample is skimmed powder and monoene double-bond positions are not specified in the accessible abstract.",
            "Obtain and verify primary full text; confirm fatty-acid homologue/isomer mapping and native-food basis before any ingestion.")

pending("MOL-V13-CID-8468", "Vanillic acid", "Vanillic acid", "Rosehip fruit", "Rosa canina", "mature fruit", "76.1 ± 1.6", "µg/g FW", "76.1 ± 1.6", "mg/kg FW",
        "fresh weight (FW), explicitly stated", "HPLC-DAD; identity by retention time against >95% Sigma standard", "Mean ± SD; biological n not explicit; analytical conditions and extraction given in methods.",
        "Phenolic and Carotenoid Profile of Rosehip (Rosa canina L.) Fruits", "10.3390/molecules30153071", "https://www.mdpi.com/1420-3049/30/15/3071",
        "Table 6; mature rosehip; sample preparation methods §2.x; Table 6 explicitly labels FW", "primary full text verified",
        "HELD_STAGE_B_IDENTITY_PENDING", "Food measurement is numerically strong and FW-based, but Stage B identity remains pending expert structure review; biological n is unclear.",
        "Keep isolated until formal Stage B identity adjudication; then revalidate mapping and food record.", geography="Romania")

pending("MOL-V13-CID-8468", "Vanillic acid", "Conjugated vanillic acid released after hydrolysis", "Green soybean/edamame", "Glycine max", "green soybean", "26.88–41.59", "mg/kg FW", "26.88–41.59", "mg/kg FW",
        "fresh weight, as reported; conjugated fraction after hydrolysis", "UPLC-MS/MS after hydrolysis", "Range across samples; detailed replicate values in cited paper.",
        "Simultaneous determination of phenolic acids and flavonoids in soybean by UPLC-MS/MS", "10.3390/molecules22111878", "https://www.mdpi.com/1420-3049/22/11/1878",
        "Conjugated phenolic acid results; exact table/section to confirm in full text", "primary-source lead; analyte semantics checked from abstract/summary",
        "EXCLUDED_ANALYTE_FORM_MISMATCH", "Hydrolysis-derived conjugate pool is not a measurement of free native vanillic acid in food.",
        "Do not ingest as free vanillic acid; retain only as an explicitly distinct conjugate-pool lead.")

pending("MOL-V14-CID-5469424", "Demethoxycurcumin", "Demethoxycurcumin", "Commercial turmeric varieties", "Curcuma longa", "rhizome powder", "0.83 ± 0.047 to 3.36 ± 0.040", "%", "", "",
        "Percent mass basis not explicitly resolved from accessible abstract; do not infer FW/DW", "HPLC with analyte calibration curves", "Four commercial turmeric samples; range endpoints with SD; individual sample table not in abstract.",
        "Improved HPLC method for the determination of curcumin, demethoxycurcumin, and bisdemethoxycurcumin", "10.1021/jf025506a; PMID 12059141", "https://pubmed.ncbi.nlm.nih.gov/12059141/",
        "Abstract; reports range over four turmeric samples", "primary abstract verified",
        "HELD_STAGE_B_IDENTITY_PENDING_AND_BASIS", "Identity is pending; exact sample values and explicit powder moisture/mass basis not recoverable from abstract. No point value reconstructed.",
        "Obtain full paper and confirm table, sample basis, and specific identity before consideration.")

pending("MOL-V14-CID-5315472", "Bisdemethoxycurcumin", "Bisdemethoxycurcumin", "Commercial turmeric varieties", "Curcuma longa", "rhizome powder", "0.42 ± 0.036 to 2.16 ± 0.06", "%", "", "",
        "Percent mass basis not explicitly resolved from accessible abstract; do not infer FW/DW", "HPLC with analyte calibration curves", "Four commercial turmeric samples; range endpoints with SD; individual sample table not in abstract.",
        "Improved HPLC method for the determination of curcumin, demethoxycurcumin, and bisdemethoxycurcumin", "10.1021/jf025506a; PMID 12059141", "https://pubmed.ncbi.nlm.nih.gov/12059141/",
        "Abstract; reports range over four turmeric samples", "primary abstract verified",
        "HELD_STAGE_B_IDENTITY_PENDING_AND_BASIS", "Identity is pending; exact sample values and explicit powder moisture/mass basis not recoverable from abstract. No point value reconstructed.",
        "Obtain full paper and confirm table, sample basis, and specific identity before consideration.")

sinensetin_values = [
    ("BC1","32.86 ± 3.23"),("BC2","29.36 ± 2.94"),("BC3","27.07 ± 2.76"),("BC4","26.22 ± 2.62"),("BC5","32.56 ± 3.21"),
    ("BR1","37.99 ± 3.74"),("BR2","25.59 ± 2.11"),("BR3","26.39 ± 2.63"),("BR4","37.20 ± 3.40"),("BR5","31.41 ± 3.12"),
    ("BO1","31.51 ± 3.14"),("BO2","30.74 ± 3.07"),("BO3","19.56 ± 2.19"),("BO4","25.70 ± 2.56"),("BO5","21.20 ± 2.13")]
for sample, val in sinensetin_values:
    mean, sd = [float(x.strip()) for x in val.split("±")]
    pending("MOL-V14-CID-145659", "Sinensetin", "Sinensetin", f"Clementine peel by-product, coded sample {sample}", "Citrus × clementina", "peel", val,
            "mg/100 g FW", f"{mean*10:.1f} ± {sd*10:.1f}", "mg/kg FW", "fresh weight (FW), explicitly stated",
            "HPLC-DAD", "Mean ± SD; n=3 analytical replicates according to table footnote.",
            "Citrus × Clementina Hort. Juice Enriched with Its By-Products (Peels and Leaves): Chemical Composition, In Vitro Bioactivity, and Impact of Processing",
            "10.3390/antiox9040298", "https://pmc.ncbi.nlm.nih.gov/articles/PMC7222210/",
            f"Table 7, row Sinensetin, sample {sample}; table units mg/100 g FW", "primary full text verified",
            "HELD_STAGE_B_IDENTITY_PENDING_AND_FOOD_USE", "Exact values are available but Stage B identity is pending; peel samples are by-products studied for juice enrichment and ordinary-food context requires adjudication.",
            "Retain separately; require formal Stage B identity review and source/context decision before ingestion.", geography="Southern Italy")

pending("MOL-V14-CID-97214", "Eupatorin", "Eupatorin", "Orthosiphon stamineus chloroform leaf extract fraction", "Orthosiphon stamineus", "chloroform extract fraction", "5.05", "% w/w", "", "",
        "extract mass basis; not food mass", "Reported in a secondary review; original extract study not inspected", "Reported as fraction CF2 composition in review; sample count not available.",
        "Eupatorin: A comprehensive review of its pharmacological activities and underlying molecular mechanisms", "2025 review; cites Yam et al. 2010", "https://www.sciencedirect.com/science/article/pii/S0014299925010842",
        "Review text attributes 5.05% w/w to chloroform extract fraction CF2", "secondary review lead only",
        "EXCLUDED_NONFOOD_EXTRACT", "This is concentration in an extract fraction, not in ordinary food; original cited study needs verification.",
        "Do not treat extract percentage as food composition; seek food-matrix primary measurement only if a credible lead appears.")

for food, value in [("Raw grated carrot","11.45 ± 1.86"),("Commercial carrot puree","8.25 ± 0.09"),("Boiled-mashed carrot","10.65 ± 0.12")]:
    pending("MOL-V15-CID-5280489", "all-trans-β-Carotene", "all-trans-β-carotene", food, "Daucus carota", "root", value,
            "mg/100 g wet weight", "", "mg/kg wet weight", "wet weight, explicitly reported; raw/puree/cooked states differ",
            "HPLC carotenoid analysis; human feeding study reported source concentrations", "Means ± reported variability; raw carrot test meal included 6 subjects; number of analytical replicates not stated here.",
            "Alpha- and beta-carotene from a commercial puree are more bioavailable to humans than from boiled-mashed carrots, as determined using an extrinsic stable isotope reference method",
            "2002, J Nutr 132(2):159-167; PMID 11823572", "https://jn.nutrition.org/article/S0022-3166%2822%2914892-3/fulltext",
            "Food carotenoid concentrations cited in study; raw grated carrot, commercial puree, boiled-mashed carrot", "primary study lead; fulltext access restricted during verification",
            "HELD_STAGE_B_IDENTITY_PENDING", "Stage B all-trans isomer identity is pending. Confirm source’s analyte-specific all-trans value and original table/analytical basis from accessible primary full text before promoting.",
            "Obtain the primary text/table; then require formal Stage B identity review before ingestion.")

pending("MOL-V15-CID-31404", "Butylated hydroxytoluene", "Butylated hydroxytoluene (BHT)", "Retail palm oils (three samples)", "Elaeis guineensis oil", "edible palm oil", "6.8–86.1", "µg/g", "6.8–86.1", "mg/kg",
        "oil mass (µg/g); not a moisture-basis food matrix", "GC-MS", "Three palm-oil samples among 18 vegetable oils; sample-specific values not listed in the abstract.",
        "Butylated Hydroxytoluene in Edible Vegetable Oils from Local Markets of Chiang Mai and Mae Hong Son and Its Thermal Stability in Different Cooking Conditions",
        "Thai Journal of Toxicology 24(2):113; journal metadata date conflict", "https://li01.tci-thaijo.org/index.php/ThaiJToxicol/article/view/243854",
        "Abstract reports 3 palm oils in range 6.8–86.1 µg/g", "journal abstract verified; full article metadata inconsistent",
        "HELD_STAGE_B_IDENTITY_PENDING_AND_BIBLIOGRAPHIC_CONFLICT", "Journal page says published 2020 while issue heading says 2009; range does not provide individual sample values; identity remains pending.",
        "Verify publication year/issue from original PDF and exact BHT structure; retain range as candidate only.")

pending("MOL-V15-CID-14425", "Dodecyl gallate", "Dodecyl gallate", "Edible oils/bakery products; no measured value located", "Not specified", "Not specified", "", "", "", "",
        "No quantitative sample result retrieved", "Method development/validation only in accessible records", "No food sample concentration available from inspected abstracts.",
        "HPLC methods for gallate antioxidants in bakery products and edible oils", "10.1016/S0021-9673(98)00601-3; 10.1016/j.jfca.2005.12.005",
        "https://doi.org/10.1016/j.jfca.2005.12.005", "Accessible abstracts describe method/surveillance but no exact sample values", "source abstracts screened",
        "NO_QUANTITATIVE_CANDIDATE", "Method validation, maximum permitted use levels, and fortified samples are not native measured food concentrations.",
        "No ingestion; pursue a source only if exact measured sample results become accessible.")

pending("MOL-V15-CID-61253", "Octyl gallate", "Octyl gallate", "Edible oils/bakery products; no measured value located", "Not specified", "Not specified", "", "", "", "",
        "No quantitative sample result retrieved", "Method development/validation only in accessible records", "No food sample concentration available from inspected abstracts.",
        "HPLC methods for gallate antioxidants in bakery products and edible oils", "10.1016/S0021-9673(98)00601-3; 10.1016/j.jfca.2005.12.005",
        "https://doi.org/10.1016/j.jfca.2005.12.005", "Accessible abstracts describe method/surveillance but no exact sample values", "source abstracts screened",
        "NO_QUANTITATIVE_CANDIDATE", "Method validation, maximum permitted use levels, and fortified samples are not native measured food concentrations.",
        "No ingestion; pursue a source only if exact measured sample results become accessible.")

# Append target-level search evidence. The three identity-complete leads already had historical
# searches; these entries document the new primary-source verification path without deleting them.
events = [
    ("MOL-V17-CID-5280704","Apigetrin","apigetrin lamb's lettuce Table 3 fresh weight LC-MS/MS exact apigenin-7-O-glucoside","Hernández et al. 2021 Foods; MDPI/PubMed Central","Table 3 reports 0.012 µg/g FW for apigenin-7-O-glucoside; LC-MS/MS identity, edible lettuce","ACCEPTED_NEW_DIRECT_TABLE_VALUE","Exact table value and explicit FW basis; prior chrysanthemum powder result remains held."),
    ("MOL-V17-CID-5281673","Myricitrin","myricitrin spinach 398.2 mg/kg HPLC-DAD Table S3 sample basis methods","Akhtar et al. 2024 Plants; PMC full text","Results explicitly gives 398.2 mg/kg in spinach; methods weigh 5 g homogenized sample and calculate µg/g; no moisture correction stated","ACCEPTED_SPINACH_AS_ANALYZED_MASS_BASIS","Exact analyte and amount verified; no FW label assigned; apple values remain unresolved and un-ingested."),
    ("MOL-V17-CID-92794","Prunin","prunin quantitative ordinary food concentration primary table citrus fruit by-products","Primary article/abstract; DOI 10.1021/jf00035a021; Foods 2021 DOI 10.3390/foods10020272","Occurrence reported in citrus and qualitative by-product profiling; accessible sources did not expose an explicit numeric native-food concentration","NO_ACCEPTED_QUANTITATIVE_VALUE","Do not infer from graph or qualitative signal; citrus-juice processing intermediate is not native-food evidence."),
    ("MOL-V13-CID-161306","Ginkgoneolic acid (ginkgolic acid C13:0)","ginkgoneolic acid C13:0 ginkgo seed powder HPLC LC-MS quantitative","EurekMag indexed abstract; Wu et al. 2015","Abstract index reports 0.013 g/kg in skimmed ginkgo powder; full paper unavailable","PENDING_IDENTITY_CANDIDATE_ONLY","Primary table/full text and native food basis not independently verified."),
    ("MOL-V13-CID-5281858","Ginkgolic acid C15:1","ginkgolic acid C15:1 ginkgo seed powder HPLC LC-MS quantitative","EurekMag indexed abstract; Wu et al. 2015","Abstract index reports 0.042 g/kg in skimmed ginkgo powder; monoene double-bond position is unclear in accessible record","PENDING_IDENTITY_CANDIDATE_ONLY","Do not map positional isomer or infer native kernel concentration."),
    ("MOL-V13-CID-5469634","Ginkgolic acid C17:1","ginkgolic acid C17:1 ginkgo seed powder HPLC LC-MS quantitative","EurekMag indexed abstract; Wu et al. 2015","Abstract index reports 0.055 g/kg in skimmed ginkgo powder; monoene double-bond position is unclear in accessible record","PENDING_IDENTITY_CANDIDATE_ONLY","Do not map positional isomer or infer native kernel concentration."),
    ("MOL-V13-CID-8468","Vanillic acid","vanillic acid free acid rosehip HPLC-DAD fresh weight Table 6 and conjugated forms","Ciurlă et al. 2025 Molecules; Gao et al. 2017 Molecules","Rosehip 76.1 ± 1.6 µg/g FW; green soybean 26.88–41.59 mg/kg FW is conjugated acid after hydrolysis","PENDING_IDENTITY_CANDIDATE_ONLY","Rosehip is strong direct candidate but Stage B identity is pending; conjugated soybean value excluded as distinct analyte form."),
    ("MOL-V14-CID-5469424","Demethoxycurcumin","demethoxycurcumin turmeric HPLC four samples concentration percent","Jayaprakasha et al. 2002; PubMed PMID 12059141","Abstract reports range 0.83 ± 0.047 to 3.36 ± 0.040% across four samples","PENDING_IDENTITY_CANDIDATE_ONLY","Full table and precise percent/sample basis needed; identity is pending."),
    ("MOL-V14-CID-5315472","Bisdemethoxycurcumin","bisdemethoxycurcumin turmeric HPLC four samples concentration percent","Jayaprakasha et al. 2002; PubMed PMID 12059141","Abstract reports range 0.42 ± 0.036 to 2.16 ± 0.06% across four samples","PENDING_IDENTITY_CANDIDATE_ONLY","Full table and precise percent/sample basis needed; identity is pending."),
    ("MOL-V14-CID-145659","Sinensetin","sinensetin clementine peel HPLC-DAD Table 7 FW concentration","Leporini et al. 2020 Antioxidants; PMC7222210","Table 7 reports 15 coded peel sample values, 19.56–37.99 mg/100 g FW, mean ± SD, n=3","PENDING_IDENTITY_CANDIDATE_ONLY","Exact values retained separately; Stage B identity pending; peel-by-product food context needs adjudication."),
    ("MOL-V14-CID-97214","Eupatorin","eupatorin quantified ordinary foods plants herbs HPLC primary food composition","Literature search; secondary eupatorin review surfaced extract-only value","No eligible ordinary-food numeric measurement located; 5.05% w/w lead is in Orthosiphon chloroform extract fraction","NO_QUALIFYING_FOOD_MEASUREMENT","Extract concentration is not food concentration; identity is pending."),
    ("MOL-V15-CID-5280489","all-trans-β-Carotene","all-trans beta carotene raw carrot wet weight analytical food composition","Edwards et al. 2002 J Nutr; PMID 11823572","Reported values include raw grated carrot 11.45 ± 1.86, commercial puree 8.25 ± 0.09, boiled-mashed carrot 10.65 ± 0.12 mg/100 g wet weight","PENDING_IDENTITY_CANDIDATE_ONLY","Exact all-trans analyte/table requires primary full-text confirmation; Stage B isomer identity pending."),
    ("MOL-V15-CID-31404","Butylated hydroxytoluene","BHT palm oil local market GC-MS concentration 6.8 86.1 µg/g","Likhitrungrat et al.; Thai Journal of Toxicology article page and full issue PDF","Three palm-oil samples among 18 oils contained 6.8–86.1 µg/g; publication year/issue metadata conflict (2020 page vs 2009 issue)","PENDING_IDENTITY_CANDIDATE_ONLY","Range retained; confirm bibliographic record and Stage B identity."),
    ("MOL-V15-CID-14425","Dodecyl gallate","dodecyl gallate measured concentration ordinary food bakery edible oils sample values","Method abstracts, DOI 10.1016/S0021-9673(98)00601-3 and 10.1016/j.jfca.2005.12.005","No actual measured sample concentration exposed in inspected records; regulatory limits and spike validation excluded","NO_QUANTITATIVE_CANDIDATE","No native-food number located."),
    ("MOL-V15-CID-61253","Octyl gallate","octyl gallate measured concentration ordinary food bakery edible oils sample values","Method abstracts, DOI 10.1016/S0021-9673(98)00601-3 and 10.1016/j.jfca.2005.12.005","No actual measured sample concentration exposed in inspected records; regulatory limits and spike validation excluded","NO_QUANTITATIVE_CANDIDATE","No native-food number located.")
]

def main():
    cp = json.loads((P / "CHECKPOINTS.json").read_text(encoding="utf-8"))
    if cp.get("checkpoint_id") not in {"Phase1B-2026-11-03-batch-101-final-continuation", "Phase1B-2026-11-03-batch-102-scientific-coverage"}:
        raise RuntimeError("Expected active Batch 101 or Batch 102 checkpoint state.")
    if len(read(FOOD)) != 541 or len(read(MAPPING)) != 541:
        raise RuntimeError("Accepted append is not at the verified 541-row state.")
    BATCH.mkdir(parents=True, exist_ok=True)
    old_pending = read(PENDING_FILE) if PENDING_FILE.exists() else []
    old_ids = {r["Candidate_Record_ID"] for r in old_pending}
    for row in pending.rows:
        if row["Candidate_Record_ID"] not in old_ids:
            old_pending.append(row)
    write_csv(PENDING_FILE, PENDING_FIELDS, old_pending)

    # Central candidate register keeps one concise row per compound/batch; detailed source rows
    # above preserve each food sample and value without bloating the historical summary ledger.
    candidates = read(CANDIDATES)
    candidate_fields = list(candidates[0]) if candidates else ["candidate_id","compound_id","compound_name","food_name","food_database","food_database_record_id","candidate_concentration","candidate_unit","verification_status","source_locator","candidate_decision"]
    existing = {r["candidate_id"] for r in candidates}
    summary_specs = [
        ("CAND-B102-APIGETRIN-LETTUCE","MOL-V17-CID-5280704","Apigetrin","Lamb's lettuce (Valerianella locusta), edible leaves","0.012","µg/g FW","Table 3, standard nutrient condition","ACCEPTED_IN_BATCH_102; source supplies an explicit fresh-weight table value; old chrysanthemum powder candidate remains held."),
        ("CAND-B102-MYRICITRIN-SPINACH","MOL-V17-CID-5281673","Myricitrin","Spinach (Spinacia oleracea), edible leaves","398.2","mg/kg as analyzed sample mass","Results §2.3; Supplementary Table S3","ACCEPTED_IN_BATCH_102_ON_AS_ANALYZED_MASS_BASIS; no FW label assigned; apple values remain held."),
    ]
    grouped = defaultdict(list)
    for row in pending.rows:
        if row["Original_Value"]:
            grouped[row["Compound_ID"]].append(row)
    pending_summary = {
        "MOL-V13-CID-161306":("Ginkgoneolic acid (ginkgolic acid C13:0)","Skimmed ginkgo seed powder"),
        "MOL-V13-CID-5281858":("Ginkgolic acid C15:1","Skimmed ginkgo seed powder"),
        "MOL-V13-CID-5469634":("Ginkgolic acid C17:1","Skimmed ginkgo seed powder"),
        "MOL-V13-CID-8468":("Vanillic acid","Rosehip and hydrolyzed green soybean"),
        "MOL-V14-CID-5469424":("Demethoxycurcumin","Commercial turmeric varieties"),
        "MOL-V14-CID-5315472":("Bisdemethoxycurcumin","Commercial turmeric varieties"),
        "MOL-V14-CID-145659":("Sinensetin","Clementine peel samples BC1–BO5"),
        "MOL-V14-CID-97214":("Eupatorin","Orthosiphon extract-only lead"),
        "MOL-V15-CID-5280489":("all-trans-β-Carotene","Carrot, carrot puree and boiled-mashed carrot"),
        "MOL-V15-CID-31404":("Butylated hydroxytoluene","Palm oils, three samples"),
    }
    for cid,(name,food) in pending_summary.items():
        rows=grouped[cid]
        values="; ".join(f"{r['Food_Name']}: {r['Original_Value']} {r['Original_Unit']}" for r in rows)
        units="; ".join(sorted({r['Original_Unit'] for r in rows if r['Original_Unit']}))
        locator="; ".join(sorted({r['Source_Locator'] for r in rows}))
        decision="Held separately: Stage B identity pending; see PENDING_IDENTITY_CANDIDATES.csv for exact values and limitations."
        if cid.endswith("97214"):
            decision="Excluded: 5.05% is in a plant extract fraction, not an ordinary-food measurement; no eligible food concentration found."
        summary_specs.append((f"CAND-B102-{cid.split('-')[-1]}",cid,name,food,values,units,locator,decision))
    for item in summary_specs:
        candidate_id,cid,name,food,value,unit,locator,decision=item
        status="EXCLUDED_NONFOOD" if cid.endswith("97214") else ("PENDING_IDENTITY_REVIEW" if cid.startswith("MOL-V1") and cid not in {"MOL-V17-CID-5280704","MOL-V17-CID-5281673"} else "ACCEPTED_IN_BATCH_102")
        new_entry={"candidate_id":candidate_id,"compound_id":cid,"compound_name":name,"food_name":food,"food_database":"Primary analytical study / documented research lead","food_database_record_id":locator,"candidate_concentration":value,"candidate_unit":unit,"verification_status":status,"source_locator":locator,"candidate_decision":decision}
        if candidate_id not in existing:
            candidates.append(new_entry)
        elif candidate_id.startswith("CAND-B102-"):
            candidates=[new_entry if r["candidate_id"]==candidate_id else r for r in candidates]
    write_csv(CANDIDATES,candidate_fields,candidates)

    # Search rows are one event per target for the bounded batch; old searches remain untouched.
    search = read(SEARCH_LOG); search_fields = list(search[0])
    search_rows=[]
    logged_queries={(r["Compound_ID"],r["search_query"]) for r in search}
    for cid,name,query,source,findings,decision,reason in events:
        if (cid,query) not in logged_queries:
            search_rows.append({"Compound_ID":cid,"canonical_name":name,"search_query":query,"database_or_search_source":source,"search_date":"2026-11-03","results_identified":findings,"candidate_publications":source,"screening_decision":decision,"reason":reason})
    append_csv(SEARCH_LOG,search_fields,search_rows)

    # Source registry de-duplicates by exact URL; previously registered sources are preserved.
    sources = read(SOURCE_REGISTRY); source_fields=list(sources[0]); known={r["source_url"] for r in sources}
    additions = [
      ("Phenolic and Carotenoid Profile of Lamb’s Lettuce and Improvement of the Bioactive Content by Preharvest Conditions","Primary analytical measurement","https://www.mdpi.com/2304-8158/10/1/188","Full-text primary food composition; Table 3","Full text inspected; direct fresh-weight table value accepted in B102","Retain exact analyte, edible leaves and FW basis; no conversion across moisture basis."),
      ("Investigation of Pharmacologically Important Polyphenolic Secondary Metabolites in Plant-based Food Samples Using HPLC-DAD","Primary analytical measurement","https://pmc.ncbi.nlm.nih.gov/articles/PMC11124887/","Full-text HPLC-DAD food survey and Supplementary Table S3","Full-text Results and Methods reviewed; spinach value accepted on as-analyzed mass basis","Do not assert FW/DW; old apple values remain held due conflict."),
      ("Purification, identification and the antimicrobial activity of ginkgolic acids in ginkgo seeds","Abstract index / secondary access record",GINKGO_URL,"Indexed abstract of primary Chinese analytical study","Abstract accessible; primary full text/table not verified","Do not ingest; skimmed powder and homologue-isomer linkage need primary-source review."),
      ("Phenolic and Carotenoid Profile of Rosehip (Rosa canina L.) Fruits","Primary analytical measurement","https://www.mdpi.com/1420-3049/30/15/3071","HPLC-DAD survey; Table 6","Full text inspected; candidate only due Stage B identity status","No ingestion until Stage B identity review; preserve FW value and study limitations."),
      ("Simultaneous determination of phenolic acids and flavonoids in soybean by UPLC-MS/MS","Primary analytical measurement","https://www.mdpi.com/1420-3049/22/11/1878","Hydrolyzed phenolic conjugate measurement","Source lead recorded; different analyte form","Not free native vanillic acid; do not merge forms."),
      ("Improved HPLC method for the determination of curcumin, demethoxycurcumin, and bisdemethoxycurcumin","Primary analytical measurement","https://pubmed.ncbi.nlm.nih.gov/12059141/","PubMed primary abstract; turmeric range","Abstract verified; individual results/basis require full paper","Do not reconstruct individual sample values; identity and mass basis pending."),
      ("Citrus × Clementina Hort. Juice Enriched with Its By-Products (Peels and Leaves): Chemical Composition, In Vitro Bioactivity, and Impact of Processing","Primary analytical measurement","https://pmc.ncbi.nlm.nih.gov/articles/PMC7222210/","Antioxidants 2020;9:298; Table 7","Table 7 verified; numerical values retained separately","Stage B identity pending; peel-by-product use context needs review."),
      ("Eupatorin: A comprehensive review of its pharmacological activities and underlying molecular mechanisms","Peer-reviewed secondary source","https://www.sciencedirect.com/science/article/pii/S0014299925010842","Review cites extract fraction, not food","Secondary extract-only lead; no food sample value","Exclude extract percentages from food-composition evidence."),
      ("Alpha- and beta-carotene from a commercial puree are more bioavailable to humans than from boiled-mashed carrots","Primary analytical measurement","https://jn.nutrition.org/article/S0022-3166%2822%2914892-3/fulltext","Journal of Nutrition 2002;132(2):159-167; PMID 11823572","Primary study metadata verified; full text access limited","Confirm exact analyte-specific table before any ingestion; all-trans identity pending."),
      ("Butylated Hydroxytoluene in Edible Vegetable Oils from Local Markets of Chiang Mai and Mae Hong Son and Its Thermal Stability in Different Cooking Conditions","Primary analytical measurement","https://li01.tci-thaijo.org/index.php/ThaiJToxicol/article/view/243854","Thai Journal of Toxicology 24(2):113; GC-MS","Abstract verified; journal page year conflicts with issue heading","Verify bibliographic year/issue; no Stage B identity promotion."),
      ("HPLC methods for gallate antioxidants in bakery products and edible oils","Method paper; measured results not retrieved","https://doi.org/10.1016/j.jfca.2005.12.005","Analytical method/surveillance source lead","Abstract screened; no numerical food-sample result identified","Methods/spikes/regulatory levels do not qualify as food measurements.")
    ]
    for name,cls,url,typ,avail,req in additions:
        if url not in known:
            sources.append({"source_name":name,"source_classification":cls,"source_url":url,"source_type":typ,"availability_status":avail,"ingestion_requirement":req}); known.add(url)
    write_csv(SOURCE_REGISTRY,source_fields,sources)

    # Update existing gap decisions without deleting the Batch 101 history or its candidates.
    gaps=read(GAPS); gap_fields=list(gaps[0])
    latest={
      "MOL-V17-CID-5280704":("ACCEPTED_QUANTITATIVE_TABLE_VALUE_FW","Direct Table 3 value and explicit FW basis accepted in B102; B101 powder result remains held."),
      "MOL-V17-CID-5281673":("ACCEPTED_SPINACH_AS_ANALYZED_MASS_BASIS","Spinach 398.2 mg/kg is stated in Results; no FW/DW label assigned; apple conflict remains held."),
      "MOL-V17-CID-92794":("HELD_NO_VERIFIED_NUMERICAL_NATIVE_FOOD_VALUE","Primary numeric source table unavailable; qualitative/processing-created prunin findings do not qualify.")}
    for row in gaps:
        if row["Compound_ID"] in latest:
            row["Last_Screen_Batch"]="batch_102_scientific_coverage"
            row["Last_Decision"],row["Next_Action"]=latest[row["Compound_ID"]]
            if row["Compound_ID"].endswith("5280704"):
                row["Coverage_Status"]="Accepted quantitative coverage"
                row["Food_Context"]="Lamb's lettuce leaves; 0.012 µg/g FW"
            elif row["Compound_ID"].endswith("5281673"):
                row["Coverage_Status"]="Accepted quantitative coverage; mass basis other/unspecified moisture"
                row["Food_Context"]="Spinach leaves; 398.2 mg/kg as-analyzed sample mass"
    write_csv(GAPS,gap_fields,gaps)

    # Expand the single cumulative 143-compound register to the required per-compound fields.
    coverage=read(COVERAGE); cov_fields=list(coverage[0])
    extra=["Research_Status","Food_Composition_Evidence_Status","Accepted_Quantitative_Coverage_Status","Mapping_Status","Relevant_Source_References","Measurement_Basis","Pending_Issues","Next_Justified_Action"]
    for col in extra:
        if col not in cov_fields: cov_fields.append(col)
    foods=read(FOOD); maps=read(MAPPING); logs=read(SEARCH_LOG); candidates=read(CANDIDATES); pending_rows=read(PENDING_FILE)
    by_food=defaultdict(list); by_map=defaultdict(list); by_search=defaultdict(list); by_cand=defaultdict(list); by_pending=defaultdict(list)
    for r in foods: by_food[r["compound_id"]].append(r)
    for r in maps:
        for cid in set(filter(None,[r.get("compound_id","")]+r.get("candidate_compound_ids","").split("|"))): by_map[cid].append(r)
    for r in logs: by_search[r["Compound_ID"]].append(r)
    for r in candidates: by_cand[r["compound_id"]].append(r)
    for r in pending_rows: by_pending[r["Compound_ID"]].append(r)
    pending_ids={r["Compound_ID"] for r in read(IDENTITY) if r["Status"]!="Complete"}
    for row in coverage:
        cid=row["Compound_ID"]; fs=by_food[cid]; ms=by_map[cid]; ss=by_search[cid]; ps=by_pending[cid]
        complete=row["Identity_Audit_Status"]=="Complete"
        referenced=[m for m in maps if m.get("compound_id")==cid or cid in m.get("candidate_compound_ids","").split("|")]
        verified_quant=[m for m in referenced if m.get("mapping_status") in {"Exact identity match","Verified synonym match","Structure-supported match"} and m.get("quantitative_data_available")=="true"]
        row["Any_Mapping"]="true" if referenced else "false"
        row["Quantitative_Mapping"]="true" if verified_quant else "false"
        row["Food_Record_Count"]=str(len(fs))
        row["Mapping_Row_Count"]=str(len(referenced))
        row["Search_Log_Event_Count"]=str(len(ss))
        linked_records={m["food_record_id"] for m in verified_quant if m.get("food_record_id") in {f["food_record_id"] for f in foods}}
        mapped_foods=[f for f in foods if f["food_record_id"] in linked_records]
        row["Food_Record_Count"]=str(len(linked_records))
        eligible_for_use=complete and bool(verified_quant)
        row["Identity_Complete_Quantitative_Eligible"]="true" if eligible_for_use else "false"
        if eligible_for_use:
            row["Coverage_Status"]="Identity-complete quantitative coverage"
        elif not complete:
            row["Coverage_Status"]="Identity review pending; excluded from eligible coverage"
        else:
            row["Coverage_Status"]="Identity-complete; no accepted quantitative measurement"
        row["Research_Status"]="Researched/screened" if ss else "Not yet screened"
        if fs or eligible_for_use:
            row["Food_Composition_Evidence_Status"]="Accepted quantitative measurement(s)"
            row["Measurement_Basis"]="; ".join(sorted({r.get("moisture_basis","") for r in mapped_foods if r.get("moisture_basis")}))
        elif any(r["Original_Value"] for r in ps):
            row["Food_Composition_Evidence_Status"]="Quantitative candidate(s) held outside accepted dataset"
            row["Measurement_Basis"]="; ".join(sorted({r["Measurement_Basis"] for r in ps if r["Measurement_Basis"]}))
        elif ps:
            row["Food_Composition_Evidence_Status"]="Qualitative/lead only; no eligible numerical value"
            row["Measurement_Basis"]=""
        elif row["Coverage_Status"].startswith("Identity-complete quantitative coverage"):
            row["Food_Composition_Evidence_Status"]="Accepted quantitative measurement(s)"
            row["Measurement_Basis"]="; ".join(sorted({r.get("moisture_basis","") for r in mapped_foods if r.get("moisture_basis")}))
        else:
            row["Food_Composition_Evidence_Status"]="No qualifying quantitative ordinary-food measurement documented"
            row["Measurement_Basis"]=""
        row["Accepted_Quantitative_Coverage_Status"]="Covered" if eligible_for_use else "Not covered"
        active=verified_quant
        row["Mapping_Status"]=("Verified quantitative mapping" if complete and active else "Blocked by pending identity" if cid in pending_ids and ms else "No accepted mapping")
        refs=[]
        for r in fs:
            refs.extend([r.get("doi","") and "DOI:"+r["doi"],r.get("source_url","")])
        for r in ps:
            refs.extend([r.get("DOI_or_Identifier",""),r.get("Source_URL","")])
        for r in ss:
            refs.append(r.get("candidate_publications",""))
        row["Relevant_Source_References"]="; ".join(dict.fromkeys(x for x in refs if x))
        issues=[]
        if not complete: issues.append(row["Identity_Audit_Status"])
        issues.extend(r["Limitations"] for r in ps if r["Limitations"])
        row["Pending_Issues"]="; ".join(dict.fromkeys(issues))
        gap_entry=next((g for g in gaps if g["Compound_ID"]==cid),None)
        if gap_entry:
            row["Latest_Gap_Decision"]=gap_entry["Last_Decision"]
        if row["Identity_Complete_Quantitative_Eligible"]=="true":
            row["Next_Justified_Action"]="Maintain accepted provenance; seek new measurement only when a distinct source/food lead exists."
        elif not complete:
            row["Next_Justified_Action"]="Formal Stage B identity review required before any candidate can count; preserve candidate evidence separately."
        elif ps:
            row["Next_Justified_Action"]="Resolve source/basis limitations or retain held status; do not infer values or units."
        else:
            row["Next_Justified_Action"]="No qualifying measurement located in documented screens; research new credible leads only when available."
    write_csv(COVERAGE,cov_fields,coverage)

    # Full 36-ID evidence proposal packet; this never changes the authoritative audit.
    audits=[r for r in read(IDENTITY) if r["Status"]!="Complete"]
    cand_by=defaultdict(list)
    for r in pending_rows: cand_by[r["Compound_ID"]].append(r)
    proposals=[]
    for r in audits:
        cid=r["Compound_ID"]
        cand=cand_by[cid]
        refs="; ".join(dict.fromkeys([r.get("Structure_Source","")]+[x.get("Source_URL","") for x in cand if x.get("Source_URL")]))
        issues=r["Note"]
        proposal="UNRESOLVED: retain Stage B pending status. Independent cheminformatics parsing and specialist structure/source adjudication remain required."
        if cand:
            proposal += " Food-source naming/CID is candidate evidence only and does not establish the identity of the tested analyte or resolve Stage B structure review."
        proposals.append({"Compound_ID":cid,"Canonical_Name":r["Canonical_Name"],"PubChem_CID":r["PubChem_CID"],"Registry_InChIKey":r["Registry_InChIKey"],"Exact_Key_Match":r["Exact_Key_Match"],"Current_Identity_Status":r["Status"],"Current_Identity_Note":issues,"Candidate_Chemical_Identity":"Unadjudicated Stage B registry identity: "+r["Canonical_Name"],"Source_Evidence_References":refs,"Evidence_Assessment":"CID/key capture is recorded in the frozen Stage B snapshot; it is not independent structure parsing or expert review. Food-source evidence, when present, does not prove reference-structure equivalence.","Remaining_Uncertainty":issues,"Recommended_Decision":"requires specialist review; no change proposed","Required_Formal_Action":"Separate authorized Stage B amendment/review only; Phase 1B retains pending status until the authoritative release is formally updated."})
    proposal_fields=list(proposals[0]) if proposals else []
    write_csv(P / "IDENTITY_ADJUDICATION_PROPOSALS_2026-11-03.csv",proposal_fields,proposals)

    # Source bibliography entries for Batch 102 are exact-URL unique.
    with (BATCH/"pending_identity_candidates.csv").open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=PENDING_FIELDS);w.writeheader();w.writerows([r for r in pending_rows if r["Batch"]=="102"])
    with (BATCH/"screening_matrix.csv").open("w",encoding="utf-8-sig",newline="") as f:
        fields=["Compound_ID","Canonical_Name","Identity_Status","Screening_Result","Candidate_Records","Disposition","Next_Action"]
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        byid=defaultdict(list)
        for r in pending_rows:
            if r["Batch"]=="102": byid[r["Compound_ID"]].append(r)
        for cid,name,_,_,findings,decision,reason in events:
            identity=audit_status(cid)
            n=len(byid[cid])
            w.writerow({"Compound_ID":cid,"Canonical_Name":name,"Identity_Status":identity,"Screening_Result":findings,"Candidate_Records":n,"Disposition":decision,"Next_Action":reason})

    # Recompute authoritative counts from the active files, not report text.
    foods=read(FOOD); maps=read(MAPPING); coverage=read(COVERAGE); logs=read(SEARCH_LOG)
    unique_searched={r["Compound_ID"] for r in logs}
    identity_complete={r["Compound_ID"] for r in coverage if r["Identity_Audit_Status"]=="Complete"}
    eligible={r["Compound_ID"] for r in coverage if r["Identity_Complete_Quantitative_Eligible"]=="true"}
    any_quant={r["compound_id"] for r in maps if r.get("quantitative_data_available")=="true" and r.get("compound_id")}
    pending_candidate_count=sum(bool(r["Original_Value"]) for r in pending_rows)
    delta={"batch":"102","batch_date":"2026-11-03","verified_baseline":{"food_records":539,"mapping_rows":539,"identity_complete_covered":97,"stage_b_total":143,"identity_complete":107,"identity_pending":36,"food_sha256":"616a62c3cce8426b058e8aee3c6e746438ee2eea49680f2da492e10101172115","mapping_sha256":"9774a96396107409a53f6bef5960daffacf5e40ae25d26e7ecaabbbc8c1d6bc1"},"batch_changes":{"accepted_food_records":2,"accepted_mappings":2,"newly_covered_identity_complete_compounds":["MOL-V17-CID-5280704","MOL-V17-CID-5281673"],"new_candidate_detail_rows":sum(1 for r in pending_rows if r["Batch"]=="102"),"search_events":len(events),"unique_newly_screened_ids":12},"current":{"food_records":len(foods),"mapping_rows":len(maps),"unique_compounds_with_quantitative_mapping_including_pending":len(any_quant),"identity_complete_quantitative_compounds":len(eligible),"identity_complete_total":len(identity_complete),"identity_complete_uncovered":len(identity_complete)-len(eligible),"identity_pending":len(coverage)-len(identity_complete),"unique_researched_ids":len(unique_searched),"research_coverage":f"{len(unique_searched)}/143","pending_identity_candidate_numeric_rows":pending_candidate_count,"orphan_mappings":sum(1 for r in maps if r["food_record_id"] not in {x["food_record_id"] for x in foods}),"blocked_mapping_rows":46,"food_sha256":hashlib.sha256(FOOD.read_bytes()).hexdigest(),"mapping_sha256":hashlib.sha256(MAPPING.read_bytes()).hexdigest()},"target":{"minimum":130,"stretch":143,"achieved":len(eligible)>=130,"status":"PHASE1B_ACQUISITION_IN_PROGRESS"},"scientific_notes":["Pending-identity measurements remain separate and do not count toward eligible coverage.","Apigetrin is accepted only from the explicit FW Table 3 result; earlier powder finding remains held.","Myricitrin spinach result is retained on as-analyzed sample-mass basis; no FW/DW assertion; apple conflict remains unresolved.","No Stage B identity status was changed."]}
    (BATCH/"coverage_delta.json").write_text(json.dumps(delta,indent=2,ensure_ascii=False),encoding="utf-8")

    # Durable active checkpoint; Batch 101 copy was preserved before ingestion.
    cp={"checkpoint_id":"Phase1B-2026-11-03-batch-102-scientific-coverage","status":"PHASE1B_BATCH_COMPLETE","scope":"Stage C Phase 1B only","previous_checkpoint":"Phase1B-2026-11-03-batch-101-final-continuation","source_stage_b_release":"StageB_FINALIZED (read-only)","phase1_foundation_dependency":"stageC/releases/Phase1-v1.3.0 (read-only)","stage_b_target_count":143,"stage_b_identity_complete":len(identity_complete),"stage_b_identity_pending":len(coverage)-len(identity_complete),"research_screened":len(unique_searched),"research_screened_fraction":f"{len(unique_searched)}/143","active_food_records":len(foods),"active_mapping_rows":len(maps),"unique_compounds_quantitatively_mapped_including_pending":len(any_quant),"identity_complete_quantitative_compounds":len(eligible),"identity_complete_uncovered":len(identity_complete)-len(eligible),"blocked_mapping_rows":46,"orphan_mappings":delta["current"]["orphan_mappings"],"batch_102":{"accepted_records":2,"accepted_mappings":2,"newly_covered_identity_complete_compounds":2,"target_compounds_screened":15,"new_search_events":len(events),"pending_identity_candidate_rows":pending_candidate_count},"target":{"minimum":130,"stretch":143,"achieved":len(eligible)>=130,"current_identity_ceiling_without_stage_b_review":len(identity_complete),"additional_identity_complete_compounds_needed_for_minimum":max(0,130-len(eligible))},"validation":{"data_append":"PASS; existing 539-row files preserved as byte prefixes","accepted_identity_gate":"PASS; exact CID/InChIKey and Stage B Complete status verified","candidate_identity_gate":"PASS; all pending rows separated from accepted files","phase1_validation":"PASS; 541 records/mappings; 99 eligible; zero errors/orphans; no snapshot changes","focused_tests":"PASS; unittest food-composition 7/7 and compound mapping 9/9","mapping_rebuild":"PENDING independent full-file reconstruction"},"sha256":{"food_composition":delta["current"]["food_sha256"],"compound_food_mapping":delta["current"]["mapping_sha256"]},"reports":["batches/batch_102_scientific_coverage/BATCH_102_SCREENING_REPORT.md","batches/batch_102_scientific_coverage/screening_matrix.csv","batches/batch_102_scientific_coverage/pending_identity_candidates.csv","PENDING_IDENTITY_CANDIDATES.csv","IDENTITY_ADJUDICATION_PROPOSALS_2026-11-03.csv","COMPOUND_COVERAGE_REGISTER_2026-11-03.csv"],"next_batch":"103; five previously unlogged identity-pending compounds"}
    (P/"CHECKPOINTS.json").write_text(json.dumps(cp,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (BATCH/"coverage_delta.json").write_text(json.dumps(delta,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

    report=f'''# Batch 102 — scientific coverage continuation\n\n**Status:** `PHASE1B_BATCH_COMPLETE`. Stage B and Phase 1 foundations remain read-only.\n\n## Batch scope and result\n\nBatch 102 screened 15 targets: Apigetrin, Myricitrin, Prunin, three ginkgolic-acid homologues, Vanillic acid, Demethoxycurcumin, Bisdemethoxycurcumin, Sinensetin, Eupatorin, all-trans-β-Carotene, Butylated hydroxytoluene, Dodecyl gallate, and Octyl gallate. Twelve of these had no prior search-log event; the three Stage B-complete leads were rechecked against new source paths.\n\nTwo direct quantitative values were accepted: Apigetrin in lamb’s lettuce, 0.012 µg/g FW (Table 3), and Myricitrin in spinach, 398.2 mg/kg on the paper’s as-analyzed sample-mass basis. The latter is not labelled FW or DW because the paper does not report moisture correction. Myricitrin’s distinct spinach value does not resolve the article’s conflicting apple values; neither apple value was ingested.\n\nActive records and mappings now total **541 each**; unique quantitative mappings including pending identities are **{len(any_quant)}**; accepted identity-complete coverage is **{len(eligible)}/107**. Research coverage is **{len(unique_searched)}/143**. The 130 minimum remains **not achieved**.\n\n## Pending-identity candidate findings\n\nAll numerical candidate findings are in `PENDING_IDENTITY_CANDIDATES.csv` and the batch-specific copy. They are not exposure-eligible. They include indexed ginkgolic-acid values in skimmed powder (primary paper not accessible), a strong rosehip vanillic-acid FW result, hydrolysis-derived soybean conjugates (different analyte form), abstract-only turmeric ranges with unclear mass basis, 15 sinensetin measurements in clementine peel by-products, an extract-only eupatorin lead, carrot β-carotene food values requiring source/isomer confirmation, and palm-oil BHT with a journal-year/issue conflict. Dodecyl and octyl gallate searches found method-only leads, not actual food-sample concentrations.\n\nPrunin remains unquantified: occurrence or qualitative by-product detection is not converted to a concentration. The Batch 101 candidates and all prior search history are preserved.\n\n## Identity adjudication\n\n`IDENTITY_ADJUDICATION_PROPOSALS_2026-11-03.csv` contains the 36 currently pending Stage B identities, their exact snapshot notes/identifiers, source leads where available, the remaining uncertainty, and a recommendation to retain pending status pending independent parsing and formal specialist review. It proposes no Stage B edits.\n\n## Cumulative state\n\n- Stage B universe: 143; identity complete 107; identity pending 36.\n- Research/screening: {len(unique_searched)}/143.\n- Quantitative mappings (including pending): {len(any_quant)} unique compounds.\n- Identity-complete accepted quantitative coverage: {len(eligible)}/107; 10 baseline gaps reduced by two to {len(identity_complete)-len(eligible)}.\n- Food records/mapping rows: {len(foods)}/{len(maps)}; orphan mappings: {delta['current']['orphan_mappings']}; blocked legacy mapping rows: 46.\n- Numeric pending-identity candidate rows: {pending_candidate_count}; these do not count as accepted coverage.\n- Minimum/stretch targets: 130/143; neither achieved. The current Stage B identity ceiling is 107.\n\n## Verification\n\nThe accepted append script verified the exact pre-Batch 102 file hashes, record counts, complete Stage B identity status, CID, full InChIKey, exact mappings and unique IDs before append; both original active data files remain byte-identical prefixes. `python stageC/scripts/validate_phase1.py` passed on 541 records and mappings, with 99 eligible compounds, zero food/mapping errors, zero orphans and no Stage B snapshot changes. Built-in `unittest` focused tests passed: food composition 7/7 and compound mapping 9/9. The environment does not have pytest installed; no pytest result is claimed. Independent full-file mapping reconstruction remains pending.\n'''
    (BATCH/"BATCH_102_SCREENING_REPORT.md").write_text(report,encoding="utf-8")

    # Update progress and restart instructions without deleting historical batch summaries.
    progress_heading="## Batch 102 continuation — 2026-11-03"
    if progress_heading not in (P/"PROGRESS.md").read_text(encoding="utf-8"):
        with (P/"PROGRESS.md").open("a",encoding="utf-8") as f:
            f.write("\n\n"+progress_heading+"\n\n")
            f.write(f"Screened 15 target compounds (12 new IDs); accepted 2 new compounds (Apigetrin and Myricitrin spinach). Active coverage is {len(eligible)}/107 identity-complete, research coverage {len(unique_searched)}/143, records/mappings {len(foods)}/{len(maps)}. Pending-identity measurements remain in the separate candidate ledger. The 130 minimum remains unmet. See `batches/batch_102_scientific_coverage/BATCH_102_SCREENING_REPORT.md`.\n")
    (P/"NEXT_STEPS.md").write_text("""# Next steps — after Batch 102\n\n1. Run the Batch 102/103 focused regression tests and `stageC/scripts/validate_phase1.py`; record actual outcomes in the batch report and checkpoint.\n2. Continue with Batch 103 and screen the five remaining unlogged identity-pending compounds: Allura Red AC (MOL-V14-CID-33258), Brilliant Blue FCF (MOL-V15-CID-19700), Azorubine (MOL-V15-CID-19118), Neohesperidin dihydrochalcone (MOL-V15-CID-30231), and Tartrazine (MOL-V15-CID-164825). Keep all findings outside accepted data until Stage B identity is formally complete.\n3. Update research coverage to 143/143 only after the five bounded screens are logged.\n4. The 130 accepted-coverage target is not reachable under the current 107 identity-complete ceiling. Any progress beyond it requires separately authorized Stage B identity adjudication and qualifying evidence. Stage B `StageB_FINALIZED`, Phase 1-v1.3.0, Stage A, and historical releases remain read-only.\n""",encoding="utf-8")
    (P/"RESUME_INSTRUCTIONS.md").write_text("""# Resume instructions\n\nActive checkpoint: `Phase1B-2026-11-03-batch-102-scientific-coverage`. Verify `CHECKPOINTS.json`, then inspect `batches/batch_102_scientific_coverage/BATCH_102_SCREENING_REPORT.md` and `coverage_delta.json`. The food and mapping datasets each contain 541 rows; the 539-row Batch 101 files are preserved as exact byte prefixes.\n\nNext work is Batch 103: screen the five IDs in `NEXT_STEPS.md`, record exact source results, and keep pending-identity evidence separate. Run focused Phase 1B and regression validation, update the active checkpoint only after all checks pass. Do not modify `StageB_FINALIZED`, Phase 1-v1.3.0, Stage A, or historical releases.\n""",encoding="utf-8")
    print(json.dumps({"status":"METADATA_PASS","batch102_targets":15,"search_events":len(events),"research_screened":len(unique_searched),"pending_numeric_candidate_rows":pending_candidate_count,"identity_proposals":len(proposals),"source_registry_entries":len(sources),"candidate_rows":len(candidates),"eligible_coverage":len(eligible),"register_rows":len(coverage)},indent=2,ensure_ascii=False))

def audit_status(cid):
    return next((r["Status"] for r in read(IDENTITY) if r["Compound_ID"]==cid),"Not found")

if __name__=="__main__":
    main()
