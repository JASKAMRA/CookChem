import csv
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_v17
import validate_v16_warnings as warning_validator


def read(rel):
    with (ROOT / rel).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


class V17IntegrityTests(unittest.TestCase):
    def test_inherited_records_and_warning_ledger_validate(self):
        self.assertEqual([], validate_v17.validate())

    def test_every_v16_warning_id_and_historical_fields_are_preserved(self):
        baseline = {r["Warning_ID"]: r for r in read("../StageB_V16_20261102/data/warning_ledger.csv")}
        current = {r["Warning_ID"]: r for r in read("data/warning_ledger.csv")}
        self.assertTrue(baseline.keys() <= current.keys())
        for wid, row in baseline.items():
            self.assertTrue(all(current[wid].get(k) == v for k, v in row.items()), wid)

    def test_invalid_closure_and_dangling_evidence_are_rejected(self):
        w = read("data/warning_ledger.csv")
        c, e = read("data/compound_registry.csv"), read("data/interaction_evidence.csv")
        s, b = read("data/study_registry.csv"), read("data/publication_bibliography.csv")
        mutated = [dict(r) for r in w]
        row = next(r for r in mutated if r["Audit_Status"] == "STILL_VALID")
        row["Audit_Status"] = "RESOLVED"
        row["Audit_Verification_Reference"] = ""
        self.assertTrue(any("resolved warning" in x for x in warning_validator.validate(mutated, c, e, s, b)))
        mutated = [dict(r) for r in w]
        row = next(r for r in mutated if "SB-" in r["Affected"])
        row["Affected"] = "SB-DOES-NOT-EXIST"
        self.assertTrue(any("unknown evidence reference" in x for x in warning_validator.validate(mutated, c, e, s, b)))

    def test_batch_08_additions_have_compound_specific_primary_evidence(self):
        compounds = read("data/compound_registry.csv")
        evidence = read("data/interaction_evidence.csv")
        new_compounds = [r for r in compounds if r.get("Origin") == "v17_batch_08"]
        new_evidence = [r for r in evidence if r.get("Evidence_ID", "") in {f"SB-V17-{n:03d}" for n in range(1, 5)}]
        self.assertEqual({"Apigetrin", "Myricitrin", "Prunin", "Quercitrin"}, {r["Canonical_Name"] for r in new_compounds})
        self.assertEqual(4, len(new_evidence))
        self.assertTrue(all(r["PMID"] == "37252098" and r["Evidence_Type"] == "In vitro" for r in new_evidence))
        self.assertTrue(all("IC50=" in r["Quantitative_Outcome"] and "Table 1" in r["Source_Locator"] for r in new_evidence))
        self.assertTrue(all("No clinical extrapolation" in r["Clinical_Extrapolation"] for r in new_evidence))

    def test_batch_warning_remains_open_and_is_not_a_clinical_claim(self):
        warnings = {r["Warning_ID"]: r for r in read("data/warning_ledger.csv")}
        row = warnings["V17-W01"]
        self.assertEqual("STILL_VALID", row["Audit_Status"])
        self.assertEqual("NOT_RECORDED", row["Inherited_Severity"])
        self.assertIn("No human", row["Remaining_Limitations"])
        self.assertTrue(all(r["Warning_ID"] in warnings for r in read("validation/V17_warning_reaudit_checkpoint.csv")))

    def test_batch_08_food_context_and_source_audit_are_linked_per_compound(self):
        compounds = [r for r in read("data/compound_registry.csv") if r.get("Origin") == "v17_batch_08"]
        food = {r["Compound_ID"]: r for r in read("provenance/food_context_audit.csv")}
        names_in_sources = {r["Compound"] for r in read("provenance/source_register.csv") if r.get("Primary_source")}
        for compound in compounds:
            self.assertTrue(food[compound["Compound_ID"]]["Context_Source"], compound["Compound_ID"])
            self.assertIn(compound["Canonical_Name"], names_in_sources)

    def test_v17_batch_source_audit_mutation_is_rejected(self):
        import tempfile
        from unittest.mock import patch
        good_rows = validate_v17.rows
        def altered(root, rel):
            values = good_rows(root, rel)
            if rel == "provenance/source_audit.csv":
                return [r for r in values if r.get("Evidence_ID") != "SB-V17-001"]
            return values
        with patch.object(validate_v17, "rows", side_effect=altered):
            errors = validate_v17.validate()
        self.assertTrue(any("V17 source audit missing: SB-V17-001" in e for e in errors))

    def test_warning_id_disappearance_and_duplicate_mutations_are_rejected(self):
        warnings = read("data/warning_ledger.csv")
        compounds, evidence = read("data/compound_registry.csv"), read("data/interaction_evidence.csv")
        studies, bibliography = read("data/study_registry.csv"), read("data/publication_bibliography.csv")
        missing = [dict(r) for r in warnings if r["Warning_ID"] != "V16-W02"]
        self.assertTrue(any("warning IDs missing or duplicated" in e for e in warning_validator.validate(warnings + [dict(warnings[-1])], compounds, evidence, studies, bibliography)))
        # The V17 release validator additionally compares every row to the V16 baseline.
        from unittest.mock import patch
        original_rows = validate_v17.rows
        def without_inherited(root, rel):
            result = original_rows(root, rel)
            return [r for r in result if r.get("Warning_ID") != "V16-W02"] if root == validate_v17.ROOT and rel == "data/warning_ledger.csv" else result
        with patch.object(validate_v17, "rows", side_effect=without_inherited):
            errors = validate_v17.validate()
        self.assertTrue(any("inherited V16 warning disappeared" in e for e in errors))
        duplicate = [dict(r) for r in warnings] + [dict(warnings[-1])]
        self.assertTrue(any("warning IDs missing or duplicated" in e for e in warning_validator.validate(duplicate, compounds, evidence, studies, bibliography)))

    def test_warning_summary_mutations_cannot_hide_ids_or_status_count_errors(self):
        import json
        summary = json.loads((ROOT / "validation/V17_warning_audit_status.json").read_text(encoding="utf-8"))
        warnings = read("data/warning_ledger.csv")
        summary["current_warning_ids"] = summary["current_warning_ids"][:-1]
        self.assertTrue(any("ID set does not match" in e for e in validate_v17.validate_warning_summary(warnings, summary)))
        summary = json.loads((ROOT / "validation/V17_warning_audit_status.json").read_text(encoding="utf-8"))
        summary["current_ledger_status_counts"]["STILL_VALID"] += 1
        self.assertTrue(any("status counts do not match" in e for e in validate_v17.validate_warning_summary(warnings, summary)))

    def test_full_warning_audit_claim_is_rejected_when_unaudited_rows_remain(self):
        import json
        summary = json.loads((ROOT / "validation/V17_warning_audit_status.json").read_text(encoding="utf-8"))
        summary["v17_reaudit_complete"] = True
        summary["v17_reaudited_warning_rows"] = 0
        self.assertTrue(any("claims incomplete inherited re-audit" in e for e in validate_v17.validate_warning_summary(read("data/warning_ledger.csv"), summary)))

    def test_fresh_warning_audit_reconciles_all_70_ids_and_dispositions(self):
        import json
        warnings = read("data/warning_ledger.csv")
        audit = read("validation/V17_warning_by_warning_audit.csv")
        summary = json.loads((ROOT / "validation/V17_warning_audit_status.json").read_text(encoding="utf-8"))
        self.assertEqual(70, len(audit))
        self.assertEqual([], validate_v17.validate_warning_audit_report(warnings, audit, summary))

    def test_warning_audit_rejects_missing_rows_and_unsupported_closure(self):
        import json
        warnings = read("data/warning_ledger.csv")
        audit = read("validation/V17_warning_by_warning_audit.csv")
        summary = json.loads((ROOT / "validation/V17_warning_audit_status.json").read_text(encoding="utf-8"))
        self.assertTrue(any("IDs do not match" in e for e in validate_v17.validate_warning_audit_report(warnings, audit[:-1], summary)))
        mutated = [dict(r) for r in audit]
        row = next(r for r in mutated if r["V17_Audit_Status"] == "STILL_VALID")
        row["V17_Audit_Status"] = "RESOLVED"
        row["Technical_Repair"] = ""
        self.assertTrue(any("resolved V17 warning lacks verified corrective action" in e for e in validate_v17.validate_warning_audit_report(warnings, mutated, summary)))

    def test_batch_09_sunset_yellow_has_compound_specific_potency_and_warning(self):
        compounds = [r for r in read("data/compound_registry.csv") if r.get("Origin") == "v17_batch_09"]
        self.assertEqual(1, len(compounds))
        evidence = [r for r in read("data/interaction_evidence.csv") if r.get("Release_Origin") == "v17_batch_09"]
        self.assertEqual(1, len(evidence))
        self.assertEqual("32571913", evidence[0]["PMID"])
        self.assertIn("68.4 μM", evidence[0]["Quantitative_Outcome"])
        warnings = {r["Warning_ID"]: r for r in read("data/warning_ledger.csv")}
        self.assertEqual("STILL_VALID", warnings["V17-W02"]["Audit_Status"])

    def test_batch_10_preserves_s_equol_stereochemistry_and_conditional_food_origin(self):
        compounds = [r for r in read("data/compound_registry.csv") if r.get("Origin") == "v17_batch_10"]
        self.assertEqual(1, len(compounds))
        self.assertEqual("S-equol", compounds[0]["Canonical_Name"])
        self.assertEqual("ADFCQWZHKCXPAJ-GFCCVEGCSA-N", compounds[0]["InChIKey"])
        self.assertIn("microbiome-dependent", compounds[0]["Food_Context"])
        evidence = [r for r in read("data/interaction_evidence.csv") if r.get("Release_Origin") == "v17_batch_10"]
        self.assertEqual("29934673", evidence[0]["PMID"])
        self.assertIn("18.6 ± 5.6 μM", evidence[0]["Quantitative_Outcome"])
        warning = {r["Warning_ID"]: r for r in read("data/warning_ledger.csv")}["V17-W03"]
        self.assertEqual("STILL_VALID", warning["Audit_Status"])
        self.assertIn("Full journal", warning["Remaining_Limitations"])

    def test_batch_11_keeps_phloridzin_distinct_from_phloretin_and_links_full_text(self):
        compounds = [r for r in read("data/compound_registry.csv") if r.get("Origin") == "v17_batch_11"]
        self.assertEqual(1, len(compounds))
        self.assertEqual(("Phloridzin", "6072"), (compounds[0]["Canonical_Name"], compounds[0]["PubChem_CID"]))
        evidence = [r for r in read("data/interaction_evidence.csv") if r.get("Release_Origin") == "v17_batch_11"]
        self.assertEqual(1, len(evidence))
        self.assertEqual("34396892", evidence[0]["PMID"])
        self.assertIn("IC50=110 μM", evidence[0]["Quantitative_Outcome"])
        self.assertIn("phloretin", evidence[0]["Limitations"])
        warning = {r["Warning_ID"]: r for r in read("data/warning_ledger.csv")}['V17-W04']
        self.assertEqual("STILL_VALID", warning["Audit_Status"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
