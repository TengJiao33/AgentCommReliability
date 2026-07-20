import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from run_mca_question_token_anchored_delta import (  # noqa: E402
    QuestionTokenAnchor,
    SegmentPayload,
    _payload_metadata,
    _question_token_positions,
    _segment_ranges,
    _select_shard,
    _top_anchors,
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


class MCAQuestionTokenAnchoredDeltaTests(unittest.TestCase):
    def test_question_token_positions_prefer_raw_question(self):
        tokenizer = CharTokenizer()
        raw_question = "What is x?"
        prepared = "### format instruction ###\nWhat is x?"
        prompt = f"<user>{prepared}\nPlease solve.</user>"

        positions = _question_token_positions(tokenizer, prompt, raw_question, prepared)

        expected_start = prompt.index(raw_question)
        expected_end = expected_start + len(raw_question)
        self.assertEqual(positions[0], expected_start)
        self.assertEqual(positions[-1], expected_end - 1)

    def test_segment_ranges(self):
        self.assertEqual(_segment_ranges(0, 4), [])
        self.assertEqual(_segment_ranges(3, 4), [(0, 3)])
        self.assertEqual(_segment_ranges(9, 4), [(0, 4), (4, 8), (8, 9)])

    def test_top_anchors_returns_softmax_weights(self):
        import torch

        tokenizer = CharTokenizer()
        prompt = "abcde"
        prompt_token_ids = [ord(ch) for ch in prompt]

        anchors = _top_anchors(
            tokenizer=tokenizer,
            prompt_token_ids=prompt_token_ids,
            question_positions=[0, 1, 2, 3, 4],
            scores=torch.tensor([0.1, 3.0, 0.2, 2.0, 0.0]),
            max_question_anchors=2,
        )

        self.assertEqual([anchor.token_position for anchor in anchors], [1, 3])
        self.assertEqual([anchor.token_text for anchor in anchors], ["b", "d"])
        self.assertAlmostEqual(sum(anchor.weight for anchor in anchors), 1.0)
        self.assertGreater(anchors[0].weight, anchors[1].weight)

    def test_payload_metadata_records_question_token_anchors(self):
        import torch

        payload = SegmentPayload(
            vector_by_layer={22: torch.tensor([3.0, 4.0])},
            source_row=7,
            source_agent=1,
            source_segment=2,
            generated_token_range=(32, 48),
            anchors=[
                QuestionTokenAnchor(
                    token_position=11,
                    token_text="x",
                    score=0.75,
                    weight=1.0,
                )
            ],
        )

        meta = _payload_metadata([payload], active=True)

        self.assertTrue(meta["active"])
        self.assertEqual(meta["payload_count"], 1)
        self.assertEqual(meta["payloads"][0]["source_segment"], 2)
        self.assertEqual(meta["payloads"][0]["anchors"][0]["token_position"], 11)
        self.assertAlmostEqual(meta["payloads"][0]["layers"]["22"]["norm"], 5.0)

    def test_select_shard_partitions_rows_without_overlap(self):
        rows = [{"id": f"row-{index}"} for index in range(10)]

        shards = [_select_shard(rows, 3, shard_index) for shard_index in range(3)]

        self.assertEqual([[row["id"] for row in shard] for shard in shards], [
            ["row-0", "row-3", "row-6", "row-9"],
            ["row-1", "row-4", "row-7"],
            ["row-2", "row-5", "row-8"],
        ])
        self.assertEqual(sorted(row["id"] for shard in shards for row in shard), sorted(row["id"] for row in rows))

    def test_select_shard_rejects_invalid_index(self):
        with self.assertRaises(ValueError):
            _select_shard([{"id": "row-0"}], 2, 2)


if __name__ == "__main__":
    unittest.main()
