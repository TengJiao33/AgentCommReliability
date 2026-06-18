# MATH Semantic Correctness Audit

This audit re-extracts raw final-answer strings from saved peer-exposure outputs and compares them to original MATH boxed answers with conservative symbolic checks. It does not run the model again.

## Source Surface

- Source cases: `59`
- Records: `649`
- Source-label-reliable cases: `47`
- Source-label-unknown/unreliable cases: `12`

## Numeric-vs-Semantic Label Changes

| Bucket | Records |
| --- | ---: |
| changed_known | 27 |
| same_known | 529 |
| semantic_unknown | 93 |

## All Source Cases

| Condition | Metric | Count | Rate | Wilson 95% |
| --- | --- | ---: | ---: | --- |
| no_peer | post_correct / records | 37/59 | 0.627 | [0.500, 0.739] |
| no_peer | unparseable / records | 13/59 | 0.220 | [0.134, 0.341] |
| wrong_answer_only | right_to_wrong / pre_correct | 1/37 | 0.027 | [0.005, 0.138] |
| wrong_answer_only | stable_right / pre_correct | 36/37 | 0.973 | [0.862, 0.995] |
| wrong_answer_only | post_correct / records | 38/59 | 0.644 | [0.517, 0.754] |
| wrong_answer_only | unparseable / records | 9/59 | 0.153 | [0.082, 0.265] |
| wrong_rationale | right_to_wrong / pre_correct | 9/37 | 0.243 | [0.134, 0.401] |
| wrong_rationale | stable_right / pre_correct | 28/37 | 0.757 | [0.599, 0.866] |
| wrong_rationale | post_correct / records | 28/59 | 0.475 | [0.353, 0.600] |
| wrong_rationale | unparseable / records | 5/59 | 0.085 | [0.037, 0.184] |
| wrong_redacted_rationale | right_to_wrong / pre_correct | 5/37 | 0.135 | [0.059, 0.280] |
| wrong_redacted_rationale | stable_right / pre_correct | 32/37 | 0.865 | [0.720, 0.941] |
| wrong_redacted_rationale | post_correct / records | 32/59 | 0.542 | [0.417, 0.663] |
| wrong_redacted_rationale | unparseable / records | 4/59 | 0.068 | [0.027, 0.162] |
| wrong_equation_surface | right_to_wrong / pre_correct | 1/37 | 0.027 | [0.005, 0.138] |
| wrong_equation_surface | stable_right / pre_correct | 36/37 | 0.973 | [0.862, 0.995] |
| wrong_equation_surface | post_correct / records | 36/59 | 0.610 | [0.483, 0.724] |
| wrong_equation_surface | unparseable / records | 11/59 | 0.186 | [0.107, 0.304] |
| wrong_typed_public_state | right_to_wrong / pre_correct | 3/37 | 0.081 | [0.028, 0.213] |
| wrong_typed_public_state | stable_right / pre_correct | 34/37 | 0.919 | [0.787, 0.972] |
| wrong_typed_public_state | post_correct / records | 35/59 | 0.593 | [0.466, 0.709] |
| wrong_typed_public_state | unparseable / records | 12/59 | 0.203 | [0.120, 0.323] |
| correct_answer_only | wrong_to_right / pre_wrong | 3/9 | 0.333 | [0.121, 0.646] |
| correct_answer_only | post_correct / records | 43/59 | 0.729 | [0.604, 0.826] |
| correct_answer_only | unparseable / records | 7/59 | 0.119 | [0.059, 0.225] |
| correct_rationale | wrong_to_right / pre_wrong | 3/9 | 0.333 | [0.121, 0.646] |
| correct_rationale | post_correct / records | 47/59 | 0.797 | [0.677, 0.880] |
| correct_rationale | unparseable / records | 3/59 | 0.051 | [0.017, 0.139] |
| correct_redacted_rationale | wrong_to_right / pre_wrong | 3/9 | 0.333 | [0.121, 0.646] |
| correct_redacted_rationale | post_correct / records | 44/59 | 0.746 | [0.622, 0.839] |
| correct_redacted_rationale | unparseable / records | 7/59 | 0.119 | [0.059, 0.225] |
| correct_equation_surface | wrong_to_right / pre_wrong | 0/9 | 0.000 | [0.000, 0.299] |
| correct_equation_surface | post_correct / records | 36/59 | 0.610 | [0.483, 0.724] |
| correct_equation_surface | unparseable / records | 10/59 | 0.169 | [0.095, 0.285] |
| correct_typed_public_state | wrong_to_right / pre_wrong | 1/9 | 0.111 | [0.020, 0.435] |
| correct_typed_public_state | post_correct / records | 38/59 | 0.644 | [0.517, 0.754] |
| correct_typed_public_state | unparseable / records | 12/59 | 0.203 | [0.120, 0.323] |

