# HiddenBench Subset Summary

- Records: `experiments/20260617-1935-a8002-hiddenbench-v2-stage3-blind-sender-smoke12-qwen25-14b/analysis_corrected/corrected_records.jsonl`

## all

- Tasks: `12`

| Condition | Correct | Records | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| `blind_exchange` | `7` | `12` | `0.583` | `0` |
| `blind_minimal_exchange` | `9` | `12` | `0.750` | `0` |
| `exchange_then_decide` | `2` | `12` | `0.167` | `0` |
| `fact_only_exchange` | `9` | `12` | `0.750` | `0` |
| `fact_only_with_options_exchange` | `8` | `12` | `0.667` | `0` |
| `full_info` | `9` | `12` | `0.750` | `0` |
| `oracle_public_facts` | `8` | `12` | `0.667` | `0` |
| `shared_only` | `1` | `12` | `0.083` | `0` |

## full_info_correct

- Tasks: `9`

| Condition | Correct | Records | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| `blind_exchange` | `7` | `9` | `0.778` | `0` |
| `blind_minimal_exchange` | `8` | `9` | `0.889` | `0` |
| `exchange_then_decide` | `2` | `9` | `0.222` | `0` |
| `fact_only_exchange` | `9` | `9` | `1.000` | `0` |
| `fact_only_with_options_exchange` | `8` | `9` | `0.889` | `0` |
| `full_info` | `9` | `9` | `1.000` | `0` |
| `oracle_public_facts` | `8` | `9` | `0.889` | `0` |
| `shared_only` | `0` | `9` | `0.000` | `0` |

## full_info_and_oracle_public_facts_correct

- Tasks: `8`

| Condition | Correct | Records | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| `blind_exchange` | `7` | `8` | `0.875` | `0` |
| `blind_minimal_exchange` | `8` | `8` | `1.000` | `0` |
| `exchange_then_decide` | `2` | `8` | `0.250` | `0` |
| `fact_only_exchange` | `8` | `8` | `1.000` | `0` |
| `fact_only_with_options_exchange` | `7` | `8` | `0.875` | `0` |
| `full_info` | `8` | `8` | `1.000` | `0` |
| `oracle_public_facts` | `8` | `8` | `1.000` | `0` |
| `shared_only` | `0` | `8` | `0.000` | `0` |

## clean_info_unstable

- Tasks: `4`

| Condition | Correct | Records | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| `blind_exchange` | `0` | `4` | `0.000` | `0` |
| `blind_minimal_exchange` | `1` | `4` | `0.250` | `0` |
| `exchange_then_decide` | `0` | `4` | `0.000` | `0` |
| `fact_only_exchange` | `1` | `4` | `0.250` | `0` |
| `fact_only_with_options_exchange` | `1` | `4` | `0.250` | `0` |
| `full_info` | `1` | `4` | `0.250` | `0` |
| `oracle_public_facts` | `0` | `4` | `0.000` | `0` |
| `shared_only` | `1` | `4` | `0.250` | `0` |

## Primary Pairs

