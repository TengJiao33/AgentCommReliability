# PACT Field-Contract Quarantine Qwen2.5-14B Run

This run tests the strongest target-contract verifier route from
`experiments/20260615-local-pact-field-contract-verifier/`.

## Run

| Field | Value |
| --- | --- |
| Run id | `20260615-1807-a8002-pact-field-contract-quarantine-qwen25-14b` |
| Host | `A800_2` |
| GPU | `7` |
| Model | `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct` |
| Served model | `qwen2.5-14b-pact-field-verifier` |
| Packet | `experiments/20260615-local-pact-field-contract-verifier/verified_quarantine_packet.jsonl` |
| Temperature | `0.0` |
| Max tokens | `64` |
| Rows | `100` |
| Completed | `100` |
| Failed | `0` |

## Condition

`verified_quarantine_risky_else_frozen_no_final`

Policy:

- risky public target: hide `Action Required`;
- non-risky public target: replace it with a frozen question-derived target;
- never expose the original public target;
- never expose the final-answer candidate.

## Result

| Records | EM | Avg F1 |
| ---: | ---: | ---: |
| `100` | `0.610` | `0.753` |

By source run:

| Source run | EM | Avg F1 |
| --- | ---: | ---: |
| `baseline` | `0.600` | `0.728` |
| `final_contract` | `0.620` | `0.778` |

Paired against prior conditions:

| Reference | Rescues | Regressions |
| --- | ---: | ---: |
| `question_plus_public_state_no_final` | `12` | `3` |
| `question_plus_evidence_no_target_no_final` | `5` | `3` |
| `frozen_target_plus_evidence_no_final` | `5` | `2` |
| `question_plus_public_state_with_final` | `11` | `5` |

## Files

- `outputs.jsonl`: raw model outputs.
- `manifest.json`: runner metadata.
- `evaluation/summary.json`: scored result.
- `evaluation/summary.md`: readable scored result.
- `evaluation/evaluated_rows.jsonl`: row-level scoring.
- `quarantine_delta_audit/quarantine_delta_summary.json`: paired delta summary.
- `quarantine_delta_audit/quarantine_delta_summary.md`: readable paired deltas.
- `quarantine_delta_audit/quarantine_delta_cards.jsonl`: row-level delta cards.

## Report

See `reports/20260615-pact-field-contract-quarantine.md`.
