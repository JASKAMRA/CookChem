from pathlib import Path
import csv,json,hashlib
R=Path(__file__).resolve().parent
with (R/'expanded_clean_stageA_dataset.csv').open(encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f))
assert len(rows)==379 and len({r['doi'] for r in rows})==8
m=json.loads((R/'diagnostic_manifest.json').read_text());assert m['parent_dataset_sha256']==hashlib.sha256((R/'expanded_clean_stageA_dataset.csv').read_bytes()).hexdigest();assert m['new_observations']==0 and not m['stage_c_integration_authorized']
for p in ['feature_ablation_comparison.csv','feature_ablation_fold_metrics.csv','source_by_compound.csv','source_by_food_matrix.csv','source_by_cooking_method.csv','source_by_measurement_basis.csv','source_confounding_report.md','v05_model_comparison.csv','v05_fold_metrics.csv']:
 assert (R/p).exists(),p
print('PASS: v0.6 preserves the v0.5 dataset hash and contains the required confounding, coverage, and ablation outputs.')
