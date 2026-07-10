# Natural Search Delta Disagreement50

日期：2026-07-08

## 目的和状态

目的：检查自然解题过程中的同题中间状态变化量，是否比无关题变化量、随机同范数扰动、同题绝对状态更能提供搜索信号。

状态：完成。结果为诊断性，不足以支撑“自然搜索状态通信有效”的论断，也不触发全量 MATH500 扩大运行。

## 运行位置

```text
machine = A800_2
remote_root = /data/xuhaoming/yfy/research_workspace
remote_run = /data/xuhaoming/yfy/research_workspace/experiments/20260708-a8002-mca-natural-search-delta-disagreement50-qwen25-7b/
local_record = experiments/20260708-a8002-mca-natural-search-delta-disagreement50-qwen25-7b/
```

## 模型和运行口径

```text
model = /mnt/quarkfs/share_model/Qwen2.5-7B-Instruct
benchmark = math500
split = mca_disagreement_v1
rows = 50
agents = 3
gpu = 7
layer = 22
checkpoints = 16,32,64,96
steering_scale = 0.03
message_max_norm = 1.0
temperature = 0.2
max_new_tokens = 1536
state_source = ordinary CoT decode trace
sender_prompt_intervention = false
uses_peer_past_key_values = false
```

## 输出文件

```text
/data/xuhaoming/yfy/research_workspace/experiments/20260708-a8002-mca-natural-search-delta-disagreement50-qwen25-7b/math500-qwen25-7b-instruct-mca-natural-search-delta/summary.json
/data/xuhaoming/yfy/research_workspace/experiments/20260708-a8002-mca-natural-search-delta-disagreement50-qwen25-7b/math500-qwen25-7b-instruct-mca-natural-search-delta/summary.md
/data/xuhaoming/yfy/research_workspace/experiments/20260708-a8002-mca-natural-search-delta-disagreement50-qwen25-7b/math500-qwen25-7b-instruct-mca-natural-search-delta/records.jsonl
/data/xuhaoming/yfy/research_workspace/logs/20260708-natural-search-delta-gpu7.nohup.log
```

远端核查时间：2026-07-08 16:31 +08:00。

## 结果摘要

| 条件 | 正确数 | 相对基线 | 错到对 | 对到错 |
|---|---:|---:|---:|---:|
| 无通道基线 | 24/50 | - | - | - |
| 同题变化量 | 26/50 | +2 | 3 | 1 |
| 无关题变化量 | 23/50 | -1 | 5 | 6 |
| 随机同范数扰动 | 26/50 | +2 | 5 | 3 |
| 同题绝对状态 | 23/50 | -1 | 2 | 3 |

## 复核判断

同题变化量的伤害最少，但救回也少；随机同范数扰动达到同样正确数，并有更多救回。这说明当前结果不能证明同题自然搜索状态优于普通扰动。

同题变化量相对无关题变化量更稳，说明同题状态可能有一定区分度；但无关题控制使用相邻行作为来源，不是强随机无关题控制，因此这条证据只能作为弱诊断。

后续如果继续，应先做样例审计和更严格控制组，而不是扩大行数。
