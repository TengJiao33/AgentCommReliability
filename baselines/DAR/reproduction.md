# DAR Reproduction Note

## Short Answer

DAR has setup/smoke evidence, a 100-sample arithmetics short matrix, and a 100-sample GSM8K short matrix on A800_2 with local Qwen2.5-7B-Instruct.

## Scope

- method: Diversity-Aware Retention for Multi-Agent Debate
- paper: https://arxiv.org/abs/2603.20640
- repo: https://github.com/DA2I2-SLM/DAR
- commit: `f3c6e9d7c5f9805113f4398c20cbf7d732d60dd0`
- local path: planned remote path `/data/xuhaoming/yfy/research_workspace/baselines/DAR`
- target settings:
  - `qwen2.5-7b`, `arithmetics`, `data_size=100`, `num_agents=3`, `debate_rounds=1`
  - `qwen2.5-7b`, `gsm8k`, `data_size=100`, `num_agents=3`, `debate_rounds=1`
- evidence level: Level 3 short-subset evidence for arithmetics and GSM8K

## Environment

- machine: A800_2
- env path: planned `/data/xuhaoming/yfy/research_workspace/envs/dar`
- Python: upstream recommends Python 3.10.16
- key packages: see `baselines/DAR/source.md`
- model paths:
  - invalid smoke: `/mnt/quarkfs/share_model/Qwen2.5-1.5B`
  - selected smoke model: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`

## Commands

Short-matrix baseline MAD:

```bash
python src/main.py --model qwen2.5-7b --num_agents 3 --data arithmetics --data_size 100 --debate_rounds 1
```

Top-K uncertainty:

```bash
python src/main.py --model qwen2.5-7b --num_agents 3 --data arithmetics --data_size 100 --debate_rounds 1 --top_k_uncertainty 0.5
```

DAR:

```bash
python src/main.py --model qwen2.5-7b --num_agents 3 --data arithmetics --data_size 100 --debate_rounds 1 \
  --uncertainty_prompt True --vote_prompt True --m_role filter_critical
