# HiddenBench Corrected Summary

- Records: `650`
- Rescoring changes: `0`

| Condition | Records | Correct | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| blind_minimal_exchange | 65 | 51 | 0.785 | 0 |
| exchange_then_decide | 65 | 18 | 0.277 | 0 |
| fact_only_exchange | 65 | 51 | 0.785 | 0 |
| full_info | 65 | 55 | 0.846 | 0 |
| full_visibility_minimal_exchange | 65 | 50 | 0.769 | 0 |
| oracle_public_facts | 65 | 51 | 0.785 | 0 |
| private_plus_options_minimal_exchange | 65 | 52 | 0.800 | 0 |
| private_plus_shared_minimal_exchange | 65 | 51 | 0.785 | 0 |
| private_plus_task_minimal_exchange | 65 | 50 | 0.769 | 0 |
| shared_only | 65 | 2 | 0.031 | 0 |

## Paired Contrasts

- `full_info_vs_shared_only`: paired `65`, left-only `53`, right-only `0`, both-correct `2`, both-wrong `10`
- `oracle_public_facts_vs_shared_only`: paired `65`, left-only `49`, right-only `0`, both-correct `2`, both-wrong `14`
- `oracle_public_facts_vs_exchange_then_decide`: paired `65`, left-only `35`, right-only `2`, both-correct `16`, both-wrong `12`
- `oracle_public_facts_vs_fact_only_exchange`: paired `65`, left-only `3`, right-only `3`, both-correct `48`, both-wrong `11`
- `blind_minimal_exchange_vs_exchange_then_decide`: paired `65`, left-only `35`, right-only `2`, both-correct `16`, both-wrong `12`
- `blind_minimal_exchange_vs_private_plus_task_minimal_exchange`: paired `65`, left-only `1`, right-only `0`, both-correct `50`, both-wrong `14`
- `blind_minimal_exchange_vs_private_plus_options_minimal_exchange`: paired `65`, left-only `0`, right-only `1`, both-correct `51`, both-wrong `13`
- `blind_minimal_exchange_vs_private_plus_shared_minimal_exchange`: paired `65`, left-only `1`, right-only `1`, both-correct `50`, both-wrong `13`
- `blind_minimal_exchange_vs_full_visibility_minimal_exchange`: paired `65`, left-only `2`, right-only `1`, both-correct `49`, both-wrong `13`
- `fact_only_exchange_vs_blind_minimal_exchange`: paired `65`, left-only `4`, right-only `4`, both-correct `47`, both-wrong `10`
- `fact_only_exchange_vs_full_visibility_minimal_exchange`: paired `65`, left-only `4`, right-only `3`, both-correct `47`, both-wrong `11`
- `full_visibility_minimal_exchange_vs_exchange_then_decide`: paired `65`, left-only `34`, right-only `2`, both-correct `16`, both-wrong `13`
- `fact_only_exchange_vs_exchange_then_decide`: paired `65`, left-only `34`, right-only `1`, both-correct `17`, both-wrong `13`

## Public Message Audit

| Condition | Messages | Private exact | Rec leakage | Shared overtalk | Answer mentions | Avg private overlap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| blind_minimal_exchange | 253 | 227 | 0 | 4 | 158 | 0.977 |
| exchange_then_decide | 253 | 8 | 104 | 150 | 244 | 0.592 |
| fact_only_exchange | 253 | 181 | 0 | 4 | 161 | 0.917 |
| full_visibility_minimal_exchange | 253 | 203 | 0 | 5 | 160 | 0.954 |
| private_plus_options_minimal_exchange | 253 | 238 | 0 | 4 | 159 | 0.990 |
| private_plus_shared_minimal_exchange | 253 | 224 | 0 | 4 | 159 | 0.984 |
| private_plus_task_minimal_exchange | 253 | 225 | 0 | 4 | 157 | 0.985 |
