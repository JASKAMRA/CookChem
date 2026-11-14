"""Controlled expansion batch 002: direct, same-fraction HPLC/DW pairs only.

This script deliberately uses one record per reported condition mean, never an
artificial row per technical replicate.  It carries the source's free/bound
extraction fraction in a separate field so neither fraction is silently read
as total phenolic-acid concentration.
"""
from pathlib import Path
import hashlib
import json
import pandas as pd


R = Path(__file__).resolve().parent
PARENT = R.parent / "updated_master_dataset.csv"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_markdown(name: str, text: str) -> None:
    (R / name).write_text(text.strip() + "\n", encoding="utf-8")


base = pd.read_csv(PARENT)
parent_columns = list(base.columns)
if "analytical_definition" not in base.columns:
    base["analytical_definition"] = pd.NA

# Individual Table 1 values, μg/g dry sample, each a mean ± SD from n=3.
# Only molecule identities already verified in the parent descriptor schema are
# admitted.  The extraction fraction is part of the measurement definition.
conditions = {
    "Atmospheric-pressure boiling": {
        "normalized": "atmospheric-pressure boiling",
        "time": 90,
        "medium": "water; 320 g water / 40 g triticale grain; rice cooker porridge setting",
        "rows": [
            ("Protocatechuic Acid", "free phenolic-acid extract", 3.33, 0.21, 7.57, 0.40),
            ("Protocatechuic Acid", "bound phenolic-acid extract", 5.65, 0.69, 2.80, 0.24),
            ("Syringic acid", "free phenolic-acid extract", 1.99, 0.21, 3.17, 0.41),
            ("Syringic acid", "bound phenolic-acid extract", 5.95, 0.11, 4.11, 0.31),
            ("P-Coumaric Acid", "free phenolic-acid extract", 3.75, 0.09, 0.59, 0.05),
            ("Ferulic Acid", "free phenolic-acid extract", 6.85, 0.03, 10.46, 1.03),
            ("Ferulic Acid", "bound phenolic-acid extract", 782.49, 1.30, 247.82, 4.83),
            ("Sinapic acid", "free phenolic-acid extract", 0.62, 0.05, 4.81, 0.42),
            ("Sinapic acid", "bound phenolic-acid extract", 27.54, 0.49, 17.96, 0.40),
        ],
    },
    "High-pressure boiling": {
        "normalized": "high-pressure boiling",
        "time": 60,
        "medium": "water; 200 g water / 40 g triticale grain; electric pressure cooker at 60 kPa",
        "rows": [
            ("Protocatechuic Acid", "free phenolic-acid extract", 3.33, 0.21, 6.08, 0.10),
            ("Protocatechuic Acid", "bound phenolic-acid extract", 5.65, 0.69, 3.86, 0.27),
            ("Syringic acid", "free phenolic-acid extract", 1.99, 0.21, 2.14, 0.17),
            ("Syringic acid", "bound phenolic-acid extract", 5.95, 0.11, 4.67, 0.42),
            ("Caffeic Acid", "free phenolic-acid extract", 1.36, 0.18, 0.15, 0.02),
            ("P-Coumaric Acid", "free phenolic-acid extract", 3.75, 0.09, 0.59, 0.04),
            ("P-Coumaric Acid", "bound phenolic-acid extract", 15.94, 0.32, 3.21, 0.19),
            ("Ferulic Acid", "free phenolic-acid extract", 6.85, 0.03, 9.72, 0.21),
            ("Ferulic Acid", "bound phenolic-acid extract", 782.49, 1.30, 409.26, 3.16),
            ("Sinapic acid", "free phenolic-acid extract", 0.62, 0.05, 4.05, 0.19),
            ("Sinapic acid", "bound phenolic-acid extract", 27.54, 0.49, 18.04, 1.05),
        ],
    },
}

