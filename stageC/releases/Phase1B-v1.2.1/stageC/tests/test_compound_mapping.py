import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from stage_c.compound_mapping import build_mappings, mapping_coverage

COMPOUNDS=[{"Compound_ID":"C-1","Canonical_Name":"Alpha acid","Aliases":"Alpha | alpha-acid","PubChem_CID":"101","InChIKey":"AAAAAAAAAAAAAA-BBBBBBBBBB-C"},{"Compound_ID":"C-2","Canonical_Name":"Beta acid","Aliases":"Beta","PubChem_CID":"102","InChIKey":"CCCCCCCCCCCCCC-DDDDDDDDDD-E"}]
def food(**kw):
 row={"food_record_id":"F-1","compound_name":"Alpha acid","food_name":"Test food","reported_concentration":"","source_verification_status":"unverified"};row.update(kw);return row

class CompoundMappingTests(unittest.TestCase):
    def test_exact_canonical_name_maps(self):
        m=build_mappings(COMPOUNDS,[food()])[0];self.assertEqual(m["compound_id"],"C-1");self.assertEqual(m["mapping_status"],"Exact identity match")

    def test_exact_structure_key_maps(self):
        m=build_mappings(COMPOUNDS,[food(compound_name="",inchikey="AAAAAAAAAAAAAA-BBBBBBBBBB-C")])[0];self.assertEqual(m["mapping_status"],"Structure-supported match")

    def test_pending_identity_is_not_marked_as_verified_mapping(self):
        pending=[{**COMPOUNDS[0],"StageC_Identity_Verification_Status":"manual review pending"},COMPOUNDS[1]]
        m=build_mappings(pending,[food(compound_name="",inchikey="AAAAAAAAAAAAAA-BBBBBBBBBB-C")])[0]
        self.assertEqual(m["mapping_status"],"Pending identity review")
        self.assertEqual(m["compound_id"],"C-1")

    def test_conflicting_chemical_identifiers_are_ambiguous(self):
        m=build_mappings(COMPOUNDS,[food(pubchem_cid="102",inchikey="AAAAAAAAAAAAAA-BBBBBBBBBB-C")])[0];self.assertEqual(m["mapping_status"],"Ambiguous match");self.assertEqual(m["compound_id"],"")

    def test_alias_requires_explicit_source_verification(self):
        unverified=build_mappings(COMPOUNDS,[food(compound_name="Alpha")])[0]
        verified=build_mappings(COMPOUNDS,[food(compound_name="Alpha",synonym_verification_status="Verified",synonym_source="reviewed source")])[0]
        self.assertEqual(unverified["mapping_status"],"Ambiguous match");self.assertEqual(verified["mapping_status"],"Verified synonym match")

    def test_isomer_specific_key_not_fuzzy_matched(self):
        m=build_mappings(COMPOUNDS,[food(compound_name="Alpha acid",inchikey="ZZZZZZZZZZZZZZ-YYYYYYYYYY-X")])[0]
        self.assertEqual(m["mapping_status"],"Ambiguous match")
        # In real imported rows, contradictory identifiers should not be accepted.
        m=build_mappings(COMPOUNDS,[food(compound_name="Alpha acid",pubchem_cid="102")])[0]
        self.assertEqual(m["mapping_status"],"Ambiguous match")

    def test_coverage_does_not_count_qualitative_context(self):
        result=mapping_coverage(COMPOUNDS,[],[]);self.assertEqual(result["compounds_with_no_quantitative_data"],2)
        pending=[{**COMPOUNDS[0],"StageC_Identity_Verification_Status":"manual review pending"},COMPOUNDS[1]]
        self.assertEqual(mapping_coverage(pending,[],[])["compounds_pending_identity_review"],1)

    def test_quantitative_coverage_requires_food_state_basis_and_ordinary_food(self):
        record=food(reported_concentration="5",reported_unit="mg/kg",raw_or_processed_state="raw",moisture_basis="wet weight",food_use_classification="ordinary food",source_classification="Primary analytical measurement",source_verification_status="Verified")
        mapped=build_mappings(COMPOUNDS,[record])
        self.assertEqual(mapped[0]["quantitative_data_available"],"true")
        ingredient=build_mappings(COMPOUNDS,[{**record,"food_use_classification":"food ingredient"}])
        self.assertEqual(ingredient[0]["quantitative_data_available"],"true")
        beverage=build_mappings(COMPOUNDS,[{**record,"food_use_classification":"prepared beverage"}])
        self.assertEqual(beverage[0]["quantitative_data_available"],"true")
        missing_basis=build_mappings(COMPOUNDS,[{**record,"moisture_basis":""}])
        self.assertEqual(missing_basis[0]["quantitative_data_available"],"false")

    def test_rejected_review_decision_is_preserved(self):
        row=food(mapping_review_status="Rejected match",mapping_review_compound_id="C-1",mapping_review_rationale="Isomer mismatch",mapping_review_source="manual review log")
        m=build_mappings(COMPOUNDS,[row])[0];self.assertEqual(m["mapping_status"],"Rejected match");self.assertEqual(m["compound_id"],"")

if __name__ == "__main__": unittest.main()
