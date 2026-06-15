# PACT Split-Alarm Verifier Evaluation

- Prediction source: `gold`
- Records: `444`
- Parse failures: `0`
- Exact label accuracy: `1.000`
- Positive/negative accuracy: `1.000`

## By Task

| Task | Records | Acc | Precision | Recall | F1 | TP | FP | TN | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `answer_contract_alarm` | 74 | 1.000 | 1.000 | 1.000 | 1.000 | 66 | 0 | 8 | 0 |
| `answer_type_relation_alarm` | 74 | 1.000 | 1.000 | 1.000 | 1.000 | 24 | 0 | 50 | 0 |
| `evidence_adequacy_alarm` | 74 | 1.000 | 1.000 | 1.000 | 1.000 | 13 | 0 | 61 | 0 |
| `final_candidate_alarm` | 74 | 1.000 | 1.000 | 1.000 | 1.000 | 5 | 0 | 69 | 0 |
| `short_span_granularity_alarm` | 74 | 1.000 | 1.000 | 1.000 | 1.000 | 29 | 0 | 45 | 0 |
| `target_authority_alarm` | 74 | 1.000 | 1.000 | 1.000 | 1.000 | 47 | 0 | 27 | 0 |

## Prediction Counts

| Task | Gold | Predicted |
| --- | --- | --- |
| `answer_contract_alarm` | `{'no': 8, 'yes': 66}` | `{'no': 8, 'yes': 66}` |
| `answer_type_relation_alarm` | `{'no': 50, 'yes': 24}` | `{'no': 50, 'yes': 24}` |
| `evidence_adequacy_alarm` | `{'no': 61, 'yes': 13}` | `{'no': 61, 'yes': 13}` |
| `final_candidate_alarm` | `{'no': 69, 'yes': 5}` | `{'no': 69, 'yes': 5}` |
| `short_span_granularity_alarm` | `{'no': 45, 'yes': 29}` | `{'no': 45, 'yes': 29}` |
| `target_authority_alarm` | `{'no': 27, 'soft': 2, 'yes': 45}` | `{'no': 27, 'soft': 2, 'yes': 45}` |
