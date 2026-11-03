# CookRisk Stage B V11

Release date: 2026-10-30. Status: PASS_WITH_WARNINGS.

V11 is a separate Stage B evidence release derived from the immutable V10 release. Counts: 105 anchors, 272 evidence rows, 121 drug/probe labels. Five anchors and nine in-vitro records were added. It does not estimate exposure or clinical risk.

Run `python build_v11.py` from this folder (with the adjacent `release_v10_20261030` folder), or pass a release directory. The rebuild uses captured source metadata and Python standard library only. Run `python audit_v11.py v11` and `python mutation_test_v11.py` for checks. Manual-review limits are listed in `reports/V11_HANDOFF.md`.
