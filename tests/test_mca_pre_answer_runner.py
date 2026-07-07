import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from mca_pre_answer_runner import (  # noqa: E402
    _source_indices,
    _transition_label,
    parse_answer_output,
    pre_state_prompt,
    receiver_prompt,
)


class MCAPreAnswerRunnerTests(unittest.TestCase):
    def test_question_only_prompt_is_pre_answer_not_certificate(self):
        prompt = pre_state_prompt("What is 1+1?", 0, "question_only")
        joined = "\n".join(message["content"] for message in prompt)

        self.assertIn("pre-answer", joined)
        self.assertIn("internal representation", joined)
        self.assertNotIn("certificate", joined.lower())
        self.assertNotIn("<answer>", joined)

    def test_receiver_prompt_is_standard_solution_prompt(self):
        prompt = receiver_prompt("What is 1+1?")
        self.assertEqual(len(prompt), 1)
        self.assertIn("Please solve the problem step by step", prompt[0]["content"])
        self.assertIn("<answer>", prompt[0]["content"])

    def test_parse_answer_output_uses_last_answer_tag(self):
        parsed = parse_answer_output("<answer>1</answer>\n<answer>2</answer>")
        self.assertEqual(parsed["parsed_answer"], "2")
        self.assertEqual(parsed["normalized_answer"], "expr:2")

    def test_source_indices_round_robin(self):
        self.assertEqual(_source_indices(2, 5), [0, 1, 0, 1, 0])

    def test_transition_label_uses_baseline_prefix(self):
        self.assertEqual(_transition_label(True, False), "BaC_to_W")
        self.assertEqual(_transition_label(False, True), "BaW_to_C")


if __name__ == "__main__":
    unittest.main()
