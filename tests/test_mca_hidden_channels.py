import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from mca_hidden_channel_runner import (  # noqa: E402
    hidden_review_prompt,
    hidden_source_text,
    parse_hidden_resolve_output,
)
from run_mca_text import CueAtom, FilteredCue  # noqa: E402


class MCAHiddenChannelTests(unittest.TestCase):
    def test_parse_hidden_resolve_output(self):
        parsed = parse_hidden_resolve_output(
            "<channel_effect>helpful</channel_effect>\n"
            "<new_realization>Track the invariant.</new_realization>\n"
            "<answer>7</answer>"
        )

        self.assertEqual(parsed.channel_effect, "helpful")
        self.assertEqual(parsed.new_realization, "Track the invariant.")
        self.assertEqual(parsed.parsed_answer, "7")
        self.assertEqual(parsed.normalized_answer, "expr:7")

    def test_parse_hidden_resolve_output_defaults_unclear(self):
        parsed = parse_hidden_resolve_output("<answer>11</answer>")

        self.assertEqual(parsed.channel_effect, "unclear")
        self.assertEqual(parsed.parsed_answer, "11")

    def test_hidden_source_text_uses_kept_cue_payload(self):
        cue = CueAtom(
            cue_id="S1C1",
            source_agent_index=0,
            source_answer="12",
            cue_type="constraint",
            cue_text="Check divisibility before counting cases.",
            why_relevant="It prevents an impossible branch.",
            self_reported_answer_leak=False,
        )

        text = hidden_source_text([FilteredCue(cue=cue, keep=True, reasons=())])

        self.assertIn("S1C1 [constraint]", text)
        self.assertIn("divisibility", text)

    def test_hidden_review_prompt_names_channel_without_showing_cues(self):
        kv_prompt = hidden_review_prompt("What is 1+1?", 0, "kv")
        steer_prompt = hidden_review_prompt("What is 1+1?", 0, "steer")

        self.assertIn("KV-cache state", kv_prompt[0]["content"])
        self.assertIn("activation steering vector", steer_prompt[0]["content"])
        self.assertIn("<answer>final answer only</answer>", kv_prompt[1]["content"])


if __name__ == "__main__":
    unittest.main()

