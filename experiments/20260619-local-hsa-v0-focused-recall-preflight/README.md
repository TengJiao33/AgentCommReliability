# HSA-v0 focused_recall 预检

日期：2026-06-19

## 目的

`recall_sweep` 把 HSA compiler strict 从 `7/9` 提到 `8/9`，但 extra final cards 从 `8` 升到 `19`。本次预检准备一个更窄的 `focused_recall` 契约：保留答案级证据扫描和单卡候选单元，但只把所选答案的支持卡、其他答案的阻断卡、必要背景约束送进 candidate units。

## 实验问题

`focused_recall` 能否在保持 `recall_sweep` 的 strict / base strict 增益时，降低 extra final cards。

## 主对照

| 条件 | Strict | Base strict | Perturb strict | Slot recall | Extra final cards | Forced commitment |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline compiler | 7/9 | 0.3333 | 1.0000 | 0.7130 | 8 | 0.7778 |
| recall_sweep compiler | 8/9 | 0.6667 | 1.0000 | 0.7963 | 19 | 0.3333 |

## 成功信号

- strict 保持或超过 `8/9`。
- base strict 至少保持 `2/3`。
- perturbation strict 保持 `6/6`。
- extra final cards 明显低于 `19`。

## 失败信号

- strict 回落到 `7/9` 或更低。
- perturbation strict 下降。
- extra final cards 仍接近 `19` 或更高。
- 输出因新增契约变长而解析失败。

## 失效条件

- prompt 泄漏 `gold_answer`、`required_slots`、`acceptable_card_ids`、`expected_final`、`expected_final_decision`、`required_cards`、`oracle` 或评分字段。
- 输出目录复用旧结果。
- GPU 或远程服务失败。
- 远程脚本和本地脚本不同步。

## 本地预检

```text
dry_run_prompts_out: experiments/20260619-local-hsa-v0-focused-recall-preflight/dry_run_focused_recall.jsonl
rows: 9
prompt chars: 7396 到 7891，平均 7588.6
```

`py_compile` 通过。泄漏检查未命中金标或评分字段。

## 计划远程运行

默认使用 GPU 7。若 GPU 7 忙，暂停，不自动切到前面的卡。

```bash
cd /data/xuhaoming/yfy/research_workspace
PROMPT_CONTRACT=focused_recall GPU_ID=7 PORT=8080 RUN_ID=20260619-a8002-hsa-v0-focused-recall-full9-qwen25-14b LIMIT=0 GPU_MEMORY_UTILIZATION=0.75 MAX_MODEL_LEN=8192 MAX_TOKENS=3072 RUN_TIMEOUT=1800 bash scripts/run_hsa_v0_sseac_a8002.sh
```

