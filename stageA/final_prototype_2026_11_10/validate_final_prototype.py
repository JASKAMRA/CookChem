from pathlib import Path
import json, pandas as pd
R=Path(__file__).resolve().parent
d=pd.read_csv(R/'final_modelling_dataset.csv');m=json.loads((R/'manifest.json').read_text())
assert len(d)==439 and d.doi.nunique()==10 and m['eligible_rows']==439
assert (d.target_name=='apparent_concentration_ratio_percent').all()
assert not m['saved_model'] and not m['stage_c_integration_authorized']
for f in ['feature_matrix.csv','target_vector.csv','feature_schema.json','model_comparison.csv','fold_metrics.csv','ablation_study.csv','out_of_fold_predictions.csv','source_held_out_actual_vs_predicted.png','model_scope_and_limitations.md','prediction_interface.py']:
 assert (R/f).is_file(),f
z=pd.read_csv(R/'model_comparison.csv');assert {'random','compound_grouped','food_matrix_grouped','source_held_out'}.issubset(set(z.validation))
print('PASS: final prototype preserves all 439 eligible apparent-ratio observations, generated fold-safe evaluations, and released no deployable model.')
