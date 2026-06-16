# TypeCastArena MATH Live Sender Stage

This packet is Stage 1 for a live sender-receiver TypeCastArena run.
Agent A solves each problem independently and emits a structured sender artifact.

Stage 2 materializes receiver prompts from the model outputs with:

```bash
python scripts/materialize_typecast_math_live_receiver_packet.py \
  --sender-packet experiments/20260616-local-typecast-arena-math-live-sender-stage/typecast_math_sender_stage_packet.jsonl \
  --sender-outputs <sender-run>/outputs.jsonl
```

## Shape

- Source rows: `12`
- Sender prompt rows: `12`
- Rows by source surface: `{'answer_only': 1, 'equation_surface': 2, 'full_rationale': 7, 'redacted_rationale': 1, 'typed_public_state': 1}`
- Rows by condition: `{'wrong_answer_only': 1, 'wrong_equation_surface': 2, 'wrong_rationale': 7, 'wrong_redacted_rationale': 1, 'wrong_typed_public_state': 1}`

## Status

Setup artifact only. A model run is required before receiver-stage prompts can be materialized from live Agent A outputs.
