# CookRisk Stage B V10 handoff

**Release:** `Documents/CookChem/stageB/release_v10_20261030`  
**Scope:** Stage B literature evidence only. No Stage A model, exposure estimate, patient risk score, or cooking-retention claim was added.

## V9 baseline recalculation

The underlying V9 files contain **74 compound anchors, 210 interaction records, and 103 distinct drug/probe labels**. This differs from the handoff's 130 drug/probe figure. There are **130 distinct PMID publications** and **125 distinct nonblank DOIs**. Five PMID publications have no DOI; the six blank DOI evidence rows include two records for one of those publications. DOI and PMID counts are therefore separate identifier counts, not interchangeable publication counts. No conflicting PMID-to-DOI mapping was found among populated identifiers.

V9 evidence classes are 70 human pharmacokinetic, 4 controlled clinical, 51 animal, and 85 in-vitro records; no separate “other human clinical” class is present. A digit-based scan finds 114 outcome fields containing numeric text. The warning ledger has 28 rows across 27 codes: 15 unresolved, 10 partially resolved, 1 resolved, and 2 not applicable (25 open or partial). The handoff's “25 inherited plus 3 new” describes the 28 rows, not 25 total rows.

The V9 verification inputs record 21 selected full-text reviews, 164 abstract reviews, and 4 abstract-supported qualitative records with numeric extraction pending. V9's own new-record claim audit adds 2 full-text-table verified and 19 abstract-verified records. Existing status labels and numerical holds were retained.

## V10 expansion

V10 contains **100 anchors** (+26) and **263 evidence records** (+53), or 52.6% of the 500-record research target; 237 records short of that target. It has 117 distinct drug/probe labels, 140 PMID publications plus one DOI-only publication, 136 distinct nonblank DOIs, and 141 publication entries in the study index. Independent cohorts were not counted because overlapping or repeated cohorts could not be reliably identified from publication identifiers alone.

All 53 new records are in vitro. The final evidence classes are 70 human pharmacokinetic, 4 controlled clinical, 51 animal, and 138 in vitro. Forty-seven of the 53 new outcome fields contain numeric text; combined with V9 the digit-based total is 161. Numeric text is not a validation of clinical relevance or effect-size comparability.

The 26 new anchors are:

- **Phenolic acids:** p-coumaric acid, gentisic acid, 4-hydroxybenzoic acid, protocatechuic acid, sinapinic acid, syringic acid. Included for primary human OAT transporter assays. Gentisic acid can also be a salicylate metabolite.
- **Flavonoid glycosides and tea polyphenol:** hyperoside, isoquercetin, neohesperidin, theaflavin. These four have a single OATP4C1 screen with no significant effect; that is a weak inclusion basis and is flagged.
- **Scutellaria botanical constituents:** baicalein, baicalin, scutellarein, wogonin, oroxylin A, 7-methoxyflavanone, wogonoside. Included on CYP1A/CYP2C9 assay evidence; these are medicinal-botanical or supplement-context anchors, not established ordinary-food exposures.
- **Rosemary constituents:** carnosic acid and carnosol, supported by human-derived CYP assays; the carnosol abstract does not provide isoform-level results.
- **Other food-associated compounds:** 6-shogaol (ginger), xanthohumol (hops), glycitein, genistin and daidzin (soy), coumestrol (legumes/sprouts), and galangin (propolis/honey and plant foods). Selection rationales and limitations are in `outputs/v10_selection_decisions.csv`.

The four null-only anchors remain explicitly flagged and should be reconsidered if a stricter policy requires positive interaction evidence. Herbal botanical anchors are also distinguishable from everyday-food exposure. The 500-record target was not pursued by duplicating compound/drug arms; this remains a targeted, non-systematic evidence expansion.

## Identity, provenance, and warnings

All **100/100** anchors now have PubChem CID, SMILES, InChI, and InChIKey. PubChem name/alias records match all 100 registry names or aliases; all 100 InChIKeys are unique, with no exact-structure duplicate detected. V9's 13 missing structure rows were completed in the V10 registry only. The inherited V9 registry and records were not edited. PubChem-standardized strings do not establish universal tautomer/protonation equivalence across databases; near-duplicate chemical forms still need expert review.

Historical provenance for the original nine remains limited: the search date is documented, but no original selection date is recovered. Four have partially documented V2 prioritization rationales and five retain only the initial-anchor record; all V10 selection rationales are retrospective.

All 28 inherited warning rows were carried forward. Seven V10 warnings were added: one partially resolved structure-standardization note and six unresolved limitations. The combined ledger has **35 rows, 33 codes, 21 unresolved, 11 partially resolved, 1 resolved, and 2 not applicable**. Apigenin/rutin attribution, apigenin Cmax, daidzein reporting, cooking-retention linkage, and the four resveratrol numeric holds remain as inherited. The cooking-retention table was carried forward byte-for-byte and remains a separate evidence domain.

Verification summary for the 263 records: 23 full-text reviewed/verified records inherited from earlier work, 233 abstract-verified records, 4 abstract-supported qualitative records with numerical extraction pending, and 3 DOI-only shogaol assay records whose article abstract was located but whose full-text table extraction remains incomplete. No metadata-only or secondary-source-only records were newly asserted. New V10 source values are generally abstract-level and are labeled conservatively; source locators and residual limits are in `outputs/v10_source_audit.csv` and `outputs/claim_support_and_verification_v10.csv`.

## Validation and preservation

- V9 baseline validation was rerun in the V10 copy before expansion: PASS; 7/7 mutation tests detected.
- V10 validation: **21/21 integrity checks passed; 10/10 mutation tests detected**. Results are in `audit/v10_validation_report.json`.
- Exact preservation of inherited V9 evidence rows passed. All 30 files listed in the V9 release checksum manifest match the separate V9 release; no mismatches were found.
- Original V9 release remains at `Documents/CookChem/stageB/release_v9_20261029` and is unchanged.

## Main deliverables

- `outputs/compound_registry_v10.csv`
- `outputs/stageB_food_drug_interactions_v10.csv`
- `outputs/drug_probe_registry_v10.csv`, `outputs/study_registry_v10.csv`, `outputs/source_bibliography_v10.csv`
- `outputs/identity_structure_audit_v10.csv`
- `outputs/v10_selection_decisions.csv`, `outputs/v10_candidate_screening_log.csv`
- `outputs/v10_source_audit.csv`, `outputs/claim_support_and_verification_v10.csv`
- `outputs/warning_resolution_ledger_v10.csv`, `outputs/v10_change_log.csv`
- `outputs/cooking_retention_evidence_v9.csv` (separate and unchanged)
- `audit/v10_baseline_recalculation.json`, `audit/v10_inherited_v9_hashes.json`, `audit/v10_validation_report.json`
- `build_v10.py`, `validate_v10.py`, `finalize_v10.py`, `README_V10.md`

The source search was targeted rather than systematic. The release remains a literature evidence resource and is not clinical decision support.
