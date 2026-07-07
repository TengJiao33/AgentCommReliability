import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from run_mca_pre_kv_then_mad import _stable_seed  # noqa: E402


class MCAPreKVThenMADTests(unittest.TestCase):
    def test_stable_seed_is_deterministic(self):
        first = _stable_seed(42, "math500", "row-1", "first_round", 0)
        second = _stable_seed(42, "math500", "row-1", "first_round", 0)

        self.assertEqual(first, second)

    def test_stable_seed_separates_conditions(self):
        first_round = _stable_seed(42, "math500", "row-1", "first_round", 0)
        debate = _stable_seed(42, "math500", "row-1", "debate", 0)
        other_agent = _stable_seed(42, "math500", "row-1", "first_round", 1)

        self.assertNotEqual(first_round, debate)
        self.assertNotEqual(first_round, other_agent)


if __name__ == "__main__":
    unittest.main()
