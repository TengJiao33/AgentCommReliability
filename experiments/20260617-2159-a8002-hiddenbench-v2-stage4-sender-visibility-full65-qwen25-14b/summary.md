# HiddenBench Communication Necessity Probe

- Tasks: `65`
- Records: `650`

| Condition | Records | Correct | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| blind_minimal_exchange | 65 | 57 | 0.877 | 0 |
| exchange_then_decide | 65 | 24 | 0.369 | 0 |
| fact_only_exchange | 65 | 57 | 0.877 | 0 |
| full_info | 65 | 59 | 0.908 | 0 |
| full_visibility_minimal_exchange | 65 | 55 | 0.846 | 0 |
| oracle_public_facts | 65 | 56 | 0.862 | 0 |
| private_plus_options_minimal_exchange | 65 | 55 | 0.846 | 0 |
| private_plus_shared_minimal_exchange | 65 | 55 | 0.846 | 0 |
| private_plus_task_minimal_exchange | 65 | 56 | 0.862 | 0 |
| shared_only | 65 | 1 | 0.015 | 0 |

## Readout Contract

- `shared_only` estimates the no-private-information floor.
- `single_private_agent` estimates individual partial-information behavior.
- `oracle_public_facts` gives the final model all private facts as clean public messages.
- `full_info` gives the final model all facts directly.
- `exchange_then_decide` first asks partial agents to emit public messages, then asks a final model to decide from those messages.
- `no_recommendation_exchange` keeps the old sender context but forbids answer recommendations and option ranking.
- `no_shared_repeat_exchange` keeps recommendations allowed but forbids repeating shared information.
- `fact_only_exchange` uses the same final decision prompt as exchange, but agents may only report their private fact.
- `fact_only_with_options_exchange` is fact-only while explicitly showing the possible answer list to senders.
- `blind_exchange` hides task description, shared facts, and answer options from senders; agents only report one local observation.
- `blind_minimal_exchange` uses the same blind sender visibility but asks for a minimal observation-note format.
- `private_plus_task_minimal_exchange` shows senders the task but keeps the minimal observation-note format.
- `private_plus_options_minimal_exchange` shows senders the answer options but keeps the minimal observation-note format.
- `private_plus_shared_minimal_exchange` shows senders shared facts but keeps the minimal observation-note format.
- `full_visibility_minimal_exchange` shows senders task, shared facts, and options while keeping the minimal observation-note format.
- `fact_only_constraint_decide` reuses the fact-only messages and changes only the final integration prompt.

A communication-necessity signal requires a clear gap from partial-information conditions to full/public-fact conditions. An exchange protocol is useful only if it closes part of that gap without simply revealing hidden gold labels.

## Paired Contrasts

- `full_info_vs_shared_only`: paired `65`, left-only `59`, right-only `1`, both-correct `0`, both-wrong `5`
- `oracle_public_facts_vs_shared_only`: paired `65`, left-only `56`, right-only `1`, both-correct `0`, both-wrong `8`
- `oracle_public_facts_vs_exchange_then_decide`: paired `65`, left-only `33`, right-only `1`, both-correct `23`, both-wrong `8`
- `oracle_public_facts_vs_fact_only_exchange`: paired `65`, left-only `1`, right-only `2`, both-correct `55`, both-wrong `7`
- `blind_minimal_exchange_vs_exchange_then_decide`: paired `65`, left-only `34`, right-only `1`, both-correct `23`, both-wrong `7`
- `blind_minimal_exchange_vs_private_plus_task_minimal_exchange`: paired `65`, left-only `1`, right-only `0`, both-correct `56`, both-wrong `8`
- `blind_minimal_exchange_vs_private_plus_options_minimal_exchange`: paired `65`, left-only `2`, right-only `0`, both-correct `55`, both-wrong `8`
- `blind_minimal_exchange_vs_private_plus_shared_minimal_exchange`: paired `65`, left-only `2`, right-only `0`, both-correct `55`, both-wrong `8`
- `blind_minimal_exchange_vs_full_visibility_minimal_exchange`: paired `65`, left-only `2`, right-only `0`, both-correct `55`, both-wrong `8`
- `fact_only_exchange_vs_blind_minimal_exchange`: paired `65`, left-only `2`, right-only `2`, both-correct `55`, both-wrong `6`
- `fact_only_exchange_vs_full_visibility_minimal_exchange`: paired `65`, left-only `3`, right-only `1`, both-correct `54`, both-wrong `7`
- `full_visibility_minimal_exchange_vs_exchange_then_decide`: paired `65`, left-only `32`, right-only `1`, both-correct `23`, both-wrong `9`
- `fact_only_exchange_vs_exchange_then_decide`: paired `65`, left-only `34`, right-only `1`, both-correct `23`, both-wrong `7`

## Public Message Audit

| Condition | Messages | Private exact | Rec leakage | Shared overtalk | Answer mentions | Avg private overlap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| blind_minimal_exchange | 253 | 238 | 0 | 4 | 158 | 0.991 |
| exchange_then_decide | 253 | 6 | 225 | 134 | 247 | 0.656 |
| fact_only_exchange | 253 | 198 | 0 | 4 | 162 | 0.951 |
| full_visibility_minimal_exchange | 253 | 223 | 0 | 4 | 160 | 0.975 |
| private_plus_options_minimal_exchange | 253 | 228 | 0 | 4 | 160 | 0.982 |
| private_plus_shared_minimal_exchange | 253 | 213 | 0 | 4 | 163 | 0.967 |
| private_plus_task_minimal_exchange | 253 | 226 | 0 | 4 | 158 | 0.985 |
