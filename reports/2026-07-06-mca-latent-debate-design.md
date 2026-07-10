# MCA 潜状态多轮讨论边界记录

日期：2026-07-06

## 做法

1. 记录先固定 Standard MAD 参照流程。每道题由 3 个智能体生成第一轮答案和理由，再把第一轮可读文本广播给其他智能体，第二轮智能体读取这些文本后生成修正答案，最后对 3 个第二轮答案做多数投票。

2. `MCA-Pre-KV question_only` 只运行一轮前置状态通信。发送方只读题并保存 `past_key_values`，不生成答案、不生成理由，也不生成可读线索。

3. 接收方接入发送方的 question-only KV 后，从 receiver prompt 生成第一轮答案。该流程到第一轮答案为止，没有把接收方答案再交给其他智能体讨论。

4. `Pre-KV + Standard MAD` 在上一步之后继续运行文本讨论。3 个 receiver 的第一轮可读答案和理由被整理成 Standard MAD memory，交给第二轮 debate agent。

5. 第二轮 debate agent 不再接收潜状态，而是读取第一轮可读文本，按 Standard MAD 方式修正答案。最终答案由第二轮 3 个智能体多数投票得到。

6. 纯潜状态多轮讨论的边界被单独记录：每一轮都继续传递 KV 或 hidden state，中间轮次不广播可读答案或理由，最终答案只在最后阶段生成。

7. 因此，`Pre-KV + Standard MAD` 被记录为桥接机制：第一阶段是前置潜状态通信，第二阶段是普通文本讨论。它的结果不能和纯潜状态多轮讨论混称。

## 工程细节

- Standard MAD 参照运行路径为 `experiments/standard-mad-math500-20260705-qwen25-7b-full-4096-a8002/`。
- Standard MAD 设置为 `math500/test`、`Qwen2.5-7B-Instruct`、3 个智能体、2 轮、输出预算 4096。
- `question_only` sender 的 `generated_tokens=0`，只保留读题后的 `past_key_values`。
- receiver 接收 sender KV 后从 receiver prompt 开始生成第一轮答案。
- debate agent 读取第一轮可读文本答案后，按 Standard MAD 文本讨论 prompt 生成第二轮答案。
- `Pre-KV + Standard MAD` 的两阶段流程为：3 个 sender 只读题得到 question-only KV；3 个 receiver 接入 KV 生成第一轮答案；第一轮文本答案广播给其他 agent；第二轮按 Standard MAD 修正；最后做多数投票。
- 多轮潜状态讨论的边界是每轮继续传递 KV 或 hidden state，并且最终答案只在最后阶段输出。若每轮都广播可读答案或理由，该机制会退回文本 MAD。
- 记录字段需要能复核每轮 agent id、state 来源、是否生成可读文本、是否生成最终答案、KV 的 prompt token 数、generated token 数、past token 数、receiver 使用的 sender state、每轮答案、最终答案和正误转移。

## 结果

| 运行 | 读数 | 数值 |
| --- | --- | ---: |
| Standard MAD | 初始多数 | 364/500 |
| Standard MAD | final | 378/500 |
| `MCA-Pre-KV question_only` 完整运行 | baseline | 341/500 |
| `MCA-Pre-KV question_only` 完整运行 | final | 362/500 |
| `MCA-Pre-KV question_only` 完整运行 | 净变化 | +21 |
| `Pre-KV + Standard MAD` bridge run | no-channel 第一轮 | 347/500 |
| `Pre-KV + Standard MAD` bridge run | Pre-KV 第一轮 | 349/500 |
| `Pre-KV + Standard MAD` bridge run | debate final | 363/500 |

`MCA-Pre-KV question_only` 完整运行的转移为 `BaC_to_C=317`、`BaC_to_W=24`、`BaW_to_C=45`、`BaW_to_W=114`。bridge run 中，Pre-KV 相对 no-channel 第一轮为 `+2`，debate final 相对 no-channel 第一轮为 `+16`，相对 Pre-KV 第一轮为 `+14`。

## 备注

`Pre-KV + Standard MAD` 不能称为纯潜状态多轮讨论，因为第二阶段的通信对象是 receiver 的可读答案和理由。它适合作为桥接对照，用来观察前置 KV 是否改变进入文本讨论的第一轮材料。
