# HiddenBench Corrected Summary

- Records: `108`
- Rescoring changes: `0`

| Condition | Records | Correct | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| exchange_then_decide | 12 | 2 | 0.167 | 0 |
| fact_only_constraint_decide | 12 | 9 | 0.750 | 0 |
| fact_only_exchange | 12 | 9 | 0.750 | 0 |
| fact_only_with_options_exchange | 12 | 8 | 0.667 | 0 |
| full_info | 12 | 9 | 0.750 | 0 |
| no_recommendation_exchange | 12 | 5 | 0.417 | 0 |
| no_shared_repeat_exchange | 12 | 5 | 0.417 | 0 |
| oracle_public_facts | 12 | 8 | 0.667 | 0 |
| shared_only | 12 | 1 | 0.083 | 0 |

## Paired Contrasts

- `full_info_vs_shared_only`: paired `12`, left-only `9`, right-only `1`, both-correct `0`, both-wrong `2`
- `oracle_public_facts_vs_shared_only`: paired `12`, left-only `8`, right-only `1`, both-correct `0`, both-wrong `3`
- `oracle_public_facts_vs_exchange_then_decide`: paired `12`, left-only `6`, right-only `0`, both-correct `2`, both-wrong `4`
- `no_recommendation_exchange_vs_exchange_then_decide`: paired `12`, left-only `3`, right-only `0`, both-correct `2`, both-wrong `7`
- `no_shared_repeat_exchange_vs_exchange_then_decide`: paired `12`, left-only `3`, right-only `0`, both-correct `2`, both-wrong `7`
- `fact_only_exchange_vs_no_recommendation_exchange`: paired `12`, left-only `5`, right-only `1`, both-correct `4`, both-wrong `2`
- `fact_only_exchange_vs_no_shared_repeat_exchange`: paired `12`, left-only `4`, right-only `0`, both-correct `5`, both-wrong `3`
- `oracle_public_facts_vs_fact_only_exchange`: paired `12`, left-only `0`, right-only `1`, both-correct `8`, both-wrong `3`
- `fact_only_exchange_vs_fact_only_with_options_exchange`: paired `12`, left-only `1`, right-only `0`, both-correct `8`, both-wrong `3`
- `fact_only_exchange_vs_exchange_then_decide`: paired `12`, left-only `7`, right-only `0`, both-correct `2`, both-wrong `3`
- `fact_only_constraint_decide_vs_fact_only_exchange`: paired `12`, left-only `0`, right-only `0`, both-correct `9`, both-wrong `3`
- `fact_only_constraint_decide_vs_exchange_then_decide`: paired `12`, left-only `7`, right-only `0`, both-correct `2`, both-wrong `3`
- `full_info_vs_fact_only_constraint_decide`: paired `12`, left-only `0`, right-only `0`, both-correct `9`, both-wrong `3`

## Public Message Audit

| Condition | Messages | Private exact | Rec leakage | Shared overtalk | Answer mentions | Avg private overlap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| exchange_then_decide | 45 | 6 | 41 | 25 | 45 | 0.714 |
| fact_only_constraint_decide | 45 | 28 | 0 | 4 | 27 | 0.896 |
| fact_only_exchange | 45 | 28 | 0 | 4 | 27 | 0.896 |
| fact_only_with_options_exchange | 45 | 28 | 0 | 4 | 28 | 0.876 |
| no_recommendation_exchange | 45 | 2 | 0 | 28 | 41 | 0.621 |
| no_shared_repeat_exchange | 45 | 3 | 31 | 5 | 44 | 0.740 |
