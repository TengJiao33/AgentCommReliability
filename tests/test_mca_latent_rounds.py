import sys
import unittest
from pathlib import Path
from unittest import mock


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from run_mca_latent_rounds import (  # noqa: E402
    _fuse_peer_vector,
    _peer_message_vector,
    _private_thought_messages,
    _seed_parts,
    _state_fusion_name,
    _thought_audit,
    _transition,
    parse_args,
)


class MCALatentRoundsTests(unittest.TestCase):
    def test_transition_labels_baseline_to_latent(self):
        self.assertEqual(_transition("Ba", True, True), "BaC_to_C")
        self.assertEqual(_transition("Ba", True, False), "BaC_to_W")
        self.assertEqual(_transition("Ba", False, True), "BaW_to_C")
        self.assertEqual(_transition("Ba", False, False), "BaW_to_W")

    def test_natural_private_thought_prompt_is_minimal(self):
        messages = _private_thought_messages("What is 1+1?", ["try parity"], 1)
        joined = "\n".join(message["content"] for message in messages)

        self.assertIn("private", joined.lower())
        self.assertIn("think naturally", joined.lower())
        self.assertNotIn("critique", joined.lower())
        self.assertNotIn("uncertainty", joined.lower())
        self.assertIn("do not state a final answer", joined.lower())
        self.assertNotIn("REPRESENTATION", joined)
        self.assertNotIn("FIRST_MOVE", joined)
        self.assertNotIn("CHECK:", joined)

    def test_deliberative_private_thought_prompt_is_explicit_variant(self):
        messages = _private_thought_messages("What is 1+1?", ["try parity"], 1, "deliberative")
        joined = "\n".join(message["content"] for message in messages)

        self.assertIn("critique", joined.lower())
        self.assertIn("uncertainty", joined.lower())
        self.assertIn("next check", joined.lower())

    def test_thought_audit_flags_answer_marker(self):
        clean = _thought_audit("I should compare the two cases.", "7")
        leak = _thought_audit("Final answer: 7", "7")

        self.assertFalse(clean["has_answer_marker"])
        self.assertTrue(leak["has_answer_marker"])
        self.assertTrue(leak["matches_gold"])

    def test_seed_parts_match_conditions_by_default(self):
        class Args:
            benchmark = "math500"
            split = "mca_disagreement_v1"
            same_seed_conditions = True

        baseline = _seed_parts(Args, "row-1", "baseline", "thought", 0, 0)
        latent = _seed_parts(Args, "row-1", "latent", "thought", 0, 0)

        self.assertEqual(baseline, latent)

    def test_peer_fusion_clips_norm(self):
        import torch

        vectors = [torch.tensor([3.0, 4.0]), torch.tensor([0.0, 6.0]), torch.tensor([8.0, 0.0])]
        fused, meta = _fuse_peer_vector(vectors, 0, fusion="mean", max_norm=1.0)

        self.assertTrue(meta["active"])
        self.assertEqual(meta["source_count"], 2)
        self.assertTrue(meta["clipped"])
        self.assertLessEqual(float(torch.linalg.vector_norm(fused).item()), 1.0001)

    def test_residual_peer_mode_uses_peer_minus_own(self):
        import torch

        vectors = [torch.tensor([1.0, 1.0]), torch.tensor([3.0, 1.0]), torch.tensor([1.0, 5.0])]
        fused, meta = _peer_message_vector(vectors, 0, mode="residual", fusion="mean", max_norm=0.0)

        self.assertTrue(meta["active"])
        self.assertEqual(meta["peer_mode"], "residual")
        self.assertTrue(meta["own_state_available"])
        self.assertTrue(torch.allclose(fused, torch.tensor([1.0, 2.0])))
        self.assertEqual(_state_fusion_name("residual"), "mean_peer_minus_own_activation")

    def test_final_peer_steering_is_opt_in(self):
        base_argv = [
            "run_mca_latent_rounds.py",
            "--run-id",
            "unit",
            "--benchmark",
            "math500",
            "--model-key",
            "qwen",
            "--model-path",
            "/tmp/model",
        ]

        with mock.patch.object(sys, "argv", base_argv):
            self.assertFalse(parse_args().apply_peer_on_final)

        with mock.patch.object(sys, "argv", [*base_argv, "--apply-peer-on-final"]):
            self.assertTrue(parse_args().apply_peer_on_final)

        with mock.patch.object(sys, "argv", [*base_argv, "--apply-peer-on-final", "--no-apply-peer-on-final"]):
            self.assertFalse(parse_args().apply_peer_on_final)

    def test_peer_mode_parser(self):
        base_argv = [
            "run_mca_latent_rounds.py",
            "--run-id",
            "unit",
            "--benchmark",
            "math500",
            "--model-key",
            "qwen",
            "--model-path",
            "/tmp/model",
        ]

        with mock.patch.object(sys, "argv", [*base_argv, "--peer-mode", "residual"]):
            self.assertEqual(parse_args().peer_mode, "residual")

        with mock.patch.object(sys, "argv", [*base_argv, "--peer-mode", "per_peer_branch"]):
            self.assertEqual(parse_args().peer_mode, "per_peer_branch")


if __name__ == "__main__":
    unittest.main()
