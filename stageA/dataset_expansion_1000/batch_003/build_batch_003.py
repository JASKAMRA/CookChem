"""Controlled expansion batch 003: two primary tables, no inferred identities."""
from pathlib import Path
import hashlib
import json
import pandas as pd

R = Path(__file__).resolve().parent
PARENT = R.parent / "batch_002" / "updated_master_dataset.csv"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, content):
    (R / name).write_text(content.strip() + "\n", encoding="utf-8")


base = pd.read_csv(PARENT)
parent_columns = list(base.columns)


def template(compound):
    match = base.loc[base["compound"].astype(str).str.casefold().eq(compound.casefold())]
    assert len(match), f"No verified descriptor template for {compound}"
    return match.iloc[0]


rows = []


def add_row(*, source, source_locator, compound, food, method, normalized, medium, raw, raw_sd, cooked, cooked_sd, unit, basis, temperature, duration, detail, analytical_definition, identity_name=None):
    source_template = template(identity_name or compound)
    row = {column: source_template[column] for column in base.columns}
    method_code = {"Water cooking": "COOKED", "Pan frying without added fat": "FRIED", "Boiling": "BOILED"}[method]
    row.update(
        {
            "observation_id": "{}-{}-{}-{}".format(source, food.upper().replace(" ", "_").replace(";", ""), compound.upper().replace(" ", "_").replace("-", "_"), method_code),
            "original_record_id": "",
            "doi": pd.NA,
            "paper_id": "NEW_LITERATURE_" + source,
            "source_locator": source_locator,
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
            "Temperature_C": temperature,
            "Cooking_Time_min": duration,
            "raw_sd": raw_sd,
            "cooked_sd": cooked_sd,
            "reported_replicate_design": "triplicate condition mean ± SD; one dataset row per condition mean",
            "analytical_definition": analytical_definition,
        }
    )
    rows.append(row)


# Najman et al. Table 3 and Table 4: explicitly reported per 100 g product.
# This is retained as its own as-reported basis, never re-labelled as fresh weight.
quince = [
    ("Lutein", 3.55, 0.06, 13.16, 0.08, 13.84, 0.06),
    ("Beta-Carotene", 13.61, 0.00, 54.38, 0.01, 54.38, 0.01),
    ("Quercetin", 0.95, 0.01, 3.48, 0.10, 3.50, 0.12),
    ("Chlorogenic Acid", 14.47, 0.14, 205.74, 1.12, 209.58, 2.32),
    ("Caffeic Acid", 0.61, 0.00, 9.86, 0.10, 2.91, 0.06),
    ("P-Coumaric Acid", 0.39, 0.00, 6.67, 0.22, 6.31, 0.41),
    ("Ferulic Acid", 0.31, 0.00, 4.99, 0.08, 2.01, 0.07),
]
for compound, raw, raw_sd, cooked, cooked_sd, fried, fried_sd in quince:
    shared = dict(
        source="NAJMAN2023",
        source_locator="Tables 3–4; Methods §§3.1–3.2.5",
        compound=compound,
        food="Quince fruit (Cydonia oblonga; diced)",
        unit="mg/100 g product",
        basis="as-reported product basis (mg/100 g); not re-labelled FW or DW",
        detail="Najman et al. (2023), Tables 3–4. HPLC-UV/VIS with named external standards; mean ± SD, n=3. Raw and processed concentrations are both stated per 100 g product.",
        analytical_definition="source-defined acetone extract (carotenoid)" if compound in {"Lutein", "Beta-Carotene"} else "source-defined methanol extract (individual phenolic compound)",
    )
    add_row(**shared, method="Water cooking", normalized="water cooking", medium="water; fruit drained and sieved into mousse after cooking", raw=raw, raw_sd=raw_sd, cooked=cooked, cooked_sd=cooked_sd, temperature=100, duration=40)
    add_row(**shared, method="Pan frying without added fat", normalized="dry pan frying", medium="hot pan without added fat; small water additions only to prevent burning", raw=raw, raw_sd=raw_sd, cooked=fried, cooked_sd=fried_sd, temperature=pd.NA, duration=40)

