"""Controlled expansion batch 005: two independently sourced primary tables.

This script deliberately accepts only direct raw/cooked, individual-analyte
pairs.  It reads Batch 004 and writes only this new package.
"""
from pathlib import Path
import hashlib
import json
import pandas as pd

R = Path(__file__).resolve().parent
PARENT = R.parent / "batch_004" / "updated_master_dataset.csv"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, text):
    (R / name).write_text(text.strip() + "\n", encoding="utf-8")


base = pd.read_csv(PARENT)


def template(name):
    found = base.loc[base.compound.astype(str).str.casefold().eq(name.casefold())]
    assert len(found), name
    return found.iloc[0]


def make_row(src, *, obs_id, doi, paper_id, locator, compound, food, method,
             normalized, medium, raw, cooked, raw_sd, cooked_sd, unit, basis,
             temp, minutes, detail, replicates, analytical_definition):
    row = {column: src[column] for column in base.columns}
    row.update({
        "observation_id": obs_id,
        "original_record_id": "",
        "doi": doi,
        "paper_id": paper_id,
        "source_locator": locator,
        "compound": compound,
        "food_matrix": food,
        "cooking_method": method,
        "cooking_method_normalized": normalized,
        "cooking_medium": medium,
        "raw_concentration": raw,
        "cooked_concentration": cooked,
        "concentration_unit": unit,
        "measurement_basis": basis,
        "target_name": "apparent_concentration_ratio_percent",
        "target_equation": "100 * C_cooked / C_raw",
        "target_value_percent": 100 * cooked / raw,
        "target_semantics": "apparent concentration ratio; not total-mass retention",
        "evidence_status": "VERIFIED_PRIMARY_TABLE",
        "cooked_yield_status": "NOT_REPORTED",
        "total_mass_retention_status": "NOT_ESTABLISHED",
        "source_detail": detail,
        "Temperature_C": temp,
        "Cooking_Time_min": minutes,
        "raw_sd": raw_sd,
        "cooked_sd": cooked_sd,
        "reported_replicate_design": replicates,
        "analytical_definition": analytical_definition,
    })
    return row


rows = []

# Kongphapa et al., primary Table 4.  Values are explicitly individual
# HPLC-DAD compounds, mg/100 g dry weight, mean +/- SD of triplicate
# experiments.  The raw and cooked material was both dried before analysis;
# source processing is kept in the cooking/protocol fields rather than
# pretending this is fresh-weight evidence.
chaya = {
    "Protocatechuic Acid": (67.98, 1.94, 20.25, 1.10),
    "Chlorogenic Acid": (82.14, 4.61, 7.31, 1.64),
    "Caffeic acid": (561.71, 27.66, 406.98, 16.55),
    "Syringic acid": (70.71, 5.10, 225.00, 8.77),
    "p-Coumaric acid": (3.86, 2.04, 6.75, 1.73),
    "Ferulic Acid": (5.25, 2.58, 0.86, 0.02),
    "Sinapic acid": (784.50, 20.76, 112.50, 6.88),
    "Rutin": (52.00, 0.06, 123.03, 6.99),
    "Quercetin": (95.36, 3.11, 9.55, 0.34),
}
for compound, (raw, raw_sd, cooked, cooked_sd) in chaya.items():
    src = template(compound)
    safe = compound.upper().replace(" ", "_").replace("-", "_")
    rows.append(make_row(
        src, obs_id=f"LIT-KONGPHAPA2022-CHAYA_LEAF-{safe}-BOILING",
        doi="10.14456/apst.2022.5", paper_id="NEW_LITERATURE_KONGPHAPA_2022",
        locator="Table 4; Methods §§2.1 and 2.7",
        compound=compound, food="Chaya leaf (Cnidoscolus chayamansa)",
        method="Boiling", normalized="boiling", medium="water; volume not reported",
        raw=raw, cooked=cooked, raw_sd=raw_sd, cooked_sd=cooked_sd,
        unit="mg/100 g dry weight", basis="dry weight (DW)", temp=100, minutes=15,
        detail="Kongphapa et al. (2022), Table 4. Individual HPLC-DAD analyte in raw versus boiled-then-dried chaya leaves; table reports mg/100 g dry weight and mean ± SD.",
        replicates="Triplicate experiments; one dataset row for the treatment mean",
        analytical_definition="Individual HPLC-DAD analyte; milled dried leaf material",
    ))

