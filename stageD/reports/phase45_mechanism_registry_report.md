# Stage D Phase 4/5 mechanism evidence tranche

Review date: 2026-11-04  
Status after Cycle 5: **25 source-pinned candidates across 7 primary studies; all pending independent manual review**

## 2026-11-04 source-pin reconciliation

The registry was rebuilt from the current manifest-verified StageB V20 CSV (`5c095c6ee22d8d998888d3d47bc4ae2fcabf17faf4df0bee8aad7d6bb9af1cec`); source rows were not edited. The prior registry is preserved in [`the pre-rebind snapshot`](source_integrity_incident/stageb_v20_pre_rebind_snapshot/). The 25 selected records and pending review state are retained.

## Scope and counts

- Read the pinned Stage B release `StageB_V20_20261103/data/interaction_evidence.csv` without modifying it: **317 rows**.
- Before Cycle 5, the registry contained 12 records across 6 studies. Cycle 5 adds **13** source-checked Stage B rows, for **25 selected records** covering **7 primary studies**.
- Stage B CSV SHA-256: `5c095c6ee22d8d998888d3d47bc4ae2fcabf17faf4df0bee8aad7d6bb9af1cec`.
- The builder copies each complete CSV row without changing strings. Tests compare the exact row dictionaries, source-file digest, row count, PMID and DOI.
- Source status: **23 full-text or full-author-manuscript reviews; 2 primary-abstract-only reviews** (`SB-0043`, `SB-0044`). No source status or reviewer decision is inferred from another record.
- Candidate relations: **18 inhibition/reduced-activity candidates; 2 induction/increased-activity candidates; 5 unresolved transport/permeability candidates**. Induction records are author interpretations of human probe pharmacokinetics, not direct molecular induction assays.
- Candidate families: **16 membrane-transporter candidates; 4 drug-metabolizing-enzyme candidates; 5 metabolism/transport-unresolved permeability records**.
- Outcome-label grouping: **19 reported effects, 5 null/non-significant permeability observations, and 1 conflicting source-outcome label**. These are descriptive source labels, not evidence-quality grades or clinical directions.
- All 25 remain `pending_manual_review`; all acceptance values remain `pending`; identity adjudication remains `not_performed`. No expert approval is claimed.

## Selected records and primary-source checks

