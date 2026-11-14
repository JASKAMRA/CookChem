from pathlib import Path
import json
import pandas as pd
R=Path(__file__).resolve().parent
d=pd.read_csv(R/'expanded_clean_stageA_dataset.csv'); m=json.loads((R/'manifest.json').read_text())
assert len(d)==439 and d.doi.nunique()==10
assert m['new_observations']==0 and m['strict_protocol_matches_obtained']==0 and not m['stage_c_integration_authorized']
for f in ['vitamin_c_candidate_study_comparison.csv','sweet_potato_candidate_study_comparison.csv','candidate_literature_investigation_report.md','measurement_harmonisation_report.md','domain_a_modelling_readiness.md','domain_b_modelling_readiness.md','comparative_domain_recommendation.md']:
    assert (R/f).is_file(), f
print('PASS: v1 preserves 439 rows/10 DOI families, admits no unverified candidate, and authorizes no Stage C integration.')
