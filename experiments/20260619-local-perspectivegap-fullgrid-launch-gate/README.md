# PerspectiveGap Official Full-Grid Launch Gate

日期：2026-06-19

## 状态

`LAUNCH_GATE_COMPLETED`

这不是模型行为结果。这个目录记录 PerspectiveGap 官方全量公开 benchmark 的本地与远程发射门禁。模型行为结果已落在 `experiments/20260619-a8002-perspectivegap-official-fullgrid-direct-qwen25-14b/`。

## 路线

`PerspectiveGap official full grid`

## 等级

公开 benchmark 主表门禁。

## 核心判断

对外报告主证据必须回到 PerspectiveGap 官方全量网格：`110` scenarios、shuffle seeds `1,42`、`role_assignment` 和 `prompt_writing` 两个任务，共 `440` 个模型请求。PG40 五行和 HSA 三十六行只能作为开发切片、机制诊断或附表材料。

## Purpose

建立 Qwen2.5-14B 在 PerspectiveGap 官方全量网格上的同模型 direct baseline，并为后续 SSEAC / system route 提供公开 benchmark 对照。

## Unit

一个 PerspectiveGap API request：

- `scenario_id`
- `shuffle_seed`
- `task`

官方 full grid 应产生：

- `220` rendered base evaluations
- `440` model prediction rows
- `440` score rows

## Primary Contrast

第一阶段只跑 direct official runner baseline：

```text
Qwen2.5-14B official direct prompt on PerspectiveGap full grid
```

第二阶段才接 system route：

```text
role_assignment system route -> deterministic assignment-to-prompt -> official scorer
```

## Secondary Contrasts

- PerspectiveGap 官方 leaderboard / published model table
- 本地 deterministic oracle
- 后续同模型 system route
- PG40 仅作为 dev/stress slice

## Success Signal

第一阶段成功信号：

- predictions `440` rows
- scores `440` rows
- scenario count `110`
- seeds `[1, 42]`
- task counts: `role_assignment: 220`, `prompt_writing: 220`
- status rows可解释，失败请求保留为 benchmark rows

第二阶段成功信号：

- system route 在 full grid 上超过同模型 direct baseline
- 同时报告 `strict_pass`、`required_coverage`、`boundary_precision`、`distractor_leakage`

## Failure Signal

- full grid 运行不能完成 `440` rows
- prompt-writing scorer 不能离线运行
- endpoint output 大量 API/server errors
- system route 只在 PG40 小切片有效，full grid 不复现

## Invalidation Conditions

- prediction-time 读取 `reference_need_sets`、`distractor_id`、SSEAC `required_slots`、PG40 `recipient_scope` 或任何 oracle-derived fields
- 修改官方 scorer 后报告为官方结果
- 只跑 PG40 或少量 scenarios 却写成公开 benchmark 主结果
- scorer 和 runner commit 与记录不一致
- model ID、endpoint、decoding defaults 或 post-processing 未记录

## Local Checks Completed

| 检查 | 结果 |
| --- | --- |
| upstream commit | `60b1dcaaeeb40619075f6cd8779c47fa4b344391` |
| local upstream tests | `18 passed` |
| local example scorer | role assignment `1/1`; prompt writing `1/1` |
| rebuilt HF evaluations | `220` rows, `110` scenarios, seeds `[1, 42]` |
| oracle assignment-to-prompt smoke | `220` prompt-writing rows generated |
| oracle prompt-writing score | `220/220`, all metrics `1.0000`, leakage `0.0000` |

## Remote Checks Completed

| 检查 | 结果 |
| --- | --- |
| A800_2 workspace | present |
| GPU 7 | free at check time |
| upstream commit | `60b1dcaaeeb40619075f6cd8779c47fa4b344391` |
| remote PerspectiveGap scripts | present |
| remote scorer tokenizer cache | synced locally to `~/.cache/huggingface/hub/models--Qwen--Qwen3.5-0.8B` |
| remote scorer smoke | passed with `HF_HUB_OFFLINE=1` |

## Artifacts

| 文件 | 用途 |
| --- | --- |
| `hf_evaluations_rebuilt.jsonl` | 本地重建的官方 `220` base evaluations |
| `oracle_prompt_from_assignment.jsonl` | oracle assignment 转 prompt-writing 的 `220` rows |
| `oracle_prompt_from_assignment.scores.jsonl` | 官方 scorer 对 oracle prompt-writing 的分数 |
| `scripts/run_perspectivegap_official_fullgrid_a8002.sh` | A800_2 官方 full-grid direct baseline 包装入口 |

## Planned Remote Launch

```bash
cd /data/xuhaoming/yfy/research_workspace
RUN_ID=20260619-a8002-perspectivegap-official-fullgrid-direct-qwen25-14b \
GPU_ID=7 \
PORT=8081 \
MAX_MODEL_LEN=32768 \
GPU_MEMORY_UTILIZATION=0.85 \
RUN_TIMEOUT=28800 \
bash scripts/run_perspectivegap_official_fullgrid_a8002.sh
```

## Expected Remote Outputs

```text
experiments/20260619-a8002-perspectivegap-official-fullgrid-direct-qwen25-14b/
  predictions_official_fullgrid.jsonl
  scores_official_fullgrid.jsonl
  summary_official_fullgrid.txt
  validation_official_fullgrid.json
  run.log
  vllm.log
```

## Current Caveat

The official runner does not expose temperature or max-output-token flags. It sends the repository default request shape, including `MAX_OUTPUT_TOKENS=16000`. This is acceptable for official-runner compatibility, but the run metadata must report that no custom decoding parameter was added by the wrapper.

## Next Step

已完成远程 direct baseline：

| 项 | 结果 |
| --- | --- |
| run id | `20260619-a8002-perspectivegap-official-fullgrid-direct-qwen25-14b` |
| predictions | `440` |
| scores | `440` |
| status | `ok: 440` |
| role assignment | strict `0/220` |
| prompt writing | strict `2/220` |
| combined | `2/440` |

下一步是 full-grid no-gold system route，而不是继续扩 PG40 小切片。
