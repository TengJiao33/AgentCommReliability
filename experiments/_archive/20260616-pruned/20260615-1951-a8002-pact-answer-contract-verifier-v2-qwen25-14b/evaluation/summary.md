# PACT Answer-Contract Verifier Evaluation

- Prediction source: `outputs`
- Records: `74`
- Exact all-fields accuracy: `0.108`
- Primary-surface accuracy: `0.216`

## Alarm Metrics

| Alarm | Exact acc | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| `answer_contract_alarm` | 0.595 | 0.974 | 0.561 | 0.712 |
| `target_authority_alarm` | 0.392 | 0.690 | 0.426 | 0.526 |
| `answer_type_relation_alarm` | 0.554 | 0.200 | 0.125 | 0.154 |
| `short_span_granularity_alarm` | 0.622 | 0.667 | 0.069 | 0.125 |
| `evidence_adequacy_alarm` | 0.811 | 0.444 | 0.308 | 0.364 |
| `final_candidate_alarm` | 0.851 | 0.125 | 0.200 | 0.154 |

## By Label Source

| Group | Records | All fields | Primary surface | Target auth F1 | Answer-contract F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| negative_control_seed | 24 | 0.333 | 0.417 | 0.364 | 0.741 |
| positive_target_layer_seed | 50 | 0.000 | 0.120 | 0.554 | 0.701 |

## By Slice

| Group | Records | All fields | Primary surface | Target auth F1 | Answer-contract F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| offset100 | 40 | 0.100 | 0.225 | 0.359 | 0.691 |
| offset150 | 34 | 0.118 | 0.206 | 0.703 | 0.735 |

## Note

Binary metrics count `soft` as positive; exact alarm accuracy keeps `soft` distinct.
