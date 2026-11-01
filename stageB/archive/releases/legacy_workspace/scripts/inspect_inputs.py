import csv,json,hashlib
from pathlib import Path
from collections import Counter
from pypdf import PdfReader
from docx import Document
ROOT=Path(__file__).resolve().parents[1]; (ROOT/'audit').mkdir(exist_ok=True)
D=Path('C:/Users/dakshant/Downloads')
paths=[D/'cookchem_master_expanded_round11.csv',D/'stageA_oof_predictions.csv',D/'CookRisk_StageA_Benchmark_Report.pdf',D/'CookRisk_BTP_Literature_Review_Assignment_2_FINAL_CORRECTED (1).docx']
manifest=[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in paths]
(ROOT/'audit/input_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
pdf=PdfReader(paths[2]); (ROOT/'audit/stageA_report_extracted.txt').write_text('\n'.join(p.extract_text() for p in pdf.pages),encoding='utf-8')
doc=Document(paths[3]); text='\n'.join(p.text for p in doc.paragraphs)+'\n'+'\n'.join(' | '.join(c.text for c in r.cells) for t in doc.tables for r in t.rows)
(ROOT/'audit/literature_review_extracted.txt').write_text(text,encoding='utf-8')
a=list(csv.DictReader(paths[0].open(encoding='utf-8-sig'))); o=list(csv.DictReader(paths[1].open(encoding='utf-8-sig')))
index={r['Record_ID']:r for r in a}; selected=[r for r in o if r['Model']=='ExtraTrees_reference']
bad=[r for r in selected if r['Record_ID'] not in index or index[r['Record_ID']]['Canonical_Molecular_ID']!=r['Canonical_Molecular_ID']]
targetbad=[r for r in selected if r['Record_ID'] in index and index[r['Record_ID']]['Retention_Final'] and abs(float(index[r['Record_ID']]['Retention_Final'])-float(r['actual']))>1e-6]
summary={'master_rows':len(a),'nonblank_master_groups':len({r['Canonical_Molecular_ID'] for r in a if r['Canonical_Molecular_ID']}),'missing_molecular_id_rows':sum(not r['Canonical_Molecular_ID'] for r in a),'unique_names':len({r['Compound_Name'] for r in a}),'unique_food_names':len({r['Food_Name'] for r in a}),'OOF_selected_rows':len(selected),'OOF_selected_groups':len({r['Canonical_Molecular_ID'] for r in selected}),'join_mismatches':len(bad),'target_mismatches':len(targetbad),'duplicate_master_record_ids':sum(v-1 for v in Counter(r['Record_ID'] for r in a).values() if v>1),'oof_only_groups':sorted({r['Canonical_Molecular_ID'] for r in selected}-{r['Canonical_Molecular_ID'] for r in a}),'master_only_groups':sorted({r['Canonical_Molecular_ID'] for r in a if r['Canonical_Molecular_ID']}-{r['Canonical_Molecular_ID'] for r in selected})}
(ROOT/'audit/inventory_statistics.json').write_text(json.dumps(summary,indent=2),encoding='utf-8'); print(json.dumps(summary,indent=2))
