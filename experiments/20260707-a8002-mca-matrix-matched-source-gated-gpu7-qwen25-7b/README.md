# 20260707 A800_2 MCA matrix matched source-gated GPU7

Status: prepared, not launched.

## Purpose

Run the source-gated MCA matrix after fixing the A/B/C/D generation path.

This run is intended to answer:

```text
Under matched low-temperature decoding, does question-only Pre-KV improve first-round answers, and does that improvement survive one Standard MAD text debate round relative to a no-channel first round?
```

## Required source state

The runner must be the version audited in:

- `reports/2026-07-07-mca-matrix-source-gate-audit.md`

Required source properties:

- A/B first-round generations are both sequential manual generations;
- same row and same agent use the same local seed for A and B;
- C/D debate generations are both sequential manual generations;
- same row and same debate agent use the same local seed for C and D;
- each record writes `generation_seeds`;
- no old partial output is resumed.

## Packets

- `math500/mca_disagreement_v1`: 221 rows, label-free disagreement packet.
- `math500/mca_gold_contrast_v1`: 142 rows, gold-stratified diagnostic packet.

## Remote

- Host: `A800_2`
- Workspace: `/data/xuhaoming/yfy/research_workspace`
- GPU: `7`
- Python: `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python`
- Model: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`

## Output run ids

- `20260707-a8002-gpu7-mca-matrix-matched-disagreement-qwen25-7b`
- `20260707-a8002-gpu7-mca-matrix-matched-gold-contrast-qwen25-7b`

## Interpretation boundary

This is a packet diagnostic. It can support `B - A` and `D - C` on the selected packets.

It cannot by itself establish full MATH500 performance or prove that the system exceeds exact Standard MAD full-run baseline.