# Chang et al. Table 5: only caffeic-acid pairs where both raw and cooked values
# are detected.  Raw/cooked soymilk uses the same grinding method per pair.
for label, raw, raw_sd, cooked, cooked_sd in [("M1", 1.5, 0.1, 0.9, 0.1), ("M3", 1.3, 0.1, 2.5, 0.1), ("M4", 1.4, 0.2, 1.4, 0.1)]:
    add_row(
        source="CHANG2024",
        source_locator="Table 5; Methods manufacturing procedure",
        compound="Caffeic Acid",
        food=f"ProSoy soymilk ({label} grinding method)",
        method="Boiling",
        normalized="boiling",
        medium="soymilk; cooked at 100 °C after preparation",
        raw=raw,
        raw_sd=raw_sd,
        cooked=cooked,
        cooked_sd=cooked_sd,
        unit="μg/g dry basis",
        basis="dry weight (DW)",
        temperature=100,
        duration=20,
        detail="Chang et al. (2024), Table 5. Free phenolic acids measured by HPLC, mean ± SD, n=3. Only detected raw/cooked caffeic-acid pairs are admitted.",
        analytical_definition="free phenolic-acid composition (HPLC; source-defined)",
    )

new = pd.DataFrame(rows, columns=base.columns)
assert len(new) == 17 and new["doi"].isna().all()
new.loc[new["paper_id"].eq("NEW_LITERATURE_NAJMAN2023"), "doi"] = "10.3390/molecules28073066"
new.loc[new["paper_id"].eq("NEW_LITERATURE_CHANG2024"), "doi"] = "10.3390/antiox13070755"
master = pd.concat([base, new], ignore_index=True)
assert len(master) == 488 and master["doi"].nunique() == 14
assert (new["target_value_percent"].round(10) == (100 * new["cooked_concentration"] / new["raw_concentration"]).round(10)).all()
assert new["canonical_molecular_id"].notna().all()
master.to_csv(R / "updated_master_dataset.csv", index=False)
new.to_csv(R / "verified_observations.csv", index=False)
new.to_csv(R / "extracted_observations.csv", index=False)

registry = pd.DataFrame([
    {"doi":"10.3390/molecules28073066", "title":"Changes in Physicochemical and Bioactive Properties of Quince (Cydonia oblonga Mill.) and Its Products", "year":2023, "admitted_rows":14, "status":"VERIFIED", "basis":"mg/100 g product (retained exactly as reported)", "reason":"Tables 3–4 provide paired raw/cooked/fried individual HPLC values, n=3, and Methods specifies 100 °C/40 min water cooking and 40-min no-fat pan frying. Only analytes with existing verified identities are admitted."},
    {"doi":"10.3390/antiox13070755", "title":"Mass Yields, Antioxidant and Anti-DU145 Prostate Cancer Cell Proliferation Properties of ProSoy Soymilk as Affected by Extraction Methods and Cooking", "year":2024, "admitted_rows":3, "status":"VERIFIED_PARTIAL", "basis":"μg/g dry basis", "reason":"Table 5 supplies detected raw/cooked free caffeic-acid HPLC pairs for M1, M3, M4; cooking is 100 °C/20 min. Other individual analytes lack pre-existing verified descriptor identities or have a non-detect in one member of the pair."},
    {"doi":"10.3390/plants10102192", "title":"Effect of Roasting, Boiling, and Frying Processing on 29 Polyphenolics and Antioxidant Activity in Seeds and Shells of Sweet Chestnut", "year":2021, "admitted_rows":0, "status":"TABLE_PENDING_STRUCTURED_TRANSCRIPTION", "basis":"mg/kg dry weight", "reason":"Primary PDF and protocol are accessible, but its dense multi-matrix Table 2 needs a separate line-by-line transcription and canonical-identity audit before any admission; no values taken from narrative summaries."},
])
registry.to_csv(R / "literature_candidate_registry.csv", index=False)
registry.loc[registry.status.ne("VERIFIED") & registry.status.ne("VERIFIED_PARTIAL")].to_csv(R / "excluded_candidates.csv", index=False)

