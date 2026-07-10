# Hybrid Micro-Gated 运行停止记录

## 做法

1. 停止前的 hybrid micro-gated run 正在 `mca_disagreement_v1` 上运行，通信对象是 micro commitment 文本加 raw unfinished KV。

2. 运行每题生成 no-channel first、raw hybrid Pre-KV first、gated selected first、no-channel + MAD、raw hybrid + MAD 和 gated selected + MAD。

3. sender pre-state 仍使用 64 个标记的 micro commitment，字段为 `REPRESENTATION`、`FIRST_MOVE`、`CHECK`。快照显示 51 个 sender outputs 中只有 2 个写到 `CHECK` 字段。

4. selected first 和 selected + MAD 由门控在已生成分支之间选择。它们不额外调用模型生成新的第一轮或新的 debate。

5. 停止时终止进程链 `1938713 -> 1938714 -> 1938715`，保留已经写出的 27 条 partial result。

6. 停止后在同一 GPU 上启动 latent-rounds disagreement run。该替换运行不再展示同伴文本，不再使用 `REPRESENTATION/FIRST_MOVE/CHECK`，不拼接同伴 KV，也不续写半截 assistant completion。

7. latent-rounds 新 run 的第 0 轮让每个 agent 在答题前私下思考并捕获 latent activation state；之后的轮次接收同伴 activation 的均值；final 阶段才输出最终答案。

## 工程细节

- 停止 run：`20260707-a8002-gpu1-mca-matrix-hybrid-micro-gated-disagreement-qwen25-7b`。
- 停止进程链：`1938713 -> 1938714 -> 1938715`。
- 替换 run：`20260707-a8002-gpu1-mca-latent-rounds-disagreement-qwen25-7b`。
- hybrid micro-gated protocol 字段：`REPRESENTATION`、`FIRST_MOVE`、`CHECK`。
- sender 输出审计：51 个 sender outputs；`REPRESENTATION` present 51；`FIRST_MOVE` present 28；`CHECK` present 2；likely truncated 46。
- 运行对象：raw hybrid Pre-KV first、gated selected first、raw hybrid + MAD、gated selected + MAD。
- selected first 和 selected + MAD 使用 gate 在已生成分支之间选择，没有额外生成新 debate。
- 替换 runner：`scripts/run_mca_latent_rounds.py`。
- latent-rounds 运行结构：第 0 轮每个 agent 在答题前私下思考并捕获 latent activation state；之后的轮次接收 mean(peer activation states)，不展示 peer text；final 阶段输出最终答案。
- latent-rounds 运行状态：新 run 启动时进入 `row 1/221`，并完成该 row 的 baseline private latent rounds。

## 结果

| 分支 | 正确数 |
| --- | ---: |
| no-channel first | 14/27 |
| raw hybrid Pre-KV | 13/27 |
| gated selected first | 16/27 |
| no-channel + MAD | 13/27 |
| raw hybrid + MAD | 14/27 |
| gated selected + MAD | 15/27 |

| 对照 | 差值 |
| --- | ---: |
| raw hybrid Pre-KV - no-channel first | -1 |
| raw hybrid + MAD - no-channel + MAD | +1 |

## 备注

停止时的通信对象为 partial sketch + raw unfinished KV。多个 `BaC_to_W` case 涉及算术、顶点配对或代数验证错误。latent-rounds 替换运行去掉了同伴文本展示、`REPRESENTATION/FIRST_MOVE/CHECK` 显式字段、同伴 KV 拼接和半截 assistant completion 续写。
