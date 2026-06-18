# HiddenBench Corrected Summary

- Records: `96`
- Rescoring changes: `0`

| Condition | Records | Correct | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| blind_exchange | 12 | 7 | 0.583 | 0 |
| blind_minimal_exchange | 12 | 9 | 0.750 | 0 |
| exchange_then_decide | 12 | 2 | 0.167 | 0 |
| fact_only_exchange | 12 | 9 | 0.750 | 0 |
| fact_only_with_options_exchange | 12 | 8 | 0.667 | 0 |
| full_info | 12 | 9 | 0.750 | 0 |
| oracle_public_facts | 12 | 8 | 0.667 | 0 |
| shared_only | 12 | 1 | 0.083 | 0 |

## Paired Contrasts

- `full_info_vs_shared_only`: paired `12`, left-only `9`, right-only `1`, both-correct `0`, both-wrong `2`
- `oracle_public_facts_vs_shared_only`: paired `12`, left-only `8`, right-only `1`, both-correct `0`, both-wrong `3`
- `oracle_public_facts_vs_exchange_then_decide`: paired `12`, left-only `6`, right-only `0`, both-correct `2`, both-wrong `4`
- `oracle_public_facts_vs_fact_only_exchange`: paired `12`, left-only `0`, right-only `1`, both-correct `8`, both-wrong `3`
- `fact_only_exchange_vs_fact_only_with_options_exchange`: paired `12`, left-only `1`, right-only `0`, both-correct `8`, both-wrong `3`
- `blind_exchange_vs_exchange_then_decide`: paired `12`, left-only `6`, right-only `1`, both-correct `1`, both-wrong `4`
- `blind_minimal_exchange_vs_exchange_then_decide`: paired `12`, left-only `7`, right-only `0`, both-correct `2`, both-wrong `3`
- `fact_only_exchange_vs_blind_exchange`: paired `12`, left-only `2`, right-only `0`, both-correct `7`, both-wrong `3`
- `fact_only_exchange_vs_blind_minimal_exchange`: paired `12`, left-only `1`, right-only `1`, both-correct `8`, both-wrong `2`
- `blind_minimal_exchange_vs_blind_exchange`: paired `12`, left-only `2`, right-only `0`, both-correct `7`, both-wrong `3`
- `fact_only_exchange_vs_exchange_then_decide`: paired `12`, left-only `7`, right-only `0`, both-correct `2`, both-wrong `3`

## Public Message Audit

| Condition | Messages | Private exact | Rec leakage | Shared overtalk | Answer mentions | Avg private overlap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| blind_exchange | 45 | 0 | 0 | 4 | 29 | 0.782 |
| blind_minimal_exchange | 45 | 38 | 0 | 4 | 28 | 0.985 |
| exchange_then_decide | 45 | 6 | 41 | 25 | 45 | 0.714 |
| fact_only_exchange | 45 | 28 | 0 | 4 | 27 | 0.896 |
| fact_only_with_options_exchange | 45 | 28 | 0 | 4 | 28 | 0.876 |
