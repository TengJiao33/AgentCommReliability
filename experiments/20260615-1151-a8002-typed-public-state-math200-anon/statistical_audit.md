# Peer Exposure Statistical Audit

Rates use Wilson 95% intervals. Paired correctness tests use an exact two-sided binomial sign test over discordant case pairs.

## Key Rates

| Condition | Metric | Count | Rate | Wilson 95% |
| --- | --- | ---: | ---: | --- |
| no_peer | post_correct / records | 37/59 | 0.627 | [0.500, 0.739] |
| no_peer | unparseable / records | 9/59 | 0.153 | [0.082, 0.265] |
| wrong_answer_only | right_to_wrong / pre_correct | 1/37 | 0.027 | [0.005, 0.138] |
| wrong_answer_only | stable_right / pre_correct | 36/37 | 0.973 | [0.862, 0.995] |
| wrong_answer_only | post_correct / records | 38/59 | 0.644 | [0.517, 0.754] |
| wrong_answer_only | unparseable / records | 3/59 | 0.051 | [0.017, 0.139] |
| wrong_answer_only | peer_answer_adopted / records | 9/59 | 0.153 | [0.082, 0.265] |
| wrong_rationale | right_to_wrong / pre_correct | 9/37 | 0.243 | [0.134, 0.401] |
| wrong_rationale | stable_right / pre_correct | 27/37 | 0.730 | [0.570, 0.846] |
| wrong_rationale | post_correct / records | 27/59 | 0.458 | [0.337, 0.583] |
| wrong_rationale | unparseable / records | 3/59 | 0.051 | [0.017, 0.139] |
| wrong_rationale | peer_answer_adopted / records | 22/59 | 0.373 | [0.261, 0.500] |
| wrong_redacted_rationale | right_to_wrong / pre_correct | 4/37 | 0.108 | [0.043, 0.247] |
| wrong_redacted_rationale | stable_right / pre_correct | 33/37 | 0.892 | [0.753, 0.957] |
| wrong_redacted_rationale | post_correct / records | 33/59 | 0.559 | [0.433, 0.678] |
| wrong_redacted_rationale | unparseable / records | 4/59 | 0.068 | [0.027, 0.162] |
| wrong_redacted_rationale | peer_answer_adopted / records | 4/59 | 0.068 | [0.027, 0.162] |
| wrong_equation_surface | right_to_wrong / pre_correct | 3/37 | 0.081 | [0.028, 0.213] |
| wrong_equation_surface | stable_right / pre_correct | 34/37 | 0.919 | [0.787, 0.972] |
| wrong_equation_surface | post_correct / records | 36/59 | 0.610 | [0.483, 0.724] |
| wrong_equation_surface | unparseable / records | 7/59 | 0.119 | [0.059, 0.225] |
| wrong_equation_surface | peer_answer_adopted / records | 7/59 | 0.119 | [0.059, 0.225] |
| wrong_typed_public_state | right_to_wrong / pre_correct | 3/37 | 0.081 | [0.028, 0.213] |
| wrong_typed_public_state | stable_right / pre_correct | 34/37 | 0.919 | [0.787, 0.972] |
| wrong_typed_public_state | post_correct / records | 35/59 | 0.593 | [0.466, 0.709] |
| wrong_typed_public_state | unparseable / records | 8/59 | 0.136 | [0.070, 0.245] |
| wrong_typed_public_state | peer_answer_adopted / records | 8/59 | 0.136 | [0.070, 0.245] |
| correct_answer_only | wrong_to_right / pre_wrong | 4/13 | 0.308 | [0.127, 0.576] |
| correct_answer_only | post_correct / records | 45/59 | 0.763 | [0.640, 0.853] |
| correct_answer_only | unparseable / records | 3/59 | 0.051 | [0.017, 0.139] |
| correct_answer_only | peer_answer_adopted / records | 45/59 | 0.763 | [0.640, 0.853] |
| correct_rationale | wrong_to_right / pre_wrong | 5/13 | 0.385 | [0.177, 0.645] |
| correct_rationale | post_correct / records | 47/59 | 0.797 | [0.677, 0.880] |
| correct_rationale | unparseable / records | 0/59 | 0.000 | [0.000, 0.061] |
| correct_rationale | peer_answer_adopted / records | 47/59 | 0.797 | [0.677, 0.880] |
| correct_redacted_rationale | wrong_to_right / pre_wrong | 5/13 | 0.385 | [0.177, 0.645] |
| correct_redacted_rationale | post_correct / records | 47/59 | 0.797 | [0.677, 0.880] |
| correct_redacted_rationale | unparseable / records | 1/59 | 0.017 | [0.003, 0.090] |
| correct_redacted_rationale | peer_answer_adopted / records | 1/59 | 0.017 | [0.003, 0.090] |
| correct_equation_surface | wrong_to_right / pre_wrong | 1/13 | 0.077 | [0.014, 0.333] |
| correct_equation_surface | post_correct / records | 37/59 | 0.627 | [0.500, 0.739] |
| correct_equation_surface | unparseable / records | 7/59 | 0.119 | [0.059, 0.225] |
| correct_equation_surface | peer_answer_adopted / records | 7/59 | 0.119 | [0.059, 0.225] |
| correct_typed_public_state | wrong_to_right / pre_wrong | 1/13 | 0.077 | [0.014, 0.333] |
| correct_typed_public_state | post_correct / records | 38/59 | 0.644 | [0.517, 0.754] |
| correct_typed_public_state | unparseable / records | 8/59 | 0.136 | [0.070, 0.245] |
| correct_typed_public_state | peer_answer_adopted / records | 8/59 | 0.136 | [0.070, 0.245] |

## Paired Correctness

| A | B | Known Pairs | A-only | B-only | Delta A-B | Exact p |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| wrong_typed_public_state | wrong_rationale | 49 | 9 | 2 | +0.143 | 0.0654 |
| wrong_typed_public_state | wrong_redacted_rationale | 49 | 5 | 3 | +0.041 | 0.7266 |
| wrong_typed_public_state | wrong_equation_surface | 50 | 1 | 2 | -0.020 | 1.0000 |
| wrong_typed_public_state | wrong_answer_only | 51 | 2 | 4 | -0.039 | 0.6875 |
| correct_typed_public_state | correct_rationale | 51 | 0 | 4 | -0.078 | 0.1250 |
| correct_typed_public_state | correct_redacted_rationale | 51 | 0 | 4 | -0.078 | 0.1250 |
| correct_typed_public_state | correct_equation_surface | 51 | 2 | 1 | +0.020 | 1.0000 |
| correct_redacted_rationale | correct_rationale | 58 | 2 | 2 | +0.000 | 1.0000 |

Case IDs for discordant pairs are in the JSON sidecar.
