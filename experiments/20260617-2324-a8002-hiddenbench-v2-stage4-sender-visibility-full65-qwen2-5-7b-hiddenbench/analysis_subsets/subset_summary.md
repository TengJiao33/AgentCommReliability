# HiddenBench Subset Summary

- Records: `experiments/20260617-2324-a8002-hiddenbench-v2-stage4-sender-visibility-full65-qwen2-5-7b-hiddenbench/analysis_corrected/corrected_records.jsonl`

## all

- Tasks: `65`

| Condition | Correct | Records | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| `blind_minimal_exchange` | `51` | `65` | `0.785` | `0` |
| `exchange_then_decide` | `18` | `65` | `0.277` | `0` |
| `fact_only_exchange` | `51` | `65` | `0.785` | `0` |
| `full_info` | `55` | `65` | `0.846` | `0` |
| `full_visibility_minimal_exchange` | `50` | `65` | `0.769` | `0` |
| `oracle_public_facts` | `51` | `65` | `0.785` | `0` |
| `private_plus_options_minimal_exchange` | `52` | `65` | `0.800` | `0` |
| `private_plus_shared_minimal_exchange` | `51` | `65` | `0.785` | `0` |
| `private_plus_task_minimal_exchange` | `50` | `65` | `0.769` | `0` |
| `shared_only` | `2` | `65` | `0.031` | `0` |

## full_info_correct

- Tasks: `55`

| Condition | Correct | Records | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| `blind_minimal_exchange` | `48` | `55` | `0.873` | `0` |
| `exchange_then_decide` | `17` | `55` | `0.309` | `0` |
| `fact_only_exchange` | `49` | `55` | `0.891` | `0` |
| `full_info` | `55` | `55` | `1.000` | `0` |
| `full_visibility_minimal_exchange` | `48` | `55` | `0.873` | `0` |
| `oracle_public_facts` | `50` | `55` | `0.909` | `0` |
| `private_plus_options_minimal_exchange` | `49` | `55` | `0.891` | `0` |
| `private_plus_shared_minimal_exchange` | `49` | `55` | `0.891` | `0` |
| `private_plus_task_minimal_exchange` | `48` | `55` | `0.873` | `0` |
| `shared_only` | `2` | `55` | `0.036` | `0` |

## full_info_and_oracle_public_facts_correct

- Tasks: `50`

| Condition | Correct | Records | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| `blind_minimal_exchange` | `47` | `50` | `0.940` | `0` |
| `exchange_then_decide` | `16` | `50` | `0.320` | `0` |
| `fact_only_exchange` | `47` | `50` | `0.940` | `0` |
| `full_info` | `50` | `50` | `1.000` | `0` |
| `full_visibility_minimal_exchange` | `46` | `50` | `0.920` | `0` |
| `oracle_public_facts` | `50` | `50` | `1.000` | `0` |
| `private_plus_options_minimal_exchange` | `47` | `50` | `0.940` | `0` |
| `private_plus_shared_minimal_exchange` | `47` | `50` | `0.940` | `0` |
| `private_plus_task_minimal_exchange` | `47` | `50` | `0.940` | `0` |
| `shared_only` | `2` | `50` | `0.040` | `0` |

## clean_info_unstable

- Tasks: `15`

| Condition | Correct | Records | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| `blind_minimal_exchange` | `4` | `15` | `0.267` | `0` |
| `exchange_then_decide` | `2` | `15` | `0.133` | `0` |
| `fact_only_exchange` | `4` | `15` | `0.267` | `0` |
| `full_info` | `5` | `15` | `0.333` | `0` |
| `full_visibility_minimal_exchange` | `4` | `15` | `0.267` | `0` |
| `oracle_public_facts` | `1` | `15` | `0.067` | `0` |
| `private_plus_options_minimal_exchange` | `5` | `15` | `0.333` | `0` |
| `private_plus_shared_minimal_exchange` | `4` | `15` | `0.267` | `0` |
| `private_plus_task_minimal_exchange` | `3` | `15` | `0.200` | `0` |
| `shared_only` | `0` | `15` | `0.000` | `0` |

## Primary Pairs

