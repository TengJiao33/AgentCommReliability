# DAR Source Note

## Upstream

- paper: https://arxiv.org/abs/2603.20640
- repo: https://github.com/DA2I2-SLM/DAR
- commit: `f3c6e9d7c5f9805113f4398c20cbf7d732d60dd0`
- license: MIT
- stars / activity: repository page showed 16 stars and 25 commits when inspected on 2026-06-12
- local path: not cloned locally; remote path `/data/xuhaoming/yfy/research_workspace/baselines/DAR`

## Why This Baseline

MAD-MM trace analysis produced cases where message retention, not only final voting, changed outcomes. DAR exposes an explicit retained-message control point through `filter_critical` and related filter modes.

## Smallest Runnable Path

- model: `qwen2.5-1.5b`
- dataset/task: `arithmetics`
- command:

```bash
python src/main.py --model qwen2.5-1.5b --num_agents 4 --data arithmetics --data_size 100 --debate_rounds 2
```

- expected output:
  - metrics: `out/arithmetics_vllm_batch_logs.tsv`
  - trace: `out/history/*.jsonl`
  - runtime logs: `result/*.jsonl`
- expected resource: one GPU for short run

## Installation Notes

- environment: create task-local env under `/data/xuhaoming/yfy/research_workspace/envs/dar`
- core dependencies: `datasets==4.0.0`, `numpy==2.1.2`, `pandas==2.3.1`, `vllm==0.16.0`, `accelerate==1.13.0`, `peft==0.18.1`
- data download: repository loads datasets through `data/data_utils.py`; arithmetics may be generated or local, GSM8K may require dataset access
- model path: A800_2 has `/mnt/quarkfs/share_model/Qwen2.5-1.5B` and `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
- known version constraints: `vllm==0.16.0` may not share the existing MAD-MM environment
- local path patch: `baselines/DAR/patches/a8002-local-qwen-paths.patch`
- parser patch: `baselines/DAR/patches/a8002-arithmetic-escaped-brace-parser.patch`
- output patch: `baselines/DAR/patches/a8002-respect-out-dir.patch`
- GSM8K offline data fallback patch: `baselines/DAR/patches/a8002-gsm8k-local-jsonl-fallback.patch`
- filter retention history patch: `baselines/DAR/patches/a8002-filter-retention-history.patch`
- guarded answer-diversity patch: `baselines/DAR/patches/a8002-guarded-answer-diversity.patch`

## Code Map

| Component | File / Function | Notes |
| --- | --- | --- |
| prompt templates | `src/evaluator.py`; `src/dev.py` | suffixes and message construction need inspection after clone |
| agent loop | `src/main.py` | batched round-0 generation and later debate rounds |
| communication | `get_new_message_global` | constructs peer context for each agent |
| memory/context | `history_agent_responses`, `history_final_resps`, `history_debate_resps` | previous round state stored per sample |
| routing/filtering | `run_filter_batch_across_samples`; `filter_critical` | retained IDs are precomputed before later-round prompts |
| judge/verifier | optional `--separate_moderator` | default uses same model as filtering moderator |
| evaluation | `evaluate_arithmetics`, `evaluate_mcq`, `evaluate_gen` | writes per-round accuracy and history JSONL |

## Known Caveats

- Repository defaults use model identifiers; local path mapping may be needed.
- README notes vLLM and HF inference can differ.
- Non-debug mode stores only first 10 history records.
- `a8002-filter-retention-history.patch` adds `--save_full_history` and per-round `retention_events`.
- `a8002-guarded-answer-diversity.patch` adds an experimental post-filter guard and optional `answer_only` retained-message surface; use only for bounded follow-up runs.
- A800_2 cannot currently rely on Hugging Face access for GSM8K; use the project-local JSONL fallback or set `DAR_GSM8K_JSONL`.
- Completed project runs are recorded under:
  - `experiments/20260612-a8002-dar-qwen25-7b-arithmetics-smoke/`
  - `experiments/20260612-a8002-dar-qwen25-7b-arithmetics-short-matrix/`
  - `experiments/20260612-a8002-dar-qwen25-7b-gsm8k-short-matrix/`

## Next Check

- Apply `a8002-guarded-answer-diversity.patch` after the existing A800_2 patch stack and run the bounded GSM8K100 guarded answer-only variant.
