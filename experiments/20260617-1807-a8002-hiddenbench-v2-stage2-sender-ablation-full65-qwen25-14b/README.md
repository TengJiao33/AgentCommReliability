# HiddenBench Communication Necessity Probe

## Purpose

This run tests whether the benchmark supplies external pressure for genuine communication necessity: individual agents see only partial private information, while public-fact and full-information conditions expose the information needed for the correct decision.

## Status

- Run id: `20260617-1807-a8002-hiddenbench-v2-stage2-sender-ablation-full65-qwen25-14b`
- Status: `completed`
- Claim status: `benchmark_probe`
- Tasks: `65`
- Records: `585`

## Primary Contrast

`shared_only` and `single_private_agent` are the partial-information floor. `oracle_public_facts` and `full_info` test whether the task is solvable when private facts are surfaced. Exchange variants separate recommendation leakage, shared-fact repetition, private-fact reporting, answer-option visibility, and final integration.

## Summary

# HiddenBench Communication Necessity Probe

- Tasks: `65`
- Records: `585`

| Condition | Records | Correct | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| exchange_then_decide | 65 | 24 | 0.369 | 0 |
| fact_only_constraint_decide | 65 | 56 | 0.862 | 0 |
| fact_only_exchange | 65 | 57 | 0.877 | 0 |
| fact_only_with_options_exchange | 65 | 56 | 0.862 | 0 |
| full_info | 65 | 59 | 0.908 | 0 |
| no_recommendation_exchange | 65 | 30 | 0.462 | 0 |
| no_shared_repeat_exchange | 65 | 33 | 0.508 | 0 |
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
- `fact_only_constraint_decide` reuses the fact-only messages and changes only the final integration prompt.

A communication-necessity signal requires a clear gap from partial-information conditions to full/public-fact conditions. An exchange protocol is useful only if it closes part of that gap without simply revealing hidden gold labels.

## Paired Contrasts

- `full_info_vs_shared_only`: paired `65`, left-only `59`, right-only `1`, both-correct `0`, both-wrong `5`
- `oracle_public_facts_vs_shared_only`: paired `65`, left-only `56`, right-only `1`, both-correct `0`, both-wrong `8`
- `oracle_public_facts_vs_exchange_then_decide`: paired `65`, left-only `33`, right-only `1`, both-correct `23`, both-wrong `8`
- `no_recommendation_exchange_vs_exchange_then_decide`: paired `65`, left-only `12`, right-only `6`, both-correct `18`, both-wrong `29`
- `no_shared_repeat_exchange_vs_exchange_then_decide`: paired `65`, left-only `11`, right-only `2`, both-correct `22`, both-wrong `30`
- `fact_only_exchange_vs_no_recommendation_exchange`: paired `65`, left-only `29`, right-only `2`, both-correct `28`, both-wrong `6`
- `fact_only_exchange_vs_no_shared_repeat_exchange`: paired `65`, left-only `25`, right-only `1`, both-correct `32`, both-wrong `7`
- `oracle_public_facts_vs_fact_only_exchange`: paired `65`, left-only `1`, right-only `2`, both-correct `55`, both-wrong `7`
- `fact_only_exchange_vs_fact_only_with_options_exchange`: paired `65`, left-only `2`, right-only `1`, both-correct `55`, both-wrong `7`
- `fact_only_exchange_vs_exchange_then_decide`: paired `65`, left-only `34`, right-only `1`, both-correct `23`, both-wrong `7`
- `fact_only_constraint_decide_vs_fact_only_exchange`: paired `65`, left-only `0`, right-only `1`, both-correct `56`, both-wrong `8`
- `fact_only_constraint_decide_vs_exchange_then_decide`: paired `65`, left-only `33`, right-only `1`, both-correct `23`, both-wrong `8`
- `full_info_vs_fact_only_constraint_decide`: paired `65`, left-only `3`, right-only `0`, both-correct `56`, both-wrong `6`

## Public Message Audit

| Condition | Messages | Private exact | Rec leakage | Shared overtalk | Answer mentions | Avg private overlap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| exchange_then_decide | 253 | 6 | 225 | 134 | 247 | 0.656 |
| fact_only_constraint_decide | 253 | 198 | 0 | 4 | 162 | 0.951 |
| fact_only_exchange | 253 | 198 | 0 | 4 | 162 | 0.951 |
| fact_only_with_options_exchange | 253 | 199 | 0 | 4 | 166 | 0.947 |
| no_recommendation_exchange | 253 | 2 | 12 | 176 | 237 | 0.628 |
| no_shared_repeat_exchange | 253 | 6 | 191 | 28 | 238 | 0.715 |


## Caveats

- This runner uses HiddenBench tasks but implements a local protocol rather than the official group-interaction harness.
- single_private_agent rows are partial-information probes, not independent human-like participants.
- exchange_then_decide can fail either because agents omit private facts or because the final decider misintegrates public messages.
- fact_only_constraint_decide reuses fact_only_exchange messages, so the paired contrast isolates final integration prompt effects.
- Stage 2 sender-ablation conditions isolate recommendation leakage, shared-fact repetition, and answer-option visibility in sender prompts.
- Public-message audit fields are automatic proxies; invented facts still require manual case inspection before becoming claims.

## Post-Run Analysis

- Corrected scoring produced `0` rescoring changes.
- Corrected analysis path: `analysis_corrected/corrected_summary.md`.
- Clean-subset analysis path: `analysis_subsets/subset_summary.md`.
- Case triage path: `case_triage_summary.md`.
- On the `55` tasks where `full_info` and `oracle_public_facts` are both correct:
  - `exchange_then_decide`: `23/55`;
  - `no_recommendation_exchange`: `28/55`;
  - `no_shared_repeat_exchange`: `31/55`;
  - `fact_only_with_options_exchange`: `53/55`;
  - `fact_only_exchange`: `55/55`;
  - `fact_only_constraint_decide`: `55/55`.
- Interpretation: local sender bans partially recover old exchange failures,
  but exact fact-only public-state transfer remains much stronger and has no
  clean-subset regressions against either local sender ban.
