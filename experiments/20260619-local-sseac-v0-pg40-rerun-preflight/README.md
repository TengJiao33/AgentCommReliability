# PG40 SSEAC-v0 五行重跑预检

日期：2026-06-19

## 目的

验证 `PG40 tight-budget` 上 true SSEAC prompt 的五行小样本是否能稳定输出结构化 candidate units，并形成 `structured_no_compiler` 与 `compiled` 的成对比较。

## 单元

- packet：`experiments/20260618-local-sseac-v0-pg40-adapter/sseac_pg40_packet.jsonl`
- limit：前 5 行
- 远程：`A800_2:/data/xuhaoming/yfy/research_workspace`
- 默认 GPU：`7`

## 主对照

`compiled` 对 `structured_no_compiler` 的成对差。

## 次要对照

- `utility_density_greedy + SSEAC compiler`
- `source_ledger_14b_fullprompt_budget_compiled`
- `oracle_utility`

## 成功信号

- 五行都能解析成 JSON 或仅有可恢复解析警告。
- budget pass 接近 `1.0`。
- utility 或 strict 至少接近旧 `source_ledger_14b_fullprompt_budget_compiled` 的方向。
- `compiled` 相比 `structured_no_compiler` 有可解释收益。

## 失败信号

- schema 大量崩溃。
- budget pass 继续崩。
- coverage 因过度保守明显坍塌。
- 编译后与未编译无可解释差异。

## 失效条件

- GPU 或服务启动失败。
- 远程脚本、packet、scorer 与本地不同步。
- prompt 泄漏 `required_slots`、`reference_need_sets`、`gold_answer` 或其他评分字段。
- 输出目录复用旧结果。

## 本地预检

```text
dry_run_prompts_out: experiments/20260619-local-sseac-v0-pg40-rerun-preflight/dry_run_prompts_limit5.jsonl
rows: 5
prompt_chars: 6507 到 10726
```

`rg` 检查未发现金标槽位或评分字段泄漏；命中的 `oracle` 只来自提示中的“不给 oracle required slots”边界说明。

## 计划远程运行

```bash
cd /data/xuhaoming/yfy/research_workspace
GPU_ID=7 PORT=8076 RUN_ID=20260619-a8002-sseac-v0-pg40-limit5-gpu7-rerun-qwen25-14b LIMIT=5 GPU_MEMORY_UTILIZATION=0.75 MAX_MODEL_LEN=8192 RUN_TIMEOUT=1800 bash scripts/run_sseac_v0_pg40_a8002.sh
```

