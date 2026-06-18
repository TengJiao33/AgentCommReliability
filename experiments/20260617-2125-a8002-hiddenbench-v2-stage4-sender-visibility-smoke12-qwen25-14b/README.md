# HiddenBench Communication Necessity Probe

## Purpose

This run tests whether the benchmark supplies external pressure for genuine communication necessity: individual agents see only partial private information, while public-fact and full-information conditions expose the information needed for the correct decision.

## Status

- Run id: `20260617-2125-a8002-hiddenbench-v2-stage4-sender-visibility-smoke12-qwen25-14b`
- Status: `completed`
- Claim status: `preflight`
- Tasks: `12`
- Records: `120`

## Primary Contrast

`shared_only` and `single_private_agent` are the partial-information floor. `oracle_public_facts` and `full_info` test whether the task is solvable when private facts are surfaced. Exchange variants separate recommendation leakage, shared-fact repetition, private-fact reporting, answer-option visibility, and final integration.

## Summary

# HiddenBench Communication Necessity Probe

- Tasks: `12`
- Records: `120`

| Condition | Records | Correct | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| blind_minimal_exchange | 12 | 9 | 0.750 | 0 |
| exchange_then_decide | 12 | 2 | 0.167 | 0 |
| fact_only_exchange | 12 | 9 | 0.750 | 0 |
| full_info | 12 | 9 | 0.750 | 0 |
| full_visibility_minimal_exchange | 12 | 7 | 0.583 | 0 |
| oracle_public_facts | 12 | 8 | 0.667 | 0 |
| private_plus_options_minimal_exchange | 12 | 7 | 0.583 | 0 |
| private_plus_shared_minimal_exchange | 12 | 7 | 0.583 | 0 |
| private_plus_task_minimal_exchange | 12 | 8 | 0.667 | 0 |
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
- `private_plus_task_minimal_exchange` shows senders the task but keeps the minimal observation-note format.
- `private_plus_options_minimal_exchange` shows senders the answer options but keeps the minimal observation-note format.
- `private_plus_shared_minimal_exchange` shows senders shared facts but keeps the minimal observation-note format.
- `full_visibility_minimal_exchange` shows senders task, shared facts, and options while keeping the minimal observation-note format.
- `fact_only_constraint_decide` reuses the fact-only messages and changes only the final integration prompt.

A communication-necessity signal requires a clear gap from partial-information conditions to full/public-fact conditions. An exchange protocol is useful only if it closes part of that gap without simply revealing hidden gold labels.

## Paired Contrasts

- `full_info_vs_shared_only`: paired `12`, left-only `9`, right-only `1`, both-correct `0`, both-wrong `2`
- `oracle_public_facts_vs_shared_only`: paired `12`, left-only `8`, right-only `1`, both-correct `0`, both-wrong `3`
- `oracle_public_facts_vs_exchange_then_decide`: paired `12`, left-only `6`, right-only `0`, both-correct `2`, both-wrong `4`
- `oracle_public_facts_vs_fact_only_exchange`: paired `12`, left-only `0`, right-only `1`, both-correct `8`, both-wrong `3`
- `blind_minimal_exchange_vs_exchange_then_decide`: paired `12`, left-only `7`, right-only `0`, both-correct `2`, both-wrong `3`
- `blind_minimal_exchange_vs_private_plus_task_minimal_exchange`: paired `12`, left-only `1`, right-only `0`, both-correct `8`, both-wrong `3`
- `blind_minimal_exchange_vs_private_plus_options_minimal_exchange`: paired `12`, left-only `2`, right-only `0`, both-correct `7`, both-wrong `3`
- `blind_minimal_exchange_vs_private_plus_shared_minimal_exchange`: paired `12`, left-only `2`, right-only `0`, both-correct `7`, both-wrong `3`
- `blind_minimal_exchange_vs_full_visibility_minimal_exchange`: paired `12`, left-only `2`, right-only `0`, both-correct `7`, both-wrong `3`
- `fact_only_exchange_vs_blind_minimal_exchange`: paired `12`, left-only `1`, right-only `1`, both-correct `8`, both-wrong `2`
- `fact_only_exchange_vs_full_visibility_minimal_exchange`: paired `12`, left-only `2`, right-only `0`, both-correct `7`, both-wrong `3`
- `full_visibility_minimal_exchange_vs_exchange_then_decide`: paired `12`, left-only `5`, right-only `0`, both-correct `2`, both-wrong `5`
- `fact_only_exchange_vs_exchange_then_decide`: paired `12`, left-only `7`, right-only `0`, both-correct `2`, both-wrong `3`

## Public Message Audit

| Condition | Messages | Private exact | Rec leakage | Shared overtalk | Answer mentions | Avg private overlap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| blind_minimal_exchange | 45 | 38 | 0 | 4 | 28 | 0.985 |
| exchange_then_decide | 45 | 6 | 41 | 25 | 45 | 0.714 |
| fact_only_exchange | 45 | 28 | 0 | 4 | 27 | 0.896 |
| full_visibility_minimal_exchange | 45 | 34 | 0 | 4 | 28 | 0.910 |
| private_plus_options_minimal_exchange | 45 | 35 | 0 | 4 | 28 | 0.960 |
| private_plus_shared_minimal_exchange | 45 | 32 | 0 | 4 | 31 | 0.884 |
| private_plus_task_minimal_exchange | 45 | 36 | 0 | 4 | 28 | 0.963 |


