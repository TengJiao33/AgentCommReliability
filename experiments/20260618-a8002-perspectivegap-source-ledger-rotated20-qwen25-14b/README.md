# PerspectiveGap Source Ledger Rotated20 Qwen2.5-14B

## Status

Completed source-perturbation gate paired with the Qwen2.5-7B run.

## Purpose

Test whether a larger model can follow the rotated source access ledger more completely than 7B.

## Run

- Remote host: `A800_2`
- Remote workspace: `/data/xuhaoming/yfy/research_workspace`
- Model: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- Served model: `qwen2.5-14b-perspectivegap-source-ledger`
- GPU: `7`
- Port: `8069`
- Packet: `experiments/20260618-local-perspectivegap-source-perturbation-v0/source_perturbation_rotated20.jsonl`
- Rows: `40`
- Temperature: `0`
- Max tokens: `1024`
- Runner: `scripts/run_perspectivegap_source_ledger_router_openai_compatible.py`
- Launch script: `scripts/run_perspectivegap_source_ledger_a8002.sh`
- Scorer: `scripts/score_perspectivegap_hard_routing.py`

GPU 7 was clean before launch and returned to `4 MB` used after cleanup. No vLLM process remained.

## Result

| Condition | Strict | Coverage | Precision | Leak/eval | Budget pass | Overrun | Source acc | Visibility acc | Reject recall | Needed rejected |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| source-ledger 14B | 3/40 | 0.854 | 0.779 | 0.075 | 0.225 | 13.150 | 1.000 | 0.761 | 1.000 | 0.000 |

All `40` rows returned `status=ok`; local re-score matched the remote summary. There were `0` parse-error rows. Failure surfaces: `0/40` needed-reject rows, `31/40` over-budget rows, and `1/40` distractor-leak row.

## Diagnosis

The 14B model largely recovers source-ledger routing under rotated scope: coverage rises from legacy-on-rotated `0.150` to `0.854`, precision from `0.197` to `0.779`, and strict pass reaches `3/40`. The bottleneck shifts to budget: `31/40` rows overrun budget and mean overrun is `13.150`.
