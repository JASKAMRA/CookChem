# QC report

No exact duplicate study/compound/drug/evidence-context/preparation/co-intervention rows were found. Original SB-0001–SB-0033 identifiers remain; additions begin at SB-0034. Same-report experiments share a PMID-based Study_ID. Different dose arms are summarized, not padded into separate records; the inherited curcumin alone versus curcumin+piperine tamoxifen arms remain distinct co-interventions. The 1988 quinolone study PMID 2853056 was deferred because overlap with PMID 3480885 could not be ruled out. Related publications and correction notices are not counted as independent evidence.

Independent Crossref audit: 33 primary titles concordant, one manually verified omitted subtitle (PMID 17963429; authors Kasibhatta/Naidu and year 2007 concordant), nine Crossref lookups unavailable, and two primary records without a supplied DOI. These eleven cases remain verifiable by primary PMID, but independent DOI confirmation is incomplete. No unresolved title mismatch was accepted. See primary_source_DOI_audit.csv.

## Identities and inherited provenance

The initial audit's 96 uncertain groups remain excluded from evidence assignment. In addition, the ascorbic-acid group mixes single L-ascorbic acid and total L-AA+DHAA measurements; it is explicitly excluded in this release's identity/priority tables. This is a QC overlay, not a silent rewrite of the initial release. Parent connectivity is distinguished from complete stereochemical verification. No uncertain group receives an interaction record. Drug names are checked against primary administered probes; external identifiers are not guessed.

The inherited retention dataset audit found 145 author/year metadata discrepancies among 208 DOI lookups and ten unavailable lookups. Those are provenance flags, not proof that every concentration is wrong. DOI 10.1016/j.lwt.2021.111500 is a confirmed source mismatch for the five Persin/avocado records: its publication concerns fish-oil/gelatin nanofibrous membranes. These issues remain unresolved and are copied into the inherited source-audit table; no original identity, DOI or measurement has been silently changed. The 221 observations without molecular IDs remain unassigned and are not linked to interaction evidence.

## Unsupported or disputed claims withheld

- PMID 28533679: Cmax ratio 0.85 has 90% CI 0.70–1.04. Do not call this a statistically established Cmax reduction. AUC reduction and repeated-regimen null are separately described within one record.
- PMID 22300367: conflicting abstract/results prose on human dose-specific AUC fold changes; those magnitudes are withheld. Mouse AUC and vesicle Ki belong only to their separate experimental contexts.
- PMID 26633237: malformed absolute AUC unit in abstract; reported dimensionless ratios retained.
- PMID 21943317: suspicious clearance units; those values omitted.
- PMID 25624269: reversed metabolite-formation wording; measured epoxide/parent ratio and parent PK retained.
- Proposed therapeutic benefits in small piperine/resveratrol PK studies are not verified clinical outcomes and were not promoted to clinical risk or benefit claims.
- Reviews, modeling-only predictions, extract effects attributed to an untested constituent, and uncertain compound identities are not included as primary clinical interaction evidence.

Every specific excluded/deferred source is listed in `source_screening_log.csv`. Other retrieved candidates are marked not fully screened, not falsely called excluded after full review. Confidence is an extraction-level descriptive assessment, not GRADE, a validated risk score, or independent second-reviewer adjudication.

## Conflicting evidence

`conflict_synthesis.csv` retains four inherited context groups and the added EGCG–rosuvastatin regimen contrast. They differ in species, dose, formulation or endpoints; the count does not imply five directly replicated contradictions. No majority-vote direction is assigned.
