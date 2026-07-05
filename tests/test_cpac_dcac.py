import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from run_consensus_quarantine import build_candidate_cards
from run_cpac_dcac import (
    analyze_candidate_pool,
    dcac_certificate_rejection_reasons,
    dcac_final_answer,
    detect_representation_risks,
    is_directional_claim_text,
    is_guarded_dcac_flip,
    parse_dcac_certificate,
)


def output(answer: str, text: str) -> dict:
    return {
        "parsed_answer": answer,
        "normalized_answer": answer,
        "output": text,
    }


class CPACDCACTest(unittest.TestCase):
    def test_unique_one_pool_keeps_initial_answer(self) -> None:
        agent_outputs = [
            output("expr:4", "2 + 2 = 4."),
            output("expr:4", "Adding two and two gives four."),
            output("expr:4", "The sum is four."),
        ]
        cards = build_candidate_cards(agent_outputs)
        decision = analyze_candidate_pool(
            agent_outputs,
            cards,
            no_majority_action="listwise",
            overlap_threshold=0.72,
        )

        self.assertEqual(decision.pool_state, "collapse")
        self.assertEqual(decision.action, "keep_initial")
        self.assertEqual(decision.support_vector, (3,))

    def test_unique_two_majority_uses_dcac(self) -> None:
        agent_outputs = [
            output("expr:4", "2 + 2 = 4."),
            output("expr:4", "Adding two and two gives four."),
            output("expr:5", "A challenger says five."),
        ]
        cards = build_candidate_cards(agent_outputs)
        decision = analyze_candidate_pool(
            agent_outputs,
            cards,
            no_majority_action="listwise",
            overlap_threshold=0.72,
        )

        self.assertEqual(decision.pool_state, "minority_bearing")
        self.assertEqual(decision.action, "dcac")
        self.assertEqual(decision.support_vector, (2, 1))

    def test_three_way_tie_uses_listwise_branch(self) -> None:
        agent_outputs = [
            output("expr:4", "Answer four."),
            output("expr:5", "Answer five."),
            output("expr:6", "Answer six."),
        ]
        cards = build_candidate_cards(agent_outputs)
        decision = analyze_candidate_pool(
            agent_outputs,
            cards,
            no_majority_action="listwise",
            overlap_threshold=0.72,
        )

        self.assertEqual(decision.pool_state, "no_majority_conflict")
        self.assertEqual(decision.action, "listwise_discriminant")
        self.assertEqual(decision.support_vector, (1, 1, 1))

    def test_representation_risk_detects_symbolic_and_base_forms(self) -> None:
        cards = build_candidate_cards(
            [
                output(r"52_8", "The answer is base notation 52_8."),
                output(r"7\pi", "The circumference term is 7 pi."),
                output("expr:7*pi", "Equivalent symbolic answer."),
            ]
        )

        self.assertIn("base_notation", detect_representation_risks(cards))
        self.assertIn("symbolic_constant", detect_representation_risks(cards))

    def test_directional_claim_rejects_nonclaims_and_consensus_support(self) -> None:
        self.assertFalse(is_directional_claim_text("NO_ADMISSIBLE_CLAIM"))
        self.assertFalse(is_directional_claim_text("The majority is correct and the challenger is wrong."))
        self.assertTrue(
            is_directional_claim_text(
                "The challenger preserves the base-eight interpretation while the majority reads the subscript as a scalar."
            )
        )

    def test_certificate_requires_majority_fail_and_challenger_pass_to_flip(self) -> None:
        parsed = parse_dcac_certificate(
            """
            <certificate>
              <condition>Check the base-eight interpretation.</condition>
              <majority>fail</majority>
              <challenger>pass</challenger>
              <calculation>52_8 means 42 in decimal, not scalar 52.</calculation>
              <decision>flip</decision>
            </certificate>
            """
        )

        self.assertTrue(parsed.admissible_flip)
        self.assertEqual(parsed.majority_status, "fail")
        self.assertEqual(parsed.challenger_status, "pass")

    def test_dcac_aggregation_is_conservative(self) -> None:
        cards = build_candidate_cards(
            [
                output("expr:4", "Majority answer four."),
                output("expr:4", "Majority answer four again."),
                output("expr:5", "Challenger answer five."),
            ]
        )
        majority = cards[0]
        challenger = cards[1]
        flip_cert = parse_dcac_certificate(
            "<certificate><condition>x</condition><majority>fail</majority>"
            "<challenger>pass</challenger><calculation>The challenger answer 5 satisfies x.</calculation>"
            "<decision>flip</decision></certificate>"
        )
        keep_cert = parse_dcac_certificate(
            "<certificate><condition>x</condition><majority>unknown</majority>"
            "<challenger>unknown</challenger><calculation>x</calculation><decision>keep</decision></certificate>"
        )

        final_answer, decision, flip_count, required = dcac_final_answer(
            majority,
            challenger,
            [flip_cert, keep_cert],
            min_flip_certificates=2,
        )

        self.assertEqual(final_answer, "expr:4")
        self.assertEqual(decision, "keep")
        self.assertEqual(flip_count, 1)
        self.assertEqual(required, 2)

    def test_guard_rejects_label_text_contradiction(self) -> None:
        cards = build_candidate_cards(
            [
                output("expr:17", "Majority x = 8 gives x + y = 17."),
                output("expr:17", "Majority x = 8 gives x + y = 17 again."),
                output("expr:7", "Challenger x = 7 gives x + y = 7."),
            ]
        )
        majority = cards[0]
        challenger = cards[1]
        cert = parse_dcac_certificate(
            """
            <certificate>
              <condition>x > 7</condition>
              <majority>fail</majority>
              <challenger>pass</challenger>
              <calculation>The majority answer x = 8 satisfies this condition, but the challenger x = 7 does not.</calculation>
              <decision>flip</decision>
            </certificate>
            """
        )

        reasons = dcac_certificate_rejection_reasons(cert, majority, challenger)

        self.assertIn("label_text_contradiction", reasons)
        self.assertIn("simple_inequality_contradiction", reasons)
        self.assertFalse(is_guarded_dcac_flip(cert, majority, challenger))

    def test_guard_rejects_arithmetic_mismatch(self) -> None:
        cards = build_candidate_cards(
            [
                output("expr:62400", "Majority answer 62400."),
                output("expr:62400", "Majority answer 62400 again."),
                output("expr:625200", "Challenger answer 625200."),
            ]
        )
        majority = cards[0]
        challenger = cards[1]
        cert = parse_dcac_certificate(
            """
            <certificate>
              <condition>Use 26*25*10*9 for distinct letters and digits.</condition>
              <majority>fail</majority>
              <challenger>pass</challenger>
              <calculation>26*25*10*9 = 625200</calculation>
              <decision>flip</decision>
            </certificate>
            """
        )

        reasons = dcac_certificate_rejection_reasons(cert, majority, challenger)

        self.assertIn("arithmetic_mismatch_in_calculation", reasons)
        self.assertFalse(is_guarded_dcac_flip(cert, majority, challenger))

    def test_guard_rejects_certificate_that_does_not_support_challenger_answer(self) -> None:
        cards = build_candidate_cards(
            [
                output("expr:7/3", "Majority answer 7/3."),
                output("expr:7/3", "Majority answer 7/3 again."),
                output("expr:3", "Challenger answer 3."),
            ]
        )
        majority = cards[0]
        challenger = cards[1]
        cert = parse_dcac_certificate(
            """
            <certificate>
              <condition>Compute the operation.</condition>
              <majority>fail</majority>
              <challenger>pass</challenger>
              <calculation>7 * 10 * (21 / 30) = 49</calculation>
              <decision>flip</decision>
            </certificate>
            """
        )

        reasons = dcac_certificate_rejection_reasons(cert, majority, challenger)

        self.assertIn("challenger_answer_not_supported_by_certificate_text", reasons)
        self.assertFalse(is_guarded_dcac_flip(cert, majority, challenger))

    def test_guard_blocks_base_notation_flips(self) -> None:
        cards = build_candidate_cards(
            [
                output("expr:6", "Majority answer 4433_6."),
                output("expr:6", "Majority answer 4433_6 again."),
                output("expr:4343", "Challenger answer 4343."),
            ]
        )
        majority = cards[0]
        challenger = cards[1]
        cert = parse_dcac_certificate(
            """
            <certificate>
              <condition>Convert 999 to base six.</condition>
              <majority>fail</majority>
              <challenger>pass</challenger>
              <calculation>The remainders form 4343.</calculation>
              <decision>flip</decision>
            </certificate>
            """
        )

        reasons = dcac_certificate_rejection_reasons(cert, majority, challenger, ("base_notation",))

        self.assertIn("blocked_representation_risk:base_notation", reasons)
        self.assertFalse(is_guarded_dcac_flip(cert, majority, challenger, ("base_notation",)))

    def test_guard_rejects_negated_text_challenger_answer(self) -> None:
        cards = build_candidate_cards(
            [
                output("str:ellipse", "Majority answer ellipse."),
                output("str:ellipse", "Majority answer ellipse again."),
                output("str:circle", "Challenger answer circle."),
            ]
        )
        majority = cards[0]
        challenger = cards[1]
        cert = parse_dcac_certificate(
            """
            <certificate>
              <condition>Check the conic form.</condition>
              <majority>fail</majority>
              <challenger>pass</challenger>
              <calculation>The rewritten equation is not in the form for a circle.</calculation>
              <decision>flip</decision>
            </certificate>
            """
        )

        reasons = dcac_certificate_rejection_reasons(cert, majority, challenger)

        self.assertIn("negated_challenger_text_answer", reasons)
        self.assertFalse(is_guarded_dcac_flip(cert, majority, challenger))


if __name__ == "__main__":
    unittest.main()
