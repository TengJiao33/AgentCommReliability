# PACT Public-State Field Packet

This packet turns the PACT HotpotQA offset50 traces into model-ready final-answer prompts.
It is a setup artifact, not a model result.

## Sources

- Baseline trace: `experiments\20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired\comm_trace_pact_offset50_baseline_v11.jsonl`
- Final-contract trace: `experiments\20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired\comm_trace_pact_offset50_final_contract_v11.jsonl`
- Bridge labels: `experiments\20260615-local-pact-public-state-field-bridge\bridge_cases.jsonl`
- Target diagnostics: `experiments\20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired\target_slot_drift_cases.jsonl`

## Size

- Samples: `50`
- Source runs: `{'baseline': 250, 'final_contract': 250}`
- Conditions per source/sample: `5`
- Prompt rows: `500`

## Conditions

| Condition | Rows | Axis |
| --- | ---: | --- |
| `frozen_target_plus_evidence_no_final` | 100 | `frozen_target_contract` |
| `public_target_plus_evidence_no_question_no_final` | 100 | `public_target_sufficiency` |
| `question_plus_evidence_no_target_no_final` | 100 | `target_field_ablation` |
| `question_plus_public_state_no_final` | 100 | `evidence_to_answer_commitment` |
| `question_plus_public_state_with_final` | 100 | `final_answer_commitment` |

## Bridge Coverage

| Bridge layer | Samples | Sample indices |
| --- | ---: | --- |
| `diagnostic_noise` | 1 | 59 |
| `evidence_carriage` | 5 | 68, 71, 77, 88, 94 |
| `final_answer_commitment` | 12 | 50, 54, 55, 62, 64, 66, 74, 83, 87, 89, 92, 97 |
| `positive_contract_rescue` | 6 | 57, 61, 78, 85, 93, 99 |
| `stable_right_or_not_focus` | 22 | 51, 52, 53, 56, 63, 65, 69, 70, 72, 73, 75, 76, 79, 80, 81, 84, 86, 90, 91, 95, 96, 98 |
| `target_contract` | 2 | 58, 82 |
| `target_final_alignment` | 2 | 60, 67 |

## How To Use

Run a model over `field_packet.jsonl`, feeding each row's `prompt` and writing back the raw output keyed by `packet_id`.
Evaluate against the `evaluation.gold_answer` metadata with HotpotQA exact match/F1, then slice by `condition`, `source_run`, `bridge_layer`, `bridge_family`, and `target_slot_diagnostic.target_slot_drift_candidate`.

The intended comparisons are:

- `question_plus_public_state_with_final` vs `question_plus_public_state_no_final`: does the final-answer candidate help or mislead?
- `question_plus_public_state_no_final` vs `question_plus_evidence_no_target_no_final`: does the public target field add value when the original question is visible?
- `question_plus_public_state_no_final` vs `frozen_target_plus_evidence_no_final`: does a question-derived frozen target repair drift or granularity failures?
- `question_plus_public_state_no_final` vs `public_target_plus_evidence_no_question_no_final`: can the public target alone preserve the task when the original question is absent?

## Caveat

The packet uses saved PACT fields and does not retrieve external evidence. It tests answer extraction/commitment from public-state surfaces, not full HotpotQA solving from scratch.