```

## Outputs

- smoke logs:
  - `/data/xuhaoming/yfy/research_workspace/logs/dar_smoke_basic_20260612_174325.log`
  - `/data/xuhaoming/yfy/research_workspace/logs/dar-smoke-qwen25-7b-arith2-parserpatch-20260612_183256.log`
  - `/data/xuhaoming/yfy/research_workspace/logs/dar-smoke-filtercritical-qwen25-7b-arith2-20260612_183819.log`
- smoke result directories:
  - `/data/xuhaoming/yfy/research_workspace/results/dar-smoke-qwen25-7b-arith2-parserpatch-20260612_183256/out`
  - `/data/xuhaoming/yfy/research_workspace/results/dar-smoke-filtercritical-qwen25-7b-arith2-20260612_183819/out`
- local run records:
  - `experiments/_archive/20260616-pruned/20260612-a8002-dar-qwen25-7b-arithmetics-smoke/`
  - `experiments/_archive/20260616-pruned/20260612-a8002-dar-qwen25-7b-arithmetics-short-matrix/`
  - `experiments/_archive/20260616-pruned/20260612-a8002-dar-qwen25-7b-gsm8k-short-matrix/`

Expected upstream paths:

- `out/*_vllm_batch_logs.tsv`
- `out/history/*.jsonl`
- `result/debate_logs.jsonl`
- `result/token_logs.jsonl`
- instrumented full-history check: `experiments/_archive/20260616-pruned/20260613-1718-a8002-trace-instrumentation-check/`
- instrumented GSM8K100 full-history check: `experiments/_archive/20260616-pruned/20260613-1730-a8002-dar-filtercritical-gsm8k100-fullhistory/`

## Result Snapshot

| Method | Model | Task | Seed | Samples | Metric | Tokens | Status |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| Basic MAD smoke | qwen2.5-7b | arithmetics | 42 | 2 | round 0/1 accuracy `1.0/1.0` | logged in history | complete |
| DAR `filter_critical` smoke | qwen2.5-7b | arithmetics | 42 | 2 | round 0/1 accuracy `1.0/1.0` | filter tokens logged | complete |
| Basic MAD short | qwen2.5-7b | arithmetics | 42 | 100 | round 0/1 accuracy `0.99/0.98` | not normalized | complete |
| Top-K uncertainty short | qwen2.5-7b | arithmetics | 42 | 100 | round 0/1 accuracy `0.97/0.94` | not normalized | complete |
| DAR `filter_critical` short | qwen2.5-7b | arithmetics | 42 | 100 | round 0/1 accuracy `0.99/0.99` | filter tokens `120,283` | complete |
| Basic MAD short | qwen2.5-7b | gsm8k | 42 | 100 | round 0/1 accuracy `0.95/0.95` | not normalized | complete |
| Top-K uncertainty short | qwen2.5-7b | gsm8k | 42 | 100 | round 0/1 accuracy `0.95/0.94` | not normalized | complete |
| DAR `filter_critical` short | qwen2.5-7b | gsm8k | 42 | 100 | round 0/1 accuracy `0.95/0.93` | filter tokens `113,657` | complete |
| DAR guarded answer-only | qwen2.5-7b | gsm8k | 42 | 100 | round 0/1 accuracy `0.95/0.95` | generation + filter tokens `418,427` | complete |
| DAR answer-only no guard | qwen2.5-7b | gsm8k | 42 | 100 | round 0/1 accuracy `0.95/0.95` | generation + filter tokens `419,180` | complete |
| DAR guard full | qwen2.5-7b | gsm8k | 42 | 100 | round 0/1 accuracy `0.95/0.96` | generation + filter tokens `545,520` | complete |

## Deviations From Upstream

- Planned runs should use local model paths on A800_2 if default Hugging Face model names trigger downloads.
- Local model-path patch prepared: `baselines/DAR/patches/a8002-local-qwen-paths.patch`.
- Arithmetic parser compatibility patch prepared: `baselines/DAR/patches/a8002-arithmetic-escaped-brace-parser.patch`.
- Output directory patch prepared: `baselines/DAR/patches/a8002-respect-out-dir.patch`.
- GSM8K offline JSONL fallback patch prepared: `baselines/DAR/patches/a8002-gsm8k-local-jsonl-fallback.patch`.
- Filter retention history patch prepared: `baselines/DAR/patches/a8002-filter-retention-history.patch`.
- Guarded answer-diversity patch prepared and run in bounded variants: `baselines/DAR/patches/a8002-guarded-answer-diversity.patch`.
- Planned runs should use explicit GPU visibility and timeout wrappers.

## Failures And Fixes

| Issue | Evidence | Fix | Method Behavior Changed? |
| --- | --- | --- | --- |
| Qwen2.5-1.5B non-Instruct smoke produced repeated invalid text and empty parsed answers. | `/data/xuhaoming/yfy/research_workspace/logs/dar_smoke_basic_20260612_174325.log` | use Instruct model for reproduction smoke | model choice changed, method logic unchanged |
| Qwen2.5-7B-Instruct Round 1 answers used escaped braces such as `\\{final answer: 371.75\\}`, causing `evaluate_arithmetics` to parse empty answers. | `/data/xuhaoming/yfy/research_workspace/logs/dar-smoke-qwen25-7b-arith2-20260612_182826.log`; history JSONL under remote DAR `out/history/` | allow optional escaped braces in arithmetic answer regex | evaluation parser changed; communication method unchanged |
| Upstream history and TSV paths ignored `--out_dir` and wrote to repository `out/`. | `src/main.py` path construction | write history and TSV under `args.out_dir` | artifact placement changed; method logic unchanged |
| A800_2 could not reach `huggingface.co` for `openai/gsm8k`, and no dataset cache entry existed. | data-only GSM8K smoke before GPU launch | load project-local MAD-MM processed GSM8K JSONL when available, or use `DAR_GSM8K_JSONL` | data loading changed, method logic unchanged |
| DAR history omitted retained/dropped filter IDs and non-debug mode saved only first 10 samples. | unified trace extraction caveat | `a8002-filter-retention-history.patch` adds per-round `retention_events` and `--save_full_history`; verified on GSM8K5 trace check | trace-only instrumentation |
| DAR `filter_critical` can drop parseable dissenting answers or retain only unparseable answers. | `reports/_archive/20260616-pruned/20260613-guarded-retention-offline-simulation.md` | `a8002-guarded-answer-diversity.patch` adds an optional `--retention_guard answer_diversity` post-filter guard and `--retention_message_mode answer_only` | experimental method variant |

## Caveats

- Existing 100-sample runs cover generated arithmetic and GSM8K, but each uses one seed and one model.
- Matched total-token accounting is available for the full-history DAR variants, but not for every older non-instrumented run.
- Non-debug history stores only the first 10 samples.
- Retained/dropped ID instrumentation is represented by a 5-sample GSM8K diagnostic run and a 100-sample GSM8K `filter_critical` rerun; the rest of the matrix has not been rerun with full history.
- Guarded retention evidence is still one seed/model/GSM8K100 slice and should not be treated as a general method ranking.

## Next Small Check

- Inspect sample `20` from the retention split ablation, then try a harder slice such as MATH50 or MMLU-Pro50 before expanding GSM8K.
