# HSA-v0 候选证据召回契约预检

日期：2026-06-19

## 目的

HSA full9 的主要失败来自候选证据召回不足：两个 base 行模型最终答案正确，但没有提出全部必需证据卡，硬准入路径保守退回 `insufficient_evidence`。本次预检准备一个最小提示改动：`recall_sweep`。

`recall_sweep` 要求模型先扫描每个候选答案的支持、阻断和背景约束证据，再输出单卡候选单元。它不改变 compiler、scorer、packet 或 gold。

## 实验问题

这次复跑想回答：显式证据扫描加单卡候选单元，能否提高 HSA base 行的候选证据召回，同时保持 perturbation 行的 hard-admission 防错能力。

## 主对照

`recall_sweep compiler` 对上一轮 `baseline compiler`：

| 条件 | Strict | Base strict | Perturb strict | Slot recall | Extra final cards | Forced commitment |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline compiler | 7/9 | 0.3333 | 1.0000 | 0.7130 | 8 | 0.7778 |

## 成功信号

- strict 超过 `7/9`，或 base strict 从 `1/3` 提升。
- slot recall 高于 `0.7130`。
- perturbation strict 保持接近 `1.0000`。
- extra final cards 不明显上升，最好低于或接近 `8`。

## 失败信号

- base strict 不升，slot recall 不升。
- perturbation strict 明显下降。
- 输出因新增 `answer_evidence_sweep` 变长而解析失败。
- 单卡候选造成大量过度准入，extra final cards 接近 all-scoped 的 `24`。

## 失效条件

- prompt 泄漏 `gold_answer`、`required_slots`、`acceptable_card_ids`、`expected_final`、`expected_final_decision`、`required_cards`、`oracle` 或评分字段。
- 输出目录复用旧结果。
- GPU 或远程服务失败。
- 远程脚本和本地脚本不同步。

## 本地预检

```text
baseline dry-run: experiments/20260619-local-hsa-v0-recall-sweep-preflight/dry_run_baseline.jsonl
recall_sweep dry-run: experiments/20260619-local-hsa-v0-recall-sweep-preflight/dry_run_recall_sweep.jsonl
rows: 9
baseline prompt chars: 5499 到 5994，平均 5691.6
recall_sweep prompt chars: 6648 到 7143，平均 6840.6
```

`py_compile` 通过。泄漏检查未命中金标或评分字段。

## 计划远程运行

默认使用 GPU 7。若 GPU 7 忙，暂停，不自动切到前面的卡。

```bash
cd /data/xuhaoming/yfy/research_workspace
PROMPT_CONTRACT=recall_sweep GPU_ID=7 PORT=8079 RUN_ID=20260619-a8002-hsa-v0-recall-sweep-full9-qwen25-14b LIMIT=0 GPU_MEMORY_UTILIZATION=0.75 MAX_MODEL_LEN=8192 MAX_TOKENS=3072 RUN_TIMEOUT=1800 bash scripts/run_hsa_v0_sseac_a8002.sh
```

