# PACT Authority Injection Arena Run

Date: 2026-06-15

## Run

- run id: `20260615-2130-a8002-pact-authority-injection-arena-qwen25-14b`
- machine: `A800_2`
- GPU: `7`
- model path: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- served model: `qwen2.5-14b-authority-injection-arena`
- packet: `experiments/20260615-local-pact-authority-injection-arena-packet/arena_packet.jsonl`
- records selected: `280`
- completed: `280`
- failed: `0`
- temperature: `0`
- max tokens: `64`

## Files

- `manifest.json`: run metadata from the packet runner.
- `outputs.jsonl`: model outputs keyed by `packet_id`.
- `evaluation/summary.json`: scored aggregate results.
- `evaluation/summary.md`: human-readable tables.
- `evaluation/evaluated_rows.jsonl`: row-level scores.
- `evaluation/paired_deltas.jsonl`: paired deltas from `original_untyped_public`.

## Evaluator

The run was scored with:

```bash
python scripts/evaluate_pact_authority_injection_arena.py \
  --packet experiments/20260615-local-pact-authority-injection-arena-packet/arena_packet.jsonl \
  --outputs experiments/20260615-2130-a8002-pact-authority-injection-arena-qwen25-14b/outputs.jsonl \
  --prediction-source outputs \
  --out-dir experiments/20260615-2130-a8002-pact-authority-injection-arena-qwen25-14b/evaluation
```

## Note

This is a selected saved-field pressure run, not a population estimate or a
full PACT rerun. Authority Violation Rate is only meaningful on cases where
`original_untyped_public` was correct.
