# TypeCastArena MATH200 Decisive Source

This local setup prepares a 200-case live-sender TypeCastArena stage from the saved MATH200 MAD-MM trace.
It does not run a model. The point is to create a large but sharp content-held-constant cast test.

## Shape

- Source rows: `200`
- Sender-stage prompt rows: `200`
- Cases with at least one correct round-0 peer: `149`
- Cases with at least one wrong round-0 peer: `110`
- Peer-mix counts: `{'0correct_3wrong': 51, '1correct_2wrong': 23, '2correct_1wrong': 36, '3correct_0wrong': 90}`
- Existing trace transitions: `{'right_to_wrong': 9, 'stable_right': 123, 'stable_wrong': 56, 'wrong_to_right': 12}`

## Decisive Question

For the same live Agent A artifact, does Agent B behave differently when the communication boundary casts it as inert scratch, a direct peer message, admitted shared state, verifier-admitted state, quarantine, or typed partial derivation requiring re-derivation?

## Later GPU Stages

Stage 1, sender artifact generation:

```bash
PACKET=<this-dir>/typecast_math200_sender_stage_packet.jsonl \
RUN_ID=<stamp>-a8002-typecast-math200-sender200-qwen25-7b \
MODEL_PATH=/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct \
SERVED_MODEL=qwen2.5-7b-typecast-sender200 \
GPU_ID=<free-gpu> PORT=<free-port> LIMIT= scripts/run_typecast_arena_packet_a8002.sh
```

Stage 2, materialize the receiver packet from sender outputs:

```bash
python scripts/materialize_typecast_math_live_receiver_packet.py \
  --source-rows <this-dir>/source_rows.jsonl \
  --sender-packet <this-dir>/typecast_math200_sender_stage_packet.jsonl \
  --sender-outputs <sender-run>/outputs.jsonl \
  --channels sender_private_scratch_visible_inert peer_message_direct shared_workspace_admitted verifier_admitted_result admission_rejected_quarantine typed_partial_derivation_requires_rederive \
  --out-dir experiments/<local-receiver-packet-dir>
```

Stage 3, receiver run can be sharded by `LIMIT` or by pre-splitting the packet. Use one GPU only and no long overnight run.

## Primary Contrasts

- `shared_workspace_admitted` versus `sender_private_scratch_visible_inert`: cast effect with content visible in both.
- `verifier_admitted_result` versus `peer_message_direct`: procedural-approval cast effect.
- `typed_partial_derivation_requires_rederive` versus `shared_workspace_admitted`: mitigation without deleting the artifact.
- `admission_rejected_quarantine`: negative control for withheld content.

## Readout

- Wrong sender artifacts: harmful cast rate, wrong-answer uptake, non-copy operator uptake.
- Correct sender artifacts: useful evidence retention and rescue rate.
- All sender artifacts: boundary obedience, especially unauthorized use under inert/quarantine/typed-rederive channels.
