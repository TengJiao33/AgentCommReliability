# MATH Sender-Receiver Micro-Protocol Packet

This packet escalates the MATH type-erasure handle from static prompt labels to communication lifecycle transitions.
It uses saved Agent A artifacts from prior MATH peer-influence rows, then varies how a communication layer delivers or admits the same object to Agent B.

This is a setup packet, not a behavior result.

## Shape

- Source rows represented: `13`
- Selected artifacts: `20`
- Prompt rows: `246`
- Rows by channel condition: `{'admitted': 40, 'baseline': 13, 'control': 53, 'erased': 40, 'quarantine': 20, 'typed': 80}`
- Rows by admission status: `{'admitted_memory': 20, 'admitted_shared_workspace': 20, 'message_only': 60, 'none': 26, 'not_admitted': 20, 'rejected': 20, 'typed_message': 60, 'typed_message_with_hidden_metadata': 20}`
- Rows by candidate visibility: `{'answer_removed': 20, 'artifact_native': 100, 'artifact_native_unrelated': 20, 'hidden_metadata': 20, 'none': 66, 'visible_field': 20}`
- Communication rows with wrong-answer literal visible: `89`
- Selected artifacts by type: `{'wrong_equation_surface': 6, 'wrong_final_answer': 6, 'wrong_numeric_role_binding': 4, 'wrong_relation_skeleton': 4}`
- Selected artifacts with v2 invalid-cast core: `2`

## Lifecycle Conditions

| Level | Channel | Family | Admission | Persistence | Candidate visibility |
| ---: | --- | --- | --- | --- | --- |
| none | `baseline_previous_solution` | baseline | none | none | none |
| -2 | `control_self_revision_no_peer` | control | none | none | none |
| -3 | `sender_private_scratch_visible_inert` | `control` | `not_admitted` | `none` | `artifact_native` |
| 0 | `peer_message_direct` | `erased` | `message_only` | `turn_local` | `artifact_native` |
| 1 | `broadcast_peer_message` | `erased` | `message_only` | `turn_local` | `artifact_native` |
| 2 | `shared_workspace_admitted` | `admitted` | `admitted_shared_workspace` | `shared_state` | `artifact_native` |
| 3 | `memory_admitted_for_reuse` | `admitted` | `admitted_memory` | `persistent_memory` | `artifact_native` |
| 4 | `admission_rejected_quarantine` | `quarantine` | `rejected` | `none` | `none` |
| 10 | `typed_inference_noncommitment` | `typed` | `typed_message` | `turn_local` | `none` |
| 11 | `typed_partial_derivation_requires_rederive` | `typed` | `typed_message` | `turn_local` | `answer_removed` |
| 12 | `typed_candidate_hidden_metadata` | `typed` | `typed_message_with_hidden_metadata` | `metadata_only` | `hidden_metadata` |
| 13 | `typed_candidate_visible_noncommitment` | `typed` | `typed_message` | `turn_local` | `visible_field` |

## Selected Sender Objects

| Artifact | Case | Surface | Type | v2 invalid cast | prior operator cards | Original harmful post |
| --- | --- | --- | --- | ---: | ---: | --- |
| `math13_wrong_typed_public_state::wrong_numeric_role_binding::1` | `13` | `typed_public_state` | `wrong_numeric_role_binding` | 0 | 0 | `-11` |
| `math13_wrong_typed_public_state::wrong_relation_skeleton::0` | `13` | `typed_public_state` | `wrong_relation_skeleton` | 0 | 0 | `-11` |
| `math21_wrong_rationale::wrong_numeric_role_binding::2` | `21` | `full_rationale` | `wrong_numeric_role_binding` | 0 | 0 | `15` |
| `math21_wrong_rationale::wrong_relation_skeleton::1` | `21` | `full_rationale` | `wrong_relation_skeleton` | 0 | 0 | `15` |
| `math25_wrong_answer_only::wrong_final_answer::0` | `25` | `answer_only` | `wrong_final_answer` | 0 | 0 | `6` |
| `math28_wrong_rationale::wrong_relation_skeleton::1` | `28` | `full_rationale` | `wrong_relation_skeleton` | 0 | 0 | `1` |
| `math28_wrong_rationale::wrong_final_answer::0` | `28` | `full_rationale` | `wrong_final_answer` | 0 | 0 | `1` |
| `math29_wrong_redacted_rationale::wrong_equation_surface::2` | `29` | `redacted_rationale` | `wrong_equation_surface` | 0 | 0 | `2` |
| `math61_wrong_equation_surface::wrong_equation_surface::2` | `61` | `equation_surface` | `wrong_equation_surface` | 0 | 0 | `66` |
| `math61_wrong_equation_surface::wrong_relation_skeleton::0` | `61` | `equation_surface` | `wrong_relation_skeleton` | 0 | 1 | `66` |
| `math96_wrong_rationale::wrong_numeric_role_binding::2` | `96` | `full_rationale` | `wrong_numeric_role_binding` | 0 | 1 | `\(\frac{128}{3}\)` |
| `math96_wrong_rationale::wrong_final_answer::0` | `96` | `full_rationale` | `wrong_final_answer` | 0 | 2 | `\(\frac{128}{3}\)` |
| `math112_wrong_rationale::wrong_final_answer::0` | `112` | `full_rationale` | `wrong_final_answer` | 0 | 0 | `43` |
| `math121_wrong_equation_surface::wrong_equation_surface::2` | `121` | `equation_surface` | `wrong_equation_surface` | 1 | 3 | `36√2` |
| `math121_wrong_rationale::wrong_equation_surface::3` | `121` | `full_rationale` | `wrong_equation_surface` | 1 | 3 | `36\sqrt{2}` |
| `math136_wrong_rationale::wrong_equation_surface::3` | `136` | `full_rationale` | `wrong_equation_surface` | 0 | 0 | `10` |
| `math136_wrong_rationale::wrong_final_answer::0` | `136` | `full_rationale` | `wrong_final_answer` | 0 | 0 | `10` |
| `math139_wrong_rationale::wrong_final_answer::0` | `139` | `full_rationale` | `wrong_final_answer` | 0 | 1 | `37.3π` |
| `math159_wrong_rationale::wrong_equation_surface::3` | `159` | `full_rationale` | `wrong_equation_surface` | 0 | 5 | `26` |
| `math159_wrong_rationale::wrong_numeric_role_binding::2` | `159` | `full_rationale` | `wrong_numeric_role_binding` | 0 | 9 | `26` |

## Caveats

- Agent A objects are saved artifacts from prior runs, not newly generated inside this packet.
- This is nevertheless a sender-receiver lifecycle test because the packet varies delivery, admission, persistence, and typing for the same sender object.
- The v2 taxonomy shows local re-solve and final-line failures can masquerade as authority violations; downstream analysis should separate those from invalid-cast core.
- A model run is required before making behavioral claims.
