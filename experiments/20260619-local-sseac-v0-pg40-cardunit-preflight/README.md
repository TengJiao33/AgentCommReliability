# PG40 SSEAC-v0 单卡候选契约预检

日期：2026-06-19

## 目的

针对上一轮 PG40 true prompt limit5 的失败面，最小化修改提示词：要求每个 candidate unit 只包含一个 card，并按 role 分别排序。复跑同样五行，检查 coverage 是否回升，同时 budget pass 是否保持。

## 变更范围

只修改 `scripts/run_sseac_v0_pg40_openai_compatible.py` 的提示词。compiler、scorer、packet 不变。

## 本地预检

```text
dry_run_prompts_out: experiments/20260619-local-sseac-v0-pg40-cardunit-preflight/dry_run_prompts_limit5.jsonl
rows: 5
prompt_chars: 6925 到 11144
```

`py_compile` 通过。`rg` 检查未命中 `required_slots`、`reference_need_sets`、`gold_answer`、`oracle_utility`、`expected_final`、`downstream_scoring` 或 `target_need_sets`。

## 计划远程运行

```bash
cd /data/xuhaoming/yfy/research_workspace
GPU_ID=7 PORT=8077 RUN_ID=20260619-a8002-sseac-v0-pg40-limit5-cardunit-qwen25-14b LIMIT=5 GPU_MEMORY_UTILIZATION=0.75 MAX_MODEL_LEN=8192 RUN_TIMEOUT=1800 bash scripts/run_sseac_v0_pg40_a8002.sh
```

