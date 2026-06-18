# HiddenBench Subset Summary

- Records: `/data/xuhaoming/yfy/research_workspace/experiments/20260617-1752-a8002-hiddenbench-v2-stage2-sender-ablation-smoke12-qwen25-14b/analysis_corrected/corrected_records.jsonl`

## all

- Tasks: `12`

| Condition | Correct | Records | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| `exchange_then_decide` | `2` | `12` | `0.167` | `0` |
| `fact_only_constraint_decide` | `9` | `12` | `0.750` | `0` |
| `fact_only_exchange` | `9` | `12` | `0.750` | `0` |
| `fact_only_with_options_exchange` | `8` | `12` | `0.667` | `0` |
| `full_info` | `9` | `12` | `0.750` | `0` |
| `no_recommendation_exchange` | `5` | `12` | `0.417` | `0` |
| `no_shared_repeat_exchange` | `5` | `12` | `0.417` | `0` |
| `oracle_public_facts` | `8` | `12` | `0.667` | `0` |
| `shared_only` | `1` | `12` | `0.083` | `0` |

## full_info_correct

- Tasks: `9`

| Condition | Correct | Records | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| `exchange_then_decide` | `2` | `9` | `0.222` | `0` |
| `fact_only_constraint_decide` | `9` | `9` | `1.000` | `0` |
| `fact_only_exchange` | `9` | `9` | `1.000` | `0` |
| `fact_only_with_options_exchange` | `8` | `9` | `0.889` | `0` |
| `full_info` | `9` | `9` | `1.000` | `0` |
| `no_recommendation_exchange` | `4` | `9` | `0.444` | `0` |
| `no_shared_repeat_exchange` | `5` | `9` | `0.556` | `0` |
| `oracle_public_facts` | `8` | `9` | `0.889` | `0` |
| `shared_only` | `0` | `9` | `0.000` | `0` |

## full_info_and_oracle_public_facts_correct

- Tasks: `8`

| Condition | Correct | Records | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| `exchange_then_decide` | `2` | `8` | `0.250` | `0` |
| `fact_only_constraint_decide` | `8` | `8` | `1.000` | `0` |
| `fact_only_exchange` | `8` | `8` | `1.000` | `0` |
| `fact_only_with_options_exchange` | `7` | `8` | `0.875` | `0` |
| `full_info` | `8` | `8` | `1.000` | `0` |
| `no_recommendation_exchange` | `4` | `8` | `0.500` | `0` |
| `no_shared_repeat_exchange` | `4` | `8` | `0.500` | `0` |
| `oracle_public_facts` | `8` | `8` | `1.000` | `0` |
| `shared_only` | `0` | `8` | `0.000` | `0` |

## clean_info_unstable

- Tasks: `4`

| Condition | Correct | Records | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| `exchange_then_decide` | `0` | `4` | `0.000` | `0` |
| `fact_only_constraint_decide` | `1` | `4` | `0.250` | `0` |
| `fact_only_exchange` | `1` | `4` | `0.250` | `0` |
| `fact_only_with_options_exchange` | `1` | `4` | `0.250` | `0` |
| `full_info` | `1` | `4` | `0.250` | `0` |
| `no_recommendation_exchange` | `1` | `4` | `0.250` | `0` |
| `no_shared_repeat_exchange` | `1` | `4` | `0.250` | `0` |
| `oracle_public_facts` | `0` | `4` | `0.000` | `0` |
| `shared_only` | `1` | `4` | `0.250` | `0` |

## Primary Pairs

