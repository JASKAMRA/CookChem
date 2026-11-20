# Phase 3 Scientific ACR Validation — Execution Log

**Date:** 2026-11-20  
**Mode:** Read-only data audit; outputs limited to this isolated report directory.  
**Status:** PARTIALLY COMPLETE — repository-level audit is complete; source-level measurement comparability and total-mass validation remain blocked by unavailable evidence.

## Sequence and verification

1. Read Phase 2 provenance report and owner-decision register.
2. Checked both approved hashes before data parsing: Reconstruction `f9391233a2d4231140d46aa58e864180eddb6f2c3a56b030df3f94ca25f083b0`; Batch021 `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8`.
3. Used Reconstruction for ACR analysis and Batch021 only for approved schema/ID/shared-field comparison.
4. Independently recalculated 1,016 ACR ratios with Decimal arithmetic; created the seven CSV reports and main report.
5. Reopened all generated content and verified CSV field counts/row widths.
6. Rechecked pins after analysis: Reconstruction `f9391233a2d4231140d46aa58e864180eddb6f2c3a56b030df3f94ca25f083b0`, Batch021 `111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8`. Shapes remain 1,016 × 43 and 1,016 × 38.

## Audit command errors and fixes

The following errors occurred in read-only previews before final report creation. Each was corrected and the affected check rerun:

| Error | Root cause | Correction | Rerun result |
|---|---|---|---|
| PowerShell ParserError: An empty pipe element is not allowed. | Pipeline followed a foreach statement without assignment; no dataset was read. | Assigned loop output to $results, then piped the variable. | Both pin checks passed. |
| KeyError: 'datasets' | The registry datasets mapping was selected and indexed a second time. | Indexed the requested dataset IDs directly in that mapping. | Schema and data preview passed. |
| UnicodeEncodeError: 'charmap' codec can't encode character \u03bc in position 342: character maps to <undefined>. | CP1252 console could not print the micro unit symbol. | Set audit-process stdout to UTF-8; no source encoding changed. | Unit/basis summary passed. |
| TypeError: '<' not supported between instances of 'dict' and 'dict' | Tied ratios caused tuple sorting to compare row dictionaries. | Sorted outlier pairs with an explicit ratio key. | Outlier summary passed. |
| MXC launcher reported packaged MSIX PowerShell cannot be launched inside a sandboxed container. | The oversized inline command was rejected before script execution. | Moved generation to this isolated Phase 3 audit helper and invoked it with a short command. | Report generation and validation passed. |
| ValueError: dict contains fields not in fieldnames: 'implication', 'next_action'. | Scientific-gap row keys did not match the CSV header. | Aligned the gap CSV header to the row fields. | Generator rerun passed. |


### Captured tracebacks and diagnostics

PowerShell parser error (no Python traceback was produced):
```text
ParserError: An empty pipe element is not allowed.
```

Registry lookup error:
```text
Traceback (most recent call last):
  File "<stdin>", line 17, in <module>
KeyError: 'datasets'
```

Windows console encoding error:
```text
Traceback (most recent call last):
  File "<stdin>", line 25, in <module>
  File "C:\Python314\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
UnicodeEncodeError: 'charmap' codec can't encode character '\u03bc' in position 342: character maps to <undefined>
```

Outlier preview sorting error:
```text
Traceback (most recent call last):
  File "<stdin>", line 37, in <module>
TypeError: '<' not supported between instances of 'dict' and 'dict'
```

Report CSV header validation error:
```text
Traceback (most recent call last):
  File "...\phase3_audit_report_generator.py", line 337, in <module>
    payload={k:csvtext(h,r) for k,(h,r) in csvdata.items()}
  File "...\phase3_audit_report_generator.py", line 50, in csvtext
    for r in rows:w.writerow(r)
ValueError: dict contains fields not in fieldnames: 'implication', 'next_action'
```

The long inline command was rejected by the launcher before execution; it returned that the packaged MSIX PowerShell executable could not be launched in the sandboxed container. No traceback was provided for the host-launcher error.


## Key results

- ACR assessable: 1016/1,016; unassessable 0.
- Target comparison: 58 exact, 840 additional within 1E-9 pp, 118 strict differences; 118/118 match stored display precision.
- Maximum target difference: 0.004822448472808542 pp.
- Global Tukey high flags: 97; ACR >100%: 346; ACR >1,000%: 22; cooked zeros: 2.
- Unit/basis labels: 20/15; combinations 23; comparability not source-verified.
- Shared IDs: 1016; 15 target-value serialization differences; maximum 2.842170943040401e-14 pp; no merge.

## Required outputs

- `ACR_RECALCULATION_AUDIT.csv`
- `DATA_QUALITY_AND_MISSINGNESS.csv`
- `GROUP_SUPPORT_AND_DISTRIBUTIONS.csv`
- `OUTLIER_REVIEW.csv`
- `PHASE3_EXECUTION_LOG.md`
- `PHASE3_SCIENTIFIC_ACR_VALIDATION_REPORT.md`
- `RECONSTRUCTION_BATCH021_COMPARISON.csv`
- `SCIENTIFIC_GAP_REGISTER.csv`
- `UNIT_AND_MEASUREMENT_COMPATIBILITY.csv`

Supplemental helper: `phase3_audit_report_generator.py` (audit/report generator only; not application or scientific source data).

## Final preservation and boundary checks

- Output directory contains the nine requested reports plus the named supplemental generator; all are readable and nonempty.
- All seven CSVs parse with consistent headers and row widths.
- Both approved hashes and dimensions match after generation.
- Only the new Phase 3 report directory was written. No application source, registry, data, historical outputs/models/metrics/predictions/validation artifacts, dependencies, or lockfiles were changed.
- No Git operation, package installation, model training/evaluation, or build occurred.
- Stage B, restricted Stage C/D materials, and `research/EXISTING_RESULTS_METRICS_CATALOG.csv` were not accessed. No broad scan was performed. `Retention_Final` source CSV was not read or hashed.
- No app tests were run because app code was not modified; the audit validated scientific fields, calculations, identities, schema, and report integrity.
