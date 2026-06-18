# State Admission V2 Smoke Packet

状态：local smoke packet。这里还没有 GPU output；`gold_answer`、`expected_units` 和 scoring obligations 都是 evaluator-only metadata。

- packet: `experiments\20260618-local-state-admission-v2-smoke\packet.jsonl`
- rows: `9`
- variants: each HiddenBench row has one base variant and two same-text source/scope perturbations.
- model prompt must not render `gold_answer`, `expected_units`, `expected_absent_units`, `expected_rejections`, or `expected_downstream_state`.

Next gate: score `oracle_predictions.jsonl` before launching a model smoke.