- `all:fact_only_exchange_vs_exchange_then_decide`: paired `12`, left-only `7`, right-only `0`, both-correct `2`, both-wrong `3`
- `all:no_recommendation_exchange_vs_exchange_then_decide`: paired `12`, left-only `3`, right-only `0`, both-correct `2`, both-wrong `7`
- `all:no_shared_repeat_exchange_vs_exchange_then_decide`: paired `12`, left-only `3`, right-only `0`, both-correct `2`, both-wrong `7`
- `all:fact_only_exchange_vs_no_recommendation_exchange`: paired `12`, left-only `5`, right-only `1`, both-correct `4`, both-wrong `2`
- `all:fact_only_exchange_vs_no_shared_repeat_exchange`: paired `12`, left-only `4`, right-only `0`, both-correct `5`, both-wrong `3`
- `all:fact_only_exchange_vs_fact_only_with_options_exchange`: paired `12`, left-only `1`, right-only `0`, both-correct `8`, both-wrong `3`
- `all:fact_only_constraint_decide_vs_fact_only_exchange`: paired `12`, left-only `0`, right-only `0`, both-correct `9`, both-wrong `3`
- `full_info_correct:fact_only_exchange_vs_exchange_then_decide`: paired `9`, left-only `7`, right-only `0`, both-correct `2`, both-wrong `0`
- `full_info_correct:no_recommendation_exchange_vs_exchange_then_decide`: paired `9`, left-only `2`, right-only `0`, both-correct `2`, both-wrong `5`
- `full_info_correct:no_shared_repeat_exchange_vs_exchange_then_decide`: paired `9`, left-only `3`, right-only `0`, both-correct `2`, both-wrong `4`
- `full_info_correct:fact_only_exchange_vs_no_recommendation_exchange`: paired `9`, left-only `5`, right-only `0`, both-correct `4`, both-wrong `0`
- `full_info_correct:fact_only_exchange_vs_no_shared_repeat_exchange`: paired `9`, left-only `4`, right-only `0`, both-correct `5`, both-wrong `0`
- `full_info_correct:fact_only_exchange_vs_fact_only_with_options_exchange`: paired `9`, left-only `1`, right-only `0`, both-correct `8`, both-wrong `0`
- `full_info_correct:fact_only_constraint_decide_vs_fact_only_exchange`: paired `9`, left-only `0`, right-only `0`, both-correct `9`, both-wrong `0`
- `full_info_and_oracle_public_facts_correct:fact_only_exchange_vs_exchange_then_decide`: paired `8`, left-only `6`, right-only `0`, both-correct `2`, both-wrong `0`
- `full_info_and_oracle_public_facts_correct:no_recommendation_exchange_vs_exchange_then_decide`: paired `8`, left-only `2`, right-only `0`, both-correct `2`, both-wrong `4`
- `full_info_and_oracle_public_facts_correct:no_shared_repeat_exchange_vs_exchange_then_decide`: paired `8`, left-only `2`, right-only `0`, both-correct `2`, both-wrong `4`
- `full_info_and_oracle_public_facts_correct:fact_only_exchange_vs_no_recommendation_exchange`: paired `8`, left-only `4`, right-only `0`, both-correct `4`, both-wrong `0`
- `full_info_and_oracle_public_facts_correct:fact_only_exchange_vs_no_shared_repeat_exchange`: paired `8`, left-only `4`, right-only `0`, both-correct `4`, both-wrong `0`
- `full_info_and_oracle_public_facts_correct:fact_only_exchange_vs_fact_only_with_options_exchange`: paired `8`, left-only `1`, right-only `0`, both-correct `7`, both-wrong `0`
- `full_info_and_oracle_public_facts_correct:fact_only_constraint_decide_vs_fact_only_exchange`: paired `8`, left-only `0`, right-only `0`, both-correct `8`, both-wrong `0`
- `clean_info_unstable:fact_only_exchange_vs_exchange_then_decide`: paired `4`, left-only `1`, right-only `0`, both-correct `0`, both-wrong `3`
- `clean_info_unstable:no_recommendation_exchange_vs_exchange_then_decide`: paired `4`, left-only `1`, right-only `0`, both-correct `0`, both-wrong `3`
- `clean_info_unstable:no_shared_repeat_exchange_vs_exchange_then_decide`: paired `4`, left-only `1`, right-only `0`, both-correct `0`, both-wrong `3`
- `clean_info_unstable:fact_only_exchange_vs_no_recommendation_exchange`: paired `4`, left-only `1`, right-only `1`, both-correct `0`, both-wrong `2`
- `clean_info_unstable:fact_only_exchange_vs_no_shared_repeat_exchange`: paired `4`, left-only `0`, right-only `0`, both-correct `1`, both-wrong `3`
- `clean_info_unstable:fact_only_exchange_vs_fact_only_with_options_exchange`: paired `4`, left-only `0`, right-only `0`, both-correct `1`, both-wrong `3`
- `clean_info_unstable:fact_only_constraint_decide_vs_fact_only_exchange`: paired `4`, left-only `0`, right-only `0`, both-correct `1`, both-wrong `3`
