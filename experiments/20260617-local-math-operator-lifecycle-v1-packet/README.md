# MATH Operator Lifecycle V1 Packet

Status: local packet only. No GPU run has been launched from this materialization step.

## Purpose

Test whether the same wrong sender operator artifact becomes more harmful when it is directly messaged, admitted, verifier-admitted, withheld, or typed.

## Shape

- Source rows represented: `11`
- Selected sender artifacts: `16`
- Prompt rows: `166`
- Selected artifacts by type: `{'wrong_equation_surface': 5, 'wrong_final_answer': 5, 'wrong_numeric_role_binding': 3, 'wrong_relation_skeleton': 3}`
- Selected artifacts by MATH case: `{'112': 2, '121': 2, '136': 2, '139': 2, '159': 2, '21': 1, '25': 1, '28': 1, '61': 1, '96': 2}`
- Rows by channel condition: `{'admitted': 32, 'baseline': 11, 'control': 43, 'erased': 16, 'quarantine': 16, 'typed': 32, 'visibility_stress': 16}`
- Rows by candidate visibility: `{'answer_removed': 16, 'artifact_native': 64, 'artifact_native_unrelated': 16, 'none': 70}`
- Prompt-audit hard-gate leaks: `0`

## Lifecycle Channels

| Level | Channel | Family | Admission | Candidate visibility | Gate role |
| ---: | --- | --- | --- | --- | --- |
| none | `baseline_previous_solution` | baseline | none | none | baseline |
| -5 | `control_self_revision_no_peer` | control | none | none | hard control |
| -4 | `metadata_only_hidden_control` | `control` | `withheld` | `none` | hard control |
| -3 | `visible_inert_archived_content` | `visibility_stress` | `not_admitted` | `artifact_native` | stress |
| 0 | `peer_message_direct` | `erased` | `message_only` | `artifact_native` | target |
| 2 | `shared_workspace_admitted` | `admitted` | `admitted_shared_workspace` | `artifact_native` | target |
| 5 | `verifier_admitted_result` | `admitted` | `verifier_admitted` | `artifact_native` | target |
| 4 | `quarantine_withheld` | `quarantine` | `rejected` | `none` | hard control |
| 10 | `typed_inference_metadata_only` | `typed` | `typed_message` | `none` | hard control |
| 11 | `typed_partial_derivation_dependency_check` | `typed` | `typed_message` | `answer_removed` | stress |
| -1 | `control_unrelated_sender_message` | control | message_only | artifact_native_unrelated | hard control |

## Selected Artifacts

| Packet id | Case | Surface | Type | Prior invalid-cast core | Prior operator cards | Sanitized changed |
| --- | --- | --- | --- | ---: | ---: | --- |
| `a01_wrong_final_answer` | `21` | `full_rationale` | `wrong_final_answer` | 0 | 1 | `True` |
| `a02_wrong_final_answer` | `25` | `answer_only` | `wrong_final_answer` | 0 | 0 | `True` |
| `a03_wrong_final_answer` | `28` | `full_rationale` | `wrong_final_answer` | 0 | 0 | `True` |
| `a04_wrong_relation_skeleton` | `61` | `equation_surface` | `wrong_relation_skeleton` | 0 | 1 | `False` |
| `a05_wrong_numeric_role_binding` | `96` | `full_rationale` | `wrong_numeric_role_binding` | 0 | 1 | `False` |
| `a06_wrong_final_answer` | `96` | `full_rationale` | `wrong_final_answer` | 0 | 2 | `True` |
| `a07_wrong_numeric_role_binding` | `112` | `full_rationale` | `wrong_numeric_role_binding` | 0 | 0 | `False` |
| `a08_wrong_relation_skeleton` | `112` | `full_rationale` | `wrong_relation_skeleton` | 0 | 0 | `False` |
| `a09_wrong_equation_surface` | `121` | `equation_surface` | `wrong_equation_surface` | 1 | 3 | `False` |
| `a10_wrong_equation_surface` | `121` | `full_rationale` | `wrong_equation_surface` | 1 | 3 | `False` |
| `a11_wrong_equation_surface` | `136` | `full_rationale` | `wrong_equation_surface` | 0 | 0 | `True` |
| `a12_wrong_relation_skeleton` | `136` | `full_rationale` | `wrong_relation_skeleton` | 0 | 0 | `False` |
| `a13_wrong_equation_surface` | `139` | `full_rationale` | `wrong_equation_surface` | 0 | 0 | `False` |
| `a14_wrong_final_answer` | `139` | `full_rationale` | `wrong_final_answer` | 0 | 1 | `True` |
| `a15_wrong_equation_surface` | `159` | `full_rationale` | `wrong_equation_surface` | 0 | 5 | `True` |
| `a16_wrong_numeric_role_binding` | `159` | `full_rationale` | `wrong_numeric_role_binding` | 0 | 9 | `True` |

## Remote Launch Template

Use the generic TypeCastArena runner after copying this packet to A800_2.

```bash
PACKET=/data/xuhaoming/yfy/research_workspace/experiments/20260617-local-math-operator-lifecycle-v1-packet/math_operator_lifecycle_v1_packet.jsonl \
RUN_ID=<stamp>-a8002-math-operator-lifecycle-v1-qwen25-14b \
MODEL_PATH=/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct \
SERVED_MODEL=qwen2.5-14b-math-operator-lifecycle-v1 \
GPU_ID=<free-gpu> PORT=<free-port> EVALUATE=1 BOUNDARY_ANALYZE=1 \
bash scripts/run_typecast_arena_packet_a8002.sh
```

## Caveats

- The sender artifacts are saved objects from prior MATH rows; this packet tests lifecycle casting around those objects.
- `visible_inert_archived_content` is a visibility stress condition because it deliberately shows sender content.
- `typed_partial_derivation_dependency_check` removes candidate-answer strings, but it still exposes operator content by design.
- A model run and case audit are required before making behavioral claims.
