import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from run_mca_pre_kv_then_mad import (  # noqa: E402
    _pre_state_messages,
    _sanitize_visible_commitment,
    _select_first_round_branch,
    _sender_state_audit,
    _stable_seed,
)


class FakeSenderState:
    def __init__(self, output):
        self.output = output


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

    def test_sender_state_audit_flags_answer_leak(self):
        states = [
            FakeSenderState(
                {
                    "output": "Private plan. <answer>7</answer>",
                    "parsed_answer": "7",
                    "normalized_answer": "expr:7",
                    "output_tokens": 5,
                }
            ),
            FakeSenderState(
                {
                    "output": "Private plan without final answer.",
                    "parsed_answer": None,
                    "normalized_answer": None,
                    "output_tokens": 5,
                }
            ),
        ]

        audit = _sender_state_audit(states, "7")

        self.assertEqual(audit["sender_answer_tag_count"], 1)
        self.assertEqual(audit["sender_gold_leak_count"], 1)
        self.assertTrue(audit["sender_state_outputs"][0]["has_answer_tag"])

    def test_micro_pre_state_prompt_requests_non_answer_sketch(self):
        messages = _pre_state_messages("What is 1+1?", 0, "early_plan", "micro")
        joined = "\n".join(message["content"] for message in messages)

        self.assertIn("REPRESENTATION", joined)
        self.assertIn("FIRST_MOVE", joined)
        self.assertIn("Do not state", joined)

    def test_visible_commitment_blocks_explicit_answer_marker(self):
        blocked = _sanitize_visible_commitment("Sketch. Final answer: 7", 200)
        shown = _sanitize_visible_commitment("REPRESENTATION: variables. FIRST_MOVE: set up equation.", 25)

        self.assertTrue(blocked["blocked"])
        self.assertEqual(blocked["text"], "")
        self.assertFalse(shown["blocked"])
        self.assertLessEqual(len(shown["text"]), 25)

    def test_pre_kv_unanimous_gate_keeps_baseline_when_pre_kv_splits(self):
        no_channel_outputs = [
            {"parsed_answer": "10"},
            {"parsed_answer": "10"},
            {"parsed_answer": "10"},
        ]
        pre_kv_outputs = [
            {"parsed_answer": "8"},
            {"parsed_answer": "5"},
            {"parsed_answer": "8"},
        ]

        selected = _select_first_round_branch(
            no_channel_outputs,
            pre_kv_outputs,
            policy="pre_kv_unanimous_else_no_channel",
            agents=3,
        )

        self.assertEqual(selected["source"], "no_channel")
        self.assertEqual(selected["majority_answer"], "expr:10")

    def test_pre_kv_unanimous_gate_accepts_unanimous_pre_kv(self):
        no_channel_outputs = [
            {"parsed_answer": "3*pi/2"},
            {"parsed_answer": "3*pi/2"},
            {"parsed_answer": "3*pi/2"},
        ]
        pre_kv_outputs = [
            {"parsed_answer": "pi"},
            {"parsed_answer": "pi"},
            {"parsed_answer": "pi"},
        ]

        selected = _select_first_round_branch(
            no_channel_outputs,
            pre_kv_outputs,
            policy="pre_kv_unanimous_else_no_channel",
            agents=3,
        )

        self.assertEqual(selected["source"], "pre_kv")
        self.assertEqual(selected["majority_answer"], "expr:pi")


if __name__ == "__main__":
    unittest.main()
