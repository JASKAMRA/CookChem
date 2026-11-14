"""Reproducible, read-only-on-parent intelligence audit for Stage A v0.9."""
from pathlib import Path
import hashlib, json, shutil
import pandas as pd
import numpy as np
from sklearn.metrics import normalized_mutual_info_score

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / "recovery_v0_8_0_2026_11_10"
DATA = PARENT / "expanded_clean_stageA_dataset.csv"
DESC = ["RDKit_Molecular_Weight","RDKit_LogP","RDKit_TPSA","RDKit_HBond_Donors","RDKit_HBond_Acceptors","RDKit_Rotatable_Bonds","RDKit_Aromatic_Rings","RDKit_Hydroxyl_Groups"]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def csv(frame, name): frame.to_csv(HERE / name, index=False)
def nuni(s): return s.nunique(dropna=True)
def nonempty(s): return s.notna() & s.astype(str).str.strip().ne("")
def descriptor_ok(x):
    a = x[DESC].apply(pd.to_numeric, errors="coerce")
    return np.isfinite(a).all(axis=1)
def md(name, text): (HERE / name).write_text(text.strip()+"\n", encoding="utf-8")

HERE.mkdir(exist_ok=True)
d = pd.read_csv(DATA)
d["descriptor_complete"] = descriptor_ok(d)
d["temperature_reported"] = nonempty(d.Temperature_C)
d["duration_reported"] = nonempty(d.Cooking_Time_min)
shutil.copy2(DATA, HERE / "expanded_clean_stageA_dataset.csv")
for name in ["source_verification_ledger.csv", "exclusion_log.csv"]:
    shutil.copy2(PARENT / name, HERE / name)

# Dimension coverage.
compound = d.groupby("compound").agg(observations=("observation_id","size"), doi_families=("doi",nuni), food_matrices=("food_matrix",nuni), cooking_methods=("cooking_method_normalized",nuni), measurement_bases=("measurement_basis",lambda x:"; ".join(sorted(x.dropna().unique()))), descriptor_complete_pct=("descriptor_complete",lambda x:100*x.mean())).reset_index()
food = d.groupby("food_matrix").agg(observations=("observation_id","size"), compounds=("compound",nuni), doi_families=("doi",nuni), cooking_methods=("cooking_method_normalized",nuni), measurement_bases=("measurement_basis",lambda x:"; ".join(sorted(x.dropna().unique()))), descriptor_complete_pct=("descriptor_complete",lambda x:100*x.mean())).reset_index()
method = d.groupby("cooking_method_normalized").agg(observations=("observation_id","size"), compounds=("compound",nuni), food_matrices=("food_matrix",nuni), doi_families=("doi",nuni), temperature_reported_pct=("temperature_reported",lambda x:100*x.mean()), duration_reported_pct=("duration_reported",lambda x:100*x.mean()), measurement_bases=("measurement_basis",lambda x:"; ".join(sorted(x.dropna().unique())))).reset_index()
source = d.groupby("doi").agg(observations=("observation_id","size"), compounds=("compound",nuni), food_matrices=("food_matrix",nuni), cooking_methods=("cooking_method_normalized",nuni), measurement_bases=("measurement_basis",lambda x:"; ".join(sorted(x.dropna().unique())),), descriptor_complete_pct=("descriptor_complete",lambda x:100*x.mean())).reset_index()
source["percent_of_dataset"] = 100*source.observations/len(d)
for x, name, sort in [(compound,"compound_coverage_matrix.csv",["doi_families","observations"]),(food,"food_matrix_coverage_matrix.csv",["doi_families","observations"]),(method,"cooking_method_coverage_matrix.csv",["doi_families","observations"]),(source,"source_family_coverage_matrix.csv",["observations"])]: csv(x.sort_values(sort, ascending=False), name)

