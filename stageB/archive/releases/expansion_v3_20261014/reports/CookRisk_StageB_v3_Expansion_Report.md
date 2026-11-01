## CookRisk Stage B Compound Expansion Report

Version 3  |  14 October 2026  |  Selection provenance and interaction evidence only

This release adds 5 compounds and 9 records to the supplied 64-record Stage B database. The result is 73 records for 14 anchor compounds and 36 drugs or probes, supported by 53 primary reports. Selection documentation is kept separate from interaction citations. Missing historical selection sources remain unresolved.

| Measure | Supplied v2 | New v3 |

| --- | --- | --- |

| Interaction records | 64 | 73 |

| Anchor compounds | 9 | 14 |

| Drugs or probes | 34 | 36 |

| Primary reports by unique PMID | 45 | 53 |

| Human PK plus controlled clinical | 49 + 2 | 55 + 2 |

| Animal plus in vitro | 7 + 6 | 10 + 6 |

## Files available and inspected

Work used the current folder only. No remote repository was required. The inventory inspected metadata and hashes for 1,203 relevant data, source and documentation files; a short inventory lists 60 key files individually with purpose, row count and source fields. Text was extracted from 31 supplied narrative documents with no extraction failures. This does not mean every cached candidate paper was fully screened.

| Available material | Role and source information |

| --- | --- |

| Expanded evidence 64 rows; study registry 45 rows | Primary interaction references and source cache links |

| Compound mapping and prioritization 198 rows each | Names, structures, identity status and selection context |

| Master dataset 1350 observations | Inherited food and cooking context; provenance not newly certified |

| Search logs, screening, DOI audits and source caches | Retrieval and evidence verification trail |

| Methods, reports, weekly logs and research PDFs | Selection history search and scientific context |

Outputs: file_inventory.csv contains the full listing; inventory_key_files.csv is the short handover inventory. Supplied inputs and existing releases were preserved. Stage A training, outlier handling, Stage C exposure and Stage D risk were outside scope.

---

## Compound selection provenance

## What can be established for the original nine

Berberine, piperine, curcumin, EGCG and caffeine are documented as the initial five anchors. The initial methods describe a full inventory search, but no contemporaneous per-compound selection ledger or specific historical selection-paper trigger was found. Their original selection sources and addition dates remain unresolved.

Resveratrol, genistein, naringin and capsaicin have an explicit v2 selection rationale: reliable exact or parent identity and useful primary human evidence. The v2 methodology specifically explains why low-frequency genistein and naringin were selected. However, a specific primary-paper trigger for each historical choice and the exact original addition date are not established. The 6 October release date is not substituted for a selection date.

See compound_selection_provenance_audit.csv for all nine determinations and original_nine_interaction_reference_map.csv for their retained interaction PMIDs and DOIs. Those interaction references do not prove why a compound was originally chosen.

## Five new decisions documented in this release

| Compound | Reason and supporting source | Rows |

| --- | --- | --- |

| Sulforaphane | Verified broccoli compound; human CYP3A probe trial PMID 23153560; processing support PMID 22471240 | 1 |

| Apigenin | Verified dietary flavone; regimen-dependent animal drug disposition PMID 24369535; provisional preparation context PMID 24871039 | 2 |

| Kaempferol | Verified dietary flavonol; animal tamoxifen and metabolite findings PMID 18338336 | 1 |

| Daidzein | Soy aglycone; human theophylline and caffeine-probe study PMID 12756512; dietary/form context PMID 11285356 | 2 |

| Quercetin | Dietary flavonol; human fexofenadine PMID 19221726 and midazolam PMIDs 21680781 and 25988261 | 3 |

Each current decision has a dated selection record, rationale, primary identifiers and identity source. Dietary relevance, human evidence where available, retention availability, identity confidence and feasibility were considered qualitatively; no numerical selection or risk score was invented.

Sulforaphane, apigenin and kaempferol retain supplied molecular IDs and exact-identity mappings. Daidzein and quercetin receive standalone PubChem-based IDs after property and synonym verification. Daidzein is not substituted for daidzin or acetylated glycosides. Quercetin is not linked to the mixed quercetin/total-flavonol measurement group. Cooking coverage is limited and does not govern literature eligibility by itself.

---

## New evidence findings and research scope

The nine new records SB-0065 through SB-0073 comprise six human PK/probe records and three animal records from eight primary reports. Same-report drug endpoints share a Study_ID. There are 47 numerical-outcome records overall, five newly added; these include metabolic ratios and are not all clinical effect sizes.

## Human evidence and tested nulls

Sulforaphane: broccoli sprout preparation did not change cohort-wide basal CYP3A activity or attenuate rifampicin induction; a high-basal-activity subgroup had increased midazolam AUC. The overall null and subgroup finding remain together, with no extracted subgroup magnitude. The source enrolled 24 adults. [PMID 23153560]

Daidzein: theophylline AUC increased about 34% after 200 mg twice daily for 10 days in a 20-person parallel trial. The same report found a caffeine metabolic-ratio change of -19.8 +/- 19.7% (P=0.009), not a caffeine AUC change. Ambiguous CI and baseline-day wording were flagged; disputed CIs were omitted. [PMID 12756512]

