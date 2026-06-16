# MATH Epistemic Type-Erasure v2 Packet

This packet is the continuity step after the MATH Epistemic Type-Erasure v1 run.
It keeps the same selected right-to-wrong MATH artifacts and the same paired-baseline scoring contract, but splits typed communication by candidate-answer visibility.

Core contrast: the same Agent A content is sent as flat text, typed content with no candidate, typed content with a hidden candidate metadata field, typed content with a visible non-committed candidate, or typed derivation with the answer removed/visible.

This is a setup packet, not a model result.

## Shape

- Source rows represented: `15`
- Selected artifacts: `24`
- Prompt rows: `222`
- Rows by channel condition: `{'baseline': 15, 'control': 39, 'erased': 48, 'typed': 120}`
- Rows by candidate visibility: `{'answer_removed': 24, 'answer_visible': 24, 'artifact_native': 48, 'artifact_native_unrelated': 24, 'hidden_metadata': 24, 'none': 54, 'visible_field': 24}`
- Communication rows with wrong-answer literal visible: `88`
- Selected artifacts by type: `{'wrong_equation_surface': 10, 'wrong_final_answer': 6, 'wrong_numeric_role_binding': 4, 'wrong_relation_skeleton': 4}`
- Selected artifacts changed by candidate removal: `11`
- Prior ladder-violation-linked artifacts: `13`

## Channel Conditions

| Level | Channel | Family | Candidate visibility | What Changes |
| ---: | --- | --- | --- | --- |
| none | `baseline_previous_solution` | baseline | none | no communication artifact |
| -2 | `control_self_revision_no_peer` | control | none | same re-check task with no peer content |
| -1 | `control_unrelated_peer_like_context` | control | artifact-native unrelated | peer-shaped text from another problem |
| 0 | `type_erased_peer_message` | `erased` | `artifact_native` | flat peer message, artifact-native candidate visibility |
| 1 | `type_erased_shared_workspace_entry` | `erased` | `artifact_native` | flat shared workspace entry, artifact-native candidate visibility |
| 20 | `typed_no_candidate_evidence_inference` | `typed` | `none` | typed evidence/inference object with no candidate-answer field |
| 21 | `typed_hidden_candidate_metadata` | `typed` | `hidden_metadata` | typed object whose candidate answer is hidden transport metadata |
| 22 | `typed_visible_candidate_noncommitment` | `typed` | `visible_field` | typed candidate field is visible but explicitly non-committed |
| 23 | `typed_derivation_answer_removed` | `typed` | `answer_removed` | typed partial derivation with answer/candidate content removed |
| 24 | `typed_derivation_answer_visible` | `typed` | `answer_visible` | typed partial derivation with candidate answer visible |

## Selected Artifacts

