# PerspectiveGap Stratified20 Qwen2.5 Summary

## qwen2.5-7b
- strict_pass: 0/40
- coverage: 0.4426
- precision: 0.7862
- distractor_leak_per_eval: 0.0500
- net_match_score_mean: 0.0452
- counts: tp=239, fp=65, fn=301, leak=2, parse_error=0

| role_count | n | coverage | precision | leak/eval | tp | fp | fn |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 8 | 0.500 | 0.549 | 0.125 | 28 | 23 | 28 |
| 3 | 8 | 0.487 | 0.740 | 0.125 | 37 | 13 | 39 |
| 4 | 8 | 0.464 | 0.981 | 0.000 | 52 | 1 | 60 |
| 5 | 8 | 0.401 | 0.735 | 0.000 | 61 | 22 | 91 |
| 6 | 8 | 0.424 | 0.910 | 0.000 | 61 | 6 | 83 |

## qwen2.5-14b
- strict_pass: 0/40
- coverage: 0.6148
- precision: 0.8078
- distractor_leak_per_eval: 0.4500
- net_match_score_mean: 0.2285
- counts: tp=332, fp=79, fn=208, leak=18, parse_error=0

| role_count | n | coverage | precision | leak/eval | tp | fp | fn |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 8 | 0.768 | 0.796 | 0.750 | 43 | 11 | 13 |
| 3 | 8 | 0.842 | 0.744 | 0.875 | 64 | 22 | 12 |
| 4 | 8 | 0.643 | 0.986 | 0.125 | 72 | 1 | 40 |
| 5 | 8 | 0.586 | 0.795 | 0.250 | 89 | 23 | 63 |
| 6 | 8 | 0.444 | 0.744 | 0.250 | 64 | 22 | 80 |

## Paired Differences

- coverage_delta_14b_minus_7b: 0.1722
- precision_delta_14b_minus_7b: 0.0216
- leak_delta_14b_minus_7b: 0.4000
