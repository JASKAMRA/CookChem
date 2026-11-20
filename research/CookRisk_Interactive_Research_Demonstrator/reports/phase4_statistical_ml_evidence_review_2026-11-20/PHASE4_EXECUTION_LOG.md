# Phase 4 Execution Log

**Status:** PARTIALLY COMPLETE  
**Date:** 2026-11-20

## Work completed

- Read the required Phase 2 provenance report and Phase 3 ACR report, gap register, execution log and comparison outputs.
- Verified dataset pins before parsing: Batch021 111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8 (1,016 x 38); Reconstruction f9391233a2d4231140d46aa58e864180eddb6f2c3a56b030df3f94ca25f083b0 (1,016 x 43). Rechecked after generation: 111064cee20b1f1536337e95b22941c5d6a07ef71360aad0df0acdbcafe669c8; f9391233a2d4231140d46aa58e864180eddb6f2c3a56b030df3f94ca25f083b0; both still match.
- Computed Reconstruction descriptive statistics for ACR, concentration/process/replicate fields and RDKit numeric predictors, plus category support, missingness, DOI clustering and summary-only Tukey sensitivity using Python standard library.
- Reviewed only named Batch021 and molecular/source saved evidence; checked sidecars, embedded input linkage, fold/OOF schemas/counts, and static model/split/preprocessing code.
- Wrote seven required reports/registers and one supporting builder helper in the new Phase 4 folder. Existing project files were not changed.

## Historical integrity

- Batch021 input, post1000 JSON/Markdown, all 21 per-model comparison/fold/OOF components, and named molecular/source summary/fold/split/OOF/report match their sidecars where checked.
- Combined post1000 comparison/fold/OOF fail their recorded hashes. The combined metric comparison conflicts in 12/21 rows. Cause is unknown.
- No historical artifact was edited, regenerated, retrained or replaced.

## Errors, root causes and corrections

1. Package probe traceback: `Traceback (most recent call last): File "<string>", line 1, in <module>; ModuleNotFoundError: No module named 'pandas'`. Cause: pandas is unavailable in the existing Python 3.14 interpreter. Classification: environment limitation. Correction: no installation; use Python standard-library parsing and arithmetic.
2. Long inline command error: `MXC launcher: target PowerShell executable was a packaged MSIX app and could not be launched inside the sandboxed container.` No audit code ran from that command. Classification: execution-launcher limitation. Correction: save the scoped report builder and invoke it with a short command; no software was installed or changed.
3. Initial helper traceback ended with `FileExistsError: [WinError 183] Cannot create a file when that file already exists`. Cause: the patch had already created the helper's parent directory. Classification: report-helper issue. Correction: make directory creation idempotent after verifying the directory contents.
4. Helper traceback ended with `NameError: name 'protocols' is not defined. Did you mean: 'protocol'?`. Cause: new helper variable-name typo. Classification: report-helper issue. Correction: reference the existing `prot` mapping and rerun.
5. Safety guard output: `Output reports already exist; refusing overwrite`. Cause: the previous failed run had created four partial Phase 4 CSVs. Classification: intentional overwrite guard, not a data error. Correction: inspect the folder, confirm it contained only this new helper and its partial outputs, then allow only the explicitly named Phase 4 outputs to be regenerated. The guard prevented writes during that attempt.
6. Helper compilation failed with SyntaxError: (unicode error) 'unicodeescape' codec can't decode bytes in position 2170-2171: truncated \UXXXXXXXX escape. Cause: a Windows path in a normal triple-quoted generated-log string. Classification: report-helper issue. Correction: use a raw f-string and rerun.
7. The next compile attempt ended with SyntaxError: unterminated string literal (detected at line 527). Cause: embedded triple-quote text closed the helper log literal. Correction: describe the source line without inserting a quote delimiter.
8. The following compile attempt ended with IndentationError: unexpected indent at line 526. Cause: a caret excerpt remained after replacing the quote delimiter. Correction: replace the caret excerpt with plain text.
9. Post-generation review found a basis-label classification discrepancy: the literal text count was 1 while Phase 3 documented 6 unspecified-basis labels. Cause: the lexical check did not match the documented semantic classification. Correction: preserve the Phase 3 value of 6 and label it as inherited documentation; no source data changed.
10. Post-generation review caught a draft sentence conflating the 118 stored-target/recalculated-ACR differences with the separate 15 Reconstruction/Batch021 target cells. Correction: describe the two comparisons separately; no scientific input changed.
11. Final helper run and CSV parsing completed successfully; no further errors occurred.

