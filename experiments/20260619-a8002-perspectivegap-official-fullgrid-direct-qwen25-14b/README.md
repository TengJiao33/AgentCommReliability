# PerspectiveGap Official Full-Grid Direct Baseline

日期：2026-06-19

## 状态

`COMPLETE_OFFICIAL_FULLGRID_DIRECT_BASELINE`

这是一条 PerspectiveGap 官方全量公开 benchmark direct baseline。它不是 SSEAC 方法结果，也不是 PG40 切片结果。

## Run

| 项 | 内容 |
| --- | --- |
| run id | `20260619-a8002-perspectivegap-official-fullgrid-direct-qwen25-14b` |
| machine | A800_2 |
| GPU | `7` |
| model path | `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct` |
| served model id | `qwen2.5-14b-perspectivegap-official-fullgrid` |
| runner | PerspectiveGap official `scripts/run_model_predictions.py` |
| scorer | PerspectiveGap official `scripts/score_predictions.py` |
| upstream commit | `60b1dcaaeeb40619075f6cd8779c47fa4b344391` |
| grid | `110` scenarios x seeds `1,42` x tasks `role_assignment,prompt_writing` |
| wrapper | `scripts/run_perspectivegap_official_fullgrid_a8002.sh` |
| decoding | official runner default request shape; wrapper did not add custom decoding parameters |

## Validation

| 检查 | 结果 |
| --- | ---: |
| prediction rows | `440` |
| score rows | `440` |
| unique prediction keys | `440` |
| unique score keys | `440` |
| scenario count | `110` |
| seeds | `[1, 42]` |
| role assignment requests | `220` |
| prompt writing requests | `220` |
| request status | `ok: 440` |

## Official Scorer Summary

| Task | Strict pass | Net match | Required coverage | Boundary precision | Distractor leakage |
| --- | ---: | ---: | ---: | ---: | ---: |
| role-fragment assignment | `0/220` | `0.1953` | `0.6063` | `0.7714` | `0.3409` |
| free-form prompt writing | `2/220` | `0.2816` | `0.5483` | `0.8970` | `0.3136` |

Combined official pass count:

```text
(role_assignment strict passes + prompt_writing strict passes) / 440
= (0 + 2) / 440
= 0.0045
```

## Interpretation

Qwen2.5-14B direct prompting is a weak official-grid baseline on PerspectiveGap: it has nonzero coverage and precision, but strict task success is almost absent.

This supports using PerspectiveGap full-grid as the public benchmark anchor. It does not prove our method. Beating this direct baseline alone is insufficient for a paper claim; the next full-grid method row still needs to compare against stronger route/system baselines, transparent controls, oracle, and any public leaderboard reference we cite.

## Artifacts

| 文件 | 用途 |
| --- | --- |
| `predictions_official_fullgrid.jsonl` | raw official-runner prediction rows |
| `scores_official_fullgrid.jsonl` | official scorer rows |
| `summary_official_fullgrid.txt` | official scorer printed summary |
| `validation_official_fullgrid.json` | row-count and key validation |
| `run.log` | wrapper metadata and validation tail |
| `runner.stdout.log` | official runner progress |
| `vllm.log` | local vLLM server log |
| `nohup.log` | remote wrapper stdout/stderr |

## Next Step

Run a full-grid no-gold system route:

```text
role_assignment predictions -> deterministic assignment-to-prompt rows -> official scorer
```

The first meaningful method question is whether that route improves over this direct baseline on the same `440`-row official grid without reading oracle-derived fields.
