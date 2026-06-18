# MAD-MM MATH50 Benchmark Probe

## What We Tried

Switched MAD-MM from the saturated GSM8K short subset to the existing processed MATH benchmark to see whether a harder benchmark exposes communication-method gaps faster.

This run used a small `--sample_count 50` override so the benchmark change could be tested quickly on one GPU. A follow-up run added subjective masking on the same slice.

## Scope

- Method family: MAD-MM
- Model: Qwen2.5-7B-Instruct
- Dataset: MATH, from MAD-MM processed data
- Seed: 41
- Samples: 50
- Agents: 3 for debate methods
- Debate rounds: 2
- Compared methods:
  - CoT baseline
  - MAD naive communication
  - MAD-MM objective masking
  - MAD-MM subjective masking

## Resource Notes

- Machine: A800_2
- GPU: 7
- Timeout wrapper: 75 minutes
- Runtime window: 2026-06-13 18:55 to 19:01 CST
- Subjective addendum window: 2026-06-13 19:35 to 19:39 CST
- GPU 7 was released after each run.

## Code

- Upstream repo: https://github.com/HongduanTian/MAD-MM
- Commit: `f02069add08280b764d059a2f06ca0043aa093e2`
- Required project patch:
  - `baselines/MAD-MM-patches/a8002-local-qwen-and-runtime-overrides.patch`
  - `baselines/MAD-MM-patches/a8002-sample-count-override.patch`
- Launcher:
  - `scripts/run_madmm_math_probe_a8002.sh`

## Environment

- Env path: `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063`
- Model path resolved by MAD-MM local config: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
- Result root: `/data/xuhaoming/yfy/research_workspace/results/mad-mm-benchmark-probe`

## Command

```bash
RUN_LOG=/data/xuhaoming/yfy/research_workspace/logs/madmm_math_probe50_20260613_1855.log \
MAD_MM_GPU_ID=7 \
MAD_MM_MODEL_NAME=qwen2.5-7b \
MAD_MM_DATASET=math \
MAD_MM_SAMPLE_COUNT=50 \
MAD_MM_EXP_NAME=math_probe50 \
MAD_MM_SAVE_PATH=/data/xuhaoming/yfy/research_workspace/results/mad-mm-benchmark-probe \
nohup timeout 75m /data/xuhaoming/yfy/research_workspace/scripts/run_madmm_math_probe_a8002.sh \
  > /data/xuhaoming/yfy/research_workspace/logs/madmm_math_probe50_20260613_1855.outer.log 2>&1 < /dev/null &
```

Subjective addendum:

```bash
timeout 75m python multi_agent_debate.py \
  --model_name qwen2.5-7b \
  --dataset math \
  --seed 41 \
  --gpu_id 7 \
  --save_path /data/xuhaoming/yfy/research_workspace/results/mad-mm-benchmark-probe \
  --exp_name math_probe50 \
  --sample_count 50 \
  --num_agents 3 \
  --max_round 2 \
  --prune_strategy subjective
```

## Remote Artifacts

| Artifact | Path |
| --- | --- |
| Result dir | `/data/xuhaoming/yfy/research_workspace/results/mad-mm-benchmark-probe/math_probe50/qwen2.5-7b/math` |
| Run log | `/data/xuhaoming/yfy/research_workspace/logs/madmm_math_probe50_20260613_1855.log` |
| Outer log | `/data/xuhaoming/yfy/research_workspace/logs/madmm_math_probe50_20260613_1855.outer.log` |
| Subjective run log | `/data/xuhaoming/yfy/research_workspace/logs/madmm_math_subjective_probe50_20260613_1935.log` |
| Subjective outer log | `/data/xuhaoming/yfy/research_workspace/logs/madmm_math_subjective_probe50_20260613_1935.outer.log` |
| Unified trace | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/madmm-qwen25-7b-math50-probe.comm_trace.jsonl` |

Small local copies:

- `cot_seed41.json`
- `mad_3agents_2rounds_seed41.json`
- `mad_objective_3agents_2rounds_seed41.json`
- `mad_subjective_3agents_2rounds_seed41.json`
- `comm_trace_madmm_math50.jsonl`
- `comm_trace_madmm_math50_v11.jsonl`
- `analysis_summary.json`
- `analysis_subjective_addendum.json`
- `run.log`
- `outer.log`
- `madmm_math_subjective_probe50_20260613_1935.log`
- `madmm_math_subjective_probe50_20260613_1935.outer.log`

## Derived Schema v1.1 Trace

Created locally without rerunning the model:

```bash
python scripts/extract_comm_trace_schema.py madmm \
  --run-id 20260613-1855-a8002-madmm-qwen25-7b-math50-probe-v11 \
  --results-dir experiments/_archive/20260616-pruned/20260613-1855-a8002-madmm-qwen25-7b-math50-probe \
  --methods cot mad_naive mad_objective mad_subjective \
  --task-regime math_reasoning \
  --out experiments/_archive/20260616-pruned/20260613-1855-a8002-madmm-qwen25-7b-math50-probe/comm_trace_madmm_math50_v11.jsonl
