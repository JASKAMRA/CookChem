from pathlib import Path
import json,csv,html
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
O=Path(__file__).resolve().parent
def load(p):return json.loads((O/p).read_text(encoding='utf8'))
def read(p):
    with (O/p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
s=load('outputs/release_summary.json');v=load('audit/validation_report.json');b=load('audit/verified_v3_baseline.json');tests=load('audit/mutation_tests.json');manifest=load('audit/preservation_manifest.json')
blocks=[]
def h(t):blocks.append(('h',t))
def p(t):blocks.append(('p',t))
def table(head,rows,widths):blocks.append(('t',head,rows,widths))
def page(t):blocks.append(('break',));h(t)
h('CookRisk Stage B v4 Release Report')
p('14 October 2026 | Provenance resolution and evidence verification')
p('V4 improves the supplied v3 evidence release without forcing additional compounds or records. All 14 compounds, 73 records, 36 drugs/probes and 53 primary PMIDs remain. One record, SB-0067, has nine fields corrected or completed from primary full text. No records or compounds were added or removed; no bibliographic metadata fields required correction. No Stage A training, outlier analysis, exposure estimation or risk scoring was performed.')
table(['Measure','Verified v3','Final v4'],[['Compounds / interaction records','14 / 73','14 / 73'],['Drugs or probes / primary PMIDs','36 / 53','36 / 53'],['Human PK / controlled clinical','55 / 2','55 / 2'],['Animal / in vitro','10 / 6','10 / 6'],['Records with numerical outcomes','47','48'],['Original v2 rows preserved exactly','64','64']], [3.4,1.3,1.3])
h('Baseline verification and inventory')
p('The actual v3 CSV, registry, validation report and mutation-test report match the reported baseline counts. V3 recorded 25/25 checks, zero errors and 6/6 mutation tests. One reporting discrepancy was found: its nine warning entries use eight distinct warning codes, because historical selection provenance occurs twice. V4 distinguishes entries from distinct categories.')
p(f"The new inventory records filename, purpose, CSV row counts, source fields, inspection level and hash. The preservation manifest covers {len(manifest):,} supplied files, including v3 files and packages found under the inspected project directories. The original v3 input manifest is checked separately. No supplied release was overwritten. Inspection of a file's metadata is not a claim that its full text or every outcome was reviewed.")
h('Verification levels')
table(['V4 record review scope','Records'],[['Primary metadata only; inherited outcomes not re-extracted','62'],['Primary abstracts rechecked for the v3 additions','8'],['Selected inherited full-text outcome checks','2'],['Selected full-text re-extraction and correction','1']], [5.25,.75])
p('Primary source metadata were rechecked for all 53 reports. The two inherited full-text checks concern saved endoxifen outcomes; they do not establish whole-paper re-extraction. Studies are grouped by PMID, not counted as independent trials for each row.')

page('Compound provenance and chemical identity')
h('Original nine selection history')
p('Berberine, piperine, curcumin, EGCG and caffeine remain documented as the initial five anchors. Available methods establish a general inventory search but do not supply a contemporaneous per-compound selection ledger, historical paper trigger or exact selection date. These gaps remain unresolved.')
p('Resveratrol, genistein, naringin and capsaicin have a documented v2 rationale based on reliable exact/parent identity and useful primary human evidence. Low-frequency genistein and naringin were explicitly justified. Specific historical paper triggers and original selection dates remain unestablished. The available documentation is retrospective; release dates are not substituted for selection dates.')
p('The updated provenance audit covers all 14 compounds. The original-nine interaction-reference map is preserved separately. Interaction PMIDs/DOIs identify retained experimental evidence, not historical reasons for compound selection. External literature cannot recover missing personal project-selection notes.')
h('Five v3 additions')
p('Sulforaphane, apigenin, kaempferol, daidzein and quercetin retain stable IDs, canonical names, aliases, identity information, rationale, selection references, evidence coverage and provenance status. Their dated v3 selection decisions are available and were rechecked against supporting primary snapshots. Identity and dietary/interaction rationales remain distinct from later retention applicability.')
p('Daidzein remains an aglycone and is not merged with daidzin, acetyldaidzin or other glycosides. Standalone quercetin remains separate from the mixed quercetin/total-flavonol measurement group. The 15 mixed-group master rows and their reported DOIs are listed for further primary-source checking; none is assigned to standalone quercetin by this release.')
h('Cooking and processing provenance')
p('Two additional primary processing full texts were reviewed for methods and analyte scope. The daidzein-context study hydrolyzes glycosylated isoflavones before assay, so its result is not automatically native free-daidzein retention. The onion study distinguishes conjugates, total flavonols and weight-basis effects, which cannot certify the mixed master group. Both support processing context only; no new retention coefficient or master link was created.')
p('Sources: Traditional and Domestic Cooking Dramatically Reduce Estrogenic Isoflavones in Soy Foods, PMC11011382, methods/sample preparation; Influence of Cooking Methods on Onion Phenolic Compounds Bioaccessibility, PMC8151956, analytical methods and sections 3.2-3.3. Their DOI and cache paths are in processing_provenance_audit.csv. Neither publication is counted among the 53 interaction reports.')

page('Evidence verification and justified correction')
h('SB-0067 apigenin and imatinib')
p('Primary full text PMC3863468 supplied missing methods: 20 male Sprague-Dawley rats, four groups with n=5 each, and imatinib 30 mg/kg after apigenin pretreatment. Apigenin regimens were 165 mg/kg for 15 days, single 165 mg/kg or single 252 mg/kg. Preparation, direction, limitations and source locator were updated alongside the numerical outcome.')
table(['Imatinib AUC to infinity','Mean plus or minus SD in mg h per L'],[['Control','90.988 +/- 11.585'],['Repeated apigenin 165 mg/kg','68.805 +/- 7.432'],['Single apigenin 165 mg/kg','127.514 +/- 12.332'],['Single apigenin 252 mg/kg','114.502 +/- 8.634']], [3.4,2.6])
p('Table 1 marks each active group P<0.05 versus control. Repeated treatment lowered exposure; single treatment increased it. Results prose says acute Cmax decreased, while Table 1 shows an increase. That inconsistency is flagged and Cmax interpretation withheld. No human conclusion or effect-size pooling was made. Source: PMID 24369535, DOI 10.1155/2013/789184; Experimental 2.1/2.5 and Table 1.')
h('Apigenin and rutin attribution remains provisional')
p('The primary publisher page for PMID 24871039, DOI 10.1007/s13318-014-0203-z, exposes its abstract but identifies the full article as subscription content. The abstract still does not establish separate versus combined apigenin/rutin groups. SB-0066 remains a provisional preparation context; no isolated-apigenin numerical magnitude is assigned. A preview check is not full-text review.')
h('Other v3 additions and inherited outcomes')
p('All nine actual v3 addition IDs SB-0065 through SB-0073 were inspected. Eight remain abstract-level reviews; missing details stay explicit. Sulforaphane retains its cohort null and subgroup finding; daidzein retains metabolic ratios separately from drug AUC and disputed CIs are withheld; quercetin retains genotype, route and regimen distinctions, including a nonsignificant interval crossing 1.')
p('The saved curcumin/endoxifen outcomes SB-0016 and SB-0017 agree with inherited full-text PMC6468355 Table 2: -7.7% (95% CI -15.4 to +0.7; p=0.07) for curcumin alone and -12.4% (-21.9 to -1.9; p=0.02) with piperine. These rows remain byte-for-byte equivalent at the field level. The remaining 62 original baseline rows were not independently re-extracted in v4.')

page('Warnings validation and reproducibility')
h('Warning resolution')
p('The ledger retains all nine v3 warning entries and adds the new source table/prose discrepancy. Twelve previously unavailable Crossref title lookups were successfully recovered. Inherited full-text scope and retention provenance were partially addressed. Historical selection sources, missing DOI fields for PMIDs 18928093 and 22512082, apigenin/rutin attribution, daidzein abstract ambiguity and bounded-review limitations remain explicit.')
p(f"V4 has {v['remaining_warning_entries']} open warning entries under {v['remaining_distinct_warning_codes']} distinct codes. This is not a clean scientific-adjudication claim. The source table/prose warning replaces no historical warning; it is separately recorded. Fresh bibliographic title verification does not establish numerical correctness.")
h('Actual v4 technical validation')
p(f"Status {v['status']}: {v['checks_passed']}/{v['checks_total']} checks passed, {len(v['errors'])} errors. Mutation tests passed {tests['passed']}/{tests['total']}: six existing v3 scenarios were rerun through the supplied validation function read-only, plus two v4 tests for corrected-claim tampering and significance overclaim. V4 did not simply reuse the old validation results.")
p('Checks cover schema, identifiers, duplicate contexts and structures, classifications, foreign keys, references, units/ratio context, current selection sources, unknown dates, source-to-claim matching, actual-source numeric diagnostics, change-log completeness, nonsignificant-interval interpretation, Crossref recovery and preservation hashes. Literal numeric checks support manual review and cannot prove endpoint semantics by themselves.')
p(f"All {len(manifest):,} manifest-listed files and the original v3 preservation manifest passed hash checks. The original 64 rows remain unchanged; only SB-0067 differs from v3 and all nine changed fields are recorded. Newly reviewed claims and inherited claims carry separate review levels.")
h('Files and reproducible execution')
p('The new v4 folder contains the registry, versioned evidence CSV, all-14 provenance audit, source and outcome audits, primary registry, original-nine reference map, field-level change log, warning ledger, processing audit, mixed-group source inventory, validation JSON, mutation results, inventory and hashes, targeted acquisition and screening logs, README, this report and build/validation/package scripts. Source cache paths can reference immutable supplied files.')
p('Run build.py, validate.py, report.py and package.py from this new folder using Python. Core build/validation use standard libraries; PDF generation uses reportlab and Arial. Full reproduction requires the supplied workspace and inherited v3 caches. collect.py is optional online acquisition, not required for offline validation. The package is incremental rather than a replacement for the workspace.')
h('Remaining work')
p('Recover contemporaneous selection notes, obtain lawful access to the paclitaxel full text, resolve primary analyte provenance for mixed cooking data and request source clarification for reporting inconsistencies. Extend independent extraction review where needed. Null findings remain context-specific; no database row means no qualifying retained evidence, not no possible interaction. No additional interaction record was scientifically necessary for this pass.')

md=[]
for x in blocks:
    if x[0] in ['h','p']:md.append(('## ' if x[0]=='h' else '')+x[1])
    elif x[0]=='t':md+=['| '+' | '.join(x[1])+' |','| '+' | '.join('---' for _ in x[1])+' |']+['| '+' | '.join(r)+' |' for r in x[2]]
(O/'reports/CookRisk_StageB_v4_Report.md').write_text('\n\n'.join(md),encoding='utf8')
for name,file in [('Arial','arial.ttf'),('Arial-Bold','arialbd.ttf')]:pdfmetrics.registerFont(TTFont(name,'C:/Windows/Fonts/'+file))
body=ParagraphStyle('body',fontName='Arial',fontSize=10,leading=13,spaceAfter=8);head=ParagraphStyle('head',fontName='Arial-Bold',fontSize=13,leading=16,spaceBefore=8,spaceAfter=8);cell=ParagraphStyle('cell',fontName='Arial',fontSize=9,leading=12);th=ParagraphStyle('th',fontName='Arial-Bold',fontSize=9,leading=12,textColor=colors.white)
story=[]
for x in blocks:
    if x[0]=='break':story.append(PageBreak())
    elif x[0] in ['h','p']:story.append(Paragraph(html.escape(x[1]),head if x[0]=='h' else body))
    else:
        t=Table([[Paragraph(html.escape(str(c)),th if i==0 else cell) for c in row] for i,row in enumerate([x[1]]+x[2])],colWidths=[w*72 for w in x[3]],repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#333333')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F3F4F5')]),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#D9D9D9')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]));story+=[t,Spacer(1,9)]
def foot(c,d):c.setFont('Arial',8);c.drawRightString(558,27,f'CookRisk Stage B v4 | Page {d.page}')
SimpleDocTemplate(str(O/'reports/CookRisk_StageB_v4_Report.pdf'),pagesize=(612,792),leftMargin=54,rightMargin=54,topMargin=42,bottomMargin=44).build(story,onFirstPage=foot,onLaterPages=foot)
(O/'README.md').write_text('''# CookRisk Stage B v4

Start with reports/CookRisk_StageB_v4_Report.pdf. The main output is outputs/stageB_food_drug_interactions_v4.csv. There are 14 compounds, 73 records, 36 drugs/probes and 53 primary PMIDs. No additions/removals were forced. SB-0067 alone has nine documented field changes; all original 64 rows are unchanged. V3 and supplied inputs are immutable.

## Offline reproduction

Keep this incremental release at stageB/release_v4_20261014 in the supplied workspace. No Git repository is required. The actual supplied stageB/expansion_v3_20261014 and its source dependencies are required. Run with Python 3.11+:

```text
python stageB/release_v4_20261014/build.py
python stageB/release_v4_20261014/validate.py
python stageB/release_v4_20261014/report.py
python stageB/release_v4_20261014/package.py
```

Build and validation need the standard library; report.py needs reportlab and Windows Arial fonts. collect.py performs optional public online retrieval. It caches successful responses, preserves retrieval errors and does not supply evidence merely by downloading it. Do not refresh the preservation manifest to conceal changes. Validation calls the v3 validation function read-only; it does not invoke its writing main routine. Supplied v3 files are never rewritten.

## Schemas and provenance rules

The evidence CSV retains all 36 supplied columns and stable SB IDs. Blank means unavailable or unextracted, never zero. Evidence_Type is Human pharmacokinetic, Controlled clinical, Animal or In vitro. PMID-based Study_ID groups reports, not necessarily independent trials. Preparation, co-compounds, dose, population, endpoint, units, uncertainty and limitations remain source-specific. Mechanisms are proposed unless demonstrated in the relevant experiment. Do not pool incompatible endpoints or infer meal exposure or risk.

The compound registry retains stable IDs and aliases and adds v4 review fields. Selection sources and interaction references are separate. Original-nine selection dates remain unknown; release dates are not historical addition dates. V3 additions have dated decision records. Daidzein remains separate from glycosides; standalone quercetin remains separate from mixed total-flavonol observations. Processing publications are outside the interaction count and establish no automatic master retention links.

## Audits and source levels

record_source_review_audit.csv records all 73 review levels: 62 metadata-only inherited outcomes, eight abstracts, two selected inherited full-text checks and one selected full-text re-extraction. claim_support_and_outcome_audit.csv preserves exact claims and source locators. evidence_change_log.csv documents every changed field. warning_resolution_ledger.csv retains all v3 warning entries plus the new Cmax discrepancy. Eight distinct open codes cover nine entries. PASS_WITH_WARNINGS is technical consistency, not scientific certainty.

The all-14 provenance audit, original-nine reference map, processing provenance audit and quercetin mixed-group source inventory document unresolved identity/source issues. The full text of the apigenin/rutin paclitaxel article was unavailable; the publisher preview does not resolve individual attribution. Retrieved processing studies use hydrolysis or conjugate/total-analyte measures; they do not validate native parent retention.

## Future changes

Create a new version folder. Reserve explicit new stable IDs only when identity and primary evidence justify them. Record dated selection decisions independently from interaction evidence. Save exact acquisition queries/URLs and locators. Preserve source units, CI, p-values and null findings; missing values stay missing. Compare abstract and tables, flag conflicting prose and distinguish human from preclinical contexts. Append a field-level change ledger rather than silently altering inherited records. Add a mutation test only for a demonstrated validation gap. Run actual validation and report counts from final files. Keep inherited outcome review scope explicit. Do not implement Stage A retraining, outlier analysis, Stage C or Stage D here.
''',encoding='utf8')
print('Created v4 report and README')
