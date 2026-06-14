# MAD-MM Benchmark Atlas

## What We Tried

Ran a compact benchmark sweep for MAD-MM on A800_2 using Qwen2.5-7B-Instruct, seed 41, and one GPU.

Benchmarks: MATH50, MMLU-Pro50, AIME24 full local set, AIME25 full local set.

Methods: CoT, MAD naive, MAD-MM objective.

Run record: `experiments/20260613-2055-a8002-madmm-benchmark-sweep/`.

## What Happened

| Benchmark | CoT | MAD naive | MAD-MM objective |
| --- | ---: | ---: | ---: |
| MATH50 | 0.46 | 0.60 | 0.66 |
| MMLU-Pro50 | 0.26 | 0.36 | 0.34 |
| AIME24 | 0.167 | 0.167 | 0.133 |
| AIME25 | 0.100 | 0.067 | 0.100 |

The important result is not that one method wins. The important result is that method ranking changes by benchmark.

## Things Noticed

- GSM8K is a weak place to build confidence because it is close to saturated in our current runs.
- MATH and MMLU-Pro are better quick diagnostic benchmarks for communication effects.
- AIME is a hard probe where multi-agent communication can cost 8x-13x tokens without improving accuracy.
- The objective mask is not a universal improvement: it helps on MATH, trails naive on MMLU-Pro, and hurts AIME24 in this run.

## Caveats

This is one seed, one model, and short slices for MATH/MMLU-Pro. It should change our workflow, not become a performance claim.

The next discussion should start from a benchmark atlas table, then inspect traces only where a pattern persists across benchmarks or repeats.
