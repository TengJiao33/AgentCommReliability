# HiddenBench Communication Necessity Probe

## Purpose

This run tests whether the benchmark supplies external pressure for genuine communication necessity: individual agents see only partial private information, while public-fact and full-information conditions expose the information needed for the correct decision.

## Status

- Run id: `20260617-1946-a8002-hiddenbench-v2-stage3-blind-sender-full65-qwen25-14b`
- Status: `completed`
- Claim status: `benchmark_probe`
- Tasks: `65`
- Records: `520`

## Primary Contrast

`shared_only` and `single_private_agent` are the partial-information floor. `oracle_public_facts` and `full_info` test whether the task is solvable when private facts are surfaced. Exchange variants separate recommendation leakage, shared-fact repetition, private-fact reporting, answer-option visibility, and final integration.

## Summary

# HiddenBench Communication Necessity Probe

- Tasks: `65`
- Records: `520`

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
- `fact_only_constraint_decide` reuses the fact-only messages and changes only the final integration prompt.

A communication-necessity signal requires a clear gap from partial-information conditions to full/public-fact conditions. An exchange protocol is useful only if it closes part of that gap without simply revealing hidden gold labels.

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


## Caveats

- This runner uses HiddenBench tasks but implements a local protocol rather than the official group-interaction harness.
- single_private_agent rows are partial-information probes, not independent human-like participants.
- exchange_then_decide can fail either because agents omit private facts or because the final decider misintegrates public messages.
- fact_only_constraint_decide reuses fact_only_exchange messages, so the paired contrast isolates final integration prompt effects.
- Stage 2 sender-ablation conditions isolate recommendation leakage, shared-fact repetition, and answer-option visibility in sender prompts.
- Stage 3 blind-sender conditions remove task description, shared facts, and answer options from sender prompts to test whether reduced sender task visibility improves public messages.
- Public-message audit fields are automatic proxies; invented facts still require manual case inspection before becoming claims.
