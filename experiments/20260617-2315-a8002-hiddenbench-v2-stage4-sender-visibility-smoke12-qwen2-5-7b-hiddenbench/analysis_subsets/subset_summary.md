# HiddenBench Subset Summary

- Records: `experiments/20260617-2315-a8002-hiddenbench-v2-stage4-sender-visibility-smoke12-qwen2-5-7b-hiddenbench/analysis_corrected/corrected_records.jsonl`

## all

- Tasks: `12`

| Condition | Correct | Records | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| `blind_minimal_exchange` | `8` | `12` | `0.667` | `0` |
| `exchange_then_decide` | `3` | `12` | `0.250` | `0` |
| `fact_only_exchange` | `7` | `12` | `0.583` | `0` |
| `full_info` | `9` | `12` | `0.750` | `0` |
| `full_visibility_minimal_exchange` | `7` | `12` | `0.583` | `0` |
| `oracle_public_facts` | `8` | `12` | `0.667` | `0` |
| `private_plus_options_minimal_exchange` | `8` | `12` | `0.667` | `0` |
| `private_plus_shared_minimal_exchange` | `7` | `12` | `0.583` | `0` |
| `private_plus_task_minimal_exchange` | `7` | `12` | `0.583` | `0` |
| `shared_only` | `1` | `12` | `0.083` | `0` |

## full_info_correct

- Tasks: `9`

| Condition | Correct | Records | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| `blind_minimal_exchange` | `7` | `9` | `0.778` | `0` |
| `exchange_then_decide` | `3` | `9` | `0.333` | `0` |
| `fact_only_exchange` | `7` | `9` | `0.778` | `0` |
| `full_info` | `9` | `9` | `1.000` | `0` |
| `full_visibility_minimal_exchange` | `7` | `9` | `0.778` | `0` |
| `oracle_public_facts` | `8` | `9` | `0.889` | `0` |
| `private_plus_options_minimal_exchange` | `7` | `9` | `0.778` | `0` |
| `private_plus_shared_minimal_exchange` | `7` | `9` | `0.778` | `0` |
| `private_plus_task_minimal_exchange` | `7` | `9` | `0.778` | `0` |
| `shared_only` | `1` | `9` | `0.111` | `0` |

## full_info_and_oracle_public_facts_correct

- Tasks: `8`

| Condition | Correct | Records | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| `blind_minimal_exchange` | `7` | `8` | `0.875` | `0` |
| `exchange_then_decide` | `3` | `8` | `0.375` | `0` |
| `fact_only_exchange` | `7` | `8` | `0.875` | `0` |
| `full_info` | `8` | `8` | `1.000` | `0` |
| `full_visibility_minimal_exchange` | `7` | `8` | `0.875` | `0` |
| `oracle_public_facts` | `8` | `8` | `1.000` | `0` |
| `private_plus_options_minimal_exchange` | `7` | `8` | `0.875` | `0` |
| `private_plus_shared_minimal_exchange` | `7` | `8` | `0.875` | `0` |
| `private_plus_task_minimal_exchange` | `7` | `8` | `0.875` | `0` |
| `shared_only` | `1` | `8` | `0.125` | `0` |

## clean_info_unstable

- Tasks: `4`

| Condition | Correct | Records | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| `blind_minimal_exchange` | `1` | `4` | `0.250` | `0` |
| `exchange_then_decide` | `0` | `4` | `0.000` | `0` |
| `fact_only_exchange` | `0` | `4` | `0.000` | `0` |
| `full_info` | `1` | `4` | `0.250` | `0` |
| `full_visibility_minimal_exchange` | `0` | `4` | `0.000` | `0` |
| `oracle_public_facts` | `0` | `4` | `0.000` | `0` |
| `private_plus_options_minimal_exchange` | `1` | `4` | `0.250` | `0` |
| `private_plus_shared_minimal_exchange` | `0` | `4` | `0.000` | `0` |
| `private_plus_task_minimal_exchange` | `0` | `4` | `0.000` | `0` |
| `shared_only` | `0` | `4` | `0.000` | `0` |

## Primary Pairs