## All Source Cases Paired Correctness

| A | B | Known Pairs | Unknown Pairs | A-only | B-only | Delta A-B | Exact p |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| wrong_typed_public_state | wrong_rationale | 47 | 12 | 10 | 3 | +0.149 | 0.0923 |
| wrong_typed_public_state | wrong_redacted_rationale | 47 | 12 | 5 | 2 | +0.064 | 0.4531 |
| wrong_typed_public_state | wrong_equation_surface | 46 | 13 | 1 | 2 | -0.022 | 1.0000 |
| wrong_typed_public_state | wrong_answer_only | 46 | 13 | 2 | 3 | -0.022 | 1.0000 |
| correct_typed_public_state | correct_rationale | 47 | 12 | 1 | 3 | -0.043 | 0.6250 |
| correct_typed_public_state | correct_redacted_rationale | 46 | 13 | 0 | 1 | -0.022 | 1.0000 |
| correct_typed_public_state | correct_equation_surface | 47 | 12 | 2 | 0 | +0.043 | 0.5000 |
| correct_redacted_rationale | correct_rationale | 52 | 7 | 1 | 1 | +0.000 | 1.0000 |

## Source-Label-Reliable Cases

| Condition | Metric | Count | Rate | Wilson 95% |
| --- | --- | ---: | ---: | --- |
| no_peer | post_correct / records | 32/47 | 0.681 | [0.538, 0.796] |
| no_peer | unparseable / records | 8/47 | 0.170 | [0.089, 0.301] |
| wrong_answer_only | right_to_wrong / pre_correct | 1/32 | 0.031 | [0.006, 0.157] |
| wrong_answer_only | stable_right / pre_correct | 31/32 | 0.969 | [0.843, 0.994] |
| wrong_answer_only | post_correct / records | 33/47 | 0.702 | [0.560, 0.813] |
| wrong_answer_only | unparseable / records | 4/47 | 0.085 | [0.034, 0.199] |
| wrong_rationale | right_to_wrong / pre_correct | 9/32 | 0.281 | [0.156, 0.454] |
| wrong_rationale | stable_right / pre_correct | 23/32 | 0.719 | [0.546, 0.844] |
| wrong_rationale | post_correct / records | 23/47 | 0.489 | [0.353, 0.628] |
| wrong_rationale | unparseable / records | 1/47 | 0.021 | [0.004, 0.111] |
| wrong_redacted_rationale | right_to_wrong / pre_correct | 5/32 | 0.156 | [0.069, 0.318] |
| wrong_redacted_rationale | stable_right / pre_correct | 27/32 | 0.844 | [0.682, 0.931] |
| wrong_redacted_rationale | post_correct / records | 27/47 | 0.574 | [0.433, 0.705] |
| wrong_redacted_rationale | unparseable / records | 1/47 | 0.021 | [0.004, 0.111] |
| wrong_equation_surface | right_to_wrong / pre_correct | 1/32 | 0.031 | [0.006, 0.157] |
| wrong_equation_surface | stable_right / pre_correct | 31/32 | 0.969 | [0.843, 0.994] |
| wrong_equation_surface | post_correct / records | 31/47 | 0.660 | [0.517, 0.778] |
| wrong_equation_surface | unparseable / records | 6/47 | 0.128 | [0.060, 0.252] |
| wrong_typed_public_state | right_to_wrong / pre_correct | 3/32 | 0.094 | [0.032, 0.242] |
| wrong_typed_public_state | stable_right / pre_correct | 29/32 | 0.906 | [0.758, 0.968] |
| wrong_typed_public_state | post_correct / records | 30/47 | 0.638 | [0.495, 0.760] |
| wrong_typed_public_state | unparseable / records | 7/47 | 0.149 | [0.074, 0.277] |
| correct_answer_only | wrong_to_right / pre_wrong | 3/7 | 0.429 | [0.158, 0.750] |
| correct_answer_only | post_correct / records | 38/47 | 0.809 | [0.675, 0.896] |
| correct_answer_only | unparseable / records | 2/47 | 0.043 | [0.012, 0.142] |
| correct_rationale | wrong_to_right / pre_wrong | 3/7 | 0.429 | [0.158, 0.750] |
| correct_rationale | post_correct / records | 42/47 | 0.894 | [0.774, 0.954] |
| correct_rationale | unparseable / records | 0/47 | 0.000 | [0.000, 0.076] |
| correct_redacted_rationale | wrong_to_right / pre_wrong | 3/7 | 0.429 | [0.158, 0.750] |
| correct_redacted_rationale | post_correct / records | 39/47 | 0.830 | [0.699, 0.911] |
| correct_redacted_rationale | unparseable / records | 4/47 | 0.085 | [0.034, 0.199] |
| correct_equation_surface | wrong_to_right / pre_wrong | 0/7 | 0.000 | [0.000, 0.354] |
| correct_equation_surface | post_correct / records | 31/47 | 0.660 | [0.517, 0.778] |
| correct_equation_surface | unparseable / records | 6/47 | 0.128 | [0.060, 0.252] |
| correct_typed_public_state | wrong_to_right / pre_wrong | 1/7 | 0.143 | [0.026, 0.513] |
| correct_typed_public_state | post_correct / records | 33/47 | 0.702 | [0.560, 0.813] |
| correct_typed_public_state | unparseable / records | 8/47 | 0.170 | [0.089, 0.301] |

