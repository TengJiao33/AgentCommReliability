#!/usr/bin/env python3
"""Run MCA-Pre-KV: pre-answer latent communication through KV cache."""

from __future__ import annotations

from mca_pre_answer_runner import build_parser, run_main


def main() -> int:
    parser = build_parser(__doc__ or "")
    return run_main("kv", parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
