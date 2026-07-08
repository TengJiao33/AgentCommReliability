# Hybrid Micro-Commitment Pre-KV Gated Run

Purpose: test a more defensive MCA-Pre-KV implementation for helping Standard MAD.

This run changes the early-plan Pre-KV bridge in two ways:

1. Each sender produces a compact non-answer micro-commitment while generating the retained KV state.
2. The selected first-round branch uses a consensus gate:

```text
use Pre-KV only if all Pre-KV agents agree;
otherwise fall back to no-channel first-round outputs.
```

The runner still records raw no-channel, raw Pre-KV, no-channel+MAD, and Pre-KV+MAD metrics. It additionally records:

- selected first accuracy;
- selected+MAD accuracy;
- selected source counts;
- visible commitment shown/blocked counts.

Primary script:

- `run_remote_serial_hybrid_micro_gated.sh`

Expected run ids:

- `20260707-a8002-gpu1-mca-matrix-hybrid-micro-gated-disagreement-qwen25-7b`
- `20260707-a8002-gpu1-mca-matrix-hybrid-micro-gated-gold-contrast-qwen25-7b`

