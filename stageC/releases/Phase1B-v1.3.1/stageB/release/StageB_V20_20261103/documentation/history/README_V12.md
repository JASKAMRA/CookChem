# CookRisk Stage B V12

V12 is a separate evidence release based on the protected V11 release. It contains 119 compound anchors and 286 evidence records. 14 anchors and 14 evidence rows were added. The 150-anchor target remains unmet; no evidence criteria were lowered.

Run `python build_v12.py <release-directory>` to rebuild versioned V12 outputs from the copied V11 tables. Run `python mutation_test_v12.py <release-directory>` for isolated mutation checks. Both use only the Python standard library. See `reports/V12_HANDOFF.md` for scope, results, and unresolved manual scientific review.

V12 is a literature-based resource, not clinical decision support.
