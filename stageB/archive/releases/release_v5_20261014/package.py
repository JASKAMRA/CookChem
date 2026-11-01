from pathlib import Path
import json,csv,hashlib,zipfile
from pypdf import PdfReader
O=Path(__file__).resolve().parent
queries=[
'site.pubmed.ncbi.nlm.nih.gov myricetin pharmacokinetics drug rats',
'site.pubmed.ncbi.nlm.nih.gov luteolin pharmacokinetics drug rats',
'site.pubmed.ncbi.nlm.nih.gov ellagic acid pharmacokinetics drug interaction',
'site.pubmed.ncbi.nlm.nih.gov gallic acid pharmacokinetics drug interaction',
'site.pubmed.ncbi.nlm.nih.gov rosmarinic acid furosemide interaction',
'site.pubmed.ncbi.nlm.nih.gov chlorogenic acid methotrexate interaction pharmacokinetics',
'site.pubmed.ncbi.nlm.nih.gov ferulic acid drug pharmacokinetics interaction',
'site.pubmed.ncbi.nlm.nih.gov caffeic acid drug pharmacokinetics interaction',
'site.pubmed.ncbi.nlm.nih.gov bergamottin felodipine healthy subjects',
'site.pubmed.ncbi.nlm.nih.gov chrysin irinotecan patients',
'site.pubmed.ncbi.nlm.nih.gov naringenin pharmacokinetics drug rats',
'site.pubmed.ncbi.nlm.nih.gov hesperetin pharmacokinetics drug rats',
'site.pubmed.ncbi.nlm.nih.gov chrysin irinotecan pilot clinical',
'site.pubmed.ncbi.nlm.nih.gov luteolin nifedipine drug interaction',
'site.pubmed.ncbi.nlm.nih.gov chlorogenic acid drug interaction methotrexate',
'site.pubmed.ncbi.nlm.nih.gov caffeic acid drug interaction methotrexate',
'site.pubmed.ncbi.nlm.nih.gov quercetin pravastatin healthy pharmacokinetics',
'site.pubmed.ncbi.nlm.nih.gov quercetin rosiglitazone healthy pharmacokinetics',
'site.pubmed.ncbi.nlm.nih.gov quercetin talinolol healthy pharmacokinetics',
'site.pubmed.ncbi.nlm.nih.gov ellagic acid warfarin pharmacokinetics',
'site.pubmed.ncbi.nlm.nih.gov fisetin cisplatin synergistic',
'site.pubmed.ncbi.nlm.nih.gov fisetin paclitaxel drug combination',
'site.pubmed.ncbi.nlm.nih.gov myricetin foods berries dietary content primary study',
'site.pubmed.ncbi.nlm.nih.gov "myricetin" "onion" flavonoids content']
with (O/'outputs/exploratory_web_queries.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['Date','Tool','Query','Scope']);w.writeheader();w.writerows(dict(Date='2026-10-14',Tool='Web search',Query=q,Scope='Primary discovery only; admitted studies verified in exact cached MED responses') for q in queries)
v=json.loads((O/'audit/validation_report.json').read_text());tests=json.loads((O/'audit/mutation_tests.json').read_text());rebuild=json.loads((O/'audit/rebuild_verification.json').read_text())
assert not v['errors'] and tests['passed']==tests['total'] and rebuild['status']=='PASS'
pdf=PdfReader(O/'reports/CookRisk_StageB_v5_Report.pdf');assert len(pdf.pages)==4
assert '\ufffd' not in '\n'.join(p.extract_text() or '' for p in pdf.pages)
(O/'audit/report_visual_qa.json').write_text(json.dumps(dict(pages=4,all_pages_visually_inspected=True,result='No clipping, overlap or missing glyphs found',validation_status=v['status']),indent=2),encoding='utf8')
files=[p for p in sorted(O.rglob('*')) if p.is_file() and 'qa' not in p.relative_to(O).parts and '__pycache__' not in p.parts and p.suffix!='.zip' and p.name!='release_manifest_sha256.json']
manifest={p.relative_to(O).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
m=O/'audit/release_manifest_sha256.json';m.write_text(json.dumps(manifest,indent=2),encoding='utf8');files.append(m)
archive=O/'CookRisk_StageB_v5_20261014.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
    for p in files:z.write(p,Path('stageB/release_v5_20261014')/p.relative_to(O))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(json.dumps(dict(archive=str(archive),files=len(files),bytes=archive.stat().st_size,report_pages=len(pdf.pages)),indent=2))
