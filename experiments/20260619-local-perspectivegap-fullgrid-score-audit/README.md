# PerspectiveGap Full-Grid Score Audit

日期：2026-06-19

## 状态

`COMPLETE_EVALUATOR_AUDIT`

这个目录复核 `20260619-a8002-perspectivegap-official-fullgrid-direct-qwen25-14b` 的低分到底来自模型行为、脚本调用，还是 scorer/parser 问题。

## 结论

低 strict pass 不是脚本算错。官方 scorer 本地重跑后 JSON 结果与远端 score JSONL 完全一致；同一个 scorer 在 oracle full-grid 上得到 role assignment `220/220`、prompt writing `220/220`。

Direct baseline 的低分主要来自模型选择错误：

- role assignment 输出格式没崩：`220/220` 都是可解析 JSON，role keys 全匹配，invalid fragment id 为 `0`。
- 但没有一行所有 role 的 fragment set 全对。
- prompt writing 也不是 header parser 崩：`218/220` 行 exact headers，`0` 行无 section。
- prompt writing 常见错误是 missing required fragment，部分还夹带 extra/distractor。

## Rechecks

| 检查 | 结果 |
| --- | --- |
| local official scorer rerun | summary 数字完全一致 |
| score JSON structural equality | `True` |
| full-grid oracle role assignment | `220/220` |
| full-grid oracle prompt writing | `220/220` |
| direct prediction rows | `440` |
| direct score rows | `440` |
| direct request status | `ok: 440` |

## Direct Role Assignment Audit

| 项 | 数字 |
| --- | ---: |
| rows | `220` |
| strict pass | `0/220` |
| direct JSON parse valid | `220/220` |
| exact role keys | `220/220` |
| invalid fragment ids | `0` |
| loose all-role exact rows | `0/220` |
| role instances exact | `155/836` |
| rows with missing and extra | `152` |
| rows with missing only | `57` |
| rows with full coverage but extra only | `11` |
| rows with distractor leak | `54` |

Example `pg_000__seed_1`:

```text
gold coder    = f1,f5,f6,f7
gold reviewer = f3,f4,f5
model coder    = f6,f7
model reviewer = f2,f3,f4,f5
```

Here `f2` is the distractor. This is a concrete selection failure, not a parser failure.

## Direct Prompt-Writing Audit

| 项 | 数字 |
| --- | ---: |
| rows | `220` |
| strict pass | `2/220` |
| exact headers | `218/220` |
| no-section rows | `0` |
| role sections exact | `163/836` |
| rows with missing only | `127` |
| rows with missing and extra | `91` |
| rows with distractor leak | `42` |

Tag-output salvage check:

| 项 | 数字 |
| --- | ---: |
| rows containing `<f...>` tags | `105` |
| tag-exact rows under non-official salvage | `0/105` |
| tag-exact role sections | `97/441` |

This means the prompt-writing loss is not only because the model sometimes prints fragment IDs instead of full text. Even under a non-official tag parser, no tag-only row becomes exact.

## Artifacts

| 文件 | 用途 |
| --- | --- |
| `scores_rescored_local.jsonl` | local official scorer rerun over direct predictions |
| `summary_rescored_local.txt` | local rerun summary |
| `oracle_role_and_prompt_predictions.jsonl` | full-grid oracle predictions for both tasks |
| `oracle_role_and_prompt_scores.jsonl` | official scorer output for oracle predictions |
| `oracle_role_and_prompt_summary.txt` | oracle scorer summary |

## Interpretation

The result is a true official-grid direct-baseline failure under the recorded runner, scorer, model route, and default decoding. It does not prove Qwen2.5-14B cannot do better with a stronger no-gold system route or different prompt surface.

The next experiment must improve role-fragment assignment itself. A deterministic prompt writer cannot rescue wrong assignments.
