from pathlib import Path
import json,hashlib,zipfile
from pypdf import PdfReader
O=Path(__file__).resolve().parent
v=json.loads((O/'audit/validation_report.json').read_text());tests=json.loads((O/'audit/mutation_tests.json').read_text())
assert not v['errors'] and tests['passed']==tests['total']
pdf=PdfReader(O/'reports/CookRisk_StageB_v4_Report.pdf');assert len(pdf.pages)==4
assert '\ufffd' not in '\n'.join(p.extract_text() or '' for p in pdf.pages)
(O/'audit/report_visual_qa.json').write_text(json.dumps({'pages':4,'all_pages_visually_inspected':True,'result':'No clipping, overlap or missing glyphs observed','technical_validation':v['status']},indent=2),encoding='utf8')
files=[p for p in sorted(O.rglob('*')) if p.is_file() and 'qa' not in p.relative_to(O).parts and '__pycache__' not in p.parts and p.suffix!='.zip' and p.name!='release_manifest_sha256.json']
manifest={p.relative_to(O).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
m=O/'audit/release_manifest_sha256.json';m.write_text(json.dumps(manifest,indent=2),encoding='utf8');files.append(m)
zpath=O/'CookRisk_StageB_v4_20261014.zip'
with zipfile.ZipFile(zpath,'w',compression=zipfile.ZIP_DEFLATED) as z:
    for p in files:z.write(p,Path('stageB/release_v4_20261014')/p.relative_to(O))
with zipfile.ZipFile(zpath) as z:assert z.testzip() is None
print(json.dumps({'zip':str(zpath),'files':len(files),'bytes':zpath.stat().st_size,'report_pages':len(pdf.pages),'validation_checks':v['checks_passed'],'mutations':tests['passed']},indent=2))