ledger = pd.read_csv(R.parent / "batch_002" / "source_verification_ledger.csv")
extra = pd.DataFrame([
    {"doi":"10.3390/molecules28073066", "paper_title":"Changes in Physicochemical and Bioactive Properties of Quince (Cydonia oblonga Mill.) and Its Products", "source_url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC10096434/", "locator":"Tables 3–4; Methods §§3.1–3.2.5", "rows_admitted":14, "compound":"Lutein, beta-carotene, quercetin, chlorogenic, caffeic, p-coumaric, ferulic acid", "basis":"as-reported product basis (mg/100 g)", "analytical_method":"HPLC-UV/VIS; named external standards", "admission_status":"VERIFIED", "rationale":"Exact common source basis and raw/cooked values retained; raw/cooked ratios are not presented as mass retention."},
    {"doi":"10.3390/antiox13070755", "paper_title":"Mass Yields, Antioxidant and Anti-DU145 Prostate Cancer Cell Proliferation Properties of ProSoy Soymilk as Affected by Extraction Methods and Cooking", "source_url":"https://www.mdpi.com/2076-3921/13/7/755", "locator":"Table 5; manufacturing procedure", "rows_admitted":3, "compound":"Caffeic acid", "basis":"μg/g dry basis", "analytical_method":"HPLC; free phenolic-acid table", "admission_status":"VERIFIED_PARTIAL", "rationale":"Three detected raw/cooked same-grinding-method pairs; non-detect pairs and molecules without verified existing identities excluded."},
])
pd.concat([ledger, extra], ignore_index=True, sort=False).to_csv(R / "source_verification_ledger.csv", index=False)

coverage = master.groupby("doi").agg(observations=("observation_id","size"), compounds=("compound","nunique"), foods=("food_matrix","nunique"), methods=("cooking_method_normalized","nunique"), bases=("measurement_basis", lambda x: "; ".join(sorted(x.dropna().unique())))).reset_index()
coverage.to_csv(R / "source_coverage_analysis.csv", index=False)
write("schema_migration.md", """
# Schema statement

Batch 003 retains Batch 002's schema unchanged. It uses the existing
`analytical_definition` field to preserve the source-specific acetone/methanol
extract definition and free-phenolic-acid qualifier. Quince's stated `mg/100 g
product` stays a separate reported basis and is not silently converted to FW or
DW.
""")
write("dataset_expansion_report.md", f"""
# Scientific dataset expansion — controlled batch 003

The controlled master is **{len(master)} observations from {master.doi.nunique()} DOI
families**. The 1,000 target remains unreached. It adds 17 direct primary-table
pairs from two independent DOI families while preserving all 471 parent rows.

Najman et al. (2023), DOI `10.3390/molecules28073066`, contributes 14 quince
rows (seven verified-identity analytes × water cooking and no-fat pan frying).
The paper reports raw and processed values as mg/100 g *product*, a label
retained exactly in the data. Chang et al. (2024), DOI
`10.3390/antiox13070755`, contributes three dry-basis, free-caffeic-acid
soymilk pairs at 100 °C for 20 minutes. It excludes non-detect pairs and all
unverified descriptor identities.

Neither source supplies evidence for total-mass retention. The new source
families improve diversity but do not create strict protocol-identical
cross-source replications, so no model is retrained and Stage C remains
untouched.
""")
write("reproduction_instructions.md", """
# Reproduction

Run `python build_batch_003.py`, then `python validate_batch_003.py`. The build
reads Batch 002 only and creates files only in this new package. It does not
perform remote, Git, historical-package, or Stage-B/C/D changes.
""")
manifest = {"package":"StageA_DatasetExpansion1000_Batch003_2026-11-10", "parent_rows":471, "parent_sha256":digest(PARENT), "new_rows":17, "total_rows":len(master), "new_doi_families":2, "strict_cross_source_replications_created":0, "target_1000_reached":False, "stage_c_integration_authorized":False}
(R / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
(R / "SHA256SUMS.txt").write_text("\n".join(f"{digest(p)}  {p.name}" for p in sorted(R.iterdir()) if p.is_file() and p.name != "SHA256SUMS.txt") + "\n", encoding="utf-8")
print(json.dumps(manifest, indent=2))
