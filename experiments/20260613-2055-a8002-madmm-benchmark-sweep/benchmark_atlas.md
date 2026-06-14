# MAD-MM Benchmark Atlas

Cells are `accuracy / delta_vs_CoT / total_tokens / token_ratio_vs_CoT`.

| Benchmark | Samples | CoT | MAD naive | MAD-MM objective | MAD-MM subjective | Accuracy spread | Result dir |
| --- | ---: | --- | --- | --- | --- | ---: | --- |
| aime24 | 30 | 0.167 / 0.000 / 31,129 / 1.00x | 0.167 / 0.000 / 415,526 / 13.35x | 0.133 / -0.033 / 271,351 / 8.72x | - | 0.033 | `experiments\20260613-2055-a8002-madmm-benchmark-sweep\benchmark_sweep_20260613_205520_aime24_all\qwen2.5-7b\aime24` |
| aime25 | 30 | 0.100 / 0.000 / 30,402 / 1.00x | 0.067 / -0.033 / 398,136 / 13.10x | 0.100 / 0.000 / 264,225 / 8.69x | - | 0.033 | `experiments\20260613-2055-a8002-madmm-benchmark-sweep\benchmark_sweep_20260613_205520_aime25_all\qwen2.5-7b\aime25` |
| math | 50 | 0.460 / 0.000 / 28,790 / 1.00x | 0.600 / +0.140 / 410,691 / 14.27x | 0.660 / +0.200 / 273,177 / 9.49x | - | 0.200 | `experiments\20260613-2055-a8002-madmm-benchmark-sweep\benchmark_sweep_20260613_205520_math_50\qwen2.5-7b\math` |
| mmlu_pro | 50 | 0.260 / 0.000 / 29,046 / 1.00x | 0.360 / +0.100 / 338,428 / 11.65x | 0.340 / +0.080 / 234,132 / 8.06x | - | 0.100 | `experiments\20260613-2055-a8002-madmm-benchmark-sweep\benchmark_sweep_20260613_205520_mmlu_pro_50\qwen2.5-7b\mmlu_pro` |

Caveat: this atlas reports short-run reproduction probes, not benchmark-scale claims.
