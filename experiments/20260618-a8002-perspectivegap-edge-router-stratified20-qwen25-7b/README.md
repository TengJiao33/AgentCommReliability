# PerspectiveGap Edge Router Stratified20 Qwen2.5-7B

## Status

Completed diagnostic gate. This run tests an edge-router plus symbolic scope compiler on the same stratified20 PerspectiveGap hard-routing subset used by the earlier role-list runs.

## Purpose

Separate two failures observed in direct hard-card prompting:

- edge selection: which fragments each role should receive;
- state-card bookkeeping: `source_id` and `visibility` labels.

The model outputs only role-fragment edges and global rejections. The local compiler then fills `source_id` from the packet and computes `visibility` from the selected recipient set.

## Run

- Remote host: `A800_2`
- Remote workspace: `/data/xuhaoming/yfy/research_workspace`
- Model: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
- Served model: `qwen2.5-7b-perspectivegap-edge-router`
- GPU: `7`
- Port: `8066`
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
GPU_ID=7 \
PORT=8066 \
RUN_ID=20260618-a8002-perspectivegap-edge-router-stratified20-qwen25-7b \
PACKET=/data/xuhaoming/yfy/research_workspace/experiments/20260618-local-perspectivegap-hard-routing-v0/hard_packet_stratified20.jsonl \
bash scripts/run_perspectivegap_edge_router_a8002.sh
```

GPU 7 was clean before launch and returned to `4 MB` used after cleanup. No vLLM process remained.

## Result

| Condition | Strict | Coverage | Precision | Leak/eval | Budget pass | Overrun | Source acc | Visibility acc | Reject recall | Needed rejected |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| edge-router compiled scope 7B | 0/40 | 0.331 | 0.613 | 0.200 | 0.575 | 4.050 | 1.000 | 0.760 | 0.550 | 1.900 |

All `40` rows returned `status=ok`; local re-score matched the remote summary. There were `0` parse-error rows. Failure surfaces: `28/40` rows rejected at least one needed fragment, `17/40` rows exceeded budget, and `7/40` rows leaked at least one distractor.

## Diagnosis

Compiled scope improves the label surface compared with direct hard-card prompting, but 7B edge selection is too conservative and too noisy. Compared with the earlier 7B legacy projection on the same 40 rows, coverage drops from `0.443` to `0.331`, precision drops from `0.786` to `0.613`, and leak rises from `0.050` to `0.200`; the gain is reject recall rising from `0.000` to `0.550`.

This suggests the hard edge-router prompt made the model more willing to reject, but it rejected too many needed fragments.
