# PACT Public-State Field Packet

This packet turns paired PACT HotpotQA traces into model-ready final-answer prompts.
It is a setup artifact, not a model result.

## Sources

- Left source `final_contract`: `experiments\_archive\20260616-pruned\20260614-1642-a8002-pact-qwen25-14b-hotpot50-offset150-compact-target\comm_trace_offset150_final_contract_v11.jsonl`
- Right source `compact_final_contract`: `experiments\_archive\20260616-pruned\20260614-1642-a8002-pact-qwen25-14b-hotpot50-offset150-compact-target\comm_trace_offset150_compact_final_v11.jsonl`
- Bridge labels: `experiments\_archive\20260616-pruned\20260615-local-pact-public-state-field-bridge-offset150\bridge_cases.jsonl`
- Target diagnostics: `experiments\_archive\20260616-pruned\20260614-1642-a8002-pact-qwen25-14b-hotpot50-offset150-compact-target\target_slot_final_vs_compact_final_cases.jsonl`

## Size

- Samples: `50`
- Source runs: `{'compact_final_contract': 250, 'final_contract': 250}`
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
| `stable_right_or_not_focus` | 50 | 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199 |

## How To Use

Run a model over `field_packet.jsonl`, feeding each row's `prompt` and writing back the raw output keyed by `packet_id`.
Evaluate against the `evaluation.gold_answer` metadata with HotpotQA exact match/F1, then slice by `condition`, `source_run`, `bridge_layer`, `bridge_family`, and `target_slot_diagnostic.target_slot_drift_candidate`.
The source-run labels in this packet are: `compact_final_contract`, `final_contract`.

The intended comparisons are:

- `question_plus_public_state_with_final` vs `question_plus_public_state_no_final`: does the final-answer candidate help or mislead?
- `question_plus_public_state_no_final` vs `question_plus_evidence_no_target_no_final`: does the public target field add value when the original question is visible?
- `question_plus_public_state_no_final` vs `frozen_target_plus_evidence_no_final`: does a question-derived frozen target repair drift or granularity failures?
- `question_plus_public_state_no_final` vs `public_target_plus_evidence_no_question_no_final`: can the public target alone preserve the task when the original question is absent?

## Caveat

The packet uses saved PACT fields and does not retrieve external evidence. It tests answer extraction/commitment from public-state surfaces, not full HotpotQA solving from scratch.
