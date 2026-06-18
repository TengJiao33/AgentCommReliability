# Scoring Plan

## Preflight Contract

Purpose: Test whether the same wrong sender operator artifact becomes more harmful when it is directly messaged, admitted, verifier-admitted, withheld, or typed.
Unit: sender artifact x lifecycle channel, paired against a real prior Agent B solution
Primary contrast: compare the same sender artifact across direct peer, shared workspace, verifier-admitted, quarantine, typed metadata, and typed partial-derivation channels.
Secondary contrasts: baseline previous solution, self revision with no sender, unrelated sender message, and metadata-only hidden control.
Success signal: admitted or verifier-admitted channels produce more base-right to wrong deltas and more operator-uptake candidates than hard controls.
Failure signal: hard controls show comparable failures, or most failures are direct candidate copies, parser artifacts, local re-solve noise, or final-line formatting errors.
Invalidation conditions: hidden controls leak sender content, baseline rows lack real previous solutions, evaluator gold differs from original MATH gold, or duplicate variants collapse paired deltas.

## Commands

Gold smoke:

```bash
python scripts/evaluate_math_authority_genesis_ladder.py \
  --packet experiments/20260617-local-math-operator-lifecycle-v1-packet/math_operator_lifecycle_v1_packet.jsonl \
  --prediction-source gold \
  --out-dir experiments/20260617-local-math-operator-lifecycle-v1-packet/gold_smoke
```

Boundary audit after a real run:

```bash
python scripts/analyze_typecast_boundary_obedience.py \
  --packet experiments/20260617-local-math-operator-lifecycle-v1-packet/math_operator_lifecycle_v1_packet.jsonl \
  --run-dir <run>/evaluation \
  --out-dir <run>/boundary_obedience
```

## Required Readouts

- `evaluation/summary.json` and `evaluation/paired_deltas.jsonl`
- boundary-obedience cards by channel
- artifact-family cards for inherited operator state vs answer copy
- leave-one-case-out sensitivity for MATH case concentration
