# PACT Public-State Field Offset150 Run

Date: 2026-06-15

## Run

- Run id: `20260615-1840-a8002-pact-public-state-field-offset150-qwen25-14b`
- Machine: `A800_2`
- GPU: `7`
- Model: Qwen2.5-14B-Instruct through vLLM
- Served model: `qwen2.5-14b-pact-field-offset150`
- Packet: `experiments/20260615-local-pact-public-state-field-packet-offset150/field_packet.jsonl`
- Rows: `500`
- Completed: `500`
- Failed: `0`
- Decoding: temperature `0`, max tokens `64`

## Outputs

- Raw outputs: `outputs.jsonl`
- Evaluation: `evaluation/summary.json`
- Delta audit: `field_delta_audit/delta_summary.json`
- Span/granularity audit: `span_granularity_audit/summary.json`
- Bridge audit: `../20260615-local-pact-public-state-field-bridge-offset150/summary.json`

## Main Scores

| Condition | EM | F1 |
| --- | ---: | ---: |
| `frozen_target_plus_evidence_no_final` | `0.480` | `0.657` |
| `question_plus_evidence_no_target_no_final` | `0.450` | `0.623` |
| `question_plus_public_state_with_final` | `0.430` | `0.599` |
| `question_plus_public_state_no_final` | `0.420` | `0.593` |
| `public_target_plus_evidence_no_question_no_final` | `0.310` | `0.495` |

## Notes

This is a saved-field re-answering pressure run, not a full PACT rerun. The
source runs are `final_contract` and `compact_final_contract`, not
baseline/final-contract.