- `all:fact_only_exchange_vs_exchange_then_decide`: paired `12`, left-only `7`, right-only `0`, both-correct `2`, both-wrong `3`
- `all:fact_only_exchange_vs_fact_only_with_options_exchange`: paired `12`, left-only `1`, right-only `0`, both-correct `8`, both-wrong `3`
- `all:blind_exchange_vs_exchange_then_decide`: paired `12`, left-only `6`, right-only `1`, both-correct `1`, both-wrong `4`
- `all:blind_minimal_exchange_vs_exchange_then_decide`: paired `12`, left-only `7`, right-only `0`, both-correct `2`, both-wrong `3`
- `all:fact_only_exchange_vs_blind_exchange`: paired `12`, left-only `2`, right-only `0`, both-correct `7`, both-wrong `3`
- `all:fact_only_exchange_vs_blind_minimal_exchange`: paired `12`, left-only `1`, right-only `1`, both-correct `8`, both-wrong `2`
- `all:blind_minimal_exchange_vs_blind_exchange`: paired `12`, left-only `2`, right-only `0`, both-correct `7`, both-wrong `3`
- `full_info_correct:fact_only_exchange_vs_exchange_then_decide`: paired `9`, left-only `7`, right-only `0`, both-correct `2`, both-wrong `0`
- `full_info_correct:fact_only_exchange_vs_fact_only_with_options_exchange`: paired `9`, left-only `1`, right-only `0`, both-correct `8`, both-wrong `0`
- `full_info_correct:blind_exchange_vs_exchange_then_decide`: paired `9`, left-only `6`, right-only `1`, both-correct `1`, both-wrong `1`
- `full_info_correct:blind_minimal_exchange_vs_exchange_then_decide`: paired `9`, left-only `6`, right-only `0`, both-correct `2`, both-wrong `1`
- `full_info_correct:fact_only_exchange_vs_blind_exchange`: paired `9`, left-only `2`, right-only `0`, both-correct `7`, both-wrong `0`
- `full_info_correct:fact_only_exchange_vs_blind_minimal_exchange`: paired `9`, left-only `1`, right-only `0`, both-correct `8`, both-wrong `0`
- `full_info_correct:blind_minimal_exchange_vs_blind_exchange`: paired `9`, left-only `1`, right-only `0`, both-correct `7`, both-wrong `1`
- `full_info_and_oracle_public_facts_correct:fact_only_exchange_vs_exchange_then_decide`: paired `8`, left-only `6`, right-only `0`, both-correct `2`, both-wrong `0`
- `full_info_and_oracle_public_facts_correct:fact_only_exchange_vs_fact_only_with_options_exchange`: paired `8`, left-only `1`, right-only `0`, both-correct `7`, both-wrong `0`
- `full_info_and_oracle_public_facts_correct:blind_exchange_vs_exchange_then_decide`: paired `8`, left-only `6`, right-only `1`, both-correct `1`, both-wrong `0`
- `full_info_and_oracle_public_facts_correct:blind_minimal_exchange_vs_exchange_then_decide`: paired `8`, left-only `6`, right-only `0`, both-correct `2`, both-wrong `0`
- `full_info_and_oracle_public_facts_correct:fact_only_exchange_vs_blind_exchange`: paired `8`, left-only `1`, right-only `0`, both-correct `7`, both-wrong `0`
- `full_info_and_oracle_public_facts_correct:fact_only_exchange_vs_blind_minimal_exchange`: paired `8`, left-only `0`, right-only `0`, both-correct `8`, both-wrong `0`
- `full_info_and_oracle_public_facts_correct:blind_minimal_exchange_vs_blind_exchange`: paired `8`, left-only `1`, right-only `0`, both-correct `7`, both-wrong `0`
- `clean_info_unstable:fact_only_exchange_vs_exchange_then_decide`: paired `4`, left-only `1`, right-only `0`, both-correct `0`, both-wrong `3`
- `clean_info_unstable:fact_only_exchange_vs_fact_only_with_options_exchange`: paired `4`, left-only `0`, right-only `0`, both-correct `1`, both-wrong `3`
- `clean_info_unstable:blind_exchange_vs_exchange_then_decide`: paired `4`, left-only `0`, right-only `0`, both-correct `0`, both-wrong `4`
- `clean_info_unstable:blind_minimal_exchange_vs_exchange_then_decide`: paired `4`, left-only `1`, right-only `0`, both-correct `0`, both-wrong `3`
- `clean_info_unstable:fact_only_exchange_vs_blind_exchange`: paired `4`, left-only `1`, right-only `0`, both-correct `0`, both-wrong `3`
- `clean_info_unstable:fact_only_exchange_vs_blind_minimal_exchange`: paired `4`, left-only `1`, right-only `1`, both-correct `0`, both-wrong `2`
- `clean_info_unstable:blind_minimal_exchange_vs_blind_exchange`: paired `4`, left-only `1`, right-only `0`, both-correct `0`, both-wrong `3`
