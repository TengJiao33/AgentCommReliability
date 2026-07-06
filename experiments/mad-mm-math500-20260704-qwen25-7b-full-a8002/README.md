# MAD-MM MATH500 20260704 Qwen2.5-7B full 实验记录

## 目的

在 AIME24/25 运行未显示 Qwen2.5-7B-Instruct 的正向准确率增益后，测试本地 MAD-MM/MAD-M2 复现在 MATH-500 上是否有可用信号。

## 设计

- 任务：`math500/test`，完整 500 题。
- 单位：一条 MATH-500 problem。
- 模型：`/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`。
- 方法：本地 `scripts/run_mad_mm.py`，3 个 agent，2 总轮次，majority vote。
- 主要对比：`naive`、`subjective`、`objective` 三种 memory masking。
- 评测器：`scripts/run_basic_mad.py` 中的共享 answer normalizer；依次尝试 boxed-answer extraction、可用时使用 SymPy/latex2sympy2 等价判断、数值 fallback，以及短文本归一化。

## 机器

- 主机：`A800_2`。
- 工作目录：`/data/xuhaoming/yfy/research_workspace`。
- Python 环境：`/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python`。
- GPU：`1`。
- 运行时间：2026-07-04 约 19:14-22:36 CST。

## 启动

```bash
WORK=/data/xuhaoming/yfy/research_workspace
RUN_ID=mad-mm-math500-20260704-qwen25-7b-full-a8002
GPU_ID=1 nohup bash "$WORK/experiments/$RUN_ID/run_remote.sh" \
  > "$WORK/experiments/$RUN_ID/launcher.out.log" \
  2> "$WORK/experiments/$RUN_ID/launcher.err.log" &
```

## 预期输出

- 远端/本地 run root：`experiments/mad-mm-math500-20260704-qwen25-7b-full-a8002/`
- 各策略输出：
  - `math500-qwen25-7b-instruct-naive/records.jsonl`
  - `math500-qwen25-7b-instruct-naive/summary.json`
  - `math500-qwen25-7b-instruct-subjective/records.jsonl`
  - `math500-qwen25-7b-instruct-subjective/summary.json`
  - `math500-qwen25-7b-instruct-objective/records.jsonl`
  - `math500-qwen25-7b-instruct-objective/summary.json`

## 状态

`COMPLETED`。

## 校验

- 每个策略都产生 500 行 `records.jsonl`。
- 每个 `summary.json` 都报告 500 rows。
- 三个策略的 final parse failures 均为 0。
- 2026-07-05 评测器审计：`scripts/run_basic_mad.py` 已修复为幂等处理 canonical `expr:/str:` answer，并处理常见 MATH-500 symbolic/text 格式；随后用 `scripts/recompute_mad_mm_summary.py` 从原始 agent answers 重算 records 与 summaries。
- 完成后的远端清理检查：没有残留 `run_mad_mm.py` 进程；GPU 1 回到 4 MiB 显存占用与 0% 利用率。

## 结果

| Strategy | Rows | Initial majority | Final correct | Final acc. | Delta vs initial | Tie rate | Memory retention | Elapsed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `naive` | 500 | 362 | 375 | 0.750 | +0.026 | 0.038 | 1.000 | 4018.8s |
| `subjective` | 500 | 362 | 369 | 0.738 | +0.014 | 0.028 | 0.987 | 4100.0s |
| `objective` | 500 | 362 | 360 | 0.720 | -0.004 | 0.002 | 0.333 | 3940.1s |

Subjective label counts：

| Label | Count |
| --- | ---: |
| `yes` | 1224 |
| `not sure` | 257 |
| `no` | 19 |

## 解释

MATH-500 比 AIME 给出了更清楚的诊断，因为 benchmark 更大，且修正后的评测器能处理常见 boxed LaTeX、symbolic、tuple、text、unit、mixed-number 和 complex answers。该设置下，`naive` MAD-MM/MAD-M2 风格 debate 表现最好。

`subjective` masking 保留 1481/1500 条 memories，因此大体接近 `naive`，最终略低。`objective` masking 几乎消除了 ties，并且每题严格保留一条 memory，但没有超过 initial majority baseline。

这是本地 Qwen2.5-7B 设置下的诊断证据，不是关于 MAD-MM 的泛化结论。当前最有用的结论是：宽松 subjective masking 在 MATH-500 上没有提供多少过滤压力，而 objective masking 是真实干预，但在这里过于有损。
