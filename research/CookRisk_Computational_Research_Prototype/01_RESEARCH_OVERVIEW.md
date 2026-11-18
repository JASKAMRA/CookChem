# CookRisk: Computational Research Prototype — Overview

**Working title:** *CookRisk: Machine Learning-Based Prediction of Cooking-Induced Changes in Bioactive Compound Concentrations*  
**Package type:** academic computational research prototype assembled from existing repository evidence. No new model was trained and no experiment was run for this assembly.

## Research problem

Published cooking studies report changes in concentrations of bioactive compounds, but observations differ by analyte identity, food matrix, basis, assay, preparation, and source. The computational question is whether a source-linked evidence base and molecular/process features can characterize these reported concentration changes, and whether patterns transfer to held-out compounds and research sources.

## Objective and central question

> Can computational analysis and machine learning characterize cooking-associated changes in bioactive compound concentrations, and do the observed patterns generalize across unseen compounds and research sources?

The primary target used by the ACR research packages is:

**ACR (%) = 100 × C_cooked / C_raw**

where the concentrations are a compatible reported pair for the same analyte and compatible measurement basis/unit. ACR describes apparent concentration change. It is not total analyte-mass retention. “Cooked concentration” is a separate endpoint, and historical `Retention_Final` is a distinct, unresolved target. Those metrics must never be combined into a single leaderboard.

## Existing evidence at a glance

- Historical benchmark: 1,124 rows; 197 molecular groups; target `Retention_Final`. **REPRODUCED (prior report only):** the current benchmark pipeline produced byte-identical outputs in two documented runs. **BLOCKED/UNVERIFIED:** those outputs do not match the historical predictions; the cause remains unresolved.
- Multiple ACR datasets exist: 117, 338, 374, 379, 407, 439, 948, 989 and 1,016 row packages/tiering, with different inclusion rules and purposes. They are not one canonical, owner-approved dataset.
- The 1,016-row Batch021 and 1,016-row verified reconstruction are separate packages; reported canonical identity counts differ (51 labels/48 canonical IDs versus 48 identities). Equal row counts do not establish data identity. The saved molecular-versus-source audit records input SHA-256 `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8`, which differs from the current Batch021 CSV SHA-256 `d866d0ffab8c335e0469f2815c3cdf518b3d019be1bdf2e37ba2ced2e7d5d3c1`; attribution of that audit to current Batch021 bytes is **BLOCKED/UNVERIFIED**.
- Existing ACR evaluations report weak/negative DOI-held-out performance in several packages. For the saved molecular-versus-source audit, the validation summary records input SHA-256 `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8`, but those exact bytes are not present in the current Stage A working tree; attribution to the current Batch021 file is **BLOCKED/UNVERIFIED**. No general-purpose deployable model is supported.
- Existing EDA reports an ACR distribution with many observations above 100%; these are concentration ratios and not evidence of increased total mass.

## Supported contribution

The strongest supported contribution is a source-traceable computational evidence workflow that preserves measurement context and makes validation design visible. Its existing negative results show that grouped interpolation is not evidence of transfer to new sources and that source/protocol structure can dominate model attribution. The package is useful as a research prototype and methodological case study, not as a cooking prediction product.

## Intended scope and non-claims

This package characterizes existing reported experimental measurements and saved computational evaluations. It does not establish causal effects of cooking methods, biological availability, human exposure, clinical risk, food safety, personalized advice, or consumer cooking recommendations. It does not claim external validation, universal molecular relationships, or deployment readiness.

## Evidence labels

- **REPORTED:** stored result, not freshly rerun here.
- **REPRODUCED:** only where a prior repository report explicitly documents independent reproduction; that prior evidence is cited.
- **PROPOSED:** future research/analysis, not a result.
- **BLOCKED/UNVERIFIED:** missing evidence, unresolved snapshot linkage, or external prerequisite.

See [11 Reproducibility and Evidence References](11_REPRODUCIBILITY_AND_EVIDENCE_REFERENCES.md) and the appendices for exact file references.
