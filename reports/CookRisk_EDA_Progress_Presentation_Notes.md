# CookRisk EDA Progress Presentation Notes

PPTX output: C:\Users\kamra\Desktop\CookChem\reports\CookRisk_EDA_Progress_Presentation.pptx

This notes file mirrors the speaker notes embedded in the PowerPoint.

## Slide 1

What this slide demonstrates: The presentation is a short research-progress story built from the current reviewed, preprocessed, and EDA outputs in the repository.
What to say: We are no longer discussing a loose literature collection. We now have a reviewed molecular-retention dataset, a deterministic preprocessing output, and a completed baseline EDA that directly informs how Week 5 modelling should be evaluated.
Why it matters: This frames the work as a data-quality and scientific-validity exercise, not just an algorithm-selection exercise.
Scientific caveats: The slide uses the repository's current final EDA counts: 1128 reviewed molecular rows, 1124 target-eligible rows, and 197 unique molecular identities in the final supervised dataset.
Likely professor questions and short answers:
Q: Why 197 here if earlier reports mentioned 198? A: 198 appears in the reviewed-input stage; the final supervised EDA has 197 unique Canonical_Molecular_ID values after excluding four target-ineligible neoformed-compound rows.
[Sources]
- C:\Users\kamra\Desktop\BTP\CookChem\data\preprocessing\final\preprocessing_manifest.json
- C:\Users\kamra\Desktop\BTP\CookChem\eda\outputs\summaries\eda_summary.json
- C:\Users\kamra\Desktop\BTP\CookChem\eda\reports\eda_report.md

## Slide 2

What this slide demonstrates: The modelling dataset is the result of multiple validation-status checkpoints, not a single straight arithmetic funnel.
What to say: The historical figures shown on the left are recorded project-status counts from the brief. The current repository-established transition we should anchor on is 1128 reviewed molecular observations to 1124 target-eligible observations to EDA.
Why it matters: It keeps us from presenting misleading arithmetic such as 970 to 1009 to 1015 to 1128 as if these were sequential subsets.
Scientific caveats: The brief references a 120-case review checkpoint and other stage totals, but the current repository files do not preserve all of those as one clean active subset. The visible slide therefore emphasizes only the repository-established current transition.
Likely professor questions and short answers:
Q: Why were 4 rows excluded after review? A: They are neoformed compounds such as acrylamide/PhIP where retention is not a meaningful target because the compound is formed during cooking rather than retained from the raw food.
Q: Why use 1124 for EDA? A: That is the final target-eligible supervised output created by the active preprocessing pipeline.
[Sources]
- C:\Users\kamra\Desktop\BTP\CookChem\data\reviewed\cookchem_molecular_retention_master.csv
- C:\Users\kamra\Desktop\BTP\CookChem\data\preprocessing\final\preprocessing_manifest.json
- C:\Users\kamra\Desktop\BTP\CookChem\data\preprocessing\final\preprocessing_report.md
- C:\Users\kamra\Desktop\BTP\CookChem\preprocessing\scripts\run_preprocessing.py

## Slide 3

What this slide demonstrates: The main data-quality issues were handled as scientific decisions, not arbitrary cleaning rules.
What to say: Apparent increases were not capped at 100 percent by default. Non-molecular observations were kept separate. Sparse predictors were retained for feature evaluation rather than used to justify row deletion. Repeated compounds lead directly to grouped validation. Descriptor incompleteness is limited and explicitly flagged.
Why it matters: This slide is where we separate resolved data-governance decisions from modelling questions that remain open.
Scientific caveats: The prompt referenced 120 reviewed apparent-increase cases with a 99/21 breakdown. The current repository does not reproduce that exact active subset. What it does show is 93 validated apparent-increase rows in the reviewed molecular file and 170 across the reviewed molecular plus non-molecular files, all retained as VALID_APPARENT_INCREASE.
Likely professor questions and short answers:
Q: Why didn't you cap >100 values at 100? A: Because the reviewed data explicitly preserves calculation-consistent or source-supported apparent increases, and automatic capping would replace source-supported values with an unsupported assumption.
Q: Are there remaining molecular-feature issues? A: Yes, 14 rows across 2 compounds still have missing RDKit_Hydroxyl_Groups and should be verified before model freezing.
[Sources]
- C:\Users\kamra\Desktop\BTP\CookChem\data\preprocessing\final\preprocessing_report.md
- C:\Users\kamra\Desktop\BTP\CookChem\data\preprocessing\final\preprocessing_manifest.json
- C:\Users\kamra\Desktop\BTP\CookChem\data\reviewed\cookchem_molecular_retention_master.csv
- C:\Users\kamra\Desktop\BTP\CookChem\data\reviewed\cookchem_non_molecular_master.csv