```

Validation: 200 rows, schema `acr.comm_trace.v1.1`, with method-specific public-state labels:

| Method | Public State Surface | Communication Policy |
| --- | --- | --- |
| `cot` | `none` | `none` |
| `mad_naive` | `full_reasoning` | `broadcast` |
| `mad_objective` | `masked_full_reasoning` | `objective_memory_mask` |
| `mad_subjective` | `masked_full_reasoning` | `subjective_memory_mask` |

Context-event validation:

- `cot`: 0 context events per row;
- `mad_naive`, `mad_objective`, and `mad_subjective`: 1 derived context event per row from `mask_history`.

## What Happened

| Method | Accuracy | Total Tokens | Tokens / CoT | Time |
| --- | ---: | ---: | ---: | ---: |
| CoT | 0.46 | 28,790 | 1.00x | 18.615s |
| MAD naive | 0.60 | 410,691 | 14.27x | 134.913s |
| MAD-MM objective | 0.66 | 273,177 | 9.49x | 122.875s |
| MAD-MM subjective | 0.60 | 494,163 | 17.16x | 228.879s |

Objective masking used `66.5%` of the naive MAD tokens, a `33.5%` reduction, while improving accuracy by 6 points over naive MAD on this probe.

Subjective masking tied naive MAD accuracy, but used `120.3%` of naive MAD tokens and `180.9%` of objective masking tokens.

Trace-normalizer final correctness transitions:

These counts use the local answer normalizer in `scripts/extract_comm_trace_schema.py`. The official accuracy table above comes from MAD-MM's own MATH evaluator.

| Comparison | Stable Right | Right -> Wrong | Wrong -> Right | Stable Wrong |
| --- | ---: | ---: | ---: | ---: |
| MAD naive vs CoT | 26 | 0 | 7 | 17 |
| MAD-MM objective vs CoT | 26 | 0 | 9 | 15 |
| MAD-MM objective vs MAD naive | 33 | 0 | 2 | 15 |
| MAD-MM subjective vs CoT | 25 | 1 | 7 | 17 |
| MAD-MM subjective vs MAD naive | 31 | 2 | 1 | 16 |
| MAD-MM subjective vs MAD-MM objective | 32 | 3 | 0 | 15 |

Objective wrong-to-right IDs versus CoT:

`494`, `570`, `1237`, `1238`, `2821`, `2965`, `2982`, `3707`, `4037`

Objective wrong-to-right IDs versus naive MAD:

`494`, `1237`

## Objective Mask Behavior

| Metric | Value |
| --- | ---: |
| Retention events | 50 |
| Retained memories per sample | 1 for all 50 samples |
| Samples with any correct round-0 agent | 34 |
| Samples dropping at least one correct round-0 agent | 29 |
| Samples dropping all correct round-0 agents | 1 |
| Retained correct agent total | 33 |
| Dropped correct agent total | 52 |

The all-correct-dropped case was `2965`. Interestingly, objective MAD still ended correct on this sample, so it is not a final right-to-wrong case; it is a mechanism warning rather than a direct failure in this run.

## Subjective Mask Behavior

Trace-normalizer counts:

| Metric | Value |
| --- | ---: |
| Retention events | 50 |
| Retained memories total | 128 |
| Dropped memories total | 22 |
| Retained memories per sample | 2.56 average |
| Retention size distribution | 0: 2, 1: 3, 2: 10, 3: 35 |
| Samples with any correct round-0 agent | 34 |
| Samples dropping at least one correct round-0 agent | 1 |
| Samples dropping all correct round-0 agents | 1 |

Compared with the earlier GSM8K subjective run, subjective masking filtered more often here, but it was still the most expensive method and did not improve official accuracy over naive MAD.

## Why This Benchmark Helped

The earlier GSM8K short subset was nearly saturated, so communication variants mostly differed by 1-2 accuracy points. MATH50 immediately produced a wider spread:

- CoT to naive MAD: +14 points
- CoT to objective MAD-MM: +20 points
- naive MAD to objective MAD-MM: +6 points
- naive MAD to subjective MAD-MM: +0 points

This makes MATH a better quick diagnostic benchmark for communication effects than the previous saturated GSM8K slice.

## Caveats

- One seed, one model, first 50 sampled examples.
- This is a probe, not a paper-style benchmark result.
- The MATH probe is not directly apples-to-apples with the earlier GSM8K run because the model and dataset differ.
- Objective pruning looked useful here, but the trace still shows frequent dropping of correct first-round memories.
- Trace-level transition counts use a local normalizer and should not be mixed with MAD-MM official MATH accuracy without this caveat.

## Loose Threads

- Try `mmlu_pro` with the same `--sample_count` patch if the goal is to stress semantic/domain reasoning rather than math derivations.
- Inspect subjective judge prompts for zero-retention samples `843` and `1237`, plus dropped-correct sample `570`.
