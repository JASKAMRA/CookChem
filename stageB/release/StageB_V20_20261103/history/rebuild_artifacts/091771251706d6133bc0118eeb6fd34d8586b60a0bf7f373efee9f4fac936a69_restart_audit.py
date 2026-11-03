from pathlib import Path
import json,csv,hashlib,collections
O=Path(__file__).resolve().parent;R=O.parents[1];V=O.parent/'release_v6_20261014';P=O.parent/'release_v7_20261014'
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def save(n,d):(O/'audit'/n).write_text(json.dumps(d,indent=2),encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
partial={p.relative_to(P).as_posix():sha(p) for p in P.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
save('interrupted_attempt_inventory.json',dict(directory=str(P),file_count=len(partial),hashes=partial,status='Incomplete, not a final release. Tables and earlier passing test reports exist; report, README, schema and final archive absent. Scripts changed after last validation, so prior results not accepted as clean-build validation.',handling='Preserved in place. No completed output table or validation success imported into the clean release. Only inspected source material and reviewed script templates may be reused.'))
manifest=json.loads((V/'audit/release_manifest_sha256.json').read_text(encoding='utf8'));bad=[p for p,h in manifest.items() if not (V/p).exists() or sha(V/p)!=h];assert not bad,bad
save('v6_original_manifest_verification.json',dict(files=len(manifest),mismatches=bad,zip_sha256=sha(V/'CookRisk_StageB_v6_20261014.zip')))
e=read(V/'outputs/stageB_food_drug_interactions_v6.csv');r=read(V/'outputs/compound_registry.csv');old=json.loads((V/'outputs/release_summary.json').read_text(encoding='utf8'))
s=dict(anchors=len(r),records=len(e),drugs=len({x['Drug'] for x in e}),publications=len({x['PMID'] for x in e}),unique_nonempty_doi=len({x['DOI'].lower() for x in e if x['DOI']}),numerical_records=sum(bool(x['Quantitative_Outcome']) for x in e),classes=dict(collections.Counter(x['Evidence_Type'] for x in e)),origins=dict(collections.Counter(x['Release_Origin'] for x in e)),duplicate_ids=len(e)-len({x['Evidence_ID'] for x in e}),duplicate_contexts=len(e)-len({tuple(x[k] for k in ['Study_ID','Compound_ID','Drug','Evidence_Type','Preparation','Co_Compounds']) for x in e}),warnings=sum(x['After'] in ['Unresolved','Partially resolved'] for x in read(V/'outputs/warning_resolution_ledger.csv')),standalone_drug_registry='Not present in V6; counts derived directly from evidence Drug field')
s['reported_count_mismatches']={k:[s[k],old[k]] for k in ['anchors','records','drugs','publications','numerical_records','classes'] if s[k]!=old[k]};save('baseline_counts.json',s)
freeze={p.relative_to(R).as_posix():sha(p) for p in R.rglob('*') if p.is_file() and O not in p.parents and '.git' not in p.parts and '__pycache__' not in p.parts and 'v6_suite_restart_20261015' not in p.parts}
save('preservation_manifest.json',freeze);print(s);print('Frozen prior files',len(freeze))
