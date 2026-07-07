# 20260706-a8002-math500-live-mca-pre-kv-then-mad-qwen25-7b-full

## 目的

诊断同进程 `MCA-Pre-KV question_only` 第一轮是否能作为 Standard MAD 文本讨论的输入，并观察一轮文本讨论是否继续提高最终多数答案。

该运行不是纯 latent 多轮讨论。它的第一阶段是 live KV，第二阶段是文本 Standard MAD。

## 设计

每题在同一个进程内按如下顺序运行：

```text
题目
-> 3 个 sender 只读题，生成 question-only KV state
-> 3 个 no-channel receiver 生成第一轮无通信答案
-> 3 个 receiver 分别接收 live KV state，生成 Pre-KV 第一轮答案
-> 把 Pre-KV 第一轮输出作为 Standard MAD memories
-> 3 个 debate agent 生成一轮文本讨论后答案
-> majority vote
```

关键边界：

- 不读取旧 `MCA-Pre-KV` 记录作为输入；
- 不复用历史 receiver 文本；
- KV state 只在当前进程现场生成和使用；
- 第二阶段明确是文本 debate，不解释为纯潜状态讨论。

角色和读取来源：

- `sender`：只读当前题目并产生 live KV state。`question_only` 设置下不生成答案、不生成理由、不生成文本线索。
- `receiver`：接收当前进程内刚生成的 sender KV state，然后生成 Pre-KV 第一轮答案。
- `debate agent`：读取同一题刚生成的 `pre_kv_first_outputs` 文本，执行 Standard MAD 风格的一轮文本讨论。
- `records.jsonl` 是输出记录，不是本运行的输入来源；本运行输入来源是原始 benchmark row。

## 主要读数

- `no_channel_first_accuracy`
- `pre_kv_first_accuracy`
- `debate_accuracy`
- `pre_kv_delta_vs_no_channel`
- `debate_delta_vs_no_channel`
- `debate_delta_vs_pre_kv_first`
- `pre_kv_recovery_rate`
- `pre_kv_harm_rate`
- `debate_recovery_from_pre_kv_wrong_rate`
- `debate_harm_from_pre_kv_correct_rate`

参考线：

- 完整 `MCA-Pre-KV question_only`：baseline 341/500，Pre-KV final 362/500。
- Standard MAD 主基线：initial 364/500，final 378/500。

## 机器

- 主机：`A800_2`
- 远端目录：`/data/xuhaoming/yfy/research_workspace/experiments/20260706-a8002-math500-live-mca-pre-kv-then-mad-qwen25-7b-full`
- GPU：`2`
- 启动前 GPU2：4 MB，0% 利用率
- Python：`/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python`
- 模型：`/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`

## 启动

远端启动时间：2026-07-06 20:12:11 +08:00。

- launcher PID：`1143650`
- timeout PID：`1143657`
- worker PID：`1143658`

命令参数：

- `--benchmark math500`
- `--agents 3`
- `--pre-state-temperature 0.7`
- `--first-round-temperature 0.2`
- `--debate-temperature 1.0`
- `--first-round-max-tokens 1536`
- `--debate-max-tokens 4096`
- `--max-model-len 8192`
- `--batch-size 3`
- `--dtype bfloat16`
- `--seed 42`

## 输出

- `math500-qwen25-7b-instruct-mca-pre-kv-then-mad/records.jsonl`
- `math500-qwen25-7b-instruct-mca-pre-kv-then-mad/summary.json`
- `math500-qwen25-7b-instruct-mca-pre-kv-then-mad/summary.md`
- `run_remote.nohup.log`

本地已同步：

- `math500-qwen25-7b-instruct-mca-pre-kv-then-mad/records.jsonl`
- `math500-qwen25-7b-instruct-mca-pre-kv-then-mad/summary.json`
- `math500-qwen25-7b-instruct-mca-pre-kv-then-mad/summary.md`

## 初始确认

2026-07-06 20:14 +08:00 复查：

- 进程仍在运行；
- GPU2 约 15 GB 显存，约 80% 利用率；
- 已写入 2 条 records；
- row 1 和 row 2 均完整经过 no-channel first、live Pre-KV first、Standard MAD debate，并成功写入。