# Kayahan and Saloglu, primary Table 4.  The table labels the unit mg/kg but
# does not state a shared FW/DW basis for this HPLC table.  That ambiguity is
# preserved explicitly, never converted or relabelled.  Only chlorogenic acid
# has a pre-existing exact descriptor identity; the other individual analytes
# are logged as identity-schema exclusions below.
artichoke = {
    "Sakiz": (2484.0, [("Boiling", "boiling", 46869.0, 590.0), ("Microwave cooking", "microwave", 41582.0, 237.0), ("Baking", "baking", 72030.0, 494.0)]),
    "Bayrampasa": (1016.0, [("Boiling", "boiling", 40096.0, 562.0), ("Microwave cooking", "microwave", 59263.0, 160.0), ("Baking", "baking", 29866.0, 324.0)]),
}
for cultivar, (raw, treatments) in artichoke.items():
    for method, normalized, cooked, cooked_sd in treatments:
        src = template("Chlorogenic Acid")
        safe_method = normalized.upper().replace(" ", "_")
        rows.append(make_row(
            src, obs_id=f"LIT-KAYAHAN2021-ARTICHOKE_{cultivar.upper()}_RECEPTACLE-CHLOROGENIC_ACID-{safe_method}",
            doi="10.3389/fsufs.2021.761145", paper_id="NEW_LITERATURE_KAYAHAN_2021",
            locator="Table 4 (receptacle rows); Methods: artichoke sample preparation and HPLC",
            compound="Chlorogenic Acid", food=f"Artichoke receptacle (Cynara scolymus cv. {cultivar})",
            method=method, normalized=normalized,
            medium="boiling/baking medium not reported; microwave conditions not reported",
            raw=raw, cooked=cooked, raw_sd=pd.NA, cooked_sd=cooked_sd,
            unit="mg/kg", basis="as reported (basis unspecified)", temp=pd.NA, minutes=pd.NA,
            detail="Kayahan and Saloglu (2021), Table 4. HPLC-DAD individual chlorogenic-acid receptacle values, mg/kg as reported; the table does not state fresh- or dry-weight basis, which is preserved.",
            replicates="Cooked Table 4 mean ± SD; raw table cells have no reported SD; replicate count not stated for HPLC table",
            analytical_definition="Individual HPLC-DAD analyte; methanolic extract",
        ))

new = pd.DataFrame(rows, columns=base.columns)
master = pd.concat([base, new], ignore_index=True)
assert len(new) == 15 and len(master) == 539 and master.doi.nunique() == 17
assert set(new.doi) == {"10.14456/apst.2022.5", "10.3389/fsufs.2021.761145"}
assert new.canonical_molecular_id.notna().all()
assert (new.target_value_percent.round(9) == (100 * new.cooked_concentration / new.raw_concentration).round(9)).all()
assert not master.observation_id.duplicated().any()
master.to_csv(R / "updated_master_dataset.csv", index=False)
new.to_csv(R / "verified_observations.csv", index=False)
new.to_csv(R / "extracted_observations.csv", index=False)

registry = pd.DataFrame([
    {"doi":"10.14456/apst.2022.5", "title":"Nutritional and phytochemical properties of Chaya leaves (Cnidoscolus chayamansa Mc Vaugh) planted in Northeastern Thailand", "year":2022, "admitted_rows":9, "status":"VERIFIED_PARTIAL", "basis":"mg/100 g dry weight", "reason":"Primary Table 4 directly reports individual raw/cooked HPLC-DAD means ± SD and Methods state boiling at 100 °C for 15 min followed by drying. Only exact existing descriptor identities admitted."},
    {"doi":"10.3389/fsufs.2021.761145", "title":"Comparison of Phenolic Compounds and Antioxidant Activities of Raw and Cooked Turkish Artichoke Cultivars", "year":2021, "admitted_rows":6, "status":"VERIFIED_PARTIAL_BASIS_PRESERVED", "basis":"mg/kg as reported; basis unspecified", "reason":"Primary Table 4 gives individual chlorogenic-acid raw/cooked receptacle values. The table does not label fresh/dry basis; values are retained exactly as reported, not converted or relabelled."},
    {"doi":"10.3390/foods11030384", "title":"Biochemical Characterization and Effects of Cooking Methods on Main Phytochemicals of Red and Purple Potato Tubers", "year":2022, "admitted_rows":0, "status":"EXCLUDED_AGGREGATE", "basis":"not used", "reason":"The relevant numeric endpoint is chlorogenic acid and isomers (CGAs), an aggregate that cannot be mapped to one individual molecular identity."},
    {"doi":"10.3390/molecules31162740", "title":"Prior candidate rejected as duplicate DOI family", "year":2026, "admitted_rows":0, "status":"EXCLUDED_DUPLICATE_DOI", "basis":"not used", "reason":"Already represented in the 439-row parent dataset; no duplicate experiment is admitted."},
])
registry.to_csv(R / "literature_candidate_registry.csv", index=False)

pd.DataFrame([
    {"category":"EXCLUDED_TABLE_VALUES", "doi":"10.14456/apst.2022.5", "reason":"Gallic acid, p-hydroxybenzoic acid, myricetin, and apigenin lack an exact pre-existing verified descriptor identity in the current schema; no identity/descriptor was inferred."},
    {"category":"EXCLUDED_TABLE_VALUES", "doi":"10.3389/fsufs.2021.761145", "reason":"Cynarine, cynaroside, luteolin, rhoifolin, and syringin were not admitted because no exact verified descriptor identity exists in the current schema; values at limit of detection are excluded."},
    {"category":"EXCLUDED_SOURCE", "doi":"10.3390/foods11030384", "reason":"Table target is an aggregate chlorogenic-acid-and-isomers endpoint, not an individually identified compound."},
    {"category":"EXCLUDED_SOURCE", "doi":"10.3390/molecules31162740", "reason":"Already present in parent DOI families; duplicate-source admission prohibited."},
    {"category":"EXCLUDED_SOURCE", "doi":"NO_DOI_IDENTIFIED_IJFS_2019", "reason":"Lima-bean table had primary numeric evidence, but no article DOI was verified in the primary record; it is not admitted to a DOI-family expansion dataset."},
]).to_csv(R / "excluded_candidates.csv", index=False)

