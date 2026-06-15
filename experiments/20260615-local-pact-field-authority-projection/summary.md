# PACT Field-Authority Projection Packet

This artifact removes the old paired target-slot diagnostic from the gating decision.
The detector uses only the original question and current public fields, then builds a security-style projection condition and a standalone quarantine condition.

- Source units: `100`
- Generated packet rows: `200`
- Detector actions: `{'hide': 30, 'project_question_root': 70}`

## Offline Routing Scores

| Slice | Records | EM | Avg F1 | Chosen conditions |
| --- | ---: | ---: | ---: | --- |
| always_base_public_state | 100 | 0.520 | 0.688 | `question_plus_public_state_no_final`=100 |
| always_hide_public_target | 100 | 0.590 | 0.725 | `question_plus_evidence_no_target_no_final`=100 |
| always_security_projection | 100 | 0.580 | 0.734 | `frozen_target_plus_evidence_no_final`=100 |
| standalone_hide_risky_else_project | 100 | 0.560 | 0.719 | `frozen_target_plus_evidence_no_final`=70, `question_plus_evidence_no_target_no_final`=30 |

## Condition Counts

| Condition | Rows |
| --- | ---: |
| `security_projection_question_root_no_final` | 100 |
| `standalone_authority_quarantine_no_final` | 100 |

## Detector Reasons

| Reason | Count |
| --- | ---: |
| `generic_low_overlap_target` | 14 |
| `no_explicit_answer_authority_verb` | 6 |
| `projected` | 70 |
| `under_specified_target` | 18 |
| `unsupported_target_terms` | 16 |

## Caveats

- Offline routing rows, when present, reuse already-run field-packet outputs and are diagnostic only.
- `always_security_projection` maps to the earlier frozen-target condition because both use a question-derived target plus evidence.
- The detector is deliberately conservative and lexical; it is a pressure object, not a semantic entailment verifier.