Quercetin: fexofenadine AUC rose 55% and Cmax 68% in 12 subjects receiving 500 mg three times daily for seven days. Another study reported reduced midazolam exposure in CYP3A5*1 genotype groups. A separate 10-person study found a single-dose null and a repeated oral AUC GMR of 0.82 (90% CI 0.61-1.10), a nonsignificant trend; the three-person IV substudy tended oppositely. [PMIDs 19221726, 21680781, 25988261]

## Animal evidence and preparation limits

Apigenin: acute versus 15-day treatment changed imatinib/metabolite disposition in rats, interpreted by the authors as regimen-dependent metabolic modulation. A separate paclitaxel abstract reports increased exposure under apigenin/rutin conditions, but separate versus combined group preparation is unresolved. That record is explicitly provisional for preparation attribution; no isolated-apigenin magnitude is assigned. [PMIDs 24369535, 24871039]

Kaempferol: oral coadministration increased rat tamoxifen exposure, while 4-hydroxytamoxifen PK was unchanged. CYP3A/P-gp inhibition was proposed. Numerical effect magnitude was not extracted. This remains animal evidence. [PMID 18338336]

## Search and processing context

Five title-focused Europe PMC queries retrieved the first 100 candidates each, followed by ten exact PMID verifications. Web discovery was followed by cached primary metadata checks. Broad retrieval returned 500 candidates before deduplication; unreviewed candidates are not labelled excluded. This is a bounded expansion, not a systematic review.

One additional processing publication describes thermal effects on sulforaphane formation in broccoli. It supports selection context but is not an interaction row, a universal retention coefficient or Stage C calculation. A separate isoflavone publication supports dietary and chemical-form context. These two reports are outside the 53 interaction-report count.

---

## Validation handover and unresolved work

## Validation results

Status: PASS_WITH_WARNINGS. All 25 of 25 checks passed with zero errors and 9 warning categories. All 6 mutation tests passed. Hash checks confirmed that all 1,259 supplied files in the preservation manifest are unchanged, and the original 64 evidence rows match exactly.

Checks cover duplicate IDs and identity keys, duplicate experimental contexts, schema preservation, compound links, PMID/DOI format, cached title/author/year/DOI consistency, selection citations, classifications, unit or ratio context and source-support ledgers. All 53 primary-report metadata records were concordant with cached MED records. Five new Crossref lookups were concordant; three were unavailable. Existing v2 Crossref statuses are retained, not described as new verification.

New numerical outcomes were manually compared with source abstracts and checked using source excerpts and numeric diagnostics. These checks cannot automatically prove scientific semantics. The 64 inherited outcome extractions were preserved and their metadata rechecked; their full-text quantitative claims were not independently re-extracted in v3.

## Main files created

outputs contains the 73-row versioned evidence release, nine new rows, 14-compound registry, selection-source records, provenance and source audits, 53-report registry, original-nine reference map, claim support and outcome audits, inventory, candidate decisions, search/screening logs, conflict synthesis and release summary. audit contains machine-readable validation, six self-tests and preservation hashes. sources contains public response snapshots; scripts contains offline builders and validation.

README.md explains usage and future additions. This PDF and its Markdown counterpart summarize the release. The versioned ZIP packages the new folder; baseline inputs and inherited caches remain in the supplied workspace and are needed for full offline rebuild and preservation checks.

## Unresolved issues and recommended work

Recover contemporaneous selection notes for the original nine; preserve unknown history until documented. Obtain full text to resolve the apigenin/rutin groups and missing doses or sample sizes. Resolve standalone quercetin and daidzein retention provenance before any later linkage. Review the inherited identity and food-source flags; do not merge aliases, salts, aglycones and mixed analytes by name alone.

Expand screening beyond capped results, obtain an independent extraction review, and recheck inaccessible DOI metadata. Null findings apply to tested conditions; no retained row does not establish no interaction. Supplement and animal doses cannot be interpreted as ordinary food risk. No Stage A modification, exposure estimation or risk scoring was performed.

## Primary references for the new interaction records

PMID 12756512 | DOI 10.1007/s00228-003-0596-0 | https://pubmed.ncbi.nlm.nih.gov/12756512/

PMID 18338336 | DOI 10.1002/bdd.593 | https://pubmed.ncbi.nlm.nih.gov/18338336/

PMID 19221726 | DOI 10.1007/s00228-009-0627-6 | https://pubmed.ncbi.nlm.nih.gov/19221726/

PMID 21680781 | DOI 10.1177/0091270011406278 | https://pubmed.ncbi.nlm.nih.gov/21680781/

PMID 23153560 | DOI 10.1016/j.taap.2012.10.029 | https://pubmed.ncbi.nlm.nih.gov/23153560/

PMID 24369535 | DOI 10.1155/2013/789184 | https://pubmed.ncbi.nlm.nih.gov/24369535/

PMID 24871039 | DOI 10.1007/s13318-014-0203-z | https://pubmed.ncbi.nlm.nih.gov/24871039/

PMID 25988261 | DOI 10.1002/jps.24500 | https://pubmed.ncbi.nlm.nih.gov/25988261/