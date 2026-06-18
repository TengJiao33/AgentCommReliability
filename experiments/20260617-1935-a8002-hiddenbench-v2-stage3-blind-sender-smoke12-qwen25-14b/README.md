# HiddenBench Communication Necessity Probe

## Purpose

This run tests whether the benchmark supplies external pressure for genuine communication necessity: individual agents see only partial private information, while public-fact and full-information conditions expose the information needed for the correct decision.

## Status

- Run id: `20260617-1935-a8002-hiddenbench-v2-stage3-blind-sender-smoke12-qwen25-14b`
- Status: `completed`
- Claim status: `preflight`
- Tasks: `12`
- Records: `96`

## Primary Contrast

`shared_only` and `single_private_agent` are the partial-information floor. `oracle_public_facts` and `full_info` test whether the task is solvable when private facts are surfaced. Exchange variants separate recommendation leakage, shared-fact repetition, private-fact reporting, answer-option visibility, and final integration.

## Summary

# HiddenBench Communication Necessity Probe

- Tasks: `12`
- Records: `96`

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


## Caveats

- This runner uses HiddenBench tasks but implements a local protocol rather than the official group-interaction harness.
- single_private_agent rows are partial-information probes, not independent human-like participants.
- exchange_then_decide can fail either because agents omit private facts or because the final decider misintegrates public messages.
- fact_only_constraint_decide reuses fact_only_exchange messages, so the paired contrast isolates final integration prompt effects.
- Stage 2 sender-ablation conditions isolate recommendation leakage, shared-fact repetition, and answer-option visibility in sender prompts.
- Stage 3 blind-sender conditions remove task description, shared facts, and answer options from sender prompts to test whether reduced sender task visibility improves public messages.
- Public-message audit fields are automatic proxies; invented facts still require manual case inspection before becoming claims.
