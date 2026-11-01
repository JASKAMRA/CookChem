"""Create concise report and maintenance guide from actual release outputs."""
from pathlib import Path
import csv,json,html
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
OUT=Path(__file__).resolve().parents[1]
def read(name):
    with (OUT/'outputs'/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
s=json.loads((OUT/'outputs/release_summary.json').read_text());v=json.loads((OUT/'audit/validation_report.json').read_text());tests=json.loads((OUT/'audit/validation_self_tests.json').read_text())
registry=read('compound_registry.csv');studies=read('study_registry.csv');docs=read('selection_document_search.csv');search=read('literature_search_log.csv')
blocks=[]
def h(t):blocks.append(('heading',t))
def p(t):blocks.append(('paragraph',t))
def table(head,rows,widths):blocks.append(('table',head,rows,widths))
def page(t):blocks.append(('page',));h(t)
h('CookRisk Stage B Compound Expansion Report')
p('Version 3  |  14 October 2026  |  Selection provenance and interaction evidence only')
p(f"This release adds {s['new_compounds']} compounds and {s['new_evidence_records']} records to the supplied 64-record Stage B database. The result is {s['total_evidence_records']} records for {s['total_compounds']} anchor compounds and {s['total_drugs']} drugs or probes, supported by {s['total_primary_reports']} primary reports. Selection documentation is kept separate from interaction citations. Missing historical selection sources remain unresolved.")
table(['Measure','Supplied v2','New v3'],[['Interaction records','64',str(s['total_evidence_records'])],['Anchor compounds','9',str(s['total_compounds'])],['Drugs or probes','34',str(s['total_drugs'])],['Primary reports by unique PMID','45',str(s['total_primary_reports'])],['Human PK plus controlled clinical','49 + 2','55 + 2'],['Animal plus in vitro','7 + 6','10 + 6']], [3.6,1.2,1.2])
h('Files available and inspected')
p(f"Work used the current folder only. No remote repository was required. The inventory inspected metadata and hashes for {s['source_files_inventoried']:,} relevant data, source and documentation files; a short inventory lists {s['key_files_inventoried']} key files individually with purpose, row count and source fields. Text was extracted from {len(docs)} supplied narrative documents with no extraction failures. This does not mean every cached candidate paper was fully screened.")
table(['Available material','Role and source information'],[['Expanded evidence 64 rows; study registry 45 rows','Primary interaction references and source cache links'],['Compound mapping and prioritization 198 rows each','Names, structures, identity status and selection context'],['Master dataset 1350 observations','Inherited food and cooking context; provenance not newly certified'],['Search logs, screening, DOI audits and source caches','Retrieval and evidence verification trail'],['Methods, reports, weekly logs and research PDFs','Selection history search and scientific context']], [2.65,3.35])
p('Outputs: file_inventory.csv contains the full listing; inventory_key_files.csv is the short handover inventory. Supplied inputs and existing releases were preserved. Stage A training, outlier handling, Stage C exposure and Stage D risk were outside scope.')

page('Compound selection provenance')
h('What can be established for the original nine')
p('Berberine, piperine, curcumin, EGCG and caffeine are documented as the initial five anchors. The initial methods describe a full inventory search, but no contemporaneous per-compound selection ledger or specific historical selection-paper trigger was found. Their original selection sources and addition dates remain unresolved.')
p('Resveratrol, genistein, naringin and capsaicin have an explicit v2 selection rationale: reliable exact or parent identity and useful primary human evidence. The v2 methodology specifically explains why low-frequency genistein and naringin were selected. However, a specific primary-paper trigger for each historical choice and the exact original addition date are not established. The 6 October release date is not substituted for a selection date.')
p('See compound_selection_provenance_audit.csv for all nine determinations and original_nine_interaction_reference_map.csv for their retained interaction PMIDs and DOIs. Those interaction references do not prove why a compound was originally chosen.')
h('Five new decisions documented in this release')
table(['Compound','Reason and supporting source','Rows'],[['Sulforaphane','Verified broccoli compound; human CYP3A probe trial PMID 23153560; processing support PMID 22471240','1'],['Apigenin','Verified dietary flavone; regimen-dependent animal drug disposition PMID 24369535; provisional preparation context PMID 24871039','2'],['Kaempferol','Verified dietary flavonol; animal tamoxifen and metabolite findings PMID 18338336','1'],['Daidzein','Soy aglycone; human theophylline and caffeine-probe study PMID 12756512; dietary/form context PMID 11285356','2'],['Quercetin','Dietary flavonol; human fexofenadine PMID 19221726 and midazolam PMIDs 21680781 and 25988261','3']], [1.05,4.35,.6])
p('Each current decision has a dated selection record, rationale, primary identifiers and identity source. Dietary relevance, human evidence where available, retention availability, identity confidence and feasibility were considered qualitatively; no numerical selection or risk score was invented.')
p('Sulforaphane, apigenin and kaempferol retain supplied molecular IDs and exact-identity mappings. Daidzein and quercetin receive standalone PubChem-based IDs after property and synonym verification. Daidzein is not substituted for daidzin or acetylated glycosides. Quercetin is not linked to the mixed quercetin/total-flavonol measurement group. Cooking coverage is limited and does not govern literature eligibility by itself.')

page('New evidence findings and research scope')
p('The nine new records SB-0065 through SB-0073 comprise six human PK/probe records and three animal records from eight primary reports. Same-report drug endpoints share a Study_ID. There are 47 numerical-outcome records overall, five newly added; these include metabolic ratios and are not all clinical effect sizes.')
h('Human evidence and tested nulls')
p('Sulforaphane: broccoli sprout preparation did not change cohort-wide basal CYP3A activity or attenuate rifampicin induction; a high-basal-activity subgroup had increased midazolam AUC. The overall null and subgroup finding remain together, with no extracted subgroup magnitude. The source enrolled 24 adults. [PMID 23153560]')
p('Daidzein: theophylline AUC increased about 34% after 200 mg twice daily for 10 days in a 20-person parallel trial. The same report found a caffeine metabolic-ratio change of -19.8 +/- 19.7% (P=0.009), not a caffeine AUC change. Ambiguous CI and baseline-day wording were flagged; disputed CIs were omitted. [PMID 12756512]')
p('Quercetin: fexofenadine AUC rose 55% and Cmax 68% in 12 subjects receiving 500 mg three times daily for seven days. Another study reported reduced midazolam exposure in CYP3A5*1 genotype groups. A separate 10-person study found a single-dose null and a repeated oral AUC GMR of 0.82 (90% CI 0.61-1.10), a nonsignificant trend; the three-person IV substudy tended oppositely. [PMIDs 19221726, 21680781, 25988261]')
h('Animal evidence and preparation limits')
p('Apigenin: acute versus 15-day treatment changed imatinib/metabolite disposition in rats, interpreted by the authors as regimen-dependent metabolic modulation. A separate paclitaxel abstract reports increased exposure under apigenin/rutin conditions, but separate versus combined group preparation is unresolved. That record is explicitly provisional for preparation attribution; no isolated-apigenin magnitude is assigned. [PMIDs 24369535, 24871039]')
p('Kaempferol: oral coadministration increased rat tamoxifen exposure, while 4-hydroxytamoxifen PK was unchanged. CYP3A/P-gp inhibition was proposed. Numerical effect magnitude was not extracted. This remains animal evidence. [PMID 18338336]')
h('Search and processing context')
p(f"Five title-focused Europe PMC queries retrieved the first 100 candidates each, followed by ten exact PMID verifications. Web discovery was followed by cached primary metadata checks. Broad retrieval returned {sum(int(r['Retrieved']) for r in search if r['Compound']!='exact source verification')} candidates before deduplication; unreviewed candidates are not labelled excluded. This is a bounded expansion, not a systematic review.")
p('One additional processing publication describes thermal effects on sulforaphane formation in broccoli. It supports selection context but is not an interaction row, a universal retention coefficient or Stage C calculation. A separate isoflavone publication supports dietary and chemical-form context. These two reports are outside the 53 interaction-report count.')

page('Validation handover and unresolved work')
h('Validation results')
p(f"Status: {v['status']}. All {v['checks_passed']} of {v['checks_total']} checks passed with zero errors and {len(v['warnings'])} warning categories. All {tests['passed']} mutation tests passed. Hash checks confirmed that all 1,259 supplied files in the preservation manifest are unchanged, and the original 64 evidence rows match exactly.")
p('Checks cover duplicate IDs and identity keys, duplicate experimental contexts, schema preservation, compound links, PMID/DOI format, cached title/author/year/DOI consistency, selection citations, classifications, unit or ratio context and source-support ledgers. All 53 primary-report metadata records were concordant with cached MED records. Five new Crossref lookups were concordant; three were unavailable. Existing v2 Crossref statuses are retained, not described as new verification.')
p('New numerical outcomes were manually compared with source abstracts and checked using source excerpts and numeric diagnostics. These checks cannot automatically prove scientific semantics. The 64 inherited outcome extractions were preserved and their metadata rechecked; their full-text quantitative claims were not independently re-extracted in v3.')
h('Main files created')
p('outputs contains the 73-row versioned evidence release, nine new rows, 14-compound registry, selection-source records, provenance and source audits, 53-report registry, original-nine reference map, claim support and outcome audits, inventory, candidate decisions, search/screening logs, conflict synthesis and release summary. audit contains machine-readable validation, six self-tests and preservation hashes. sources contains public response snapshots; scripts contains offline builders and validation.')
p('README.md explains usage and future additions. This PDF and its Markdown counterpart summarize the release. The versioned ZIP packages the new folder; baseline inputs and inherited caches remain in the supplied workspace and are needed for full offline rebuild and preservation checks.')
h('Unresolved issues and recommended work')
p('Recover contemporaneous selection notes for the original nine; preserve unknown history until documented. Obtain full text to resolve the apigenin/rutin groups and missing doses or sample sizes. Resolve standalone quercetin and daidzein retention provenance before any later linkage. Review the inherited identity and food-source flags; do not merge aliases, salts, aglycones and mixed analytes by name alone.')
p('Expand screening beyond capped results, obtain an independent extraction review, and recheck inaccessible DOI metadata. Null findings apply to tested conditions; no retained row does not establish no interaction. Supplement and animal doses cannot be interpreted as ordinary food risk. No Stage A modification, exposure estimation or risk scoring was performed.')
h('Primary references for the new interaction records')
for r in studies:
    if r['PMID'] in {'23153560','24871039','24369535','18338336','12756512','19221726','21680781','25988261'}:
        p(f"PMID {r['PMID']} | DOI {r['DOI']} | https://pubmed.ncbi.nlm.nih.gov/{r['PMID']}/")

md=[]
for b in blocks:
    if b[0]=='heading':md.append('## '+b[1])
    elif b[0]=='paragraph':md.append(b[1])
    elif b[0]=='table':md+=['| '+' | '.join(b[1])+' |','| '+' | '.join('---' for _ in b[1])+' |']+['| '+' | '.join(row)+' |' for row in b[2]]
    else:md.append('---')
(OUT/'reports/CookRisk_StageB_v3_Expansion_Report.md').write_text('\n\n'.join(md),encoding='utf8')
for font,file in [('Arial','arial.ttf'),('Arial-Bold','arialbd.ttf')]:pdfmetrics.registerFont(TTFont(font,'C:/Windows/Fonts/'+file))
styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='BodyCustom',fontName='Arial',fontSize=10,leading=13,spaceAfter=7));styles.add(ParagraphStyle(name='HeadCustom',fontName='Arial-Bold',fontSize=13,leading=16,spaceBefore=9,spaceAfter=7));styles.add(ParagraphStyle(name='CellCustom',fontName='Arial',fontSize=9,leading=11));styles.add(ParagraphStyle(name='CellHead',fontName='Arial-Bold',fontSize=9,leading=11,textColor=colors.white))
story=[]
for b in blocks:
    if b[0]=='page':story.append(PageBreak())
    elif b[0] in ['heading','paragraph']:story.append(Paragraph(html.escape(b[1]),styles['HeadCustom' if b[0]=='heading' else 'BodyCustom']))
    else:
        data=[[Paragraph(html.escape(str(x)),styles['CellHead' if i==0 else 'CellCustom']) for x in row] for i,row in enumerate([b[1]]+b[2])]
        t=Table(data,colWidths=[x*72 for x in b[3]],repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#333333')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F3F4F5')]),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#D9D9D9')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]));story +=[t,Spacer(1,9)]
def foot(c,d):
    c.setFont('Arial',8);c.drawRightString(558,30,f'CookRisk Stage B v3 | 14 October 2026 | Page {d.page}')
SimpleDocTemplate(str(OUT/'reports/CookRisk_StageB_v3_Expansion_Report.pdf'),pagesize=(612,792),rightMargin=54,leftMargin=54,topMargin=42,bottomMargin=44).build(story,onFirstPage=foot,onLaterPages=foot)
readme='''# CookRisk Stage B release v3 20261014

Open reports/CookRisk_StageB_v3_Expansion_Report.pdf first. The main table is outputs/stageB_food_drug_interactions_v3.csv. Original supplied files are not overwritten. This is Stage B evidence only.

## What changed

Added five compounds and nine evidence rows, SB-0065 through SB-0073. All 64 baseline rows and all 36 original columns are preserved. The result has 73 rows, 14 anchors, 36 drugs/probes and 53 primary PMIDs. Human records: 55 PK/probe plus two controlled clinical; animal 10; in vitro six. One apigenin/rutin record remains provisional for preparation attribution.

Selection sources are in selection_sources.csv and the compound registry; interaction sources are in study_registry.csv. An interaction paper is not evidence of historical selection. For the original five anchors, original selection sources remain unresolved; the four v2 additions have a documented general rationale but not a specific historical primary-paper trigger. Unknown original dates stay blank.

## Rebuild and validate offline

Keep this folder at stageB/expansion_v3_20261014 in the supplied workspace. The scripts do not require Git or the original remote repository. They discover their paths relative to their own saved location. They read the available stageB/inputs, stageB/outputs, stageB/expansion_v2 and inherited source caches. The package is an incremental release, not a replacement for the supplied workspace. Python 3.11+ standard library suffices for core build and validation; document search additionally needs pypdf and python-docx; PDF generation needs reportlab and Arial fonts on Windows.

Run in order from the workspace root:

```text
python stageB/expansion_v3_20261014/scripts/audit_selection_documents.py
python stageB/expansion_v3_20261014/scripts/build_release.py
python stageB/expansion_v3_20261014/scripts/validate_release.py
python stageB/expansion_v3_20261014/scripts/test_validation.py
python stageB/expansion_v3_20261014/scripts/document_release.py
```

Use the supplied Python runtime if python is not on PATH. collect_sources.py is optional online collection, not needed for offline reproduction. Existing cache files, including recorded failures, are not silently replaced. A new retrieval attempt should use a new dated cache or explicitly versioned collection script. The supplied-file hash manifest is created only once and is never refreshed to conceal changes.

## Add a compound or evidence record

1. Create the next versioned output folder; preserve supplied releases. Reuse a verified stable compound ID where chemically appropriate. For a genuinely new canonical chemical, reserve an explicit ID and record PubChem CID, synonyms, structure, InChIKey and identity source. Do not merge salt, stereoisomer, glycoside or mixed-analyte groups by name alone.
2. Record a dated selection decision, dietary relevance, human/preclinical evidence availability, retention coverage, identity confidence and feasibility. Add each supporting paper and its actual role to the selection-source ledger. Leave unavailable historical dates and references blank with an explicit unresolved status.
3. Save exact search queries, search date, caps, results and source responses. Record incomplete screening honestly. Cache primary MED metadata/abstract or verified full text and an exact locator. Check bibliographic metadata and correction/retraction notices where available.
4. Append curated records to curation.py with primary identifiers, preparation, co-interventions, doses, population, drug endpoint, direction, numerical units, uncertainty, null/conflict context and limitations. Update the registry specifications. Reserve the next unused SB ID; never renumber inherited rows. This builder assigns SB-0065 onward in fixed list order; do not reorder existing entries. For later releases, use an explicit ID map rather than inserting into this list.
5. For numerical claims, preserve reported endpoint, units, p-values and intervals; add source support. Do not convert metabolic ratios into AUC or animal/cell findings into human outcomes. Retain no-effect results and context differences. Missing values are not zero. Mechanisms must be labelled proposed unless directly supported.
6. Rebuild and run validation plus mutation tests. Resolve errors. Retain provenance gaps and reviewed source limitations as warnings; never relabel PASS_WITH_WARNINGS as complete source adjudication. Review new source claims manually because literal token checks do not establish scientific meaning. Update documentation using generated counts.

## Important limitations

Standalone quercetin CHEM-PUBCHEM-5280343 is intentionally not linked to the mixed master group MOL-FDB10E6B0C4171D1. Daidzein CHEM-PUBCHEM-5281708 has no exact master aglycone group; daidzin and acetyldaidzin are different compounds. Three other added compounds reuse inherited exact mappings. Original-nine selection history, apigenin/rutin group preparation, some abstract doses/sample sizes, inherited food provenance and unavailable Crossref lookups remain unresolved. Baseline numerical outcomes were retained, not independently re-extracted. No complete cross-paper trial independence audit, systematic review, second-reviewer adjudication, Stage A training, Stage C or Stage D work is claimed.

## File map

- outputs/file_inventory.csv: full metadata and row-count inventory; inventory_key_files.csv: short key-file inventory.
- outputs/selection_document_search.csv: text search of supplied narrative documents.
- outputs/compound_registry.csv, selection_sources.csv and compound_selection_provenance_audit.csv: identity, current decisions and unresolved history.
- outputs/original_nine_interaction_reference_map.csv: retained references, explicitly separate from selection history.
- outputs/stageB_food_drug_interactions_v3.csv and new_evidence_records.csv: full and incremental evidence.
- outputs/study_registry.csv and interaction_evidence_source_audit.csv: primary references and verification scope.
- outputs/claim_support_ledger.csv and outcome_validation_audit.csv: source support and extraction limitations.
- outputs/literature_search_log.csv, source_screening_log.csv and inventory_candidate_decisions.csv: search and candidate decisions.
- outputs/conflict_synthesis.csv, processing_selection_context.csv and release_summary.json: context and actual totals.
- audit/validation_report.json and validation_self_tests.json: reproducible checks.
- audit/supplied_file_manifest.json: unchanged source-file hashes. sources: raw public snapshots. scripts: collection, extraction, build, validation and report generation.
'''
(OUT/'README.md').write_text(readme,encoding='utf8')
print('Created concise PDF report, Markdown report and README')
