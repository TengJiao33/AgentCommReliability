# HiddenBench Corrected Summary

- Records: `120`
- Rescoring changes: `0`

| Condition | Records | Correct | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| blind_minimal_exchange | 12 | 8 | 0.667 | 0 |
| exchange_then_decide | 12 | 3 | 0.250 | 0 |
| fact_only_exchange | 12 | 7 | 0.583 | 0 |
| full_info | 12 | 9 | 0.750 | 0 |
| full_visibility_minimal_exchange | 12 | 7 | 0.583 | 0 |
| oracle_public_facts | 12 | 8 | 0.667 | 0 |
| private_plus_options_minimal_exchange | 12 | 8 | 0.667 | 0 |
| private_plus_shared_minimal_exchange | 12 | 7 | 0.583 | 0 |
| private_plus_task_minimal_exchange | 12 | 7 | 0.583 | 0 |
| shared_only | 12 | 1 | 0.083 | 0 |

## Paired Contrasts

- `full_info_vs_shared_only`: paired `12`, left-only `8`, right-only `0`, both-correct `1`, both-wrong `3`
- `oracle_public_facts_vs_shared_only`: paired `12`, left-only `7`, right-only `0`, both-correct `1`, both-wrong `4`
- `oracle_public_facts_vs_exchange_then_decide`: paired `12`, left-only `5`, right-only `0`, both-correct `3`, both-wrong `4`
- `oracle_public_facts_vs_fact_only_exchange`: paired `12`, left-only `1`, right-only `0`, both-correct `7`, both-wrong `4`
- `blind_minimal_exchange_vs_exchange_then_decide`: paired `12`, left-only `5`, right-only `0`, both-correct `3`, both-wrong `4`
- `blind_minimal_exchange_vs_private_plus_task_minimal_exchange`: paired `12`, left-only `1`, right-only `0`, both-correct `7`, both-wrong `4`
- `blind_minimal_exchange_vs_private_plus_options_minimal_exchange`: paired `12`, left-only `0`, right-only `0`, both-correct `8`, both-wrong `4`
- `blind_minimal_exchange_vs_private_plus_shared_minimal_exchange`: paired `12`, left-only `1`, right-only `0`, both-correct `7`, both-wrong `4`
- `blind_minimal_exchange_vs_full_visibility_minimal_exchange`: paired `12`, left-only `1`, right-only `0`, both-correct `7`, both-wrong `4`
- `fact_only_exchange_vs_blind_minimal_exchange`: paired `12`, left-only `1`, right-only `2`, both-correct `6`, both-wrong `3`
- `fact_only_exchange_vs_full_visibility_minimal_exchange`: paired `12`, left-only `1`, right-only `1`, both-correct `6`, both-wrong `4`
- `full_visibility_minimal_exchange_vs_exchange_then_decide`: paired `12`, left-only `4`, right-only `0`, both-correct `3`, both-wrong `5`
- `fact_only_exchange_vs_exchange_then_decide`: paired `12`, left-only `4`, right-only `0`, both-correct `3`, both-wrong `5`

## Public Message Audit

| Condition | Messages | Private exact | Rec leakage | Shared overtalk | Answer mentions | Avg private overlap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| blind_minimal_exchange | 45 | 35 | 0 | 4 | 28 | 0.944 |
| exchange_then_decide | 45 | 5 | 19 | 21 | 45 | 0.621 |
| fact_only_exchange | 45 | 32 | 0 | 4 | 28 | 0.819 |
| full_visibility_minimal_exchange | 45 | 35 | 0 | 4 | 30 | 0.916 |
| private_plus_options_minimal_exchange | 45 | 36 | 0 | 4 | 28 | 0.956 |
| private_plus_shared_minimal_exchange | 45 | 36 | 0 | 4 | 28 | 0.982 |
| private_plus_task_minimal_exchange | 45 | 36 | 0 | 4 | 27 | 0.978 |
