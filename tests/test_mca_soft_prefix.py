import unittest

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from run_mca_soft_prefix import (  # noqa: E402
    balanced_pool_spans,
    parse_soft_prefix_resolve_output,
    soft_prefix_source_text,
)
from run_mca_text import CueAtom, FilteredCue  # noqa: E402


class McaSoftPrefixTests(unittest.TestCase):
    def test_balanced_pool_spans_keeps_single_token_spans_when_short(self):
        self.assertEqual(balanced_pool_spans(3, 5), [(0, 1), (1, 2), (2, 3)])

    def test_balanced_pool_spans_covers_all_tokens_when_long(self):
        spans = balanced_pool_spans(10, 4)
        self.assertEqual(spans, [(0, 2), (2, 5), (5, 7), (7, 10)])
        covered = [idx for start, end in spans for idx in range(start, end)]
        self.assertEqual(covered, list(range(10)))

    def test_balanced_pool_spans_empty_inputs(self):
        self.assertEqual(balanced_pool_spans(0, 4), [])
        self.assertEqual(balanced_pool_spans(4, 0), [])

    def test_soft_prefix_source_text_uses_kept_cues(self):
        cue = CueAtom(
            cue_id="S1C1",
            source_agent_index=0,
            source_answer="12",
            cue_type="constraint",
            cue_text="Check the parity constraint before counting cases.",
            why_relevant="It prevents overcounting.",
            self_reported_answer_leak=False,
        )
        text = soft_prefix_source_text([FilteredCue(cue=cue, keep=True, reasons=())])
        self.assertIn("S1C1 [constraint]", text)
        self.assertIn("parity constraint", text)

    def test_parse_soft_prefix_resolve_output(self):
        parsed = parse_soft_prefix_resolve_output(
            "<prefix_effect>helpful</prefix_effect>\n"
            "<new_realization>Use the discriminant.</new_realization>\n"
            "<answer>3</answer>"
        )
        self.assertEqual(parsed.prefix_effect, "helpful")
        self.assertEqual(parsed.new_realization, "Use the discriminant.")
        self.assertEqual(parsed.parsed_answer, "3")
        self.assertEqual(parsed.normalized_answer, "expr:3")

    def test_parse_soft_prefix_resolve_output_defaults_unclear(self):
        parsed = parse_soft_prefix_resolve_output("<answer>14/3</answer>")
        self.assertEqual(parsed.prefix_effect, "unclear")
        self.assertEqual(parsed.parsed_answer, "14/3")


if __name__ == "__main__":
    unittest.main()
