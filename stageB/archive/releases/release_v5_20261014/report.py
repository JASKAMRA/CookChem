from pathlib import Path
import csv,json,html
from reportlab.platypus import SimpleDocTemplate,Paragraph,Table,TableStyle,Spacer,PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
O=Path(__file__).resolve().parent
def load(p):return json.loads((O/p).read_text(encoding='utf8'))
def read(p):
    with (O/p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
s=load('outputs/release_summary.json');v=load('audit/validation_report.json');tests=load('audit/mutation_tests.json');rebuild=load('audit/rebuild_verification.json');manifest=load('audit/preservation_manifest.json');reg=read('outputs/compound_registry.csv');new=read('outputs/new_evidence_records.csv')
blocks=[]
def h(t):blocks.append(('h',t))
def p(t):blocks.append(('p',t))
def table(head,rows,widths):blocks.append(('t',head,rows,widths))
def page(t):blocks.append(('break',));h(t)
h('CookRisk Stage B v5 Expansion Report')
p('14 October 2026 | Evidence-backed compound and interaction database release')
p(f"V5 adds {s['new_compounds']} compounds and {s['new_records']} primary-source interaction records to the verified v4 baseline. The final database contains {s['compounds']} compounds, {s['records']} records, {s['drugs']} drugs/probes and {s['primary_reports']} primary reports. All 73 inherited records and their stable identifiers remain unchanged. No Stage A training or outlier work, exposure estimation, clinical risk scoring, Stage C or Stage D was performed.")
table(['Measure','Verified v4','Final v5'],[['Compounds','14',str(s['compounds'])],['Evidence records','73',str(s['records'])],['Drugs and probes','36',str(s['drugs'])],['Primary reports by unique PMID','53',str(s['primary_reports'])],['Human PK / controlled clinical','55 / 2','61 / 2'],['Animal / in vitro','10 / 6','27 / 28'],['Numerical-outcome records','48',str(s['numerical_records'])]], [3.4,1.3,1.3])
h('Changes and planning targets')
p('The 12 additions are myricetin, luteolin, ellagic acid, gallic acid, ferulic acid, caffeic acid, chlorogenic acid, rosmarinic acid, naringenin, bergamottin, chrysin and fisetin. The 45 new records are SB-0074 through SB-0118 and are supported by 27 new primary reports. No inherited evidence record was corrected or removed. Registry coverage counts were updated with a separate field-level change log.')
p('The 25-30-compound and approximately 80-120-primary-report planning ranges were reached. The 150-200-record range was not reached: this bounded pass retained 118 supported records. Remaining candidates require further source and preparation review; records were not duplicated, inferred or weakened to fill the gap. This result does not imply the broader literature contains no further eligible evidence.')
h('Available files and baseline freeze')
p(f"The current-folder inventory includes the v4 registry, evidence table, primary reports, claim and warning audits, identity mappings, candidate files, search logs, primary caches, scripts and previous packages. Filenames, purposes, row counts, source fields and inspection status are recorded. All {len(manifest):,} files in the v5 preservation manifest are unchanged. Metadata/hash inventory is distinguished from scientific source review.")
p('Direct verification confirmed the reported v4 counts, 48 numerical records, original 64 preserved rows, 24/24 technical checks, 8/8 mutation tests and nine open warning entries across eight codes. V4 was treated as immutable; no remote repository was needed.')

page('Candidate selection identity and food provenance')
p('Sixteen candidates were considered: 12 selected, four deferred and zero rejected. Selection considered dietary relevance, primary drug endpoints, human evidence where available, identity/analyte specificity, cooking information, source accessibility and incremental scientific value. No numerical selection score was created. The dated selection ledger is separate from experimental interaction citations.')
table(['New compound','Evidence basis and important restriction'],[['Myricetin','Animal PK plus microsomal null; standalone parent because original group is uncertain'],['Luteolin','GHB transport and clearance; experimental IV doses are not food exposure'],['Ellagic acid','Isolated warfarin arm; separate from total ellagic acid and extracts'],['Gallic acid','Named renal transport probes and paclitaxel null; not a human RLQ drug-interaction trial'],['Ferulic acid','Clopidogrel changes compound disposition; reverse direction preserved'],['Caffeic acid','Named OAT1/OAT3 probes; parent-connectivity mapping only'],['Chlorogenic acid','Platinum-drug cell effects and resistant-cell null; isomers not pooled'],['Rosmarinic acid','Furosemide effect, valsartan null and reverse probenecid interaction'],['Naringenin','Animal PK and microsomal null; generic parent CID 932, no uncertain master link'],['Bergamottin','Human isolated capsules distinguish constituent from grapefruit juice'],['Chrysin','Human uncontrolled pilot and rat caffeine null; no safety conclusion'],['Fisetin','Separate named chemotherapy experiments; synergy and no-synergy distinguished']], [1.15,4.85])
p('Hesperetin was deferred because the accessible rasagiline abstract did not resolve separate-compound attribution. Baicalein requires further preparation and dietary-context review. Theobromine had an old candidate interaction citation without sufficient verified details. Lycopene cooking/bioavailability papers alone did not establish an eligible drug interaction. These are bounded-review deferrals, not evidence of no possible interaction.')
p('Seven additions reuse verified exact or parent-connectivity inventory mappings; five use separately verified external parent identities. Naringenin is not naringin, and a stereochemically unspecified study was not assigned to natural (S)-naringenin. Myricetin was not linked to its uncertain master group. Existing quercetin/total-flavonol and daidzein/glycoside restrictions remain.')
p('Primary food/processing papers on edible berry flavonols (PMID 10794622), berry processing (11032486) and cooked-tomato bioavailability (15309458) were retained separately. They do not count among the 80 interaction reports or certify native aglycone retention. No retained dose or retention coefficient was calculated.')

page('Primary evidence results and review scope')
p('The 45 additions comprise six human PK/probe records, 17 animal records and 22 in-vitro records. Eight have selected full-text methods/outcome review and 37 have primary abstract-level manual extraction. Full-text availability alone is not described as full review. All inherited review levels remain explicit in all_record_review_audit.csv.')
h('Human evidence')
p('Bergamottin capsules increased felodipine exposure in an 11-person crossover: at 12 mg, Cmax increased 40% and AUC 37%. Larger grapefruit juice effects were not attributed to bergamottin alone. Chrysin with irinotecan was an uncontrolled 20-patient pilot with PK in 18 patients; its historical-comparator metabolite ratio does not prove clinical protection or safety. [PMIDs 15592332, 16003560]')
p('New quercetin records cover pravastatin and two talinolol experiments; curcumin adds a human talinolol experiment. One quercetin study had nonsignificant mean talinolol changes; another reported decreased exposure with genotype variation. Shared genotype-pool descriptions do not establish independent trial populations. Ambiguous pravastatin percentage/CI wording was withheld pending reliable table review. [PMIDs 22114872, 24472704, 23422925, 17468862]')
h('Preclinical effects null findings and context differences')
p('Myricetin increased exposure to several orally administered drugs in rats, but IV doxorubicin/docetaxel results were null under tested conditions; a coamorphous formulation was identified separately. Luteolin changed GHB clearance and sleep duration in rats and inhibited named GHB uptake in cells. Ferulic acid with clopidogrel and rosmarinic acid with probenecid are reverse interactions affecting the food compound.')
p('Rosmarinic acid increased rat furosemide exposure but did not significantly change valsartan PK. Gallic/caffeic acid assays use named transport probes, not general enzyme statements. Ellagic acid and quercetin warfarin arms were separated from whole plant extracts. Chlorogenic acid/platinum-drug effects were cell-context dependent, including a resistant-cell null; no pooled interaction coefficient was created.')
p('Fisetin experiments include drug-specific synergy and no synergy. No synergy with mitoxantrone or methotrexate does not mean no interaction. A separate microsomal study found no paclitaxel metabolism inhibition by myricetin, gallic acid or naringenin, while other tested compounds inhibited metabolism. Separate compounds/drugs share one PMID; metabolites and donors were not inflated into extra reports. [PMIDs 26884726, 12920504]')
p('Five new records are classified as null findings and two as no synergy detected; additional rows preserve mixed endpoint/route nulls and nonsignificant changes. The 73 numerical-outcome records include exposure measures, assay constants, metabolic ratios and a combination index. The combination index is not a confidence interval or clinical risk score.')

page('Search validation reproducibility and limitations')
h('Search and screening')
p(f"Sixteen broad queries and 16 historical title-focused queries used a 100-result cap. They retrieved {s['retrieved_candidate_occurrences']} candidate occurrences, corresponding to {s['raw_unique_retrieved_candidates']} unique retrieved records and {s['duplicate_retrieval_occurrences']} repeated retrieval occurrences. Exact PMID and primary food-source follow-up added verification snapshots. {s['adjudicated_primary_or_context_sources']} sources received explicit inclusion, deferral or context-only decisions. Remaining retrieved candidates are marked not fully screened, not falsely excluded.")
h('Actual v5 validation')
p(f"Status: {v['status']}. All {v['checks_passed']}/{v['checks_total']} checks passed with zero errors: 24 existing v4 checks rerun against its immutable baseline and 29 v5 checks for append-only expansion. All {tests['passed']}/{tests['total']} mutation tests passed, preserving the eight existing scenarios and adding tests for unsupported new quantities, no-synergy misclassification and reversed affected entity.")
p(f"An offline rebuild reproduced {rebuild['output_files_compared']} CSV/JSON outputs byte-for-byte. Validation covers stable IDs, duplicate contexts, identity keys, schema, foreign keys, bibliographic metadata, selection sources, units, source/claim diagnostics, study counting, null/reverse classifications, change logs and preservation. Manual source interpretation remains separate from these technical checks.")
h('Warnings and inherited limitations')
p(f"There are {v['warning_entries']} open warning entries across {v['distinct_warning_codes']} distinct codes. The original-nine selection history remains unresolved or only retrospectively documented. Apigenin/rutin attribution and the apigenin Cmax prose/table discrepancy remain flagged; no new source clarification was obtained. Quercetin and daidzein cooking/analyte links remain unvalidated. Earlier bibliographic resolutions remain recorded rather than silently reset.")
p('New limitations include missing abstract doses/sample sizes, parent-identity scope, uncertain food measurement provenance, source unit/percentage ambiguities, possible participant overlap and the unmet record target. Twenty-four new primary reports had concordant fresh Crossref titles; two lookups were unavailable and one new report had no supplied DOI. Primary MED identifiers remain verified. No independent second-reviewer or exhaustive cross-paper independence claim is made.')
h('Files created and recommended work')
p('The separate v5 folder contains the 26-compound registry, 118-row evidence CSV, 45-row incremental table, 80-report registry, selection and identity audits, 16-candidate decisions, search/screening logs, new and inherited claim audits, all-record review scopes, context comparison, processing audit, warning ledger, field-level registry and evidence logs, preservation hashes, validation/mutation/rebuild JSON, README, scripts, report and ZIP.')
p('The package is incremental and requires the supplied workspace for inherited sources and baseline validation. Next work should review deferred primary preparations, resolve reporting ambiguities and original selection records, extend uncapped source screening and obtain independent extraction review. Animal/cell and supplement results must remain distinct from ordinary dietary exposure and clinical risk.')

md=[]
for x in blocks:
    if x[0] in ['h','p']:md.append(('## ' if x[0]=='h' else '')+x[1])
    elif x[0]=='t':md+=['| '+' | '.join(x[1])+' |','| '+' | '.join('---' for _ in x[1])+' |']+['| '+' | '.join(row)+' |' for row in x[2]]
(O/'reports/CookRisk_StageB_v5_Report.md').write_text('\n\n'.join(md),encoding='utf8')
for name,file in [('Arial','arial.ttf'),('Arial-Bold','arialbd.ttf')]:pdfmetrics.registerFont(TTFont(name,'C:/Windows/Fonts/'+file))
body=ParagraphStyle('body',fontName='Arial',fontSize=10,leading=13,spaceAfter=7);head=ParagraphStyle('head',fontName='Arial-Bold',fontSize=13,leading=16,spaceAfter=8,spaceBefore=8);cell=ParagraphStyle('cell',fontName='Arial',fontSize=9,leading=11);th=ParagraphStyle('th',fontName='Arial-Bold',fontSize=9,leading=11,textColor=colors.white)
story=[]
for x in blocks:
    if x[0]=='break':story.append(PageBreak())
    elif x[0] in ['h','p']:story.append(Paragraph(html.escape(x[1]),head if x[0]=='h' else body))
    else:
        t=Table([[Paragraph(html.escape(str(c)),th if i==0 else cell) for c in row] for i,row in enumerate([x[1]]+x[2])],colWidths=[w*72 for w in x[3]],repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#333333')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F3F4F5')]),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#D9D9D9')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]));story+=[t,Spacer(1,8)]
def footer(c,d):c.setFont('Arial',8);c.drawRightString(558,27,f'CookRisk Stage B v5 | 14 October 2026 | Page {d.page}')
SimpleDocTemplate(str(O/'reports/CookRisk_StageB_v5_Report.pdf'),pagesize=(612,792),leftMargin=54,rightMargin=54,topMargin=40,bottomMargin=44).build(story,onFirstPage=footer,onLaterPages=footer)
(O/'README.md').write_text('''# CookRisk Stage B v5

Open reports/CookRisk_StageB_v5_Report.pdf first. The release contains 26 compounds, 118 evidence records, 58 drugs/probes and 80 unique primary PMIDs. Added 12 compounds, 45 records and 27 primary reports; no inherited evidence changes or removals. All 73 v4 records remain identical. Historical release-origin and review-date fields are intentionally retained on inherited records.

## Offline reproduction

Keep this incremental folder at stageB/release_v5_20261014 in the supplied workspace. No remote repository is needed. Existing stageB inputs, v2/v3/v4 registries and cached sources are required. Use Python 3.11+ (the bundled runtime is suitable):

```text
python stageB/release_v5_20261014/build.py
python stageB/release_v5_20261014/verify_rebuild.py
python stageB/release_v5_20261014/validate.py
python stageB/release_v5_20261014/report.py
python stageB/release_v5_20261014/package.py
```

Core scripts require the standard library. Report generation needs reportlab and Windows Arial; packaging PDF verification needs pypdf. Do not refresh audit/preservation_manifest.json to conceal changes. Offline rebuild uses saved snapshots and is tested byte-for-byte. Actual v4 validation functions are invoked read-only for baseline compatibility; their writing main routines are never invoked. Validation preserves eight prior mutation scenarios and adds three identified expansion risks.

Optional online acquisition sequence: collect.py, targeted.py, exact.py, supplement.py, food_sources.py. These cache public PubChem, MED/Crossref and accessible XML sources; caches can include failures and are not silently replaced. Run acquisition only in a new versioned workspace. Search logs retain exact queries/limits/URLs and distinguish incomplete screening. Exploratory web queries are listed separately. Source download availability alone is not scientific review.

## Schemas and review levels

The interaction CSV retains all 36 original fields. Stable IDs SB-0001 through SB-0073 are inherited; SB-0074 through SB-0118 are the fixed-order v5 additions. Do not reorder the curation list for future additions; reserve explicit IDs in a new version. Evidence_Type is Human pharmacokinetic, Controlled clinical, Animal or In vitro. Chrysin's uncontrolled pilot is Human pharmacokinetic, not Controlled clinical. Study_ID groups unique primary PMIDs and is not proof of independent trial participants.

Selection sources document a dated decision independently from interaction citations. Original-nine historical selection sources and dates remain unresolved or only retrospectively described. Newly selected compounds have current dated rationale and primary support. Seven new compounds reuse verified inventory identities; five use standalone external parent IDs. Naringenin CID 932 is a generic parent/racemate representation; natural (S)-naringenin CID 439246 is not silently substituted. No uncertain myricetin or naringenin master group is repaired by assigning literature. Naringenin is distinct from naringin. Existing daidzein/glycoside and quercetin/total-flavonol restrictions remain.

new_evidence_records.csv and claim_support_and_outcome_audit.csv cover 45 additions: 37 primary abstract extractions and eight selected full-text reviews. inherited_v4_claim_support.csv retains earlier claims; all_record_review_audit.csv covers all 118 rows with explicit review inheritance. Source locators state actual abstract or selected-section scope. Literal numeric checks complement manual review and do not prove meaning. No complete full-paper review or independent second reviewer is claimed.

Missing values are unknown or unextracted, never zero. No synergy is not no interaction. Nonsignificant means are not established effect directions. Metabolic ratios, inhibition constants, combination indices and AUC are different endpoints. CI in the fisetin record is a combination index, not a confidence interval. Reverse interactions retain the compound as Affected_Entity. Drug/probe counts include experimental transport substrates, not only prescribed medicines.

Processing and food-composition sources are separate from interaction studies and cannot establish native parent retention or meal exposure. Inherited food labels are not newly certified measurements. Supplement, injected animal and cell concentrations must not become clinical risk thresholds. No Stage A, outlier, Stage C or Stage D work is included.

## File map

- compound_registry.csv: 26 selected compounds; candidate_selection.csv: 16 decisions (12 selected, four deferred, zero rejected).
- stageB_food_drug_interactions_v5.csv: 118 rows; new_evidence_records.csv: 45 additions.
- study_registry.csv: 80 primary PMIDs; interaction_evidence_source_audit.csv: verification status.
- compound_selection_provenance_audit.csv and selection_sources.csv: decision lineage; original_nine_interaction_reference_map.csv: experimental citations, not historical selection triggers.
- identity_structure_audit.csv: stable identity keys and restrictions; processing_provenance_audit.csv: separate food/processing context.
- search_log.csv, exact_source_log.csv, food_processing_source_log.csv and screening_log.csv: capped discovery and adjudication states. Unreviewed candidates are not excluded.
- claim_support_and_outcome_audit.csv, inherited_v4_claim_support.csv and all_record_review_audit.csv: new versus inherited source scopes.
- context_comparison_audit.csv: differing drug/preparation/species contexts, not automatic direct contradictions.
- evidence_change_log.csv and registry_change_log.csv: every new evidence ID and registry field change.
- warning_resolution_ledger.csv: inherited unresolved limitations plus new issues; prior resolved warnings remain as history.
- file_inventory.csv and baseline_key_file_inventory.csv: actual paths, row counts, source fields and inspection status.
- audit/verified_v4_baseline.json, validation_report.json, mutation_tests.json, rebuild_verification.json and preservation_manifest.json: machine-readable checks.
- sources: public response snapshots; curation.py: explicit manual extraction; build.py/validate.py: reproducible release logic; reports: PDF and Markdown.

## Future additions

Create the next version without overwriting v5. Verify identity and food relevance, record a dated selection decision, cache exact primary identifiers and source locators, and preserve original experimental units and context. Require relevant drug/probe endpoints; exclude predictions and unverified review claims. Separate doses/endpoints only when genuinely different compound/drug/context experiments justify a record, and share primary Study_ID. Record nulls and incompatible contexts without pooling. Keep changes auditable, run the complete validation and mutation suite, verify deterministic rebuilding, and report actual counts plus unresolved limitations. The unmet 150-record target does not justify duplicate or speculative rows.
''',encoding='utf8')
print('Created report and README')
