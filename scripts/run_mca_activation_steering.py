#!/usr/bin/env python3
"""Run MCA-S: live sender generation state transfer through activation steering."""

from __future__ import annotations

from mca_hidden_channel_runner import build_parser, run_main


def main() -> int:
    parser = build_parser(__doc__ or "")
    return run_main("steer", parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
