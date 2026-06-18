# HiddenBench Communication Necessity Probe

## Purpose

This run tests whether the benchmark supplies external pressure for genuine communication necessity: individual agents see only partial private information, while public-fact and full-information conditions expose the information needed for the correct decision.

## Status

- Run id: `20260617-20260617-102311-a8002-hiddenbench-full65-answerfirst-qwen25-14b`
- Status: `completed`
- Claim status: `benchmark_probe`
- Tasks: `65`
- Records: `513`

## Primary Contrast

`shared_only` and `single_private_agent` are the partial-information floor. `oracle_public_facts`, `full_info`, and `exchange_then_decide` test whether surfaced private facts support a better decision.

## Summary

# HiddenBench Communication Necessity Probe

- Tasks: `65`
- Records: `513`

| Condition | Records | Correct | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| exchange_then_decide | 65 | 23 | 0.354 | 1 |
| full_info | 65 | 59 | 0.908 | 0 |
| oracle_public_facts | 65 | 56 | 0.862 | 0 |
| shared_only | 65 | 1 | 0.015 | 0 |
| single_private_agent | 253 | 62 | 0.245 | 1 |
| single_private_task_any | 65 | 37 | 0.569 | 0 |
| single_private_task_majority | 65 | 16 | 0.246 | 0 |

## Readout Contract

- `shared_only` estimates the no-private-information floor.
- `single_private_agent` estimates individual partial-information behavior.
- `oracle_public_facts` gives the final model all private facts as clean public messages.
- `full_info` gives the final model all facts directly.
- `exchange_then_decide` first asks partial agents to emit public messages, then asks a final model to decide from those messages.

A communication-necessity signal requires a clear gap from partial-information conditions to full/public-fact conditions. An exchange protocol is useful only if it closes part of that gap without simply revealing hidden gold labels.


## Caveats

- This runner uses HiddenBench tasks but implements a local protocol rather than the official group-interaction harness.
- single_private_agent rows are partial-information probes, not independent human-like participants.
- exchange_then_decide can fail either because agents omit private facts or because the final decider misintegrates public messages.
