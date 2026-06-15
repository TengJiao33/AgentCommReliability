# MATH Parser-Sensitivity Audit

This audit joins peer-exposure source cases back to original MATH boxed answers, flags answers that are not plain numeric values under the current project normalizer, and recomputes key rates after excluding those parser-sensitive source cases.

## Case Surface

- Total source cases: `59`
- Plain numeric source cases: `38`
- Parser-sensitive source cases: `21`

| Reason | Cases |
| --- | ---: |
| complex | 1 |
| expression_not_single_number | 10 |
| latex_non_fraction | 14 |
| multi_value_or_comma | 1 |
| non_plain_numeric | 4 |
| pi | 4 |
| radical | 3 |
| symbolic_letter | 6 |

Parser-sensitive case IDs:

`11, 13, 14, 18, 22, 56, 60, 68, 73, 89, 94, 101, 112, 116, 118, 121, 139, 146, 181, 191, 193`

## Plain-Numeric Subset Rates

| Condition | Metric | Count | Rate | Wilson 95% |
| --- | --- | ---: | ---: | --- |
| no_peer | post_correct / records | 24/38 | 0.632 | [0.473, 0.766] |
| no_peer | unparseable / records | 8/38 | 0.211 | [0.111, 0.363] |
| wrong_answer_only | right_to_wrong / pre_correct | 1/24 | 0.042 | [0.007, 0.202] |
| wrong_answer_only | post_correct / records | 24/38 | 0.632 | [0.473, 0.766] |
| wrong_rationale | right_to_wrong / pre_correct | 6/24 | 0.250 | [0.120, 0.449] |
| wrong_rationale | post_correct / records | 17/38 | 0.447 | [0.301, 0.603] |
| wrong_redacted_rationale | right_to_wrong / pre_correct | 4/24 | 0.167 | [0.067, 0.359] |
| wrong_redacted_rationale | post_correct / records | 20/38 | 0.526 | [0.373, 0.675] |
| wrong_equation_surface | right_to_wrong / pre_correct | 2/24 | 0.083 | [0.023, 0.258] |
| wrong_equation_surface | post_correct / records | 22/38 | 0.579 | [0.422, 0.721] |
| wrong_typed_public_state | right_to_wrong / pre_correct | 1/24 | 0.042 | [0.007, 0.202] |
| wrong_typed_public_state | post_correct / records | 23/38 | 0.605 | [0.447, 0.744] |
| correct_answer_only | wrong_to_right / pre_wrong | 3/6 | 0.500 | [0.188, 0.812] |
| correct_answer_only | post_correct / records | 30/38 | 0.789 | [0.637, 0.889] |
| correct_rationale | wrong_to_right / pre_wrong | 4/6 | 0.667 | [0.300, 0.903] |
| correct_rationale | post_correct / records | 32/38 | 0.842 | [0.696, 0.926] |
| correct_redacted_rationale | wrong_to_right / pre_wrong | 2/6 | 0.333 | [0.097, 0.700] |
| correct_redacted_rationale | post_correct / records | 30/38 | 0.789 | [0.637, 0.889] |
| correct_equation_surface | wrong_to_right / pre_wrong | 0/6 | 0.000 | [0.000, 0.390] |
| correct_equation_surface | post_correct / records | 23/38 | 0.605 | [0.447, 0.744] |
| correct_typed_public_state | wrong_to_right / pre_wrong | 1/6 | 0.167 | [0.030, 0.564] |
| correct_typed_public_state | post_correct / records | 25/38 | 0.658 | [0.499, 0.788] |

## Plain-Numeric Paired Correctness

| A | B | Known Pairs | A-only | B-only | Delta A-B | Exact p |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| wrong_typed_public_state | wrong_rationale | 29 | 6 | 1 | +0.172 | 0.1250 |
| wrong_typed_public_state | wrong_redacted_rationale | 30 | 4 | 1 | +0.100 | 0.3750 |
| wrong_typed_public_state | wrong_equation_surface | 30 | 1 | 0 | +0.033 | 1.0000 |
| wrong_typed_public_state | wrong_answer_only | 31 | 1 | 2 | -0.032 | 1.0000 |
| correct_typed_public_state | correct_rationale | 31 | 0 | 3 | -0.097 | 0.2500 |
| correct_typed_public_state | correct_redacted_rationale | 31 | 0 | 1 | -0.032 | 1.0000 |
| correct_typed_public_state | correct_equation_surface | 31 | 2 | 0 | +0.065 | 0.5000 |

## Notes

- This is a conservative exclusion audit, not a semantic MATH evaluator.
- A parser-sensitive source answer can still be correctly solved by the model; the flag only says the current numeric normalizer is not trustworthy enough for strong semantic claims on that case.
- Plain-numeric rates are useful as a robustness check for the main statistical audit.
