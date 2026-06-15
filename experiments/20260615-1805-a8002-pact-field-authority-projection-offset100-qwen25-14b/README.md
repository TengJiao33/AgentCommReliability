# 20260615-1805-a8002-pact-field-authority-projection-offset100-qwen25-14b

## What We Tried

Ran the offset100 field-authority projection packet with Qwen2.5-14B on A800_2.
The packet contains two conditions:

- `security_projection_question_root_no_final`
- `standalone_authority_quarantine_no_final`

## Machine

- Host: A800_2
- GPU: `7`
- Free memory before launch: about `81149` MiB
- Work dir: `/data/xuhaoming/yfy/research_workspace`

## Code

- Runner: `scripts/run_pact_public_state_field_packet_a8002.sh`
- Packet: `experiments/20260615-local-pact-field-authority-projection-offset100/projection_packet.jsonl`
- Local analysis script: `scripts/analyze_pact_field_authority_projection_results.py`

## Environment

- Model: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- Served model: `qwen2.5-14b-pact-authority-offset100`
- Backend: vLLM OpenAI-compatible server
- Temperature: `0`
- Max tokens: `64`

## Command

```bash
RUN_STAMP=20260615-1805 \
RUN_ID=20260615-1805-a8002-pact-field-authority-projection-offset100-qwen25-14b \
GPU_ID=7 \
PORT=8035 \
SERVED_MODEL=qwen2.5-14b-pact-authority-offset100 \
PACKET=/data/xuhaoming/yfy/research_workspace/experiments/20260615-local-pact-field-authority-projection-offset100/projection_packet.jsonl \
OUT_DIR=/data/xuhaoming/yfy/research_workspace/experiments/20260615-1805-a8002-pact-field-authority-projection-offset100-qwen25-14b \
bash scripts/run_pact_public_state_field_packet_a8002.sh
```

## Outputs

- Raw outputs: `outputs.jsonl`
- Evaluation: `evaluation/summary.json`
- Evaluation table: `evaluation/evaluated_rows.jsonl`
- Projection delta audit: `projection_delta_audit/projection_delta_summary.json`
- Span/granularity audit: `span_granularity_audit/summary.json`

## Result

- Completed: `200/200`
- Failed: `0`
- Overall EM: `0.475`
- Overall F1: `0.633`

| Condition | Records | EM | Avg F1 |
| --- | ---: | ---: | ---: |
| `security_projection_question_root_no_final` | `100` | `0.510` | `0.661` |
| `standalone_authority_quarantine_no_final` | `100` | `0.440` | `0.604` |

## Notes

The standalone detector underperforms the simpler security projection. Treat
this as a detector pressure failure, not as a method win.
