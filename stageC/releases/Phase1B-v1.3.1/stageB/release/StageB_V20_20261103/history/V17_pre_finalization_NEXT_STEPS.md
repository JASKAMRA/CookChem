# V17 next steps — stable checkpoint

Current state is preserved in `StageB_V17_20261103`.

## Verified counts

- Compounds: 143/150 (seven eligible additions remain).
- Interaction evidence: 317; drug/probe rows: 133; bibliography rows: 163; study rows: 161.
- Warnings: 70 (66 inherited + four V17). Fresh inherited warning audits: 0/66; three partial source rechecks only.
- Candidate screening log: 80 rows, 75 distinct names total; seven distinct new V17 leads relative to the inherited count of 68. The requirement is 40.
- V17 focused validation: 13/13 tests passed; structural validator passed.
- Root regression last passed 46/46 before Batches 9–11; rerun after remaining work.

## Resume sequence

1. Research and individually screen additional distinct leads from primary sources, capturing decisions and evidence levels in the existing candidate log. Reach at least 40 new V17 leads; do not count inherited leads or repeated duplicate checks.
2. Admit only fully supported candidates, in sequential batches of no more than four, until exactly 150. For each batch, add and link identity, food context, evidence, study/bibliography, source audit, screening decision and open scientific warnings; run the focused validator/tests and manifest checks.
3. Audit each of the 66 inherited warning IDs from affected records and primary sources. Record V17 findings separately from historical V16 dispositions; repair only demonstrable technical defects.
4. Reconcile warning status/severity summaries and run synthetic mutation tests.
5. Run the complete Stage B root regression, V17 tests, structural/provenance checks, deterministic exact manifest verification, and independent clean-copy verification.
6. Update release metadata and status from observed outputs. Keep readiness partial if any required work remains.

## Important unresolved science

- S-equol’s journal full text and tested preparation details were not accessible; V17-W03 remains open. The reported quantitative values are attributed to the located dissertation, not silently to the journal article.
- Phloridzin’s interaction study does not report the source lot/preparation in the reviewed methods. Its animal rosuvastatin results concern phloretin aglycone and must not be mapped to phloridzin.
- In-vitro transport findings do not establish a clinical food–drug interaction.
