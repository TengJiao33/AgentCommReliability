# HiddenBench Communication Necessity Probe

- Tasks: `12`
- Records: `120`

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