# Strict cell audit: categorical cell first; protocol identity additionally needs fully reported equal duration,
# temperature, medium and source analytical wording. Missing protocol data cannot establish an exact replication.
keys = ["compound","food_matrix","cooking_method_normalized","measurement_basis"]
rows=[]
for k,g in d.groupby(keys, dropna=False):
    dois=sorted(g.doi.unique()); proto=g[["Temperature_C","Cooking_Time_min","cooking_medium"]].fillna("NOT_REPORTED").astype(str)
    protocol_signatures=proto.agg(" | ".join,axis=1).nunique()
    categorical_multi=len(dois)>1
    fully_same=categorical_multi and protocol_signatures==1 and not proto.eq("NOT_REPORTED").any().any()
    if fully_same: status="EXACT_CROSS_SOURCE_REPLICATION"; pool="REVIEW_ANALYTICAL_DEFINITION"
    elif categorical_multi: status="CATEGORICAL_NEAR_MATCH_PROTOCOL_DIFFERENCE_OR_MISSINGNESS"; pool="NOT_POOLABLE_AS_EXACT"
    elif len(g)>1: status="REPEATED_WITHIN_ONE_SOURCE"; pool="NOT_INDEPENDENT"
    else: status="UNIQUE_CELL"; pool="NOT_POOLABLE"
    rows.append(dict(zip(keys,k), observations=len(g), unique_doi_families=len(dois), source_identifiers="; ".join(dois), raw_cooked_available=bool((g.raw_concentration.notna() & g.cooked_concentration.notna()).all()), descriptor_complete_pct=100*g.descriptor_complete.mean(), protocol_signature_count=protocol_signatures, exact_match_status=status, pooling_eligibility=pool, evidence_confidence="VERIFIED_PRIMARY_TABLE" if (g.evidence_status=="VERIFIED_PRIMARY_TABLE").all() else "MIXED_OR_REVIEW", protocol_signatures=" || ".join(sorted(proto.agg(" | ".join,axis=1).unique()))))
cells=pd.DataFrame(rows).sort_values(["unique_doi_families","observations"],ascending=False)
csv(cells,"full_exact_matched_cell_matrix.csv")
csv(cells[cells.exact_match_status.str.contains("NEAR")],"near_match_cell_matrix.csv")
# Basis conflict at a broad compound-food-method group is a separate non-comparability signal.
broad=d.groupby(keys[:-1]).agg(observations=("observation_id","size"), doi_families=("doi",nuni), measurement_bases=("measurement_basis",lambda x:"; ".join(sorted(x.unique())),), basis_count=("measurement_basis",nuni)).reset_index()
noncomp=broad[broad.basis_count>1].copy(); noncomp["reason"]="Different stated measurement bases; no conversion or pooling performed."
csv(noncomp,"non_comparable_cell_matrix.csv")

# Cross-tabs are coverage maps, not claims of independence.
for c, name in [(["compound","food_matrix"],"compound_by_food_matrix.csv"),(["compound","cooking_method_normalized"],"compound_by_method.csv"),(["food_matrix","cooking_method_normalized"],"food_matrix_by_method.csv")]:
    z=d.groupby(c).agg(observations=("observation_id","size"),doi_families=("doi",nuni)).reset_index(); csv(z,name)

# Descriptor identities and completeness.
ids=d.groupby(["compound","canonical_molecular_id"],dropna=False).agg(observations=("observation_id","size"), descriptor_complete_pct=("descriptor_complete",lambda x:100*x.mean()), doi_families=("doi",nuni)).reset_index()
csv(ids,"descriptor_identity_audit.csv")
by_src=d.groupby("doi").agg(observations=("observation_id","size"),descriptor_complete_pct=("descriptor_complete",lambda x:100*x.mean())).reset_index(); csv(by_src,"descriptor_coverage_by_source.csv")
md("molecular_descriptor_coverage_report.md", f"""
# Molecular descriptor coverage

The v0.8 parent has **{len(d)} observations**, **{d.compound.nunique()} compound labels**, and **{d.canonical_molecular_id.nunique()} canonical molecular identifiers**. All eight recorded RDKit descriptor fields are finite for **{d.descriptor_complete.sum()} / {len(d)} ({100*d.descriptor_complete.mean():.1f}%)** observations. The compound/identifier mapping and source-level completeness are in the accompanying CSVs. This audit does not create structures or impute descriptor values. The historical exclusion of neochlorogenic acid remains outside this dataset and therefore outside this completeness percentage.

Descriptor-complete representation is not evidence of experimental comparability; descriptor availability cannot repair source/protocol confounding.
""")

