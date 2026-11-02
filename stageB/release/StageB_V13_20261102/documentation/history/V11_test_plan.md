# V11 Comprehensive Test Plan

Test cases are defined in `audit/v11_test_plan.csv`. Automated assertions and manual scientific reviews are reported separately. A passing script execution alone does not count as a passed test. Each result contains expected rule, actual observation, status, severity, affected records, and diagnostic.

## Test groups

- **ST-01 — Structural:** All registry/evidence rows use a single documented header schema. (Automated).
- **ST-02 — Structural:** Required identifiers and category fields are nonblank and allowed. (Automated).
- **ST-03 — Structural:** Compound IDs and Evidence IDs are unique and stable. (Automated).
- **RI-01 — Referential integrity:** Every evidence Compound_ID resolves to one registry row and its name agrees. (Automated).
- **RI-02 — Referential integrity:** Every evidence drug/probe resolves in drug registry. (Automated).
- **RI-03 — Referential integrity:** Every Study_ID resolves in study registry. (Automated).
- **RI-04 — Referential integrity:** Every PMID/DOI resolves in publication index or is explicitly DOI-only. (Automated).
- **RI-05 — Referential integrity:** Every source cache or source URL referenced by a record exists. (Automated).
- **RI-06 — Referential integrity:** Selection decision/rationale coverage spans all anchors. (Automated).
- **CH-01 — Chemical identity:** All CIDs are valid numeric PubChem IDs and unique. (Automated).
- **CH-02 — Chemical identity:** SMILES, InChI and InChIKey match captured PubChem data. (Automated).
- **CH-03 — Chemical identity:** InChIKey syntax and exact-structure uniqueness hold. (Automated).
- **CH-04 — Chemical identity:** Standard names/aliases occur in CID synonym responses. (Automated).
- **CH-05 — Chemical identity:** Near-duplicate, stereo, salt, tautomer, glycoside/aglycone pairs are reviewed. (Human).
- **FC-01 — Food context:** Every food-context claim has a traceable source independent of interaction evidence. (Human).
- **PV-01 — Publication integrity:** PMIDs exist and title/DOI metadata agree with PubMed. (Automated).
- **PV-02 — Publication integrity:** DOI normalization and PMID:DOI relationships are one-to-one where known. (Automated).
- **PV-03 — Publication integrity:** Bibliography and study registry contain the same publication set. (Automated).
- **PV-04 — Publication integrity:** Overlapping cohorts and multiple reports are distinguished from publications. (Human).
- **EV-01 — Evidence integrity:** Evidence IDs, schema, required fields, and duplicate rows are checked. (Automated).
- **EV-02 — Evidence integrity:** Compound, probe, study, publication, source, and claim references reconcile. (Automated).
- **SC-01 — Study classification:** Human, animal, and in-vitro labels match population/species descriptions. (Automated + Human).
- **SC-02 — Study classification:** Human-derived cells/microsomes are not labeled clinical PK. (Automated + Human).
- **NX-01 — Numerical validation:** Outcome numbers are separated from doses, sample sizes, PMIDs, and years. (Automated + Human).
- **NX-02 — Numerical validation:** Units, endpoint labels, CI/P-value forms and effect direction are checked. (Automated + Human).
- **NX-03 — Numerical validation:** Reported values and calculations are verified against source tables. (Human).
- **CL-01 — Claim verification:** All 263 records have explicit source verification states and locators. (Automated).
- **CL-02 — Claim verification:** Source actually supports compound/probe/endpoint/number/preparation. (Human).
- **CL-03 — Claim verification:** Full text has been examined before the record is called full-text verified. (Human).
- **PR-01 — Provenance:** Each anchor has a decision, rationale and retrospective/historical status. (Automated).
- **PR-02 — Provenance:** Original nine dates/rationales are not invented. (Automated + Human).
- **WA-01 — Warning ledger:** Warning IDs/statuses are valid, unique and inherited; affected entities exist. (Automated + Human).
- **WA-02 — Warning ledger:** Scientific closures have primary-source support. (Human).
- **DD-01 — Duplicate/overlap:** Exact duplicate evidence rows and study-context duplicates are detected. (Automated).
- **DD-02 — Duplicate/overlap:** Near-duplicate compounds and overlapping cohorts are adjudicated. (Human).
- **CD-01 — Cooking-domain separation:** Cooking retention and interaction records remain separate and linked by identity only. (Automated).
- **RG-01 — Regression:** V10 rows/anchors/cooking/warnings remain present; intended edits have a diff. (Automated).
- **RP-01 — Reproducibility:** Build scripts use relative paths, stable IDs, captured inputs and deterministic outputs. (Automated).
- **RP-02 — Reproducibility:** A clean-copy rebuild reproduces release CSVs and summary counts. (Automated).
- **MT-01 — Mutation testing:** One-defect mutations are detected by the intended rule in isolated temporary files. (Automated).
- **RI-07 — Release integrity:** Manifest covers all release files and no unexpected V10 changes occur. (Automated).

Manual source extraction, food-context substantiation, cohort independence, stereochemical/tautomer adjudication, and table-level numeric validation require a human reviewer; those checks are not credited as automated passes.
