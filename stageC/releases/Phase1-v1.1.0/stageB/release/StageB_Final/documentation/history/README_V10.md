# CookRisk Stage B V10

This release expands the Stage B food–drug interaction evidence library to 100 compound anchors and 263 evidence records. It is a literature resource, not a clinical decision-support product. V9 is retained as an immutable baseline in its original release directory.

Start with `V10_HANDOFF.md` for the recalculated baseline, expansion counts, source-verification levels, warning status, and remaining limitations. The machine-readable handoff inputs are in `audit/` and the V10 registries/audits are in `outputs/`.

## Rebuild and validate

The build uses the captured PubChem and PubMed response files in this release; it does not need network access. From this directory run:

```text
python build_v10.py
python validate_v10.py
python finalize_v10.py
```

The V9-specific preservation validation is also retained as `prepare_validate_v9.py`. The V10 validator checks identifiers, structure completeness and uniqueness, record links, selection and source coverage, warning inheritance, cooking-domain separation, V9 file hashes, and ten critical-rule mutations.

## Interpretation

All 53 V10 additions are in vitro. Herbal botanical findings, null-only transporter screens, abstract-level extractions, and the DOI-only shogaol source have specific caveats in the records and warning ledger. Do not interpret assay outcomes as clinical effects or exposure estimates. Candidate screening was focused, not systematic.