# Target contract audit.
same_target=(d.target_name=="apparent_concentration_ratio_percent").sum()
mass=(d.total_mass_retention_status.astype(str).str.contains("ESTABLISHED",case=False,na=False) & ~d.total_mass_retention_status.astype(str).str.contains("NOT_ESTABLISHED",case=False,na=False)).sum()
csv(d.groupby(["measurement_basis","concentration_unit"],dropna=False).agg(observations=("observation_id","size"),doi_families=("doi",nuni)).reset_index(),"measurement_unit_basis_matrix.csv")
md("target_measurement_compatibility_report.md", f"""
# Target and measurement compatibility

- Target contract: **{same_target}/{len(d)}** rows are labelled `apparent_concentration_ratio_percent = 100 × C_cooked / C_raw`.
- **{(d.raw_concentration.notna() & d.cooked_concentration.notna()).sum()}/{len(d)}** have both tabulated concentrations.
- Measurement basis and unit combinations are enumerated in `measurement_unit_basis_matrix.csv`; they are retained as stated and never converted in this audit.
- **{mass}** rows are documented as having sufficient established mass-retention status. Therefore this package makes **no true total-mass retention calculation**.

The values are comparable apparent ratios only within their verified raw/cooked measurement contract. Moisture loss and unreported yield can raise concentration without proving preservation of total compound mass.
""")

# Association diagnostics, descriptive only.
features=["compound","food_matrix","cooking_method_normalized","measurement_basis","compound_class","cooking_medium","descriptor_complete"]
assoc=[]
for f in features:
    assoc.append({"feature":f,"normalized_mutual_information_with_doi":normalized_mutual_info_score(d.doi.astype(str),d[f].fillna("MISSING").astype(str))})
for f in ["Temperature_C","Cooking_Time_min"]:
    m=~nonempty(d[f]); assoc.append({"feature":f+"_missingness","normalized_mutual_information_with_doi":normalized_mutual_info_score(d.doi.astype(str),m.astype(str)),"missing_pct":100*m.mean(),"source_missingness_range_pct":100*(m.groupby(d.doi).mean().max()-m.groupby(d.doi).mean().min())})
assoc=pd.DataFrame(assoc); csv(assoc,"source_feature_associations.csv")
md("source_confounding_diagnostic_report.md", f"""
# Source-confounding diagnostic

There are {d.doi.nunique()} DOI families. The accompanying NMI table measures association with DOI family, not causal influence. High association indicates that a held-out source can represent a different compound-food-protocol domain rather than an independent replication. The parent v0.6 controlled analysis already found negative source-LOSO performance; this iteration intentionally does not retrain on the same structurally sparse evidence.

Only **{(cells.unique_doi_families>1).sum()}** categorical compound × food × method × basis cells span more than one DOI family, and **{(cells.exact_match_status=='EXACT_CROSS_SOURCE_REPLICATION').sum()}** satisfy this audit's stricter fully reported, identical-protocol criterion. This is the central overlap limitation.
""")