prior = pd.read_csv(R.parent / "batch_004" / "source_verification_ledger.csv")
extra = pd.DataFrame([
    {"doi":"10.14456/apst.2022.5", "paper_title":"Nutritional and phytochemical properties of Chaya leaves (Cnidoscolus chayamansa Mc Vaugh) planted in Northeastern Thailand", "source_url":"https://doi.nrct.go.th/ListDoi/Download/607362?Resolve_DOI=10.14456%2Fapst.2022.5", "locator":"Table 4; Methods §§2.1 and 2.7", "rows_admitted":9, "compound":"Protocatechuic, chlorogenic, caffeic, syringic, p-coumaric, ferulic and sinapic acids; rutin; quercetin", "basis":"mg/100 g dry weight", "analytical_method":"Individual HPLC-DAD", "admission_status":"VERIFIED_PARTIAL", "rationale":"Direct primary table values; identical raw/cooked dry-weight basis; boiling protocol directly stated."},
    {"doi":"10.3389/fsufs.2021.761145", "paper_title":"Comparison of Phenolic Compounds and Antioxidant Activities of Raw and Cooked Turkish Artichoke Cultivars", "source_url":"https://www.frontiersin.org/journals/sustainable-food-systems/articles/10.3389/fsufs.2021.761145/full", "locator":"Table 4 receptacle rows; HPLC Methods", "rows_admitted":6, "compound":"Chlorogenic acid", "basis":"mg/kg as reported; basis unspecified", "analytical_method":"Individual HPLC-DAD", "admission_status":"VERIFIED_PARTIAL_BASIS_PRESERVED", "rationale":"Direct primary-table raw/cooked values. Basis ambiguity is preserved as reported, not imputed or converted."},
])
pd.concat([prior, extra], ignore_index=True, sort=False).to_csv(R / "source_verification_ledger.csv", index=False)

coverage = master.groupby("doi").agg(observations=("observation_id", "size"), compounds=("compound", "nunique"), foods=("food_matrix", "nunique"), methods=("cooking_method_normalized", "nunique"), bases=("measurement_basis", lambda x: "; ".join(sorted(x.dropna().unique())))).reset_index()
coverage.to_csv(R / "source_coverage_analysis.csv", index=False)

write("dataset_expansion_report.md", f"""
# Scientific dataset expansion — controlled batch 005

The controlled master becomes **{len(master)} verified observations from {master.doi.nunique()} DOI families**. The 1,000-observation target remains unreached. This package adds 15 table-traceable raw/cooked pairs from two independent DOI families and preserves every one of the 524 parent records.

Kongphapa et al. (2022), DOI `10.14456/apst.2022.5`, Table 4 and Methods, contributes nine individual HPLC-DAD Chaya-leaf pairs after boiling at 100 °C for 15 minutes followed by drying. The table reports mg/100 g dry weight and triplicate mean ± SD. Only established exact molecular identities are admitted.

Kayahan and Saloglu (2021), DOI `10.3389/fsufs.2021.761145`, Table 4, contributes six individual HPLC-DAD chlorogenic-acid pairs in receptacles of two Turkish artichoke cultivars after boiling, microwave cooking, and baking. The source table says mg/kg but does not state a fresh- or dry-weight basis. Its basis is therefore recorded as `as reported (basis unspecified)` and is never converted or relabelled.

Candidate exclusions are retained in `excluded_candidates.csv`: an aggregate chlorogenic-acid/isomer endpoint, an existing parent DOI family, table molecules not yet mapped to exact descriptors, and a DOI-unverified Lima-bean paper. No model is retrained; Stage C remains untouched and unauthorized.
""")
write("reproduction_instructions.md", """
# Reproduction

Run `python build_batch_005.py`, then `python validate_batch_005.py`. The build reads only Batch 004 and writes only this package. It performs no remote, Git, historical-package, or Stage-B/C/D change.
""")
manifest = {
    "package": "StageA_DatasetExpansion1000_Batch005_2026-11-10",
    "parent_rows": 524,
    "parent_sha256": sha(PARENT),
    "new_rows": 15,
    "total_rows": len(master),
    "new_doi_families": 2,
    "strict_cross_source_replications_created": 0,
    "target_1000_reached": False,
    "stage_c_integration_authorized": False,
}
(R / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
(R / "SHA256SUMS.txt").write_text("\n".join(f"{sha(p)}  {p.name}" for p in sorted(R.iterdir()) if p.is_file() and p.name != "SHA256SUMS.txt") + "\n", encoding="utf-8")
print(json.dumps(manifest, indent=2))
