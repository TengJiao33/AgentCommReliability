# PACT Public-State Field Packet

This packet turns the PACT HotpotQA offset50 traces into model-ready final-answer prompts.
It is a setup artifact, not a model result.

## Sources

- Baseline trace: `experiments\_archive\20260616-pruned\20260614-1552-a8002-pact-qwen25-14b-hotpot50-offset100-target-contract\comm_trace_offset100_baseline_v11.jsonl`
- Final-contract trace: `experiments\_archive\20260616-pruned\20260614-1552-a8002-pact-qwen25-14b-hotpot50-offset100-target-contract\comm_trace_offset100_final_contract_v11.jsonl`
- Bridge labels: `experiments\_archive\20260616-pruned\20260615-local-pact-public-state-field-bridge-offset100\bridge_cases.jsonl`
- Target diagnostics: `experiments\_archive\20260616-pruned\20260614-1552-a8002-pact-qwen25-14b-hotpot50-offset100-target-contract\target_slot_baseline_vs_final_cases.jsonl`

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
| `stable_right_or_not_focus` | 50 | 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149 |

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
