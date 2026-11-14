from pathlib import Path
import json, hashlib
import pandas as pd
R=Path(__file__).resolve().parent
d=pd.read_csv(R/'expanded_clean_stageA_dataset.csv')
m=json.loads((R/'manifest.json').read_text())
assert len(d)==439 and d.doi.nunique()==10 and m['new_observations']==0
cells=pd.read_csv(R/'full_exact_matched_cell_matrix.csv')
assert (cells.exact_match_status=='EXACT_CROSS_SOURCE_REPLICATION').sum()==0
assert (cells.exact_match_status.str.contains('NEAR')).sum()==6
for n in ['complete_dataset_coverage_report.md','molecular_descriptor_coverage_report.md','target_measurement_compatibility_report.md','source_confounding_diagnostic_report.md','validation_feasibility_report.md','domain_a_vitamin_c_readiness.md','domain_b_sweet_potato_readiness.md','final_strategic_recommendation.md','ranked_evidence_acquisition_priorities.csv']:
    assert (R/n).is_file(),n
print('PASS: v0.9 preserves 439 rows/10 DOI families and classifies six categorical Vitamin-C near-matches with zero strict protocol-identical cross-source replications.')
