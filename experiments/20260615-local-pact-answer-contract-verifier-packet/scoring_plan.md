# PACT Answer-Contract Verifier Packet

This packet turns the positive answer-contract audit seed and the negative-control seed into model-ready verifier prompts.
The prompt does not include gold answers or observed downstream behavior.

## Size

- Records: `74`
- Label sources: `{'negative_control_seed': 24, 'positive_target_layer_seed': 50}`
- Primary surfaces: `{'answer_type_or_relation_mismatch': 21, 'evidence_or_content_failure': 8, 'evidence_sentence_or_distractor_copy': 3, 'final_candidate_attractor': 5, 'no_answer_contract_failure': 8, 'public_target_misdirection': 3, 'question_root_ambiguity_regression': 2, 'short_span_or_granularity_mismatch': 21, 'strict_span_or_granularity_surface': 3}`

## Output Schema

The verifier must emit one JSON object with these fields:

- `answer_contract_alarm`: `yes` or `no`
- `target_authority_alarm`: `yes`, `no`, or `soft`
- `answer_type_relation_alarm`: `yes` or `no`
- `short_span_granularity_alarm`: `yes` or `no`
- `evidence_adequacy_alarm`: `yes` or `no`
- `final_candidate_alarm`: `yes` or `no`
- `primary_failure_surface`: one of `answer_type_or_relation_mismatch`, `short_span_or_granularity_mismatch`, `public_target_misdirection`, `evidence_sentence_or_distractor_copy`, `question_root_ambiguity_regression`, `evidence_or_content_failure`, `final_candidate_attractor`, `strict_span_or_granularity_surface`, `no_answer_contract_failure`
- `rationale`: one short sentence

## Scoring

Use `scripts/evaluate_pact_answer_contract_verifier.py` to score model outputs.
Primary checks:

- exact accuracy for every alarm field;
- binary precision/recall/F1 where `yes` and `soft` count as positive;
- primary-surface accuracy and confusion matrix;
- separate positive-seed and negative-control scores.

## Caveat

This is a verifier benchmark packet, not evidence that a verifier works.
