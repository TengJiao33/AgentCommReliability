import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from run_mca_text_anchored_delta import (  # noqa: E402
    AnchorPayload,
    _last_token_for_substring,
    _overlapping_token_indices,
    _payload_metadata,
    parse_anchor_units,
)


class CharTokenizer:
    def __call__(self, text, add_special_tokens=False):
        class Encoded:
            pass

        encoded = Encoded()
        encoded.input_ids = [ord(ch) for ch in text]
        return encoded

    def decode(self, token_ids, skip_special_tokens=True):
        return "".join(chr(int(token_id)) for token_id in token_ids)


class MCATextAnchoredDeltaTests(unittest.TestCase):
    def test_parse_anchor_units(self):
        text = (
            "<unit><anchor>set up equation</anchor><work>Let x be the value.</work></unit>\n"
            "<unit><anchor>solve equation</anchor><work>x = 3.</work></unit>\n"
            "<answer>3</answer>"
        )

        units = parse_anchor_units(text)

        self.assertEqual(len(units), 2)
        self.assertEqual(units[0].anchor, "set up equation")
        self.assertEqual(units[0].work, "Let x be the value.")
        self.assertEqual(text[units[1].work_start : units[1].work_end], "x = 3.")

    def test_overlapping_token_indices(self):
        spans = [(0, 1), (1, 2), (2, 3), (3, 4)]

        self.assertEqual(_overlapping_token_indices(spans, 1, 3), [1, 2])
        self.assertEqual(_overlapping_token_indices(spans, 4, 5), [])

    def test_last_token_for_substring(self):
        tokenizer = CharTokenizer()

        position = _last_token_for_substring(tokenizer, "abc [A1] solve equation xyz", "[A1] solve equation")

        self.assertEqual(position, len("abc [A1] solve equation") - 1)

    def test_payload_metadata_records_norms(self):
        import torch

        payload = AnchorPayload(
            anchor="set up equation",
            vector_by_layer={22: torch.tensor([3.0, 4.0])},
            source_row=7,
            source_agent=1,
            source_unit=0,
            token_indices=[2, 3, 4],
        )

        meta = _payload_metadata([payload], active=True)

        self.assertTrue(meta["active"])
        self.assertEqual(meta["payload_count"], 1)
        self.assertAlmostEqual(meta["payloads"][0]["layers"]["22"]["norm"], 5.0)


if __name__ == "__main__":
    unittest.main()
