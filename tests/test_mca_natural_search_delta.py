import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from run_mca_natural_search_delta import (  # noqa: E402
    _condition_counts_update,
    _condition_metrics,
    _other_row_index,
    _parse_int_csv,
    _random_like_same_norm,
    _transition,
)


class MCANaturalSearchDeltaTests(unittest.TestCase):
    def test_parse_int_csv(self):
        self.assertEqual(_parse_int_csv("22, 24,9", name="layers"), [22, 24, 9])

    def test_transition_labels(self):
        self.assertEqual(_transition("Ba", True, True), "BaC_to_C")
        self.assertEqual(_transition("Ba", True, False), "BaC_to_W")
        self.assertEqual(_transition("Ba", False, True), "BaW_to_C")
        self.assertEqual(_transition("Ba", False, False), "BaW_to_W")

    def test_other_row_index_uses_neighbor(self):
        self.assertIsNone(_other_row_index(0, 1))
        self.assertEqual(_other_row_index(0, 3), 1)
        self.assertEqual(_other_row_index(2, 3), 1)

    def test_random_like_same_norm(self):
        import torch

        reference = torch.tensor([3.0, 4.0])
        random_vec = _random_like_same_norm(reference, seed=7)

        self.assertAlmostEqual(
            float(torch.linalg.vector_norm(random_vec).item()),
            float(torch.linalg.vector_norm(reference).item()),
            places=5,
        )

    def test_condition_metrics(self):
        from collections import Counter

        counts = Counter()
        counts["baseline_correct"] = 1
        _condition_counts_update(
            counts,
            condition="same_question_peer_delta",
            baseline_ok=False,
            condition_ok=True,
            answer_changed=True,
            tie=False,
        )
        metrics = _condition_metrics(counts, "same_question_peer_delta")

        self.assertEqual(metrics["rows"], 1)
        self.assertEqual(metrics["delta_vs_baseline"], 0)
        self.assertEqual(metrics["recovery_rate"], 1.0)
        self.assertEqual(metrics["answer_change_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
