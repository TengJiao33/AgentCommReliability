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
| same_known | 527 |
| semantic_unknown | 93 |

## All Source Cases

| Condition | Metric | Count | Rate | Wilson 95% |
| --- | --- | ---: | ---: | --- |
| no_peer | post_correct / records | 37/59 | 0.627 | [0.500, 0.739] |
| no_peer | unparseable / records | 13/59 | 0.220 | [0.134, 0.341] |
| wrong_answer_only | right_to_wrong / pre_correct | 2/37 | 0.054 | [0.015, 0.177] |
| wrong_answer_only | stable_right / pre_correct | 34/37 | 0.919 | [0.787, 0.972] |
| wrong_answer_only | post_correct / records | 36/59 | 0.610 | [0.483, 0.724] |
| wrong_answer_only | unparseable / records | 8/59 | 0.136 | [0.070, 0.245] |
| wrong_rationale | right_to_wrong / pre_correct | 8/37 | 0.216 | [0.114, 0.372] |
| wrong_rationale | stable_right / pre_correct | 29/37 | 0.784 | [0.628, 0.886] |
| wrong_rationale | post_correct / records | 29/59 | 0.492 | [0.368, 0.616] |
| wrong_rationale | unparseable / records | 7/59 | 0.119 | [0.059, 0.225] |
| wrong_redacted_rationale | right_to_wrong / pre_correct | 5/37 | 0.135 | [0.059, 0.280] |
| wrong_redacted_rationale | stable_right / pre_correct | 32/37 | 0.865 | [0.720, 0.941] |
| wrong_redacted_rationale | post_correct / records | 34/59 | 0.576 | [0.449, 0.694] |
| wrong_redacted_rationale | unparseable / records | 5/59 | 0.085 | [0.037, 0.184] |
| wrong_equation_surface | right_to_wrong / pre_correct | 3/37 | 0.081 | [0.028, 0.213] |
| wrong_equation_surface | stable_right / pre_correct | 34/37 | 0.919 | [0.787, 0.972] |
| wrong_equation_surface | post_correct / records | 35/59 | 0.593 | [0.466, 0.709] |
| wrong_equation_surface | unparseable / records | 9/59 | 0.153 | [0.082, 0.265] |
| wrong_typed_public_state | right_to_wrong / pre_correct | 3/37 | 0.081 | [0.028, 0.213] |
| wrong_typed_public_state | stable_right / pre_correct | 34/37 | 0.919 | [0.787, 0.972] |
| wrong_typed_public_state | post_correct / records | 35/59 | 0.593 | [0.466, 0.709] |
| wrong_typed_public_state | unparseable / records | 11/59 | 0.186 | [0.107, 0.304] |
| correct_answer_only | wrong_to_right / pre_wrong | 2/9 | 0.222 | [0.063, 0.547] |
| correct_answer_only | post_correct / records | 42/59 | 0.712 | [0.586, 0.812] |
| correct_answer_only | unparseable / records | 7/59 | 0.119 | [0.059, 0.225] |
| correct_rationale | wrong_to_right / pre_wrong | 4/9 | 0.444 | [0.189, 0.733] |
| correct_rationale | post_correct / records | 46/59 | 0.780 | [0.659, 0.866] |
| correct_rationale | unparseable / records | 5/59 | 0.085 | [0.037, 0.184] |
| correct_redacted_rationale | wrong_to_right / pre_wrong | 4/9 | 0.444 | [0.189, 0.733] |
| correct_redacted_rationale | post_correct / records | 47/59 | 0.797 | [0.677, 0.880] |
| correct_redacted_rationale | unparseable / records | 5/59 | 0.085 | [0.037, 0.184] |
| correct_equation_surface | wrong_to_right / pre_wrong | 2/9 | 0.222 | [0.063, 0.547] |
| correct_equation_surface | post_correct / records | 38/59 | 0.644 | [0.517, 0.754] |
| correct_equation_surface | unparseable / records | 10/59 | 0.169 | [0.095, 0.285] |
| correct_typed_public_state | wrong_to_right / pre_wrong | 0/9 | 0.000 | [0.000, 0.299] |
| correct_typed_public_state | post_correct / records | 37/59 | 0.627 | [0.500, 0.739] |
| correct_typed_public_state | unparseable / records | 13/59 | 0.220 | [0.134, 0.341] |

## All Source Cases Paired Correctness

| A | B | Known Pairs | Unknown Pairs | A-only | B-only | Delta A-B | Exact p |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| wrong_typed_public_state | wrong_rationale | 47 | 12 | 8 | 2 | +0.128 | 0.1094 |
| wrong_typed_public_state | wrong_redacted_rationale | 47 | 12 | 5 | 3 | +0.043 | 0.7266 |
| wrong_typed_public_state | wrong_equation_surface | 48 | 11 | 2 | 1 | +0.021 | 1.0000 |
| wrong_typed_public_state | wrong_answer_only | 47 | 12 | 3 | 3 | +0.000 | 1.0000 |
| correct_typed_public_state | correct_rationale | 45 | 14 | 0 | 4 | -0.089 | 0.1250 |
| correct_typed_public_state | correct_redacted_rationale | 45 | 14 | 0 | 3 | -0.067 | 0.2500 |
| correct_typed_public_state | correct_equation_surface | 46 | 13 | 1 | 1 | +0.000 | 1.0000 |
| correct_redacted_rationale | correct_rationale | 52 | 7 | 1 | 1 | +0.000 | 1.0000 |

## Source-Label-Reliable Cases

