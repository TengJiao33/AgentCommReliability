# PerspectiveGap Source Ledger Rotated20 Qwen2.5-7B

## Status

Completed source-perturbation gate.

## Purpose

Test whether Qwen2.5-7B can recover from rotated source/scope perturbation when given an explicit source access ledger. The model must output `source_id` lists for each role and global rejects; local code compiles those selections into hard-routing state cards.

## Run

- Remote host: `A800_2`
- Remote workspace: `/data/xuhaoming/yfy/research_workspace`
- Model: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
- Served model: `qwen2.5-7b-perspectivegap-source-ledger`
- GPU: `7`
- Port: `8068`
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
| source-ledger 7B | 0/40 | 0.574 | 0.745 | 0.300 | 0.350 | 4.650 | 1.000 | 0.700 | 1.000 | 0.025 |

All `40` rows returned `status=ok`; local re-score matched the remote summary. There were `0` parse-error rows. Failure surfaces: `1/40` needed-reject row, `26/40` over-budget rows, and `10/40` distractor-leak rows.

## Diagnosis

The source ledger strongly improves over content-driven legacy routing on rotated scope: coverage rises from `0.076` to `0.574`, precision from `0.135` to `0.745`, and reject recall from `0.000` to `1.000`. The remaining bottleneck is budget and extra delivery.
