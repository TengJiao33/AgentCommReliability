# PACT Target-State Freeze Inspection

## Scope

- input run: `experiments/20260614-1642-a8002-pact-qwen25-14b-hotpot50-offset150-compact-target/`
- comparison: final-answer contract -> compact target + final-answer contract
- model/run behavior: no new model calls
- compute: local CPU-only postprocessing
- script: `scripts/build_pact_target_state_freeze_inspection.py`

## What We Tried

I inspected whether the offset150 compact `Target Slot` failures suggest a
useful frozen-target intervention.

The script joins:

- `comm_trace_offset150_compact_final_v11.jsonl`
- `comm_trace_offset150_final_contract_v11.jsonl`
- `final_vs_compact_final_cases.jsonl`

It emits per-sample target-slot sequences, mechanical freeze buckets, a compact
Markdown focus packet, and manual labels over the first 16 focus cases.

## What Happened

Mechanical scan over 50 samples:

- unstable target-slot records: `23/50`
- first/final target-slot mismatch: `22/50`
- template-collapse records: `4/50`
- right-to-wrong cases: `8`
  - `4` with visible target drift regression
  - `4` with stable target slots

Manual labels over 16 focus cases:

- likely or maybe helped by a question-derived/anchor-checked target state:
  samples `189`, `197`, `199`, `184`
- first-turn generated freeze would hurt or preserve an early error:
  samples `193`, `176`, `188`, `160`
- not primarily target-state failures:
  samples `153`, `154`, `164`, `182`, `185`, `163`
- target drift was useful or not needed:
  samples `152`, `173`

## Things Noticed

Freezing the first generated `Target Slot` is too crude.

Some drift is harmful, such as sample `199`, where the public target oscillates
between `1999 Odisha cyclone` and `Cyclone Gonu`. But some drift is the needed
bridge, such as sample `176`, where the target refines from the artist/museum
path to `drawings`.

The stronger next object is not:

```text
keep the first generated target slot
```

It is closer to:

```text
derive a compact target state from the original question, then check later
public targets against it without blocking necessary bridge refinement
```

## Artifacts

- `summary.json`
- `cases.jsonl`
- `focus_cases.jsonl`
- `focus_packet.md`
- `manual_labels.jsonl`
- `manual_summary.json`

## Caveats

- This is diagnostic postprocessing over saved traces.
- No frozen-target method was actually run.
- Manual labels are lightweight and local to the first 16 focus cases.
- HotpotQA exact match still mixes target-state errors with answer surface,
  alias granularity, and extraction artifacts.
