# HiddenBench Communication Necessity Probe

- Tasks: `12`
- Records: `93`

| Condition | Records | Correct | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| exchange_then_decide | 12 | 4 | 0.333 | 5 |
| full_info | 12 | 7 | 0.583 | 5 |
| oracle_public_facts | 12 | 6 | 0.500 | 5 |
| shared_only | 12 | 0 | 0.000 | 6 |
| single_private_agent | 45 | 7 | 0.156 | 16 |
| single_private_task_any | 12 | 6 | 0.500 | 0 |
| single_private_task_majority | 12 | 2 | 0.167 | 0 |

## Readout Contract

- `shared_only` estimates the no-private-information floor.
- `single_private_agent` estimates individual partial-information behavior.
- `oracle_public_facts` gives the final model all private facts as clean public messages.
- `full_info` gives the final model all facts directly.
- `exchange_then_decide` first asks partial agents to emit public messages, then asks a final model to decide from those messages.

A communication-necessity signal requires a clear gap from partial-information conditions to full/public-fact conditions. An exchange protocol is useful only if it closes part of that gap without simply revealing hidden gold labels.
