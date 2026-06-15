# 20260615-1951-a8002-pact-answer-contract-verifier-v2-qwen25-14b

## What We Tried

Ran the same `74`-record PACT answer-contract verifier packet with a stricter
prompt-v2. The records, public-state fields, gold labels, model, temperature,
and evaluator are the same as the v1 Qwen2.5-14B verifier run.

Prompt-v2 changes:

- adds consistency rules tying `answer_contract_alarm` to subalarms and primary
  surface;
- restricts `target_authority_alarm = soft`;
- adds a decision order;
- sharpens distinctions between public-target misdirection, evidence adequacy,
  final-candidate attraction, and span/granularity.

## Machine

- Host: A800_2 (`10-116-90-20`)
- GPU: `7`
- Free memory before launch: `81149 MiB`
- Work dir: `/data/xuhaoming/yfy/research_workspace`

## Code

- Prompt-v2 packet builder:
  `scripts/build_pact_answer_contract_verifier_prompt_v2_packet.py`
- Local runner: `scripts/run_pact_public_state_field_packet.py`
- Verifier evaluator: `scripts/evaluate_pact_answer_contract_verifier.py`
- Launcher: `scripts/run_pact_answer_contract_verifier_a8002.sh`

## Environment

- Python: `3.10.20`
- PyTorch: `2.4.0+cu121`
- vLLM: `dev`
- LLM/API backend: vLLM OpenAI-compatible server
- Model path: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- Served model: `qwen2.5-14b-answer-contract-verifier`

## Data / Task

- Packet:
  `/data/xuhaoming/yfy/research_workspace/experiments/20260615-local-pact-answer-contract-verifier-packet-v2/verifier_packet.jsonl`
- Local packet source:
  `experiments/20260615-local-pact-answer-contract-verifier-packet-v2/verifier_packet.jsonl`
- Size: `74` records
- Label sources: `50` positive target-layer seed records and `24` negative-control seed records
- Prompt version: `v2_strict_consistency`

## Command

```bash
cd /data/xuhaoming/yfy/research_workspace
GPU_ID=7 \
PORT=8035 \
RUN_STAMP=20260615-1951 \
RUN_ID=20260615-1951-a8002-pact-answer-contract-verifier-v2-qwen25-14b \
PACKET=/data/xuhaoming/yfy/research_workspace/experiments/20260615-local-pact-answer-contract-verifier-packet-v2/verifier_packet.jsonl \
bash scripts/run_pact_answer_contract_verifier_a8002.sh
```

## Outputs

- Remote run log:
  `/data/xuhaoming/yfy/research_workspace/logs/pact-answer-contract-verifier-20260615-1951.log`
- Remote vLLM log:
  `/data/xuhaoming/yfy/research_workspace/logs/pact-answer-contract-verifier-vllm-20260615-1951.log`
- Local run log copies:
  `pact-answer-contract-verifier-20260615-1951.log`
  and `pact-answer-contract-verifier-vllm-20260615-1951.log`
- Outputs: `outputs.jsonl`
- Manifest: `manifest.json`
- Evaluation: `evaluation/summary.md`, `evaluation/summary.json`,
  `evaluation/evaluated_rows.jsonl`

## Result

- Status: passed execution; prompt-v2 partly repaired alarms but still failed as
  a structured verifier.
- Completed: `74/74`
- Failed requests: `0`
- JSON parse failures: `0`
- Exact all-fields accuracy: `0.108`
- Primary-surface accuracy: `0.216`

Selected comparison against v1:

| Metric | v1 | v2 |
| --- | ---: | ---: |
| Exact all-fields accuracy | `0.081` | `0.108` |
| Primary-surface accuracy | `0.230` | `0.216` |
| `answer_contract_alarm` F1 | `0.442` | `0.712` |
| `answer_contract_alarm` recall | `0.288` | `0.561` |
| `target_authority_alarm` F1 | `0.688` | `0.526` |
| `target_authority_alarm = soft` predictions | `43` | `12` |
| `short_span_granularity_alarm` F1 | `0.324` | `0.125` |

## Notes

Prompt-v2 did what it was designed to do in one narrow sense: it reduced
`soft` overuse and made the global answer-contract alarm fire more often.

It did not solve the verifier:

- primary-surface accuracy stayed low;
- positive-seed all-fields accuracy remained `0.000`;
- short-span/granularity recall collapsed to `2/29`;
- the model still over-predicted `no_answer_contract_failure` and
  `public_target_misdirection`.

This suggests the next repair should not be another longer one-shot taxonomy
prompt. A better next shape is likely split-stage scoring: first binary
answer-contract risk, then separate targeted classifiers or few-shot contrast
sets for target authority, answer type/relation, span/granularity, evidence
adequacy, and final-candidate attraction.
