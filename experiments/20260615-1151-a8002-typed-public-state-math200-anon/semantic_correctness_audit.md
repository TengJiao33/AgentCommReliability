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
| changed_known | 29 |
| same_known | 521 |
| semantic_unknown | 99 |

## All Source Cases

| Condition | Metric | Count | Rate | Wilson 95% |
| --- | --- | ---: | ---: | --- |
| no_peer | post_correct / records | 37/59 | 0.627 | [0.500, 0.739] |
| no_peer | unparseable / records | 13/59 | 0.220 | [0.134, 0.341] |
| wrong_answer_only | right_to_wrong / pre_correct | 1/37 | 0.027 | [0.005, 0.138] |
| wrong_answer_only | stable_right / pre_correct | 36/37 | 0.973 | [0.862, 0.995] |
| wrong_answer_only | post_correct / records | 38/59 | 0.644 | [0.517, 0.754] |
| wrong_answer_only | unparseable / records | 8/59 | 0.136 | [0.070, 0.245] |
| wrong_rationale | right_to_wrong / pre_correct | 9/37 | 0.243 | [0.134, 0.401] |
| wrong_rationale | stable_right / pre_correct | 27/37 | 0.730 | [0.570, 0.846] |
| wrong_rationale | post_correct / records | 27/59 | 0.458 | [0.337, 0.583] |
| wrong_rationale | unparseable / records | 8/59 | 0.136 | [0.070, 0.245] |
| wrong_redacted_rationale | right_to_wrong / pre_correct | 4/37 | 0.108 | [0.043, 0.247] |
| wrong_redacted_rationale | stable_right / pre_correct | 32/37 | 0.865 | [0.720, 0.941] |
| wrong_redacted_rationale | post_correct / records | 32/59 | 0.542 | [0.417, 0.663] |
| wrong_redacted_rationale | unparseable / records | 10/59 | 0.169 | [0.095, 0.285] |
| wrong_equation_surface | right_to_wrong / pre_correct | 3/37 | 0.081 | [0.028, 0.213] |
| wrong_equation_surface | stable_right / pre_correct | 34/37 | 0.919 | [0.787, 0.972] |
| wrong_equation_surface | post_correct / records | 35/59 | 0.593 | [0.466, 0.709] |
| wrong_equation_surface | unparseable / records | 11/59 | 0.186 | [0.107, 0.304] |
| wrong_typed_public_state | right_to_wrong / pre_correct | 3/37 | 0.081 | [0.028, 0.213] |
| wrong_typed_public_state | stable_right / pre_correct | 34/37 | 0.919 | [0.787, 0.972] |
| wrong_typed_public_state | post_correct / records | 35/59 | 0.593 | [0.466, 0.709] |
| wrong_typed_public_state | unparseable / records | 12/59 | 0.203 | [0.120, 0.323] |
| correct_answer_only | wrong_to_right / pre_wrong | 2/9 | 0.222 | [0.063, 0.547] |
| correct_answer_only | post_correct / records | 44/59 | 0.746 | [0.622, 0.839] |
| correct_answer_only | unparseable / records | 6/59 | 0.102 | [0.047, 0.205] |
| correct_rationale | wrong_to_right / pre_wrong | 5/9 | 0.556 | [0.267, 0.811] |
| correct_rationale | post_correct / records | 49/59 | 0.831 | [0.715, 0.905] |
| correct_rationale | unparseable / records | 3/59 | 0.051 | [0.017, 0.139] |
| correct_redacted_rationale | wrong_to_right / pre_wrong | 4/9 | 0.444 | [0.189, 0.733] |
| correct_redacted_rationale | post_correct / records | 47/59 | 0.797 | [0.677, 0.880] |
| correct_redacted_rationale | unparseable / records | 5/59 | 0.085 | [0.037, 0.184] |
| correct_equation_surface | wrong_to_right / pre_wrong | 1/9 | 0.111 | [0.020, 0.435] |
| correct_equation_surface | post_correct / records | 37/59 | 0.627 | [0.500, 0.739] |
| correct_equation_surface | unparseable / records | 11/59 | 0.186 | [0.107, 0.304] |
| correct_typed_public_state | wrong_to_right / pre_wrong | 1/9 | 0.111 | [0.020, 0.435] |
| correct_typed_public_state | post_correct / records | 38/59 | 0.644 | [0.517, 0.754] |
| correct_typed_public_state | unparseable / records | 12/59 | 0.203 | [0.120, 0.323] |

## All Source Cases Paired Correctness

| A | B | Known Pairs | Unknown Pairs | A-only | B-only | Delta A-B | Exact p |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| wrong_typed_public_state | wrong_rationale | 45 | 14 | 9 | 2 | +0.156 | 0.0654 |
| wrong_typed_public_state | wrong_redacted_rationale | 45 | 14 | 4 | 2 | +0.044 | 0.6875 |
| wrong_typed_public_state | wrong_equation_surface | 46 | 13 | 1 | 1 | +0.000 | 1.0000 |
| wrong_typed_public_state | wrong_answer_only | 47 | 12 | 2 | 3 | -0.021 | 1.0000 |
| correct_typed_public_state | correct_rationale | 47 | 12 | 0 | 4 | -0.085 | 0.1250 |
| correct_typed_public_state | correct_redacted_rationale | 47 | 12 | 0 | 3 | -0.064 | 0.2500 |
| correct_typed_public_state | correct_equation_surface | 47 | 12 | 2 | 1 | +0.021 | 1.0000 |
| correct_redacted_rationale | correct_rationale | 54 | 5 | 1 | 2 | -0.019 | 1.0000 |

## Source-Label-Reliable Cases