templates = {
    name.casefold(): base.loc[base["compound"].astype(str).str.casefold().eq(name.casefold())].iloc[0]
    for name in {entry[0] for condition in conditions.values() for entry in condition["rows"]}
}
new_rows = []
for method, details in conditions.items():
    for compound, fraction, raw, raw_sd, cooked, cooked_sd in details["rows"]:
        template = templates[compound.casefold()]
        row = {column: template[column] for column in base.columns}
        row.update(
            {
                "observation_id": "LIT-LI2024-TRITICALE-{}-{}-{}".format(
                    compound.upper().replace(" ", "_").replace("-", "_"),
                    fraction.split()[0].upper(),
                    "CAP" if method.startswith("Atmospheric") else "CHP",
                ),
                "original_record_id": "",
                "doi": "10.3390/foods13020230",
                "paper_id": "NEW_LITERATURE_LI_2024",
                "source_locator": "Table 1 (individual phenolic acids); Methods §§2.2, 2.4–2.7",
                "compound": compound,
                "food_matrix": "Triticale grain (ND2201; cooked as porridge)",
                "cooking_method": method,
                "cooking_method_normalized": details["normalized"],
                "cooking_medium": details["medium"],
                "raw_concentration": raw,
                "cooked_concentration": cooked,
                "concentration_unit": "μg/g dry sample",
                "measurement_basis": "dry weight (DW)",
                "target_name": "apparent_concentration_ratio_percent",
                "target_equation": "100 * C_cooked / C_raw",
                "target_value_percent": 100 * cooked / raw,
                "target_semantics": "apparent concentration ratio; not total-mass retention",
                "evidence_status": "VERIFIED_PRIMARY_TABLE",
                "cooked_yield_status": "NOT_REPORTED",
                "total_mass_retention_status": "NOT_ESTABLISHED",
                "source_detail": (
                    "Li et al. (2024), Table 1. Individual phenolic acids in explicitly "
                    "separate free or bound extracts, HPLC-DAD with authentic standards; "
                    "mean ± SD, n=3. Cooked samples freeze-dried before dry-sample analysis."
                ),
                "Temperature_C": pd.NA,
                "Cooking_Time_min": details["time"],
                "raw_sd": raw_sd,
                "cooked_sd": cooked_sd,
                "reported_replicate_design": "triplicate condition mean ± SD; one dataset row per condition mean",
                "analytical_definition": fraction,
            }
        )
        new_rows.append(row)

new = pd.DataFrame(new_rows, columns=base.columns)
master = pd.concat([base, new], ignore_index=True)
assert len(new) == 20
assert len(master) == 471 and master["doi"].nunique() == 12
assert (new["target_value_percent"].round(10) == (100 * new["cooked_concentration"] / new["raw_concentration"]).round(10)).all()
assert new["canonical_molecular_id"].notna().all()
assert set(new["analytical_definition"]) == {"free phenolic-acid extract", "bound phenolic-acid extract"}

master.to_csv(R / "updated_master_dataset.csv", index=False)
new.to_csv(R / "extracted_observations.csv", index=False)
new.to_csv(R / "verified_observations.csv", index=False)

registry = pd.DataFrame(
    [
        {
            "doi": "10.3390/foods13020230",
            "title": "Impact of Cooking Methods on Phenolic Acid Composition, Antioxidant Activity, and Starch Digestibility of Chinese Triticale Porridges",
            "year": 2024,
            "compound_scope": "ten individual phenolic acids; six have existing verified descriptor identities",
            "food_matrix": "Triticale grain / porridge, cultivar ND2201",
            "cooking_method": "atmospheric-pressure boiling; high-pressure boiling",
            "measurement_technique": "HPLC-DAD, authentic standards; free and bound extraction protocols separately specified",
            "measurement_basis": "μg/g dry sample",
            "raw_and_cooked_values": "Table 1, means ± SD, n=3",
            "extractable_observations": 20,
            "verification_status": "VERIFIED",
            "rejection_reason": "Four Table 1 compounds (p-hydroxybenzoic, vanillic, gallic, and trans-cinnamic acid) were not admitted because no exact existing verified descriptor identity was found in the parent schema; not inferred.",
        },
        {
            "doi": "10.1016/j.heliyon.2019.e01310",
            "title": "Effects of domestic cooking on flavonoids in broccoli and calculation of retention factors",
            "year": 2019,
            "compound_scope": "individual flavonoid glycosides",
            "food_matrix": "Broccoli",
            "cooking_method": "boiling; steaming; microwave",
            "measurement_technique": "HPLC-MS",
            "measurement_basis": "mg/100 g fresh weight",
            "raw_and_cooked_values": "primary tables",
            "extractable_observations": "not admitted",
            "verification_status": "DESCRIPTOR_IDENTITY_PENDING",
            "rejection_reason": "The table is primary evidence, but its glycoside analytes lack verified canonical molecular identities in the current descriptor schema. No structure or descriptor is inferred from a name.",
        },
        {
            "doi": "10.1016/j.fochx.2022.100339",
            "title": "Cooking methods affected phytochemicals and antioxidant activities of potato",
            "year": 2022,
            "compound_scope": "phenolic acids",
            "food_matrix": "Potato",
            "cooking_method": "multiple",
            "measurement_technique": "primary table",
            "measurement_basis": "dry weight",
            "raw_and_cooked_values": "primary table",
            "extractable_observations": "already represented",
            "verification_status": "DUPLICATE",
            "rejection_reason": "DOI already represented in the parent; no duplicate extraction.",
        },
    ]
)
registry.to_csv(R / "literature_candidate_registry.csv", index=False)
registry.loc[registry["verification_status"].ne("VERIFIED")].to_csv(R / "excluded_candidates.csv", index=False)

