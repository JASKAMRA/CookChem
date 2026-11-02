import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from stage_c.compound_mapping import build_mappings
from stage_c.exposure_engine import calculate_exposure,aggregate_exposures
from stage_c.stage_b_connector import load_stage_b
from stage_c.validation import validate_all
from stage_c.food_composition import load_food_data
from stage_c.compound_mapping import load_mappings
from stage_c.provenance import project_root

class PhaseOneIntegrationTests(unittest.TestCase):
    def test_authoritative_compound_identity_to_synthetic_measurement_to_estimate(self):
        stage_b=load_stage_b();compounds=stage_b["source_files"]["compound_registry.csv"]
        compound=compounds[0];food={"food_record_id":"SYN-F-1","compound_id":compound["Compound_ID"],"compound_name":compound["Canonical_Name"],"pubchem_cid":compound["PubChem_CID"],"inchikey":compound["InChIKey"],"food_name":"Synthetic test matrix","reported_concentration":"5","reported_unit":"mg/kg","normalized_concentration":"5","normalized_unit":"mg/kg","raw_or_processed_state":"raw","food_use_classification":"ordinary food","moisture_basis":"wet weight","source_title":"Synthetic test fixture; not empirical data","source_url":"","source_classification":"Primary analytical measurement","source_verification_status":"Verified"}
        mapping=build_mappings(compounds,[food]);self.assertEqual(mapping[0]["compound_id"],compound["Compound_ID"])
        estimate=calculate_exposure({"estimate_id":"SYN-1","compound_id":compound["Compound_ID"],"food_record_id":"SYN-F-1","ingredient_quantity":"0.2","ingredient_unit":"kg","serving_mass":"0.2","serving_unit":"kg","consumed_fraction":"0.5","period_id":"synthetic-meal"},{"SYN-F-1":food},mapping,{c["Compound_ID"]:c for c in compounds},stage_b["release"]["manifest_sha256"],timestamp="2026-01-01T00:00:00Z")
        self.assertEqual(estimate["calculation_status"],"Complete");self.assertEqual(estimate["estimated_consumed_amount"],"0.50")
        self.assertEqual(estimate["stage_b_release_reference"],"StageB_Final")
        self.assertEqual(validate_all([food],mapping,[estimate],{c["Compound_ID"] for c in compounds})["status"],"PASS")

    def test_real_stage_b_context_alone_produces_incomplete_estimate(self):
        stage_b=load_stage_b();compound=stage_b["source_files"]["compound_registry.csv"][0]
        food={"food_record_id":"NO-QUANT-DATA","compound_id":compound["Compound_ID"],"compound_name":compound["Canonical_Name"],"food_name":compound["Food_Context"],"reported_concentration":"","normalized_concentration":"","normalized_unit":"mg/kg","raw_or_processed_state":"","moisture_basis":"","source_verification_status":"unverified","source_classification":"Missing data"}
        m=build_mappings([compound],[food]);out=calculate_exposure({"compound_id":compound["Compound_ID"],"food_record_id":"NO-QUANT-DATA","ingredient_quantity":"0.2","ingredient_unit":"kg","consumed_fraction":"1"},{food["food_record_id"]:food},m,{compound["Compound_ID"]:compound})
        self.assertNotEqual(out["calculation_status"],"Complete");self.assertEqual(out["estimated_consumed_amount"],"")

    def test_phase1b_verified_food_records_map_and_calculate_with_warning(self):
        stage=project_root()/"stageC"
        foods=load_food_data(stage/"data"/"food_composition"/"food_composition.csv")
        mappings=load_mappings(stage/"data"/"compound_food_mapping"/"compound_food_mapping.csv")
        data=load_stage_b(); compounds={c["Compound_ID"]:c for c in data["source_files"]["compound_registry.csv"]}
        self.assertEqual(len(foods),14)
        expected={
            "USDA-FLAV33-NDB09003-EPICATECHIN":("(-)-Epicatechin","7.53","CHEM-PUBCHEM-72276"),
            "USDA-FLAV33-NDB09003-CATECHIN":("(+)-Catechin","1.30","CHEM-PUBCHEM-9064"),
            "USDA-FLAV33-NDB19165-EPICATECHIN":("(-)-Epicatechin","196.43","CHEM-PUBCHEM-72276"),
            "USDA-FLAV33-NDB19165-CATECHIN":("(+)-Catechin","64.82","CHEM-PUBCHEM-9064"),
            "USDA-FLAV33-NDB99069-EGCG":("(-)-Epigallocatechin 3-gallate","26.05","MOL-6B599D234F2062A2"),
            "USDA-FLAV33-NDB99069-THEAFLAVIN":("Theaflavin","0.12","MOL-V10-135403798"),
            "USDA-FDC-SRLEGACY-171890-CAFFEINE":("Caffeine","40","MOL-693364CB16A9EA2D"),
            "USDA-ISOFLAV-R21-NDB11001-FORMONONETIN":("Formononetin","1.43","MOL-V9-5280378"),
            "USDA-ISOFLAV-R21-NDB11001-BIOCHANIN-A":("Biochanin A","0.04","MOL-V9-5280373"),
        }
        self.assertTrue(set(expected).issubset({r["food_record_id"] for r in foods}))
        by_id={r["food_record_id"]:r for r in foods}
        for food_id, (name, concentration, compound_id) in expected.items():
            food=by_id[food_id]
            self.assertEqual(food["compound_name"],name)
            mapping=next(m for m in mappings if m["food_record_id"]==food["food_record_id"])
            expected_mapping_status="Verified synonym match" if food_id.endswith("EGCG") else "Exact identity match"
            self.assertEqual(mapping["mapping_status"],expected_mapping_status)
            self.assertEqual(mapping["compound_id"],compound_id)
            self.assertEqual(food["reported_concentration"],concentration)
            estimate=calculate_exposure({"estimate_id":"INTEGRATION-"+food["food_record_id"],"compound_id":mapping["compound_id"],"food_record_id":food["food_record_id"],"ingredient_quantity":"100","ingredient_unit":"g","serving_mass":"100","serving_unit":"g","consumed_fraction":"1"},{food["food_record_id"]:food},[mapping],compounds,data["release"]["manifest_sha256"],timestamp="2026-01-01T00:00:00Z")
            self.assertEqual(estimate["calculation_status"],"Complete")
            if compound_id in {"CHEM-PUBCHEM-72276","CHEM-PUBCHEM-9064"}:
                self.assertIn("V11-W02",estimate["warning_identifiers"])
            self.assertTrue(estimate["provenance"].get("stage_b_manifest_sha256"))

    def test_batch_009_primary_measurements_map_without_basis_inference(self):
        stage=project_root()/"stageC"
        foods=load_food_data(stage/"data"/"food_composition"/"food_composition.csv")
        mappings=load_mappings(stage/"data"/"compound_food_mapping"/"compound_food_mapping.csv")
        expected={
            "JAPAN-GINGER-2017-6GINGEROL":("CHEM-PUBCHEM-442793","268.3","mg/kg"),
            "JAPAN-GINGER-2017-6SHOGAOL":("MOL-V10-5281794","133.2","mg/kg"),
            "HOP-HPLC-2019-XANTHOHUMOL-H":("MOL-V10-639665","855.68","mg/kg"),
            "CAPSAICIN-2026-HABANERO-DW":("MOL-1F36FE6AE1F46586","4777.56","mg/kg"),
            "KOREA-PEPPER-2021-PIPERINE":("MOL-A888520F9EA99648","44180","mg/kg"),
        }
        by_id={r["food_record_id"]:r for r in foods}
        for food_id,(compound_id,concentration,unit) in expected.items():
            food=by_id[food_id]
            mapping=next(m for m in mappings if m["food_record_id"]==food_id)
            self.assertEqual(mapping["mapping_status"],"Exact identity match")
            self.assertEqual(mapping["compound_id"],compound_id)
            self.assertEqual(food["normalized_concentration"],concentration)
            self.assertEqual(food["normalized_unit"],unit)
            self.assertEqual(food["source_verification_status"],"Full-text verified")
        self.assertIn("dry-weight",by_id["CAPSAICIN-2026-HABANERO-DW"]["moisture_basis"].lower())
        self.assertIn("not separately reported",by_id["KOREA-PEPPER-2021-PIPERINE"]["moisture_basis"])

    def test_usda_biochanin_a_maps_exactly_without_inferred_metadata(self):
        stage=project_root()/"stageC"
        foods=load_food_data(stage/"data"/"food_composition"/"food_composition.csv")
        mappings=load_mappings(stage/"data"/"compound_food_mapping"/"compound_food_mapping.csv")
        data=load_stage_b(); compounds={c["Compound_ID"]:c for c in data["source_files"]["compound_registry.csv"]}
        food=next(r for r in foods if r["food_record_id"]=="USDA-ISOFLAV-R21-NDB11001-BIOCHANIN-A")
        mapping=next(r for r in mappings if r["food_record_id"]==food["food_record_id"])
        self.assertEqual(mapping["compound_id"],"MOL-V9-5280373")
        self.assertEqual(food["reported_concentration"],"0.04")
        self.assertEqual(food["sample_size"],"")
        estimate=calculate_exposure({"estimate_id":"ISOFLAV-BIOCHANIN-A-100G","compound_id":mapping["compound_id"],"food_record_id":food["food_record_id"],"ingredient_quantity":"100","ingredient_unit":"g","serving_mass":"100","serving_unit":"g","consumed_fraction":"1"},{food["food_record_id"]:food},[mapping],compounds,data["release"]["manifest_sha256"],timestamp="2026-01-01T00:00:00Z")
        self.assertEqual(estimate["calculation_status"],"Complete")
        self.assertEqual(estimate["estimated_consumed_amount"],"0.040")

    def test_usda_formononetin_uses_exact_other_phytoestrogen_measurement(self):
        stage=project_root()/"stageC"
        foods=load_food_data(stage/"data"/"food_composition"/"food_composition.csv")
        mappings=load_mappings(stage/"data"/"compound_food_mapping"/"compound_food_mapping.csv")
        data=load_stage_b(); compounds={c["Compound_ID"]:c for c in data["source_files"]["compound_registry.csv"]}
        food=next(r for r in foods if r["food_record_id"]=="USDA-ISOFLAV-R21-NDB11001-FORMONONETIN")
        mapping=next(r for r in mappings if r["food_record_id"]==food["food_record_id"])
        self.assertEqual(mapping["compound_id"],"MOL-V9-5280378")
        self.assertEqual(food["reported_concentration"],"1.43")
        estimate=calculate_exposure({"estimate_id":"ISOFLAV-FORMONONETIN-100G","compound_id":mapping["compound_id"],"food_record_id":food["food_record_id"],"ingredient_quantity":"100","ingredient_unit":"g","serving_mass":"100","serving_unit":"g","consumed_fraction":"1"},{food["food_record_id"]:food},[mapping],compounds,data["release"]["manifest_sha256"],timestamp="2026-01-01T00:00:00Z")
        self.assertEqual(estimate["calculation_status"],"Complete")
        self.assertEqual(estimate["estimated_consumed_amount"],"1.430")

    def test_official_fdc_coffee_caffeine_uses_usda_portion_mass(self):
        stage=project_root()/"stageC"
        foods=load_food_data(stage/"data"/"food_composition"/"food_composition.csv")
        mappings=load_mappings(stage/"data"/"compound_food_mapping"/"compound_food_mapping.csv")
        data=load_stage_b(); compounds={c["Compound_ID"]:c for c in data["source_files"]["compound_registry.csv"]}
        food=next(r for r in foods if r["food_record_id"]=="USDA-FDC-SRLEGACY-171890-CAFFEINE")
        mapping=next(r for r in mappings if r["food_record_id"]==food["food_record_id"])
        self.assertEqual(mapping["compound_id"],"MOL-693364CB16A9EA2D")
        self.assertEqual(food["reported_concentration"],"40")
        self.assertEqual(food["reported_unit"],"mg/100g")
        estimate=calculate_exposure({"estimate_id":"FDC-COFFEE-1-CUP","compound_id":mapping["compound_id"],"food_record_id":food["food_record_id"],"ingredient_quantity":"237","ingredient_unit":"g","serving_mass":"237","serving_unit":"g","consumed_fraction":"1","period_id":"illustrative-usda-srlegacy-coffee-cup"},{food["food_record_id"]:food},[mapping],compounds,data["release"]["manifest_sha256"],timestamp="2026-01-01T00:00:00Z")
        self.assertEqual(estimate["calculation_status"],"Complete")
        self.assertEqual(estimate["estimated_consumed_amount"],"94.800")

if __name__=="__main__":unittest.main()
