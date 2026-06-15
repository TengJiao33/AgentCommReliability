# PACT Public-State Field Qwen2.5-14B Pressure Run

Full model run of the PACT public-state field packet.

## Run

| Field | Value |
| --- | --- |
| Run id | `20260615-1655-a8002-pact-public-state-field-qwen25-14b` |
| Host | `A800_2` |
| GPU | `7` |
| Model | `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct` |
| Served model | `qwen2.5-14b-pact-field` |
| Temperature | `0.0` |
| Max tokens | `64` |
| Packet rows | `500` |
| Completed | `500` |
| Failed | `0` |

## Files

- `outputs.jsonl`: model predictions keyed by packet row.
- `manifest.json`: runner configuration and counts.
- `pact-field-packet-20260615-1655.log`: launcher log.
- `pact-field-vllm-20260615-1655.log`: vLLM server log.
- `runner.stdout.jsonl`: runner progress.
- `runner.stderr.log`: runner stderr.
- `evaluator.stdout.json`: evaluator JSON output.
- `evaluator.stderr.log`: evaluator stderr.
- `evaluation/summary.json`: official evaluation summary.
- `evaluation/summary.md`: readable evaluation summary.
- `evaluation/evaluated_rows.jsonl`: row-level scored outputs.
- `field_delta_audit/delta_summary.json`: paired condition delta summary.
- `field_delta_audit/delta_summary.md`: readable paired condition delta summary.
- `field_delta_audit/delta_cards.jsonl`: row-level paired delta cards.

## Main Result

Overall score: EM `0.536`, Avg F1 `0.689` over `500` rows.

By condition:

| Condition | EM | Avg F1 |
| --- | ---: | ---: |
| `question_plus_evidence_no_target_no_final` | `0.590` | `0.725` |
| `frozen_target_plus_evidence_no_final` | `0.580` | `0.734` |
| `question_plus_public_state_with_final` | `0.550` | `0.710` |
| `question_plus_public_state_no_final` | `0.520` | `0.688` |
| `public_target_plus_evidence_no_question_no_final` | `0.440` | `0.591` |

Paired deltas against `question_plus_public_state_no_final`:

| Comparison | Rescues | Regressions |
| --- | ---: | ---: |
| `hide_public_target` | `11` | `4` |
| `freeze_question_target` | `10` | `4` |
| `hide_question_keep_public_target` | `2` | `10` |
| `show_final_answer_candidate` | `6` | `3` |

## Interpretation

The run does not support a simple "public state helps" story. The public target
field is useful only when it stays coupled to the original question and usable
evidence. Hiding the public target improved the base condition, while hiding the
question and trusting the public target sharply hurt performance.

This run supports the next project object: field-level public-state reliability
across target contract, evidence carriage, and final-answer commitment.

## Report

See `reports/20260615-pact-public-state-field-qwen25-14b-pressure.md`.
