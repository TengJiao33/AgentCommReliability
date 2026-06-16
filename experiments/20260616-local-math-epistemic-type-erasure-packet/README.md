# MATH Epistemic Type-Erasure Packet

This local v0 packet is the continuity step after the MATH Authority Genesis ladder.
It reuses the same right-to-wrong MATH peer artifacts, but changes the causal handle from authority strength to communication type preservation.

Core contrast: the same Agent A content is either serialized as a flat peer/shared-context message or carried with explicit epistemic type, provenance, confidence, and commitment fields.

This is a setup packet, not a model result.

## Shape

- Source rows represented: `15`
- Selected artifacts: `24`
- Prompt rows: `222`
- Rows by channel condition: `{'baseline': 15, 'control': 39, 'erased': 48, 'preserved': 120}`
- Selected artifacts by type: `{'wrong_equation_surface': 10, 'wrong_final_answer': 6, 'wrong_numeric_role_binding': 4, 'wrong_relation_skeleton': 4}`
- Selected artifacts by MATH case: `{'112': 2, '121': 2, '13': 2, '136': 2, '139': 2, '159': 2, '165': 2, '21': 2, '25': 1, '28': 2, '29': 1, '61': 2, '96': 2}`
- Prior ladder-violation-linked artifacts: `13`
- Prior operator-candidate-linked artifacts: `8`

## Channel Conditions

| Level | Channel | Family | What Changes |
| ---: | --- | --- | --- |
| none | `baseline_previous_solution` | baseline | no communication artifact |
| -2 | `control_self_revision_no_peer` | control | same re-check task with no peer content |
| -1 | `control_unrelated_peer_like_context` | control | peer-shaped text from another problem |
| 0 | `type_erased_peer_message` | `erased` | flat peer message |
| 1 | `type_erased_shared_workspace_entry` | `erased` | flat shared workspace entry |
| 10 | `type_preserved_evidence_inference_split` | `preserved` | evidence/inference split |
| 11 | `type_preserved_hypothesis_low_confidence` | `preserved` | hypothesis with low/unknown confidence |
| 12 | `type_preserved_partial_derivation_check_required` | `preserved` | partial derivation with cast check |
| 13 | `type_preserved_candidate_noncommitment` | `preserved` | candidate state, not a commitment |
| 14 | `type_preserved_provenance_missing_context` | `preserved` | provenance/missing-context record |

## Selected Artifacts

