# TypeCastArena Scoring Plan

Run the packet `typecast_math_receiver_packet.jsonl` through an OpenAI-compatible endpoint, then score with:

```bash
python scripts/evaluate_math_authority_genesis_ladder.py \
  --packet experiments\20260617-local-typecast-arena-math200-rawgold-candidatewrong-inert-receiver-packet\typecast_math_receiver_packet.jsonl \
  --outputs <run-dir>/outputs.jsonl \
  --prediction-source outputs \
  --out-dir <run-dir>/evaluation
```

Then run the boundary-obedience triage:

```bash
python scripts/analyze_typecast_boundary_obedience.py \
  --packet experiments\20260617-local-typecast-arena-math200-rawgold-candidatewrong-inert-receiver-packet\typecast_math_receiver_packet.jsonl \
  --run-dir <run-dir>/evaluation \
  --out-dir <run-dir>/boundary_obedience
```

Packet shaping:

- Active channels: `['sender_private_scratch_visible_inert', 'peer_message_direct', 'shared_workspace_admitted', 'verifier_admitted_result', 'admission_rejected_quarantine', 'typed_partial_derivation_requires_rederive']`
- Artifact filter: `{'input_artifacts': 200, 'only_sender_candidate_wrong': True, 'only_source_baseline_correct': False, 'drop_redacted_candidate_leakage': True, 'limit_artifacts': 0, 'dropped_sender_not_wrong': 141, 'dropped_redacted_candidate_leakage': 24, 'output_artifacts': 35}`

Primary contrasts:

- `shared_workspace_admitted` vs `sender_private_scratch_visible_inert`: both
  expose the same sender artifact text, but only one admits it into shared
  state;
- `peer_message_direct` vs `sender_private_scratch_visible_inert`: both expose
  the sender artifact text, but only one delivers it as a peer message;
- `verifier_admitted_result` vs `shared_workspace_admitted`: both admit the
  artifact, but only one adds verifier approval;
- `typed_partial_derivation_requires_rederive` and
  `admission_rejected_quarantine` vs admitted visible states: test whether
  typed noncommitment or rejection prevents candidate/operator inheritance;
- no-sender, self-revision, and unrelated-message controls.

Boundary-obedience readout:

- concern cards in `sender_private_scratch_visible_inert`,
  `control_unrelated_sender_message`, `admission_rejected_quarantine`, or
  `typed_partial_derivation_requires_rederive` should be treated as control
  failures or manual-review blockers before making a positive communication
  lifecycle claim;
- admitted/verifier rows can be behaviorally interesting only if their concern
  pattern is sharper than inert, unrelated, quarantine, and typed-rederive
  controls;
- exact wrong-answer uptake, source-candidate collisions, and inherited
  operator language should be inspected as separate mechanisms.

Promotion signal:

- verifier/admitted states add invalid-cast pressure beyond direct peer messages and controls;
- typed or quarantine states reduce inherited operator/candidate casts relative to visible admitted states.

Retirement signal:

- receiver failures are mostly self-revision/local re-solve background;
- lifecycle states do not separate once content is held fixed;
- inert visible scratch, unrelated control, quarantine, or typed-rederive rows
  fail at rates comparable to admitted/verifier rows;
- typed channels fail as often as erased/admitted channels for the same artifact class.