### Captured exception tracebacks

Pandas probe:

    Traceback (most recent call last):
      File "<string>", line 1, in <module>
    ModuleNotFoundError: No module named 'pandas'

First helper run:

    Traceback (most recent call last):
      File "C:\Users\dakshant\Desktop\CookChem\research\CookRisk_Interactive_Research_Demonstrator\reports\phase4_statistical_ml_evidence_review_2026-11-20\phase4_report_builder.py", line 508, in <module>
        main()
      File "C:\Users\dakshant\Desktop\CookChem\research\CookRisk_Interactive_Research_Demonstrator\reports\phase4_statistical_ml_evidence_review_2026-11-20\phase4_report_builder.py", line 146, in main
        OUT.mkdir(parents=True)
      File "C:\Python314\Lib\pathlib\__init__.py", line 1011, in mkdir
        os.mkdir(self, mode)
    FileExistsError: [WinError 183] Cannot create a file when that file already exists: 'research\CookRisk_Interactive_Research_Demonstrator\reports\phase4_statistical_ml_evidence_review_2026-11-20'

Second helper run:

    Traceback (most recent call last):
      File "C:\Users\dakshant\Desktop\CookChem\research\CookRisk_Interactive_Research_Demonstrator\reports\phase4_statistical_ml_evidence_review_2026-11-20\phase4_report_builder.py", line 508, in <module>
        main()
      File "C:\Users\dakshant\Desktop\CookChem\research\CookRisk_Interactive_Research_Demonstrator\reports\phase4_statistical_ml_evidence_review_2026-11-20\phase4_report_builder.py", line 312, in main
        evaluation_population=protocols[protocol]+"; pooled 1,016 OOF predictions",
    NameError: name 'protocols' is not defined. Did you mean: 'protocol'?

The launcher rejection had no Python traceback. The later output-directory guard was an intentional stop and printed its exact refusal message; it did not modify files during that attempt.

Compile-time error on the next attempt:

    File "C:\Users\dakshant\Desktop\CookChem\research\CookRisk_Interactive_Research_Demonstrator\reports\phase4_statistical_ml_evidence_review_2026-11-20\phase4_report_builder.py", line 527
        SyntaxError: (unicode error) 'unicodeescape' codec can't decode bytes in position 2170-2171: truncated \UXXXXXXXX escape
                                                              ^
    SyntaxError: unterminated string literal (detected at line 527)

Compile-time error on the following attempt:

    File "C:\Users\dakshant\Desktop\CookChem\research\CookRisk_Interactive_Research_Demonstrator\reports\phase4_statistical_ml_evidence_review_2026-11-20\phase4_report_builder.py", line 526
        ^^^
    IndentationError: unexpected indent

Compile-time error:

    File "C:\Users\dakshant\Desktop\CookChem\research\CookRisk_Interactive_Research_Demonstrator\reports\phase4_statistical_ml_evidence_review_2026-11-20\phase4_report_builder.py", line 536
        [closing triple-quote delimiter; compiler caret was displayed here]
    SyntaxError: (unicode error) 'unicodeescape' codec can't decode bytes in position 2170-2171: truncated \UXXXXXXXX escape

## Verification

- Hash gates before and after: PASS.
- Expected shapes: PASS (Batch021 1,016 x 38; Reconstruction 1,016 x 43).
- Component/summary consistency: PASS, 21/21.
- Combined comparison consistency: FAIL, 12/21 conflicting rows; preserved, not repaired.
- Combined comparison/fold/OOF sidecars: FAIL; component files and JSON/Markdown: PASS.
- Molecular/source input hash and named audit sidecars: PASS.
- Report CSV parsing: PASS; counts below.
- Training, predictions, metric recalculation, model build, validation rerun and dependency install: NOT PERFORMED.

## Boundaries

No Git writes; no Stage B/C/D access; no restricted catalog or Retention_Final source access; no application, dataset, registry, model, metric, dependency or lockfile edits. Writes are confined to this new Phase 4 report package.

## Required CSV parse counts

- STATISTICAL_REVIEW_TABLE.csv: PASS; 28 data rows.
- HISTORICAL_ML_EVIDENCE_REGISTER.csv: PASS; 24 data rows.
- ML_PROVENANCE_GAP_REGISTER.csv: PASS; 10 data rows.
- VALIDATION_DESIGN_REVIEW.csv: PASS; 28 data rows.
- METRIC_INTERPRETATION_REGISTER.csv: PASS; 23 data rows.
