# Scoring Plan

Run a model over `math_sender_receiver_micro_protocol_packet.jsonl`, then evaluate with `scripts/evaluate_math_authority_genesis_ladder.py`.
The inherited evaluator gives semantic correctness, paired deltas from `baseline_previous_solution`, wrong-answer uptake, and operator-candidate flags.

Primary contrasts:

- `peer_message_direct` versus `shared_workspace_admitted` for the same sender object.
- `sender_private_scratch_visible_inert` versus admitted shared workspace and memory.
- `admission_rejected_quarantine` versus typed and erased delivery.
- `typed_inference_noncommitment` and `typed_partial_derivation_requires_rederive` versus flat admitted state.
- `typed_candidate_hidden_metadata` versus `typed_candidate_visible_noncommitment`.
- Controls: no sender message and unrelated sender message.

Post-run analysis should add the v2 invalid-cast taxonomy:

- invalid-cast core: inherited relation/numeric/equation operator state without exact wrong-answer copy;
- direct answer copy: semantic match to a visible wrong candidate;
- local re-solve error: wrong answer after empty or non-substantive typed artifact;
- final-answer contract or semantic collision: reasoning supports the base answer but final line changes, or prediction matches a hidden source answer.

Promotion signal:

- admitted shared workspace or memory causes more invalid-cast-core failures than direct peer messages, inert scratch, quarantine, and unrelated controls.
- typed boundaries reduce invalid-cast-core failures without deleting useful correct information transfer.

Retirement signal:

- lifecycle transitions add no signal beyond self-revision or unrelated-message controls.
- most failures are local re-solve or final-line artifacts rather than inherited operator state.

Current source rows represented: `13`
Current selected artifacts: `20`
Current prompt rows: `246`
