# PACT Answer-Contract Split-Alarm Packet

This packet decomposes the answer-contract verifier into one narrow prompt per alarm.

- Base records: `74`
- Prompt rows: `444`
- Tasks: `['answer_contract_alarm', 'target_authority_alarm', 'answer_type_relation_alarm', 'short_span_granularity_alarm', 'evidence_adequacy_alarm', 'final_candidate_alarm']`

## Gold Counts By Task

| Task | Gold counts |
| --- | --- |
| `answer_contract_alarm` | `{'no': 8, 'yes': 66}` |
| `target_authority_alarm` | `{'no': 27, 'soft': 2, 'yes': 45}` |
| `answer_type_relation_alarm` | `{'no': 50, 'yes': 24}` |
| `short_span_granularity_alarm` | `{'no': 45, 'yes': 29}` |
| `evidence_adequacy_alarm` | `{'no': 61, 'yes': 13}` |
| `final_candidate_alarm` | `{'no': 69, 'yes': 5}` |

## Output Schema

Each model output should be one JSON object with:

- `label`: `yes`, `no`, or `soft` for target-authority; `yes` or `no` for other tasks;
- `rationale`: one short sentence.