| Condition | Metric | Count | Rate | Wilson 95% |
| --- | --- | ---: | ---: | --- |
| no_peer | post_correct / records | 32/47 | 0.681 | [0.538, 0.796] |
| no_peer | unparseable / records | 8/47 | 0.170 | [0.089, 0.301] |
| wrong_answer_only | right_to_wrong / pre_correct | 2/32 | 0.062 | [0.017, 0.201] |
| wrong_answer_only | stable_right / pre_correct | 29/32 | 0.906 | [0.758, 0.968] |
| wrong_answer_only | post_correct / records | 31/47 | 0.660 | [0.517, 0.778] |
| wrong_answer_only | unparseable / records | 4/47 | 0.085 | [0.034, 0.199] |
| wrong_rationale | right_to_wrong / pre_correct | 8/32 | 0.250 | [0.133, 0.421] |
| wrong_rationale | stable_right / pre_correct | 24/32 | 0.750 | [0.579, 0.867] |
| wrong_rationale | post_correct / records | 24/47 | 0.511 | [0.372, 0.647] |
| wrong_rationale | unparseable / records | 2/47 | 0.043 | [0.012, 0.142] |
| wrong_redacted_rationale | right_to_wrong / pre_correct | 5/32 | 0.156 | [0.069, 0.318] |
| wrong_redacted_rationale | stable_right / pre_correct | 27/32 | 0.844 | [0.682, 0.931] |
| wrong_redacted_rationale | post_correct / records | 29/47 | 0.617 | [0.474, 0.742] |
| wrong_redacted_rationale | unparseable / records | 1/47 | 0.021 | [0.004, 0.111] |
| wrong_equation_surface | right_to_wrong / pre_correct | 3/32 | 0.094 | [0.032, 0.242] |
| wrong_equation_surface | stable_right / pre_correct | 29/32 | 0.906 | [0.758, 0.968] |
| wrong_equation_surface | post_correct / records | 30/47 | 0.638 | [0.495, 0.760] |
| wrong_equation_surface | unparseable / records | 4/47 | 0.085 | [0.034, 0.199] |
| wrong_typed_public_state | right_to_wrong / pre_correct | 3/32 | 0.094 | [0.032, 0.242] |
| wrong_typed_public_state | stable_right / pre_correct | 29/32 | 0.906 | [0.758, 0.968] |
| wrong_typed_public_state | post_correct / records | 30/47 | 0.638 | [0.495, 0.760] |
| wrong_typed_public_state | unparseable / records | 6/47 | 0.128 | [0.060, 0.252] |
| correct_answer_only | wrong_to_right / pre_wrong | 2/7 | 0.286 | [0.082, 0.641] |
| correct_answer_only | post_correct / records | 36/47 | 0.766 | [0.628, 0.864] |
| correct_answer_only | unparseable / records | 3/47 | 0.064 | [0.022, 0.172] |
| correct_rationale | wrong_to_right / pre_wrong | 4/7 | 0.571 | [0.250, 0.842] |
| correct_rationale | post_correct / records | 41/47 | 0.872 | [0.748, 0.940] |
| correct_rationale | unparseable / records | 2/47 | 0.043 | [0.012, 0.142] |
| correct_redacted_rationale | wrong_to_right / pre_wrong | 4/7 | 0.571 | [0.250, 0.842] |
| correct_redacted_rationale | post_correct / records | 42/47 | 0.894 | [0.774, 0.954] |
| correct_redacted_rationale | unparseable / records | 2/47 | 0.043 | [0.012, 0.142] |
| correct_equation_surface | wrong_to_right / pre_wrong | 2/7 | 0.286 | [0.082, 0.641] |
| correct_equation_surface | post_correct / records | 33/47 | 0.702 | [0.560, 0.813] |
| correct_equation_surface | unparseable / records | 6/47 | 0.128 | [0.060, 0.252] |
| correct_typed_public_state | wrong_to_right / pre_wrong | 0/7 | 0.000 | [0.000, 0.354] |
| correct_typed_public_state | post_correct / records | 32/47 | 0.681 | [0.538, 0.796] |
| correct_typed_public_state | unparseable / records | 8/47 | 0.170 | [0.089, 0.301] |

## Source-Label-Reliable Paired Correctness

| A | B | Known Pairs | Unknown Pairs | A-only | B-only | Delta A-B | Exact p |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| wrong_typed_public_state | wrong_rationale | 40 | 7 | 8 | 2 | +0.150 | 0.1094 |
| wrong_typed_public_state | wrong_redacted_rationale | 40 | 7 | 5 | 3 | +0.050 | 0.7266 |
| wrong_typed_public_state | wrong_equation_surface | 41 | 6 | 2 | 1 | +0.024 | 1.0000 |
| wrong_typed_public_state | wrong_answer_only | 40 | 7 | 3 | 3 | +0.000 | 1.0000 |
| correct_typed_public_state | correct_rationale | 38 | 9 | 0 | 4 | -0.105 | 0.1250 |
| correct_typed_public_state | correct_redacted_rationale | 38 | 9 | 0 | 3 | -0.079 | 0.2500 |
| correct_typed_public_state | correct_equation_surface | 39 | 8 | 1 | 1 | +0.000 | 1.0000 |
| correct_redacted_rationale | correct_rationale | 43 | 4 | 1 | 1 | +0.000 | 1.0000 |

## Notes

- `unparseable / records` means semantic unknown here, not necessarily missing text.
- Source-label-reliable cases are those where the saved `correct_peer` response is semantically correct and the saved `wrong_peer` response is semantically wrong against the original boxed answer.
- Peer-answer adoption is intentionally not recomputed here because the saved peer answer fields came from the older numeric parser.
- Cases with `unknown_semantic_parse` should be inspected before becoming claim-bearing evidence.
