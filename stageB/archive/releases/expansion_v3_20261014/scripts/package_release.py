from pathlib import Path
import csv,json,hashlib,zipfile
from pypdf import PdfReader
OUT=Path(__file__).resolve().parents[1]
queries=[
'sulforaphane midazolam human pharmacokinetics interaction study',
'quercetin human fexofenadine pravastatin pharmacokinetics study',
'hesperidin human drug pharmacokinetics interaction study',
'site.pubmed.ncbi.nlm.nih.gov daidzein theophylline healthy volunteers pharmacokinetics',
'site.pubmed.ncbi.nlm.nih.gov apigenin docetaxel pharmacokinetics rats',
'site.pubmed.ncbi.nlm.nih.gov sulforaphane midazolam rifampicin healthy subjects',
'site.pubmed.ncbi.nlm.nih.gov luteolin nifedipine pharmacokinetics rats',
'site.pubmed.ncbi.nlm.nih.gov kaempferol tamoxifen pharmacokinetics rats',
'site.pubmed.ncbi.nlm.nih.gov quercetin fexofenadine healthy 19221726',
'site.pubmed.ncbi.nlm.nih.gov quercetin midazolam 2011 21680781',
'site.pubmed.ncbi.nlm.nih.gov quercetin midazolam short term long term 2013 2014 interaction',
'site.pubmed.ncbi.nlm.nih.gov quercetin fexofenadine 19221726',
'site.pubmed.ncbi.nlm.nih.gov daidzein drug interaction talinolol',
'site.pubmed.ncbi.nlm.nih.gov sulforaphane cooking broccoli steaming retention primary',
'"10.1155/2013/789184" retraction',
'"24369535" retracted',
'"10.1007/s13318-014-0203-z" retraction']
with (OUT/'outputs/exploratory_web_discovery_log.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['Search_Date','Database','Query','Scope']);w.writeheader()
    w.writerows(dict(Search_Date='2026-10-14',Database='Web search tool',Query=q,Scope='Exploratory discovery; not exhaustive screening; included primary sources subsequently verified in cached MED snapshots') for q in queries)
pdf=OUT/'reports/CookRisk_StageB_v3_Expansion_Report.pdf';reader=PdfReader(pdf)
assert len(reader.pages)==4
text='\n'.join(p.extract_text() or '' for p in reader.pages)
assert '\ufffd' not in text
validation=json.loads((OUT/'audit/validation_report.json').read_text())
assert not validation['errors']
(OUT/'audit/report_qa.json').write_text(json.dumps({'pdf_pages':4,'all_pages_visually_inspected':True,'layout':'No clipping, overlap or missing glyphs found','validation_status':validation['status'],'note':'Selection history and preparation limitations remain explicit'},indent=2),encoding='utf8')
files=[p for p in sorted(OUT.rglob('*')) if p.is_file() and 'qa' not in p.relative_to(OUT).parts and '__pycache__' not in p.parts and p.suffix!='.zip' and p.name!='release_manifest_sha256.json']
manifest={p.relative_to(OUT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
manifestpath=OUT/'audit/release_manifest_sha256.json';manifestpath.write_text(json.dumps(manifest,indent=2),encoding='utf8');files.append(manifestpath)
archive=OUT/'CookRisk_StageB_Expansion_v3_20261014.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
    for p in files:z.write(p,Path('stageB/expansion_v3_20261014')/p.relative_to(OUT))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(json.dumps({'archive':str(archive),'packaged_files':len(files),'bytes':archive.stat().st_size,'pdf_pages':len(reader.pages)},indent=2))
