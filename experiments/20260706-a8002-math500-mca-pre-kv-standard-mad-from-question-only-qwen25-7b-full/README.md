# 20260706-a8002-math500-mca-pre-kv-standard-mad-from-question-only-qwen25-7b-full

## 目的

检查 `MCA-Pre-KV question_only` 的一轮 receiver 输出接入 Standard MAD 文本讨论后，是否能提高最终多数答案。

该运行是桥接诊断，不是对潜状态通信方向的总判定。它只检验当前 `question_only` KV、当前 receiver 输出、当前 naive Standard MAD 二轮文本协议这一组合。

## 主要对照

- 输入来源：`20260706-a8002-math500-mca-pre-kv-question-only-standard-qwen25-7b-full`
- 输入记录：`math500-qwen25-7b-instruct-mca-pre-kv-cache-question_only-state/records.jsonl`
- 输入 run 最终结果：baseline 341/500，Pre-KV one-round 362/500。
- 参考基线：Standard MAD final 378/500，来自 `standard-mad-math500-20260705-qwen25-7b-full-4096-a8002`。

## 设计

每题读取已有 `MCA-Pre-KV question_only` 记录中的 `receiver_outputs`，把这 3 个 receiver 输出作为 Standard MAD 的当前 round memories，再运行一轮 `run_mad_mm.py` 中的 naive debate prompt。

流程：

```text
Pre-KV receiver outputs
-> Standard MAD debate_prompt
-> 3 个 debate agent 输出
-> majority vote
```

## 机器

- 主机：`A800_2`
- 远端目录：`/data/xuhaoming/yfy/research_workspace/experiments/20260706-a8002-math500-mca-pre-kv-standard-mad-from-question-only-qwen25-7b-full`
- GPU：`2`
- 启动前 GPU2：约 4 MB，0% 利用率
- Python：`/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python`
- 模型：`/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`

## 启动

远端启动时间：2026-07-06 19:38:37 +08:00。

- launcher PID：`1020532`
- timeout PID：`1020544`
- worker PID：`1020545`

输出：

- `math500-qwen25-7b-instruct-mca-pre-kv-standard-mad/records.jsonl`
- `math500-qwen25-7b-instruct-mca-pre-kv-standard-mad/summary.json`
- `math500-qwen25-7b-instruct-mca-pre-kv-standard-mad/summary.md`
- `run_remote.nohup.log`

## 解释边界

如果该运行超过 362/500，说明文本讨论能继续利用 Pre-KV receiver outputs。若超过 378/500，才说明该桥接版本超过当前 Standard MAD final 参考线。

如果该运行不超过 378/500，不能否定潜状态通信方向；它只说明当前 naive bridge 没有超过 Standard MAD final。
