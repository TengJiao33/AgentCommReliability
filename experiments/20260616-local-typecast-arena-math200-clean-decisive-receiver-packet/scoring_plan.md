# TypeCastArena Scoring Plan

Run the packet `typecast_math_receiver_packet.jsonl` through an OpenAI-compatible endpoint, then score with:

```bash
python scripts/evaluate_math_authority_genesis_ladder.py \
  --packet experiments\20260616-local-typecast-arena-math200-clean-decisive-receiver-packet\typecast_math_receiver_packet.jsonl \
  --outputs <run-dir>/outputs.jsonl \
  --prediction-source outputs \
  --out-dir <run-dir>/evaluation
```

Packet shaping:

- Active channels: `['peer_message_direct', 'shared_workspace_admitted', 'verifier_admitted_result', 'admission_rejected_quarantine', 'typed_partial_derivation_requires_rederive']`
- Artifact filter: `{'input_artifacts': 200, 'only_sender_candidate_wrong': True, 'only_source_baseline_correct': True, 'drop_redacted_candidate_leakage': True, 'limit_artifacts': 0, 'dropped_sender_not_wrong': 99, 'dropped_source_baseline_not_correct': 46, 'dropped_redacted_candidate_leakage': 17, 'output_artifacts': 38}`

Primary contrasts:

- direct peer message vs no-sender and unrelated-message controls;
- verifier-admitted result vs direct peer message;
- verifier-admitted result vs shared-workspace admitted state;
- typed partial derivation and rejected quarantine vs admitted visible states;
- self-revision and unrelated-message controls.

Promotion signal:

- verifier/admitted states add invalid-cast pressure beyond direct peer messages and controls;
- typed or quarantine states reduce inherited operator/candidate casts relative to visible admitted states.

Retirement signal:

- receiver failures are mostly self-revision/local re-solve background;
- lifecycle states do not separate once content is held fixed;
- typed channels fail as often as erased/admitted channels for the same artifact class.
