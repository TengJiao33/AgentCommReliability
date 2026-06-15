# PACT Split-Alarm Verifier Evaluation

- Prediction source: `outputs`
- Records: `444`
- Parse failures: `0`
- Exact label accuracy: `0.590`
- Positive/negative accuracy: `0.617`

## By Task

| Task | Records | Acc | Precision | Recall | F1 | TP | FP | TN | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `answer_contract_alarm` | 74 | 0.419 | 0.926 | 0.379 | 0.538 | 25 | 2 | 6 | 41 |
| `answer_type_relation_alarm` | 74 | 0.622 | 0.250 | 0.083 | 0.125 | 2 | 6 | 44 | 22 |
| `evidence_adequacy_alarm` | 74 | 0.743 | 0.350 | 0.538 | 0.424 | 7 | 13 | 48 | 6 |
| `final_candidate_alarm` | 74 | 0.824 | 0.000 | 0.000 | 0.000 | 0 | 8 | 61 | 5 |
| `short_span_granularity_alarm` | 74 | 0.608 | 0.500 | 0.034 | 0.065 | 1 | 1 | 44 | 28 |
| `target_authority_alarm` | 74 | 0.486 | 0.667 | 0.383 | 0.486 | 18 | 9 | 18 | 29 |

## Prediction Counts

| Task | Gold | Predicted |
| --- | --- | --- |
| `answer_contract_alarm` | `{'no': 8, 'yes': 66}` | `{'no': 47, 'yes': 27}` |
| `answer_type_relation_alarm` | `{'no': 50, 'yes': 24}` | `{'no': 66, 'yes': 8}` |
| `evidence_adequacy_alarm` | `{'no': 61, 'yes': 13}` | `{'no': 54, 'yes': 20}` |
| `final_candidate_alarm` | `{'no': 69, 'yes': 5}` | `{'no': 66, 'yes': 8}` |
| `short_span_granularity_alarm` | `{'no': 45, 'yes': 29}` | `{'no': 72, 'yes': 2}` |
| `target_authority_alarm` | `{'no': 27, 'soft': 2, 'yes': 45}` | `{'no': 47, 'soft': 12, 'yes': 15}` |