| Artifact | Case | Surface | Type | Source has candidate literal | Removal changed text | Prior violations | Prior operator candidates | Original harmful post |
| --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| `math13_wrong_typed_public_state::wrong_numeric_role_binding::1` | `13` | `typed_public_state` | `wrong_numeric_role_binding` | `True` | `True` | 0 | 0 | `-11` |
| `math13_wrong_typed_public_state::wrong_relation_skeleton::0` | `13` | `typed_public_state` | `wrong_relation_skeleton` | `False` | `False` | 0 | 0 | `-11` |
| `math21_wrong_rationale::wrong_numeric_role_binding::2` | `21` | `full_rationale` | `wrong_numeric_role_binding` | `False` | `False` | 0 | 0 | `15` |
| `math21_wrong_rationale::wrong_relation_skeleton::1` | `21` | `full_rationale` | `wrong_relation_skeleton` | `False` | `False` | 0 | 0 | `15` |
| `math25_wrong_answer_only::wrong_final_answer::0` | `25` | `answer_only` | `wrong_final_answer` | `True` | `True` | 1 | 0 | `6` |
| `math28_wrong_rationale::wrong_relation_skeleton::1` | `28` | `full_rationale` | `wrong_relation_skeleton` | `False` | `False` | 0 | 0 | `1` |
| `math28_wrong_rationale::wrong_final_answer::0` | `28` | `full_rationale` | `wrong_final_answer` | `True` | `True` | 1 | 0 | `1` |
| `math29_wrong_redacted_rationale::wrong_equation_surface::2` | `29` | `redacted_rationale` | `wrong_equation_surface` | `True` | `True` | 0 | 0 | `2` |
| `math61_wrong_equation_surface::wrong_equation_surface::2` | `61` | `equation_surface` | `wrong_equation_surface` | `False` | `False` | 0 | 0 | `66` |
| `math61_wrong_equation_surface::wrong_relation_skeleton::0` | `61` | `equation_surface` | `wrong_relation_skeleton` | `False` | `False` | 1 | 1 | `66` |
| `math96_wrong_rationale::wrong_numeric_role_binding::2` | `96` | `full_rationale` | `wrong_numeric_role_binding` | `False` | `False` | 1 | 1 | `\(\frac{128}{3}\)` |
| `math96_wrong_rationale::wrong_final_answer::0` | `96` | `full_rationale` | `wrong_final_answer` | `True` | `True` | 5 | 2 | `\(\frac{128}{3}\)` |
| `math112_wrong_rationale::wrong_equation_surface::3` | `112` | `full_rationale` | `wrong_equation_surface` | `False` | `False` | 0 | 0 | `43` |
| `math112_wrong_rationale::wrong_final_answer::0` | `112` | `full_rationale` | `wrong_final_answer` | `True` | `True` | 1 | 0 | `43` |
| `math121_wrong_equation_surface::wrong_equation_surface::2` | `121` | `equation_surface` | `wrong_equation_surface` | `False` | `False` | 3 | 3 | `36√2` |
| `math121_wrong_rationale::wrong_equation_surface::3` | `121` | `full_rationale` | `wrong_equation_surface` | `False` | `False` | 3 | 3 | `36\sqrt{2}` |
| `math136_wrong_rationale::wrong_equation_surface::3` | `136` | `full_rationale` | `wrong_equation_surface` | `True` | `True` | 4 | 0 | `10` |
| `math136_wrong_rationale::wrong_final_answer::0` | `136` | `full_rationale` | `wrong_final_answer` | `True` | `True` | 1 | 0 | `10` |
| `math139_wrong_rationale::wrong_equation_surface::3` | `139` | `full_rationale` | `wrong_equation_surface` | `False` | `False` | 0 | 0 | `37.3π` |
| `math139_wrong_rationale::wrong_final_answer::0` | `139` | `full_rationale` | `wrong_final_answer` | `True` | `True` | 1 | 1 | `37.3π` |
| `math159_wrong_rationale::wrong_equation_surface::3` | `159` | `full_rationale` | `wrong_equation_surface` | `True` | `True` | 5 | 5 | `26` |
| `math159_wrong_rationale::wrong_numeric_role_binding::2` | `159` | `full_rationale` | `wrong_numeric_role_binding` | `True` | `True` | 9 | 9 | `26` |
| `math165_wrong_equation_surface::wrong_equation_surface::2` | `165` | `equation_surface` | `wrong_equation_surface` | `False` | `False` | 0 | 0 | `108` |
| `math165_wrong_redacted_rationale::wrong_equation_surface::2` | `165` | `redacted_rationale` | `wrong_equation_surface` | `False` | `False` | 0 | 0 | `108` |

## Caveats

- Candidate removal is exact-string based; some derivations may still carry wrong operators or relation structure without a final-answer literal.
- Hidden candidate metadata is stored in row metadata for analysis; the answer value is not included in the prompt.
- This packet still uses static communication artifacts. A sender-receiver lifecycle remains the next escalation if v2 separates the arms.
- A model run is required before making behavioral claims.
