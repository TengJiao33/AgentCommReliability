# 20260613-2038-a8002-dar-guarded-answer-diversity-gsm8k100

## What We Tried

Ran a bounded DAR GSM8K100 guarded-retention variant on A800_2.

This run applies a post-filter answer-diversity guard after DAR `filter_critical`, then passes retained peer context as parsed answers only rather than full prior reasoning.

## Scope

- Method: DAR `filter_critical` plus answer-diversity guard
- Model: Qwen2.5-7B-Instruct
- Dataset: GSM8K, project-local MAD-MM JSONL fallback
- Seed: 42
- Samples: 100
- Agents: 3
- Debate rounds: 1
- Message surface: `answer_only`

## Resource Notes

- Machine: A800_2
- GPU: 7
- Timeout: 60m
- Wall time: about 2m04s
- Status: completed; GPU 7 released

## Code

- Upstream DAR commit: `f3c6e9d7c5f9805113f4398c20cbf7d732d60dd0`
- Existing A800_2 patches:
  - `a8002-local-qwen-paths.patch`
  - `a8002-arithmetic-escaped-brace-parser.patch`
  - `a8002-respect-out-dir.patch`
  - `a8002-gsm8k-local-jsonl-fallback.patch`
  - `a8002-filter-retention-history.patch`
- New patch:
  - `baselines/DAR/patches/a8002-guarded-answer-diversity.patch`
- Launcher:
  - `scripts/run_dar_guarded_retention_a8002.sh`

## Command

```bash
DAR_GPU_ID=7 DAR_TIMEOUT=60m DAR_STAMP=20260613_2038 \
bash /data/xuhaoming/yfy/research_workspace/scripts/run_dar_guarded_retention_a8002.sh
```

Core `src/main.py` args:

```bash
--model qwen2.5-7b
--num_agents 3
--data gsm8k
--data_size 100
--debate_rounds 1
--uncertainty_prompt True
--vote_prompt True
--m_role filter_critical
--retention_guard answer_diversity
--retention_guard_max 3
--retention_message_mode answer_only
--save_full_history
```

## Remote Artifacts

- Log: `/data/xuhaoming/yfy/research_workspace/logs/dar-guarded-answer-diversity-qwen25-7b-gsm8k100-20260613_2038.log`
- Result dir: `/data/xuhaoming/yfy/research_workspace/results/dar-guarded-answer-diversity-qwen25-7b-gsm8k100-20260613_2038/out`
- Unified trace: `/data/xuhaoming/yfy/research_workspace/results/unified-traces/dar-guarded-answer-diversity-gsm8k100-20260613_2038.comm_trace.jsonl`

## Local Artifacts

- `run.log`
- `dar_history_guarded_answer_diversity_gsm8k100.jsonl`
- `comm_trace_dar_guarded.jsonl`
- `analysis_summary.json`
- `changed_cases.jsonl`

## What Happened

| Method | Round 0 Acc. | Round 1 Acc. | Transitions | Total Tokens |
| --- | ---: | ---: | --- | ---: |
| original DAR `filter_critical` | 0.95 | 0.93 | 92 stable-right, 3 right-to-wrong, 1 wrong-to-right, 4 stable-wrong | 542,498 |
| guarded answer-only | 0.95 | 0.95 | 94 stable-right, 1 right-to-wrong, 1 wrong-to-right, 4 stable-wrong | 418,427 |

Token accounting above sums generation tokens and filter tokens from saved history. The guarded answer-only run used about `77.1%` of the original token total.

Guard behavior:

- changed retained sets: 17 / 100
- recovered at least one correct retained first-round message: 13 cases
- lost correct retained first-round messages: 0 cases
- all 100 retention events used `answer_only` message mode

Known original right-to-wrong cases:

| Sample | Original | Guarded | Note |
| ---: | --- | --- | --- |
| 5 | right-to-wrong, final `3` | stable-right, final `5` | guard did not change IDs; answer-only context avoided the earlier continuation/parser failure. |
| 20 | right-to-wrong, final `700` | right-to-wrong, final `12` | guard added correct `Agent1`, but wrong alternatives still dominated. |
| 22 | right-to-wrong, final empty | stable-right, final `131250` | guard replaced unparseable retained `Agent1` with parseable correct `Agent2`. |

## Caveats

- This is one seed/model/slice.
- Two changes happened together: answer-diversity guard and answer-only retained-message surface.
- The run improves this slice, but sample `20` shows answer diversity is not enough when wrong alternatives remain visible.
- Token totals are from saved DAR history and are comparable to the prior full-history run because both include generation and filter token logs.

## Loose Threads

- Separate the two interventions later: answer-only without guard, and guard with full messages.
- Inspect sample `20` to see whether answer-only should include vote counts, confidence, or a verifier prompt.
- Consider a tiny MATH or MMLU-Pro analog only after the DAR GSM8K case behavior is understood.
