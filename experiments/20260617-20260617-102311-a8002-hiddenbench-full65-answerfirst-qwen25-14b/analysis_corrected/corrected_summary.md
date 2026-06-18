# HiddenBench Corrected Summary

- Records: `513`
- Rescoring changes: `1`

| Condition | Records | Correct | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| exchange_then_decide | 65 | 24 | 0.369 | 0 |
| full_info | 65 | 59 | 0.908 | 0 |
| oracle_public_facts | 65 | 56 | 0.862 | 0 |
| shared_only | 65 | 1 | 0.015 | 0 |
| single_private_agent | 253 | 62 | 0.245 | 1 |

## Paired Contrasts

- `full_info_correct_shared_only_wrong`: `59`
- `oracle_public_facts_correct_shared_only_wrong`: `56`
- `oracle_public_facts_correct_exchange_then_decide_wrong`: `33`
- `full_info_correct_exchange_then_decide_wrong`: `35`
- `exchange_then_decide_correct_shared_only_wrong`: `24`
- `exchange_then_decide_correct_oracle_public_facts_wrong`: `1`
- `full_info_correct_oracle_public_facts_wrong`: `4`
- `oracle_public_facts_correct_full_info_wrong`: `1`
- `oracle_and_exchange_both_correct`: `23`

## Rescoring Changes

- task `62` `exchange_then_decide`: `None` -> `Option C: Logistics software company`, correct `False` -> `True`