md("validation_feasibility_report.md", f"""
# Validation feasibility

| Design | Groups | Decision |
|---|---:|---|
| Random split | records | Not a generalisation claim: correlated rows from a source can appear on both sides. |
| Compound-grouped | {d.canonical_molecular_id.nunique()} | Descriptive molecular extrapolation only; compounds remain source/food clustered. |
| Food-matrix-grouped | {d.food_matrix.nunique()} | Feasible mechanically, but many foods occur in a single source and test support is heterogeneous. |
| Cooking-method-grouped | {d.cooking_method_normalized.nunique()} | Feasible mechanically but semantically heterogeneous labels and singleton method/source patterns weaken interpretation. |
| Leave-one-source-family-out | {d.doi.nunique()} | Most honest available broad-domain stress test, but often extrapolation; prior pooled performance is negative. |
| Connected cross-source experimental components | {int((cells.unique_doi_families>1).sum())} categorical overlap cells | Not sufficient for a valid predictive benchmark: zero strict cross-source protocol replications. |

No new metric is reported because no new evidence was added and a repeated fit would not resolve the validity failure.
""")

# Readiness assessments.
vit=d[(d.compound=="Vitamin C") & d.food_matrix.isin(["Carrot","Spinach"]) & d.cooking_method_normalized.isin(["boiling","steaming","microwave"]) & (d.measurement_basis=="fresh weight (FW)")]
sweet=d[(d.compound.isin(["Chlorogenic Acid","Ferulic Acid"])) & d.food_matrix.str.startswith("Sweet potato",na=False)]
md("domain_a_vitamin_c_readiness.md", f"""
# Domain A — Vitamin C in carrot and spinach

The selected fresh-weight scope contains **{len(vit)} observations**, **{vit.doi.nunique()} DOI families**, two foods and three methods. It produces six categorical cross-source matches. Inspection of `full_exact_matched_cell_matrix.csv` shows they are **protocol near-matches**, not strict replicated experiments: duration and/or medium/protocol reporting differs by source. Temperature is not consistently reported.

**Decision: C — more matched evidence required.** The domain can support a limited descriptive comparison of reported apparent ratios, not a predictive model or an inter-laboratory replication estimate. Obtain a third independent primary study with raw/cooked fresh-weight vitamin C concentrations and closely aligned preparation, method, duration, water/power and analytical definitions.
""")
md("domain_b_sweet_potato_readiness.md", f"""
# Domain B — phenolic acids in sweet potato

This scope contains **{len(sweet)} observations** from **{sweet.doi.nunique()} DOI family**, {sweet.food_matrix.nunique()} cultivar-origin matrices, {sweet.cooking_method_normalized.nunique()} methods and stated fresh-weight basis. Both included compounds have finite recorded descriptors. The design is useful within-source factorial evidence, but cultivar/origin strata are not independent papers or laboratories.

**Decision: C — more matched evidence required.** It is not an honest predictive domain until an independent study supplies comparable raw/cooked fresh-weight chlorogenic and/or ferulic acid measurements with explicit cooking conditions. No model is trained.
""")

prior=pd.DataFrame([
 {"rank":1,"target":"Vitamin C | carrot and spinach | boiling, steaming, microwave | fresh weight","existing_independent_sources":2,"existing_observations":len(vit),"need":"A third independent, protocol-aligned primary study","value":"Converts categorical near-matches into testable inter-laboratory evidence","literature_status":"Candidate search only; no observations admitted in v0.9"},
 {"rank":2,"target":"Chlorogenic acid and ferulic acid | sweet potato | boiling, steaming, microwave, baking | fresh weight","existing_independent_sources":1,"existing_observations":len(sweet),"need":"Independent raw/cooked HPLC study with cultivar and cooking details","value":"Tests whether Candidate B patterns transfer beyond one research group","literature_status":"Candidate search only; no observations admitted in v0.9"},
 {"rank":3,"target":"Existing multi-source categorical cells with unresolved basis/protocol conflict","existing_independent_sources":"varies","existing_observations":"see matrices","need":"Primary-table verification of basis, yield/moisture and analytical definition","value":"May resolve comparability without expanding unrelated coverage","literature_status":"Do not infer or convert missing basis"}
])
csv(prior,"ranked_evidence_acquisition_priorities.csv")
md("candidate_literature_investigation_report.md", """
# Bounded candidate-literature investigation

This iteration did not admit new measurements. The acquisition priorities above are deliberately evidence-shaped rather than row-count-shaped. Candidate papers must be primary experimental studies with traceable raw and cooked values, an explicit shared fresh-weight basis, method and duration, and a table/figure locator. Search snippets, reviews, and values lacking a verified measurement contract remain unverified candidates rather than dataset rows.

Known admitted provenance remains the v0.8 ledger: Lee et al. (2018), DOI 10.1007/s10068-017-0281-1, Tables 1–2; and Musilova et al. (2020), DOI 10.1155/2020/8856260, Table 6.
""")

