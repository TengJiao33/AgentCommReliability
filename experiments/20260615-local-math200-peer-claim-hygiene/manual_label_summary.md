# Peer Field-Label Summary

This summarizes existing manual seed labels for the MATH200 claim-hygiene packet. It does not infer new labels.

## Coverage

- Packet rows: `97`
- Manual seed rows: `21`
- Manual source-label-sensitive seed rows: `23`
- Unique labeled rows: `44`
- Unlabeled rows: `53`

Unlabeled by reason:

| Value | Rows |
| --- | ---: |
| `source_label_sensitive` | 38 |
| `behavior_changing` | 15 |

Unlabeled by surface:

| Value | Rows |
| --- | ---: |
| `answer_only` | 15 |
| `redacted_rationale` | 14 |
| `full_rationale` | 12 |
| `equation_surface` | 9 |
| `typed_public_state` | 3 |

## Anonymous Behavior Labels

Relation skeleton quality:

| Value | Rows |
| --- | ---: |
| `wrong` | 18 |
| `incomplete` | 1 |
| `mixed` | 1 |
| `not_visible` | 1 |

Numeric / role slot quality:

| Value | Rows |
| --- | ---: |
| `wrong` | 14 |
| `mixed` | 4 |
| `mostly_correct` | 1 |
| `not_visible` | 1 |
| `thin` | 1 |

Final-answer authority visible:

| Value | Rows |
| --- | ---: |
| `False` | 11 |
| `True` | 10 |

## Source-Label-Sensitive Labels

Sensitivity category:

| Value | Rows |
| --- | ---: |
| `rescue_lost` | 9 |
| `harm_added` | 6 |
| `harm_removed` | 6 |
| `rescue_added` | 2 |

Field family:

| Value | Rows |
| --- | ---: |
| `absolute-value_curve_endpoint_relation` | 4 |
| `centroid_area_partition_relation` | 2 |
| `modular_coprimality_relation` | 2 |
| `square_side_vs_diagonal_role` | 2 |
| `target_predicate_shift_position_vs_shared_digit_set` | 2 |
| `units-digit_cycle_count` | 2 |
| `answer_only_parser_loss` | 1 |
| `circle_radius_after_completing_square` | 1 |
| `clock_hour-hand_numeric_slot` | 1 |
| `count_vs_value_predicate` | 1 |
| `digit-count_double-count_relation` | 1 |
| `final_answer_authority_plus_incomplete_factor_slots` | 1 |
| `geometry_relation_ambiguous` | 1 |
| `mixture_component_total_equations` | 1 |
| `rationalization_sign_slot` | 1 |

Final-answer authority visible:

| Value | Rows |
| --- | ---: |
| `False` | 15 |
| `True` | 8 |

Parser-surface confound:

| Value | Rows |
| --- | ---: |
| `False` | 22 |
| `True` | 1 |

## Reading Rule

These are seed labels and coverage counts, not population estimates. Use the unlabeled sidecar to decide whether another manual pass is worth doing before moving to a split-evidence task.
