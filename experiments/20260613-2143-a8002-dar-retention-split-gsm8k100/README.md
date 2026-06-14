# 20260613-2143-a8002-dar-retention-split-gsm8k100

## What We Tried

Split the previous DAR guarded answer-only run into two bounded GSM8K100 ablations:

- `answer_only_no_guard`: original DAR `filter_critical` retained IDs, but retained peer context is passed as parsed answers only.
- `guard_full`: answer-diversity guard after `filter_critical`, but retained peer context remains full prior messages.

The goal was to separate the two handles combined in `20260613-2038-a8002-dar-guarded-answer-diversity-gsm8k100`: selection guard versus retained-message surface.

## Scope

- Method: DAR `filter_critical` ablations
- Model: Qwen2.5-7B-Instruct
- Dataset: GSM8K, project-local MAD-MM JSONL fallback
- Seed: 42
- Samples: 100
- Agents: 3
- Debate rounds: 1

## Resource Notes

- Machine: A800_2
- GPU: 7
- Timeout: 60m
- Wall time:
  - `answer_only_no_guard`: 1m55s
  - `guard_full`: 2m09s
- Status: both completed; GPU 7 released

## Code

- Upstream DAR commit: `f3c6e9d7c5f9805113f4398c20cbf7d732d60dd0`
- Patch stack on A800_2:
  - `a8002-local-qwen-paths.patch`
  - `a8002-arithmetic-escaped-brace-parser.patch`
  - `a8002-respect-out-dir.patch`
  - `a8002-gsm8k-local-jsonl-fallback.patch`
  - `a8002-filter-retention-history.patch`
  - `a8002-guarded-answer-diversity.patch`
- Launcher:
  - `scripts/run_dar_retention_ablation_a8002.sh`
- Summary script:
  - `scripts/summarize_dar_retention_ablation.py`

## Command

```bash
DAR_GPU_ID=7 DAR_TIMEOUT=60m DAR_STAMP=20260613_2143 \
bash /data/xuhaoming/yfy/research_workspace/scripts/run_dar_retention_ablation_a8002.sh
```

Variants expanded by the launcher:

```bash
# answer_only_no_guard
--retention_guard none
--retention_message_mode answer_only

# guard_full
--retention_guard answer_diversity
--retention_guard_max 3
--retention_message_mode full
```

Shared core args:

```bash
--model qwen2.5-7b
--num_agents 3
--data gsm8k
--data_size 100
--debate_rounds 1
--uncertainty_prompt True
--vote_prompt True
--m_role filter_critical
--save_full_history
```

## Remote Artifacts

- `answer_only_no_guard` log: `/data/xuhaoming/yfy/research_workspace/logs/dar-answer-only-noguard-qwen25-7b-gsm8k100-20260613_2143.log`
- `answer_only_no_guard` result dir: `/data/xuhaoming/yfy/research_workspace/results/dar-answer-only-noguard-qwen25-7b-gsm8k100-20260613_2143/out`
- `answer_only_no_guard` unified trace: `/data/xuhaoming/yfy/research_workspace/results/unified-traces/dar-answer-only-noguard-gsm8k100-20260613_2143.comm_trace.jsonl`
- `guard_full` log: `/data/xuhaoming/yfy/research_workspace/logs/dar-guard-full-qwen25-7b-gsm8k100-20260613_2143.log`
- `guard_full` result dir: `/data/xuhaoming/yfy/research_workspace/results/dar-guard-full-qwen25-7b-gsm8k100-20260613_2143/out`
- `guard_full` unified trace: `/data/xuhaoming/yfy/research_workspace/results/unified-traces/dar-guard-full-gsm8k100-20260613_2143.comm_trace.jsonl`
- Combined remote summary: `/data/xuhaoming/yfy/research_workspace/results/dar-retention-ablation-20260613_2143/analysis_summary.json`

## Local Artifacts

- `run_answer_only_noguard.log`
- `run_guard_full.log`
- `dar_history_answer_only_noguard_gsm8k100.jsonl`
- `dar_history_guard_full_gsm8k100.jsonl`
- `comm_trace_answer_only_noguard.jsonl`
- `comm_trace_guard_full.jsonl`
- `analysis_summary.json`
- `changed_cases.jsonl`

## What Happened

| Method | Round 0 Acc. | Round 1 Acc. | Right-to-Wrong | Wrong-to-Right | Total Tokens |
| --- | ---: | ---: | ---: | ---: | ---: |
| original DAR `filter_critical` | 0.95 | 0.93 | 3 | 1 | 542,498 |
| `answer_only_no_guard` | 0.95 | 0.95 | 1 | 1 | 419,180 |
| guarded answer-only | 0.95 | 0.95 | 1 | 1 | 418,427 |
| `guard_full` | 0.95 | 0.96 | 0 | 1 | 545,520 |

Token totals sum generation and filter tokens from unified traces.

## Case Notes

Compared with original `filter_critical`:

- `answer_only_no_guard` recovered samples `5` and `22`, matching the earlier guarded answer-only run's final correctness changes.
- `guard_full` recovered samples `5`, `20`, and `22`.
- Sample `20` stayed wrong under both answer-only variants but became correct under `guard_full`; the guard added correct `Agent1`, and full retained reasoning appears to matter for this case.
- Sample `5` improved even without changing retained IDs, so the previous failure is still best treated as a continuation/parser or message-surface failure rather than a selection failure.
- Sample `22` improved under answer-only even without replacing the retained ID, which means answer-only context can avoid a parser-incompatible retained message surface even when selection remains unchanged.

## Caveats

- One seed/model/slice only.
- GSM8K100 is not the hardest place to expose communication differences.
- `guard_full` improves this slice but does not reduce token cost; it is slightly more expensive than original full-message `filter_critical`.
- `answer_only` saves tokens and fixes two right-to-wrong cases, but it still fails sample `20`.

## Loose Threads

- Inspect sample `20` to understand what information full retained reasoning preserved that answer-only removed.
- If continuing empirically, try a harder slice such as MATH50 or MMLU-Pro50 before expanding GSM8K.
