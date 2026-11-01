## CookRisk Stage B v4 Release Report

14 October 2026 | Provenance resolution and evidence verification

V4 improves the supplied v3 evidence release without forcing additional compounds or records. All 14 compounds, 73 records, 36 drugs/probes and 53 primary PMIDs remain. One record, SB-0067, has nine fields corrected or completed from primary full text. No records or compounds were added or removed; no bibliographic metadata fields required correction. No Stage A training, outlier analysis, exposure estimation or risk scoring was performed.

| Measure | Verified v3 | Final v4 |

| --- | --- | --- |

| Compounds / interaction records | 14 / 73 | 14 / 73 |

| Drugs or probes / primary PMIDs | 36 / 53 | 36 / 53 |

| Human PK / controlled clinical | 55 / 2 | 55 / 2 |

| Animal / in vitro | 10 / 6 | 10 / 6 |

| Records with numerical outcomes | 47 | 48 |

| Original v2 rows preserved exactly | 64 | 64 |

## Baseline verification and inventory

The actual v3 CSV, registry, validation report and mutation-test report match the reported baseline counts. V3 recorded 25/25 checks, zero errors and 6/6 mutation tests. One reporting discrepancy was found: its nine warning entries use eight distinct warning codes, because historical selection provenance occurs twice. V4 distinguishes entries from distinct categories.

The new inventory records filename, purpose, CSV row counts, source fields, inspection level and hash. The preservation manifest covers 1,325 supplied files, including v3 files and packages found under the inspected project directories. The original v3 input manifest is checked separately. No supplied release was overwritten. Inspection of a file's metadata is not a claim that its full text or every outcome was reviewed.

## Verification levels

| V4 record review scope | Records |

| --- | --- |

| Primary metadata only; inherited outcomes not re-extracted | 62 |

| Primary abstracts rechecked for the v3 additions | 8 |

| Selected inherited full-text outcome checks | 2 |

| Selected full-text re-extraction and correction | 1 |

Primary source metadata were rechecked for all 53 reports. The two inherited full-text checks concern saved endoxifen outcomes; they do not establish whole-paper re-extraction. Studies are grouped by PMID, not counted as independent trials for each row.

## Compound provenance and chemical identity

## Original nine selection history

Berberine, piperine, curcumin, EGCG and caffeine remain documented as the initial five anchors. Available methods establish a general inventory search but do not supply a contemporaneous per-compound selection ledger, historical paper trigger or exact selection date. These gaps remain unresolved.

Resveratrol, genistein, naringin and capsaicin have a documented v2 rationale based on reliable exact/parent identity and useful primary human evidence. Low-frequency genistein and naringin were explicitly justified. Specific historical paper triggers and original selection dates remain unestablished. The available documentation is retrospective; release dates are not substituted for selection dates.

The updated provenance audit covers all 14 compounds. The original-nine interaction-reference map is preserved separately. Interaction PMIDs/DOIs identify retained experimental evidence, not historical reasons for compound selection. External literature cannot recover missing personal project-selection notes.

## Five v3 additions

Sulforaphane, apigenin, kaempferol, daidzein and quercetin retain stable IDs, canonical names, aliases, identity information, rationale, selection references, evidence coverage and provenance status. Their dated v3 selection decisions are available and were rechecked against supporting primary snapshots. Identity and dietary/interaction rationales remain distinct from later retention applicability.

Daidzein remains an aglycone and is not merged with daidzin, acetyldaidzin or other glycosides. Standalone quercetin remains separate from the mixed quercetin/total-flavonol measurement group. The 15 mixed-group master rows and their reported DOIs are listed for further primary-source checking; none is assigned to standalone quercetin by this release.

## Cooking and processing provenance

Two additional primary processing full texts were reviewed for methods and analyte scope. The daidzein-context study hydrolyzes glycosylated isoflavones before assay, so its result is not automatically native free-daidzein retention. The onion study distinguishes conjugates, total flavonols and weight-basis effects, which cannot certify the mixed master group. Both support processing context only; no new retention coefficient or master link was created.

Sources: Traditional and Domestic Cooking Dramatically Reduce Estrogenic Isoflavones in Soy Foods, PMC11011382, methods/sample preparation; Influence of Cooking Methods on Onion Phenolic Compounds Bioaccessibility, PMC8151956, analytical methods and sections 3.2-3.3. Their DOI and cache paths are in processing_provenance_audit.csv. Neither publication is counted among the 53 interaction reports.

## Evidence verification and justified correction

## SB-0067 apigenin and imatinib

Primary full text PMC3863468 supplied missing methods: 20 male Sprague-Dawley rats, four groups with n=5 each, and imatinib 30 mg/kg after apigenin pretreatment. Apigenin regimens were 165 mg/kg for 15 days, single 165 mg/kg or single 252 mg/kg. Preparation, direction, limitations and source locator were updated alongside the numerical outcome.

