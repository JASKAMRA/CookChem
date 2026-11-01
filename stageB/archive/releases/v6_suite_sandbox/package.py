from build import *
import hashlib,zipfile
def closure():
 rows=read(O/'outputs/stageB_food_drug_interactions_v6.csv');paths={r['Source_Cache'] for r in rows if not r['Source_Cache'].startswith(O.name+'/')}
 # Preserve the exact old cache bytes under their original stageB-relative paths.
 for rel in paths:
  src=B/rel
  if not src.exists():raise FileNotFoundError(src)
  dst=O/'inherited_sources'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
 proc=[]
 for r in read(O/'outputs/processing_provenance_audit.csv'):
  rel=r.get('Cache','');matches=[p/rel for p in [B/'release_v4_20261014',V,B] if (p/rel).exists()]
  if not matches:raise FileNotFoundError(rel)
  src=matches[0];dst=O/'inherited_sources'/src.relative_to(B);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
  proc.append(dict(Compound=r['Compound'],Original_Cache=rel,Resolved_StageB_Path=src.relative_to(B).as_posix(),Archived_Copy=dst.relative_to(O).as_posix(),Scope='Inherited processing/context source; no new retention coefficient'))
 for r in read(O/'outputs/cooking_retention_evidence.csv'):
  src=B/r['source_cache'];dst=O/'inherited_sources'/r['source_cache'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
 write('processing_source_resolution.csv',proc)
 for n in ['all_record_review_audit.csv','compound_selection_provenance_audit.csv','identity_structure_audit.csv','interaction_evidence_source_audit.csv','inherited_v4_claim_support.csv','original_nine_interaction_reference_map.csv']:
  dst=O/'inherited_audits'/n;dst.parent.mkdir(exist_ok=True);shutil.copy2(V/'outputs'/n,dst)
 def support(n):
  p=O/'sources'/('description_'+slug(n)+'.json');d=load(p);return ' | '.join(x.get('DescriptionURL','') for x in d.get('InformationList',{}).get('Information',[]) if x.get('Description'))
 write('supplemental_food_context_sources.csv',[dict(Compound=n,Domain='Food context and identity only',Source_URL=support(n),Cache='sources/description_'+slug(n)+'.json',Scope='Authoritative ChEBI description via PubChem; not experimental drug-interaction proof') for n in ['6-Gingerol','Eugenol','Diallyl sulfide','Hesperetin']])
 write('correction_notice_audit.csv',[dict(Primary_PMID='33074419',Correction_PMID='33319311',Cache='sources/PMC7736380.xml',Review='Full correction notice reviewed',Finding='Author affiliation corrected; no scientific outcome correction reported',Counted_As_Independent_Interaction_Publication='False')])
def package():
 target=O/'CookRisk_StageB_v6_20261014.zip';manifest=O/'audit/release_manifest_sha256.json'
 files=[p for p in O.rglob('*') if p.is_file() and p not in [target,manifest] and '__pycache__' not in p.parts and 'previews' not in p.parts]
 hashes={p.relative_to(O).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)};manifest.write_text(json.dumps(hashes,indent=2),encoding='utf8')
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
  for p in files+[manifest]:z.write(p,arcname=O.name+'/'+p.relative_to(O).as_posix())
 with zipfile.ZipFile(target) as z:
  assert z.testzip() is None
  assert all(hashlib.sha256(z.read(O.name+'/'+p)).hexdigest()==h for p,h in hashes.items())
 print('Archive verified:',len(files)+1,'files;',target.stat().st_size,'bytes')
if __name__=='__main__':closure();package()
