import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from run_mca_text_audit import aggregate_audit_decision, parse_audit_certificate


class MCATextAuditTest(unittest.TestCase):
    def test_parse_audit_certificate_accepts_admissible_change(self) -> None:
        parsed = parse_audit_certificate(
            """
            <certificate>
              <used_cues>S1C1,S2C1</used_cues>
              <condition>Substitute the proposed value into the original equation.</condition>
              <initial>fail</initial>
              <alternative>pass</alternative>
              <calculation>The current value violates the equation, while 3 satisfies it.</calculation>
              <answer>3</answer>
              <decision>change</decision>
            </certificate>
            """
        )

        self.assertTrue(parsed.admissible_change)
        self.assertEqual(parsed.used_cues, ("S1C1", "S2C1"))
        self.assertEqual(parsed.initial_status, "fail")
        self.assertEqual(parsed.alternative_status, "pass")
        self.assertEqual(parsed.normalized_answer, "expr:3")

    def test_parse_audit_certificate_rejects_unknown_or_keep(self) -> None:
        unknown = parse_audit_certificate(
            """
            <certificate>
              <used_cues>S1C1</used_cues>
              <condition>Check a boundary condition.</condition>
              <initial>unknown</initial>
              <alternative>pass</alternative>
              <calculation>The condition is not decisive.</calculation>
              <answer>5</answer>
              <decision>change</decision>
            </certificate>
            """
        )
        keep = parse_audit_certificate(
            """
            <certificate>
              <used_cues>S1C1</used_cues>
              <condition>Check a boundary condition.</condition>
              <initial>fail</initial>
              <alternative>pass</alternative>
              <calculation>A change would be possible, but reviewer keeps.</calculation>
              <answer>5</answer>
              <decision>keep</decision>
            </certificate>
            """
        )

        self.assertFalse(unknown.admissible_change)
        self.assertFalse(keep.admissible_change)

    def test_aggregate_requires_enough_matching_change_certificates(self) -> None:
        cert_a = parse_audit_certificate(
            "<certificate><used_cues>S1C1</used_cues><condition>x</condition>"
            "<initial>fail</initial><alternative>pass</alternative><calculation>x</calculation>"
            "<answer>3</answer><decision>change</decision></certificate>"
        )
        cert_b = parse_audit_certificate(
            "<certificate><used_cues>S2C1</used_cues><condition>x</condition>"
            "<initial>fail</initial><alternative>pass</alternative><calculation>x</calculation>"
            "<answer>3</answer><decision>change</decision></certificate>"
        )

        final_answer, decision, count, required = aggregate_audit_decision(
            "2",
            [cert_a, cert_b],
            min_change_certificates=2,
        )

        self.assertEqual(final_answer, "3")
        self.assertEqual(decision, "change")
        self.assertEqual(count, 2)
        self.assertEqual(required, 2)

    def test_aggregate_keeps_when_changes_disagree(self) -> None:
        cert_a = parse_audit_certificate(
            "<certificate><used_cues>S1C1</used_cues><condition>x</condition>"
            "<initial>fail</initial><alternative>pass</alternative><calculation>x</calculation>"
            "<answer>3</answer><decision>change</decision></certificate>"
        )
        cert_b = parse_audit_certificate(
            "<certificate><used_cues>S2C1</used_cues><condition>x</condition>"
            "<initial>fail</initial><alternative>pass</alternative><calculation>x</calculation>"
            "<answer>4</answer><decision>change</decision></certificate>"
        )

        final_answer, decision, count, required = aggregate_audit_decision(
            "2",
            [cert_a, cert_b],
            min_change_certificates=2,
        )

        self.assertEqual(final_answer, "2")
        self.assertEqual(decision, "keep")
        self.assertEqual(count, 0)
        self.assertEqual(required, 2)

    def test_aggregate_keeps_when_change_matches_initial(self) -> None:
        cert = parse_audit_certificate(
            "<certificate><used_cues>S1C1</used_cues><condition>x</condition>"
            "<initial>fail</initial><alternative>pass</alternative><calculation>x</calculation>"
            "<answer>2</answer><decision>change</decision></certificate>"
        )

        final_answer, decision, count, required = aggregate_audit_decision(
            "2",
            [cert],
            min_change_certificates=1,
        )

        self.assertEqual(final_answer, "2")
        self.assertEqual(decision, "keep")
        self.assertEqual(count, 0)
        self.assertEqual(required, 1)


if __name__ == "__main__":
    unittest.main()
