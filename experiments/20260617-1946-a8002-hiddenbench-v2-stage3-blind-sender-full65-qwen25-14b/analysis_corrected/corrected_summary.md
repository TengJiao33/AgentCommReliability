# HiddenBench Corrected Summary

- Records: `520`
- Rescoring changes: `0`

| Condition | Records | Correct | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| blind_exchange | 65 | 54 | 0.831 | 1 |
| blind_minimal_exchange | 65 | 57 | 0.877 | 0 |
| exchange_then_decide | 65 | 24 | 0.369 | 0 |
| fact_only_exchange | 65 | 57 | 0.877 | 0 |
| fact_only_with_options_exchange | 65 | 56 | 0.862 | 0 |
| full_info | 65 | 59 | 0.908 | 0 |
| oracle_public_facts | 65 | 56 | 0.862 | 0 |
| shared_only | 65 | 1 | 0.015 | 0 |

## Paired Contrasts

- `full_info_vs_shared_only`: paired `65`, left-only `59`, right-only `1`, both-correct `0`, both-wrong `5`
- `oracle_public_facts_vs_shared_only`: paired `65`, left-only `56`, right-only `1`, both-correct `0`, both-wrong `8`
- `oracle_public_facts_vs_exchange_then_decide`: paired `65`, left-only `33`, right-only `1`, both-correct `23`, both-wrong `8`
- `oracle_public_facts_vs_fact_only_exchange`: paired `65`, left-only `1`, right-only `2`, both-correct `55`, both-wrong `7`
- `fact_only_exchange_vs_fact_only_with_options_exchange`: paired `65`, left-only `2`, right-only `1`, both-correct `55`, both-wrong `7`
- `blind_exchange_vs_exchange_then_decide`: paired `65`, left-only `32`, right-only `2`, both-correct `22`, both-wrong `9`
- `blind_minimal_exchange_vs_exchange_then_decide`: paired `65`, left-only `34`, right-only `1`, both-correct `23`, both-wrong `7`
- `fact_only_exchange_vs_blind_exchange`: paired `65`, left-only `4`, right-only `1`, both-correct `53`, both-wrong `7`
- `fact_only_exchange_vs_blind_minimal_exchange`: paired `65`, left-only `2`, right-only `2`, both-correct `55`, both-wrong `6`
- `blind_minimal_exchange_vs_blind_exchange`: paired `65`, left-only `3`, right-only `0`, both-correct `54`, both-wrong `8`
- `fact_only_exchange_vs_exchange_then_decide`: paired `65`, left-only `34`, right-only `1`, both-correct `23`, both-wrong `7`

## Public Message Audit

| Condition | Messages | Private exact | Rec leakage | Shared overtalk | Answer mentions | Avg private overlap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| blind_exchange | 253 | 2 | 2 | 4 | 170 | 0.787 |
| blind_minimal_exchange | 253 | 238 | 0 | 4 | 158 | 0.991 |
| exchange_then_decide | 253 | 6 | 225 | 134 | 247 | 0.656 |
| fact_only_exchange | 253 | 198 | 0 | 4 | 162 | 0.951 |
| fact_only_with_options_exchange | 253 | 199 | 0 | 4 | 166 | 0.947 |