| Condition | Metric | Count | Rate | Wilson 95% |
| --- | --- | ---: | ---: | --- |
| no_peer | post_correct / records | 32/47 | 0.681 | [0.538, 0.796] |
| no_peer | unparseable / records | 8/47 | 0.170 | [0.089, 0.301] |
| wrong_answer_only | right_to_wrong / pre_correct | 1/32 | 0.031 | [0.006, 0.157] |
| wrong_answer_only | stable_right / pre_correct | 31/32 | 0.969 | [0.843, 0.994] |
| wrong_answer_only | post_correct / records | 33/47 | 0.702 | [0.560, 0.813] |
| wrong_answer_only | unparseable / records | 3/47 | 0.064 | [0.022, 0.172] |
| wrong_rationale | right_to_wrong / pre_correct | 9/32 | 0.281 | [0.156, 0.454] |
| wrong_rationale | stable_right / pre_correct | 22/32 | 0.688 | [0.514, 0.820] |
| wrong_rationale | post_correct / records | 22/47 | 0.468 | [0.333, 0.608] |
| wrong_rationale | unparseable / records | 3/47 | 0.064 | [0.022, 0.172] |
| wrong_redacted_rationale | right_to_wrong / pre_correct | 4/32 | 0.125 | [0.050, 0.281] |
| wrong_redacted_rationale | stable_right / pre_correct | 28/32 | 0.875 | [0.719, 0.950] |
| wrong_redacted_rationale | post_correct / records | 28/47 | 0.596 | [0.453, 0.724] |
| wrong_redacted_rationale | unparseable / records | 4/47 | 0.085 | [0.034, 0.199] |
| wrong_equation_surface | right_to_wrong / pre_correct | 3/32 | 0.094 | [0.032, 0.242] |
| wrong_equation_surface | stable_right / pre_correct | 29/32 | 0.906 | [0.758, 0.968] |
| wrong_equation_surface | post_correct / records | 30/47 | 0.638 | [0.495, 0.760] |
| wrong_equation_surface | unparseable / records | 6/47 | 0.128 | [0.060, 0.252] |
| wrong_typed_public_state | right_to_wrong / pre_correct | 3/32 | 0.094 | [0.032, 0.242] |
| wrong_typed_public_state | stable_right / pre_correct | 29/32 | 0.906 | [0.758, 0.968] |
| wrong_typed_public_state | post_correct / records | 30/47 | 0.638 | [0.495, 0.760] |
| wrong_typed_public_state | unparseable / records | 7/47 | 0.149 | [0.074, 0.277] |
| correct_answer_only | wrong_to_right / pre_wrong | 2/7 | 0.286 | [0.082, 0.641] |
| correct_answer_only | post_correct / records | 38/47 | 0.809 | [0.675, 0.896] |
| correct_answer_only | unparseable / records | 2/47 | 0.043 | [0.012, 0.142] |
| correct_rationale | wrong_to_right / pre_wrong | 5/7 | 0.714 | [0.359, 0.918] |
| correct_rationale | post_correct / records | 44/47 | 0.936 | [0.828, 0.978] |
| correct_rationale | unparseable / records | 0/47 | 0.000 | [0.000, 0.076] |
| correct_redacted_rationale | wrong_to_right / pre_wrong | 4/7 | 0.571 | [0.250, 0.842] |
| correct_redacted_rationale | post_correct / records | 42/47 | 0.894 | [0.774, 0.954] |
| correct_redacted_rationale | unparseable / records | 2/47 | 0.043 | [0.012, 0.142] |
| correct_equation_surface | wrong_to_right / pre_wrong | 1/7 | 0.143 | [0.026, 0.513] |
| correct_equation_surface | post_correct / records | 32/47 | 0.681 | [0.538, 0.796] |
| correct_equation_surface | unparseable / records | 7/47 | 0.149 | [0.074, 0.277] |
| correct_typed_public_state | wrong_to_right / pre_wrong | 1/7 | 0.143 | [0.026, 0.513] |
| correct_typed_public_state | post_correct / records | 33/47 | 0.702 | [0.560, 0.813] |
| correct_typed_public_state | unparseable / records | 8/47 | 0.170 | [0.089, 0.301] |

## Source-Label-Reliable Paired Correctness

| A | B | Known Pairs | Unknown Pairs | A-only | B-only | Delta A-B | Exact p |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| wrong_typed_public_state | wrong_rationale | 38 | 9 | 9 | 2 | +0.184 | 0.0654 |
| wrong_typed_public_state | wrong_redacted_rationale | 39 | 8 | 4 | 2 | +0.051 | 0.6875 |
| wrong_typed_public_state | wrong_equation_surface | 39 | 8 | 1 | 1 | +0.000 | 1.0000 |
| wrong_typed_public_state | wrong_answer_only | 40 | 7 | 2 | 3 | -0.025 | 1.0000 |
| correct_typed_public_state | correct_rationale | 39 | 8 | 0 | 4 | -0.103 | 0.1250 |
| correct_typed_public_state | correct_redacted_rationale | 39 | 8 | 0 | 3 | -0.077 | 0.2500 |
| correct_typed_public_state | correct_equation_surface | 39 | 8 | 2 | 1 | +0.026 | 1.0000 |
| correct_redacted_rationale | correct_rationale | 45 | 2 | 1 | 2 | -0.022 | 1.0000 |

## Notes

- `unparseable / records` means semantic unknown here, not necessarily missing text.
- Source-label-reliable cases are those where the saved `correct_peer` response is semantically correct and the saved `wrong_peer` response is semantically wrong against the original boxed answer.
- Peer-answer adoption is intentionally not recomputed here because the saved peer answer fields came from the older numeric parser.
- Cases with `unknown_semantic_parse` should be inspected before becoming claim-bearing evidence.
