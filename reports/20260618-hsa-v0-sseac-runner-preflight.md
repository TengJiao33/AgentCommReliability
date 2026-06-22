# HSA-v0 SSEAC Runner Preflight

## 核心判断

`HSA-v0` 现在也有了可发起模型预测的 runner。PG40 与 HSA-v0 两条主线都已进入“等待小样本模型输出”的状态。

这一步是 prompt/run preflight，没有方法结果。它把下一轮实验风险从“没有入口”缩小到“模型是否能稳定输出 candidate_units”。

## 做了什么

新增脚本：`scripts/run_hsa_v0_sseac_openai_compatible.py`。

脚本输入：`experiments/20260618-local-hsa-v0-sseac-adapter/hsa_v0_packet.jsonl`。

脚本输出：每行包含 `packet_id`、`model`、`task=hsa_v0_sseac_candidate_units` 和 `response`。`response` 应包含 `option_states`、`candidate_units`、`proposed_rejections`、`final_decision`。

脚本支持 `--dry-run-prompts-out`，用于模型调用前审 prompt。

## Preflight 结果

本地检查通过：

```powershell
python -m py_compile scripts/run_hsa_v0_sseac_openai_compatible.py scripts/build_hsa_v0_sseac_packet.py scripts/score_hsa_v0_compiled.py scripts/compile_sseac_v0.py
```

全量 `9` 行 dry-run prompt 生成成功：

```json
{
  "rows": 9,
  "dry_run_prompts_out": "experiments\\20260618-local-hsa-v0-sseac-runner-preflight\\dry_run_prompts_full9.jsonl"
}
```

prompt 长度范围是 `5499` 到 `5994` 字符，平均 `5691.56` 字符；每行 source cards 数量为 `7` 到 `8`，平均 `7.67`。

## 边界检查

全量 prompt 中没有命中这些 evaluator-only 字段：

```text
required_slots
acceptable_card_ids
slot_id
expected_final_decision
gold_answer
oracle_unit_ids
downstream_scoring_obligations
```

prompt 给模型的字段包括 answer options、roles、final_decider、role_budgets、source_cards、recipient_scope、verification_state、evidence_type、cost 和事实内容。gold、required slots、oracle units 和 scoring obligations 全部留在 scorer 侧。

## 对主表的意义

HSA-v0 现在有三层本地链路：adapter/scorer smoke、透明 baseline 闭环、prompt runner preflight。它已经能承接小样本模型输出。

当前最关键的 caveat 来自 `all_scoped_verified`：answer strict 可以达到 9/9，同时产生 24 张 extra final cards。后续主表必须把 over-admission / evidence discipline 放在 answer strict 旁边，否则这个 benchmark 会被“全塞进去”策略掩盖。

## 下一步压力

有 openai-compatible endpoint 后，先跑 `--limit 3`。成功信号应包括：

1. JSON schema 稳定；
2. compiler error rows 为 `0`；
3. base rows 有合理 slot recall；
4. perturbation rows 能输出或被 compiler 推到 `insufficient_evidence`；
5. extra final cards 低于 `all_scoped_verified`。
