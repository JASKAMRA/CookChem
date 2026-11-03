"""Apply V19-002 primary-source re-extractions to the V19 release tree."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-11-03"

SOURCES = {
    "22725836": {
        "doi": "10.1111/j.1365-2125.2012.04364.x",
        "title": "Effect of a herbal extract containing curcumin and piperine on midazolam, flurbiprofen and paracetamol (acetaminophen) pharmacokinetics in healthy volunteers.",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC3579260/",
        "cache": "source_archive/e66d84e148eab25af94ed9efe8ec6e7e6d8536261454c9de91b5e798856fc809_pmid_22725836.json",
        "access": "Primary PMC full text viewed online; local archive retains PubMed metadata only.",
    },
    "22114872": {
        "doi": "10.1111/j.1365-2125.2011.04150.x",
        "title": "Inhibition of the organic anion-transporting polypeptide 1B1 by quercetin: an in vitro and in vivo assessment.",
        "url": "https://bpspubs.onlinelibrary.wiley.com/doi/10.1111/j.1365-2125.2011.04150.x",
        "cache": "source_archive/000ac944a870cad5527a3bd67770332ca58a3b80f3e9d038faee0853281fc54f_pmid_22114872.json",
        "access": "Free-access publisher full text viewed online; local archive retains PubMed metadata only.",
    },
    "29908072": {
        "doi": "10.1111/bph.14393",
        "title": "Glycyrrhizin has a high likelihood to be a victim of drug-drug interactions mediated by hepatic organic anion-transporting polypeptide 1B1/1B3.",
        "url": "https://bpspubs.onlinelibrary.wiley.com/doi/10.1111/bph.14393",
        "cache": "source_archive/cea6b6020ad656ec69932aa25231748c501c204f62dc4f984c83a83f6865825a_pmid_29908072.json",
        "access": "Free-access publisher full text viewed online; local archive retains PubMed metadata only.",
    },
    "33435470": {
        "doi": "10.3390/pharmaceutics13010083",
        "title": "Involvement of Organic Anion Transporters in the Pharmacokinetics and Drug Interaction of Rosmarinic Acid.",
        "url": "https://www.mdpi.com/1999-4923/13/1/83",
        "cache": "source_archive/6d21bce6b7f20ae316b5a7af48f73b52f55596c9245ecc27a253a356e22e8235_pmid_33435470.json",
        "access": "Publisher full-text content and a legitimate article PDF mirror were viewed; direct publisher requests were rate-limited. Local archive retains PubMed metadata only.",
    },
}

RECORDS = {
    "SB-0018": {
        "pmid": "22725836", "drug": "Midazolam", "locator": "PMC3579260 full text: Methods—Study design and procedures; Results—Midazolam pharmacokinetics; Table 1.",
        "dose": "Curcuminoid/piperine capsule dose: 4 g total curcuminoids (70–80% curcumin, 15–25% demethoxycurcumin, 2.5–6.5% bisdemethoxycurcumin) plus 24 mg piperine per administration, four administrations over 2 days; oral midazolam 3 mg.",
        "population": "8 healthy volunteers (7 men, 1 woman; age 24–52 years).",
        "design": "Randomized, placebo-controlled six-period crossover; each probe studied in separate conditions; ≥7-day washout between treatment periods.",
        "effect": "No significant change in parent midazolam Cmax or AUC; Table 1 reports higher 1′-OH-midazolam Cmax with curcuminoid/piperine (p=0.03).",
        "outcome": "Table 1 (n=8; mean ± SD): midazolam Cmax 10.1 ± 6.1 placebo vs 9.9 ± 5.2 ng/mL, p=0.61; GMR 0.97 (90% CI 0.79–1.20). AUC(0,∞) 37.8 ± 31.5 vs 34.0 ± 23.4 ng·h/mL, p=0.32; GMR 0.91 (90% CI 0.75–1.11). 1′-OH-midazolam Cmax 3.4 ± 2.2 vs 5.0 ± 3.0 ng/mL, p=0.03; metabolite AUC p=0.07.",
        "limitations": "Small study (n=8), short two-day exposure, and combination-preparation-specific. The study did not test isolated curcumin or establish an ordinary-food exposure equivalence; one metabolite Cmax signal was reported.",
        "notes": "The paper describes a standardized multi-component capsule, not pure curcumin. Capsule contents were checked by HPLC during the study; no constituent-specific causal attribution is possible.",
        "direction": "No significant parent-drug PK change; 1′-OH-midazolam Cmax increased in Table 1.",
        "claims": "Table 1 verifies null parent-drug Cmax/AUC contrasts and a statistically significant 1′-OH-midazolam Cmax difference (p=0.03); no significant metabolite AUC difference (p=0.07).",
        "remaining": "Small n and short combination exposure; metabolite Cmax signal does not establish clinically important interaction or isolate the responsible constituent.",
        "verified": "Parent midazolam Cmax and AUC(0,∞), geometric mean ratios and 90% CIs, metabolite Cmax/AUC, n=8, preparation and probe dose.",
        "audit_disposition": "V19_TIER_1_FULL_TEXT_REVIEWED; RECORD_RECONCILED; METABOLITE_SIGNAL_RECORDED",
        "level": "formulation", "identity": "Curcumin identity verified as a constituent; the primary study tested a standardized curcuminoid/piperine multi-component preparation, not isolated curcumin.",
    },
    "SB-0019": {
        "pmid": "22725836", "drug": "Flurbiprofen", "locator": "PMC3579260 full text: Methods—Study design and procedures; Results—Flurbiprofen pharmacokinetics; Table 3.",
        "dose": "Curcuminoid/piperine capsule dose: 4 g total curcuminoids plus 24 mg piperine per administration, four administrations over 2 days; oral flurbiprofen 100 mg.",
        "population": "8 healthy volunteers (7 men, 1 woman; age 24–52 years).",
        "design": "Randomized, placebo-controlled six-period crossover; each probe studied in separate conditions; ≥7-day washout between treatment periods.",
        "effect": "No significant change in parent flurbiprofen Cmax or AUC; 4-OH-flurbiprofen Tmax was reported as shortened by 31% (Table 3 p=0.05).",
        "outcome": "Table 3 (n=8; mean ± SD): flurbiprofen Cmax 12.3 ± 2.0 placebo vs 11.6 ± 2.2 μg/mL, p=0.35; GMR 0.94 (90% CI 0.83–1.06). AUC(0,∞) 75.4 ± 21.7 vs 72.6 ± 20.4 μg·h/mL, p=0.22; GMR 0.97 (90% CI 0.93–1.00). 4-OH-flurbiprofen Tmax 3.6 ± 1.1 vs 2.0 ± 0.7 h; Table p=0.05, while Results prose says p<0.05 and reports 31% shortening.",
        "limitations": "Small study (n=8), short two-day exposure, and combination-preparation-specific. The parent drug's measured Cmax/AUC were not significantly changed; the metabolite Tmax result is borderline and the table/prose p-value precision differs.",
        "notes": "The tested intervention was the standardized curcuminoid/piperine combination, not isolated curcumin or ordinary turmeric/pepper food exposure.",
        "direction": "No significant parent-drug PK change; 4-OH-flurbiprofen Tmax shortened in the source.",
        "claims": "Table 3 verifies parent flurbiprofen Cmax/AUC, GMRs and 90% CIs; it also reports the 4-OH-flurbiprofen Tmax values and p=0.05.",
        "remaining": "Small n and combination-specific exposure; source reports a borderline metabolite Tmax change without a corresponding significant metabolite Cmax/AUC change.",
        "verified": "Parent flurbiprofen Cmax/AUC and 90% CIs, 4-OH-flurbiprofen Cmax/Tmax/AUC, n=8, preparation and probe dose.",
        "audit_disposition": "V19_TIER_1_FULL_TEXT_REVIEWED; RECORD_RECONCILED; METABOLITE_TMAX_RECORDED",
        "level": "formulation", "identity": "Curcumin identity verified as a constituent; the primary study tested a standardized curcuminoid/piperine multi-component preparation, not isolated curcumin.",
    },
    "SB-0020": {
        "pmid": "22725836", "drug": "Acetaminophen", "locator": "PMC3579260 full text: Methods—Study design and procedures; Results—Paracetamol pharmacokinetics; Table 4; Statistical analysis.",
        "dose": "Curcuminoid/piperine capsule dose: 4 g total curcuminoids plus 24 mg piperine per administration, four administrations over 2 days; oral paracetamol 325 mg.",
        "population": "8 healthy volunteers (7 men, 1 woman; age 24–52 years).",
        "design": "Randomized, placebo-controlled six-period crossover; each probe studied in separate conditions; ≥7-day washout between treatment periods.",
        "effect": "Results prose describes no significant overall paracetamol PK difference; Table 4 reports a borderline Cmax contrast (p=0.05; GMR 1.13, 90% CI 1.01–1.27). This source discrepancy remains open under V19-W02.",
        "outcome": "Table 4 (n=8; mean ± SD): paracetamol Cmax 3.4 ± 0.8 placebo vs 4.0 ± 1.2 μg/mL, p=0.05; GMR 1.13 (90% CI 1.01–1.27). AUC(0,∞) 14.6 ± 3.6 vs 14.2 ± 3.0 μg·h/mL, p=0.80; GMR 0.98 (90% CI 0.91–1.05). Results text says paracetamol PK values did not differ significantly; the rounded p-value and table interval/narrative interpretation are not reconciled (V19-W02).",
        "limitations": "Small study (n=8), short two-day combination exposure. Table 4 Cmax and the broad null narrative are not fully concordant; no effect/absence conclusion is assigned beyond the source's stated uncertainty.",
        "notes": "V19-W02 remains open. The tested intervention was a standardized curcuminoid/piperine combination, not isolated curcumin or an ordinary-food exposure.",
        "direction": "Source interpretation conflict: Table 4 Cmax estimate is higher while AUC is null; Results text describes no significant overall PK difference.",
        "claims": "Table 4 verifies Cmax/AUC means, units, p-values and 90% CIs; Results prose says plasma PK values did not differ significantly. Discrepancy is retained, not resolved by assumption.",
        "remaining": "Rounded p=0.05 and 90% CI 1.01–1.27 contrast with a null narrative. Exact unrounded test output and multiplicity interpretation are not supplied.",
        "verified": "Paracetamol Cmax/AUC table values, units, p-values, GMRs/90% CIs, study design, dose and narrative/table discrepancy.",
        "audit_disposition": "V19_TIER_1_FULL_TEXT_REVIEWED; SOURCE_DISCREPANCY_OPEN",
        "level": "formulation", "identity": "Curcumin identity verified as a constituent; the primary study tested a standardized curcuminoid/piperine multi-component preparation, not isolated curcumin.",
    },
    "SB-0090": {
        "pmid": "33435470", "drug": "Furosemide", "locator": "MDPI/PMC full text: Methods §2.6; Results—Inhibitory Effects of Rosmarinic Acid on the Pharmacokinetics of Furosemide and Valsartan; Figure 6; Table 3.",
        "dose": "Furosemide 0.2 mg/kg IV followed by rosmarinic acid 10 mg/kg IV or vehicle.",
        "population": "Rats; n=4 per group for the reported concentration-time data.",
        "design": "Controlled in-vivo intravenous rat pharmacokinetic experiment; furosemide followed by rosmarinic acid or vehicle; plasma samples through 8 h and urine collection through 12 h.",
        "effect": "Rosmarinic acid increased rat furosemide AUC and reduced clearance; urinary excretion was also reported to decrease.",
        "outcome": "Table 3 (mean ± SD; n=4): furosemide C0 2.25 ± 0.21 μM (control) vs 4.89 ± 0.39 μM (+ rosmarinic acid; p<0.05); AUC0–8 h 1.51 ± 0.11 vs 3.29 ± 0.05 μM·h (p<0.05); AUC0–∞ 1.52 ± 0.11 vs 3.30 ± 0.06 μM·h (p<0.05); clearance 6.68 ± 0.47 vs 3.06 ± 0.05 mL/h/kg (p<0.05). Source reports decreased urinary furosemide excretion (Figure 6).",
        "limitations": "Preclinical intravenous rat experiment (n=4); high parenteral doses and no direct human or ordinary-food exposure equivalence. Transporter mechanism is source-proposed and model-specific.",
        "notes": "Source examined furosemide and valsartan in separate rat experiments; results must remain probe- and regimen-specific.",
        "direction": "Increased furosemide plasma exposure and reduced clearance in rats under the tested IV regimen.",
        "claims": "Methods §2.6, Results, Figure 6 and Table 3 verify IV doses, rat model, sample size, C0/AUC/clearance values and the stated urinary excretion direction.",
        "remaining": "No translation to human therapeutic dosing, oral exposure or food-level rosmarinic acid is established.",
        "verified": "Furosemide dose/route, rosmarinic acid dose/route, n, comparator, C0, AUC0–8 h, AUC0–∞, clearance, units and urinary excretion direction.",
        "audit_disposition": "V19_TIER_1_FULL_TEXT_REVIEWED; QUANTITATIVE_OUTCOME_RECOVERED",
        "level": "formulation", "identity": "verified_connectivity",
    },
    "SB-0091": {
        "pmid": "33435470", "drug": "Valsartan", "locator": "MDPI/PMC full text: Methods §2.6; Results—Inhibitory Effects of Rosmarinic Acid on the Pharmacokinetics of Furosemide and Valsartan; Figure 7; Table 4.",
        "dose": "Valsartan 3 mg/kg IV followed by rosmarinic acid 10 mg/kg IV or vehicle.",
        "population": "Rats; n=4 per group for concentration-time data.",
        "design": "Controlled in-vivo intravenous rat pharmacokinetic/biliary excretion experiment; valsartan followed by rosmarinic acid or vehicle.",
        "effect": "Results prose reports no significant valsartan PK or biliary-excretion interaction; Table 4 marks an increase in C0 (p<0.05). This discrepancy remains open under V19-W03.",
        "outcome": "Table 4 (mean ± SD; n=4): valsartan C0 17.8 ± 1.3 μM (control) vs 25.8 ± 4.5 μM (+ rosmarinic acid; table marks p<0.05). AUC0–6 h 3.57 ± 1.3 vs 5.27 ± 0.81 μM·h and AUC0–∞ 3.73 ± 1.2 vs 5.41 ± 0.83 μM·h have no significance marker. Results prose states plasma concentration and biliary excretion were not significantly changed; reconcile the C0 marker with the narrative before assigning a null/effect conclusion (V19-W03).",
        "limitations": "Preclinical intravenous rat experiment (n=4). Table 4's C0 significance marker conflicts with the general null narrative; no clean null or interaction conclusion is assigned. No human/food equivalence.",
        "notes": "V19-W03 remains open. Values are transcribed as printed; no significance is inferred for unmarked AUC entries.",
        "direction": "Source discrepancy: isolated C0 increase is marked significant, while Results prose reports no significant overall valsartan PK change.",
        "claims": "Methods §2.6, Results, Figure 7 and Table 4 verify IV doses, model, n, PK/biliary context, C0/AUC values and the table-versus-text discrepancy.",
        "remaining": "Table 4 marks C0 p<0.05 while the narrative calls plasma concentration unchanged; author/source clarification or independent statistical adjudication is needed.",
        "verified": "Valsartan dose/route, rosmarinic acid dose/route, n, comparator, C0/AUC values and units, Table 4 significance marker, narrative and biliary endpoint.",
        "audit_disposition": "V19_TIER_1_FULL_TEXT_REVIEWED; SOURCE_DISCREPANCY_OPEN",
        "level": "formulation", "identity": "verified_connectivity",
    },
    "SB-0092": {
        "pmid": "33435470", "drug": "Probenecid", "locator": "MDPI/PMC full text: Methods—OAT1-mediated rosmarinic acid interaction study; Results §3.2; Figure 4; Table 2.",
        "dose": "Rosmarinic acid 1 mg/kg IV followed by probenecid 10 mg/kg IV or vehicle.",
        "population": "Rats; n=4 per group for the reported concentration-time data.",
        "design": "Controlled in-vivo intravenous rat pharmacokinetic experiment; rosmarinic acid followed by probenecid or vehicle; plasma sampling through 6 h.",
        "effect": "Probenecid increased rosmarinic acid plasma exposure and reduced its clearance; the primary paper reports reduced urinary excretion.",
        "outcome": "Table 2 (mean ± SD; n=4): rosmarinic acid AUC0–6 h 7.63 ± 0.68 μM·h (control) vs 15.6 ± 4.7 μM·h with probenecid (p<0.05); AUC0–∞ 7.74 ± 0.73 vs 15.6 ± 4.7 μM·h (p<0.05); clearance 6.02 ± 0.56 vs 3.17 ± 0.95 mL/h/kg (p<0.05). Probenecid dose 10 mg/kg IV; rosmarinic acid 1 mg/kg IV.",
        "limitations": "Preclinical intravenous rat experiment (n=4), inhibitor dose-specific; no direct human or ordinary-food exposure equivalence.",
        "notes": "This is a reverse disposition result: probenecid alters rosmarinic acid disposition. It is not evidence that rosmarinic acid raises probenecid exposure or establishes a food-drug effect.",
        "direction": "Increased rosmarinic acid exposure under probenecid co-injection; reverse interaction direction.",
        "claims": "Methods, Results §3.2, Figure 4 and Table 2 verify dose sequence, n, AUC values, units and decreased clearance/urinary excretion.",
        "remaining": "No human clinical interaction or dietary equivalence is established; the result is a rat IV OAT1 probe experiment.",
        "verified": "Rosmarinic acid and probenecid dose/route/order, comparator, n, AUC, clearance, units and urinary excretion direction.",
        "audit_disposition": "V19_TIER_1_FULL_TEXT_REVIEWED; QUANTITATIVE_OUTCOME_RECOVERED",
        "level": "formulation", "identity": "verified_connectivity",
    },
    "SB-0101": {
        "pmid": "22114872", "drug": "Pravastatin", "locator": "Wiley full text: Methods—Assessment of the effect of quercetin on pravastatin PK; Results—In vivo influence; Table 1.",
        "dose": "Quercetin 500 mg capsule once daily for 14 days vs corn-starch placebo; pravastatin 40 mg orally on Day 14, 1 h after capsule.",
        "population": "16 healthy Chinese-Han men, ages 19–24 years.",
        "design": "Two-phase randomized crossover; 14-day quercetin or placebo period; 2-week washout; single-dose pravastatin PK on Day 14.",
        "effect": "Quercetin pretreatment increased pravastatin AUC(0,10 h) by 24% and Cmax by 31%; apparent clearance decreased 18%; Table 1 resolves the abstract's ambiguous clearance interval wording.",
        "outcome": "Table 1 (n=16): AUC(0,10 h) 354.6 ± 89.6 placebo vs 437.8 ± 118.6 ng·h/mL; 124% of control (95% CI 115–132), p<0.001. Cmax 123.2 ± 48.3 vs 162.0 ± 76.0 ng/mL; 131% (95% CI 120–142), p<0.001. t1/2 1.6 ± 0.3 vs 1.8 ± 0.3 h; 114% (95% CI 104–124), p=0.027. CL/F 119.5 ± 29.2 vs 97.3 ± 24.7 L/h; ratio 82% (95% CI 75–89), p<0.001. Tmax values printed as 0.9 ± 0.4 vs 0.9 ± 0.3 h, p=0.065; table footnote instead says Tmax is median (range), so the dispersion notation remains unresolved (V19-W04).",
        "limitations": "Small supplement study in 16 healthy Chinese-Han men; no ordinary-food exposure equivalence. Table footnote conflicts with printed Tmax dispersion notation (V19-W04).",
        "notes": "Full Table 1 resolves the human percent changes and CL/F ratio/CI previously withheld due to abstract formatting. Quercetin capsules contained excipients; no food-equivalent dose is established.",
        "direction": "Pravastatin AUC/Cmax increased and CL/F decreased under the 14-day supplement regimen; Tmax not significantly changed per table p=0.065.",
        "claims": "Full-text Methods and Table 1 verify randomized crossover, 16 male volunteers, regimen, AUC/Cmax/t1/2/CL/F values and confidence intervals; exact Tmax spread interpretation remains open.",
        "remaining": "Supplement-specific result in a small all-male cohort; Table 1 Tmax values use ± notation although its footnote says median and range.",
        "verified": "Human regimen/design, n, AUC/Cmax/t1/2/CL/F/Tmax, units, percentage-of-control ratios, confidence intervals and p-values.",
        "audit_disposition": "V19_TIER_1_FULL_TEXT_REVIEWED; TABLE_VALUES_RECOVERED; CLEARANCE_CI_CLARIFIED; TMAX_NOTATION_OPEN",
        "level": "formulation", "identity": "verified_external_parent_identity_no_master_link",
    },
    "SB-0147": {
        "pmid": "29908072", "drug": "Rifampin", "locator": "Wiley full text: Methods—Rat pharmacokinetic studies; Results—Rat pharmacokinetics of IV glycyrrhizin altered by rifampin inhibition of hepatic Oatp1b2; Tables 3–4; Figure 5.",
        "dose": "Glycyrrhizin 2.6 mg/kg IV bolus; rifampin 20 mg/kg IV at 0, 3 and 6 h vs saline control.",
        "population": "Rats; plasma PK total n=12 across three independent experiments; separate tissue-distribution experiment n=5.",
        "design": "Controlled rat intravenous pharmacokinetic experiment with rifampin pretreatment vs saline; serial plasma sampling to 12 h. Human values in the paper are prior data/model validation and PBPK predictions, not a human rifampin interaction trial.",
        "effect": "Rifampin inhibition of rat Oatp1b2 reduced glycyrrhizin systemic clearance and raised plasma exposure in rats; this is not a clinical licorice interaction result.",
        "outcome": "Table 3 (observed rat values, mean ± SD): after IV glycyrrhizin 2.6 mg/kg, AUC0–12 h 41.3 ± 10.4 μM·h (control) vs 151.8 ± 14.8 μM·h (rifampin; 3.7-fold; p<0.05); AUC0–∞ 43.1 ± 12.0 vs 199.8 ± 40.1 μM·h; t1/2 2.1 ± 0.5 vs 6.3 ± 1.3 h; total plasma clearance 76.4 ± 22.7 vs 20.7 ± 3.4 mL·h−1·kg−1 (27.1% of control; p<0.05). Plasma data total n=12 over three experiments.",
        "limitations": "Preclinical IV interaction using research-inhibitor rifampin doses in rats. The paper's human PBPK predictions are not direct human coadministration evidence; IV glycyrrhizin does not establish oral licorice/food effects.",
        "notes": "Reverse interaction: rifampin altered glycyrrhizin exposure. Do not report this as licorice increasing rifampin exposure. Human projections depend on a model of transporter impairment.",
        "direction": "Increased glycyrrhizin systemic exposure after rifampin in rats; no human observed interaction.",
        "claims": "Methods, Results, Tables 3–4 and Figure 5 verify rat dose/regimen, sample size, AUC, half-life and clearance values; human section is PBPK prediction only.",
        "remaining": "No direct human rifampin–glycyrrhizin interaction trial, no oral licorice equivalence, and no ordinary-food inference.",
        "verified": "Rat IV doses/timing, comparator, species/sample size, plasma AUC/t1/2/clearance values, units, statistical markers, and separation from human PBPK predictions.",
        "audit_disposition": "V19_TIER_1_FULL_TEXT_REVIEWED; QUANTITATIVE_OUTCOME_RECOVERED; SPECIES_SCOPE_RETAINED",
        "level": "compound", "identity": "external_reference_identity",
    },
}


def read_csv(rel: str) -> tuple[list[str], list[dict[str, str]], bool]:
    path = ROOT / rel
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader), bom


def write_csv(rel: str, fields: list[str], rows: list[dict[str, str]], bom: bool) -> None:
    path = ROOT / rel
    with path.open("w", encoding="utf-8-sig" if bom else "utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def update_rows(rel: str, key: str, updates: dict[str, dict[str, str]]) -> None:
    fields, rows, bom = read_csv(rel)
    seen: set[str] = set()
    for row in rows:
        identifier = row.get(key, "")
        if identifier in updates:
            row.update(updates[identifier])
            seen.add(identifier)
    missing = set(updates) - seen
    if missing:
        raise ValueError(f"{rel}: expected identifiers not found: {sorted(missing)}")
    write_csv(rel, fields, rows, bom)


def warning_rows() -> None:
    fields, rows, bom = read_csv("data/warning_ledger.csv")
    target = next(r for r in rows if r["Warning_ID"] == "V5-source_reporting_units")
    target.update({
        "Action": target["Action"] + " V19-002: reviewed Quercetin–Pravastatin (SB-0101, PMID 22114872) publisher full text and Table 1; recovered units/percentages and resolved the CL/F ratio interval for this component.",
        "After": "Partially resolved: Quercetin–Pravastatin table values and CL/F confidence interval recovered; two affected source pairs remain pending.",
        "Remaining_Limitations": "Naringenin-Felodipine and Ferulic acid-Clopidogrel remain unreviewed in V19-002; their AUC/concentration units and percentage/CI wording are not adjudicated. Quercetin Tmax notation is tracked separately as V19-W04.",
        "Resolution_Source": target["Resolution_Source"] + "; Wiley full text, Table 1, PMID 22114872, DOI 10.1111/j.1365-2125.2011.04150.x",
        "Review_Date": DATE,
        "Audit_Status": "PARTIALLY_RESOLVED",
        "Audit_Rationale": "Direct full-text recheck resolved the withheld Quercetin–Pravastatin Table 1 values and clearance interval (82% of control; 95% CI 75–89%). The warning covers two additional unreviewed pairs, so it remains partially resolved.",
        "Audit_Verification_Reference": "Wiley full text, Methods and Table 1 for PMID 22114872; V19_batch_002_review.csv; V19-W04 tracks separate Tmax notation issue.",
        "Audit_Dependencies": "Primary-source review of Naringenin-Felodipine and Ferulic acid-Clopidogrel; no assumptions or extrapolation from quercetin.",
    })
    write_csv("data/warning_ledger.csv", fields, rows, bom)

    def new_warning(wid: str, code: str, description: str, affected: str, before: str, action: str, remaining: str, reference: str, dependency: str, status: str) -> dict[str, str]:
        return {
            "Warning_ID": wid, "Code": code, "Description": description, "Affected": affected,
            "Classification": "scientific source discrepancy / quantitative outcome",
            "Before": before, "Action": action,
            "After": "Open; primary-source reporting discrepancy retained pending expert/source adjudication.",
            "Remaining_Limitations": remaining, "Resolution_Source": reference, "Review_Date": DATE,
            "Audit_Status": status, "Inherited_Severity": "NOT_RECORDED",
            "Audit_Rationale": "Direct primary full-text review found a table/text reporting discrepancy; numerical values are preserved as reported and no unsupported interpretation was imposed.",
            "Audit_Verification_Reference": reference,
            "Audit_Dependencies": dependency, "V17_Ledger_Audit_Status": "NOT_IN_V18",
        }

    additions = [
        new_warning(
            "V19-W02", "TABLE_NARRATIVE_PARACETAMOL_CMAX_DISCREPANCY",
            "For SB-0020 (PMID 22725836), Table 4 reports paracetamol Cmax GMR 1.13 (90% CI 1.01–1.27) and p=0.05, while Results and abstract describe no significant/meaningful overall PK change. The rounded p-value and interval/text interpretation remain unreconciled.",
            "SB-0020 | PMID:22725836 | paracetamol Cmax", "Quantitative outcome blank; inherited evidence characterized the study as no meaningful parent PK change.",
            "Reviewed primary full text, Methods statistical analysis, Results and Table 4; extracted Cmax/AUC means, units, p-values and GMR intervals while preserving both table and narrative interpretations.",
            "Exact unrounded p-value and any multiplicity treatment are not supplied; do not conclude a confirmed interaction or absence from these rounded/internally discordant statements.",
            "PMC3579260 full text, Results—Paracetamol pharmacokinetics and Table 4; PMID 22725836; V19_batch_002_review.csv.",
            "Independent statistical adjudication or explicit author/source clarification of rounded p=0.05 and the Cmax interval versus the null narrative.",
            "NEEDS_MANUAL_REVIEW",
        ),
        new_warning(
            "V19-W03", "TABLE_NARRATIVE_VALSARTAN_C0_DISCREPANCY",
            "For SB-0091 (PMID 33435470), Table 4 marks valsartan C0 as increased with rosmarinic acid (17.8 ± 1.3 to 25.8 ± 4.5 μM; p<0.05), while Results state that valsartan plasma concentration and biliary excretion were not significantly changed.",
            "SB-0091 | PMID:33435470 | valsartan C0", "Quantitative outcome blank; inherited record described a null valsartan PK result.",
            "Reviewed primary full text Methods §2.6, Results, Figure 7 and Table 4; transcribed C0/AUC values and retained the C0 marker and null narrative.",
            "The source does not reconcile the C0 significance marker with its broad null statement; no clean null/effect interpretation is assigned.",
            "MDPI/PMC primary full text, Results—Inhibitory Effects of Rosmarinic Acid on the Pharmacokinetics of Furosemide and Valsartan; Figure 7; Table 4; PMID 33435470.",
            "Expert/source adjudication of the C0 significance marker against the results narrative; no significance may be inferred for unmarked AUC values.",
            "NEEDS_MANUAL_REVIEW",
        ),
        new_warning(
            "V19-W04", "TMAX_SUMMARY_NOTATION_CONFLICT",
            "For SB-0101 (PMID 22114872), Table 1 prints pravastatin Tmax as 0.9 ± 0.4 h and 0.9 ± 0.3 h, while the same table's footnote says Tmax data are medians with range. The summary statistic/dispersion notation is unclear.",
            "SB-0101 | PMID:22114872 | pravastatin Tmax", "Inherited record stated Tmax unchanged without extracting Table 1 or its footnote.",
            "Reviewed the publisher full-text Methods and Table 1; retained the printed values and p=0.065 without reinterpreting ± as SD or range.",
            "The table does not reconcile ± notation with the stated median/range format; do not normalize or relabel its dispersion.",
            "Wiley full text, Table 1 and footnote, PMID 22114872; V19_batch_002_review.csv.",
            "Author/publisher clarification of whether the displayed Tmax ± quantities are a range or another summary statistic.",
            "NEEDS_MANUAL_REVIEW",
        ),
    ]
    existing = {row["Warning_ID"] for row in rows}
    if existing.intersection({r["Warning_ID"] for r in additions}):
        raise ValueError("V19-002 warning IDs already exist; refusing duplicate insertion")
    rows.extend(additions)
    write_csv("data/warning_ledger.csv", fields, rows, bom)

    audit_fields, audit_rows, audit_bom = read_csv("validation/V19_warning_audit.csv")
    wa = next(r for r in audit_rows if r["Warning_ID"] == "V5-source_reporting_units")
    wa.update({
        "V19_Status": "PARTIALLY_RESOLVED", "V19_Recheck_Status": "RECHECKED_PARTIAL_IN_BATCH_002",
        "V19_Review_Work": "Reviewed the full Wiley article for SB-0101 (PMID 22114872), including Methods and Table 1. Recovered AUC/Cmax/CL/F values, units and CIs; Table 1 reports CL/F at 82% of control (95% CI 75–89%).",
        "V19_Evidence_or_Rationale": "The Quercetin–Pravastatin component of this aggregate warning is resolved for its quantitative values; Naringenin-Felodipine and Ferulic acid-Clopidogrel remain unreviewed. V19-W04 separately records a Table 1 Tmax notation ambiguity.",
        "Remaining_Limitations": "Two affected pairs remain unreviewed: Naringenin-Felodipine and Ferulic acid-Clopidogrel. No cross-study inference is made.",
    })
    new_audits = [
        {"Warning_ID":"V19-W02","V18_Status":"NEW_IN_V19","V19_Status":"NEEDS_MANUAL_REVIEW","V19_Recheck_Status":"NEW_WARNING_IN_BATCH_002","V19_Review_Work":"Primary PMC full text, Results and Table 4 reviewed for SB-0020.","V19_Evidence_or_Rationale":"Table 4 Cmax GMR 1.13 (90% CI 1.01–1.27), p=0.05; Results and abstract call overall parent PK null/no meaningful. Preserve both.","Remaining_Limitations":"Rounded p-value and table interval/narrative significance interpretation require expert/source adjudication."},
        {"Warning_ID":"V19-W03","V18_Status":"NEW_IN_V19","V19_Status":"NEEDS_MANUAL_REVIEW","V19_Recheck_Status":"NEW_WARNING_IN_BATCH_002","V19_Review_Work":"Primary MDPI/PMC full text, Methods §2.6, Results, Figure 7 and Table 4 reviewed for SB-0091.","V19_Evidence_or_Rationale":"Table 4 marks valsartan C0 increase p<0.05; Results prose says plasma concentration and biliary excretion were not significantly changed.","Remaining_Limitations":"Table C0 marker versus narrative requires adjudication; AUC values without significance markers remain unclassified."},
        {"Warning_ID":"V19-W04","V18_Status":"NEW_IN_V19","V19_Status":"NEEDS_MANUAL_REVIEW","V19_Recheck_Status":"NEW_WARNING_IN_BATCH_002","V19_Review_Work":"Publisher full-text Table 1 and footnote reviewed for SB-0101.","V19_Evidence_or_Rationale":"Table prints Tmax as 0.9 ± 0.4 and 0.9 ± 0.3 h but footnote says medians with range; values retained verbatim.","Remaining_Limitations":"No source explanation for the summary notation; do not interpret the ± values."},
    ]
    audit_rows.extend(new_audits)
    write_csv("validation/V19_warning_audit.csv", audit_fields, audit_rows, audit_bom)


def build_review_rows() -> None:
    fields = ["Batch", "Evidence_ID", "Compound_ID", "Compound", "Drug_Probe", "Study_ID", "PMID", "DOI", "Primary_Source_URL", "Source_Access_Status", "Local_Metadata_Cache", "Source_Locator", "Verification_Tier", "Review_Date", "Correction_Made", "Verified_Outcome", "Remaining_Limitation"]
    evidence = {r["Evidence_ID"]: r for r in read_csv("data/interaction_evidence.csv")[1]}
    rows = []
    for evidence_id, spec in RECORDS.items():
        e = evidence[evidence_id]
        s = SOURCES[spec["pmid"]]
        correction = "Recovered blank quantitative outcome from primary-source table; updated source locator and full-text verification; "
        if evidence_id in {"SB-0018", "SB-0019", "SB-0020"}:
            correction += "qualified the multi-component curcuminoid/piperine preparation and its secondary findings."
        elif evidence_id == "SB-0101":
            correction += "resolved the CL/F ratio interval from Table 1; retained separate Tmax notation warning V19-W04."
        elif evidence_id == "SB-0147":
            correction += "replaced abstract-only regimen/outcome with observed rat table values; kept human PBPK predictions distinct."
        elif evidence_id == "SB-0091":
            correction += "recorded Table 4 values and added the open narrative/table warning V19-W03."
        elif evidence_id == "SB-0020":
            correction += "recorded Table 4 values and added the open narrative/table warning V19-W02."
        else:
            correction += "recovered rat Table 2/3 values without human extrapolation."
        rows.append({
            "Batch":"V19-002", "Evidence_ID":evidence_id, "Compound_ID":e["Compound_ID"], "Compound":e["Compound"], "Drug_Probe":e["Drug"],
            "Study_ID":e["Study_ID"], "PMID":spec["pmid"], "DOI":SOURCES[spec["pmid"]]["doi"], "Primary_Source_URL":s["url"],
            "Source_Access_Status":s["access"], "Local_Metadata_Cache":"provenance/"+s["cache"], "Source_Locator":spec["locator"],
            "Verification_Tier":"1", "Review_Date":DATE, "Correction_Made":correction,
            "Verified_Outcome":spec["outcome"], "Remaining_Limitation":spec["remaining"],
        })
    write_csv("validation/V19_batch_002_review.csv", fields, rows, False)


def apply() -> dict[str, object]:
    if not (ROOT / "release_metadata.json").is_file():
        raise SystemExit(f"Not a V19 release tree: {ROOT}")
    evidence_updates = {}
    source_updates = {}
    claim_updates = {}
    for evidence_id, spec in RECORDS.items():
        source = SOURCES[spec["pmid"]]
        evidence_updates[evidence_id] = {
            "Interaction_Effect": spec["effect"], "Evidence_Level": spec["level"], "Direction": spec["direction"],
            "Quantitative_Outcome": spec["outcome"], "Dose": spec["dose"], "Population": spec["population"],
            "Study_Design": spec["design"], "Source_URL": source["url"], "Source_Cache": "provenance/"+source["cache"],
            "Source_Locator": spec["locator"], "Preparation": spec["dose"], "Identity_Status": spec["identity"],
            "Limitations": spec["limitations"], "Notes": spec["notes"],
        }
        if evidence_id in {"SB-0018", "SB-0019", "SB-0020"}:
            evidence_updates[evidence_id]["Co_Compounds"] = "Piperine | Demethoxycurcumin | Bisdemethoxycurcumin"
            evidence_updates[evidence_id]["Perpetrator"] = "compound_or_preparation"
            evidence_updates[evidence_id]["CookRisk_Exposure_Link"] = "Curcumin constituent mapping only; preparation-to-food exposure equivalence is not established."
        if evidence_id == "SB-0020":
            evidence_updates[evidence_id]["Outcome"] = "source_discrepancy_pending_adjudication"
        if evidence_id == "SB-0091":
            evidence_updates[evidence_id]["Outcome"] = "source_discrepancy_pending_adjudication"
        source_updates[evidence_id] = {
            "DOI": source["doi"], "Source_Title": source["title"], "Source_URL": source["url"],
            "Source_Cache": source["cache"], "Source_Locator": spec["locator"],
            "Verification_Status": "Tier 1: primary full text and relevant methods/results/table directly reviewed in V19-002",
            "Fields_Audited": "compound/form identity; comparator; dose/route; study design/model; sample size; endpoint and direction; original numerical values/units/statistics; source limitations and discrepancies",
            "Limitations": spec["limitations"], "Source_Type": "Primary research", "Verification_Date": DATE,
            "Verification_Method": source["access"] + " Record-specific table extraction and limitations are in validation/V19_batch_002_review.csv.",
            "Verification_Level": "1", "Audit_Disposition": spec["audit_disposition"],
            "Reviewer": "Codex AI-assisted primary-source curation; expert adjudication remains open for flagged conflicts",
            "Endpoint_Verified": spec["verified"], "Numerical_Outcome_Verified": spec["claims"],
            "Study_ID": "PMID:"+spec["pmid"], "Drug_Probe": spec["drug"],
            "V18_Unresolved_Discrepancy": "V18 source content was carried forward without reopening. V19-002 directly reviewed the linked primary full text; " + spec["remaining"],
            "Disposition_Date": DATE,
        }
        claim_updates[evidence_id] = {
            "Source_Locator": spec["locator"],
            "Verification_Status": "V19 Tier 1 primary full-text review completed; see batch-level source review.",
            "Numerical_Use": spec["claims"],
            "Limitations": spec["limitations"],
        }
    update_rows("data/interaction_evidence.csv", "Evidence_ID", evidence_updates)
    update_rows("provenance/source_audit.csv", "Evidence_ID", source_updates)
    update_rows("provenance/claim_support_and_verification.csv", "Evidence_ID", claim_updates)

    study_updates = {
        "PMID:22725836": {"Verification_Status":"V19-002: primary PMC full text; Methods and Tables 1, 3 and 4 reviewed for SB-0018–SB-0020; combination preparation retained."},
        "PMID:22114872": {"Verification_Status":"V19-002: free-access Wiley full text and Table 1 reviewed for SB-0101. SB-0102 remains without a separate V19 claim-level review."},
        "PMID:29908072": {"Verification_Status":"V19-002: free-access Wiley full text; rat Methods, Results, Tables 3–4 and Figure 5 reviewed for SB-0147; human section distinguished as PBPK/model validation."},
        "PMID:33435470": {"Verification_Status":"V19-002: primary article Methods, Results, Figures 4/6/7 and Tables 2–4 reviewed via MDPI/PMC indexed full text and article PDF for SB-0090–SB-0092."},
    }
    update_rows("data/study_registry.csv", "Study_ID", study_updates)
    warning_rows()
    build_review_rows()

    meta_path = ROOT / "release_metadata.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8-sig"))
    meta["readiness"] = "SCIENTIFIC_REMEDIATION_IN_PROGRESS"
    meta["release_status"] = "SCIENTIFIC_REMEDIATION_IN_PROGRESS"
    meta["warning_count"] = 74
    meta["v19_primary_source_review"] = {
        "batches_completed": ["V19-001", "V19-002"],
        "evidence_records_reviewed": 11,
        "tier_1_primary_full_text_records": 11,
        "records_corrected_or_reconstructed": 9,
        "source_review_remaining": 306,
        "warnings_individually_reaudited_in_v19": 2,
        "inherited_warning_rows_preserved": 70,
        "inherited_warning_rows_reaudited": 2,
        "inherited_warning_rows_carried_forward_without_v19_reaudit": 68,
        "warning_rows_preserved": 74,
        "warning_status_counts": {"RESOLVED":3,"PARTIALLY_RESOLVED":15,"STILL_VALID":26,"NEEDS_MANUAL_REVIEW":28,"NOT_APPLICABLE":2},
        "new_warning_count": 4,
        "warning_ids_added": ["V19-W01","V19-W02","V19-W03","V19-W04"],
    }
    meta["v19_quantitative_outcome_audit"] = {"original_blank_fields":90,"outcomes_recovered_in_v19":8,"blank_fields_remaining":82,"source_review_batch":"V19-002"}
    meta["v19_validation"] = {
        **meta.get("v19_validation", {}),
        "batch01_integrity":"PASS", "batch02_integrity":"PENDING_VALIDATION",
        "batch02_tests_passed":0,"batch02_tests_failed":0,
        "full_stageB_regression":"PENDING_FINAL_VALIDATION",
        "v19_exact_manifest":"PENDING_FINAL_PACKAGING",
        "v19_clean_copy_manifest":"PENDING_FINAL_PACKAGING",
    }
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    return {"batch":"V19-002","records_updated":len(RECORDS),"new_warnings":3,"status":"APPLIED_PENDING_VALIDATION"}


if __name__ == "__main__":
    print(json.dumps(apply(), indent=2, ensure_ascii=False))
