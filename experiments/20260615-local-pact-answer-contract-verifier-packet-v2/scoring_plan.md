# PACT Answer-Contract Verifier Packet V2

This packet keeps the same records and gold labels as the v1 verifier packet.
Only the prompt is changed.

## Prompt Repair

- Adds consistency rules tying `answer_contract_alarm` to subalarms and primary surface.
- Restricts `target_authority_alarm = soft` to secondary Action Required issues.
- Adds a decision order and sharper surface definitions.
- Separates target authority from evidence adequacy, final-candidate attraction, and strict span/granularity.

## Size

- Records: `74`
- Label sources: `{'negative_control_seed': 24, 'positive_target_layer_seed': 50}`
- Primary surfaces: `{'answer_type_or_relation_mismatch': 21, 'evidence_or_content_failure': 8, 'evidence_sentence_or_distractor_copy': 3, 'final_candidate_attractor': 5, 'no_answer_contract_failure': 8, 'public_target_misdirection': 3, 'question_root_ambiguity_regression': 2, 'short_span_or_granularity_mismatch': 21, 'strict_span_or_granularity_surface': 3}`

## Scoring

Use `scripts/evaluate_pact_answer_contract_verifier.py` with `--prediction-source outputs`.