md("complete_dataset_coverage_report.md", f"""
# Complete dataset coverage audit — v0.9

Parent dataset: v0.8, SHA-256 `{sha(DATA)}`. This package preserves its **{len(d)} observations**, **{d.doi.nunique()} DOI families**, **{d.compound.nunique()} compound labels**, **{d.food_matrix.nunique()} food matrices**, and **{d.cooking_method_normalized.nunique()} normalized cooking methods**; no observations were added, removed, converted or re-estimated.

Use the four coverage matrices and three cross-tabs for full counts. Rows are not independent merely because they differ by cultivar, method, compound or repeated treatment within a paper. `full_exact_matched_cell_matrix.csv` is the authoritative strict cell classification.

Key correction: there are **{(cells.unique_doi_families>1).sum()} categorical cross-source matches**, all of which require protocol review; there are **zero** strict cross-source replications after requiring identical, fully reported protocol dimensions. This corrects the overly broad interpretation of the six Vitamin-C category matches without altering their data or provenance.
""")
md("final_strategic_recommendation.md", f"""
# Final strategic recommendation — Iteration 6

**Stage A remains an evidence-recovery research prototype, not a deployable model, and Stage C remains blocked.** The row count is 439, but the limiting resource is cross-laboratory, protocol-comparable overlap—not observations.

1. Do not train another broad or narrow model on this iteration's unchanged data.
2. Make the next iteration a bounded primary-source acquisition and protocol-verification pass for ranked priority 1, then priority 2.
3. Admit data only when raw/cooked values, shared basis, cooking details, analytical definition and source locator are verified. Preserve near-matches as near-matches.
4. Consider a narrow exploratory model only after a domain has at least three independent source families with genuinely comparable cells, sufficient protocol reporting, and a pre-specified leave-one-source-family-out design whose folds are not pure extrapolation. It must predict apparent concentration ratio only, not total-mass retention.

The strongest current evidence is within-source factorial coverage (especially sweet potato phenolic acids) and categorical Vitamin-C overlap; neither is sufficient predictive evidence across laboratories.
""")

manifest={"package":"StageA_DatasetIntelligence_v0.9.0_2026-11-10","parent_dataset":str(DATA).replace('\\\\','/'),"parent_dataset_sha256":sha(DATA),"rows":len(d),"source_families":int(d.doi.nunique()),"new_observations":0,"purpose":"coverage, compatibility, source-confounding and readiness audit","stage_c_integration_authorized":False,"strict_cross_source_replications":int((cells.exact_match_status=="EXACT_CROSS_SOURCE_REPLICATION").sum()),"categorical_cross_source_near_matches":int((cells.exact_match_status.str.contains("NEAR")).sum())}
(HERE/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
checks=[len(d)==439,d.doi.nunique()==10,(cells.exact_match_status=="EXACT_CROSS_SOURCE_REPLICATION").sum()==0,len(vit)==12,len(sweet)==32]
assert all(checks), checks
(HERE/"SHA256SUMS.txt").write_text("\n".join(f"{sha(p)}  {p.name}" for p in sorted(HERE.iterdir()) if p.is_file() and p.name!="SHA256SUMS.txt")+"\n",encoding="utf-8")
print(json.dumps(manifest,indent=2))
