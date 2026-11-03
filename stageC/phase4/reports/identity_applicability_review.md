# Phase 4 identity and applicability review — working registry v0.1.2

## Current counts

| Dimension | Status | Count |
|---|---|---:|
| Registered sources | full-text reviewed | 1 |
| Evidence records | full-text extracted | 6 |
| Outcomes | measured numeric | 5 |
| Outcomes | qualitative | 1 |
| Identity | NAME_ONLY_MATCH | 6 |
| Applicability | CONTEXT_LIMITED | 6 |
| Independent review | pending second reviewer | 6 |
| Accepted downstream records | none | 0 |

## Decision

The paper names caffeine; the Phase1B-v1.3.1 candidate is Caffeine (PubChem CID 2519). The paper does not report CID, InChI, or structure, so the cross-reference stays `NAME_ONLY_MATCH` pending independent adjudication. Five source-reported plasma Cmax means and one statistical comparison record are scientifically extracted but not identity-adjudicated.

The trial concerns 160 mg caffeine in fixed-volume instant coffee or a sugar-free energy drink, consumed under five temperature/rate protocols in healthy adults. Applicability is context-limited to the exact human study conditions. Plasma PK outcomes cannot be used as food-composition values, direct consumed-dose multipliers, cooking retention, safety thresholds, or clinical guidance.

The study's denominator is internally unresolved in the publication: the abstract says 24 subjects completed; Methods says 24 recruited and two excluded; Table 1 supplies no condition-specific n. The package records this conflict without choosing a denominator. Funding and author consultancy disclosures are also retained for independent quality assessment.

All evidence is excluded by the Phase 3 read-only context selector until a second reviewer adjudicates identity, conditions, applicability, and quality. The current adapter only selects accepted contextual evidence; it does not expose quantitative PK values to calculations.
