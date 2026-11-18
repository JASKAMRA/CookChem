# Scientific Contributions Supported by Existing Evidence

## 1. Evidence qualification as part of the computational method

The repository shows why a numerical raw/cooked pair is not automatically an admissible observation. Its source review records inclusion and exclusion decisions for basis, analyte identity, assay/table provenance, non-detects, aggregate measurements, and replicate structure. The 989 arithmetic-matching audit retains provenance conflicts and ambiguities rather than treating numerical agreement as source verification.

**Contribution status:** REPORTED in Stage A evidence audits. No claim is made that this assembly re-reviewed every original paper.

## 2. Endpoint discipline for cooking-associated changes

The ACR packages explicitly calculate `100 × C_cooked / C_raw` only for compatible concentration pairs and distinguish this ratio from total-mass retention. The repository preserves above-100% ACR values and explains that concentration can change with sample water/mass and analytical context.

**Contribution status:** REPORTED. No mass-retention model or human exposure inference is established.

## 3. Validation design changes the scientific question

The stored evaluations separate random, compound-grouped, food-grouped, and source-heldout splits. The Batch021 ExtraTrees audit reports negative pooled performance under both molecular-grouped and DOI-heldout designs, while explicitly measuring the remaining overlap dimensions. This supports the conclusion that earlier grouped scores should not be interpreted as unseen-source generalization.

**Contribution status:** REPORTED; prior benchmark repeatability is separately labeled REPRODUCED only where the dated reproduction report supports it.

## 4. Source/protocol confounding is visible in saved ablations

Ablation and importance outputs show strong association between a source-linked cooking-medium category and model importance. The v0.6 reports caution that this is not a causal microwave effect. The project thereby identifies a design problem: many source families occupy distinct compound–matrix–protocol regions.

**Contribution status:** REPORTED exploratory diagnosis; not causal identification.

## 5. A partially reproduced, transparent research workflow

Stage A contains versioned data, target contracts, scripts, fold/OOF outputs, manifests, and tests. A prior dated report documents repeatability for the specific 1,124-row `Retention_Final` benchmark in two Python 3.12.14 environments, with byte-identical newly generated OOF predictions and fold assignments. That result does not establish reproducibility for the ACR packages or for the research project as a whole. The historical prediction discrepancy remains unresolved; the Batch021 audit’s recorded input bytes are also unavailable in the current working tree.

**Contribution status:** the prior benchmark repeatability is REPRODUCED as documented by that report only; historical equivalence and broader ACR-package reproducibility remain BLOCKED/UNVERIFIED.

## Overall contribution statement

The current evidence supports CookRisk as a traceable research prototype for studying reported cooking-associated concentration changes and testing the limits of molecular/process-feature generalization. Its most defensible current finding is the absence of demonstrated source-heldout predictive transfer under the existing evaluation designs—not a validated predictor of cooking outcomes.
