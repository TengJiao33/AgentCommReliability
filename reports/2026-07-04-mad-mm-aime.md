# MAD-M2 AIME 复现诊断

## 问题


## 配置

- 任务：AIME24 train + AIME25 test。
- 对比方法：MAD-M2 `naive`、`subjective`、`objective`。
- 模型：Qwen2.5-7B-Instruct。
- 样本量：共 60 题，30 + 30。

## 证据来源

| 来源 | 类型 | 路径/链接 |
| --- | --- | --- |
| Multi-Agent Debate with Memory Masking | 论文 | https://arxiv.org/abs/2603.20215 |
| MAD-MM upstream code | 仓库 | https://github.com/HongduanTian/MAD-MM |
| 本地来源说明 | 方法说明 | `baselines/mad-mm/source.md` |
| 运行记录 | 实验 | `experiments/mad-mm-aime24-25-20260704-qwen25-7b-full-a8002/README.md` |

## 结果

| 方法 | 模型 | 任务 | 样本数 | 正确数 | 准确率 | 状态 |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `naive` | Qwen2.5-7B-Instruct | AIME24 train + AIME25 test | 60 | 5 | 0.0833 | 已完成 |
| `subjective` | Qwen2.5-7B-Instruct | AIME24 train + AIME25 test | 60 | 5 | 0.0833 | 已完成 |
| `objective` | Qwen2.5-7B-Instruct | AIME24 train + AIME25 test | 60 | 4 | 0.0667 | 已完成 |
