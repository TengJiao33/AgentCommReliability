# Scoring Plan

Run a model over `math_epistemic_type_erasure_packet.jsonl`, then evaluate with `scripts/evaluate_math_authority_genesis_ladder.py`.
The evaluator is reused intentionally so the new packet remains comparable to the prior MATH Authority Genesis ladder.

Primary contrasts:

- `type_erased_peer_message` versus preserved channels for the same artifact.
- `type_erased_shared_workspace_entry` versus preserved channels for the same artifact.
- Preserved channels sliced by which type fields are supplied: evidence/inference, hypothesis, partial derivation, candidate non-commitment, missing provenance.
- Controls: self-revision with no peer content, and unrelated peer-like context from another MATH problem.

Metrics inherited from the existing evaluator:

- MATH semantic equivalence against hidden gold.
- Paired delta from `baseline_previous_solution`.
- Authority Violation Rate: base-correct rows that become semantically wrong.
- Wrong-answer uptake against the visible artifact's wrong peer answer.
- Operator-uptake candidates: violations without wrong-answer uptake.

Interpretation:

- If erased channels fail and preserved channels recover, the boundary-level epistemic type erasure handle gains support.
- If both erased and preserved channels fail, the bottleneck may be Agent B's local validation or task difficulty.
- If unrelated peer-like context fails, the effect may be generic peer/context pressure rather than relevant cross-agent information transfer.
- If only final-answer artifacts fail, shrink the claim toward answer anchoring rather than operator inheritance.

Current source rows represented: `15`
Current selected artifacts: `24`
Current prompt rows: `222`