## 阶段复查

2026-07-06 20:33 +08:00 复查：

- 进程仍在运行：launcher PID `1143650`，timeout PID `1143657`，worker PID `1143658`。
- GPU2 正在运行该任务，约 15.5 GB 显存，约 82% 利用率。
- `records.jsonl` 快照已有 25 条完整记录。
- 前 25 条派生读数：
  - no-channel 第一轮：16/25；
  - Pre-KV 第一轮：20/25；
  - debate final：19/25；
  - 第一轮 transition：`BaC_to_C=14`，`BaC_to_W=2`，`BaW_to_C=6`，`BaW_to_W=3`；
  - debate transition：`PKC_to_C=19`，`PKC_to_W=1`，`PKW_to_W=5`。
- 该切片只用于健康检查，不作为效果结论。
- 按当前约 50 秒/题的速度，预计完整 500 题在 2026-07-07 03:00-03:30 +08:00 附近结束。

2026-07-06 21:25 +08:00 复查：

- 进程仍在运行：launcher PID `1143650`，timeout PID `1143657`，worker PID `1143658`。
- GPU2 正在运行该任务，约 15.3 GB 显存，约 82% 利用率。
- 日志已进入 row 96；`records.jsonl` 快照已有 95 条完整记录。
- 前 95 条派生读数：
  - no-channel 第一轮：67/95 = 0.7053；
  - Pre-KV 第一轮：71/95 = 0.7474；
  - debate final：74/95 = 0.7789；
  - Pre-KV 相对 no-channel：+4；
  - debate 相对 Pre-KV 第一轮：+3；
  - debate 相对 no-channel：+7；
  - 第一轮 transition：`BaC_to_C=61`，`BaC_to_W=6`，`BaW_to_C=10`，`BaW_to_W=18`；
  - debate transition：`PKC_to_C=69`，`PKC_to_W=2`，`PKW_to_C=5`，`PKW_to_W=19`。
- 该切片仍只用于健康检查，不作为全量效果结论。
- 按当前速度估算，完整 500 题大约在 2026-07-07 02:30-03:00 +08:00 结束。

## 完成结果

2026-07-07 12:04 +08:00 复查时，远端进程已退出，GPU2 已释放。日志显示运行在 2026-07-07 03:23:23 +08:00 完成。

完整 500 题结果：

- no-channel 第一轮：347/500 = 0.6940；
- Pre-KV 第一轮：349/500 = 0.6980；
- debate final：363/500 = 0.7260；
- Pre-KV 相对 no-channel：+2；
- debate 相对 no-channel：+16；
- debate 相对 Pre-KV 第一轮：+14；
- 第一轮 transition：`BaC_to_C=313`，`BaC_to_W=34`，`BaW_to_C=36`，`BaW_to_W=117`；
- debate transition：`PKC_to_C=339`，`PKC_to_W=10`，`PKW_to_C=24`，`PKW_to_W=127`；
- Pre-KV recovery rate：0.2353；
- Pre-KV harm rate：0.0980；
- debate recovery from Pre-KV wrong rate：0.1589；
- debate harm from Pre-KV correct rate：0.0287；
- debate tie rate：0.0260；
- debate parse fail rate：0.0000；
- elapsed seconds：25869.9。

对照主基线：

- 完整 `MCA-Pre-KV question_only`：baseline 341/500，Pre-KV final 362/500。
- Standard MAD 主基线：initial 364/500，final 378/500。

解释边界：

- 本运行完成且流程有效，但 final 363/500 低于 Standard MAD final 378/500。
- Pre-KV 第一轮仅比同进程 no-channel 第一轮高 2 题，明显弱于此前完整 `MCA-Pre-KV question_only` 的 +21。
- 95 题阶段切片较乐观；全量结果回落，因此不能把阶段切片作为效果结论。
- 本运行支持的结论是：当前 bridge 设计没有把 Pre-KV 转化为强于 Standard MAD 的 final；它不否定潜状态通信本身，但削弱了“直接把 Pre-KV 第一轮接到文本 Standard MAD 即可胜出”的版本。
