# HiddenBench Communication Necessity Probe

## Purpose

This run tests whether the benchmark supplies external pressure for genuine communication necessity: individual agents see only partial private information, while public-fact and full-information conditions expose the information needed for the correct decision.

## Status

- Run id: `20260617-2159-a8002-hiddenbench-v2-stage4-sender-visibility-full65-qwen25-14b`
- Status: `completed`
- Claim status: `benchmark_probe`
- Tasks: `65`
- Records: `650`

## Primary Contrast

`shared_only` and `single_private_agent` are the partial-information floor. `oracle_public_facts` and `full_info` test whether the task is solvable when private facts are surfaced. Exchange variants separate recommendation leakage, shared-fact repetition, private-fact reporting, answer-option visibility, and final integration.

## Summary

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


## Caveats

- This runner uses HiddenBench tasks but implements a local protocol rather than the official group-interaction harness.
- single_private_agent rows are partial-information probes, not independent human-like participants.
- exchange_then_decide can fail either because agents omit private facts or because the final decider misintegrates public messages.
- fact_only_constraint_decide reuses fact_only_exchange messages, so the paired contrast isolates final integration prompt effects.
- Stage 2 sender-ablation conditions isolate recommendation leakage, shared-fact repetition, and answer-option visibility in sender prompts.
- Stage 3 blind-sender conditions remove task description, shared facts, and answer options from sender prompts to test whether reduced sender task visibility improves public messages.
- Stage 4 sender-visibility-matrix conditions keep a minimal observation-note output format while varying task, shared-fact, answer-option, and full sender visibility.
- Public-message audit fields are automatic proxies; invented facts still require manual case inspection before becoming claims.

## Stage 4 Full65 Post-Run Record

- Local mirror: `experiments/20260617-2159-a8002-hiddenbench-v2-stage4-sender-visibility-full65-qwen25-14b/`
- Remote path: `/data/xuhaoming/yfy/research_workspace/experiments/20260617-2159-a8002-hiddenbench-v2-stage4-sender-visibility-full65-qwen25-14b/`
- Host/GPU/port: `A800_2`, GPU `7`, port `8053`
- Model path: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- Served model: `qwen2.5-14b-hiddenbench`
- Temperature: `0.0`
- Max tokens: `320`
- Request timeout: `240`
- Launch command:

```powershell
.\scripts\run_hiddenbench_stage4_sender_visibility_a8002.ps1 -Limit 65 -Port 8053 -RunTimeout 24000 -RunId 20260617-2159-a8002-hiddenbench-v2-stage4-sender-visibility-full65-qwen25-14b
```

Analysis commands:

```bash
python scripts/analyze_hiddenbench_records.py \
  --records experiments/20260617-2159-a8002-hiddenbench-v2-stage4-sender-visibility-full65-qwen25-14b/records.jsonl \
  --out-dir experiments/20260617-2159-a8002-hiddenbench-v2-stage4-sender-visibility-full65-qwen25-14b/analysis_corrected

python scripts/analyze_hiddenbench_subsets.py \
  --records experiments/20260617-2159-a8002-hiddenbench-v2-stage4-sender-visibility-full65-qwen25-14b/analysis_corrected/corrected_records.jsonl \
  --out-dir experiments/20260617-2159-a8002-hiddenbench-v2-stage4-sender-visibility-full65-qwen25-14b/analysis_subsets
```

Post-run checks:

- `records.jsonl`: `650` records, matching `65` tasks x `10` conditions.
- `runner.stderr.log`: empty.
- Corrected rescoring changes: `0`.
- Cleanup: no `run_hiddenbench_probe` or vLLM process remained on `A800_2`; port `8053` had no listener after completion.
- Remote GPU 7 after cleanup: `4 MiB` used, `0%` utilization.

Claim status: `mechanism-diagnostic`. This run supports a strong output-contract/fact-state hypothesis on HiddenBench. It only weakly supports sender-visibility hiding as a mechanism, because clean visibility split cases are rare.

Key corrected results:

| Subset | Tasks | blind_minimal | fact_only | private+task | private+options | private+shared | full_visibility | old_exchange |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| all | 65 | 57 | 57 | 56 | 55 | 55 | 55 | 24 |
| full_info_correct | 59 | 55 | 57 | 55 | 54 | 54 | 54 | 24 |
| full_info_and_oracle_public_facts_correct | 55 | 55 | 55 | 55 | 54 | 54 | 54 | 23 |

Manual/case-atlas triage:

- Case atlas: `analysis_case_atlas/case_atlas.md`
- Clean subset size: `55`.
- Clean visibility split cases where `blind_minimal_exchange` differs from any visibility-minimal condition: `1` (`baker_2010`).
- Clean old-exchange failures where `blind_minimal_exchange` is correct: `32`.
- Across those 32 old-exchange failures, old exchange messages show `113` recommendation-leakage hits, `59` shared-overtalk hits, and `120` answer-mention hits over `125` public messages.

Interpretation:

- HiddenBench supplies a usable communication-necessity pressure: `shared_only` is `1/65`, while `full_info` is `59/65` and the clean subset contains `55` tasks.
- Old helpful exchange remains the failure mode: clean subset `23/55`, with heavy recommendation leakage and shared-fact overtalk.
- Minimal/fact-state style public messages are robust: `blind_minimal_exchange`, `fact_only_exchange`, and `private_plus_task_minimal_exchange` all reach `55/55` on the clean subset.
- Sender visibility hiding alone is a weak explanation in this run. Adding options/shared/full context under the same minimal output contract loses only one clean case.

Next usable artifact:

- Use this run as the main HiddenBench evidence for a fact-state/output-contract story.
- Treat `baker_2010` as a live counterexample-like case for candidate anchoring under extra sender visibility, not as a broad mechanism by itself.
- Next pressure should implement an explicit `fact_state_admission` protocol and compare it against old exchange, blind minimal, and full-visibility minimal on the same clean-subset readout.
