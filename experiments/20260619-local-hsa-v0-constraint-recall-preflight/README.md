# HSA-v0 constraint_recall 预检

日期：2026-06-19

## 目的

`focused_recall` 保持 compiler `8/9`，并把 extra final cards 从 `19` 降到 `12`。唯一失败行仍是 `hiddenbench_evacuation_west_city` base：模型保留了 `hb01_shared_3`，但漏掉约束卡 `hb01_hidden_2`。

本次预检准备 `constraint_recall`：在 focused recall 基础上，额外要求保留 verified、final_decider-visible 的 blocker 或 background constraint，即使它们不单独排除所选答案。

## 实验问题

`constraint_recall` 能否补回剩余约束卡，同时保持 extra final cards 低于 `recall_sweep` 的 `19`。

## 主对照

| 条件 | Strict | Base strict | Perturb strict | Slot recall | Extra final cards | Forced commitment |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| recall_sweep compiler | 8/9 | 0.6667 | 1.0000 | 0.7963 | 19 | 0.3333 |
| focused_recall compiler | 8/9 | 0.6667 | 1.0000 | 0.8148 | 12 | 0.5556 |

## 成功信号

- strict 超过 `8/9`，或至少保持 `8/9`。
- slot recall 高于 `0.8148`。
- extra final cards 低于 `19`，最好接近或低于 `12`。
- perturbation strict 保持 `6/6`。

## 失败信号

- strict 回落到 `7/9` 或更低。
- extra final cards 回到 `19` 附近。
- 输出解析失败。

## 失效条件

- prompt 泄漏 `gold_answer`、`required_slots`、`acceptable_card_ids`、`expected_final`、`expected_final_decision`、`required_cards`、`oracle` 或评分字段。
- 输出目录复用旧结果。
- GPU 或远程服务失败。
- 远程脚本和本地脚本不同步。

## 本地预检

```text
dry_run_prompts_out: experiments/20260619-local-hsa-v0-constraint-recall-preflight/dry_run_constraint_recall.jsonl
rows: 9
prompt chars: 7949 到 8444，平均 8141.6
```

`py_compile` 通过。泄漏检查未命中金标或评分字段。

## 计划远程运行

默认使用 GPU 7。若 GPU 7 忙，暂停，不自动切到前面的卡。

```bash
cd /data/xuhaoming/yfy/research_workspace
PROMPT_CONTRACT=constraint_recall GPU_ID=7 PORT=8081 RUN_ID=20260619-a8002-hsa-v0-constraint-recall-full9-qwen25-14b LIMIT=0 GPU_MEMORY_UTILIZATION=0.75 MAX_MODEL_LEN=8192 MAX_TOKENS=3072 RUN_TIMEOUT=1800 bash scripts/run_hsa_v0_sseac_a8002.sh
```