| Imatinib AUC to infinity | Mean plus or minus SD in mg h per L |

| --- | --- |

| Control | 90.988 +/- 11.585 |

| Repeated apigenin 165 mg/kg | 68.805 +/- 7.432 |

| Single apigenin 165 mg/kg | 127.514 +/- 12.332 |

| Single apigenin 252 mg/kg | 114.502 +/- 8.634 |

Table 1 marks each active group P<0.05 versus control. Repeated treatment lowered exposure; single treatment increased it. Results prose says acute Cmax decreased, while Table 1 shows an increase. That inconsistency is flagged and Cmax interpretation withheld. No human conclusion or effect-size pooling was made. Source: PMID 24369535, DOI 10.1155/2013/789184; Experimental 2.1/2.5 and Table 1.

## Apigenin and rutin attribution remains provisional

The primary publisher page for PMID 24871039, DOI 10.1007/s13318-014-0203-z, exposes its abstract but identifies the full article as subscription content. The abstract still does not establish separate versus combined apigenin/rutin groups. SB-0066 remains a provisional preparation context; no isolated-apigenin numerical magnitude is assigned. A preview check is not full-text review.

## Other v3 additions and inherited outcomes

All nine actual v3 addition IDs SB-0065 through SB-0073 were inspected. Eight remain abstract-level reviews; missing details stay explicit. Sulforaphane retains its cohort null and subgroup finding; daidzein retains metabolic ratios separately from drug AUC and disputed CIs are withheld; quercetin retains genotype, route and regimen distinctions, including a nonsignificant interval crossing 1.

The saved curcumin/endoxifen outcomes SB-0016 and SB-0017 agree with inherited full-text PMC6468355 Table 2: -7.7% (95% CI -15.4 to +0.7; p=0.07) for curcumin alone and -12.4% (-21.9 to -1.9; p=0.02) with piperine. These rows remain byte-for-byte equivalent at the field level. The remaining 62 original baseline rows were not independently re-extracted in v4.

## Warnings validation and reproducibility

## Warning resolution

The ledger retains all nine v3 warning entries and adds the new source table/prose discrepancy. Twelve previously unavailable Crossref title lookups were successfully recovered. Inherited full-text scope and retention provenance were partially addressed. Historical selection sources, missing DOI fields for PMIDs 18928093 and 22512082, apigenin/rutin attribution, daidzein abstract ambiguity and bounded-review limitations remain explicit.

V4 has 9 open warning entries under 8 distinct codes. This is not a clean scientific-adjudication claim. The source table/prose warning replaces no historical warning; it is separately recorded. Fresh bibliographic title verification does not establish numerical correctness.

## Actual v4 technical validation

Status PASS_WITH_WARNINGS: 24/24 checks passed, 0 errors. Mutation tests passed 8/8: six existing v3 scenarios were rerun through the supplied validation function read-only, plus two v4 tests for corrected-claim tampering and significance overclaim. V4 did not simply reuse the old validation results.

Checks cover schema, identifiers, duplicate contexts and structures, classifications, foreign keys, references, units/ratio context, current selection sources, unknown dates, source-to-claim matching, actual-source numeric diagnostics, change-log completeness, nonsignificant-interval interpretation, Crossref recovery and preservation hashes. Literal numeric checks support manual review and cannot prove endpoint semantics by themselves.

All 1,325 manifest-listed files and the original v3 preservation manifest passed hash checks. The original 64 rows remain unchanged; only SB-0067 differs from v3 and all nine changed fields are recorded. Newly reviewed claims and inherited claims carry separate review levels.

## Files and reproducible execution

The new v4 folder contains the registry, versioned evidence CSV, all-14 provenance audit, source and outcome audits, primary registry, original-nine reference map, field-level change log, warning ledger, processing audit, mixed-group source inventory, validation JSON, mutation results, inventory and hashes, targeted acquisition and screening logs, README, this report and build/validation/package scripts. Source cache paths can reference immutable supplied files.

Run build.py, validate.py, report.py and package.py from this new folder using Python. Core build/validation use standard libraries; PDF generation uses reportlab and Arial. Full reproduction requires the supplied workspace and inherited v3 caches. collect.py is optional online acquisition, not required for offline validation. The package is incremental rather than a replacement for the workspace.

## Remaining work

Recover contemporaneous selection notes, obtain lawful access to the paclitaxel full text, resolve primary analyte provenance for mixed cooking data and request source clarification for reporting inconsistencies. Extend independent extraction review where needed. Null findings remain context-specific; no database row means no qualifying retained evidence, not no possible interaction. No additional interaction record was scientifically necessary for this pass.