from pathlib import Path
import csv,json,re,zipfile,xml.etree.ElementTree as ET,hashlib
from pypdf import PdfReader
O=Path(__file__).resolve().parent;R=O.parents[1]
names=['Berberine','Caffeine','Curcumin','EGCG','Piperine','Resveratrol','Genistein','Naringin','Capsaicin']
paths=[]
for base in ['docs','literature','reports']:
 paths.extend(p for p in (R/base).rglob('*') if p.is_file() and p.suffix.lower() in ['.md','.txt','.pdf','.docx'])
paths += [R/'stageB/reports/stageB_methodology.md',R/'stageB/scripts/curated_evidence.py',R/'stageB/scripts/build_stageB.py',R/'stageB/expansion_v2/scripts/build.py',R/'stageB/expansion_v2/reports/literature_search_methodology.md',R/'stageB/expansion_v2/reports/evidence_summary.md']
paths += [Path('C:/Users/dakshant/Downloads/CookRisk_BTP_Literature_Review_Assignment_2_FINAL_CORRECTED (1).docx'),Path('C:/Users/dakshant/.codex/attachments/61f53716-4c5f-40c2-bb72-0f48e09ebfee/Pasted text.txt'),Path('C:/Users/dakshant/.codex/attachments/978fc99e-50af-49e8-b345-b5213a62465d/Pasted text.txt')]
rows=[]
for p in paths:
 try:
  if p.suffix=='.pdf':text='\n'.join(x.extract_text() or '' for x in PdfReader(p).pages)
  elif p.suffix=='.docx':
   with zipfile.ZipFile(p) as z:text=' '.join(ET.fromstring(z.read('word/document.xml')).itertext())
  else:text=p.read_text(encoding='utf-8-sig')
  matches=[n for n in names if n.lower() in text.lower()];contexts=[]
  for m in re.finditer('select|priorit|anchor',text,re.I):
   s=text[max(0,m.start()-100):m.start()+300]
   if any(n.lower() in s.lower() for n in names):contexts.append(s.replace('\n',' '))
  rows.append(dict(File=str(p),SHA256=hashlib.sha256(p.read_bytes()).hexdigest(),Status='Text extracted and selection-context inspected',Characters=len(text),Mentions=' | '.join(matches),Selection_Excerpts=' | '.join(contexts[:8]),Historical_Interpretation='Mentions and workflow rules do not establish an original per-compound decision date or triggering primary reference'))
 except Exception as ex:rows.append(dict(File=str(p),SHA256='',Status=str(ex),Characters=0,Mentions='',Selection_Excerpts='',Historical_Interpretation='Access/extraction limitation'))
with (O/'outputs/historical_document_search.csv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
for r in rows:
 if r['Mentions']:print(r['File'],r['Mentions'],r['Selection_Excerpts'][:1700])
print('Historical materials inspected',len(rows))
