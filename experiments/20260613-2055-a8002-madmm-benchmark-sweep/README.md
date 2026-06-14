# MAD-MM Benchmark Sweep

## What We Tried

Ran a small benchmark-first MAD-MM sweep on A800_2 after the GSM8K/DAR guarded-retention discussion raised a noise concern.

- Machine: A800_2
- Model: Qwen2.5-7B-Instruct via local vLLM
- Seed: 41
- GPU: 7
- Run window: 2026-06-13 20:55:20 to 21:23:27 CST
- Methods: CoT, MAD naive, MAD-MM objective
- Benchmarks:
  - MATH, 50 samples
  - MMLU-Pro, 50 samples
  - AIME24, full local set of 30 samples
  - AIME25, full local set of 30 samples

Launcher:

```bash
bash /data/xuhaoming/yfy/research_workspace/scripts/run_madmm_benchmark_sweep_a8002.sh
```

Local launcher source:

```text
scripts/run_madmm_benchmark_sweep_a8002.sh
```

## Official Accuracy Atlas

Cells are `accuracy / delta_vs_CoT / total_tokens / token_ratio_vs_CoT`.

| Benchmark | Samples | CoT | MAD naive | MAD-MM objective | Accuracy spread |
| --- | ---: | --- | --- | --- | ---: |
| MATH | 50 | 0.460 / 0.000 / 28,790 / 1.00x | 0.600 / +0.140 / 410,691 / 14.27x | 0.660 / +0.200 / 273,177 / 9.49x | 0.200 |
| MMLU-Pro | 50 | 0.260 / 0.000 / 29,046 / 1.00x | 0.360 / +0.100 / 338,428 / 11.65x | 0.340 / +0.080 / 234,132 / 8.06x | 0.100 |
| AIME24 | 30 | 0.167 / 0.000 / 31,129 / 1.00x | 0.167 / 0.000 / 415,526 / 13.35x | 0.133 / -0.033 / 271,351 / 8.72x | 0.033 |
| AIME25 | 30 | 0.100 / 0.000 / 30,402 / 1.00x | 0.067 / -0.033 / 398,136 / 13.10x | 0.100 / 0.000 / 264,225 / 8.69x | 0.033 |

Generated atlas:

```text
benchmark_atlas.md
analysis_summary.json
```

## Trace Summary

Unified traces were extracted for each benchmark.

| Benchmark | Rows | Local trace |
| --- | ---: | --- |
| MATH50 | 150 | `madmm-benchmark-sweep-20260613_205520-math-50.comm_trace.jsonl` |
| MMLU-Pro50 | 150 | `madmm-benchmark-sweep-20260613_205520-mmlu_pro-50.comm_trace.jsonl` |
| AIME24 | 90 | `madmm-benchmark-sweep-20260613_205520-aime24-all.comm_trace.jsonl` |
| AIME25 | 90 | `madmm-benchmark-sweep-20260613_205520-aime25-all.comm_trace.jsonl` |

Remote traces:

```text
/data/xuhaoming/yfy/research_workspace/results/unified-traces/madmm-benchmark-sweep-20260613_205520-math-50.comm_trace.jsonl
/data/xuhaoming/yfy/research_workspace/results/unified-traces/madmm-benchmark-sweep-20260613_205520-mmlu_pro-50.comm_trace.jsonl
/data/xuhaoming/yfy/research_workspace/results/unified-traces/madmm-benchmark-sweep-20260613_205520-aime24-all.comm_trace.jsonl
/data/xuhaoming/yfy/research_workspace/results/unified-traces/madmm-benchmark-sweep-20260613_205520-aime25-all.comm_trace.jsonl
```

Trace-level transition summary is saved in:

```text
trace_summary.json
```

## Things Noticed

- MATH and MMLU-Pro expose much larger method gaps than the saturated GSM8K slices.
- Method ranking is benchmark-dependent: objective is best on MATH, naive is slightly best on MMLU-Pro, and AIME does not benefit from multi-agent debate in this setup.
- AIME makes the cost/benefit picture harsh: 8x-13x token cost produced no gain and sometimes a regression.
- MMLU-Pro produced many upstream parse warnings before the trace fix. The official evaluator accuracy is the aggregate source of truth; the trace extractor now compares textual multiple-choice labels case-insensitively.

## Caveats

- This is a short-run atlas, not benchmark-scale evidence.
- There is only one seed and one model.
- MATH and MMLU-Pro use 50-sample slices; AIME24/AIME25 use the full local 30-question files.
- MAD-MM reloads the model per method, so wall-clock cost is not optimized.

## Next Useful Checks

- Add at least one repeated seed for MATH50 and MMLU-Pro50 before discussing method superiority.
- Treat GSM8K improvements as trace observations unless they survive a harder benchmark.
- If testing DAR guarded retention further, port the intervention to a benchmark with visible spread rather than expanding GSM8K first.
