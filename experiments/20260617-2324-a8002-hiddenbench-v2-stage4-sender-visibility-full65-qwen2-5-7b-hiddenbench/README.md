# HiddenBench Communication Necessity Probe

## Purpose

This run tests whether the benchmark supplies external pressure for genuine communication necessity: individual agents see only partial private information, while public-fact and full-information conditions expose the information needed for the correct decision.

## Status

- Run id: `20260617-2324-a8002-hiddenbench-v2-stage4-sender-visibility-full65-qwen2-5-7b-hiddenbench`
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


## Caveats

- This runner uses HiddenBench tasks but implements a local protocol rather than the official group-interaction harness.
- single_private_agent rows are partial-information probes, not independent human-like participants.
- exchange_then_decide can fail either because agents omit private facts or because the final decider misintegrates public messages.
- fact_only_constraint_decide reuses fact_only_exchange messages, so the paired contrast isolates final integration prompt effects.
- Stage 2 sender-ablation conditions isolate recommendation leakage, shared-fact repetition, and answer-option visibility in sender prompts.
- Stage 3 blind-sender conditions remove task description, shared facts, and answer options from sender prompts to test whether reduced sender task visibility improves public messages.
- Stage 4 sender-visibility-matrix conditions keep a minimal observation-note output format while varying task, shared-fact, answer-option, and full sender visibility.
- Public-message audit fields are automatic proxies; invented facts still require manual case inspection before becoming claims.

## 7B Full65 Post-Run Record

- Local mirror: `experiments/20260617-2324-a8002-hiddenbench-v2-stage4-sender-visibility-full65-qwen2-5-7b-hiddenbench/`
- Remote path: `/data/xuhaoming/yfy/research_workspace/experiments/20260617-2324-a8002-hiddenbench-v2-stage4-sender-visibility-full65-qwen2-5-7b-hiddenbench/`
- Host/GPU/port: `A800_2`, GPU `7`, port `8053`
- Model path: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
- Served model: `qwen2.5-7b-hiddenbench`
- Temperature: `0.0`
- Max tokens: `320`
- Request timeout: `240`
- Launch command:

```powershell
.\scripts\run_hiddenbench_stage4_sender_visibility_a8002.ps1 -Limit 65 -Port 8053 -ModelPath /mnt/quarkfs/share_model/Qwen2.5-7B-Instruct -ServedModel qwen2.5-7b-hiddenbench -RunTimeout 20000 -RunId 20260617-2324-a8002-hiddenbench-v2-stage4-sender-visibility-full65-qwen2-5-7b-hiddenbench
```

Analysis commands:

```bash
python scripts/analyze_hiddenbench_records.py \
  --records experiments/20260617-2324-a8002-hiddenbench-v2-stage4-sender-visibility-full65-qwen2-5-7b-hiddenbench/records.jsonl \
  --out-dir experiments/20260617-2324-a8002-hiddenbench-v2-stage4-sender-visibility-full65-qwen2-5-7b-hiddenbench/analysis_corrected

python scripts/analyze_hiddenbench_subsets.py \
  --records experiments/20260617-2324-a8002-hiddenbench-v2-stage4-sender-visibility-full65-qwen2-5-7b-hiddenbench/analysis_corrected/corrected_records.jsonl \
  --out-dir experiments/20260617-2324-a8002-hiddenbench-v2-stage4-sender-visibility-full65-qwen2-5-7b-hiddenbench/analysis_subsets
```

Post-run checks:

- `records.jsonl`: `650` records, matching `65` tasks x `10` conditions.
- `runner.stderr.log`: empty.
- Corrected rescoring changes: `0`.
- Cleanup: no `run_hiddenbench_probe` or vLLM process remained on `A800_2`; port `8053` had no listener after completion.
- Remote GPU 7 after cleanup: `4 MiB` used, `0%` utilization.

Claim status: `cross-model mechanism diagnostic`. 7B lowers the ceiling relative to 14B while preserving the same main contrast: old exchange is much worse than minimal fact-state style public messages.

Key corrected results:

| Subset | Tasks | blind_minimal | fact_only | private+task | private+options | private+shared | full_visibility | old_exchange |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| all | 65 | 51 | 51 | 50 | 52 | 51 | 50 | 18 |
| full_info_correct | 55 | 48 | 49 | 48 | 49 | 49 | 48 | 17 |
| full_info_and_oracle_public_facts_correct | 50 | 47 | 47 | 47 | 47 | 47 | 46 | 16 |

Manual/case-atlas triage:

- Case atlas: `analysis_case_atlas/case_atlas.md`
- Clean subset size: `50`.
- Clean visibility split cases where `blind_minimal_exchange` differs from any visibility-minimal condition: `1` (`city_storm_shelter_decision`).
- Clean minimal-condition disagreements: `4`.
- Clean old-exchange failures where `blind_minimal_exchange` is correct: `32`.
- Across those 32 old-exchange failures, old exchange messages show `55` recommendation-leakage hits, `73` shared-overtalk hits, and `115` answer-mention hits over `124` public messages.

Interpretation:

- 7B is a useful external pressure because it reduces the ceiling: clean minimal fact-state conditions are around `47/50`, compared with 14B's `55/55`.
- The main phenomenon survives the smaller model. Old exchange is `16/50` on clean tasks, while blind/fact/minimal-visibility conditions are `46-47/50`.
- Sender visibility remains a weak secondary effect. Clean visibility split cases are rare, and the visibility-minimal conditions stay clustered.
- The strongest mechanism remains output-contract/fact-state formation: old helpful messages are polluted by candidate mentions, recommendations, and shared-fact overtalk; minimal local-observation messages preserve usable private evidence.

Next usable artifact:

- Use the 7B/14B pair as cross-model evidence that the failure is not just a 14B ceiling artifact.
- Next pressure should implement `fact_state_admission` directly and compare it against old exchange plus minimal-message controls on both 7B and 14B.
