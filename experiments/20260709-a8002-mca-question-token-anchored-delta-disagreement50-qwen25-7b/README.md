# MCA Question-Token Anchored Delta Disagreement50

日期：2026-07-09

## 目的

验证 `mca-question-token-anchored-delta-v0` 是否能在 50 道 disagreement 题上稳定运行，并初步观察题目词元锚定的潜状态注入是否和裸状态注入、随机同范数题目词元注入拉开差距。

## 开跑合同

- 假设：把发送方普通解题轨迹中的 hidden delta 锚定到原题词元后注入，可能比把同一批 delta 聚合后注入 prompt 末尾更接近有效通信。
- 单位：`math500/mca_disagreement_v1` 中的题目；每题 3 个智能体。
- 主比较：`question_token_delta` 对比 `raw_delta`。
- 次要对照：`question_token_random_same_norm`，用于检查收益是否只是题目位置扰动。
- 样本数：50。
- 预期产物：`records.jsonl`、`summary.json`、`summary.md`、本 README、启动脚本和等待日志。

## 范围

- 任务：MATH-500 disagreement split。
- 模型：Qwen2.5-7B-Instruct。
- 方法：题目词元锚定 hidden delta。
- 数据集：`data/benchmarks/math500/mca_disagreement_v1/canonical.jsonl`。
- 条件：
  - `raw_delta`
  - `question_token_delta`
  - `question_token_random_same_norm`

## 机器

- 主机：A800_2 / `10-116-90-20`。
- 工作目录：`/data/xuhaoming/yfy/research_workspace`。
- GPU：等待器从 `0 1 2 3 4 5 6 7` 中选择真正空闲的单卡。
- 空闲判定：`nvidia-smi pmon` 无计算进程，空闲显存不少于 `70000` MiB，利用率不高于 `5%`。

## 代码

- 主脚本：`scripts/run_mca_question_token_anchored_delta.py`。
- 测试：`tests/test_mca_question_token_anchored_delta.py`。
- 当前本地脚本已通过：
  - `python -m py_compile scripts/run_mca_question_token_anchored_delta.py`
  - `python -m unittest tests.test_mca_question_token_anchored_delta`

## 运行参数

```text
split = mca_disagreement_v1
limit = 50
agents = 3
layers = 22
conditions = raw_delta,question_token_delta,question_token_random_same_norm
span_tokens = 16
max_payloads = 8
max_question_anchors = 3
attribution_method = attention
steering_scale = 0.03
message_max_norm = 1.0
temperature = 0.2
top_p = 1.0
max_new_tokens = 1536
max_model_len = 8192
```

## 启动命令

```bash
nohup bash /data/xuhaoming/yfy/research_workspace/experiments/20260709-a8002-mca-question-token-anchored-delta-disagreement50-qwen25-7b/launch_when_gpu_empty.sh \
  > /data/xuhaoming/yfy/research_workspace/experiments/20260709-a8002-mca-question-token-anchored-delta-disagreement50-qwen25-7b/wait_launcher.log 2>&1 < /dev/null &
```

## 输出

- 远端运行目录：`/data/xuhaoming/yfy/research_workspace/experiments/20260709-a8002-mca-question-token-anchored-delta-disagreement50-qwen25-7b/`
- 结果目录：等待脚本启动后生成。
- 等待日志：`wait_launcher.log`。
- 运行日志：`run_question_token_anchored.nohup.log`。
- 选中 GPU：等待脚本启动后写入 `selected_gpu.txt`。

## 当前状态

- 状态：QUEUED。
- 2026-07-09 18:57 +08:00 检查时，8 张 GPU 均有 `pmon` 计算进程；GPU 3 空闲显存最高但仍有活跃进程，因此未直接抢卡。
- 2026-07-09 18:59 +08:00 已启动等待器，远端 PID 为 `2563759`；首轮检查跳过全部 GPU，原因均为 `pmon` 仍有计算进程。
- 结果：等待运行生成。
