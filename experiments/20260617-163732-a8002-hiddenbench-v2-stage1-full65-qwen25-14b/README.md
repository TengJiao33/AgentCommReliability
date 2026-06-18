# HiddenBench Communication Necessity Probe

## Purpose

This run tests whether the benchmark supplies external pressure for genuine communication necessity: individual agents see only partial private information, while public-fact and full-information conditions expose the information needed for the correct decision.

## Status

- Run id: `20260617-163732-a8002-hiddenbench-v2-stage1-full65-qwen25-14b`
- Status: `completed`
- Claim status: `benchmark_probe`
- Tasks: `65`
- Records: `390`

## Primary Contrast

`shared_only` is the no-private-information floor. `oracle_public_facts` and `full_info` test whether the task is solvable when private facts are surfaced. `exchange_then_decide`, `fact_only_exchange`, and `fact_only_constraint_decide` separate public-message quality from final integration. This Stage 1 run did not include `single_private_agent`.

## Summary

# HiddenBench Communication Necessity Probe

- Tasks: `65`
- Records: `390`

| Condition | Records | Correct | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| exchange_then_decide | 65 | 24 | 0.369 | 0 |
| fact_only_constraint_decide | 65 | 56 | 0.862 | 0 |
| fact_only_exchange | 65 | 57 | 0.877 | 0 |
| full_info | 65 | 59 | 0.908 | 0 |
| oracle_public_facts | 65 | 56 | 0.862 | 0 |
| shared_only | 65 | 1 | 0.015 | 0 |

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

- `full_info_vs_shared_only`: paired `65`, left-only `59`, right-only `1`, both-correct `0`, both-wrong `5`
- `oracle_public_facts_vs_shared_only`: paired `65`, left-only `56`, right-only `1`, both-correct `0`, both-wrong `8`
- `oracle_public_facts_vs_exchange_then_decide`: paired `65`, left-only `33`, right-only `1`, both-correct `23`, both-wrong `8`
- `oracle_public_facts_vs_fact_only_exchange`: paired `65`, left-only `1`, right-only `2`, both-correct `55`, both-wrong `7`
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


## Caveats

- This runner uses HiddenBench tasks but implements a local protocol rather than the official group-interaction harness.
- This Stage 1 run excludes `single_private_agent`; compare it to the earlier old-protocol full65 only through shared conditions.
- exchange_then_decide can fail either because agents omit private facts or because the final decider misintegrates public messages.
- fact_only_constraint_decide reuses fact_only_exchange messages, so the paired contrast isolates final integration prompt effects.
- Public-message audit fields are automatic proxies; invented facts still require manual case inspection before becoming claims.

## Corrected Analysis

- Corrected summary: `analysis_corrected/corrected_summary.json`
- Corrected records: `analysis_corrected/corrected_records.jsonl`
- Subset summary: `analysis_corrected/subset_summary.json`
- Subset markdown: `analysis_corrected/subset_summary.md`

Evaluation command:

```bash
envs/mad-mm-vllm063/bin/python scripts/analyze_hiddenbench_records.py \
  --records experiments/20260617-163732-a8002-hiddenbench-v2-stage1-full65-qwen25-14b/records.jsonl \
  --out-dir experiments/20260617-163732-a8002-hiddenbench-v2-stage1-full65-qwen25-14b/analysis_corrected
```

Key subset readout:

- On all `65` tasks, `fact_only_exchange` is `57/65` and `exchange_then_decide` is `24/65`.
- On the `55` tasks where both `full_info` and `oracle_public_facts` are correct, `fact_only_exchange` is `55/55` and `exchange_then_decide` is `23/55`.