prior_ledger = pd.read_csv(R.parent / "source_verification_ledger.csv")
ledger_row = pd.DataFrame(
    [
        {
            "doi": "10.3390/foods13020230",
            "paper_title": "Impact of Cooking Methods on Phenolic Acid Composition, Antioxidant Activity, and Starch Digestibility of Chinese Triticale Porridges",
            "source_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC10814846/",
            "locator": "Table 1; Methods §§2.2, 2.4–2.7",
            "rows_admitted": 20,
            "compound": "Protocatechuic, syringic, caffeic, p-coumaric, ferulic, and sinapic acids",
            "basis": "μg/g dry sample",
            "analytical_method": "HPLC-DAD; separate free/bound extraction; authentic standards",
            "admission_status": "VERIFIED",
            "rationale": "Raw/cooked condition means, dry-sample basis, protocol, extraction fraction, and HPLC identity evidence are directly traceable. Fractions remain distinct.",
        }
    ]
)
pd.concat([prior_ledger, ledger_row], ignore_index=True, sort=False).to_csv(R / "source_verification_ledger.csv", index=False)

coverage = (
    master.groupby("doi")
    .agg(
        observations=("observation_id", "size"),
        compounds=("compound", "nunique"),
        foods=("food_matrix", "nunique"),
        methods=("cooking_method_normalized", "nunique"),
        bases=("measurement_basis", lambda x: "; ".join(sorted(x.dropna().unique())),),
    )
    .reset_index()
)
coverage.to_csv(R / "source_coverage_analysis.csv", index=False)

write_markdown(
    "schema_migration.md",
    """
    # Schema migration

    Batch 002 preserves every Batch-001 field and adds `analytical_definition`.
    Parent and Batch-001 rows are null for that field because an individual
    free/bound extraction category was not captured in their source contracts.
    The 20 Li rows set it to either `free phenolic-acid extract` or `bound
    phenolic-acid extract`. These are distinct analytical quantities; no row is
    a total-phenolic or total-mass-retention result.
    """,
)
write_markdown(
    "dataset_expansion_report.md",
    f"""
    # Scientific dataset expansion — controlled batch 002

    ## Result

    The 1,000-observation target is **not reached**. The controlled master is
    **{len(master)} observations** from **{master.doi.nunique()} DOI families**:
    20 additions from one independent primary paper. Its 451-row Batch-001
    parent is preserved exactly when projected to the parent schema.

    ## Admission

    Li et al. (2024), DOI `10.3390/foods13020230`, Table 1 and Methods, reports
    individual phenolic acids in raw and cooked triticale as mean ± SD across
    three repetitions. Values are HPLC-DAD measurements in μg/g dry sample.
    Atmospheric-pressure porridge boiling is 90 minutes; high-pressure boiling
    is 60 minutes at 60 kPa. The source explicitly uses separate free and bound
    extraction procedures; that fraction is preserved in `analytical_definition`
    and comparisons are only made within the same fraction.

    Six compounds with pre-existing verified descriptor identities contribute 20
    direct raw/cooked pairs: protocatechuic (4), syringic (4), caffeic (1),
    p-coumaric (3), ferulic (4), and sinapic acid (4). Four other Table-1
    analytes are deliberately excluded because no exact verified descriptor
    identity is available in the parent schema. No descriptor was generated or
    inferred.

    ## Boundary

    These are apparent concentration ratios only, not total-mass retention.
    They diversify source, cereal matrix, method, and analytical fraction, but
    do not create a strict protocol-identical cross-source replication. No model
    is retrained and Stage C is not authorized.
    """,
)
write_markdown(
    "reproduction_instructions.md",
    """
    # Reproduction

    Run `python build_batch_002.py`, then `python validate_batch_002.py`.
    The build reads only Batch 001's immutable master, produces a new master in
    this directory, and uses the explicitly transcribed source values listed in
    the script and candidate registry. It performs no remote, Git, Stage-B/C/D,
    or historical-package modification.
    """,
)

manifest = {
    "package": "StageA_DatasetExpansion1000_Batch002_2026-11-10",
    "parent_rows": 451,
    "parent_sha256": sha256(PARENT),
    "new_rows": len(new),
    "total_rows": len(master),
    "new_doi_families": 1,
    "strict_cross_source_replications_created": 0,
    "target_1000_reached": False,
    "stage_c_integration_authorized": False,
}
(R / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
(R / "SHA256SUMS.txt").write_text(
    "\n".join(
        f"{sha256(path)}  {path.name}"
        for path in sorted(R.iterdir())
        if path.is_file() and path.name != "SHA256SUMS.txt"
    )
    + "\n",
    encoding="utf-8",
)
print(json.dumps(manifest, indent=2))
