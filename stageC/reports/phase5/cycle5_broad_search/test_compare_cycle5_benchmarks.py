import unittest

import compare_cycle5_benchmarks as benchmark


class Cycle5BenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.observations = benchmark.read_csv(benchmark.OBSERVATIONS_CSV)
        cls.phase1b = benchmark.read_csv(benchmark.PHASE1B_CSV)

    def test_source_dataset_conversions_and_traceability(self):
        benchmark.validate_observations(self.observations)
        self.assertEqual(len(self.observations), 10)
        rows = {row["observation_id"]: row for row in self.observations}
        self.assertEqual(rows["CHANG2013-SPINACH-LUTEIN-RAW"]["normalized_mg_per_100g"], "0.495")
        self.assertEqual(rows["LEE2018-BROCCOLI-ASCORBIC-RAW"]["normalized_mg_per_100g"], "66.804")

    def test_candidate_matrix_is_ranked_and_multifood(self):
        candidates = benchmark.read_csv(benchmark.CANDIDATES_CSV)
        candidate_ids = [row["candidate_id"] for row in candidates]
        self.assertEqual(len(candidates), 9)
        self.assertEqual(len(candidate_ids), len(set(candidate_ids)))
        self.assertEqual([int(row["rank"]) for row in candidates], list(range(1, 10)))
        self.assertTrue(all(row["exact_gate_or_exclusion_reason"].strip() for row in candidates))
        self.assertGreaterEqual(len({row["food_compound_pair"] for row in candidates}), 5)

    def test_only_two_descriptive_raw_pairs_are_emitted(self):
        comparisons = benchmark.build_comparisons(self.observations, self.phase1b)
        self.assertEqual(len(comparisons), 2)
        self.assertTrue(all(row["status"] == "CONTEXT_LIMITED_SOURCE_TO_SOURCE_ONLY" for row in comparisons))
        self.assertTrue(all("not a model prediction" in row["scope"] for row in comparisons))
        by_food = {row["food_name"]: row for row in comparisons}
        self.assertEqual(by_food["Spinach"]["phase1b_record_id"], "CHUNG2004-SPINACH-5281243")
        self.assertEqual(by_food["Broccoli"]["phase1b_record_id"], "WATADA1982-BROCCOLI-ASCORBIC-ACID")

    def test_duplicate_observation_is_rejected(self):
        duplicate = list(self.observations)
        duplicate.append(dict(self.observations[0]))
        with self.assertRaisesRegex(ValueError, "Duplicate observation_id"):
            benchmark.validate_observations(duplicate)

    def test_incorrect_conversion_is_rejected(self):
        mutated = [dict(row) for row in self.observations]
        mutated[0]["normalized_mg_per_100g"] = "9.99"
        with self.assertRaisesRegex(ValueError, "Unit conversion mismatch"):
            benchmark.validate_observations(mutated)


if __name__ == "__main__":
    unittest.main()
