# TypeCastArena Repaired Receiver Packet

This packet is derived from the 315-row inert-control receiver run after it failed the control gate.
It keeps the same communication contrasts but filters to receiver-control-stable cases and strengthens the final-answer contract.

## Shape

- Repair tag: `controlstable_v1`
- Selected cases: `13`
- Excluded cases: `22`
- Receiver prompt rows: `117`
- Required correct variants: `['baseline_previous_solution', 'control_self_revision_no_sender', 'control_unrelated_sender_message']`
- Strict final-answer contract: `True`
- Rows by channel condition: `{'admitted': 26, 'baseline': 13, 'control': 39, 'erased': 13, 'quarantine': 13, 'typed': 13}`
- Rows by candidate visibility: `{'answer_removed': 13, 'artifact_native': 52, 'artifact_native_unrelated': 13, 'none': 39}`

## Purpose

The next GPU run should answer a narrower diagnostic question: after receiver baseline, self-revision, and unrelated-message controls are already correct, do admitted/verifier channels separate from inert, quarantine, and typed-rederive controls?

## Gate

- This packet is still setup evidence until a model run is completed.
- A future run is not claim-bearing if inert, unrelated, quarantine, or typed-rederive controls fail at rates comparable to admitted/verifier channels.
- If the strict final-answer contract still yields many missing-answer rows, repair the prompt before running a larger packet.

## Local Validation

- Script syntax check passed:
  `python -m py_compile scripts/build_typecast_receiver_repair_packet.py scripts/analyze_typecast_boundary_obedience.py`.
- Packet audit:
  - `117` rows;
  - `117` unique packet ids;
  - `13` rows for each future signal;
  - all rows use the strict output contract;
  - no rows retain the older one-line final-answer instruction.
- Gold-smoke evaluation:
  - `117/117` semantic-correct rows;
  - `0` semantic-wrong rows;
  - `0` semantic-unknown rows.
- Boundary-obedience gold-smoke:
  - `0/117` boundary concern cards.

## Caveats

- The `13` cases are selected post hoc from the
  `20260617-0033-a8002-typecast-math200-inert-receiver315-qwen25-14b`
  Qwen2.5-14B run by requiring baseline, self-revision, and unrelated-message
  rows to be semantically correct.
- This packet is therefore a repaired diagnostic slice, not a population sample
  and not behavior evidence by itself.
- Future behavior claims must be conditioned on these controls staying clean in
  the actual model run.

## Behavior Follow-Up

- Follow-up run:
  `experiments/20260617-0148-a8002-typecast-repaired-controlstable117-qwen25-14b/`.
- Status:
  diagnostic control-gate failure, not positive lifecycle evidence.
- Key result:
  - self-revision: `0/11` paired violations;
  - unrelated control: `0/11`;
  - quarantine: `0/11`;
  - inert visible scratch: `2/11`;
  - direct peer: `2/11`;
  - shared workspace: `2/11`;
  - verifier admitted: `2/11`;
  - typed rederive: `1/11`.
- Boundary-obedience follow-up:
  `3/117` concern cards: `1` inert candidate uptake and `2` typed
  hidden/removed candidate uptake.
- Consequence:
  redesign inert and typed controls locally before any further GPU run.
