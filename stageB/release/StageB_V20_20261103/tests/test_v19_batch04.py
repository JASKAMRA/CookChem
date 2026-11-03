import csv
import unittest
from pathlib import Path

from scripts.validate_v19_batch04 import validate, validate_records


class V19Batch04Tests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]
        parent = self.root.parent / "StageB_V18_20261103"

        def read(base, rel):
            with (base / rel).open(encoding="utf-8-sig", newline="") as handle:
                return list(csv.DictReader(handle))

        self.e = read(self.root, "data/interaction_evidence.csv")
        self.a = read(self.root, "provenance/source_audit.csv")
        self.c = read(self.root, "provenance/claim_support_and_verification.csv")
        self.w = read(self.root, "data/warning_ledger.csv")
        self.wa = read(self.root, "validation/V19_warning_audit.csv")
        self.r = read(self.root, "validation/V19_batch_004_review.csv")
        self.b = read(self.root, "data/publication_bibliography.csv")
        self.be = read(parent, "data/interaction_evidence.csv")
        self.bw = read(parent, "data/warning_ledger.csv")

    def errors(self, e=None, a=None, c=None, w=None, wa=None, r=None, b=None):
        return validate_records(
            self.root, e if e is not None else self.e, a if a is not None else self.a,
            c if c is not None else self.c, w if w is not None else self.w,
            wa if wa is not None else self.wa, r if r is not None else self.r,
            b if b is not None else self.b, self.be, self.bw,
        )

    def test_actual_batch_passes(self):
        self.assertEqual(validate(self.root), [])

    def test_four_records_are_required(self):
        self.assertTrue(any("all four target" in x for x in self.errors(r=self.r[:-1])))

    def test_graph_only_cinnamaldehyde_values_cannot_be_digitized(self):
        e = [dict(x) for x in self.e]
        row = next(x for x in e if x["Evidence_ID"] == "SB-0138")
        row["Quantitative_Outcome"] = "CI=0.2; exact numerical outcome"
        self.assertTrue(any("graph-only CI" in x or "source outcome or limitation" in x for x in self.errors(e=e)))

    def test_lovo_antagonism_cannot_be_dropped(self):
        e = [dict(x) for x in self.e]
        row = next(x for x in e if x["Evidence_ID"] == "SB-0139")
        row["Outcome"] = "synergy_detected"
        self.assertTrue(any("LoVo concentration-dependent antagonism" in x for x in self.errors(e=e)))

    def test_in_vitro_duration_discrepancy_must_remain_visible(self):
        e = [dict(x) for x in self.e]
        row = next(x for x in e if x["Evidence_ID"] == "SB-0182")
        row["Quantitative_Outcome"] = row["Quantitative_Outcome"].replace("V19-W09", "")
        self.assertTrue(any("V19-W09" in x for x in self.errors(e=e)))

    def test_animal_regimen_discrepancy_must_remain_visible(self):
        e = [dict(x) for x in self.e]
        row = next(x for x in e if x["Evidence_ID"] == "SB-0183")
        row["Dose"] = "AITC daily; cisplatin once"
        self.assertTrue(any("conflicting dosing frequency" in x for x in self.errors(e=e)))

    def test_unresolved_scientific_warning_cannot_be_closed(self):
        w, wa = [dict(x) for x in self.w], [dict(x) for x in self.wa]
        next(x for x in w if x["Warning_ID"] == "V19-W07")["Audit_Status"] = "RESOLVED"
        next(x for x in wa if x["Warning_ID"] == "V19-W07")["V19_Status"] = "RESOLVED"
        self.assertTrue(any("must remain open" in x for x in self.errors(w=w, wa=wa)))

    def test_resolved_cache_warning_requires_resolution_evidence(self):
        w = [dict(x) for x in self.w]
        next(x for x in w if x["Warning_ID"] == "V19-W10")["Resolution_Source"] = ""
        self.assertTrue(any("resolved warning lacks Resolution_Source" in x for x in self.errors(w=w)))

    def test_broken_cache_locator_is_detected(self):
        a = [dict(x) for x in self.a]
        next(x for x in a if x["Evidence_ID"] == "SB-0183")["Source_Cache"] = "release_v7/sources/missing.json"
        self.assertTrue(any("not repaired or consistent" in x for x in self.errors(a=a)))

    def test_bibliography_cache_path_must_match(self):
        b = [dict(x) for x in self.b]
        next(x for x in b if x["PMID"] == "24276478")["Source"] = "sources/missing.json"
        self.assertTrue(any("bibliography metadata source path is not repaired" in x for x in self.errors(b=b)))

    def test_no_doi_is_not_fabricated(self):
        b = [dict(x) for x in self.b]
        next(x for x in b if x["PMID"] == "26396928")["DOI"] = "10.0000/fabricated"
        self.assertTrue(any("unsupported DOI must remain blank" in x for x in self.errors(b=b)))

    def test_inherited_warning_cannot_disappear(self):
        w = [dict(x) for x in self.w if x["Warning_ID"] != "V3-W02"]
        wa = [dict(x) for x in self.wa if x["Warning_ID"] != "V3-W02"]
        self.assertTrue(any("all 70 inherited" in x or "match uniquely" in x for x in self.errors(w=w, wa=wa)))


if __name__ == "__main__":
    unittest.main()
