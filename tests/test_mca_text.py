import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from run_consensus_quarantine import build_candidate_cards
from run_mca_text import (
    candidate_answer_strings,
    contains_candidate_answer,
    filter_cues,
    is_generic_cue,
    parse_cue_atoms,
    parse_cue_id_list,
    parse_cue_resolve_output,
)


def output(answer: str, text: str) -> dict:
    return {
        "parsed_answer": answer,
        "normalized_answer": answer,
        "output": text,
    }


class MCATextTest(unittest.TestCase):
    def test_parse_cue_atoms_reads_multiple_xml_cues(self) -> None:
        cues = parse_cue_atoms(
            """
            <cues>
              <cue>
                <type>representation</type>
                <text>Interpret the subscript as base notation before converting the number.</text>
                <why>The notation changes the value being compared.</why>
                <answer_leak>no</answer_leak>
              </cue>
              <cue>
                <type>pitfall</type>
                <text>Do not treat the base marker as multiplication by the subscript.</text>
                <why>That is the common parsing error here.</why>
                <answer_leak>yes</answer_leak>
              </cue>
            </cues>
            """,
            source_agent_index=1,
            source_answer="expr:42",
            max_cues=3,
        )

        self.assertEqual([cue.cue_id for cue in cues], ["S2C1", "S2C2"])
        self.assertEqual(cues[0].cue_type, "representation")
        self.assertFalse(cues[0].self_reported_answer_leak)
        self.assertTrue(cues[1].self_reported_answer_leak)

    def test_candidate_answer_strings_include_normalized_payloads(self) -> None:
        cards = build_candidate_cards(
            [
                output("42", "Answer 42."),
                output("52_8", "Answer 52_8."),
            ]
        )

        answers = candidate_answer_strings(cards)

        self.assertIn("42", answers)
        self.assertIn("52_8", answers)

    def test_contains_candidate_answer_detects_exact_payload(self) -> None:
        cards = build_candidate_cards([output("42", "Answer 42.")])
        answers = candidate_answer_strings(cards)

        self.assertTrue(contains_candidate_answer("The final converted value is 42.", answers))
        self.assertFalse(contains_candidate_answer("Convert the base notation before comparing values.", answers))

    def test_generic_cue_filter_rejects_placeholders(self) -> None:
        self.assertTrue(is_generic_cue("Check your work."))
        self.assertTrue(is_generic_cue("Be careful with calculations."))
        self.assertFalse(is_generic_cue("Check base-eight notation before treating the subscript as a scalar."))

    def test_filter_cues_rejects_leaks_generic_and_duplicates(self) -> None:
        cards = build_candidate_cards([output("42", "Answer 42."), output("50", "Answer 50.")])
        cues = parse_cue_atoms(
            """
            <cues>
              <cue>
                <type>representation</type>
                <text>Check base-eight notation before treating the subscript as a scalar.</text>
                <why>It changes the interpretation.</why>
                <answer_leak>no</answer_leak>
              </cue>
              <cue>
                <type>representation</type>
                <text>Check base-eight notation before treating the subscript as a scalar.</text>
                <why>Duplicate cue.</why>
                <answer_leak>no</answer_leak>
              </cue>
              <cue>
                <type>sanity_check</type>
                <text>Check your work carefully.</text>
                <why>Generic.</why>
                <answer_leak>no</answer_leak>
              </cue>
              <cue>
                <type>pitfall</type>
                <text>The converted answer should be 42.</text>
                <why>Leaks answer.</why>
                <answer_leak>no</answer_leak>
              </cue>
            </cues>
            """,
            source_agent_index=0,
            source_answer="42",
            max_cues=4,
        )

        filtered = filter_cues(cues, cards)

        self.assertTrue(filtered[0].keep)
        self.assertFalse(filtered[1].keep)
        self.assertIn("duplicate", filtered[1].reasons)
        self.assertFalse(filtered[2].keep)
        self.assertIn("generic", filtered[2].reasons)
        self.assertFalse(filtered[3].keep)
        self.assertIn("candidate_answer_leak", filtered[3].reasons)

    def test_parse_cue_id_list_handles_none_and_commas(self) -> None:
        self.assertEqual(parse_cue_id_list("NONE"), ())
        self.assertEqual(parse_cue_id_list("S1C1, S2C2"), ("S1C1", "S2C2"))

    def test_parse_cue_resolve_output_extracts_answer_and_usage(self) -> None:
        parsed = parse_cue_resolve_output(
            """
            <used_cues>S1C1, S3C2</used_cues>
            <ignored_cues>NONE</ignored_cues>
            <new_realization>The base marker changes the value.</new_realization>
            <answer>42</answer>
            """
        )

        self.assertEqual(parsed.parsed_answer, "42")
        self.assertEqual(parsed.normalized_answer, "expr:42")
        self.assertEqual(parsed.used_cues, ("S1C1", "S3C2"))
        self.assertEqual(parsed.ignored_cues, ())


if __name__ == "__main__":
    unittest.main()
