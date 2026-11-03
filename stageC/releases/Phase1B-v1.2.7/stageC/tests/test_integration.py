import json
import sys
import unittest
import csv
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
    def test_final_contextual_reconciliation_stays_separate_from_food_coverage(self):
        root=project_root()/"stageC"
        context=root/"reports"/"phase1b"/"batches"/"batch_100_contextual_reconciliation"
        with (context/"CONTEXTUAL_QUANTITATIVE_SCREEN.csv").open(encoding="utf-8-sig",newline="") as stream:
            records=list(csv.DictReader(stream))
        coverage=json.loads((context/"CONTEXT_COVERAGE.json").read_text(encoding="utf-8"))
        self.assertTrue(all(r["phase1b_food_eligible"]=="false" for r in records))
        numeric={r["compound_id"] for r in records if r["reported_value"]}
        missing={r["compound_id"] for r in records if not r["reported_value"]}
        self.assertEqual(len(numeric),8)
        self.assertEqual(len(missing),2)
        self.assertEqual(len(numeric|missing),10)
        self.assertEqual(coverage["ordinary_food_coverage"],109)
        self.assertEqual(coverage["final_10_with_numeric_contextual_leads"],8)
        active=load_food_data(root/"data"/"food_composition"/"food_composition.csv")
        active_sources={r["source_url"] for r in active}
        contextual_sources={r["source"] for r in records if r["reported_value"]}
        # A later, independently verified ordinary-tea source may cover an ID
        # that also has an excluded medicinal-root value. Test the source gate.
        self.assertTrue(contextual_sources.isdisjoint(active_sources))

    def test_authoritative_compound_identity_to_synthetic_measurement_to_estimate(self):
        stage_b=load_stage_b();compounds=stage_b["source_files"]["compound_registry.csv"]
        compound=compounds[0];food={"food_record_id":"SYN-F-1","compound_id":compound["Compound_ID"],"compound_name":compound["Canonical_Name"],"pubchem_cid":compound["PubChem_CID"],"inchikey":compound["InChIKey"],"food_name":"Synthetic test matrix","reported_concentration":"5","reported_unit":"mg/kg","normalized_concentration":"5","normalized_unit":"mg/kg","raw_or_processed_state":"raw","food_use_classification":"ordinary food","moisture_basis":"wet weight","source_title":"Synthetic test fixture; not empirical data","source_url":"","source_classification":"Primary analytical measurement","source_verification_status":"Verified"}
        mapping=build_mappings(compounds,[food]);self.assertEqual(mapping[0]["compound_id"],compound["Compound_ID"])
        estimate=calculate_exposure({"estimate_id":"SYN-1","compound_id":compound["Compound_ID"],"food_record_id":"SYN-F-1","ingredient_quantity":"0.2","ingredient_unit":"kg","serving_mass":"0.2","serving_unit":"kg","consumed_fraction":"0.5","period_id":"synthetic-meal"},{"SYN-F-1":food},mapping,{c["Compound_ID"]:c for c in compounds},stage_b["release"]["manifest_sha256"],timestamp="2026-01-01T00:00:00Z")
        self.assertEqual(estimate["calculation_status"],"Complete");self.assertEqual(estimate["estimated_consumed_amount"],"0.50")
        self.assertEqual(estimate["stage_b_release_reference"],"StageB_FINALIZED")
        self.assertEqual(validate_all([food],mapping,[estimate],{c["Compound_ID"] for c in compounds})["status"],"PASS")

    def test_real_stage_b_context_alone_produces_incomplete_estimate(self):
        stage_b=load_stage_b();compound=stage_b["source_files"]["compound_registry.csv"][0]
        food={"food_record_id":"NO-QUANT-DATA","compound_id":compound["Compound_ID"],"compound_name":compound["Canonical_Name"],"food_name":compound["Food_Context"],"reported_concentration":"","normalized_concentration":"","normalized_unit":"mg/kg","raw_or_processed_state":"","moisture_basis":"","source_verification_status":"unverified","source_classification":"Missing data"}
        m=build_mappings([compound],[food]);out=calculate_exposure({"compound_id":compound["Compound_ID"],"food_record_id":"NO-QUANT-DATA","ingredient_quantity":"0.2","ingredient_unit":"kg","consumed_fraction":"1"},{food["food_record_id"]:food},m,{compound["Compound_ID"]:compound})
        self.assertNotEqual(out["calculation_status"],"Complete");self.assertEqual(out["estimated_consumed_amount"],"")

    def test_legacy_mappings_for_pending_current_identities_cannot_calculate_exposure(self):
        stage=project_root()/"stageC"
        data=load_stage_b()
        compounds={row["Compound_ID"]:row for row in data["source_files"]["compound_registry.csv"]}
        mappings=load_mappings(stage/"data"/"compound_food_mapping"/"compound_food_mapping.csv")
        pending_ids={
            row["compound_id"] for row in mappings
            if row.get("mapping_status") in {"Exact identity match","Verified synonym match","Structure-supported match"}
            and compounds.get(row.get("compound_id"),{}).get("StageC_Identity_Verification_Status") != "Complete"
        }
        self.assertEqual(len(pending_ids),16)
        for compound_id in pending_ids:
            mapping=next(row for row in mappings if row.get("compound_id")==compound_id)
            food_id="SYNTHETIC-PENDING-"+compound_id
            food={"food_record_id":food_id,"compound_id":compound_id,"compound_name":compounds[compound_id]["Canonical_Name"],"food_name":"Synthetic test matrix","reported_concentration":"5","reported_unit":"mg/kg","normalized_concentration":"5","normalized_unit":"mg/kg","raw_or_processed_state":"raw","food_use_classification":"ordinary food","moisture_basis":"wet weight","source_title":"Synthetic test fixture; not empirical data","source_verification_status":"Verified","source_classification":"Primary analytical measurement"}
            result=calculate_exposure({"compound_id":compound_id,"food_record_id":food_id,"ingredient_quantity":"100","ingredient_unit":"g","consumed_fraction":"1"},{food_id:food},[mapping],compounds)
            self.assertEqual(result["calculation_status"],"Incomplete: unresolved identity")
            self.assertEqual(result["estimated_consumed_amount"],"")

    def test_phase1b_verified_food_records_map_and_calculate_with_warning(self):
        stage=project_root()/"stageC"
        foods=load_food_data(stage/"data"/"food_composition"/"food_composition.csv")
        mappings=load_mappings(stage/"data"/"compound_food_mapping"/"compound_food_mapping.csv")
        data=load_stage_b(); compounds={c["Compound_ID"]:c for c in data["source_files"]["compound_registry.csv"]}
        self.assertEqual(len(foods),len(mappings))
        self.assertGreaterEqual(len(foods),511)
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

    def test_batch_010_primary_measurements_keep_fraction_and_basis(self):
        stage=project_root()/"stageC"
        foods=load_food_data(stage/"data"/"food_composition"/"food_composition.csv")
        mappings=load_mappings(stage/"data"/"compound_food_mapping"/"compound_food_mapping.csv")
        by_id={r["food_record_id"]:r for r in foods}
        expected={
            "B010-BERRY-01":("MOL-25F875E0BC8D5FF1","1.3995","dry weight"),
            "B010-BERRY-02":("MOL-25F8CD05AD250A06","4.6726","dry weight"),
            "B010-BERRY-03":("MOL-V10-637542","0.6611","dry weight"),
            "B010-BERRY-04":("MOL-25433E39C2198405","2.3719","dry weight"),
            "B010-BERRY-05":("CHEM-PUBCHEM-932","0.1406","dry weight"),
            "B010-BERRY-06":("CHEM-PUBCHEM-5281672","0.1189","dry weight"),
            "B010-BERRY-07":("CHEM-PUBCHEM-5281670","4.0738","dry weight"),
            "B010-BERRY-08":("CHEM-PUBCHEM-5280343","0.0186","dry weight"),
            "B010-BERRY-09":("MOL-0DD55E4F408730D4","0.4059","dry weight"),
            "B010-BERRY-10":("MOL-06FA7CEF96696340","0.5113","dry weight"),
            "B010-BERRY-11":("MOL-6213BC022378CC3A","3.8259","dry weight"),
            "B010-BERRY-12":("MOL-V10-637542","4.7476","dry weight"),
            "B010-FURO-01":("CHEM-PUBCHEM-2355","0.0302","food mass basis"),
            "B010-FURO-02":("MOL-V9-6440498","12.2437","food mass basis"),
            "B010-FURO-03":("CHEM-PUBCHEM-5471349","8.3567","food mass basis"),
        }
        self.assertEqual(len(expected),15)
        for food_id,(compound_id,normalized,basis) in expected.items():
            food=by_id[food_id]
            mapping=next(m for m in mappings if m["food_record_id"]==food_id)
            self.assertEqual(mapping["compound_id"],compound_id)
            self.assertEqual(food["normalized_concentration"],normalized)
            self.assertEqual(food["normalized_unit"],"mg/kg")
            self.assertIn(basis,food["moisture_basis"])
            self.assertEqual(food["source_verification_status"],"Full-text verified")
        self.assertIn("free fraction only",by_id["B010-BERRY-01"]["extraction_notes"])
        self.assertEqual(by_id["B010-FURO-01"]["sample_size"],"n=3")

    def test_batch_011_hplc_measurements_keep_fresh_basis_and_exact_analytes(self):
        stage=project_root()/"stageC"
        foods=load_food_data(stage/"data"/"food_composition"/"food_composition.csv")
        mappings=load_mappings(stage/"data"/"compound_food_mapping"/"compound_food_mapping.csv")
        by_id={r["food_record_id"]:r for r in foods}
        expected={
            "B011-HPLC-01":("MOL-V10-135","14.0"),
            "B011-HPLC-02":("MOL-06FA7CEF96696340","832.0"),
            "B011-HPLC-03":("MOL-6213BC022378CC3A","306.0"),
            "B011-HPLC-04":("MOL-25F875E0BC8D5FF1","323.0"),
            "B011-HPLC-05":("MOL-25F8CD05AD250A06","29.80"),
            "B011-HPLC-06":("CHEM-PUBCHEM-5280343","26.60"),
            "B011-HPLC-07":("MOL-3811F42D3C15ED32","116.0"),
        }
        for food_id,(compound_id,normalized) in expected.items():
            food=by_id[food_id]
            mapping=next(m for m in mappings if m["food_record_id"]==food_id)
            self.assertEqual(mapping["compound_id"],compound_id)
            self.assertEqual(food["normalized_concentration"],normalized)
            self.assertEqual(food["normalized_unit"],"mg/kg")
            self.assertEqual(food["moisture_basis"],"fresh weight, edible portion")
            self.assertEqual(food["sample_size"],"n=3 independent measurements")

    def test_batch_012_herb_profiles_preserve_dry_basis_and_semiquantitation(self):
        stage=project_root()/"stageC"
        foods=load_food_data(stage/"data"/"food_composition"/"food_composition.csv")
        mappings=load_mappings(stage/"data"/"compound_food_mapping"/"compound_food_mapping.csv")
        by_id={r["food_record_id"]:r for r in foods}
        expected={
            "B012-HERB-01":("MOL-91A03F746BDB1805","1650.13"),
            "B012-HERB-02":("MOL-91A03F746BDB1805","540.76"),
            "B012-HERB-03":("MOL-91A03F746BDB1805","210.23"),
            "B012-HERB-04":("MOL-91A03F746BDB1805","199.54"),
            "B012-HERB-05":("MOL-91A03F746BDB1805","167.84"),
            "B012-HERB-06":("MOL-91A03F746BDB1805","154.34"),
            "B012-HERB-07":("MOL-V10-442009","0.11"),
            "B012-HERB-08":("MOL-V10-65126","0.65"),
            "B012-HERB-09":("MOL-V10-72","331.45"),
            "B012-HERB-10":("MOL-V10-72","110.01"),
            "B012-HERB-11":("MOL-6213BC022378CC3A","140.05"),
            "B012-HERB-12":("MOL-25F875E0BC8D5FF1","270.05"),
            "B012-HERB-13":("MOL-25F875E0BC8D5FF1","32.12"),
            "B012-HERB-14":("CHEM-PUBCHEM-5280343","170.95"),
            "B012-HERB-15":("CHEM-PUBCHEM-5280343","70.3"),
        }
        for food_id,(compound_id,normalized) in expected.items():
            food=by_id[food_id]
            mapping=next(m for m in mappings if m["food_record_id"]==food_id)
            self.assertEqual(mapping["compound_id"],compound_id)
            self.assertEqual(food["normalized_concentration"],normalized)
            self.assertEqual(food["normalized_unit"],"mg/kg")
            self.assertEqual(food["moisture_basis"],"dry weight, as reported by study")
            self.assertIn("semi-quantitative",food["extraction_notes"])
            self.assertEqual(food["sample_size"],"n=3 (study triplicate)")

    def test_batch_013_native_food_herb_records_preserve_dried_sample_basis(self):
        stage=project_root()/"stageC"
        foods=load_food_data(stage/"data"/"food_composition"/"food_composition.csv")
        mappings=load_mappings(stage/"data"/"compound_food_mapping"/"compound_food_mapping.csv")
        by_id={r["food_record_id"]:r for r in foods}
        expected={
            "B013-NATIVE-01":("MOL-91A03F746BDB1805","945.56"),
            "B013-NATIVE-02":("MOL-91A03F746BDB1805","745.67"),
            "B013-NATIVE-03":("MOL-91A03F746BDB1805","76.57"),
            "B013-NATIVE-04":("MOL-91A03F746BDB1805","23.43"),
            "B013-NATIVE-05":("MOL-6213BC022378CC3A","747.52"),
            "B013-NATIVE-06":("MOL-6213BC022378CC3A","584.07"),
            "B013-NATIVE-07":("MOL-6213BC022378CC3A","238.76"),
            "B013-NATIVE-08":("MOL-6213BC022378CC3A","29.07"),
            "B013-NATIVE-09":("MOL-25F875E0BC8D5FF1","556.8"),
            "B013-NATIVE-10":("MOL-25F875E0BC8D5FF1","11.66"),
            "B013-NATIVE-11":("CHEM-PUBCHEM-5281612","65.61"),
            "B013-NATIVE-12":("MOL-V9-5280442","138.37"),
            "B013-NATIVE-13":("MOL-39FEB7124D04D54E","98.36"),
            "B013-NATIVE-14":("CHEM-PUBCHEM-5281613","45.17"),
            "B013-NATIVE-15":("CHEM-PUBCHEM-5281613","14.04"),
            "B013-NATIVE-16":("CHEM-PUBCHEM-5281613","71.46"),
            "B013-NATIVE-17":("CHEM-PUBCHEM-5281613","10.64"),
            "B013-NATIVE-18":("MOL-3811F42D3C15ED32","64.16"),
            "B013-NATIVE-19":("MOL-3811F42D3C15ED32","12.48"),
            "B013-NATIVE-20":("MOL-25433E39C2198405","116.03"),
            "B013-NATIVE-21":("MOL-25433E39C2198405","135.25"),
        }
        self.assertEqual(len(expected),21)
        for food_id,(compound_id,normalized) in expected.items():
            food=by_id[food_id]
            mapping=next(m for m in mappings if m["food_record_id"]==food_id)
            self.assertEqual(mapping["compound_id"],compound_id)
            self.assertEqual(food["normalized_concentration"],normalized)
            self.assertEqual(food["normalized_unit"],"mg/kg")
            self.assertEqual(food["moisture_basis"],"dried sample; reported per gram of sample")
            self.assertIn("semi-quantified",food["extraction_notes"])
            self.assertEqual(food["sample_size"],"n=3 extraction replicates")


    def test_batch_014_native_fruit_values_preserve_source_state_and_semiquantitation(self):
        stage=project_root()/"stageC"
        foods=load_food_data(stage/"data"/"food_composition"/"food_composition.csv")
        mappings=load_mappings(stage/"data"/"compound_food_mapping"/"compound_food_mapping.csv")
        by_id={r["food_record_id"]:r for r in foods}
        expected={
            "B014-NATIVE-01":("MOL-V10-72","63.56"),
            "B014-NATIVE-03":("MOL-V10-135","11.74"),
            "B014-NATIVE-05":("MOL-25F875E0BC8D5FF1","23.49"),
            "B014-NATIVE-07":("MOL-06FA7CEF96696340","19.24"),
            "B014-NATIVE-10":("MOL-V10-637542","10.56"),
            "B014-NATIVE-11":("MOL-6213BC022378CC3A","134.05"),
            "B014-NATIVE-12":("CHEM-PUBCHEM-5280343","71.46"),
            "B014-NATIVE-14":("CHEM-PUBCHEM-5281672","23.67"),
            "B014-NATIVE-16":("CHEM-PUBCHEM-932","24.72"),
            "B014-NATIVE-17":("MOL-V9-5281654","26.83"),
            "B014-NATIVE-19":("CHEM-PUBCHEM-5280805","56.61"),
        }
        for food_id,(compound_id,normalized) in expected.items():
            food=by_id[food_id]
            mapping=next(m for m in mappings if m["food_record_id"]==food_id)
            self.assertEqual(mapping["compound_id"],compound_id)
            self.assertEqual(food["normalized_concentration"],normalized)
            self.assertEqual(food["normalized_unit"],"mg/kg")
            self.assertEqual(food["raw_or_processed_state"],"dried")
            self.assertIn("dried",food["moisture_basis"])
            self.assertIn("semi-quantification",food["analytical_method"])
            self.assertEqual(food["sample_size"],"n=3 extraction replicates")


    def test_batch_015_raw_common_beans_keep_dry_weight_and_exact_analytes(self):
        stage=project_root()/"stageC"
        foods=load_food_data(stage/"data"/"food_composition"/"food_composition.csv")
        mappings=load_mappings(stage/"data"/"compound_food_mapping"/"compound_food_mapping.csv")
        by_id={r["food_record_id"]:r for r in foods}
        expected={
            "B015-BEAN-01":("MOL-06FA7CEF96696340","0.19"),
            "B015-BEAN-02":("MOL-V10-72","5.15"),
            "B015-BEAN-03":("MOL-V10-135","0.60"),
            "B015-BEAN-04":("MOL-25F875E0BC8D5FF1","0.26"),
            "B015-BEAN-05":("MOL-V10-637542","0.68"),
            "B015-BEAN-06":("MOL-V10-1549091","3.38"),
            "B015-BEAN-07":("CHEM-PUBCHEM-5280343","1.34"),
            "B015-BEAN-08":("MOL-3811F42D3C15ED32","13.54"),
        }
        for food_id,(compound_id,normalized) in expected.items():
            food=by_id[food_id]
            mapping=next(m for m in mappings if m["food_record_id"]==food_id)
            self.assertEqual(mapping["compound_id"],compound_id)
            self.assertEqual(food["normalized_concentration"],normalized)
            self.assertEqual(food["normalized_unit"],"mg/kg")
            self.assertEqual(food["raw_or_processed_state"],"raw")
            self.assertIn("dry weight",food["moisture_basis"])
            self.assertEqual(food["sample_size"],"n=3 extraction replicates")
            self.assertIn("authentic-standard",food["analytical_method"])

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
        self.assertIn("FoodData_Central_sr_legacy_food_csv_2018-04.zip",food["source_url"])
        self.assertIn("nutrient ID 1057",food["database_reference"])
        self.assertIn("8 data points",food["database_reference"])
        self.assertIn("237 g",food["database_reference"])
        self.assertIn("API record",food["extraction_notes"])
        estimate=calculate_exposure({"estimate_id":"FDC-COFFEE-1-CUP","compound_id":mapping["compound_id"],"food_record_id":food["food_record_id"],"ingredient_quantity":"237","ingredient_unit":"g","serving_mass":"237","serving_unit":"g","consumed_fraction":"1","period_id":"illustrative-usda-srlegacy-coffee-cup"},{food["food_record_id"]:food},[mapping],compounds,data["release"]["manifest_sha256"],timestamp="2026-01-01T00:00:00Z")
        self.assertEqual(estimate["calculation_status"],"Complete")
        self.assertEqual(estimate["estimated_consumed_amount"],"94.800")

if __name__=="__main__":unittest.main()



