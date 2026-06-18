# PACT Answer-Contract Verifier Evaluation

- Prediction source: `all_no`
- Records: `74`
- Exact all-fields accuracy: `0.108`
- Primary-surface accuracy: `0.108`

## Alarm Metrics

| Alarm | Exact acc | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| `answer_contract_alarm` | 0.108 | 0.000 | 0.000 | 0.000 |
| `target_authority_alarm` | 0.365 | 0.000 | 0.000 | 0.000 |
| `answer_type_relation_alarm` | 0.676 | 0.000 | 0.000 | 0.000 |
| `short_span_granularity_alarm` | 0.608 | 0.000 | 0.000 | 0.000 |
| `evidence_adequacy_alarm` | 0.824 | 0.000 | 0.000 | 0.000 |
| `final_candidate_alarm` | 0.932 | 0.000 | 0.000 | 0.000 |

## By Label Source

| Group | Records | All fields | Primary surface | Target auth F1 | Answer-contract F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| negative_control_seed | 24 | 0.333 | 0.333 | 0.000 | 0.000 |
| positive_target_layer_seed | 50 | 0.000 | 0.000 | 0.000 | 0.000 |

## By Slice

| Group | Records | All fields | Primary surface | Target auth F1 | Answer-contract F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| offset100 | 40 | 0.100 | 0.100 | 0.000 | 0.000 |
| offset150 | 34 | 0.118 | 0.118 | 0.000 | 0.000 |

## Note

Binary metrics count `soft` as positive; exact alarm accuracy keeps `soft` distinct.
