from build import *
import hashlib,zipfile
def closure():
 for src in (V/'inherited_sources').rglob('*'):
  if src.is_file():dst=O/'inherited_sources'/src.relative_to(V/'inherited_sources');dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
 for folder,name in [(V/'outputs','v6'),(V/'inherited_audits','v5')]:
  for src in folder.rglob('*'):
   if src.is_file():dst=O/'inherited_audits'/name/src.relative_to(folder);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
 write('inherited_quality_audit.csv',[
 dict(Category='Metadata and primary links',Status='Partially resolved',Finding='Every inherited PMID/cached source retained; six outcomes rechecked. Missing DOI remains explicit.',Evidence='study_registry.csv; claim_support_and_outcome_audit.csv; inherited_audits/'),
 dict(Category='Duplicates and context',Status='Resolved with supporting source',Finding='No exact duplicate IDs or study/compound/drug/class/preparation contexts found. Independent cohorts are not inferred from unique PMIDs.',Evidence='validation_report.json; evidence table'),
 dict(Category='Historical selection provenance',Status='Unresolved',Finding='Original-nine selection triggers/dates remain unknown; current rationale does not reconstruct historical selection.',Evidence='V6 registry; warning ledger; inherited historical audits'),
 dict(Category='Apigenin/rutin paclitaxel attribution',Status='Unresolved',Finding='SB-0066 remains provisional. New isolated-rutin florfenicol evidence admits rutin but does not repair the old paclitaxel arm attribution.',Evidence='PMID24871039; PMID31252064; SB-0066'),
 dict(Category='Apigenin Cmax table versus prose',Status='Unresolved',Finding='SB-0067 prior Table 1/prose discrepancy retained; no disputed Cmax value imported.',Evidence='Inherited PMC3863468.xml and prior claim audit'),
 dict(Category='Daidzein/quercetin retention and identity',Status='Partially resolved',Finding='Prior analyte/hydrolysis restrictions retained; no certified master links or new retention coefficients.',Evidence='processing_provenance_audit.csv; inherited source copies'),
 dict(Category='Inherited outcome verification',Status='Partially resolved',Finding='SB-0001/0003/0004/0005 reverified from primary abstracts; two bergapten-macitentan records from selected full text; 58 earlier metadata-audit-only rows remain.',Evidence='claim_support_and_outcome_audit.csv; all_record_review_audit.csv'),
 dict(Category='Study classification and secondary evidence',Status='Partially resolved',Finding='New RCTs separated from PK and human-cell work. No new secondary-only interaction claim admitted. Historical outcomes not all independently re-extracted.',Evidence='new_evidence_records.csv; baseline_review_levels.csv')])
def package():
 target=O/'CookRisk_StageB_v7_20261015_clean.zip';manifest=O/'audit/release_manifest_sha256.json'
 files=[p for p in O.rglob('*') if p.is_file() and p not in [target,manifest] and '__pycache__' not in p.parts and 'previews' not in p.parts]
 hashes={p.relative_to(O).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)};manifest.write_text(json.dumps(hashes,indent=2),encoding='utf8')
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
  for p in files+[manifest]:z.write(p,arcname=O.name+'/'+p.relative_to(O).as_posix())
 with zipfile.ZipFile(target) as z:assert z.testzip() is None;assert all(hashlib.sha256(z.read(O.name+'/'+p)).hexdigest()==h for p,h in hashes.items())
 print('ZIP verified',len(files)+1,'files',target.stat().st_size,'bytes')
if __name__=='__main__':closure();package()
