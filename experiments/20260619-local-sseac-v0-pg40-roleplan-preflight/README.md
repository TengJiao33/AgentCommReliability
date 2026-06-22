# PG40 SSEAC-v0 角色内排序契约预检

日期：2026-06-19

## 目的

在单卡候选契约基础上，增加 `role_plans`：每个角色先做预算内草案，并把每个可见 verified support card 标成 `select`、`backup` 或 `omit`。这次复跑同样五行，目标是判断 role-specific ranking 是否能把 strict 从 `1/5` 继续往上推，并让 utility 接近或超过旧内部基线 `0.8707`。

## 变更范围

只修改 `scripts/run_sseac_v0_pg40_openai_compatible.py` 的提示词和响应 schema。

不修改：

- `scripts/compile_sseac_v0.py`
- `scripts/score_sseac_pg40_compiled.py`
- `experiments/20260618-local-sseac-v0-pg40-adapter/sseac_pg40_packet.jsonl`
- `experiments/20260618-local-perspectivegap-tight-budget-v0/tight_budget_rotated20.jsonl`

## 主对照

`roleplan compiled` 对上一轮 `card-unit compiled`：

| 条件 | Strict | Coverage | Precision | Budget pass | Utility |
| --- | ---: | ---: | ---: | ---: | ---: |
| card-unit compiled | 1/5 | 0.6667 | 0.8571 | 1.0000 | 0.8155 |

## 成功信号

- strict 超过 `1/5`。
- utility 接近或超过 `0.8707`。
- budget pass 保持 `1.0000`。
- coverage 不明显低于 `0.6667`。

## 失败信号

- JSON 因输出过长解析失败。
- strict 仍为 `1/5` 或下降。
- utility 仍明显低于 `0.8707`。
- role plan 只产生解释文本，没有改善 `candidate_units`。

## 失效条件

- prompt 泄漏 `required_slots`、`reference_need_sets`、`gold_answer`、`oracle_utility`、`expected_final`、`downstream_scoring` 或 `target_need_sets`。
- 输出目录复用旧结果。
- GPU 或远程服务失败。

## 本地预检

```text
dry_run_prompts_out: experiments/20260619-local-sseac-v0-pg40-roleplan-preflight/dry_run_prompts_limit5.jsonl
rows: 5
prompt_chars: 7985 到 12204
```

`py_compile` 通过。`rg` 检查未命中金标或评分字段。由于输出 schema 增加 `role_plans`，远程运行计划使用 `MAX_TOKENS=3072`。

## 计划远程运行

```bash
cd /data/xuhaoming/yfy/research_workspace
GPU_ID=7 PORT=8078 RUN_ID=20260619-a8002-sseac-v0-pg40-limit5-roleplan-qwen25-14b LIMIT=5 GPU_MEMORY_UTILIZATION=0.75 MAX_MODEL_LEN=8192 MAX_TOKENS=3072 RUN_TIMEOUT=1800 bash scripts/run_sseac_v0_pg40_a8002.sh
```

