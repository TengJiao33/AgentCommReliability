# PACT Split-Alarm Verifier Evaluation

- Prediction source: `all_no`
- Records: `444`
- Parse failures: `0`
- Exact label accuracy: `0.586`
- Positive/negative accuracy: `0.586`

## By Task

| Task | Records | Acc | Precision | Recall | F1 | TP | FP | TN | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `answer_contract_alarm` | 74 | 0.108 | 0.000 | 0.000 | 0.000 | 0 | 0 | 8 | 66 |
| `answer_type_relation_alarm` | 74 | 0.676 | 0.000 | 0.000 | 0.000 | 0 | 0 | 50 | 24 |
| `evidence_adequacy_alarm` | 74 | 0.824 | 0.000 | 0.000 | 0.000 | 0 | 0 | 61 | 13 |
| `final_candidate_alarm` | 74 | 0.932 | 0.000 | 0.000 | 0.000 | 0 | 0 | 69 | 5 |
| `short_span_granularity_alarm` | 74 | 0.608 | 0.000 | 0.000 | 0.000 | 0 | 0 | 45 | 29 |
| `target_authority_alarm` | 74 | 0.365 | 0.000 | 0.000 | 0.000 | 0 | 0 | 27 | 47 |

## Prediction Counts

| Task | Gold | Predicted |
| --- | --- | --- |
| `answer_contract_alarm` | `{'no': 8, 'yes': 66}` | `{'no': 74}` |
| `answer_type_relation_alarm` | `{'no': 50, 'yes': 24}` | `{'no': 74}` |
| `evidence_adequacy_alarm` | `{'no': 61, 'yes': 13}` | `{'no': 74}` |
| `final_candidate_alarm` | `{'no': 69, 'yes': 5}` | `{'no': 74}` |
| `short_span_granularity_alarm` | `{'no': 45, 'yes': 29}` | `{'no': 74}` |
| `target_authority_alarm` | `{'no': 27, 'soft': 2, 'yes': 45}` | `{'no': 74}` |
