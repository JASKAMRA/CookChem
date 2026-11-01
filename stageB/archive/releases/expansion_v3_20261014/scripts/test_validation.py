"""Mutation tests ensure the release validator detects material integrity faults."""
import copy,json
from validate_release import OUT,B,read,validate
e=read(OUT/'outputs/stageB_food_drug_interactions_v3.csv');r=read(OUT/'outputs/compound_registry.csv');b=read(B/'expansion_v2/outputs/stageB_food_drug_interactions_expanded.csv')
cases=[]
def case(name,mutate,expected):
    ee,rr=copy.deepcopy(e),copy.deepcopy(r);mutate(ee,rr)
    result=validate(ee,rr,b);codes={x['check'] for x in result['errors']}
    cases.append({'test':name,'passed':expected in codes,'expected_detection':expected})
case('duplicate evidence ID',lambda ee,rr:ee[-1].update(Evidence_ID=ee[0]['Evidence_ID']),'evidence_ids_unique')
case('broken compound reference',lambda ee,rr:ee[-1].update(Compound_ID='MISSING'),'compound_evidence_foreign_keys')
case('unsupported numerical change',lambda ee,rr:ee[-1].update(Quantitative_Outcome='AUC GMR 99.99'),'ledger_matches_actual_claim_fields')
case('bibliographic title corruption',lambda ee,rr:ee[-1].update(Source_Title='Unrelated report'),'live_table_fields_match_cached_primary_metadata')
case('baseline outcome changed',lambda ee,rr:ee[0].update(Interaction_Effect='Changed outcome'),'baseline_64_rows_unchanged')
case('missing new selection citation',lambda ee,rr:rr[-1].update(Selection_PMID=''),'all_new_compounds_have_selection_sources')
(OUT/'audit/validation_self_tests.json').write_text(json.dumps({'tests':cases,'passed':sum(c['passed'] for c in cases),'total':len(cases)},indent=2),encoding='utf8')
print(json.dumps(cases,indent=2));assert all(c['passed'] for c in cases)
