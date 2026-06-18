# TypeCastArena Scoring Plan

Run the packet `typecast_math_receiver_packet.jsonl` through an OpenAI-compatible endpoint, then score with:

```bash
python scripts/evaluate_math_authority_genesis_ladder.py \
  --packet experiments\_archive\20260616-pruned\20260616-local-typecast-arena-math-live-receiver-packet-sender12\typecast_math_receiver_packet.jsonl \
  --outputs <run-dir>/outputs.jsonl \
  --prediction-source outputs \
  --out-dir <run-dir>/evaluation
```

Primary contrasts:

- private scratch visible but inert vs peer message vs shared workspace vs memory;
- shared workspace vs majority consensus vs verifier-admitted result;
- admitted states vs rejected quarantine;
- typed evidence/inference/hypothesis/partial-derivation/candidate channels vs flat admitted states;
- self-revision and unrelated-message controls.

Promotion signal:

- admission/reuse states add invalid-cast pressure beyond direct peer messages and controls;
- typed or quarantine states reduce inherited operator/candidate casts without wiping out useful correct transfer.

Retirement signal:

- receiver failures are mostly self-revision/local re-solve background;
- lifecycle states do not separate once content is held fixed;
- typed channels fail as often as erased/admitted channels for the same artifact class.
