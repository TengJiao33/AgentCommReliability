# PerspectiveGap Hard Routing Smoke4 Qwen2.5-7B

## Status

Superseded diagnostic smoke. This first direct hard-card run used the original V0 prompt and exposed a prompt-contract ambiguity around global `rejected` and `visibility`.

## Purpose

Check whether the hard-routing packet can be served to a local OpenAI-compatible Qwen2.5-7B endpoint and scored end to end.

## Run

- Remote host: `A800_2`
- Remote workspace: `/data/xuhaoming/yfy/research_workspace`
- Model: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
- Served model: `qwen2.5-7b-perspectivegap-hard-smoke4`
- GPU: `7`
- Port: `8065`
- Packet: `experiments/20260618-local-perspectivegap-hard-routing-v0/hard_packet_smoke4.jsonl`
- Rows: `4`
- Temperature: `0`
- Max tokens: `1536`
- Runner: `scripts/run_perspectivegap_hard_routing_openai_compatible.py`
- Scorer: `scripts/score_perspectivegap_hard_routing.py`

## Result

| Run | Strict | Coverage | Precision | Leak/eval | Budget pass | Source acc | Visibility acc | Reject recall | Needed rejected |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| direct hard-card v0 prompt | 0/4 | 0.467 | 0.875 | 0.000 | 1.000 | 1.000 | 0.143 | 1.000 | 2.500 |

The result parsed and scored, but concrete outputs showed the prompt allowed a bad interpretation: the model put fragments in global `rejected` because one role did not need them, even when another role did. It also used `shared_all` as a generic usefulness label rather than intended recipient scope.

## Consequence

This run is plumbing-positive but behaviorally superseded by `20260618-a8002-perspectivegap-hard-routing-smoke4-promptv2-qwen25-7b`, which clarifies the prompt contract.
