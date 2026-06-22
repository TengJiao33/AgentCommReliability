# PerspectiveGap Full-Grid Direct Role-To-Prompt Control

日期：2026-06-19

## 状态

`COMPLETE_FULLGRID_CONTROL_NEGATIVE`

这个本地对照复用 official full-grid direct baseline 的 `role_assignment` 预测，不再调用模型。它把模型给出的 role-fragment assignment deterministic 转成 prompt-writing rows，再交给 PerspectiveGap official scorer。

## Input

| 项 | 内容 |
| --- | --- |
| source run | `experiments/20260619-a8002-perspectivegap-official-fullgrid-direct-qwen25-14b/` |
| source rows | `220` role-assignment predictions |
| converter | `scripts/perspectivegap_assignment_to_prompt_predictions.py` |
| scorer | PerspectiveGap official `scripts/score_predictions.py` |
| grid | same `110` scenarios x seeds `1,42` |

## Validation

| 检查 | 结果 |
| --- | ---: |
| role rows | `220` |
| converted prompt rows | `220` |
| combined prediction rows | `440` |
| score rows | `440` |
| scenario count | `110` |
| seeds | `[1, 42]` |
| status | `ok: 440` |

## Official Scorer Summary

| Task | Strict pass | Net match | Required coverage | Boundary precision | Distractor leakage |
| --- | ---: | ---: | ---: | ---: | ---: |
| role-fragment assignment | `0/220` | `0.1953` | `0.6063` | `0.7714` | `0.3409` |
| deterministic prompt from direct role assignment | `0/220` | `0.1953` | `0.6063` | `0.7714` | `0.3409` |

Combined pass:

```text
0/440
```

## Interpretation

The deterministic writer does not rescue direct prompting. The bottleneck is the model's role-fragment assignment itself, not free-form prompt-writing style.

This is a useful negative control for the next full-grid system route: a successful system route must improve role assignment quality, not merely render selected fragments more cleanly.

## Artifacts

| 文件 | 用途 |
| --- | --- |
| `predictions_prompt_from_direct_role_assignment.jsonl` | converted prompt-writing rows |
| `predictions_direct_role_plus_det_prompt.jsonl` | role rows plus converted prompt rows |
| `scores_direct_role_plus_det_prompt.jsonl` | official scorer rows |
| `summary_direct_role_plus_det_prompt.txt` | official scorer printed summary |
