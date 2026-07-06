# MAD-MM AIME24/25 20260704 Qwen2.5-7B full 实验记录

## 尝试内容

为 MAD-M2 准备 AIME24/AIME25 的完整复现切片，使用 Qwen2.5-7B-Instruct，对比 upstream-style naive MAD、subjective memory masking 和 objective memory masking，三者使用同一 runner。

## 范围

- 方法：MAD-M2 memory masking，包含 `naive`、`subjective`、`objective`。
- 模型：Qwen2.5-7B-Instruct。
- 数据集：AIME24 train split 与 AIME25 test split。
- 随机种子：42。
- 样本：两个 split 全量，各 30 题，共 60 题。
- 对比对象：同一运行内 naive MAD，并把早期本地 AIME basic MAD 与 CoT-SC 结果作为背景参考。

## 实验门禁

- 目的：检验 upstream-style memory masking 在更难的 AIME 设置上是否优于同一运行内的 naive MAD。
- 单位：benchmark row/question。
- 主要对比：`subjective` 与 `objective` 的 final accuracy 对比 `naive` final accuracy；模型、prompt、temperature、seed、agent count 和 round count 相同。
- 次要对比：initial-round majority accuracy、final tie rate、memory retention rate、subjective label distribution。
- 支持信号：任一 masking 策略在合并 60 道 AIME 题上提高 final accuracy，且没有明显 parser failure。
- 失败信号：masking 持平或落后 naive MAD，或收益可由 parser/gold 问题解释。
- 失效条件：缺行、gold label 错误、XML/answer parsing 损坏、模型路径不一致、输出截断、GPU 中断、误用非全量 `--limit`。
- 预期产物：本 README、`run_remote.sh`，以及各方法目录下的 `summary.json`、`summary.md`、`records.jsonl`。

## 资源

- 机器：A800_2。
- 远端工作目录：`/data/xuhaoming/yfy/research_workspace`。
- GPU：计划使用空闲的 GPU 7。
- 超时：12h launcher timeout。
- 预计耗时：全部 6 个 method/dataset job 约 45-60 分钟。
- 发起者：Codex。

## 代码

- 上游仓库：https://github.com/HongduanTian/MAD-MM
- 已检查的上游 commit：`f02069a`。
- 本地脚本：`scripts/run_mad_mm.py`。
- 本地变更：新增本地 runner 与 source note。

## 环境

- 环境路径：`/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063`。
- Python：3.10.20。
- vLLM：0.6.3。
- PyTorch：2.4.0。
- Transformers：4.46.2。

## 数据

- 数据路径：
  - `/data/xuhaoming/yfy/research_workspace/data/benchmarks/aime24/train/canonical.jsonl`
  - `/data/xuhaoming/yfy/research_workspace/data/benchmarks/aime25/test/canonical.jsonl`
- Split：AIME24 `train`，AIME25 `test`。
- 采样：完整 split，不使用 `--limit`。

## 命令

```bash
bash experiments/mad-mm-aime24-25-20260704-qwen25-7b-full-a8002/run_remote.sh
```

## 远端产物

- 主日志：`experiments/mad-mm-aime24-25-20260704-qwen25-7b-full-a8002/launcher.out.log`
- 错误日志：`experiments/mad-mm-aime24-25-20260704-qwen25-7b-full-a8002/launcher.err.log`
- 结果：`experiments/mad-mm-aime24-25-20260704-qwen25-7b-full-a8002/*/summary.json`
- 轨迹：`experiments/mad-mm-aime24-25-20260704-qwen25-7b-full-a8002/*/records.jsonl`

## 实际结果

- 状态：`COMPLETED`。
- 准确率：同一运行内，masking 没有在合并 60 道 AIME 题上提高 final correct count。
- Memory retention：subjective 保留 176/180 条 memory；objective 保留 60/180 条 memory。
- 评测耗时：模型初始化后，每个 job 约 421-505 秒。
- 墙钟时间：成功的 full launcher 约 47 分钟，从 `2026-07-04 16:55:21 CST` 到 `2026-07-04 17:42:05 CST`。

| Dataset | Split | Method | Correct | Accuracy | Initial Majority | Tie Rate | Memory Retention | Subjective Labels |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| AIME24 | train | naive | 4/30 | 0.1333 | 0.1000 | 0.3667 | 1.0000 | - |
| AIME24 | train | subjective | 4/30 | 0.1333 | 0.1000 | 0.3000 | 0.9667 | yes 80, not sure 7, no 3 |
| AIME24 | train | objective | 3/30 | 0.1000 | 0.1000 | 0.0667 | 0.3333 | - |
| AIME25 | test | naive | 1/30 | 0.0333 | 0.0333 | 0.2667 | 1.0000 | - |
| AIME25 | test | subjective | 1/30 | 0.0333 | 0.0333 | 0.2333 | 0.9889 | yes 83, not sure 6, no 1 |
| AIME25 | test | objective | 1/30 | 0.0333 | 0.0333 | 0.0000 | 0.3333 | - |

合并 AIME24 train 与 AIME25 test：

| Method | Correct | Accuracy | Tie Rate | Memory Retention |
| --- | ---: | ---: | ---: | ---: |
| naive | 5/60 | 0.0833 | 0.3167 | 1.0000 |
| subjective | 5/60 | 0.0833 | 0.2667 | 0.9778 |
| objective | 4/60 | 0.0667 | 0.0333 | 0.3333 |

## 状态时间线

- `2026-07-04`：准备完成。
- `2026-07-04 16:45 CST`：第一次 launcher 因查找 `aime24/test/canonical.jsonl` 失败，未产出结果。
- `2026-07-04 16:53 CST`：第二次 launcher 因本地 runner 在存储 `context["parsed"]` 前引用该字段失败，未产出可用于结论的结果。
- `2026-07-04 16:55 CST`：成功的 full launcher 在 A800_2 GPU 7 启动。
- `2026-07-04 17:42 CST`：成功的 full launcher 完成；GPU 7 回到 4 MiB 显存占用。

## 悬而未决

- 若要增加干预压力，可在 MATH500 或更大模型上运行同一本地 runner，或把 subjective pruning 改成严格屏蔽 `NOT SURE`。
