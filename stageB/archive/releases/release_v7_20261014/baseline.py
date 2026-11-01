from collect import O
from pathlib import Path
import csv,json,hashlib,collections
B=O.parent;V=B/'release_v6_20261014';R=O.parents[1]
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def save(p,d):p.write_text(json.dumps(d,indent=2),encoding='utf8')
e=read(V/'outputs/stageB_food_drug_interactions_v6.csv');r=read(V/'outputs/compound_registry.csv')
levels={x['Evidence_ID']:x['Verification_Level'] for x in read(B/'release_v4_20261014/outputs/claim_support_and_outcome_audit.csv')}
levels.update({x['Evidence_ID']:x['Review_Level'] if 'Review_Level' in x else x['Verification_Level'] for x in read(B/'release_v5_20261014/outputs/claim_support_and_outcome_audit.csv')})
levels.update({x['Evidence_ID']:'abstract' for x in e if x['Release_Origin']=='v6_20261014'})
reviews=[dict(Evidence_ID=x['Evidence_ID'],Verification_Level='full_text_selected' if 'full_text' in levels[x['Evidence_ID']] else 'metadata_only_recent_audit' if 'metadata' in levels[x['Evidence_ID']] else 'abstract',Detail=levels[x['Evidence_ID']],Scope='Conservative latest documented outcome-review scope; not a new re-extraction') for x in e]
with (O/'inputs/baseline_review_levels.csv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(reviews[0]));w.writeheader();w.writerows(reviews)
s=dict(anchors=len(r),records=len(e),drugs=len({x['Drug'] for x in e}),publications=len({x['PMID'] for x in e}),unique_nonempty_doi=len({x['DOI'].lower() for x in e if x['DOI']}),numerical_records=sum(bool(x['Quantitative_Outcome']) for x in e),classes=dict(collections.Counter(x['Evidence_Type'] for x in e)),verification=dict(collections.Counter(x['Verification_Level'] for x in reviews)),origins=dict(collections.Counter(x['Release_Origin'] for x in e)),duplicate_contexts=len(e)-len({tuple(x[k] for k in ['Study_ID','Compound_ID','Drug','Evidence_Type','Preparation','Co_Compounds']) for x in e}))
reported=json.loads((V/'outputs/release_summary.json').read_text(encoding='utf8'));s['reported_count_mismatches']={k:[s[k],reported[k]] for k in ['anchors','records','drugs','publications','numerical_records','classes'] if s[k]!=reported[k]}
save(O/'audit/baseline_counts.json',s)
manifest={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in R.rglob('*') if p.is_file() and O not in p.parents and '.git' not in p.parts and '__pycache__' not in p.parts and 'v6_suite_sandbox' not in p.parts}
save(O/'audit/preservation_manifest.json',manifest);print(s);print('Frozen files',len(manifest))
