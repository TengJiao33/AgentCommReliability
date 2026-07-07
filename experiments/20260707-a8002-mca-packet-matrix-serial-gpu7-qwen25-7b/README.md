# 20260707 A800_2 MCA packet matrix serial GPU7

Status: stopped and invalidated on 2026-07-07.

## Purpose

Run the MCA packet matrix diagnostics serially on A800_2 GPU 7.

The diagnostic question is:

```text
On filtered MATH500 packets, does question-only Pre-KV improve the first-round answer, and does that improvement survive a one-round Standard MAD text debate compared with a no-channel first round followed by the same debate?
```

## Unit

One benchmark row from a materialized packet split.

## Packets

- `math500/mca_disagreement_v1`: 221 rows, label-free disagreement packet.
- `math500/mca_gold_contrast_v1`: 142 rows, gold-stratified diagnostic packet.

## Matrix

The patched `scripts/run_mca_pre_kv_then_mad.py` writes all four conditions per row:

- A: no-channel first round, `temperature=0.2`, `max_tokens=1536`.
- B: question-only Pre-KV first round, `temperature=0.2`, `max_tokens=1536`.
- C: no-channel first round followed by one Standard MAD text debate round.
- D: Pre-KV first round followed by one Standard MAD text debate round.

Primary contrasts:

- `B - A`: fixed-parameter first-round Pre-KV effect.
- `D - C`: fixed-parameter Pre-KV effect after MAD debate.

Secondary contrasts:

- `C - A`: no-channel debate effect.
- `D - B`: Pre-KV debate effect.

## Launch

Remote host:

- `A800_2`

Remote workspace:

- `/data/xuhaoming/yfy/research_workspace`

GPU:

- `CUDA_VISIBLE_DEVICES=7`

Model:

- `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
- model key: `qwen25-7b-instruct`

Runner:

- `/data/xuhaoming/yfy/research_workspace/scripts/run_mca_pre_kv_then_mad.py`

Launch script:

- `/data/xuhaoming/yfy/research_workspace/experiments/20260707-a8002-mca-packet-matrix-serial-gpu7-qwen25-7b/run_remote_serial.sh`

Log:

- `/data/xuhaoming/yfy/research_workspace/experiments/20260707-a8002-mca-packet-matrix-serial-gpu7-qwen25-7b/serial.log`

Process ids at launch:

- serial script: `3622408`
- first packet timeout wrapper: `3622428`
- first packet Python runner: `3622429`

Output run ids:

- `20260707-a8002-gpu7-mca-matrix-disagreement-qwen25-7b`
- `20260707-a8002-gpu7-mca-matrix-gold-contrast-qwen25-7b`

Expected output directories:

- `experiments/20260707-a8002-gpu7-mca-matrix-disagreement-qwen25-7b/math500-qwen25-7b-instruct-mca-pre-kv-then-mad/`
- `experiments/20260707-a8002-gpu7-mca-matrix-gold-contrast-qwen25-7b/math500-qwen25-7b-instruct-mca-pre-kv-then-mad/`

## Launch check

Remote preflight passed before launch:

- remote `py_compile` passed for the patched runner and dependencies;
- packet row counts were `221` and `142`;
- GPU 7 had `4 MB / 80 GB` used and no compute process.

After launch, GPU 7 showed the Python runner using about `15 GB` and active utilization.
The first packet wrote partial records. The run was stopped after source audit because the runner still mixed generation forms:

- A/no-channel first used batched HF `generate`;
- B/Pre-KV first used sequential manual generation with KV state;
- C/D debate used batched HF `generate`;
- the run-level random stream could still couple conditions through generation order.

These partial records are not valid evidence for `B - A` or `D - C`.

The log showed all four stages for early rows:

- no-channel first;
- Pre-KV first;
- no-channel + MAD;
- Pre-KV + MAD.

## Caveats

This is a packet diagnostic, not a full MATH500 claim.

This stopped run should not be interpreted as a diagnostic result.

The replacement runner must use per-row/per-agent local seeds and the same sequential manual generation path for all A/B/C/D conditions.