## Source-Label-Reliable Paired Correctness

| A | B | Known Pairs | Unknown Pairs | A-only | B-only | Delta A-B | Exact p |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| wrong_typed_public_state | wrong_rationale | 40 | 7 | 10 | 3 | +0.175 | 0.0923 |
| wrong_typed_public_state | wrong_redacted_rationale | 40 | 7 | 5 | 2 | +0.075 | 0.4531 |
| wrong_typed_public_state | wrong_equation_surface | 39 | 8 | 1 | 2 | -0.026 | 1.0000 |
| wrong_typed_public_state | wrong_answer_only | 39 | 8 | 2 | 3 | -0.026 | 1.0000 |
| correct_typed_public_state | correct_rationale | 39 | 8 | 1 | 3 | -0.051 | 0.6250 |
| correct_typed_public_state | correct_redacted_rationale | 38 | 9 | 0 | 1 | -0.026 | 1.0000 |
| correct_typed_public_state | correct_equation_surface | 39 | 8 | 2 | 0 | +0.051 | 0.5000 |
| correct_redacted_rationale | correct_rationale | 43 | 4 | 1 | 1 | +0.000 | 1.0000 |

## Notes

- `unparseable / records` means semantic unknown here, not necessarily missing text.
- Source-label-reliable cases are those where the saved `correct_peer` response is semantically correct and the saved `wrong_peer` response is semantically wrong against the original boxed answer.
- Peer-answer adoption is intentionally not recomputed here because the saved peer answer fields came from the older numeric parser.
- Cases with `unknown_semantic_parse` should be inspected before becoming claim-bearing evidence.
