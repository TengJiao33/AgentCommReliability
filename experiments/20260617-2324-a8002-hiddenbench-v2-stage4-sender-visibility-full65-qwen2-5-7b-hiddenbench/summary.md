# HiddenBench Communication Necessity Probe

- Tasks: `65`
- Records: `650`

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
