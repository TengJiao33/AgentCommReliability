import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from merge_mca_question_token_anchored_delta_shards import _interleave_shard_records  # noqa: E402


class MergeQuestionTokenAnchoredDeltaShardsTests(unittest.TestCase):
    def test_interleave_restores_round_robin_input_order(self):
        shards = [
            [{"id": "row-0"}, {"id": "row-3"}, {"id": "row-6"}],
            [{"id": "row-1"}, {"id": "row-4"}],
            [{"id": "row-2"}, {"id": "row-5"}],
        ]

        merged = _interleave_shard_records(shards)

        self.assertEqual([record["id"] for _, record in merged], [f"row-{index}" for index in range(7)])
        self.assertEqual([shard_index for shard_index, _ in merged], [0, 1, 2, 0, 1, 2, 0])

    def test_interleave_handles_empty_input(self):
        self.assertEqual(_interleave_shard_records([]), [])


if __name__ == "__main__":
    unittest.main()
