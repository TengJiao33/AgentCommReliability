# HiddenBench Communication Necessity Probe

- Tasks: `12`
- Records: `93`

| Condition | Records | Correct | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| exchange_then_decide | 12 | 2 | 0.167 | 0 |
| full_info | 12 | 9 | 0.750 | 0 |
| oracle_public_facts | 12 | 8 | 0.667 | 0 |
| shared_only | 12 | 1 | 0.083 | 0 |
| single_private_agent | 45 | 10 | 0.222 | 0 |
| single_private_task_any | 12 | 5 | 0.417 | 0 |
| single_private_task_majority | 12 | 3 | 0.250 | 0 |

## Readout Contract

- `shared_only` estimates the no-private-information floor.
- `single_private_agent` estimates individual partial-information behavior.
- `oracle_public_facts` gives the final model all private facts as clean public messages.
- `full_info` gives the final model all facts directly.
- `exchange_then_decide` first asks partial agents to emit public messages, then asks a final model to decide from those messages.

A communication-necessity signal requires a clear gap from partial-information conditions to full/public-fact conditions. An exchange protocol is useful only if it closes part of that gap without simply revealing hidden gold labels.
