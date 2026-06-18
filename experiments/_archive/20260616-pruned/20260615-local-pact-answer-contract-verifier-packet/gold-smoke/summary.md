# PACT Answer-Contract Verifier Evaluation

- Prediction source: `gold`
- Records: `74`
- Exact all-fields accuracy: `1.000`
- Primary-surface accuracy: `1.000`

## Alarm Metrics

| Alarm | Exact acc | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| `answer_contract_alarm` | 1.000 | 1.000 | 1.000 | 1.000 |
| `target_authority_alarm` | 1.000 | 1.000 | 1.000 | 1.000 |
| `answer_type_relation_alarm` | 1.000 | 1.000 | 1.000 | 1.000 |
| `short_span_granularity_alarm` | 1.000 | 1.000 | 1.000 | 1.000 |
| `evidence_adequacy_alarm` | 1.000 | 1.000 | 1.000 | 1.000 |
| `final_candidate_alarm` | 1.000 | 1.000 | 1.000 | 1.000 |

## By Label Source

| Group | Records | All fields | Primary surface | Target auth F1 | Answer-contract F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| negative_control_seed | 24 | 1.000 | 1.000 | 1.000 | 1.000 |
| positive_target_layer_seed | 50 | 1.000 | 1.000 | 1.000 | 1.000 |

## By Slice

| Group | Records | All fields | Primary surface | Target auth F1 | Answer-contract F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| offset100 | 40 | 1.000 | 1.000 | 1.000 | 1.000 |
| offset150 | 34 | 1.000 | 1.000 | 1.000 | 1.000 |

## Note

Binary metrics count `soft` as positive; exact alarm accuracy keeps `soft` distinct.
