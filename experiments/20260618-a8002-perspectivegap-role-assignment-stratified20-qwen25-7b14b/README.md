# PerspectiveGap Stratified20 Role-Assignment Run

## Gate

- Purpose: turn the 4-row PerspectiveGap smoke into a broader benchmark-contact signal before designing a method.
- Benchmark unit: official PerspectiveGap role-fragment assignment, scored by upstream `scripts/score_predictions.py`.
- Runner: project wrapper `scripts/run_perspectivegap_role_assignment_openai_compatible.py`, reusing upstream renderer and output schema while exposing `temperature` and `max_tokens`.
- Models:
  - `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
  - `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- Scope: 20 scenarios stratified by role count, seeds `1` and `42`, total `40` requests per model.
- Temperature: `0.0`.
- Max output tokens: `1024`.
- Success condition: both models complete all 40 requests, local scorer parses all rows, and paired coverage/precision/leak trends can be compared against the 4-row smoke.
- Failure condition: server/API errors, parser failures, or output count mismatch. In those cases treat this as plumbing evidence only.
- Invalidation guard: this is still a small stratified subset, not the full 220-row benchmark.

## Scenario Set

```text
pg_000,pg_015,pg_022,pg_029,
pg_002,pg_003,pg_049,pg_109,
pg_006,pg_072,pg_076,pg_079,
pg_004,pg_007,pg_089,pg_099,
pg_005,pg_062,pg_066,pg_069
```

These cover role counts `2, 3, 4, 5, 6` with four scenarios per bucket.

## Results

Both model runs completed `40/40` requests with empty runner stderr. GPU 7 and ports `8063/8064` were clean after the driver finished.

| Model | Strict | Coverage | Precision | Distractor leak/eval | Counts |
| --- | ---: | ---: | ---: | ---: | --- |
| Qwen2.5-7B-Instruct | 0/40 | 0.443 | 0.786 | 0.050 | tp=239, fp=65, fn=301, leak=2 |
| Qwen2.5-14B-Instruct | 0/40 | 0.615 | 0.808 | 0.450 | tp=332, fp=79, fn=208, leak=18 |

Summary artifacts:

- `stratified_summary.md`
- `stratified_summary.json`
- `scores_qwen25_7b.jsonl`
- `scores_qwen25_14b.jsonl`
