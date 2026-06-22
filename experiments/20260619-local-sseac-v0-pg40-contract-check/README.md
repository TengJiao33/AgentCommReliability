# PG40 SSEAC-v0 提示契约检查

日期：2026-06-19

## 目的

角色计划契约复跑后，结果低于单卡候选契约。为避免后续远程运行误用已退休契约，runner 改为显式选择提示契约：

- 默认：`cardunit`
- 可选诊断：`roleplan`

## 修改范围

| 文件 | 修改 |
| --- | --- |
| `scripts/run_sseac_v0_pg40_openai_compatible.py` | 增加 `--prompt-contract {cardunit,roleplan}`，默认 `cardunit` |
| `scripts/run_sseac_v0_pg40_a8002.sh` | 增加 `PROMPT_CONTRACT` 环境变量并传给 runner |

## 本地检查

```text
python -m py_compile scripts\run_sseac_v0_pg40_openai_compatible.py
```

通过。

Dry-run 结果：

| 契约 | 输出 | 行数 | prompt 长度范围 | 平均长度 | 检查 |
| --- | --- | ---: | ---: | ---: | --- |
| `cardunit` | `dry_run_cardunit.jsonl` | 5 | 7064 到 11283 | 8906.2 | 不含 `role_plans` 字段 |
| `roleplan` | `dry_run_roleplan.jsonl` | 5 | 8010 到 12229 | 9852.2 | 含 `role_plans` 字段 |

远程同步后检查：

```text
py_compile 通过
bash -n scripts/run_sseac_v0_pg40_a8002.sh 通过
远程脚本包含 PROMPT_CONTRACT / --prompt-contract / prompt_contract
```

## 当前运行规则

常规 PG40 五行运行默认走单卡候选契约：

```bash
GPU_ID=7 PORT=<free-port> RUN_ID=<run-id> LIMIT=5 GPU_MEMORY_UTILIZATION=0.75 MAX_MODEL_LEN=8192 bash scripts/run_sseac_v0_pg40_a8002.sh
```

只有复现或诊断角色计划契约时才显式传：

```bash
PROMPT_CONTRACT=roleplan GPU_ID=7 PORT=<free-port> RUN_ID=<run-id> LIMIT=5 GPU_MEMORY_UTILIZATION=0.75 MAX_MODEL_LEN=8192 MAX_TOKENS=3072 bash scripts/run_sseac_v0_pg40_a8002.sh
```

