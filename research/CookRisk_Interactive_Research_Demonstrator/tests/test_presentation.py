from __future__ import annotations

import unittest

import pandas

from presentation import filter_table_for_display, is_excluded_claim_entry


class PresentationFilterTests(unittest.TestCase):
    def test_claim_row_and_column_are_removed_from_copy_only(self) -> None:
        source = [
            {"Result record": "FRIEND-CLAIM", "Pooled R²": "0.3301", "Mean-fold R²": "0.2990"},
            {"Gap": "U10", "Area": "Friend claims", "Finding": "No source for .3301/.2990 was found."},
            {"Result record": "VERIFIED-RESULT", "Pooled R²": "0.22", "Mean-fold R²": "0.19",
             "FRIEND-CLAIM note": "not displayed"},
        ]

        displayed = filter_table_for_display(source)

        self.assertEqual(displayed, [{"Result record": "VERIFIED-RESULT", "Pooled R²": "0.22",
                                      "Mean-fold R²": "0.19"}])
        self.assertEqual(len(source), 3)

    def test_dataframe_claim_row_and_column_are_removed(self) -> None:
        source = pandas.DataFrame([
            {"Result record": "FRIEND-CLAIM", "Pooled R²": "0.3301", "FRIEND-CLAIM note": "claim"},
            {"Result record": "VERIFIED-RESULT", "Pooled R²": "0.22", "FRIEND-CLAIM note": ""},
        ])

        displayed = filter_table_for_display(source)

        self.assertEqual(displayed["Result record"].tolist(), ["VERIFIED-RESULT"])
        self.assertNotIn("FRIEND-CLAIM note", displayed.columns)
        self.assertEqual(len(source), 2)

    def test_limitation_record_is_removed_from_presentation(self) -> None:
        self.assertTrue(is_excluded_claim_entry({"issue": "Friend-reported R² claims", "status": "UNVERIFIED"}))
        self.assertFalse(is_excluded_claim_entry({"issue": "Unverified evidence", "status": "UNVERIFIED"}))


if __name__ == "__main__":
    unittest.main()
