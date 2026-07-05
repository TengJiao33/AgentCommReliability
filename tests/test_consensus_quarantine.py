import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from run_consensus_quarantine import (
    analyze_quarantine,
    build_candidate_cards,
    duplicate_reasoning_score,
    is_valid_appeal_text,
    transition_label,
)


def output(answer: str, text: str) -> dict:
    return {
        "parsed_answer": answer,
        "normalized_answer": answer,
        "output": text,
    }


class ConsensusQuarantineTest(unittest.TestCase):
    def test_candidate_cards_deduplicate_by_normalized_answer(self) -> None:
        cards = build_candidate_cards(
            [
                output("expr:4", "Final answer is 4 after adding 2 and 2."),
                output("expr:4", "A much longer explanation that still ends with 4."),
                output("expr:5", "Final answer is 5."),
            ]
        )

        self.assertEqual([card.normalized_answer for card in cards], ["expr:4", "expr:5"])
        self.assertEqual(cards[0].source_indices, (0, 1))
        self.assertEqual(cards[0].representative_output, "Final answer is 4 after adding 2 and 2.")

    def test_divergent_majority_triggers_quarantine(self) -> None:
        agent_outputs = [
            output("expr:4", "2 + 2 = 4."),
            output("expr:4", "Adding two and two gives four."),
            output("expr:5", "I think the answer is five."),
        ]
        cards = build_candidate_cards(agent_outputs)
        decision = analyze_quarantine(agent_outputs, cards, "divergent", 0.72)

        self.assertTrue(decision.should_quarantine)
        self.assertEqual(decision.reason, "non_unanimous_majority")
        self.assertEqual(decision.majority_answer, "expr:4")
        self.assertEqual(decision.majority_count, 2)
        self.assertEqual(decision.unique_answer_count, 2)

    def test_unanimous_answer_does_not_trigger_quarantine(self) -> None:
        agent_outputs = [
            output("expr:4", "2 + 2 = 4."),
            output("expr:4", "Adding two and two gives four."),
            output("expr:4", "The sum is four."),
        ]
        cards = build_candidate_cards(agent_outputs)
        decision = analyze_quarantine(agent_outputs, cards, "divergent", 0.72)

        self.assertFalse(decision.should_quarantine)
        self.assertEqual(decision.reason, "unanimous_or_single_answer")

    def test_transition_labels_match_majority_state_change(self) -> None:
        self.assertEqual(transition_label(True, True), "MaC_to_C")
        self.assertEqual(transition_label(True, False), "MaC_to_W")
        self.assertEqual(transition_label(False, True), "MaW_to_C")
        self.assertEqual(transition_label(False, False), "MaW_to_W")

    def test_duplicate_reasoning_score_is_pairwise_average(self) -> None:
        same = duplicate_reasoning_score(["alpha beta gamma", "alpha beta gamma"])
        different = duplicate_reasoning_score(["alpha beta gamma", "delta epsilon zeta"])

        self.assertEqual(same, 1.0)
        self.assertEqual(different, 0.0)

    def test_valid_appeal_rejects_sentinels_and_placeholders(self) -> None:
        self.assertFalse(is_valid_appeal_text("NO_VALID_APPEAL"))
        self.assertFalse(is_valid_appeal_text("your concrete objection"))
        self.assertTrue(is_valid_appeal_text("The consensus uses diameter where the problem asks for radius."))


if __name__ == "__main__":
    unittest.main()
