# PACT Field-Authority Projection Packet

This artifact removes the old paired target-slot diagnostic from the gating decision.
The detector uses only the original question and current public fields, then builds a security-style projection condition and a standalone quarantine condition.

- Source units: `100`
- Generated packet rows: `200`
- Detector actions: `{'hide': 35, 'project_question_root': 65}`

## Offline Routing Scores

No evaluated rows were provided for this packet, so no offline routing audit was run.

## Condition Counts

| Condition | Rows |
| --- | ---: |
| `security_projection_question_root_no_final` | 100 |
| `standalone_authority_quarantine_no_final` | 100 |

## Detector Reasons

| Reason | Count |
| --- | ---: |
| `generic_low_overlap_target` | 13 |
| `no_explicit_answer_authority_verb` | 2 |
| `projected` | 65 |
| `under_specified_target` | 18 |
| `unsupported_target_terms` | 24 |

## Caveats

- Offline routing rows, when present, reuse already-run field-packet outputs and are diagnostic only.
- `always_security_projection` maps to the earlier frozen-target condition because both use a question-derived target plus evidence.
- The detector is deliberately conservative and lexical; it is a pressure object, not a semantic entailment verifier.
