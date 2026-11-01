## CookRisk Stage B v5 Expansion Report

14 October 2026 | Evidence-backed compound and interaction database release

V5 adds 12 compounds and 45 primary-source interaction records to the verified v4 baseline. The final database contains 26 compounds, 118 records, 58 drugs/probes and 80 primary reports. All 73 inherited records and their stable identifiers remain unchanged. No Stage A training or outlier work, exposure estimation, clinical risk scoring, Stage C or Stage D was performed.

| Measure | Verified v4 | Final v5 |

| --- | --- | --- |

| Compounds | 14 | 26 |

| Evidence records | 73 | 118 |

| Drugs and probes | 36 | 58 |

| Primary reports by unique PMID | 53 | 80 |

| Human PK / controlled clinical | 55 / 2 | 61 / 2 |

| Animal / in vitro | 10 / 6 | 27 / 28 |

| Numerical-outcome records | 48 | 73 |

## Changes and planning targets

The 12 additions are myricetin, luteolin, ellagic acid, gallic acid, ferulic acid, caffeic acid, chlorogenic acid, rosmarinic acid, naringenin, bergamottin, chrysin and fisetin. The 45 new records are SB-0074 through SB-0118 and are supported by 27 new primary reports. No inherited evidence record was corrected or removed. Registry coverage counts were updated with a separate field-level change log.

The 25-30-compound and approximately 80-120-primary-report planning ranges were reached. The 150-200-record range was not reached: this bounded pass retained 118 supported records. Remaining candidates require further source and preparation review; records were not duplicated, inferred or weakened to fill the gap. This result does not imply the broader literature contains no further eligible evidence.

## Available files and baseline freeze

The current-folder inventory includes the v4 registry, evidence table, primary reports, claim and warning audits, identity mappings, candidate files, search logs, primary caches, scripts and previous packages. Filenames, purposes, row counts, source fields and inspection status are recorded. All 1,383 files in the v5 preservation manifest are unchanged. Metadata/hash inventory is distinguished from scientific source review.

Direct verification confirmed the reported v4 counts, 48 numerical records, original 64 preserved rows, 24/24 technical checks, 8/8 mutation tests and nine open warning entries across eight codes. V4 was treated as immutable; no remote repository was needed.

## Candidate selection identity and food provenance

Sixteen candidates were considered: 12 selected, four deferred and zero rejected. Selection considered dietary relevance, primary drug endpoints, human evidence where available, identity/analyte specificity, cooking information, source accessibility and incremental scientific value. No numerical selection score was created. The dated selection ledger is separate from experimental interaction citations.

| New compound | Evidence basis and important restriction |

| --- | --- |

| Myricetin | Animal PK plus microsomal null; standalone parent because original group is uncertain |

| Luteolin | GHB transport and clearance; experimental IV doses are not food exposure |

| Ellagic acid | Isolated warfarin arm; separate from total ellagic acid and extracts |

| Gallic acid | Named renal transport probes and paclitaxel null; not a human RLQ drug-interaction trial |

| Ferulic acid | Clopidogrel changes compound disposition; reverse direction preserved |

| Caffeic acid | Named OAT1/OAT3 probes; parent-connectivity mapping only |

| Chlorogenic acid | Platinum-drug cell effects and resistant-cell null; isomers not pooled |

| Rosmarinic acid | Furosemide effect, valsartan null and reverse probenecid interaction |

| Naringenin | Animal PK and microsomal null; generic parent CID 932, no uncertain master link |

| Bergamottin | Human isolated capsules distinguish constituent from grapefruit juice |

| Chrysin | Human uncontrolled pilot and rat caffeine null; no safety conclusion |

| Fisetin | Separate named chemotherapy experiments; synergy and no-synergy distinguished |

Hesperetin was deferred because the accessible rasagiline abstract did not resolve separate-compound attribution. Baicalein requires further preparation and dietary-context review. Theobromine had an old candidate interaction citation without sufficient verified details. Lycopene cooking/bioavailability papers alone did not establish an eligible drug interaction. These are bounded-review deferrals, not evidence of no possible interaction.

Seven additions reuse verified exact or parent-connectivity inventory mappings; five use separately verified external parent identities. Naringenin is not naringin, and a stereochemically unspecified study was not assigned to natural (S)-naringenin. Myricetin was not linked to its uncertain master group. Existing quercetin/total-flavonol and daidzein/glycoside restrictions remain.

Primary food/processing papers on edible berry flavonols (PMID 10794622), berry processing (11032486) and cooked-tomato bioavailability (15309458) were retained separately. They do not count among the 80 interaction reports or certify native aglycone retention. No retained dose or retention coefficient was calculated.

## Primary evidence results and review scope

The 45 additions comprise six human PK/probe records, 17 animal records and 22 in-vitro records. Eight have selected full-text methods/outcome review and 37 have primary abstract-level manual extraction. Full-text availability alone is not described as full review. All inherited review levels remain explicit in all_record_review_audit.csv.

