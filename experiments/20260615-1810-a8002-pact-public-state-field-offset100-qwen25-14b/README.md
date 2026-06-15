# 20260615-1810-a8002-pact-public-state-field-offset100-qwen25-14b

## What We Tried

Ran the full offset100 PACT public-state field packet with Qwen2.5-14B on
A800_2 to provide fixed controls for the field-authority projection run.

## Machine

- Host: A800_2
- GPU: `7`
- Free memory before launch: about `81149` MiB
- Work dir: `/data/xuhaoming/yfy/research_workspace`

## Code

- Runner: `scripts/run_pact_public_state_field_packet_a8002.sh`
- Packet: `experiments/20260615-local-pact-public-state-field-packet-offset100/field_packet.jsonl`
- Delta audit: `scripts/analyze_pact_public_state_field_results.py`

## Environment

- Model: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- Served model: `qwen2.5-14b-pact-field-offset100`
- Backend: vLLM OpenAI-compatible server
- Temperature: `0`
- Max tokens: `64`

## Command

```bash
RUN_STAMP=20260615-1810 \
RUN_ID=20260615-1810-a8002-pact-public-state-field-offset100-qwen25-14b \
GPU_ID=7 \
PORT=8036 \
SERVED_MODEL=qwen2.5-14b-pact-field-offset100 \
PACKET=/data/xuhaoming/yfy/research_workspace/experiments/20260615-local-pact-public-state-field-packet-offset100/field_packet.jsonl \
OUT_DIR=/data/xuhaoming/yfy/research_workspace/experiments/20260615-1810-a8002-pact-public-state-field-offset100-qwen25-14b \
bash scripts/run_pact_public_state_field_packet_a8002.sh
```

## Outputs

- Raw outputs: `outputs.jsonl`
- Evaluation: `evaluation/summary.json`
- Evaluation table: `evaluation/evaluated_rows.jsonl`
- Field delta audit: `field_delta_audit/delta_summary.json`
- Span/granularity audit: `span_granularity_audit/summary.json`

## Result

- Completed: `500/500`
- Failed: `0`
- Overall EM: `0.452`
- Overall F1: `0.602`

| Condition | Records | EM | Avg F1 |
| --- | ---: | ---: | ---: |
| `frozen_target_plus_evidence_no_final` | `100` | `0.560` | `0.698` |
| `question_plus_public_state_no_final` | `100` | `0.500` | `0.648` |
| `question_plus_evidence_no_target_no_final` | `100` | `0.470` | `0.610` |
| `question_plus_public_state_with_final` | `100` | `0.430` | `0.575` |
| `public_target_plus_evidence_no_question_no_final` | `100` | `0.300` | `0.481` |

## Notes

Replacing public `Action Required` with a frozen question-derived target is the
best fixed control on this neighboring slice. Hiding the original question while
keeping public target is sharply harmful.
