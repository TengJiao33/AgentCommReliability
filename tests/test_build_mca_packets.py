import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from build_mca_packets import (  # noqa: E402
    build_packet,
    gold_stratum,
    label_free_stratum,
    packet_row,
)


def record(
    parsed_answers,
    normalized_answers,
    *,
    majority_answer,
    gold_answer,
    record_id="row-1",
):
    return {
        "id": record_id,
        "index": 7,
        "benchmark": "math500",
        "split": "test",
        "question": "What is 1+1?",
        "gold_answer": gold_answer,
        "mad_mm": {
            "rounds": [
                {
                    "round": 1,
                    "majority_answer": majority_answer,
                    "majority_tie": False,
                    "agent_outputs": [
                        {"parsed_answer": parsed, "normalized_answer": normalized}
                        for parsed, normalized in zip(parsed_answers, normalized_answers)
                    ],
                }
            ]
        },
    }


class BuildMCAPacketsTests(unittest.TestCase):
    def test_label_free_keeps_visible_disagreement_without_gold(self):
        row = record(["1", "1", "2"], ["expr:1", "expr:1", "expr:2"], majority_answer="1", gold_answer="1")

        self.assertEqual(label_free_stratum(row), "minority_bearing")

    def test_label_free_drops_collapse_even_when_wrong(self):
        row = record(["3", "3", "3"], ["expr:3", "expr:3", "expr:3"], majority_answer="3", gold_answer="2")

        self.assertIsNone(label_free_stratum(row))

    def test_gold_stratum_keeps_majority_wrong_minority_correct(self):
        row = record(["3", "3", "2"], ["expr:3", "expr:3", "expr:2"], majority_answer="3", gold_answer="2")

        self.assertEqual(gold_stratum(row), "majority_wrong_minority_correct")

    def test_gold_stratum_keeps_majority_correct_minority_wrong(self):
        row = record(["2", "2", "3"], ["expr:2", "expr:2", "expr:3"], majority_answer="2", gold_answer="2")

        self.assertEqual(gold_stratum(row), "majority_correct_minority_wrong")

    def test_gold_stratum_drops_all_correct_and_all_wrong(self):
        all_correct = record(["2", "2", "2"], ["expr:2", "expr:2", "expr:2"], majority_answer="2", gold_answer="2")
        all_wrong = record(["3", "3", "3"], ["expr:3", "expr:3", "expr:3"], majority_answer="3", gold_answer="2")

        self.assertIsNone(gold_stratum(all_correct))
        self.assertIsNone(gold_stratum(all_wrong))

    def test_build_packet_writes_runner_compatible_rows(self):
        rows = [
            record(["1", "1", "2"], ["expr:1", "expr:1", "expr:2"], majority_answer="1", gold_answer="1"),
            record(["3", "3", "3"], ["expr:3", "expr:3", "expr:3"], majority_answer="3", gold_answer="2"),
        ]

        packet, counts = build_packet(rows, split="packet", packet_type="label_free_disagreement")

        self.assertEqual(len(packet), 1)
        self.assertEqual(counts["selected"], 1)
        self.assertEqual(packet[0]["answer"], "1")
        self.assertEqual(packet[0]["metadata"]["packet_stratum"], "minority_bearing")

    def test_packet_row_preserves_source_key(self):
        row = record(["1", "2", "3"], ["expr:1", "expr:2", "expr:3"], majority_answer="1", gold_answer="1")

        packet = packet_row(row, split="packet", packet_type="label_free_disagreement", stratum="no_majority_conflict")

        self.assertEqual(packet["id"], "row-1")
        self.assertEqual(packet["index"], 7)
        self.assertEqual(packet["metadata"]["source_record_id"], "row-1")


if __name__ == "__main__":
    unittest.main()