| Stage B record(s) | Primary source and access | Source-supported scope |
|---|---|---|
| `SB-0003` | [PMID 21870106, DOI 10.1007/s00228-011-1108-2, full text on PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC4898966/) | Midazolam is identified as the CYP3A4 probe; the primary paper reports a human probe-PK phenotype after berberine capsules. This is not a direct binding assay or food-dose equivalence. |
| `SB-0046`, `SB-0047`, `SB-0048` | [PMID 22300367, DOI 10.1111/j.1476-5381.2012.01887.x, full text on PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC3402804/) | `SB-0048`: concentration-dependent inhibition of ATP-dependent sulfasalazine uptake by hBCRP vesicles (Results and Fig. 1). `SB-0047`: curcumin increased oral sulfasalazine exposure in wild-type mice but had no significant effect in Bcrp-null mice (Results and Fig. 2), an animal absorption phenotype. `SB-0046`: the human microdose/therapeutic-dose source discrepancy is preserved and source-record adjudication remains pending independent review. |
| `SB-V17-001`–`SB-V17-004` | [PMID 37252098, DOI 10.1039/d3md00078h, full text on PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10211325/) | Results §§3.2–3.3, Fig. 4 and Table 1 report compound-specific IC50 values for apigetrin (10.5 ± 1.5 μM), myricitrin (46.2 ± 1.3 μM), prunin (101.0 ± 1.6 μM) and quercitrin (63.1 ± 1.3 μM) on OATP2B1-mediated DBF uptake. These are isolated in-vitro assay results, not clinical or dietary thresholds. |
| `SB-V17-007` | [PMID 34396892, DOI 10.1080/00498254.2021.1969480, full author manuscript](https://eprints.lib.hokudai.ac.jp/dspace/bitstream/2115/87010/1/Manuscript_Takahashi%20et%20al.pdf); [PubMed bibliographic record](https://pubmed.ncbi.nlm.nih.gov/34396892/) | Fig. 1 reports phloridzin IC50 110 μM on OATP2B1-mediated E3S uptake; Table 1 reports kinetic results at 100 μM consistent with competitive inhibition in this assay. The rat rosuvastatin arm used phloretin, not phloridzin. |
| `SB-0043`, `SB-0044` | [PMID 21943317, DOI 10.3109/00498254.2011.615954, primary PubMed abstract](https://pubmed.ncbi.nlm.nih.gov/21943317/) | Abstract interprets human midazolam probe changes as modest CYP3A induction and describes P-gp activity changes as possible based on talinolol probe PK. Both remain author-interpreted phenotypes; full text was not reviewed, especially the P-gp explanation. |
| `SB-V14-008` | [PMID 32571913, DOI 10.1073/pnas.1920483117, full text on PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7355017/) | The primary source reports an OATP2B1 screen of 136 excipients and validation of 24 hits (Fig. 1D–E; SI Appendix Table S1). Allura Red AC is included in the validated set. No untranscribed dose or Ki was added. Its distinct mouse fexofenadine experiment is not treated as a human dietary result. |
| `SB-0004`, `SB-0005` | [PMID 21870106, DOI 10.1007/s00228-011-1108-2, full text on PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC4898966/) | Added separate Stage B endpoints from the same 17-completer berberine probe study: dextromethorphan/dextrorphan urinary ratio (CYP2D6 phenotype) and losartan/E-3174 ratio. The CYP2C9-versus-CYP2C19 mapping disagreement for losartan is retained open; no canonical target is assigned. |
| `SB-V15-001`–`SB-V15-007` | [PMID 40773056, DOI 10.1021/acs.molpharmaceut.5c00705, full text on PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12406256/) | Adds six transporter-assay candidate records from a 2025 primary study: beta-carotene with BCRP, P-gp and OATP2B1; butylated hydroxytoluene with MRP2; dodecyl gallate with BCRP; and octyl gallate with OATP2B1. The latter remains a 65%-at-50-μM single-concentration finding with no IC50. Beta-carotene and dodecyl-gallate fluorescence-interference caveats are retained. |
| `SB-V15-004`, `SB-V15-008`–`SB-V15-011` | [PMID 40773056, DOI 10.1021/acs.molpharmaceut.5c00705, full text on PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12406256/) | Adds five separate Stage B rows for the same study's Caco-2 sulfasalazine permeability nulls. The article tested additives apically at 200 μM, except neohesperidin dihydrochalcone at 100 μM, with 500 μM sulfasalazine over 120 min. These integrated monolayer outcomes remain distinct from transporter inhibition and are not treated as human negative findings. |

## Classification boundaries

The controlled relations describe the candidate compound's reported effect on the named target. The records keep assay substrates and victim drugs separate: DBF, E3S and sulfasalazine are transporter assay substrates; midazolam and talinolol are human probes. They are not thereby classified as the Stage B candidate food compound.

Inhibition candidates include direct transporter assays (`SB-0048`, `SB-V17-001`–`SB-V17-004`, `SB-V17-007`, `SB-V14-008`, `SB-V15-001`–`SB-V15-003`, `SB-V15-005`–`SB-V15-007`) and human probe phenotypes (`SB-0003`–`SB-0005`, `SB-0046`). `SB-0047` remains a separate mouse genotype-supported oral-absorption phenotype. The two CYP induction records (`SB-0043`, `SB-0044`) preserve tentative author interpretation and are not direct induction experiments. Five `SB-V15` Caco-2 rows preserve null permeability outcomes under tested conditions; these do not negate their separate in-vitro transporter findings, establish a human null, or establish clinical safety. No pathway-specific causal relation is accepted. Every target identity, mechanism interpretation, food context, dose bridge, and clinical interpretation remains for independent review.

## PMID 22300367 source discrepancy preservation

The existing `SB-0046` source-extraction adjudication and original Stage B row were retained unchanged. Its registry discrepancy record preserves four locator-specific observations, including the conflicting Results assignment, the abstract/Table 1 assignment, the dose-ordered table means, the arithmetic check, rationale, and pending manual review. The reviewer packet requires confirmation of this conflict. The added `SB-0047` uses the same article's separate mouse genotype experiment and points reviewers back to the `SB-0046` conflict record; it does not repeat or overwrite the disputed human sentence.

The new `SB-0005` record keeps its separate berberine-paper conflict open: the Methods section labels losartan as a CYP2C19 probe while Abstract/Results/Table 1 identify a CYP2C9 phenotype. The target candidate lists both labels, and the record remains unapproved. The 2025 article also describes octyl gallate OATP2B1 inhibition as weak and notes prior disagreement; its Stage B row is preserved and no dose-response/IC50 is imputed.

## Independent reviewer packets

[The reviewer packet file](mechanism_reviewer_packets.md) provides one packet per record with primary-source access status, exact locators, evidence boundaries, and a record-specific review focus. Reviewer identity and disposition are blank/unassigned. Packets do not imply completed independent review, mechanism acceptance, compound-identity approval, or clinical relevance.

## Validation

Focused mechanism tests passed **13 tests, 0 failed, 0 skipped** with the pinned Draft 2020-12 dependency. They cover the 25-record exact-row registry, Stage B digest and row count, raw-row and PMID/DOI matching, primary-source access distinctions, pending review, mechanism families, separation of direct transporter assays from Caco-2 nulls, preservation of assay interference and no-IC50 caveats, both open source discrepancies, synthetic outcome classification, and reviewer-packet coverage. An initial focused run caught missing Cycle 5 reviewer-packet entries and an assertion phrase mismatch; the packet index/details and assertion were corrected, then the suite passed. The source label `observed_in_vitro_effect` maps to descriptive `reported_effect`; that mapping does not infer direction, quality, or clinical meaning.

## Limits and next action

- The registry is a bounded source-reviewed tranche, not an exhaustive Stage B mechanism census.
- Abstract-only records `SB-0043` and `SB-0044` need full-text review before any stronger CYP3A/P-gp interpretation.
- Independent review has not been performed. All records remain pending.
- Stage B and release artifacts were not edited. No food-dose equivalence, exposure calculation, clinical risk, or patient-level conclusion is produced.