- `all:fact_only_exchange_vs_exchange_then_decide`: paired `65`, left-only `34`, right-only `1`, both-correct `17`, both-wrong `13`
- `all:blind_minimal_exchange_vs_exchange_then_decide`: paired `65`, left-only `35`, right-only `2`, both-correct `16`, both-wrong `12`
- `all:blind_minimal_exchange_vs_private_plus_task_minimal_exchange`: paired `65`, left-only `1`, right-only `0`, both-correct `50`, both-wrong `14`
- `all:blind_minimal_exchange_vs_private_plus_options_minimal_exchange`: paired `65`, left-only `0`, right-only `1`, both-correct `51`, both-wrong `13`
- `all:blind_minimal_exchange_vs_private_plus_shared_minimal_exchange`: paired `65`, left-only `1`, right-only `1`, both-correct `50`, both-wrong `13`
- `all:blind_minimal_exchange_vs_full_visibility_minimal_exchange`: paired `65`, left-only `2`, right-only `1`, both-correct `49`, both-wrong `13`
- `all:fact_only_exchange_vs_blind_minimal_exchange`: paired `65`, left-only `4`, right-only `4`, both-correct `47`, both-wrong `10`
- `all:fact_only_exchange_vs_full_visibility_minimal_exchange`: paired `65`, left-only `4`, right-only `3`, both-correct `47`, both-wrong `11`
- `all:full_visibility_minimal_exchange_vs_exchange_then_decide`: paired `65`, left-only `34`, right-only `2`, both-correct `16`, both-wrong `13`
- `full_info_correct:fact_only_exchange_vs_exchange_then_decide`: paired `55`, left-only `32`, right-only `0`, both-correct `17`, both-wrong `6`
- `full_info_correct:blind_minimal_exchange_vs_exchange_then_decide`: paired `55`, left-only `33`, right-only `2`, both-correct `15`, both-wrong `5`
- `full_info_correct:blind_minimal_exchange_vs_private_plus_task_minimal_exchange`: paired `55`, left-only `0`, right-only `0`, both-correct `48`, both-wrong `7`
- `full_info_correct:blind_minimal_exchange_vs_private_plus_options_minimal_exchange`: paired `55`, left-only `0`, right-only `1`, both-correct `48`, both-wrong `6`
- `full_info_correct:blind_minimal_exchange_vs_private_plus_shared_minimal_exchange`: paired `55`, left-only `0`, right-only `1`, both-correct `48`, both-wrong `6`
- `full_info_correct:blind_minimal_exchange_vs_full_visibility_minimal_exchange`: paired `55`, left-only `1`, right-only `1`, both-correct `47`, both-wrong `6`
- `full_info_correct:fact_only_exchange_vs_blind_minimal_exchange`: paired `55`, left-only `3`, right-only `2`, both-correct `46`, both-wrong `4`
- `full_info_correct:fact_only_exchange_vs_full_visibility_minimal_exchange`: paired `55`, left-only `3`, right-only `2`, both-correct `46`, both-wrong `4`
- `full_info_correct:full_visibility_minimal_exchange_vs_exchange_then_decide`: paired `55`, left-only `33`, right-only `2`, both-correct `15`, both-wrong `5`
- `full_info_and_oracle_public_facts_correct:fact_only_exchange_vs_exchange_then_decide`: paired `50`, left-only `31`, right-only `0`, both-correct `16`, both-wrong `3`
- `full_info_and_oracle_public_facts_correct:blind_minimal_exchange_vs_exchange_then_decide`: paired `50`, left-only `32`, right-only `1`, both-correct `15`, both-wrong `2`
- `full_info_and_oracle_public_facts_correct:blind_minimal_exchange_vs_private_plus_task_minimal_exchange`: paired `50`, left-only `0`, right-only `0`, both-correct `47`, both-wrong `3`
- `full_info_and_oracle_public_facts_correct:blind_minimal_exchange_vs_private_plus_options_minimal_exchange`: paired `50`, left-only `0`, right-only `0`, both-correct `47`, both-wrong `3`
- `full_info_and_oracle_public_facts_correct:blind_minimal_exchange_vs_private_plus_shared_minimal_exchange`: paired `50`, left-only `0`, right-only `0`, both-correct `47`, both-wrong `3`
- `full_info_and_oracle_public_facts_correct:blind_minimal_exchange_vs_full_visibility_minimal_exchange`: paired `50`, left-only `1`, right-only `0`, both-correct `46`, both-wrong `3`
- `full_info_and_oracle_public_facts_correct:fact_only_exchange_vs_blind_minimal_exchange`: paired `50`, left-only `2`, right-only `2`, both-correct `45`, both-wrong `1`
- `full_info_and_oracle_public_facts_correct:fact_only_exchange_vs_full_visibility_minimal_exchange`: paired `50`, left-only `2`, right-only `1`, both-correct `45`, both-wrong `2`
- `full_info_and_oracle_public_facts_correct:full_visibility_minimal_exchange_vs_exchange_then_decide`: paired `50`, left-only `31`, right-only `1`, both-correct `15`, both-wrong `3`
- `clean_info_unstable:fact_only_exchange_vs_exchange_then_decide`: paired `15`, left-only `3`, right-only `1`, both-correct `1`, both-wrong `10`
- `clean_info_unstable:blind_minimal_exchange_vs_exchange_then_decide`: paired `15`, left-only `3`, right-only `1`, both-correct `1`, both-wrong `10`
- `clean_info_unstable:blind_minimal_exchange_vs_private_plus_task_minimal_exchange`: paired `15`, left-only `1`, right-only `0`, both-correct `3`, both-wrong `11`
- `clean_info_unstable:blind_minimal_exchange_vs_private_plus_options_minimal_exchange`: paired `15`, left-only `0`, right-only `1`, both-correct `4`, both-wrong `10`
- `clean_info_unstable:blind_minimal_exchange_vs_private_plus_shared_minimal_exchange`: paired `15`, left-only `1`, right-only `1`, both-correct `3`, both-wrong `10`
- `clean_info_unstable:blind_minimal_exchange_vs_full_visibility_minimal_exchange`: paired `15`, left-only `1`, right-only `1`, both-correct `3`, both-wrong `10`
- `clean_info_unstable:fact_only_exchange_vs_blind_minimal_exchange`: paired `15`, left-only `2`, right-only `2`, both-correct `2`, both-wrong `9`
- `clean_info_unstable:fact_only_exchange_vs_full_visibility_minimal_exchange`: paired `15`, left-only `2`, right-only `2`, both-correct `2`, both-wrong `9`
- `clean_info_unstable:full_visibility_minimal_exchange_vs_exchange_then_decide`: paired `15`, left-only `3`, right-only `1`, both-correct `1`, both-wrong `10`
