# PACT Answer-Contract Verifier Evaluation

- Prediction source: `outputs`
- Records: `74`
- Exact all-fields accuracy: `0.081`
- Primary-surface accuracy: `0.230`

## Alarm Metrics

| Alarm | Exact acc | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| `answer_contract_alarm` | 0.351 | 0.950 | 0.288 | 0.442 |
| `target_authority_alarm` | 0.203 | 0.673 | 0.702 | 0.688 |
| `answer_type_relation_alarm` | 0.649 | 0.333 | 0.083 | 0.133 |
| `short_span_granularity_alarm` | 0.662 | 0.750 | 0.207 | 0.324 |
| `evidence_adequacy_alarm` | 0.743 | 0.286 | 0.308 | 0.296 |
| `final_candidate_alarm` | 0.743 | 0.111 | 0.400 | 0.174 |

## By Label Source

| Group | Records | All fields | Primary surface | Target auth F1 | Answer-contract F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| negative_control_seed | 24 | 0.250 | 0.375 | 0.250 | 0.455 |
| positive_target_layer_seed | 50 | 0.000 | 0.160 | 0.775 | 0.438 |

## By Slice

| Group | Records | All fields | Primary surface | Target auth F1 | Answer-contract F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| offset100 | 40 | 0.100 | 0.250 | 0.640 | 0.364 |
| offset150 | 34 | 0.059 | 0.206 | 0.739 | 0.524 |

## Note

Binary metrics count `soft` as positive; exact alarm accuracy keeps `soft` distinct.
