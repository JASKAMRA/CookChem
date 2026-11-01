"""Meaningful offline delivery checks, independent of the builder's in-memory tables."""
import csv,json,hashlib,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(n): return list(csv.DictReader((ROOT/'outputs'/n).open(encoding='utf-8-sig')))
main=read('stageB_food_drug_interactions.csv'); mapping=read('stageB_compound_mapping.csv'); evidence=read('stageB_literature_evidence.csv'); relations=read('stageB_interaction_compounds.csv'); links=read('stageB_stageA_observation_links.csv')
byid={r['interaction_id']:r for r in main}; maps={r['Canonical_Molecular_ID']:r for r in mapping}
assert len(main)==33 and len(mapping)==198 and len(links)==1124
assert {r['interaction_id'] for r in evidence}==set(byid)
assert all(r['interaction_id'] in byid and r['Canonical_Molecular_ID'] in maps for r in relations)
assert all(not r['food_id'] for r in main if r['evidence_level']=='compound')
assert len({(r['source_id'],r['Canonical_Molecular_ID'],r['drug_name'],r['evidence_type'],r['co_compounds'],r['compound_form']) for r in main})==len(main)
assert all(r['clinical_relevance']=='Clinical relevance not established' for r in main if r['evidence_type'] in ['Animal','In vitro'])
assert len(read('stageB_unassigned_observations.csv'))+sum(int(r['observation_count']) for r in mapping)==1350
assert all(len(r)==len(next(csv.reader(p.open(encoding='utf-8-sig')))) for p in (ROOT/'outputs').glob('*.csv') for r in csv.reader(p.open(encoding='utf-8-sig')))
for e in evidence:
    p=ROOT/e['source_cache']; assert p.exists()
    records=json.loads(p.read_text(encoding='utf-8'))['resultList']['result']
    s=next(r for r in records if r['id']==e['source_id'])
    assert s['title']==e['source_title'] and s.get('doi','')==e['doi']
    assert s.get('authorString','')==e['authors']
manifest=json.loads((ROOT/'audit/input_manifest.json').read_text(encoding='utf-8'))
assert all(hashlib.sha256((ROOT/r['bundled_path']).read_bytes()).hexdigest()==r['sha256'] for r in manifest)
before={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for d in ['outputs','reports'] for p in (ROOT/d).iterdir() if p.is_file()}
subprocess.run([sys.executable,str(ROOT/'scripts/build_stageB.py')],check=True,stdout=subprocess.DEVNULL)
after={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for d in ['outputs','reports'] for p in (ROOT/d).iterdir() if p.is_file()}
assert before==after,'Offline rebuild changed delivered output bytes'
result={'disk_table_integrity':'PASS','one_source_metadata_match_per_evidence_record':'PASS','original_group_and_row_counts':'PASS','food_level_claim_separation':'PASS','unique_study_relationship_contexts':'PASS','immutable_input_copies':'PASS','byte_identical_offline_rebuild':'PASS','limitations':'Integrity and reproducibility checks do not certify exhaustive searches, chemical form, clinical relevance, or upstream source measurements.'}
(ROOT/'audit/release_verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
