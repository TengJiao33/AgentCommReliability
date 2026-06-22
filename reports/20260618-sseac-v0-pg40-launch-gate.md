# SSEAC-v0 PG40 Limit5 Launch Gate

日期：2026-06-18

现状修正（2026-06-19）：这个 launch gate 已被后续 PG40 五行真跑吸收。true SSEAC prompt、单卡候选契约和角色计划契约都已经完成五行结果；当前公开主线缺口是补齐同模型公开切片主表，并设计预算感知单卡重排或成对排序器。

## 核心判断

`PG40 true SSEAC prompt` 在当时已经推进到 launch gate。runner、packet、limit5 prompt、baseline 对照和 leak check 都已准备好；2026-06-19 已补上项目惯用的 A800_2 包装运行脚本 `scripts/run_sseac_v0_pg40_a8002.sh`。这个状态当时足以发起远程 A800_2 五行模型预测，但还没有产生方法效果；后续已经被五行 PG40 诊断链路吸收。

修正说明：本报告原先写“只缺 openai-compatible endpoint”。这个词来自 runner 参数名，不属于研究概念。项目实际工作流一直是远程 A800_2 上临时启动 vLLM，再由脚本调用远程机器本地的 `127.0.0.1:<port>/v1`。因此真实缺口是 A800_2 包装运行路径；“端点”只是接口参数名。

这一步很关键，因为 PG40 的强 baseline 已经明确：`utility_density_greedy_after_sseac_compiler` 是 `25/40` strict、utility `0.9825`。任何 SSEAC model row 都要先对它说话。

## 证据链

本地静态检查通过：

```powershell
python -m py_compile scripts\run_sseac_v0_pg40_openai_compatible.py scripts\compile_sseac_v0.py scripts\score_sseac_pg40_compiled.py
```

`limit 5` dry-run prompt 生成成功：

```json
{
  "rows": 5,
  "dry_run_prompts_out": "experiments\\20260618-local-sseac-v0-pg40-launch-gate\\dry_run_prompts_limit5.jsonl"
}
```

prompt 规模：

| Metric | Value |
| --- | ---: |
| rows | 5 |
| prompt chars min | 6507 |
| prompt chars max | 10726 |
| prompt chars avg | 8349.2 |
| source cards min | 7 |
| source cards max | 9 |
| source cards avg | 7.4 |

精确 evaluator-only 字段检查无命中：

```text
required_slots
acceptable_card_ids
slot_id
expected_final_decision
gold_answer
oracle_unit_ids
downstream_scoring_obligations
```

## A800_2 执行路径状态

历史检查只说明本地 Windows 环境没有正在监听的模型服务：

```text
OPENAI_API_KEY=<unset>
OPENAI_BASE_URL=<unset>
VLLM_BASE_URL=<unset>
LOCAL_OPENAI_BASE_URL=<unset>
A8002_BASE_URL=<unset>
```

常用本地 vLLM 端口 `8000`、`8001`、`8002`、`8008`、`8010`、`8047`、`8051`、`8053` 均未监听。因此本轮没有发起模型调用；这不影响远程 A800_2 工作流。

## 对主表的意义

这次 launch gate 把 `PG40` 从“runner 已存在”推进到“5 行小样本可直接发起”。主表缺口已经很具体：需要一个真正的 `SSEAC prompt output` 行，接同一套 compiler 和 scorer，然后和以下 baseline 同表比较：

| Condition | Strict | Utility | Role |
| --- | ---: | ---: | --- |
| `oracle_utility` | 40/40 | 1.0000 | 上界 |
| `utility_density_greedy_after_sseac_compiler` | 25/40 | 0.9825 | 强 baseline |
| `source_ledger_14b_fullprompt_budget_compiled` | 11/40 | 0.8707 | 旧 source-ledger 诊断 |
| `source_ledger_7b_fullprompt_budget_compiled` | 2/40 | 0.6034 | 旧 source-ledger 诊断 |

## 历史压力设计

A800_2 小样本执行时只跑 `limit 5`。第一轮读数只看：

1. JSON schema 是否稳定；
2. compiler error rows 是否为 0；
3. invented card ids / roles 是否出现；
4. candidate priority 是否比旧 source-ledger 更接近 utility-density / oracle；
5. budget、scope、rejection 是否主要由 compiler 稳定执行。

若 `limit 5` 仍低于旧 source-ledger 14B 或 schema 不稳，先改 prompt。若 `limit 5` 出现明确 case-level 正信号，再扩到 40 行并填入 `docs/pg40_tight_budget_numeric_rows.csv`。

## Artifacts

- Run record: `experiments/20260618-local-sseac-v0-pg40-launch-gate/README.md`
- Dry-run prompts: `experiments/20260618-local-sseac-v0-pg40-launch-gate/dry_run_prompts_limit5.jsonl`
- Runner: `scripts/run_sseac_v0_pg40_openai_compatible.py`
- Compiler: `scripts/compile_sseac_v0.py`
- Scorer: `scripts/score_sseac_pg40_compiled.py`
- Numeric table: `docs/pg40_tight_budget_numeric_main_table.md`