| Artifact | Case | Surface | Type | Prior violations | Prior operator candidates | Original harmful post | Manual behavior |
| --- | --- | --- | --- | ---: | ---: | --- | --- |
| `math13_wrong_typed_public_state::wrong_numeric_role_binding::1` | `13` | `typed_public_state` | `wrong_numeric_role_binding` | 0 | 0 | `-11` | adopted_wrong_rotation_operator_from_hidden-final_typed_state |
| `math13_wrong_typed_public_state::wrong_relation_skeleton::0` | `13` | `typed_public_state` | `wrong_relation_skeleton` | 0 | 0 | `-11` | adopted_wrong_rotation_operator_from_hidden-final_typed_state |
| `math21_wrong_rationale::wrong_numeric_role_binding::2` | `21` | `full_rationale` | `wrong_numeric_role_binding` | 0 | 0 | `15` | copied_peer_final_despite_own_cube-exponent_check |
| `math21_wrong_rationale::wrong_relation_skeleton::1` | `21` | `full_rationale` | `wrong_relation_skeleton` | 0 | 0 | `15` | copied_peer_final_despite_own_cube-exponent_check |
| `math25_wrong_answer_only::wrong_final_answer::0` | `25` | `answer_only` | `wrong_final_answer` | 1 | 0 | `6` | accepted_final_answer_anchor_without_maximality_check |
| `math28_wrong_rationale::wrong_relation_skeleton::1` | `28` | `full_rationale` | `wrong_relation_skeleton` | 0 | 0 | `1` | accepted_wrong_function-count_argument |
| `math28_wrong_rationale::wrong_final_answer::0` | `28` | `full_rationale` | `wrong_final_answer` | 1 | 0 | `1` | accepted_wrong_function-count_argument |
| `math29_wrong_redacted_rationale::wrong_equation_surface::2` | `29` | `redacted_rationale` | `wrong_equation_surface` | 0 | 0 | `2` | adopted_wrong_position-wise_digit_comparison |
| `math61_wrong_equation_surface::wrong_equation_surface::2` | `61` | `equation_surface` | `wrong_equation_surface` | 0 | 0 | `66` | copied_missing_opposing-team_multiplicity |
| `math61_wrong_equation_surface::wrong_relation_skeleton::0` | `61` | `equation_surface` | `wrong_relation_skeleton` | 1 | 1 | `66` | copied_missing_opposing-team_multiplicity |
| `math96_wrong_rationale::wrong_numeric_role_binding::2` | `96` | `full_rationale` | `wrong_numeric_role_binding` | 1 | 1 | `\(\frac{128}{3}\)` | adopted_wrong_equal-area_partition |
| `math96_wrong_rationale::wrong_final_answer::0` | `96` | `full_rationale` | `wrong_final_answer` | 5 | 2 | `\(\frac{128}{3}\)` | adopted_wrong_equal-area_partition |
| `math112_wrong_rationale::wrong_equation_surface::3` | `112` | `full_rationale` | `wrong_equation_surface` | 0 | 0 | `43` | accepted_wrong_angle-decomposition_slot |
| `math112_wrong_rationale::wrong_final_answer::0` | `112` | `full_rationale` | `wrong_final_answer` | 1 | 0 | `43` | accepted_wrong_angle-decomposition_slot |
| `math121_wrong_equation_surface::wrong_equation_surface::2` | `121` | `equation_surface` | `wrong_equation_surface` | 3 | 3 | `36√2` | copied_square_side-vs-diagonal_role_error |
| `math121_wrong_rationale::wrong_equation_surface::3` | `121` | `full_rationale` | `wrong_equation_surface` | 3 | 3 | `36\sqrt{2}` | copied_square_side-vs-diagonal_role_error_with_full_rationale |
| `math136_wrong_rationale::wrong_equation_surface::3` | `136` | `full_rationale` | `wrong_equation_surface` | 4 | 0 | `10` | accepted_impossible_all-Angela_cup_equations |
| `math136_wrong_rationale::wrong_final_answer::0` | `136` | `full_rationale` | `wrong_final_answer` | 1 | 0 | `10` | accepted_impossible_all-Angela_cup_equations |
| `math139_wrong_rationale::wrong_equation_surface::3` | `139` | `full_rationale` | `wrong_equation_surface` | 0 | 0 | `37.3π` | adopted_wrong_diagram_height_slot |
| `math139_wrong_rationale::wrong_final_answer::0` | `139` | `full_rationale` | `wrong_final_answer` | 1 | 1 | `37.3π` | adopted_wrong_diagram_height_slot |
| `math159_wrong_rationale::wrong_equation_surface::3` | `159` | `full_rationale` | `wrong_equation_surface` | 5 | 5 | `26` | independent_boundary_regression_after_peer_prompt |
| `math159_wrong_rationale::wrong_numeric_role_binding::2` | `159` | `full_rationale` | `wrong_numeric_role_binding` | 9 | 9 | `26` | independent_boundary_regression_after_peer_prompt |
| `math165_wrong_equation_surface::wrong_equation_surface::2` | `165` | `equation_surface` | `wrong_equation_surface` | 0 | 0 | `108` | copied_rationalization_sign_error |
| `math165_wrong_redacted_rationale::wrong_equation_surface::2` | `165` | `redacted_rationale` | `wrong_equation_surface` | 0 | 0 | `108` | copied_rationalization_sign_error_after_redaction |

## Caveats

- The packet is intentionally deconcentrated by MATH case because the previous mechanism audit was dominated by two cases.
- The preserved channels are not meant as a safety prompt; they are a typed communication boundary.
- If preserved channels still fail, the problem may be inside Agent B's local validation, not only the boundary representation.
- If unrelated peer-like context fails often, the result is not specific to relevant multi-agent information transfer.
- A model run is required before making behavioral claims.
