# 20260707 A800_2 MCA matrix matched source-gated GPU1

Status: launched on 2026-07-07 17:12:51 CST.

## Purpose

Run the source-gated MCA matrix on A800_2 GPU 1.

The run is intended to answer:

```text
Under matched low-temperature decoding, does question-only Pre-KV improve first-round answers, and does that improvement survive one Standard MAD text debate round relative to a no-channel first round?
```

## Matrix

- A: no-channel first round.
- B: question-only Pre-KV first round.
- C: no-channel first round followed by one Standard MAD text debate round.
- D: Pre-KV first round followed by one Standard MAD text debate round.

Primary contrasts:

- `B - A`: first-round Pre-KV effect.
- `D - C`: Pre-KV effect after MAD text debate.

## Source gate

Required source properties:

- A/B first-round generations are both sequential manual generations.
- Same row and same agent use the same local seed for A and B.
- C/D debate generations are both sequential manual generations.
- Same row and same debate agent use the same local seed for C and D.
- Each record writes `generation_seeds`.
- The run does not resume old partial output.

Audit report:

- `reports/2026-07-07-mca-matrix-source-gate-audit.md`

## Packets

- `math500/mca_disagreement_v1`: 221 rows.
- `math500/mca_gold_contrast_v1`: 142 rows.

## Remote

- Host: `A800_2`
- Workspace: `/data/xuhaoming/yfy/research_workspace`
- GPU: `1`
- Python: `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python`
- Model: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`

## Output run ids

- `20260707-a8002-gpu1-mca-matrix-matched-disagreement-qwen25-7b`
- `20260707-a8002-gpu1-mca-matrix-matched-gold-contrast-qwen25-7b`

## Expected outputs

- `/data/xuhaoming/yfy/research_workspace/experiments/20260707-a8002-gpu1-mca-matrix-matched-disagreement-qwen25-7b/math500-qwen25-7b-instruct-mca-pre-kv-then-mad/records.jsonl`
- `/data/xuhaoming/yfy/research_workspace/experiments/20260707-a8002-gpu1-mca-matrix-matched-gold-contrast-qwen25-7b/math500-qwen25-7b-instruct-mca-pre-kv-then-mad/records.jsonl`

## Launch record

Launch command:

```bash
cd /data/xuhaoming/yfy/research_workspace/experiments/20260707-a8002-mca-matrix-matched-source-gated-gpu1-qwen25-7b
nohup bash run_remote_serial_matched.sh > serial.log 2>&1 < /dev/null &
```

Process ids after launch:

- serial script: `4050883`
- first packet timeout wrapper: `4050909`
- first packet Python runner: `4050910`

Launch checks:

- local and remote `scripts/run_mca_pre_kv_then_mad.py` SHA256 matched: `02b9fb01612939d2fcd4bf9cc743f38faadc7bdb8ca6ce0b081e944effc85e52`;
- remote `py_compile` passed;
- `bash -n run_remote_serial_matched.sh` passed;
- packet row counts were `221` and `142`;
- GPU 1 was empty at launch: `4 MB / 81920 MB`, `0%` utilization;
- output run directories did not exist before launch.

First record check:

- `mca_disagreement_v1` wrote `1` record by 2026-07-07 17:17 CST;
- log showed matched sequential stages: `no-channel first 1/3..3/3`, `pre-kv receiver 1/3..3/3`, `no-channel debate 1/3..3/3`, `pre-kv debate 1/3..3/3`;
- first record contains `generation_seeds`;
- A/B first-round seeds match per agent;
- C/D debate seeds match per agent.

## Boundary

This is a packet diagnostic, not a full MATH500 claim. It can support packet-level `B - A` and `D - C` under the matched source gate.
