# HiddenBench Corrected Summary

- Records: `585`
- Rescoring changes: `0`

| Condition | Records | Correct | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| exchange_then_decide | 65 | 24 | 0.369 | 0 |
| fact_only_constraint_decide | 65 | 56 | 0.862 | 0 |
| fact_only_exchange | 65 | 57 | 0.877 | 0 |
| fact_only_with_options_exchange | 65 | 56 | 0.862 | 0 |
| full_info | 65 | 59 | 0.908 | 0 |
| no_recommendation_exchange | 65 | 30 | 0.462 | 0 |
| no_shared_repeat_exchange | 65 | 33 | 0.508 | 0 |
| oracle_public_facts | 65 | 56 | 0.862 | 0 |
| shared_only | 65 | 1 | 0.015 | 0 |

## Paired Contrasts

- `full_info_vs_shared_only`: paired `65`, left-only `59`, right-only `1`, both-correct `0`, both-wrong `5`
- `oracle_public_facts_vs_shared_only`: paired `65`, left-only `56`, right-only `1`, both-correct `0`, both-wrong `8`
- `oracle_public_facts_vs_exchange_then_decide`: paired `65`, left-only `33`, right-only `1`, both-correct `23`, both-wrong `8`
- `no_recommendation_exchange_vs_exchange_then_decide`: paired `65`, left-only `12`, right-only `6`, both-correct `18`, both-wrong `29`
- `no_shared_repeat_exchange_vs_exchange_then_decide`: paired `65`, left-only `11`, right-only `2`, both-correct `22`, both-wrong `30`
- `fact_only_exchange_vs_no_recommendation_exchange`: paired `65`, left-only `29`, right-only `2`, both-correct `28`, both-wrong `6`
- `fact_only_exchange_vs_no_shared_repeat_exchange`: paired `65`, left-only `25`, right-only `1`, both-correct `32`, both-wrong `7`
- `oracle_public_facts_vs_fact_only_exchange`: paired `65`, left-only `1`, right-only `2`, both-correct `55`, both-wrong `7`
- `fact_only_exchange_vs_fact_only_with_options_exchange`: paired `65`, left-only `2`, right-only `1`, both-correct `55`, both-wrong `7`
- `fact_only_exchange_vs_exchange_then_decide`: paired `65`, left-only `34`, right-only `1`, both-correct `23`, both-wrong `7`
- `fact_only_constraint_decide_vs_fact_only_exchange`: paired `65`, left-only `0`, right-only `1`, both-correct `56`, both-wrong `8`
- `fact_only_constraint_decide_vs_exchange_then_decide`: paired `65`, left-only `33`, right-only `1`, both-correct `23`, both-wrong `8`
- `full_info_vs_fact_only_constraint_decide`: paired `65`, left-only `3`, right-only `0`, both-correct `56`, both-wrong `6`

## Public Message Audit

| Condition | Messages | Private exact | Rec leakage | Shared overtalk | Answer mentions | Avg private overlap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| exchange_then_decide | 253 | 6 | 225 | 134 | 247 | 0.656 |
| fact_only_constraint_decide | 253 | 198 | 0 | 4 | 162 | 0.951 |
| fact_only_exchange | 253 | 198 | 0 | 4 | 162 | 0.951 |
| fact_only_with_options_exchange | 253 | 199 | 0 | 4 | 166 | 0.947 |
| no_recommendation_exchange | 253 | 2 | 12 | 176 | 237 | 0.628 |
| no_shared_repeat_exchange | 253 | 6 | 191 | 28 | 238 | 0.715 |
