# HiddenBench Communication Necessity Probe

- Tasks: `12`
- Records: `72`

| Condition | Records | Correct | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| exchange_then_decide | 12 | 2 | 0.167 | 0 |
| fact_only_constraint_decide | 12 | 9 | 0.750 | 0 |
| fact_only_exchange | 12 | 9 | 0.750 | 0 |
| full_info | 12 | 9 | 0.750 | 0 |
| oracle_public_facts | 12 | 8 | 0.667 | 0 |
| shared_only | 12 | 1 | 0.083 | 0 |

## Readout Contract

- `shared_only` estimates the no-private-information floor.
- `single_private_agent` estimates individual partial-information behavior.
- `oracle_public_facts` gives the final model all private facts as clean public messages.
- `full_info` gives the final model all facts directly.
- `exchange_then_decide` first asks partial agents to emit public messages, then asks a final model to decide from those messages.
- `fact_only_exchange` uses the same final decision prompt as exchange, but agents may only report their private fact.
- `fact_only_constraint_decide` reuses the fact-only messages and changes only the final integration prompt.

A communication-necessity signal requires a clear gap from partial-information conditions to full/public-fact conditions. An exchange protocol is useful only if it closes part of that gap without simply revealing hidden gold labels.

## Paired Contrasts

- `full_info_vs_shared_only`: paired `12`, left-only `9`, right-only `1`, both-correct `0`, both-wrong `2`
- `oracle_public_facts_vs_shared_only`: paired `12`, left-only `8`, right-only `1`, both-correct `0`, both-wrong `3`
- `oracle_public_facts_vs_exchange_then_decide`: paired `12`, left-only `6`, right-only `0`, both-correct `2`, both-wrong `4`
- `oracle_public_facts_vs_fact_only_exchange`: paired `12`, left-only `0`, right-only `1`, both-correct `8`, both-wrong `3`
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
