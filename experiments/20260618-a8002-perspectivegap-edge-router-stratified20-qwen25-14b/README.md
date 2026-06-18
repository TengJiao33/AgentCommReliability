# PerspectiveGap Edge Router Stratified20 Qwen2.5-14B

## Status

Completed diagnostic gate paired with the Qwen2.5-7B edge-router run.

## Purpose

Check whether a larger model fixes the edge selection failure after `source_id` and `visibility` are compiled deterministically from the selected role-fragment edges.

## Run

- Remote host: `A800_2`
- Remote workspace: `/data/xuhaoming/yfy/research_workspace`
- Model: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- Served model: `qwen2.5-14b-perspectivegap-edge-router`
- GPU: `7`
- Port: `8067`
- Packet: `experiments/20260618-local-perspectivegap-hard-routing-v0/hard_packet_stratified20.jsonl`
- Rows: `40`
- Temperature: `0`
- Max tokens: `1024`
- Runner: `scripts/run_perspectivegap_edge_router_openai_compatible.py`
- Launch script: `scripts/run_perspectivegap_edge_router_a8002.sh`
- Scorer: `scripts/score_perspectivegap_hard_routing.py`

Remote command:

```bash
WORKSPACE=/data/xuhaoming/yfy/research_workspace \
MODEL_PATH=/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct \
SERVED_MODEL=qwen2.5-14b-perspectivegap-edge-router \
GPU_ID=7 \
PORT=8067 \
RUN_ID=20260618-a8002-perspectivegap-edge-router-stratified20-qwen25-14b \
PACKET=/data/xuhaoming/yfy/research_workspace/experiments/20260618-local-perspectivegap-hard-routing-v0/hard_packet_stratified20.jsonl \
bash scripts/run_perspectivegap_edge_router_a8002.sh
```

GPU 7 was clean before launch and returned to `4 MB` used after cleanup. No vLLM process remained.

## Result

| Condition | Strict | Coverage | Precision | Leak/eval | Budget pass | Overrun | Source acc | Visibility acc | Reject recall | Needed rejected |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| edge-router compiled scope 14B | 0/40 | 0.513 | 0.669 | 0.600 | 0.100 | 7.650 | 1.000 | 0.751 | 0.525 | 1.350 |

All `40` rows returned `status=ok`; local re-score matched the remote summary. There were `0` parse-error rows. Failure surfaces: `31/40` rows rejected at least one needed fragment, `36/40` rows exceeded budget, and `22/40` rows leaked at least one distractor.

## Diagnosis

The 14B model raises coverage over 7B (`0.513` vs `0.331`) but loses budget control and leaks more distractors. Compared with the earlier 14B legacy projection on the same 40 rows, coverage drops from `0.615` to `0.513`, precision drops from `0.808` to `0.669`, leak rises from `0.450` to `0.600`, and budget pass drops from `0.400` to `0.100`.

The scale trend is clear but not encouraging: a larger model routes more aggressively, while the hard edge-router prompt makes budget and leakage worse.
