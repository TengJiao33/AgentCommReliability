# HiddenBench Subset Summary

- Records: `experiments\20260617-163732-a8002-hiddenbench-v2-stage1-full65-qwen25-14b\analysis_corrected\corrected_records.jsonl`

## all

- Tasks: `65`

| Condition | Correct | Records | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| `exchange_then_decide` | `24` | `65` | `0.369` | `0` |
| `fact_only_constraint_decide` | `56` | `65` | `0.862` | `0` |
| `fact_only_exchange` | `57` | `65` | `0.877` | `0` |
| `full_info` | `59` | `65` | `0.908` | `0` |
| `oracle_public_facts` | `56` | `65` | `0.862` | `0` |
| `shared_only` | `1` | `65` | `0.015` | `0` |

## full_info_correct

- Tasks: `59`

| Condition | Correct | Records | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| `exchange_then_decide` | `24` | `59` | `0.407` | `0` |
| `fact_only_constraint_decide` | `56` | `59` | `0.949` | `0` |
| `fact_only_exchange` | `57` | `59` | `0.966` | `0` |
| `full_info` | `59` | `59` | `1.000` | `0` |
| `oracle_public_facts` | `55` | `59` | `0.932` | `0` |
| `shared_only` | `0` | `59` | `0.000` | `0` |

## full_info_and_oracle_public_facts_correct

- Tasks: `55`

| Condition | Correct | Records | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| `exchange_then_decide` | `23` | `55` | `0.418` | `0` |
| `fact_only_constraint_decide` | `55` | `55` | `1.000` | `0` |
| `fact_only_exchange` | `55` | `55` | `1.000` | `0` |
| `full_info` | `55` | `55` | `1.000` | `0` |
| `oracle_public_facts` | `55` | `55` | `1.000` | `0` |
| `shared_only` | `0` | `55` | `0.000` | `0` |

## clean_info_unstable

- Tasks: `10`

| Condition | Correct | Records | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| `exchange_then_decide` | `1` | `10` | `0.100` | `0` |
| `fact_only_constraint_decide` | `1` | `10` | `0.100` | `0` |
| `fact_only_exchange` | `2` | `10` | `0.200` | `0` |
| `full_info` | `4` | `10` | `0.400` | `0` |
| `oracle_public_facts` | `1` | `10` | `0.100` | `0` |
| `shared_only` | `1` | `10` | `0.100` | `0` |

## Primary Pairs

- `all:fact_only_exchange_vs_exchange_then_decide`: paired `65`, left-only `34`, right-only `1`, both-correct `23`, both-wrong `7`
- `all:fact_only_constraint_decide_vs_fact_only_exchange`: paired `65`, left-only `0`, right-only `1`, both-correct `56`, both-wrong `8`
- `full_info_correct:fact_only_exchange_vs_exchange_then_decide`: paired `59`, left-only `34`, right-only `1`, both-correct `23`, both-wrong `1`
- `full_info_correct:fact_only_constraint_decide_vs_fact_only_exchange`: paired `59`, left-only `0`, right-only `1`, both-correct `56`, both-wrong `2`
- `full_info_and_oracle_public_facts_correct:fact_only_exchange_vs_exchange_then_decide`: paired `55`, left-only `32`, right-only `0`, both-correct `23`, both-wrong `0`
- `full_info_and_oracle_public_facts_correct:fact_only_constraint_decide_vs_fact_only_exchange`: paired `55`, left-only `0`, right-only `0`, both-correct `55`, both-wrong `0`
- `clean_info_unstable:fact_only_exchange_vs_exchange_then_decide`: paired `10`, left-only `2`, right-only `1`, both-correct `0`, both-wrong `7`
- `clean_info_unstable:fact_only_constraint_decide_vs_fact_only_exchange`: paired `10`, left-only `0`, right-only `1`, both-correct `1`, both-wrong `8`
