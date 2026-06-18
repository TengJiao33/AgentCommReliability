# MAD-MM Short Subset First Insights

## Short Answer

This run is not our idea implementation. It is a contrastive reproduction slice used to expose where multi-agent communication helps, where it is wasteful, and where masking fails.

The first useful signal is already visible: communication can rescue some CoT failures, but the current masking strategies are crude along different axes. Objective masking is cheap and aggressive but loses at least one correct answer. Subjective masking is expensive and mostly keeps everything, behaving like costly naive debate on this subset.

## Scope

- Model: `qwen2.5-14b`
- Dataset: `gsm8k`
- Seed: `41`
- Samples: `100`
- Methods: CoT, MAD naive, MAD-MM objective masking, MAD-MM subjective masking
- Evidence level: short-subset evidence only

## Metric Snapshot

| method | correct | accuracy | tokens | calls | note |
| --- | ---: | ---: | ---: | ---: | --- |
| CoT | 94/100 | 0.94 | 37,990 | 1 | cheapest baseline |
| MAD naive | 96/100 | 0.96 | 441,846 | 6 | +2 correct over CoT, high token cost |
| MAD-MM objective | 95/100 | 0.95 | 304,287 | 6 | lower cost, one regression |
| MAD-MM subjective | 96/100 | 0.96 | 600,499 | 106 | same accuracy as naive, much higher cost |

Marginal cost versus CoT:

| method | extra correct | extra tokens | tokens per extra correct |
| --- | ---: | ---: | ---: |
| MAD naive | 2 | 403,856 | 201,928 |
| MAD-MM objective | 1 | 266,297 | 266,297 |
| MAD-MM subjective | 2 | 562,509 | 281,254.5 |

## Case Signals

Communication rescued two CoT failures:

- `id=335`: CoT predicted `250`; all debate variants predicted `310`, which matches the ground truth.
- `id=562`: CoT predicted `140`; all debate variants predicted `82`, which matches the ground truth.

Objective masking introduced one regression:

- `id=214`: CoT, MAD naive, and subjective masking predicted `8`; objective masking predicted `24`.

## Masking Behavior

| method | mask entries | kept | keep rate |
| --- | ---: | ---: | ---: |
| MAD naive | 300 | 300 | 1.000 |
| MAD-MM objective | 300 | 100 | 0.333 |
| MAD-MM subjective | 300 | 296 | 0.987 |

This is the most important early observation:

- Objective masking is a strong compressor: it keeps one of three previous memories per sample.
- Subjective masking is almost a no-op on this subset: it keeps nearly all memories while adding 100 extra model calls.

## Working Hypotheses

1. The main research opportunity is not "debate helps"; it is deciding when communication is worth paying for.
2. Subjective LLM-based memory masking may be too permissive on simple GSM8K-style problems, producing high cost with little filtering.
3. Objective masking may be useful as a cheap communication compressor, but it needs a risk-aware fallback when pruning removes stabilizing context.
4. The next idea should probably be a reliability controller: communicate only for uncertain cases, compress aggressively when agents agree, and fall back when mask confidence is low.

## Next Non-GPU Work

Before launching more runs, inspect trace-level cases:

- `335` and `562`: why did communication rescue CoT?
- `214`: why did objective masking break a problem that every other method solved?
- subjective masks: why did the judge keep 296/300 memories?

Raw summary:

- `experiments/_archive/20260616-pruned/20260612-a8002-madmm-qwen25-14b-gsm8k-short-subset/analysis_short_subset_summary.json`
