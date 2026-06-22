# PG40 Pairwise Role-Card Selector 五行运行记录

日期：2026-06-20

## 状态

`DIAGNOSTIC_NEGATIVE_RESULT`

这次运行把 pairwise role-card selector 从 launch preflight 推到 GPU 五行真跑。模型只看 `roles`、`role_budgets`、card id、card cost 和 card text，不读取 PG40 `recipient_scope`、required slots、need sets、utility gold 或目标角色标注。

核心结果很清楚：管道可用，模型输出可解析，但 no-scope pairwise prompt 没有学会 PG40 的 source-to-recipient 转换。模型按卡片文本里的表面 actor / role 语义分配，目标 recipient 经常错位；compiler 因此拦下越界候选，最后没有可用 admitted units。

## 目的

上一轮 no-scope 规则 selector 显示，手写 lexical / cost 规则无法解决 role-card affinity。这个真跑要回答：如果让 Qwen2.5-14B 逐对判断 `role, card -> assign`，是否能在不读 oracle-derived scope 的情况下超过 card-unit compiled 的 `1/5`、utility `0.8155`。

成功信号是 parse clean、budget pass 稳定、coverage/utility 超过 card-unit compiled，并出现超过 `1/5` strict 的五行正例。失败信号是 assignment 太稀、送错 recipient、compiler 拦截后 coverage 归零，或结果低于 source-ledger / transparent baselines。

## 启动记录

- 主机：`A800_2` (`10-116-90-20`)
- 远程工作区：`/data/xuhaoming/yfy/research_workspace`
- 本地镜像：`experiments/20260620-a8002-pg40-pairwise-selector-limit5-qwen25-14b/`
- 模型路径：`/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- 服务模型名：`qwen2.5-14b-pg40-pairwise-selector`
- 显卡：`7`
- 端口：`8081`
- 输入包：`experiments/20260618-local-sseac-v0-pg40-adapter/sseac_pg40_packet.jsonl`
- 本次运行输入包：`packet_limit5.jsonl`
- 行数：`5`
- 温度：`0`
- 最大生成长度：`3072`
- 最大上下文长度：`8192`
- 显存利用：`0.75`

远程门禁：

- GPU 7 运行前空闲：`4 MB` used，`81149 MB` free，util `0%`。
- 端口 `8081` 运行前未见监听。
- 远程 `python -m py_compile` 通过。
- 远程 `bash -n scripts/run_pg40_pairwise_role_card_selector_a8002.sh` 通过。
- 运行结束后 GPU 7 回到 `4 MB` used，util `0%`。

命令：

```bash
cd /data/xuhaoming/yfy/research_workspace
GPU_ID=7 PORT=8081 RUN_ID=20260620-a8002-pg40-pairwise-selector-limit5-qwen25-14b LIMIT=5 GPU_MEMORY_UTILIZATION=0.75 MAX_MODEL_LEN=8192 MAX_TOKENS=3072 RUN_TIMEOUT=2400 bash scripts/run_pg40_pairwise_role_card_selector_a8002.sh
```

## 结果摘要

| 条件 | Strict | Coverage | Precision | Budget pass | Utility | Raw utility | Exact role |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| pairwise model-only | 0/5 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 |
| pairwise + compiler | 0/5 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 |

编译摘要：

| 条件 | rows | ok_rows | forced commitment | downstream ok | scope violations prevented |
| --- | ---: | ---: | ---: | ---: | ---: |
| model-only | 5 | 5 | 1.0000 | 1.0000 | 0 |
| compiler | 5 | 5 | 1.0000 | 0.0000 | 14 |

Triage 摘要见 `triage_pairwise_limit5.json`：

| 指标 | 值 |
| --- | ---: |
| rows | 5 |
| parse ok rows | 5 |
| prompt leak rows | 0 |
| raw assignments | 22 |
| admitted units | 0 |
| scope violations prevented | 14 |
| satisfied slots | 0 |

## 具体失败面

模型不是空输出，也不是 JSON parser 失败。五行都能抽出 assignments，但 assignments 跟 gold target recipient 错开。

例子：

- `pg_000__seed_1`：模型给 `coder f1/f6/f7`、`reviewer f3/f4`；期望是 `coder::f3`、`coder::f5`、`reviewer::f1`、`reviewer::f5`。compiler 拦下 `coder f1`、`coder f6`、`reviewer f3`、`coder f7` 等越界项。
- `pg_000__seed_42`：模型给 `coder f1/f3`、`reviewer f7`；期望是 `coder::f6`、`coder::f7`、`reviewer::f2`、`reviewer::f3`。
- `pg_003__seed_1`：模型给 `dispatcher f2/f5`、`coder f3`、`reviewer f4/f8/f9`；期望是 `dispatcher::f1/f4/f6`、`coder::f2`、`reviewer::f1/f3/f6`。

这说明 current prompt 的输入接口不够。PG40 `source_rotated_scope` 里的 target recipient 常常不能从卡片里的表面 actor role 直接推出；只给 role 名、预算和卡片文本，会诱导模型做 actor-affinity，而非 recipient-affinity。

## 证据等级

这是干净的诊断负结果。它能支持的窄判断是：

- pairwise 脚本、A800_2 wrapper、compiler、scorer 和本地拉取流程可用；
- no-scope pairwise prompt 在五行上未超过 card-unit compiled；
- 失败来自 role/recipient interface mismatch，而非 parser、GPU、同步或 scorer 事故；
- 当前 pairwise 分支不应扩 full40。

它不能支持的判断：

- 不能说 Qwen2.5-14B 无法做 PG40 role assignment；
- 不能说 SSEAC compiler 导致失败；
- 不能说 PG40 方法线完全退休。

## 关键产物

| 文件 | 用途 |
| --- | --- |
| `packet_limit5.jsonl` | 本次五行输入包 |
| `predictions_pairwise.jsonl` | 模型 pairwise assignments 原始结构输出 |
| `compiled_model_only.jsonl` | model-only 编译态 |
| `compiled_compiler.jsonl` | hard executor 编译态 |
| `scores_model_only.jsonl` | model-only PG40 评分 |
| `scores_compiler.jsonl` | compiler PG40 评分 |
| `summary_model_only.md` | model-only 摘要 |
| `summary_compiler.md` | compiler 摘要 |
| `triage_pairwise_limit5.json` | assignment / rejection / slot triage |
| `run.log` | A800_2 wrapper 日志 |
| `runner.stdout.log` | pairwise runner stdout |
| `vllm.log` | vLLM 服务日志 |

## 下一步

不扩 full40 pairwise selector。下一步应先修任务接口：

1. 回到 PerspectiveGap official role-assignment setting，让模型看到官方 scenario / role descriptions，并只输出官方允许的 role assignment。
2. 或者为 PG40 构造一个不含 oracle-derived target sets 的 public recipient-context prompt，让模型判断信息应该给谁，避免只按文本中的 actor 角色贴标签。
3. 保留现有 pairwise runner 作为接口实验脚手架，但不要把当前 no-scope prompt 当方法候选。