## Human evidence

Bergamottin capsules increased felodipine exposure in an 11-person crossover: at 12 mg, Cmax increased 40% and AUC 37%. Larger grapefruit juice effects were not attributed to bergamottin alone. Chrysin with irinotecan was an uncontrolled 20-patient pilot with PK in 18 patients; its historical-comparator metabolite ratio does not prove clinical protection or safety. [PMIDs 15592332, 16003560]

New quercetin records cover pravastatin and two talinolol experiments; curcumin adds a human talinolol experiment. One quercetin study had nonsignificant mean talinolol changes; another reported decreased exposure with genotype variation. Shared genotype-pool descriptions do not establish independent trial populations. Ambiguous pravastatin percentage/CI wording was withheld pending reliable table review. [PMIDs 22114872, 24472704, 23422925, 17468862]

## Preclinical effects null findings and context differences

Myricetin increased exposure to several orally administered drugs in rats, but IV doxorubicin/docetaxel results were null under tested conditions; a coamorphous formulation was identified separately. Luteolin changed GHB clearance and sleep duration in rats and inhibited named GHB uptake in cells. Ferulic acid with clopidogrel and rosmarinic acid with probenecid are reverse interactions affecting the food compound.

Rosmarinic acid increased rat furosemide exposure but did not significantly change valsartan PK. Gallic/caffeic acid assays use named transport probes, not general enzyme statements. Ellagic acid and quercetin warfarin arms were separated from whole plant extracts. Chlorogenic acid/platinum-drug effects were cell-context dependent, including a resistant-cell null; no pooled interaction coefficient was created.

Fisetin experiments include drug-specific synergy and no synergy. No synergy with mitoxantrone or methotrexate does not mean no interaction. A separate microsomal study found no paclitaxel metabolism inhibition by myricetin, gallic acid or naringenin, while other tested compounds inhibited metabolism. Separate compounds/drugs share one PMID; metabolites and donors were not inflated into extra reports. [PMIDs 26884726, 12920504]

Five new records are classified as null findings and two as no synergy detected; additional rows preserve mixed endpoint/route nulls and nonsignificant changes. The 73 numerical-outcome records include exposure measures, assay constants, metabolic ratios and a combination index. The combination index is not a confidence interval or clinical risk score.

## Search validation reproducibility and limitations

## Search and screening

Sixteen broad queries and 16 historical title-focused queries used a 100-result cap. They retrieved 1892 candidate occurrences, corresponding to 1850 unique retrieved records and 42 repeated retrieval occurrences. Exact PMID and primary food-source follow-up added verification snapshots. 34 sources received explicit inclusion, deferral or context-only decisions. Remaining retrieved candidates are marked not fully screened, not falsely excluded.

## Actual v5 validation

Status: PASS_WITH_WARNINGS. All 53/53 checks passed with zero errors: 24 existing v4 checks rerun against its immutable baseline and 29 v5 checks for append-only expansion. All 11/11 mutation tests passed, preserving the eight existing scenarios and adding tests for unsupported new quantities, no-synergy misclassification and reversed affected entity.

An offline rebuild reproduced 25 CSV/JSON outputs byte-for-byte. Validation covers stable IDs, duplicate contexts, identity keys, schema, foreign keys, bibliographic metadata, selection sources, units, source/claim diagnostics, study counting, null/reverse classifications, change logs and preservation. Manual source interpretation remains separate from these technical checks.

## Warnings and inherited limitations

There are 15 open warning entries across 14 distinct codes. The original-nine selection history remains unresolved or only retrospectively documented. Apigenin/rutin attribution and the apigenin Cmax prose/table discrepancy remain flagged; no new source clarification was obtained. Quercetin and daidzein cooking/analyte links remain unvalidated. Earlier bibliographic resolutions remain recorded rather than silently reset.

New limitations include missing abstract doses/sample sizes, parent-identity scope, uncertain food measurement provenance, source unit/percentage ambiguities, possible participant overlap and the unmet record target. Twenty-four new primary reports had concordant fresh Crossref titles; two lookups were unavailable and one new report had no supplied DOI. Primary MED identifiers remain verified. No independent second-reviewer or exhaustive cross-paper independence claim is made.

## Files created and recommended work

The separate v5 folder contains the 26-compound registry, 118-row evidence CSV, 45-row incremental table, 80-report registry, selection and identity audits, 16-candidate decisions, search/screening logs, new and inherited claim audits, all-record review scopes, context comparison, processing audit, warning ledger, field-level registry and evidence logs, preservation hashes, validation/mutation/rebuild JSON, README, scripts, report and ZIP.

The package is incremental and requires the supplied workspace for inherited sources and baseline validation. Next work should review deferred primary preparations, resolve reporting ambiguities and original selection records, extend uncapped source screening and obtain independent extraction review. Animal/cell and supplement results must remain distinct from ordinary dietary exposure and clinical risk.