"""Search supplied narrative files; a mention is not proof of historical selection."""
from pathlib import Path
import csv,re,json
from pypdf import PdfReader
from docx import Document
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[1]
names=['Berberine','Piperine','Curcumin','EGCG','Caffeine','Resveratrol','Genistein','Naringin','Capsaicin']
rows=[]
for folder in ['docs','literature','reports','stageB/reports','stageB/expansion_v2/reports','stageB/inputs','stageB/audit']:
    for p in sorted((ROOT/folder).rglob('*')):
        if p.suffix.lower() not in ['.md','.txt','.pdf','.docx'] or not p.is_file():continue
        status='text_read';text=''
        try:
            if p.suffix.lower()=='.pdf':text='\n'.join(page.extract_text() or '' for page in PdfReader(p).pages)
            elif p.suffix.lower()=='.docx':
                d=Document(p);text='\n'.join(x.text for x in d.paragraphs)+'\n'+'\n'.join(c.text for t in d.tables for row in t.rows for c in row.cells)
            else:text=p.read_text(encoding='utf-8-sig')
        except Exception as e:status='extraction_unavailable: '+str(e)
        hits=[n for n in names if n.lower() in text.lower()]
        selectionlines=[line.strip()[:600] for line in text.splitlines() if re.search(r'select|priorit|anchor|rationale',line,re.I) and any(n.lower() in line.lower() for n in names)]
        rows.append(dict(File=p.relative_to(ROOT).as_posix(),Inspection_Status=status,Characters_Extracted=len(text),Compound_Mentions=' | '.join(hits),Selection_Context_Excerpts=' || '.join(selectionlines[:8]),Interpretation='Mention/context search only; historical-source conclusion requires manual review, not keyword occurrence'))
with (OUT/'outputs/selection_document_search.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print(json.dumps({'documents_searched':len(rows),'with_anchor_mentions':sum(bool(r['Compound_Mentions']) for r in rows),'extraction_failures':[r['File'] for r in rows if r['Inspection_Status']!='text_read']},indent=2))
print('\n'.join(r['File']+'\n'+r['Selection_Context_Excerpts'] for r in rows if r['Selection_Context_Excerpts'] and not r['File'].startswith('stageB/')))