## Slide 4

What this slide demonstrates: Retention is highly right-skewed and includes a meaningful apparent-increase regime.
What to say: The median is 78 percent, the mean is 96.4 percent, and the maximum is 3650 percent. That combination tells us the target distribution is not symmetric and has a substantial upper tail. In the current final dataset, 189 of 1124 observations, or 16.8 percent, are above 100 percent.
Why it matters: The skew affects error metrics, model stability, and whether we should compare raw versus transformed target representations in Week 5.
Scientific caveats: Extreme values are not automatically errors. The repository's EDA report explicitly preserves them and recommends tracing them to source context rather than deleting them by rule.
Likely professor questions and short answers:
Q: Why is the target so skewed? A: The literature-derived retention values span many compounds, foods, and conditions, and the valid apparent-increase regime creates a long upper tail.
Q: Will you transform the target? A: That is a Week 5 modelling question, not a preprocessing decision. We should compare raw versus transformed targets under the same grouped validation.
Q: Are the largest values errors? A: Not by default. They need source-level tracing; the current EDA treats them as scientifically plausible unless contradicted by evidence.
[Sources]
- C:\Users\kamra\Desktop\BTP\CookChem\eda\outputs\tables\retention_summary.csv
- C:\Users\kamra\Desktop\BTP\CookChem\eda\outputs\tables\apparent_increase_summary.csv
- C:\Users\kamra\Desktop\BTP\CookChem\eda\outputs\tables\top_retention_observations.csv
- C:\Users\kamra\Desktop\BTP\CookChem\eda\outputs\figures\retention_distribution.png

## Slide 5

What this slide demonstrates: Missingness is concentrated in a small set of predictors rather than meaning the observations themselves are unusable.
What to say: Pressure, microwave power, oil type, and food-water ratio are sparse. Temperature and cooking time are much better covered and remain strong candidates for process features. The key principle is missing feature does not equal missing observation.
Why it matters: This stops us from destroying sample size unnecessarily. Instead, sparse predictors can be evaluated for exclusion or specialized handling during modelling.
Scientific caveats: No imputation has been performed in preprocessing. If we use imputation later, it must be learned inside training folds only.
Likely professor questions and short answers:
Q: Why not delete rows with missing variables? A: Because many rows still contain valid target values and valid other predictors; dropping them would discard usable information.
Q: How will missing values be handled? A: That remains a modelling decision. Any imputation or indicator strategy must be fit within training folds only.
Q: Why focus on temperature and time? A: Their coverage is materially higher than pressure or microwave power in the current dataset.
[Sources]
- C:\Users\kamra\Desktop\BTP\CookChem\eda\outputs\tables\missingness_summary.csv
- C:\Users\kamra\Desktop\BTP\CookChem\data\preprocessing\final\preprocessing_report.md

## Slide 6

What this slide demonstrates: Both molecular descriptors and core cooking variables show enough association to justify Week 5 comparison experiments.
What to say: The strongest descriptor Spearman relationships are moderate rather than trivial: H-bond acceptors, TPSA, H-bond donors, hydroxyl groups, and LogP. On the process side, temperature has 721 observed rows and cooking time has 895, so these are much more model-usable than pressure.
Why it matters: This provides a defensible basis for process-only, molecular-only, and combined feature-group baselines.
Scientific caveats: These are exploratory associations only. The EDA report explicitly warns that repeated observations of the same compound violate independence assumptions, so correlation does not prove causality or predictive improvement.
Likely professor questions and short answers:
Q: Why use molecular descriptors? A: They summarize structural properties that plausibly relate to retention behavior and show non-trivial exploratory associations in the current data.
Q: How will you prove descriptors actually help? A: By comparing grouped-validation performance of process-only, molecular-only, and combined models.
Q: Are you claiming temperature causes the observed pattern? A: No. The slide shows association and feature coverage, not a causal estimate.
[Sources]
- C:\Users\kamra\Desktop\BTP\CookChem\eda\outputs\tables\descriptor_retention_correlations.csv
- C:\Users\kamra\Desktop\BTP\CookChem\eda\outputs\tables\temperature_summary.csv
- C:\Users\kamra\Desktop\BTP\CookChem\eda\outputs\tables\cooking_time_summary.csv
- C:\Users\kamra\Desktop\BTP\CookChem\eda\outputs\figures\retention_vs_temperature.png

