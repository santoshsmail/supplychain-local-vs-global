import unittest

from model import allocate, compare_decisions, source


class ModelTests(unittest.TestCase):
    def test_allocation_default_and_floor(self):
        result = allocate()
        self.assertAlmostEqual(result["system"]["a"], 6.5)
        self.assertAlmostEqual(result["system"]["b"], 3.5)
        self.assertAlmostEqual(result["system"]["score"], 13.5)
        self.assertAlmostEqual(result["local"]["a"], 5)
        self.assertAlmostEqual(result["local"]["score"], 18)
        self.assertTrue(result["binding"])

    def test_nonbinding_floor(self):
        result = allocate(floor=2)
        self.assertFalse(result["binding"])
        self.assertAlmostEqual(result["system"]["a"], result["local"]["a"])

    def test_supply_bounds_and_conservation(self):
        for supply in (0, 6, 10, 16):
            for plan in (allocate(supply=supply, floor=8)[key] for key in ("system", "local")):
                self.assertAlmostEqual(plan["a"] + plan["b"], supply)
                self.assertTrue(0 <= plan["a"] <= 8 and 0 <= plan["b"] <= 8)

    def test_source_default_and_no_disruption(self):
        result = source()
        self.assertAlmostEqual(result["today"]["expected_total"], 8)
        self.assertAlmostEqual(result["long_term"]["local_order"], 20 / 3)
        self.assertAlmostEqual(result["long_term"]["expected_total"], 20 / 3)
        self.assertEqual(source(probability=0)["long_term"]["local_order"], 0)
        self.assertEqual(source(probability=20)["long_term"]["local_order"], 0)

    def test_decisions_reproducible_and_fair_inputs(self):
        first = compare_decisions(seed=123)
        self.assertEqual(first, compare_decisions(seed=123))
        self.assertNotEqual(first["humans"], compare_decisions(seed=124)["humans"])
        self.assertAlmostEqual(first["agents"][0]["score"], first["benchmark"])
        self.assertAlmostEqual(first["agents"][1]["score"], allocate()["local"]["score"])
        for style in first["humans"]:
            self.assertAlmostEqual(style["average_a"] + style["average_b"], 10)
            self.assertGreaterEqual(style["mean_score"], first["benchmark"] - 1e-7)
            self.assertLessEqual(style["min_score"], style["mean_score"])
            self.assertLessEqual(style["mean_score"], style["max_score"])

    def test_equal_priority_gain_seeking_is_neutral(self):
        result = compare_decisions(priority=1, trials=1000)
        gain = result["humans"][1]
        self.assertAlmostEqual(gain["average_a"], 5, delta=0.1)


if __name__ == "__main__":
    unittest.main()
