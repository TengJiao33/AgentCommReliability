# Hybrid Micro-Gated Pre-KV 实现记录

## 做法

1. 实现基于 `scripts/run_mca_pre_kv_then_mad.py`。每道题仍然同时生成 no-channel first、raw Pre-KV first、no-channel + MAD 和 raw Pre-KV + MAD。

2. 当参数 `--pre-state-stage early_plan` 与 `--visible-commitment-mode micro` 同时启用时，发送方早期草稿被要求写成 `REPRESENTATION`、`FIRST_MOVE`、`CHECK` 三个短字段。

3. 发送方生成 micro commitment 时保留 live KV。该 KV 仍作为 raw Pre-KV receiver 的历史状态；字段文本也作为可见短承诺候选。

4. 在把可见短承诺展示给 receiver 前，脚本检查答案标记。若短承诺包含 `<answer>`、`Final answer:`、`####` 或 `\boxed{...}`，该可见短承诺不会展示给 receiver。

5. raw Pre-KV first 仍按原流程生成：receiver prompt 接在 sender retained KV 后面，生成第一轮答案。

6. no-channel first 使用相同题目、相同 agent 和匹配种子，但不接入 sender KV。

7. 第一轮选择门控由 `--first-round-selection-policy pre_kv_unanimous_else_no_channel` 控制。脚本先归一化 3 个 raw Pre-KV first answers。

8. 如果 3 个 Pre-KV answers 一致，selected first 使用 raw Pre-KV first outputs；如果 Pre-KV answers 不一致，selected first 回退到 no-channel first outputs。

9. `selected + MAD` 不重新生成新 debate。脚本已经生成 no-channel + MAD 和 raw Pre-KV + MAD；selected source 选择哪个第一轮来源，就读取对应的 MAD final 作为 selected + MAD。

10. record 同时保存 raw metrics 和 selected metrics，避免门控结果覆盖 raw Pre-KV 读数。

## 工程细节

- 实现文件：`scripts/run_mca_pre_kv_then_mad.py`。
- 实验目录：`experiments/20260707-a8002-mca-matrix-hybrid-micro-gated-gpu1-qwen25-7b/`。
- 启动脚本：`run_remote_serial_hybrid_micro_gated.sh`。
- 主 run id：`20260707-a8002-gpu1-mca-matrix-hybrid-micro-gated-disagreement-qwen25-7b`、`20260707-a8002-gpu1-mca-matrix-hybrid-micro-gated-gold-contrast-qwen25-7b`。
- 可见短承诺参数：`--visible-commitment-mode micro`。
- 可见短承诺启用条件：与 `--pre-state-stage early_plan` 同时使用。
- 发送方字段：`REPRESENTATION`、`FIRST_MOVE`、`CHECK`。
- 可见短承诺用途：保留在 sender KV state；同时作为可见提示展示给 paired Pre-KV receiver。
- 答案标记拦截：若短承诺包含 `<answer>`、`Final answer:`、`####`、`\boxed{...}`，则不展示给 receiver。
- 第一轮选择门控参数：`--first-round-selection-policy pre_kv_unanimous_else_no_channel`。
- 门控规则：所有 Pre-KV agents 归一化后一致时使用 raw Pre-KV first-round outputs；否则回退到 no-channel first-round outputs。
- raw metrics 仍然记录：no-channel first、raw Pre-KV first、no-channel + MAD、raw Pre-KV + MAD。
- 门控指标：selected first、selected + MAD、selected source counts。
- `selected + MAD` 不额外生成新 debate；它在已有 no-channel + MAD 和 raw Pre-KV + MAD 之间，按 selected first source 选择。

## 结果

| 检查项 | 状态 |
| --- | --- |
| structured micro pre-state prompt 单测 | 覆盖 |
| explicit answer marker blocking 单测 | 覆盖 |
| Pre-KV unanimous gate 接受 unanimous Pre-KV | 覆盖 |
| Pre-KV split 时 gate 回退 no-channel | 覆盖 |

## 备注

该实现记录的是机制落地位置和记录口径。运行读数记录在 `2026-07-07-hybrid-micro-gated-failure-audit.md` 和 `2026-07-07-hybrid-micro-gated-stop-note.md`。