## Caveats

- This runner uses HiddenBench tasks but implements a local protocol rather than the official group-interaction harness.
- single_private_agent rows are partial-information probes, not independent human-like participants.
- exchange_then_decide can fail either because agents omit private facts or because the final decider misintegrates public messages.
- fact_only_constraint_decide reuses fact_only_exchange messages, so the paired contrast isolates final integration prompt effects.
- Stage 2 sender-ablation conditions isolate recommendation leakage, shared-fact repetition, and answer-option visibility in sender prompts.
- Stage 3 blind-sender conditions remove task description, shared facts, and answer options from sender prompts to test whether reduced sender task visibility improves public messages.
- Stage 4 sender-visibility-matrix conditions keep a minimal observation-note output format while varying task, shared-fact, answer-option, and full sender visibility.
- Public-message audit fields are automatic proxies; invented facts still require manual case inspection before becoming claims.

## Stage 4 Post-Run Record

- Local mirror: `experiments/20260617-2125-a8002-hiddenbench-v2-stage4-sender-visibility-smoke12-qwen25-14b/`
- Remote path: `/data/xuhaoming/yfy/research_workspace/experiments/20260617-2125-a8002-hiddenbench-v2-stage4-sender-visibility-smoke12-qwen25-14b/`
- Host/GPU/port: `A800_2`, GPU `7`, port `8053`
- Model path: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- Served model: `qwen2.5-14b-hiddenbench`
- Temperature: `0.0`
- Max tokens: `320`
- Request timeout: `240`
- Launch command:

```powershell
.\scripts\run_hiddenbench_stage4_sender_visibility_a8002.ps1 -Limit 12 -Port 8053 -RunId 20260617-2125-a8002-hiddenbench-v2-stage4-sender-visibility-smoke12-qwen25-14b
```

Analysis commands:

```bash
python scripts/analyze_hiddenbench_records.py \
  --records experiments/20260617-2125-a8002-hiddenbench-v2-stage4-sender-visibility-smoke12-qwen25-14b/records.jsonl \
  --out-dir experiments/20260617-2125-a8002-hiddenbench-v2-stage4-sender-visibility-smoke12-qwen25-14b/analysis_corrected

python scripts/analyze_hiddenbench_subsets.py \
  --records experiments/20260617-2125-a8002-hiddenbench-v2-stage4-sender-visibility-smoke12-qwen25-14b/analysis_corrected/corrected_records.jsonl \
  --out-dir experiments/20260617-2125-a8002-hiddenbench-v2-stage4-sender-visibility-smoke12-qwen25-14b/analysis_subsets
```

Post-run checks:

- `records.jsonl`: `120` records, matching `12` tasks x `10` conditions.
- `runner.stderr.log`: empty.
- Corrected rescoring changes: `0`.
- Cleanup: no `run_hiddenbench_probe` or vLLM process remained on `A800_2`; port `8053` had no listener after completion.
- Remote GPU 7 after cleanup: about `6083 MiB` used, no active vLLM server from this run.

Claim status: `diagnostic smoke`. The run supports using the Stage 4 matrix for a full run, but it is not a paper-level claim because the clean subset is only `8` tasks.

Key corrected results:

| Subset | Tasks | blind_minimal | fact_only | private+task | private+options | private+shared | full_visibility | old_exchange |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| all | 12 | 9 | 9 | 8 | 7 | 7 | 7 | 2 |
| full_info_correct | 9 | 8 | 9 | 8 | 7 | 7 | 7 | 2 |
| full_info_and_oracle_public_facts_correct | 8 | 8 | 8 | 8 | 7 | 7 | 7 | 2 |

Manual triage:

- On the clean subset, `exchange_then_decide` fails on `6/8` tasks where `blind_minimal_exchange` succeeds. The public-message audit shows old exchange has `41/45` recommendation-leakage messages and `25/45` shared-overtalk messages.
- `baker_2010` is the only clean task in this smoke that separates the minimal visibility conditions: `blind_minimal_exchange`, `fact_only_exchange`, and `private_plus_task_minimal_exchange` choose `Roberts`, while `private_plus_options_minimal_exchange`, `private_plus_shared_minimal_exchange`, and `full_visibility_minimal_exchange` choose `Jones`.
- In that case, the added sender context appears to encourage selective compression around surface-visible candidate advantages. This is a hypothesis from one case, not a supported mechanism claim.
- The `clean_info_unstable` subset has only `4` tasks and should be treated as background instability, because full-info or oracle-public-fact controls do not reliably solve those tasks.

Next usable artifact:

- A full `Limit 65` Stage 4 run is justified if the goal is to pressure the sender-visibility hypothesis.
- The full run should report the same clean subsets and include a manual case atlas for all tasks where `blind_minimal_exchange` differs from any visibility-minimal condition.