- `all:fact_only_exchange_vs_exchange_then_decide`: paired `12`, left-only `4`, right-only `0`, both-correct `3`, both-wrong `5`
- `all:blind_minimal_exchange_vs_exchange_then_decide`: paired `12`, left-only `5`, right-only `0`, both-correct `3`, both-wrong `4`
- `all:blind_minimal_exchange_vs_private_plus_task_minimal_exchange`: paired `12`, left-only `1`, right-only `0`, both-correct `7`, both-wrong `4`
- `all:blind_minimal_exchange_vs_private_plus_options_minimal_exchange`: paired `12`, left-only `0`, right-only `0`, both-correct `8`, both-wrong `4`
- `all:blind_minimal_exchange_vs_private_plus_shared_minimal_exchange`: paired `12`, left-only `1`, right-only `0`, both-correct `7`, both-wrong `4`
- `all:blind_minimal_exchange_vs_full_visibility_minimal_exchange`: paired `12`, left-only `1`, right-only `0`, both-correct `7`, both-wrong `4`
- `all:fact_only_exchange_vs_blind_minimal_exchange`: paired `12`, left-only `1`, right-only `2`, both-correct `6`, both-wrong `3`
- `all:fact_only_exchange_vs_full_visibility_minimal_exchange`: paired `12`, left-only `1`, right-only `1`, both-correct `6`, both-wrong `4`
- `all:full_visibility_minimal_exchange_vs_exchange_then_decide`: paired `12`, left-only `4`, right-only `0`, both-correct `3`, both-wrong `5`
- `full_info_correct:fact_only_exchange_vs_exchange_then_decide`: paired `9`, left-only `4`, right-only `0`, both-correct `3`, both-wrong `2`
- `full_info_correct:blind_minimal_exchange_vs_exchange_then_decide`: paired `9`, left-only `4`, right-only `0`, both-correct `3`, both-wrong `2`
- `full_info_correct:blind_minimal_exchange_vs_private_plus_task_minimal_exchange`: paired `9`, left-only `0`, right-only `0`, both-correct `7`, both-wrong `2`
- `full_info_correct:blind_minimal_exchange_vs_private_plus_options_minimal_exchange`: paired `9`, left-only `0`, right-only `0`, both-correct `7`, both-wrong `2`
- `full_info_correct:blind_minimal_exchange_vs_private_plus_shared_minimal_exchange`: paired `9`, left-only `0`, right-only `0`, both-correct `7`, both-wrong `2`
- `full_info_correct:blind_minimal_exchange_vs_full_visibility_minimal_exchange`: paired `9`, left-only `0`, right-only `0`, both-correct `7`, both-wrong `2`
- `full_info_correct:fact_only_exchange_vs_blind_minimal_exchange`: paired `9`, left-only `1`, right-only `1`, both-correct `6`, both-wrong `1`
- `full_info_correct:fact_only_exchange_vs_full_visibility_minimal_exchange`: paired `9`, left-only `1`, right-only `1`, both-correct `6`, both-wrong `1`
- `full_info_correct:full_visibility_minimal_exchange_vs_exchange_then_decide`: paired `9`, left-only `4`, right-only `0`, both-correct `3`, both-wrong `2`
- `full_info_and_oracle_public_facts_correct:fact_only_exchange_vs_exchange_then_decide`: paired `8`, left-only `4`, right-only `0`, both-correct `3`, both-wrong `1`
- `full_info_and_oracle_public_facts_correct:blind_minimal_exchange_vs_exchange_then_decide`: paired `8`, left-only `4`, right-only `0`, both-correct `3`, both-wrong `1`
- `full_info_and_oracle_public_facts_correct:blind_minimal_exchange_vs_private_plus_task_minimal_exchange`: paired `8`, left-only `0`, right-only `0`, both-correct `7`, both-wrong `1`
- `full_info_and_oracle_public_facts_correct:blind_minimal_exchange_vs_private_plus_options_minimal_exchange`: paired `8`, left-only `0`, right-only `0`, both-correct `7`, both-wrong `1`
- `full_info_and_oracle_public_facts_correct:blind_minimal_exchange_vs_private_plus_shared_minimal_exchange`: paired `8`, left-only `0`, right-only `0`, both-correct `7`, both-wrong `1`
- `full_info_and_oracle_public_facts_correct:blind_minimal_exchange_vs_full_visibility_minimal_exchange`: paired `8`, left-only `0`, right-only `0`, both-correct `7`, both-wrong `1`
- `full_info_and_oracle_public_facts_correct:fact_only_exchange_vs_blind_minimal_exchange`: paired `8`, left-only `1`, right-only `1`, both-correct `6`, both-wrong `0`
- `full_info_and_oracle_public_facts_correct:fact_only_exchange_vs_full_visibility_minimal_exchange`: paired `8`, left-only `1`, right-only `1`, both-correct `6`, both-wrong `0`
- `full_info_and_oracle_public_facts_correct:full_visibility_minimal_exchange_vs_exchange_then_decide`: paired `8`, left-only `4`, right-only `0`, both-correct `3`, both-wrong `1`
- `clean_info_unstable:fact_only_exchange_vs_exchange_then_decide`: paired `4`, left-only `0`, right-only `0`, both-correct `0`, both-wrong `4`
- `clean_info_unstable:blind_minimal_exchange_vs_exchange_then_decide`: paired `4`, left-only `1`, right-only `0`, both-correct `0`, both-wrong `3`
- `clean_info_unstable:blind_minimal_exchange_vs_private_plus_task_minimal_exchange`: paired `4`, left-only `1`, right-only `0`, both-correct `0`, both-wrong `3`
- `clean_info_unstable:blind_minimal_exchange_vs_private_plus_options_minimal_exchange`: paired `4`, left-only `0`, right-only `0`, both-correct `1`, both-wrong `3`
- `clean_info_unstable:blind_minimal_exchange_vs_private_plus_shared_minimal_exchange`: paired `4`, left-only `1`, right-only `0`, both-correct `0`, both-wrong `3`
- `clean_info_unstable:blind_minimal_exchange_vs_full_visibility_minimal_exchange`: paired `4`, left-only `1`, right-only `0`, both-correct `0`, both-wrong `3`
- `clean_info_unstable:fact_only_exchange_vs_blind_minimal_exchange`: paired `4`, left-only `0`, right-only `1`, both-correct `0`, both-wrong `3`
- `clean_info_unstable:fact_only_exchange_vs_full_visibility_minimal_exchange`: paired `4`, left-only `0`, right-only `0`, both-correct `0`, both-wrong `4`
- `clean_info_unstable:full_visibility_minimal_exchange_vs_exchange_then_decide`: paired `4`, left-only `0`, right-only `0`, both-correct `0`, both-wrong `4`
