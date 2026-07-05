import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from run_basic_mad import is_correct, majority_vote, normalize_numeric


class EvaluatorTest(unittest.TestCase):
    def test_canonical_answers_are_idempotent(self) -> None:
        self.assertEqual(normalize_numeric("expr:p - q"), "expr:p - q")
        self.assertEqual(normalize_numeric("expr:(3, pi/2)"), "expr:(3, pi/2)")
        self.assertEqual(normalize_numeric("expr:6 + 9*I"), "expr:6 + 9*I")
        self.assertEqual(normalize_numeric("expr:5.40000000000000"), "expr:27/5")

    def test_math500_formats_from_records(self) -> None:
        self.assertTrue(is_correct("expr:p - q", "p - q"))
        self.assertTrue(is_correct("expr:(3, pi/2)", r"\left( 3, \frac{\pi}{2} \right)"))
        self.assertTrue(is_correct(r"\boxed{11\sqrt{2}}", r"11\sqrt2"))
        self.assertTrue(is_correct(r"\boxed{6+9i}", "6+9i"))
        self.assertTrue(is_correct("expr:6 + 9*I", "6+9i"))
        self.assertTrue(is_correct(r"\text{Evelyn}", r"\text{Evelyn}"))
        self.assertTrue(is_correct("5.4", r"5.4 \text{ cents}"))
        self.assertTrue(is_correct("$8,400", "8400"))
        self.assertTrue(is_correct(r"\$17,500.", "17500"))
        self.assertTrue(is_correct("2,125", "2125"))
        self.assertTrue(is_correct("Harald sold 8,000 copies.", "8000"))
        self.assertTrue(is_correct("There are **20 total windows** between the houses.", "20"))

    def test_mixed_numbers_are_not_treated_as_simple_fractions(self) -> None:
        self.assertEqual(normalize_numeric(r"137 \frac{1}{2}"), "expr:275/2")
        self.assertTrue(is_correct(r"\boxed{137 \frac{1}{2}}", r"137 \frac{1}{2}"))
        self.assertFalse(is_correct("expr:137/2", r"137 \frac{1}{2}"))

    def test_comma_separated_lists_stay_tuples(self) -> None:
        self.assertEqual(normalize_numeric("3, 5, 7"), "expr:(3, 5, 7)")
        self.assertTrue(is_correct("expr:(3, 5, 7)", "3, 5, 7"))

    def test_punctuation_only_is_not_an_answer(self) -> None:
        self.assertIsNone(normalize_numeric("**"))
        self.assertIsNone(normalize_numeric("YOUR FINAL ANSWER ONLY"))

    def test_majority_vote_returns_canonical_answer_usable_by_is_correct(self) -> None:
        majority, tied = majority_vote(
            [r"\boxed{(3, \frac{\pi}{2})}", r"$(3, \frac{\pi}{2})$", r"1"]
        )
        self.assertFalse(tied)
        self.assertEqual(majority, "expr:(3, pi/2)")
        self.assertTrue(is_correct(majority, r"\left( 3, \frac{\pi}{2} \right)"))


if __name__ == "__main__":
    unittest.main()
