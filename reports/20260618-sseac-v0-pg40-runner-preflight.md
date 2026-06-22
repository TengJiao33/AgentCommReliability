# SSEAC-v0 PG40 Runner Preflight

## 核心判断

`PG40` 上的 `ours_sseac_v0` 现在有了可运行的 openai-compatible 模型入口。新增 runner 能把 SSEAC packet 转成 prompt，让模型直接输出 `candidate_units`，再交给现有 compiler 和 scorer。

这一步是 pipeline preflight，尚未产生方法效果。它的价值是把下一次小样本模型 run 从“想法”推进到“可执行命令”。

## 做了什么

新增脚本：`scripts/run_sseac_v0_pg40_openai_compatible.py`。

脚本输入：`experiments/20260618-local-sseac-v0-pg40-adapter/sseac_pg40_packet.jsonl`。

脚本输出：每行包含 `packet_id`、`model`、`task=sseac_v0_pg40_candidate_units` 和 `response`。其中 `response` 应包含 `option_states`、`candidate_units`、`proposed_rejections`、`final_decision`。

脚本支持 `--dry-run-prompts-out`，用于在调用模型前审 prompt。

## Preflight 结果

本地检查通过：

```powershell
python -m py_compile scripts/run_sseac_v0_pg40_openai_compatible.py scripts/compile_sseac_v0.py scripts/score_sseac_pg40_compiled.py
```

全量 `40` 行 dry-run prompt 生成成功：

```json
{
  "rows": 40,
  "dry_run_prompts_out": "experiments\\20260618-local-sseac-v0-pg40-runner-preflight\\dry_run_prompts_full40.jsonl"
}
```

prompt 长度范围是 `6507` 到 `16081` 字符，平均 `12249.75` 字符；每行 source cards 数量为 `7` 到 `13`，平均 `10.25`。

## 边界检查

全量 prompt 中没有命中这些 oracle 字段：

```text
required_slots
acceptable_card_ids
slot_id
expected_final_decision
```

prompt 会给模型 `recipient_scope`、`verification_state`、`evidence_type`、`cost` 和内容摘要。这符合 source/scope admission 设定，也限定了测量对象：给定 source/scope ledger 后的预算化准入。纯文本恢复所有角色目标属于另一条更难的任务线。

## 对主表的意义

之前 PG40 的 SSEAC 链路停在 adapter/compiler/scorer 与旧预测转换。现在缺口收窄到模型小样本结果：跑一个 `--limit 5` 的 SSEAC proposer，然后接 `compile_sseac_v0.py` 和 `score_sseac_pg40_compiled.py`。

主表判断仍要看强 baseline。当前已知 `utility_density_greedy` 是 `25/40` strict、utility `0.9825`；旧 `source_ledger_14b_compiled` 是 `11/40`、utility `0.8707`。新的 runner 只有在模型输出经过 compiler 后逼近或超过这些 baseline，才会产生方法层面的正信号。

## 下一步压力

下一步建议只跑小样本，不开全量 GPU。成功信号是：

1. 模型输出 JSON schema 稳定；
2. compiler error rows 为 `0`；
3. budget / scope 违规主要由 compiler 拦住；
4. 至少在若干具体 case 上，candidate priority 比旧 source-ledger 输出更贴近 utility-density / oracle 选择。

小样本如果连 schema 和 candidate priority 都不稳，应该先改 prompt，暂缓扩到 40 行。