## Slide 7

What this slide demonstrates: The row count overstates independence because many observations repeat the same molecular identity.
What to say: We have 1124 observations but only 197 unique molecular identities in the final EDA. The top 10 compounds contribute 33.27 percent of all rows and the top 20 contribute 46.26 percent. That makes a random row split a leakage risk because the same compound can appear in both train and test.
Why it matters: If we want to know whether molecular features generalize to unseen compounds, validation must be grouped by Canonical_Molecular_ID.
Scientific caveats: Grouped splitting is stricter and may reduce nominal performance compared with row-wise random splitting, but it is the more defensible estimate of unseen-compound generalization.
Likely professor questions and short answers:
Q: Why can't you randomly split the dataset? A: Because repeated rows from the same compound would leak compound-specific descriptor information into both train and test.
Q: Why group by molecular identity rather than by paper? A: The main generalization question for molecular descriptors is whether they work on compounds not seen in training; Canonical_Molecular_ID is the direct grouping key for that question.
Q: Is 1124 observations enough? A: The effective diversity is much closer to 197 identities, so grouped validation is critical for an honest answer.
[Sources]
- C:\Users\kamra\Desktop\BTP\CookChem\eda\outputs\tables\compound_frequency_eda.csv
- C:\Users\kamra\Desktop\BTP\CookChem\eda\outputs\tables\repeated_compound_structure.csv
- C:\Users\kamra\Desktop\BTP\CookChem\eda\outputs\figures\top_compounds_by_observations.png

## Slide 8

What this slide demonstrates: The EDA separates resolved data decisions from hypotheses that must still be tested during modelling.
What to say: Some decisions are already made: keep scientifically valid >100 values, define the target as Retention_Final, and use grouped validation. Other questions remain open: target transformation, sparse-variable exclusion, Food as a high-cardinality feature, and the value of molecular descriptors.
Why it matters: This prevents us from overselling EDA as if it had already answered the modelling question.
Scientific caveats: The food count should be discussed as high-cardinality contextual information, not automatically as a final feature choice.
Likely professor questions and short answers:
Q: Why is Food not automatically included? A: The standardized food space is large, so we should test whether it improves grouped-validation performance enough to justify the extra complexity.
Q: Why exclude pressure or microwave power? A: We are not excluding them yet; we are evaluating whether their extreme sparsity makes them non-useful.
[Sources]
- C:\Users\kamra\Desktop\BTP\CookChem\eda\reports\eda_report.md
- C:\Users\kamra\Desktop\BTP\CookChem\eda\outputs\tables\missingness_summary.csv
- C:\Users\kamra\Desktop\BTP\CookChem\eda\outputs\tables\descriptor_retention_correlations.csv
- C:\Users\kamra\Desktop\BTP\CookChem\eda\outputs\tables\repeated_compound_structure.csv

## Slide 9

What this slide demonstrates: Week 5 should produce the first scientifically defensible baseline retention model, not a polished final model.
What to say: The immediate plan is to finalize candidate features from EDA, keep preprocessing fold-safe, validate by Canonical_Molecular_ID groups, and compare process-only, molecular-only, and combined baselines using MAE, RMSE, and R². The following weeks then handle feature engineering, validation, interpretation, risk scoring, and application integration.
Why it matters: It turns the EDA into a concrete modelling plan with the right safeguards.
Scientific caveats: No Week 5 results are shown because modelling has not happened yet.
Likely professor questions and short answers:
Q: What is the main Week 5 deliverable? A: A grouped-validation baseline model plus first-pass metrics and a clearer picture of the dataset's limits.
Q: What preprocessing belongs inside the fold? A: Any imputation, scaling, encoding, or feature filtering that learns from data rather than using fixed prior knowledge.
[Sources]
- C:\Users\kamra\Desktop\BTP\CookChem\docs\weekly_logs\Weekly logs.pdf
- C:\Users\kamra\Desktop\BTP\CookChem\eda\reports\eda_report.md
- C:\Users\kamra\Desktop\BTP\CookChem\data\preprocessing\final\preprocessing_manifest.json
