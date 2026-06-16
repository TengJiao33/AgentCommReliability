# Scoring Plan

Run a model over `math_epistemic_type_erasure_v2_packet.jsonl`, then evaluate with `scripts/evaluate_math_authority_genesis_ladder.py`.
The evaluator is reused intentionally so v2 remains comparable to the prior MATH Authority Genesis and Type-Erasure runs.

Primary contrasts:

- `type_erased_shared_workspace_entry` versus `typed_no_candidate_evidence_inference`.
- `typed_hidden_candidate_metadata` versus `typed_visible_candidate_noncommitment`.
- `typed_derivation_answer_removed` versus `typed_derivation_answer_visible`.
- Candidate-visible typed arms versus erased arms, to separate answer anchoring from type erasure.
- Controls: self-revision with no peer content, and unrelated peer-like context from another MATH problem.

Metrics inherited from the existing evaluator:

- MATH semantic equivalence against hidden gold.
- Paired delta from `baseline_previous_solution`.
- Authority Violation Rate: base-correct rows that become semantically wrong.
- Wrong-answer uptake against the hidden/source wrong peer answer.
- Operator-uptake candidates: violations without wrong-answer uptake.

Interpretation:

- If erased channels fail but typed no-candidate and hidden-candidate arms remain clean, the boundary-level type-erasure story gains support.
- If visible-candidate typed arms fail while hidden/no-candidate arms remain clean, the remaining v1 failure is mostly candidate visibility.
- If answer-removed derivations still fail, the issue is not answer copying but operator/relation inheritance.
- If unrelated peer-like context fails often, the effect is too generic to support a multi-agent communication-boundary claim.

Current source rows represented: `15`
Current selected artifacts: `24`
Current prompt rows: `222`
