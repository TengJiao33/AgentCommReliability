# PACT Field-Contract Verifier Packet

This artifact builds a first deterministic verifier for the PACT public-state field packet.
It is a pressure object, not a method result.

The verifier uses no gold answer in its decisions. It checks whether the public target looks under-specified or drift-prone, and whether a visible final-answer candidate is concise and supported by the visible evidence fields.

## Output Files

- `verified_packet.jsonl`: model-ready gated packet with all verifier conditions.
- `verified_quarantine_packet.jsonl`: focused packet for the strongest offline target-quarantine strategy.
- `verifier_records.jsonl`: one verifier decision per sample/source pair.
- `summary.json`: verifier counts and offline routing audit.
- `summary.md`: readable summary.

## Packet Size

- Source units: `100`
- Generated rows: `400`

## Verifier Actions

- Target actions: `{'freeze': 33, 'keep': 67}`
- Candidate actions: `{'hide': 9, 'show': 91}`

## Offline Routing Audit

The offline routing audit chooses among the already-run five condition outputs using the verifier decision. It is diagnostic only; it is not a new model result.

## Routing Scores

| Slice | Records | EM | Avg F1 | Chosen conditions |
| --- | ---: | ---: | ---: | --- |
| always_base_public_state | 100 | 0.520 | 0.688 | `question_plus_public_state_no_final`=100 |
| always_hide_public_target | 100 | 0.590 | 0.725 | `question_plus_evidence_no_target_no_final`=100 |
| always_freeze_question_target | 100 | 0.580 | 0.734 | `frozen_target_plus_evidence_no_final`=100 |
| always_show_final_candidate | 100 | 0.550 | 0.710 | `question_plus_public_state_with_final`=100 |
| verifier_freeze_risky_else_base | 100 | 0.540 | 0.685 | `frozen_target_plus_evidence_no_final`=33, `question_plus_public_state_no_final`=67 |
| verifier_hide_risky_else_base | 100 | 0.570 | 0.710 | `question_plus_evidence_no_target_no_final`=33, `question_plus_public_state_no_final`=67 |
| verifier_hide_risky_else_freeze | 100 | 0.610 | 0.759 | `frozen_target_plus_evidence_no_final`=67, `question_plus_evidence_no_target_no_final`=33 |
| verifier_licensed_final_else_freeze | 100 | 0.540 | 0.683 | `frozen_target_plus_evidence_no_final`=5, `question_plus_public_state_no_final`=4, `question_plus_public_state_with_final`=91 |
| verifier_licensed_final_else_hide | 100 | 0.550 | 0.689 | `question_plus_evidence_no_target_no_final`=5, `question_plus_public_state_no_final`=4, `question_plus_public_state_with_final`=91 |

## Caveats

- Target-risk rules use lexical overlap, generic target patterns, and the existing target-slot diagnostic.
- Candidate licensing is surface-level token support, not semantic entailment.
- Offline routing reuses outputs from the previous pressure run and can overstate what a newly prompted gated packet will do.
- The next real test is to run `verified_packet.jsonl` through the same model runner.
