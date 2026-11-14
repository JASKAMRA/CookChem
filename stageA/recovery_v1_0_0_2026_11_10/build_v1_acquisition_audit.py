"""Iteration 7 bounded acquisition audit. Parent data are copied, never altered."""
from pathlib import Path
import hashlib, json, shutil
import pandas as pd

R=Path(__file__).resolve().parent
P=R.parent/'recovery_v0_9_0_2026_11_10'
DATA=P/'expanded_clean_stageA_dataset.csv'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,text): (R/name).write_text(text.strip()+'\n',encoding='utf-8')
def copy(name): shutil.copy2(P/name,R/name)
R.mkdir(exist_ok=True)
for f in ['expanded_clean_stageA_dataset.csv','source_verification_ledger.csv','exclusion_log.csv','full_exact_matched_cell_matrix.csv','near_match_cell_matrix.csv','non_comparable_cell_matrix.csv','molecular_descriptor_coverage_report.md']:
    copy(f)
d=pd.read_csv(DATA)

# Evidence is recorded even when no row qualifies; values below are not admitted model data.
vc=pd.DataFrame([
 {'doi':'10.1108/NFS-12-2012-0126','study':'Oliveira et al. (2013), Vitamin retention in vegetables submitted to heat treatment','direct_url':'https://www.researchgate.net/publication/280184339_Vitamin_retention_in_vegetables_submitted_to_heat_treatment','food':'Carrot','methods':'boiling/conventional; steaming; microwaving','raw_cooked_numeric_values':'Yes, Table I (wet basis; mg/100 g)','basis_as_reported':'wet basis (not explicitly labelled fresh weight)','analytical_definition':'Ascorbic acid, HPLC-UV (254 nm)','temperature_duration':'Boiling 100 C/25 min; steaming 100 C/25 min; microwave 10 min/max power; microwave power not numerically stated','sample_protocol':'500 g, peeled 1-cm carrot slices; water and salt specified; duplicate analyses','classification':'CATEGORICAL_MATCH_ONLY','admission':'EXCLUDED_FROM_MODEL_DATA','reason':'Independent DOI and traceable numeric table, but basis is reported as wet—not explicit FW under this project contract—and times/protocols are materially unlike both existing sources. It is evidence for acquisition priority, not a strict match.'},
 {'doi':'10.1108/NFS-11-2012-0123','study':'Zeng (2013), Effects of different cooking methods on vitamin C content of selected vegetables','direct_url':'https://cir.nii.ac.jp/crid/1360011144869607296?lang=en','food':'Spinach','methods':'boiling; steaming; microwaving','raw_cooked_numeric_values':'No primary numeric raw/cooked table verified in accessible record; abstract reports losses only','basis_as_reported':'not verified','analytical_definition':'simple UV method','temperature_duration':'5 min stated; temperature not verified','sample_protocol':'100 g homogeneous pieces (abstract)','classification':'INSUFFICIENT_EVIDENCE','admission':'NOT_ADMITTED','reason':'DOI and broad spinach/method domain verified, but source-level raw/cooked numerical values and measurement-basis contract were not verified.'},
 {'doi':'NO_DOI_LOCATED','study':'Bembem and Sadana (2014), Effect of different cooking methods on antioxidant components of carrot','direct_url':'https://jbsd.in/Vol%205%20No%201%20Jan%202014/Bembem112-116.pdf','food':'Carrot','methods':'boiling; steaming; microwave cooking','raw_cooked_numeric_values':'Yes, Table 2','basis_as_reported':'mg/100 g; narrative says FW','analytical_definition':'colorimetric 2,6-dichlorophenylindophenol assay','temperature_duration':'9/10/5 min; temperature not stated','sample_protocol':'0.5-cm cubes, 200 g; water amounts given','classification':'INSUFFICIENT_EVIDENCE','admission':'NOT_ADMITTED','reason':'A full primary table exists, but no DOI was located in the article. The project requires a DOI for every admitted observation; temperature is also unreported and assay differs from existing HPLC studies.'}
])
vc.to_csv(R/'vitamin_c_candidate_study_comparison.csv',index=False)
sp=pd.DataFrame([
 {'doi':'10.3390/foods13071101','study':'Kido et al. (2024), Effects of Cooking Methods on Caffeoylquinic Acids and Radical Scavenging Activity of Sweet Potato','direct_url':'https://www.mdpi.com/2304-8158/13/7/1101','independence':'Independent Japanese DOI/source family','compound_definition':'5-O-caffeoylquinic acid (chlorogenic acid) and CQA derivatives; no trans-ferulic acid','analytical_method':'HPLC','methods':'steaming, deep-frying, baking','basis':'Concentration basis not verified as FW in the accessible primary report','classification':'INCOMPATIBLE','admission':'NOT_ADMITTED','reason':'Different analyte set and cooking methods; no verified shared FW concentration contract. Isomerisation makes direct pooling with a generic chlorogenic-acid record inappropriate.'},
 {'doi':'10.3390/molecules27061884','study':'Frankova et al. (2022), Changes in Antioxidant Properties and Phenolics in Sweet Potatoes Due to Heat Treatments','direct_url':'https://www.mdpi.com/1420-3049/27/6/1884','independence':'Not independent for this purpose: shared author Musilova and overlapping Slovak cultivar/protocol context with Candidate B; possible material reuse must not be assumed independent','compound_definition':'chlorogenic/cryptochlorogenic/neochlorogenic acids; no trans-ferulic acid','analytical_method':'HPLC','methods':'microwaving, steaming, baking, boiling','basis':'dry weight','classification':'INCOMPATIBLE','admission':'NOT_ADMITTED','reason':'Explicit DW basis conflicts with Candidate B FW contract; source/material independence is not established, and the individual analyte set differs.'},
 {'doi':'10.3746/jkfn.2020.49.8.836','study':'Ryu et al. (2020), Determination of Chlorogenic Acids Content in Vegetables, Root and Tuber Crops by LC-MS/MS','direct_url':'https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearchBean.artiId=ART002620779','independence':'Independent Korean DOI/source family','compound_definition':'chlorogenic-acid isomer group, not verified individual chlorogenic/ferulic pair','analytical_method':'validated LC-MS/MS','methods':'sweet potato steaming (20 min) reported','basis':'mg/100 g FW stated','classification':'INSUFFICIENT_EVIDENCE','admission':'NOT_ADMITTED','reason':'Primary metadata and FW/LC-MS/MS scope are verified, but accessible record did not supply a traceable raw/cooked individual-compound numeric table or a compatible ferulic-acid definition.'}
])
sp.to_csv(R/'sweet_potato_candidate_study_comparison.csv',index=False)
write('candidate_literature_investigation_report.md', '''
# Iteration 7 candidate-literature investigation

## Method

Bounded primary-literature searches targeted the v0.9 gaps. A study was admitted only if a DOI, traceable raw/cooked numerical values, stated shared fresh-weight basis, analyte definition, protocol, and source-level comparability were all verified. Search results and abstracts never supplied new model observations.

## Vitamin C result

Oliveira et al. (2013), DOI `10.1108/NFS-12-2012-0126`, is the strongest independent carrot candidate: its Table I gives raw and cooked ascorbic-acid concentrations, uses HPLC-UV, and specifies long boiling/steaming and microwave protocols. It was **not admitted**. The table labels its concentrations `wet basis`, not explicitly fresh weight as required here, and 25-min boiling/steaming or 10-min microwave treatment is not protocol-aligned with the existing 6/8/1-min and 12/15/4-min sources. It is a categorical match only, not a strict replication.

Zeng (2013), DOI `10.1108/NFS-11-2012-0123`, independently covers spinach under all three methods but the accessible primary record supplied percentage loss rather than an auditable raw/cooked numeric table and did not verify the measurement basis. Bembem and Sadana (2014) supplies a full carrot table but no DOI was located and uses a different colorimetric method.

## Sweet-potato result

Kido et al. (2024), DOI `10.3390/foods13071101`, is an independent HPLC study of caffeoylquinic acids, but its CQA/isomer scope, methods, and unverified shared-FW concentration contract do not support pooling with Candidate B chlorogenic/trans-ferulic observations. Frankova et al. (2022), DOI `10.3390/molecules27061884`, uses a stated dry-weight basis and overlaps the Candidate-B author/protocol context; it is not independent matched evidence. Ryu et al. (2020), DOI `10.3746/jkfn.2020.49.8.836`, verifies FW LC-MS/MS and 20-min sweet-potato steaming, but no auditable individual raw/cooked compound table was accessible.

**New observations admitted: zero. New independent DOI families admitted: zero.**
''')
write('measurement_harmonisation_report.md', '''
# Measurement harmonisation

No conversion was performed. `wet basis` was not silently relabelled as the project’s required `fresh weight (FW)` basis. Dry-weight CQA data were not converted to FW. Generic chlorogenic-acid groups, individual 5-CQA/chlorogenic acid, and trans-ferulic acid were not merged. Apparent concentration ratio remains `100 × C_cooked / C_raw`; no true mass-retention outcome was calculated.
''')
write('domain_a_modelling_readiness.md', '''
# Domain A: Vitamin C selected vegetables

Dataset status remains 12 selected carrot/spinach FW observations from two admitted DOI families, producing six categorical protocol near-matches and **zero strict protocol-identical cross-source cells**. Oliveira et al. is useful external corroboration but not admissible under the locked basis/protocol contract. Zeng and Bembem are unadmitted evidence gaps. **Decision: C — additional independent matched evidence required.**
''')
write('domain_b_modelling_readiness.md', '''
# Domain B: Sweet-potato phenolic acids

Dataset status remains 32 FW observations from one admitted DOI family. The new search found relevant primary research but no independent, individual-compound, raw/cooked FW dataset compatible with Candidate B. **Decision: C — additional independent matched evidence required.**
''')
write('comparative_domain_recommendation.md', '''
# Comparative domain recommendation

**Final decision: C — both domains still require additional independent matched evidence.**

Vitamin C is closer: it has two admitted source families and a fully documented independent HPLC carrot candidate that nearly meets the evidence contract. The next narrowly bounded retrieval should seek an independent paper with explicitly FW-labelled carrot or spinach raw/cooked values and protocol close to a pre-specified target cell. Sweet potato remains farther away because it has one admitted source family and candidate studies change basis, analyte definition, or source independence.

Neither domain supports model fitting or held-out-source validation. Stage C remains blocked.
''')
write('iteration_summary.md', f'''# Stage A Iteration 7 summary

- Parent: v0.9 / `{sha(DATA)}`.
- Observations: {len(d)} (unchanged); DOI families: {d.doi.nunique()} (unchanged).
- New observations: 0; new admitted DOI families: 0.
- Strict protocol matches obtained: 0; categorical near-matches added to model-ready data: 0.
- No model was trained.
- Complete candidate decisions are recorded in the two comparison CSVs and the candidate investigation report.
''')
m={'package':'StageA_TargetedIndependentSourceAcquisition_v1.0.0_2026-11-10','parent_dataset_sha256':sha(DATA),'rows':len(d),'source_families':int(d.doi.nunique()),'new_observations':0,'new_admitted_source_families':0,'strict_protocol_matches_obtained':0,'decision':'C_BOTH_DOMAINS_REQUIRE_MORE_INDEPENDENT_MATCHED_EVIDENCE','stage_c_integration_authorized':False}
(R/'manifest.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8')
(R/'SHA256SUMS.txt').write_text('\n'.join(f'{sha(x)}  {x.name}' for x in sorted(R.iterdir()) if x.is_file() and x.name!='SHA256SUMS.txt')+'\n',encoding='utf-8')
print(json.dumps(m,indent=2))
