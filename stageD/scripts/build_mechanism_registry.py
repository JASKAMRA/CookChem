"""Build the bounded Stage D mechanism registry from a pinned Stage B release.

This script reads Stage B only. It never edits Stage B, performs no identity
resolution, and copies the selected CSV rows without altering their strings.
The manually reviewed source metadata below is limited to bibliographic and
source-locator facts; scientific acceptance remains pending.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "stageD" / "src"))
from stage_d.mechanisms import classify_source_outcome  # noqa: E402

RELEASE_ID = "StageB_V20_20261103"
SOURCE_RELATIVE = Path("stageB/release") / RELEASE_ID / "data/interaction_evidence.csv"
OUTPUT = ROOT / "stageD/data/mechanism_evidence_registry.json"
SOURCE_METADATA = {
    "SB-0003": {
        "candidate_family": "drug_metabolizing_enzyme",
        "source_reported_target": "CYP3A4 (midazolam probe enzyme)",
        "source_reported_relation": "inhibition_or_reduced_activity",
        "classification_basis": "Stage B names reduced CYP activity. The primary full text identifies midazolam as the CYP3A4 probe and reports CYP3A4 activity changes by probe pharmacokinetics. This is a human probe phenotype, not a binding assay.",
        "access_level": "primary_article_full_text_reviewed",
        "verified_source_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC4898966/",
        "pmid": "21870106",
        "doi": "10.1007/s00228-011-1108-2",
        "pmcid": "PMC4898966",
        "source_locator": "Abstract Results and Conclusions; Methods (probe-drug mapping); Results, Table 1 and footnotes.",
        "verification_note": "The primary article states that 17 healthy Chinese male volunteers completed a 14-day, 300 mg three-times-daily berberine capsule regimen; midazolam is the CYP3A4 probe. It reports increased midazolam exposure and reduced apparent oral clearance. The underlying Stage B quantitative_outcome and limitations are retained verbatim; no food-dose equivalence or clinical risk conclusion is added.",
    },
    "SB-0046": {
        "candidate_family": "membrane_transporter",
        "source_reported_target": "BCRP",
        "source_reported_relation": "inhibition_or_reduced_activity",
        "classification_basis": "Stage B explicitly reports intestinal BCRP inhibition supported by parallel experiments. The primary article describes the hBCRP vesicle assay and human sulfasalazine pharmacokinetic arm. Human mechanism attribution remains an author interpretation; a source-level dose-assignment discrepancy is separately documented and adjudicated without altering Stage B.",
        "access_level": "primary_article_full_text_reviewed",
        "verified_source_url": "https://bpspubs.onlinelibrary.wiley.com/doi/10.1111/j.1476-5381.2012.01887.x",
        "pmid": "22300367",
        "doi": "10.1111/j.1476-5381.2012.01887.x",
        "pmcid": "PMC3402804",
        "source_locator": "Primary full text: Abstract, Key Results; Results, human microdose/therapeutic-dose section; Table 1, dose-normalized AUC0-24 entries.",
        "verification_note": "The Wiley primary full text and PubMed bibliographic record agree on PMID, DOI, title, authors, and PMCID. The abstract, dose-ordered Table 1 values, the next Results sentence, and the Discussion support the abstract's dose assignment; one Results sentence reverses the labels. Stage D records this as a source-record-level transcription adjudication, retains the conflicting prose verbatim, and keeps independent manual confirmation pending. The original Stage B outcome and Notes are copied exactly.",
        "source_discrepancies": [
            {
                "code": "primary_source_endpoint_text_conflict",
                "status": "resolved_source_record_level",
                "observations": [
                    {"locator": "Abstract, Key Results", "summary": "Verbatim fragment: ‘2.0-fold at microdoses and 3.2-fold at therapeutic doses’."},
                    {"locator": "Results, human microdose and therapeutic-dose section", "summary": "Verbatim fragment: ‘3.2- and 1.8-fold larger in curcumin-treated groups at the microdose and therapeutic dose’."},
                    {"locator": "Table 1, AUC0-24/Dose column (×10−5 mL−1·hr), microdose then therapeutic dose", "summary": "Verbatim control;curcumin means: microdose 43.5 ± 5.3; 79.4 ± 6.8. Therapeutic dose 5.89 ± 0.71; 19.0 ± 2.7. Footnote: each value is mean ± SE."},
                    {"locator": "Results, paragraph immediately after the conflicting fold-change sentence; Discussion, microdose-versus-therapeutic-dose interpretation", "summary": "Both following narrative statements describe a stronger BCRP-inhibition effect at the therapeutic dose than at the microdose."}
                ],
                "resolution": {
                    "decision": "source_record_level_assignment",
                    "selected_assignment": "For Stage D extraction, retain the abstract's assignment (microdose 2.0-fold; therapeutic dose 3.2-fold). Table 1 reports AUC0-24/Dose means of 43.5 and 79.4 for microdose control/curcumin, and 5.89 and 19.0 for therapeutic-dose control/curcumin (each mean ± SE); transparent arithmetic ratios of those displayed means are 79.4/43.5 ≈ 1.83 and 19.0/5.89 ≈ 3.23. These are arithmetic checks of table means, not replacements for the paper's reported paired estimates.",
                    "conflicting_assignment": "The exact conflicting Results fragment is preserved in the Results observation above; no second copy is stored.",
                    "rationale": "The Table 1 dose-normalized mean pairs and their transparent ratio check support the abstract's assignment. The sentence immediately following the conflicting Results sentence and the Discussion both state that the therapeutic-dose effect is stronger than the microdose effect. The Results sentence is therefore treated as a likely dose-label transposition for Stage D extraction only; the original conflicting source text and Stage B row are not edited.",
                    "manual_review_status": "pending_manual_review",
                    "scope": "Source-record transcription adjudication only; identity, mechanism acceptance, clinical meaning, and exposure relevance remain unassessed."
                }
            }
        ],
    },
    "SB-0048": {
        "candidate_family": "membrane_transporter",
        "source_reported_target": "hBCRP",
        "source_reported_relation": "inhibition_or_reduced_activity",
        "classification_basis": "Stage B labels this an in-vitro BCRP inhibition result. The primary article full text reports concentration-dependent inhibition of ATP-dependent sulfasalazine uptake by hBCRP membrane vesicles and an inhibition constant.",
        "access_level": "primary_article_full_text_reviewed",
        "verified_source_url": "https://bpspubs.onlinelibrary.wiley.com/doi/10.1111/j.1476-5381.2012.01887.x",
        "pmid": "22300367",
        "doi": "10.1111/j.1476-5381.2012.01887.x",
        "pmcid": "PMC3402804",
        "source_locator": "Primary full text: Results, Effect of curcumin on ATP-dependent uptake of sulphasalazine by hBCRP; Figure 1.",
        "verification_note": "The primary article reports concentration-dependent inhibition of ATP-dependent uptake by hBCRP membrane vesicles. The reported Ki is retained only in the verbatim Stage B field; this in-vitro assay does not establish a dietary exposure threshold or clinical effect.",
        "source_discrepancies": [],
    },
    # Four separate compound records from one primary, full-text flavonoid
    # uptake study. Stage B rows remain the source of the verbatim values.
    "SB-V17-001": {
        "candidate_family": "membrane_transporter",
        "source_reported_target": "Human OATP2B1-mediated DBF uptake",
        "source_reported_relation": "inhibition_or_reduced_activity",
        "classification_basis": "The primary full text reports an apigetrin IC50 for inhibition of OATP2B1-mediated DBF uptake (Results §§3.2–3.3, Fig. 4, Table 1). This is an in-vitro uptake inhibition result, not a binding assay, food-dose equivalence, or clinical interaction.",
        "access_level": "primary_article_full_text_reviewed",
        "verified_source_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC10211325/",
        "pmid": "37252098",
        "doi": "10.1039/d3md00078h",
        "pmcid": "PMC10211325",
        "source_locator": "Primary full text: Results §§3.2–3.3; Fig. 4; Table 1, Apigetrin row.",
        "verification_note": "The primary paper and PubMed record agree on title, authors, PMID, PMCID, and DOI. Table 1 reports apigetrin IC50 10.5 ± 1.5 μM for OATP2B1-mediated DBF uptake. Fig. 4 describes the DBF uptake screen using CHO-WT and CHO-OATP2B1 cells, 5 μM DBF, 37 °C, 2 min, with 10 and 100 μM test conditions. Stage B's row, units, and uncertainty notation are copied unchanged. The assay does not establish binding, dietary exposure equivalence, or clinical effect.",
    },
    "SB-V17-002": {
        "candidate_family": "membrane_transporter",
        "source_reported_target": "Human OATP2B1-mediated DBF uptake",
        "source_reported_relation": "inhibition_or_reduced_activity",
        "classification_basis": "The primary full text reports a myricitrin IC50 for inhibition of OATP2B1-mediated DBF uptake (Results §§3.2–3.3, Fig. 4, Table 1). This is an in-vitro uptake inhibition result, not a binding assay, food-dose equivalence, or clinical interaction.",
        "access_level": "primary_article_full_text_reviewed",
        "verified_source_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC10211325/",
        "pmid": "37252098",
        "doi": "10.1039/d3md00078h",
        "pmcid": "PMC10211325",
        "source_locator": "Primary full text: Results §§3.2–3.3; Fig. 4; Table 1, Myricitrin row.",
        "verification_note": "The primary paper and PubMed record agree on title, authors, PMID, PMCID, and DOI. Table 1 reports myricitrin IC50 46.2 ± 1.3 μM for OATP2B1-mediated DBF uptake. Fig. 4 describes the DBF uptake screen using CHO-WT and CHO-OATP2B1 cells, 5 μM DBF, 37 °C, 2 min, with 10 and 100 μM test conditions. Stage B's row, units, and uncertainty notation are copied unchanged. The assay does not establish binding, dietary exposure equivalence, or clinical effect.",
    },
    "SB-V17-003": {
        "candidate_family": "membrane_transporter",
        "source_reported_target": "Human OATP2B1-mediated DBF uptake",
        "source_reported_relation": "inhibition_or_reduced_activity",
        "classification_basis": "The primary full text reports a prunin IC50 for inhibition of OATP2B1-mediated DBF uptake (Results §§3.2–3.3, Fig. 4, Table 1). This is an in-vitro uptake inhibition result, not a binding assay, food-dose equivalence, or clinical interaction.",
        "access_level": "primary_article_full_text_reviewed",
        "verified_source_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC10211325/",
        "pmid": "37252098",
        "doi": "10.1039/d3md00078h",
        "pmcid": "PMC10211325",
        "source_locator": "Primary full text: Results §§3.2–3.3; Fig. 4; Table 1, Prunin row.",
        "verification_note": "The primary paper and PubMed record agree on title, authors, PMID, PMCID, and DOI. Table 1 reports prunin IC50 101.0 ± 1.6 μM for OATP2B1-mediated DBF uptake. Fig. 4 describes the DBF uptake screen using CHO-WT and CHO-OATP2B1 cells, 5 μM DBF, 37 °C, 2 min, with 10 and 100 μM test conditions. Stage B's row, units, and uncertainty notation are copied unchanged. The assay does not establish binding, dietary exposure equivalence, or clinical effect.",
    },
    "SB-V17-004": {
        "candidate_family": "membrane_transporter",
        "source_reported_target": "Human OATP2B1-mediated DBF uptake",
        "source_reported_relation": "inhibition_or_reduced_activity",
        "classification_basis": "The primary full text reports a quercitrin IC50 for inhibition of OATP2B1-mediated DBF uptake (Results §§3.2–3.3, Fig. 4, Table 1). This is an in-vitro uptake inhibition result, not a binding assay, food-dose equivalence, or clinical interaction.",
        "access_level": "primary_article_full_text_reviewed",
        "verified_source_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC10211325/",
        "pmid": "37252098",
        "doi": "10.1039/d3md00078h",
        "pmcid": "PMC10211325",
        "source_locator": "Primary full text: Results §§3.2–3.3; Fig. 4; Table 1, Quercitrin row.",
        "verification_note": "The primary paper and PubMed record agree on title, authors, PMID, PMCID, and DOI. Table 1 reports quercitrin IC50 63.1 ± 1.3 μM for OATP2B1-mediated DBF uptake. Fig. 4 describes the DBF uptake screen using CHO-WT and CHO-OATP2B1 cells, 5 μM DBF, 37 °C, 2 min, with 10 and 100 μM test conditions. Stage B's row, units, and uncertainty notation are copied unchanged. The assay does not establish binding, dietary exposure equivalence, or clinical effect.",
    },
    "SB-V17-007": {
        "candidate_family": "membrane_transporter",
        "source_reported_target": "Human OATP2B1-mediated estrone-3-sulfate (E3S) uptake",
        "source_reported_relation": "inhibition_or_reduced_activity",
        "classification_basis": "The primary author manuscript reports concentration-dependent phloridzin inhibition of OATP2B1-mediated E3S uptake and kinetic results consistent with competitive inhibition in that assay (Results, ‘Effect of coincubation’; Fig. 1; Table 1). No clinical phloridzin interaction is inferred.",
        "access_level": "primary_article_full_text_reviewed",
        "verified_source_url": "https://eprints.lib.hokudai.ac.jp/dspace/bitstream/2115/87010/1/Manuscript_Takahashi%20et%20al.pdf",
        "pmid": "34396892",
        "doi": "10.1080/00498254.2021.1969480",
        "pmcid": None,
        "source_locator": "Primary author manuscript: Methods, HEK293 uptake; Results, ‘Effect of coincubation’; Fig. 1 and Table 1.",
        "verification_note": "The primary author manuscript and PubMed bibliographic record agree on title, authors, PMID, and DOI. Fig. 1 reports phloridzin IC50 110 μM for OATP2B1-mediated E3S uptake; Table 1 reports the kinetic comparison at 100 μM, where Km increased while Vmax was not changed, consistent with competitive inhibition in this assay. The assay used HEK293 cells expressing OATP2B1 and mock controls. The paper's rat rosuvastatin experiment used phloretin; no in-vivo phloridzin effect is attributed here. Stage B's quantitative outcome remains verbatim.",
    },
    "SB-0043": {
        "candidate_family": "drug_metabolizing_enzyme",
        "source_reported_target": "CYP3A activity assessed with midazolam probe pharmacokinetics",
        "source_reported_relation": "induction_or_increased_activity",
        "classification_basis": "The primary abstract describes a randomized two-phase crossover in 18 healthy men and interprets reduced midazolam exposure after 14 days of genistein as modest CYP3A induction. This is an author-reported human probe phenotype, not direct CYP3A expression or enzyme-activity measurement; causal attribution remains pending.",
        "access_level": "primary_article_abstract_reviewed",
        "verified_source_url": "https://pubmed.ncbi.nlm.nih.gov/21943317/",
        "pmid": "21943317",
        "doi": "10.3109/00498254.2011.615954",
        "pmcid": None,
        "source_locator": "Primary abstract: Methods and Results; conclusion on CYP3A probe activity.",
        "verification_note": "PubMed's primary article abstract supports the title, authors, PMID, DOI, study design and reported midazolam exposure changes. The abstract concludes genistein can result in modest CYP3A induction in healthy volunteers. Full text and detailed study tables were not reviewed in this tranche. The clearance units in the abstract are not used because Stage B records the reporting inconsistency; no clearance value is added or recalculated. This remains a pending human probe-phenotype candidate, not proof of molecular induction or food-dose relevance.",
    },
    "SB-0044": {
        "candidate_family": "membrane_transporter",
        "source_reported_target": "P-glycoprotein (P-gp) activity assessed with talinolol probe pharmacokinetics",
        "source_reported_relation": "induction_or_increased_activity",
        "classification_basis": "The primary abstract reports lower talinolol exposure after 14 days of genistein and describes possible P-gp activity induction. It is an author-proposed interpretation of oral probe pharmacokinetics, not a direct P-gp transport, expression, or induction assay. Absorption and other pharmacokinetic explanations are not resolved.",
        "access_level": "primary_article_abstract_reviewed",
        "verified_source_url": "https://pubmed.ncbi.nlm.nih.gov/21943317/",
        "pmid": "21943317",
        "doi": "10.3109/00498254.2011.615954",
        "pmcid": None,
        "source_locator": "Primary abstract: Methods and Results; concluding author interpretation of possible P-gp activity.",
        "verification_note": "PubMed's primary article abstract supports the title, authors, PMID, DOI, study design and reported talinolol exposure changes. It characterizes P-gp activity induction as possible, not established. Full text and detailed study tables were not reviewed in this tranche. Stage B's raw outcome, direction, and reported values remain unchanged. Mechanism, target identity, intestinal absorption contribution, and dietary relevance remain open.",
    },
    "SB-V14-008": {
        "candidate_family": "membrane_transporter",
        "source_reported_target": "Human OATP2B1-mediated DBF uptake",
        "source_reported_relation": "inhibition_or_reduced_activity",
        "classification_basis": "The primary full text identifies Allura Red AC (FD&C Red No. 40) among 24 validated OATP2B1 inhibitors from a 136-excipient screen (Fig. 1D–E, Results). The Stage B row's direction string ‘inhibition of enzyme activity in vitro’ is preserved exactly as raw provenance; this candidate is classified from the named transporter assay context, not as an enzyme effect. No untranscribed dose or Ki is added.",
        "access_level": "primary_article_full_text_reviewed",
        "verified_source_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC7355017/",
        "pmid": "32571913",
        "doi": "10.1073/pnas.1920483117",
        "pmcid": "PMC7355017",
        "source_locator": "Primary full text: Results, ‘Multiple oral excipients inhibit OATP2B1-mediated transport’; Fig. 1D–E; SI Appendix Table S1 (validated inhibitor set).",
        "verification_note": "The primary full text reports a screen of 136 oral excipients and dose-response validation of 24 hits; Allura Red AC is in the validated set. Article Fig. 1D–E and SI Appendix Table S1 are the source locators. No compound-specific Ki or dose is entered because the Stage B row did not transcribe one and this record does not require a quantitative claim. The separate mouse fexofenadine experiment concerns FD&C Red No. 40 and is not attributed to an Allura Red dietary serving or human effect. Stage B's raw row is unchanged.",
    },
    "SB-0047": {
        "candidate_family": "membrane_transporter",
        "source_reported_target": "BCRP (ABCG2)-dependent sulfasalazine oral absorption in mice",
        "source_reported_relation": "inhibition_or_reduced_activity",
        "classification_basis": "The primary full text reports curcumin-associated increases in oral sulfasalazine exposure in wild-type mice that were not significant in Bcrp-null mice and attributes most of the effect to BCRP inhibition. This is an in-vivo genotype-supported transporter/absorption phenotype; it is not a dietary-dose or human effect estimate. The same paper's human dose-assignment text discrepancy is separately preserved in SB-0046, with independent review pending.",
        "access_level": "primary_article_full_text_reviewed",
        "verified_source_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC3402804/",
        "pmid": "22300367",
        "doi": "10.1111/j.1476-5381.2012.01887.x",
        "pmcid": "PMC3402804",
        "source_locator": "Primary full text: Results, ‘Effect of curcumin on the plasma concentrations of sulphasalazine in wild-type and Bcrp(–/–) mice’; Fig. 2; Discussion, attribution to Bcrp inhibition.",
        "verification_note": "The primary full text supports the Stage B description of a mouse wild-type versus Bcrp-knockout oral PK comparison, curcumin pretreatment, increased sulfasalazine exposure in wild-type mice, and no statistically significant effect in knockout mice. Stage B's approximately eightfold outcome is retained exactly; the full text reports 8.5-fold at 300 mg/kg and 8.0-fold at 400 mg/kg. This is an animal absorption phenotype with genotype support, not a dietary equivalence claim. The paper's separate human dose-assignment conflict remains preserved in SB-0046 and is awaiting independent review.",
    },
}

# Cycle 5 additions are source-pinned to exact Stage B rows. The 2025 study's
# direct transporter assays and its separate Caco-2 permeability observations
# are kept as distinct records so an in-vitro inhibition result is not treated
# as evidence of increased transcellular drug permeability.
_BERBERINE_STUDY = {
    "access_level": "primary_article_full_text_reviewed",
    "verified_source_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC4898966/",
    "pmid": "21870106",
    "doi": "10.1007/s00228-011-1108-2",
    "pmcid": "PMC4898966",
}
SOURCE_METADATA.update({
    "SB-0004": {
        "candidate_family": "drug_metabolizing_enzyme",
        "source_reported_target": "CYP2D6 (dextromethorphan/dextrorphan urinary probe ratio)",
        "source_reported_relation": "inhibition_or_reduced_activity",
        "classification_basis": "The primary human study reports a ninefold increase in the 0–8 h urinary dextromethorphan/dextrorphan ratio after repeated berberine and interprets it as reduced CYP2D6 activity. This is a probe phenotype, not a direct enzyme assay; the ratio is not dextromethorphan AUC or a clinical outcome.",
        **_BERBERINE_STUDY,
        "source_locator": "Primary full text: Abstract Results; Methods, probe-drug mapping and urine collection; Results and Table 1, dextromethorphan (CYP2D6) row and footnotes.",
        "verification_note": "The full text identifies dextromethorphan as the CYP2D6 probe and reports the 0–8 h urinary parent/metabolite ratio for 17 completers after 14 days of berberine 300 mg three times daily. The original Stage B row, numeric string, and limitations are copied unchanged. Probe phenotype only; dietary exposure, direct binding, and clinical consequences are not inferred.",
    },
    "SB-0005": {
        "candidate_family": "drug_metabolizing_enzyme",
        "source_reported_target": "CYP2C9 in Abstract/Results/Table 1; CYP2C19 in Methods probe list (unresolved source discrepancy)",
        "source_reported_relation": "inhibition_or_reduced_activity",
        "classification_basis": "The primary article's Abstract, Results, and Table 1 label the losartan/E-3174 urinary ratio as a CYP2C9 phenotype, while the Methods probe list labels losartan CYP2C19. The target attribution is deliberately left unresolved; the Stage B row already flags this conflict.",
        **_BERBERINE_STUDY,
        "source_locator": "Primary full text: Methods, probe-drug mapping; Abstract Results; Results and Table 1, losartan/E-3174 row and footnotes; Discussion.",
        "verification_note": "The article and Stage B row identifiers match. The Results and Table 1 describe the losartan/E-3174 ratio as CYP2C9, but the Methods list says CYP2C19; Stage B Notes preserves this discrepancy and it remains open for independent adjudication. No canonical target is assigned. The source row and reported ratio are copied unchanged.",
    },
})

_FOOD_ADDITIVE_STUDY = {
    "access_level": "primary_article_full_text_reviewed",
    "verified_source_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12406256/",
    "pmid": "40773056",
    "doi": "10.1021/acs.molpharmaceut.5c00705",
    "pmcid": "PMC12406256",
}
SOURCE_METADATA.update({
    "SB-V15-001": {
        "candidate_family": "membrane_transporter",
        "source_reported_target": "BCRP/ABCG2 ATP-dependent vesicular transport of Lucifer yellow",
        "source_reported_relation": "inhibition_or_reduced_activity",
        "classification_basis": "The primary study reports a beta-carotene dose-response for BCRP vesicular transport inhibition, Table 2 IC50 12.1 μM (95% CI 9.9–15.5). Lucifer yellow was the substrate. The article also reports beta-carotene fluorescence quenching; this assay limitation is retained and requires reviewer assessment.",
        **_FOOD_ADDITIVE_STUDY,
        "source_locator": "Primary full text: Results §3.1; Figure 1 and Figure 2 captions (BCRP vesicle assay, Lucifer yellow 50 μM); Table 2, beta-carotene/BCRP row; Supporting Information Figure S1 (fluorescence interference).",
        "verification_note": "The 2025 primary article reports BCRP vesicular transport inhibition with beta-carotene and IC50 12.1 μM (95% CI 9.9–15.5). Figure 2 dose-response data are means of three independent experiments, each in triplicate wells. The article notes >20% fluorescence interference at the highest possible concentration and up to about 30% quenching for Lucifer yellow at lower concentrations. No exposure or clinical inference is added.",
    },
    "SB-V15-002": {
        "candidate_family": "membrane_transporter",
        "source_reported_target": "P-glycoprotein/ABCB1 vesicular transport of N-methyl-quinidine",
        "source_reported_relation": "inhibition_or_reduced_activity",
        "classification_basis": "The primary study reports beta-carotene dose-response inhibition of P-gp-mediated vesicular transport; Table 2 IC50 3.2 μM (95% CI 2.4–4.3). N-methyl-quinidine was the substrate. The article reports fluorescence-interference checks, which remain a review consideration.",
        **_FOOD_ADDITIVE_STUDY,
        "source_locator": "Primary full text: Results §3.1; Figure 1 and Figure 2 captions (P-gp vesicle assay, N-methyl-quinidine 2 μM); Table 2, beta-carotene/P-gp row; Supporting Information Figure S1.",
        "verification_note": "The primary article reports P-gp vesicular transport inhibition with beta-carotene and IC50 3.2 μM (95% CI 2.4–4.3). Figure 2 data are means of three independent experiments, each in triplicate wells. The study checked beta-carotene fluorescence interference; interpretation remains pending reviewer assessment. No dietary dose or clinical interaction is inferred.",
    },
    "SB-V15-003": {
        "candidate_family": "membrane_transporter",
        "source_reported_target": "OATP2B1-mediated 5-carboxyfluorescein uptake in HEK293 cells",
        "source_reported_relation": "inhibition_or_reduced_activity",
        "classification_basis": "The primary study reports beta-carotene dose-response inhibition of OATP2B1-mediated uptake in HEK293 cells; Table 2 IC50 27.5 μM (95% CI 22.6–35.6). 5-carboxyfluorescein was the substrate. The article notes fluorescence quenching, so this assay caveat remains visible.",
        **_FOOD_ADDITIVE_STUDY,
        "source_locator": "Primary full text: Results §3.1; Figure 1 and Figure 2 captions (HEK293 OATP2B1 uptake assay, 5-carboxyfluorescein 2 μM); Table 2, beta-carotene/OATP2B1 row; Supporting Information Figure S1.",
        "verification_note": "The primary article reports OATP2B1 uptake inhibition with beta-carotene and IC50 27.5 μM (95% CI 22.6–35.6). Figure 2 data are means of three independent experiments, each in triplicate wells. Beta-carotene partially quenched fluorescence; the source's caveat is preserved. This cell assay does not establish food exposure equivalence or clinical effect.",
    },
    "SB-V15-004": {
        "candidate_family": "metabolism_or_transport_unresolved",
        "source_reported_target": "Caco-2 apical-to-basolateral sulfasalazine permeability; no single transporter attribution",
        "source_reported_relation": "unresolved_or_mixed",
        "classification_basis": "This is the study's separate transcellular permeability endpoint, not a direct transporter inhibition assay. The primary article reports no detectable change in sulfasalazine permeability under tested Caco-2 conditions; it is preserved as a null result without inferring a clinical negative.",
        **_FOOD_ADDITIVE_STUDY,
        "source_locator": "Primary full text: Methods, Caco-2 permeability assay; Results §3.2; Figure 3 caption, beta-carotene row and apical-to-basolateral direction.",
        "verification_note": "The primary study tested beta-carotene at 200 μM with sulfasalazine 500 μM added apically to Caco-2 Transwell monolayers and measured apical-to-basolateral apparent permeability over 120 min. The article reports no effect on sulfasalazine permeability; Figure 3 shows triplicate wells from a representative study. This null in-vitro endpoint is distinct from transporter-assay inhibition and is not a human or clinical null finding.",
    },
    "SB-V15-005": {
        "candidate_family": "membrane_transporter",
        "source_reported_target": "MRP2/ABCC2 vesicular transport of 5(6)-carboxy-2,7-dichlorofluorescein",
        "source_reported_relation": "inhibition_or_reduced_activity",
        "classification_basis": "The primary study reports butylated hydroxytoluene inhibition in the MRP2 vesicular assay; Table 2 IC50 49.0 μM (95% CI 43.1–55.4), with 5 μM fluorescent substrate. This is an in-vitro transporter result, not an intestinal or clinical exposure estimate.",
        **_FOOD_ADDITIVE_STUDY,
        "source_locator": "Primary full text: Results §3.1; Figure 1 and Figure 2 captions (MRP2 vesicle assay, 5 μM substrate); Table 2, butylated hydroxytoluene/MRP2 row.",
        "verification_note": "The primary article reports MRP2 vesicular transport inhibition with butylated hydroxytoluene and IC50 49.0 μM (95% CI 43.1–55.4). Figure 2 dose-response data are means of three independent experiments, each in triplicate wells. The raw Stage B outcome is retained unchanged; no food-serving concentration or clinical interaction is inferred.",
    },
    "SB-V15-006": {
        "candidate_family": "membrane_transporter",
        "source_reported_target": "BCRP/ABCG2 ATP-dependent vesicular transport of Lucifer yellow",
        "source_reported_relation": "inhibition_or_reduced_activity",
        "classification_basis": "The primary study reports dodecyl-gallate dose-response inhibition of BCRP vesicular transport; Table 2 IC50 22.5 μM (95% CI 16.4–31.2). The article notes Lucifer-yellow fluorescence quenching at the highest concentration, which requires reviewer consideration.",
        **_FOOD_ADDITIVE_STUDY,
        "source_locator": "Primary full text: Results §3.1; Figure 1 and Figure 2 captions (BCRP vesicle assay, Lucifer yellow 50 μM); Table 2, dodecyl gallate/BCRP row; Supporting Information Figure S1.",
        "verification_note": "The primary article reports BCRP vesicular transport inhibition with dodecyl gallate and IC50 22.5 μM (95% CI 16.4–31.2). Figure 2 data are means of three independent experiments, each in triplicate wells. The source reports ≥20% Lucifer-yellow fluorescence quenching at the highest tested concentration; no correction or causal conclusion is imposed here.",
    },
    "SB-V15-007": {
        "candidate_family": "membrane_transporter",
        "source_reported_target": "OATP2B1-mediated 5-carboxyfluorescein uptake in HEK293 cells",
        "source_reported_relation": "inhibition_or_reduced_activity",
        "classification_basis": "The primary article reports only 65% inhibition by octyl gallate at 50 μM in the single-concentration OATP2B1 screen and did not perform a dose-response/IC50 for this effect. Its discussion describes the result as relatively weak and mentions contradictory earlier findings; this candidate remains pending review.",
        **_FOOD_ADDITIVE_STUDY,
        "source_locator": "Primary full text: Results §3.1, Figure 1 and caption (50 μM screen); Discussion, octyl-gallate transporter findings; Table 2 marks OATP2B1 as ND for an IC50.",
        "verification_note": "The primary article reports 65% OATP2B1 inhibition at 50 μM octyl gallate, but no dose-response or IC50 was assigned; Table 2 marks that cell ND. The authors call the inhibition relatively weak and discuss disagreement with previous transporter findings. Those differences are not resolved in this candidate; Stage B text remains verbatim and independent review is pending.",
    },
    "SB-V15-008": {
        "candidate_family": "metabolism_or_transport_unresolved",
        "source_reported_target": "Caco-2 apical-to-basolateral sulfasalazine permeability; no single transporter attribution",
        "source_reported_relation": "unresolved_or_mixed",
        "classification_basis": "This is the study's separate transcellular permeability endpoint, not a direct transporter inhibition assay. The primary article reports no detectable change in sulfasalazine permeability under tested conditions; this is recorded as a condition-limited null and no clinical negative is inferred.",
        **_FOOD_ADDITIVE_STUDY,
        "source_locator": "Primary full text: Methods, Caco-2 permeability assay; Results §3.2; Figure 3 caption, brilliant blue FCF row and apical-to-basolateral direction.",
        "verification_note": "The primary study tested brilliant blue FCF at 200 μM with sulfasalazine 500 μM added apically to Caco-2 Transwell monolayers and measured apical-to-basolateral apparent permeability over 120 min. No effect was reported; Figure 3 presents triplicate wells from a representative study. This is an in-vitro permeability null only, not a negative human interaction finding.",
    },
    "SB-V15-009": {
        "candidate_family": "metabolism_or_transport_unresolved",
        "source_reported_target": "Caco-2 apical-to-basolateral sulfasalazine permeability; no single transporter attribution",
        "source_reported_relation": "unresolved_or_mixed",
        "classification_basis": "This is the study's separate transcellular permeability endpoint, not a direct transporter inhibition assay. The primary article reports no detectable change in sulfasalazine permeability under tested conditions; this is recorded as a condition-limited null and no clinical negative is inferred.",
        **_FOOD_ADDITIVE_STUDY,
        "source_locator": "Primary full text: Methods, Caco-2 permeability assay; Results §3.2; Figure 3 caption, carmoisine row and apical-to-basolateral direction.",
        "verification_note": "The primary study tested carmoisine at 200 μM with sulfasalazine 500 μM added apically to Caco-2 Transwell monolayers and measured apical-to-basolateral apparent permeability over 120 min. No effect was reported; Figure 3 presents triplicate wells from a representative study. This is an in-vitro permeability null only, not a negative human interaction finding.",
    },
    "SB-V15-010": {
        "candidate_family": "metabolism_or_transport_unresolved",
        "source_reported_target": "Caco-2 apical-to-basolateral sulfasalazine permeability; no single transporter attribution",
        "source_reported_relation": "unresolved_or_mixed",
        "classification_basis": "This is the study's separate transcellular permeability endpoint, not a direct transporter inhibition assay. The primary article reports no detectable change in sulfasalazine permeability under tested conditions; this is recorded as a condition-limited null and no clinical negative is inferred.",
        **_FOOD_ADDITIVE_STUDY,
        "source_locator": "Primary full text: Methods, Caco-2 permeability assay; Results §3.2; Figure 3 caption, neohesperidin dihydrochalcone row and apical-to-basolateral direction.",
        "verification_note": "The primary study tested neohesperidin dihydrochalcone at 100 μM (the exception to the 200 μM additive concentration) with sulfasalazine 500 μM added apically to Caco-2 Transwell monolayers and measured apical-to-basolateral apparent permeability over 120 min. No effect was reported; Figure 3 presents triplicate wells from a representative study. This is an in-vitro permeability null only, not a negative human interaction finding.",
    },
    "SB-V15-011": {
        "candidate_family": "metabolism_or_transport_unresolved",
        "source_reported_target": "Caco-2 apical-to-basolateral sulfasalazine permeability; no single transporter attribution",
        "source_reported_relation": "unresolved_or_mixed",
        "classification_basis": "This is the study's separate transcellular permeability endpoint, not a direct transporter inhibition assay. The primary article reports no detectable change in sulfasalazine permeability under tested conditions; this is recorded as a condition-limited null and no clinical negative is inferred.",
        **_FOOD_ADDITIVE_STUDY,
        "source_locator": "Primary full text: Methods, Caco-2 permeability assay; Results §3.2; Figure 3 caption, tartrazine row and apical-to-basolateral direction.",
        "verification_note": "The primary study tested tartrazine at 200 μM with sulfasalazine 500 μM added apically to Caco-2 Transwell monolayers and measured apical-to-basolateral apparent permeability over 120 min. No effect was reported; Figure 3 presents triplicate wells from a representative study. This is an in-vitro permeability null only, not a negative human interaction finding.",
    },
})
REASON_BY_CRITERION = {
    "primary_source_match": ("meets", "primary_source_page_checked"),
    "record_to_source_match": ("meets", "release_record_identifiers_match_article"),
    "compound_identity": ("not_assessed", "compound_identity_not_adjudicated"),
    "target_identity": ("not_assessed", "target_mapping_not_adjudicated"),
    "assay_context": ("not_assessed", "assay_model_requires_human_review"),
    "study_design_and_confounding": ("not_assessed", "study_design_and_population_require_review"),
    "independent_replication": ("not_assessed", "independent_replication_not_assessed"),
    "food_context": ("not_assessed", "food_preparation_not_studied"),
    "human_exposure_relevance": ("not_assessed", "food_exposure_bridge_not_established"),
    "clinical_interpretation": ("not_assessed", "clinical_interpretation_not_performed"),
}


def _criteria(evidence_id: str) -> dict[str, dict[str, object]]:
    criteria = {name: {"state": state, "reason_codes": [reason]} for name, (state, reason) in REASON_BY_CRITERION.items()}
    direct_transport_assays = {"SB-0048", "SB-V17-001", "SB-V17-002", "SB-V17-003", "SB-V17-004", "SB-V17-007", "SB-V14-008", "SB-V15-001", "SB-V15-002", "SB-V15-003", "SB-V15-005", "SB-V15-006", "SB-V15-007"}
    directness_reason = (
        "probe_phenotype_not_direct_binding_assay" if evidence_id == "SB-0003"
        else "direct_transport_assay_still_requires_review" if evidence_id in direct_transport_assays
        else "mechanistic_causality_not_adjudicated"
    )
    criteria["mechanistic_directness"] = {"state": "not_assessed", "reason_codes": [directness_reason]}
    if evidence_id == "SB-0046":
        criteria["endpoint_reconciliation"] = {
            "state": "meets",
            "reason_codes": ["source_table_abstract_discussion_corroboration"],
        }
    else:
        criteria["endpoint_reconciliation"] = {"state": "not_assessed", "reason_codes": ["endpoint_semantics_not_adjudicated"]}
    return criteria


def build() -> dict[str, object]:
    source_path = ROOT / SOURCE_RELATIVE
    source_bytes = source_path.read_bytes()
    rows = list(csv.DictReader(io.StringIO(source_bytes.decode("utf-8-sig"), newline="")))
    by_id = {row["Evidence_ID"]: row for row in rows}
    if len(by_id) != len(rows):
        raise ValueError("Stage B Evidence_ID values are not unique")
    if set(SOURCE_METADATA) - set(by_id):
        raise ValueError(f"Selected Stage B evidence records missing: {sorted(set(SOURCE_METADATA) - set(by_id))}")

    records = []
    for sequence, (evidence_id, source) in enumerate(SOURCE_METADATA.items(), start=1):
        metadata = source.copy()
        criteria = _criteria(evidence_id)
        raw = by_id[evidence_id]
        record = {
            "schema_version": "1.0.0",
            "mechanism_record_id": f"SBD-MECH-{sequence:04d}",
            "stage_b_reference": {
                "release_id": RELEASE_ID,
                "source_file": SOURCE_RELATIVE.as_posix(),
                "source_file_sha256": hashlib.sha256(source_bytes).hexdigest(),
                "row_count_at_build": len(rows),
                "evidence_id": evidence_id,
            },
            "raw_stage_b_record": raw,
            "mechanism_candidate": {
                "candidate_family": metadata.pop("candidate_family"),
                "source_reported_target": metadata.pop("source_reported_target"),
                "source_reported_relation": metadata.pop("source_reported_relation"),
                "classification_basis": metadata.pop("classification_basis"),
                "classification_status": "pending_manual_review",
                "canonical_target_id": None,
            },
            "source_verification": {
                "access_level": metadata.pop("access_level"),
                "verified_source_url": metadata.pop("verified_source_url"),
                "pmid": metadata.pop("pmid"),
                "doi": metadata.pop("doi"),
                "pmcid": metadata.pop("pmcid"),
                "source_locator": metadata.pop("source_locator"),
                "verification_note": metadata.pop("verification_note"),
            },
            "source_outcome_classification": {
                "raw_outcome": raw.get("Outcome", ""),
                "raw_direction": raw.get("Direction", ""),
                "raw_conflict_group": raw.get("Conflict_Group", ""),
                **classify_source_outcome(
                    raw.get("Outcome", ""),
                    direction=raw.get("Direction", ""),
                    conflict_group=raw.get("Conflict_Group", ""),
                ),
            },
            "review_criteria": criteria,
            "review_reasons": [
                {
                    "criterion": criterion,
                    "code": item["reason_codes"][0],
                    "status": "verified_source_check" if item["state"] == "meets" else "open",
                }
                for criterion, item in criteria.items()
            ],
            "source_discrepancies": metadata.pop("source_discrepancies", []),
            "review_state": {
                "status": "pending_manual_review",
                "acceptance": "pending",
                "identity_adjudication": "not_performed",
                "reviewer": None,
                "reviewed_on": None,
            },
        }
        records.append(record)
    return {
        "schema_version": "1.0.0",
        "release_id": RELEASE_ID,
        "source_file": SOURCE_RELATIVE.as_posix(),
        "source_file_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "source_row_count": len(rows),
        "selected_record_count": len(records),
        "warning": "Candidate classifications only. Every assessment is pending manual review; no identity, causal mechanism, dose equivalence, or clinical interpretation is approved.",
        "records": records,
    }


if __name__ == "__main__":
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(build(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
