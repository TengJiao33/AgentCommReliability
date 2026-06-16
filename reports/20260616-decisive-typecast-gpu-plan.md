# 决定性 GPU 实验准备：Content-Held-Constant Cast Test

日期：2026-06-16

状态：只做本地准备；没有 SSH；没有启动 GPU。

## 为什么要改

之前的实验设计太像“把所有 channel 都铺开看看”。这会变大，但不够一针见血。

下一枪应该只问一个决定论文命运的问题：

```text
同一份 Agent A artifact，内容完全相同，只改变通信边界如何 cast 它，
Agent B 是否会系统性改变继承行为？
```

如果答案是“会”，我们的核心故事就是 receiver-side invalid epistemic cast。

如果答案是“不会”，这个方向就要降级成普通 peer influence / context authority。

## 主实验

实验名：

```text
MATH200 Content-Held-Constant Cast Test
```

源数据：

```text
experiments/20260615-1151-a8002-typed-public-state-math200-anon/
madmm-qwen25-7b-math200-naive-20260615_1142.comm_trace.jsonl
```

这个源池有 `200` 个 MATH case：

| 分层 | 数量 |
| --- | ---: |
| 全部 case | `200` |
| 至少一个正确 round-0 peer | `149` |
| 至少一个错误 round-0 peer | `110` |
| 3 正 0 错 | `90` |
| 2 正 1 错 | `36` |
| 1 正 2 错 | `23` |
| 0 正 3 错 | `51` |
| 原 trace stable_right | `123` |
| 原 trace stable_wrong | `56` |
| 原 trace wrong_to_right | `12` |
| 原 trace right_to_wrong | `9` |

本地已生成：

```text
experiments/20260616-local-typecast-arena-math200-decisive-source/
```

里面有：

```text
source_rows.jsonl                         # 200 case source rows
typecast_math200_sender_stage_packet.jsonl # 200 row sender-stage packet
summary.json
README.md
```

## 两阶段设计

### Stage 1：live sender 生成 200 个真实 artifact

用较弱的 sender，例如 Qwen2.5-7B，让 Agent A 独立解题并输出结构化 artifact。

这一步不是为了测 receiver，而是为了得到自然分布的：

- correct sender artifacts；
- wrong sender artifacts；
- partial derivations；
- candidate answers；
- confidence / commitment status；
- 可能的错误算子表面。

建议只跑一次：

```bash
PACKET=/data/xuhaoming/yfy/research_workspace/experiments/20260616-local-typecast-arena-math200-decisive-source/typecast_math200_sender_stage_packet.jsonl \
RUN_ID=<stamp>-a8002-typecast-math200-sender200-qwen25-7b \
MODEL_PATH=/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct \
SERVED_MODEL=qwen2.5-7b-typecast-sender200 \
GPU_ID=<free-gpu> \
PORT=<free-port> \
MAX_TOKENS=768 \
RUN_TIMEOUT=3600 \
scripts/run_typecast_arena_packet_a8002.sh
```

### Stage 2：同一 artifact，只改 cast 状态

sender 输出回来后，用 materializer 生成 receiver packet。

这一步只保留 6 个关键 channel，不铺 16 个：

| Channel | 目的 |
| --- | --- |
| `sender_private_scratch_visible_inert` | 内容可见但声明未投递、未接纳；测试“只是看到文本” |
| `peer_message_direct` | 普通同伴消息；测试 message-only 影响 |
| `shared_workspace_admitted` | 共享状态接纳；测试 state cast |
| `verifier_admitted_result` | verifier 批准样式；测试 approval cast |
| `admission_rejected_quarantine` | 内容被隔离；负控制 |
| `typed_partial_derivation_requires_rederive` | 不删内容但要求重新推导；协议 mitigation |

生成命令：

```bash
python scripts/materialize_typecast_math_live_receiver_packet.py \
  --source-rows experiments/20260616-local-typecast-arena-math200-decisive-source/source_rows.jsonl \
  --sender-packet experiments/20260616-local-typecast-arena-math200-decisive-source/typecast_math200_sender_stage_packet.jsonl \
  --sender-outputs <sender-run>/outputs.jsonl \
  --channels sender_private_scratch_visible_inert peer_message_direct shared_workspace_admitted verifier_admitted_result admission_rejected_quarantine typed_partial_derivation_requires_rederive \
  --max-cases 0 \
  --out-dir experiments/<local-typecast-math200-receiver-packet>
```

预计 receiver rows：

```text
200 baseline rows
200 self-revision rows
200 unrelated-control rows
200 × 6 cast rows
= 1800 rows
```

这够大，但仍然尖锐，因为主变量只有一个：

```text
communication-boundary cast
```

内容不变。

## 主对比

### 对比一：state cast 是否真的有额外伤害

```text
shared_workspace_admitted
vs
sender_private_scratch_visible_inert
```

这是一针见血的主对比。

两边都能看到同一段 artifact。区别只是：

```text
未接纳草稿
vs
已接纳共享状态
```

如果 shared workspace 明显更容易让 baseline-right receiver 变错，这就是
invalid cast 的核心证据。

### 对比二：approval cast 是否比普通消息更危险

```text
verifier_admitted_result
vs
peer_message_direct
```

如果 verifier-approved 样式显著更强，说明问题不只是 peer text，而是
“程序性批准”这个 cast 赋权。

### 对比三：typed rederive 能否保留内容但降低非法继承

```text
typed_partial_derivation_requires_rederive
vs
shared_workspace_admitted
```

这决定我们是不是有 protocol 方向。

如果 typed rederive 只是删信息或让模型本地重解，那不够。

如果它在 wrong sender artifact 上减少 harm，同时在 correct sender artifact 上
还能保留一部分 useful evidence，那就像论文方法雏形。

### 对比四：quarantine 是否干净

```text
admission_rejected_quarantine
```

这不是方法主角，而是 sanity check。

如果 quarantine 还大量使用 sender 内容，说明提示或评估器有问题。

## 主要指标

### Wrong sender artifact 子集

看：

- harmful cast rate；
- direct wrong-answer uptake；
- non-copy operator uptake；
- baseline-right -> variant-wrong；
- artifact text overlap；
- boundary-obedience violation。

关键句：

```text
answer-copy 指标漏掉了多少 harmful communication failure？
```

### Correct sender artifact 子集

看：

- useful evidence retention；
- baseline-wrong -> variant-right；
- correct artifact uptake；
- typed rederive 是否保留 utility；
- admitted/verifier 是否只是更强 copying。

关键句：

```text
typed/admission protocol 不是简单删信息，而是在 wrong artifact 上降 harm，
同时在 correct artifact 上保留 useful transfer。
```

### 全部 artifact

看：

- cast 状态是否解释 receiver 行为；
- 同一 content 在不同 cast 下的 paired delta；
- case-level leave-one-out；
- sender correctness 分层；
- 原 MAD-MM peer mix 分层。

## 晋升条件

这轮实验如果出现下面形状，就值得继续冲 A 会故事：

```text
1. shared_workspace_admitted 的 harmful cast rate 明显高于 inert visible scratch；
2. verifier_admitted_result 高于 direct peer message；
3. typed_partial_derivation_requires_rederive 明显降低 invalid-cast core；
4. 很多 harm 不是 direct answer copy，而是 non-copy operator uptake；
5. correct sender artifact 上 typed/admission 仍有 useful evidence transfer；
6. quarantine 基本干净。
```

最理想的摘要数字长这样：

```text
On 200 MATH cases and 1800 receiver trials, holding sender content fixed,
admitted state casts caused X% harmful revisions versus Y% for inert-visible
scratch. Z% of harmful revisions were missed by answer-copy metrics and
manifested as non-copy operator uptake. A typed rederive boundary reduced
invalid casts by B% while retaining C% of useful evidence transfer.
```

## 退休条件

如果出现下面形状，就应该收缩或放弃这个主故事：

```text
1. admitted / verifier / peer / inert 条件没有可解释差异；
2. harm 几乎全是 direct answer copy；
3. typed rederive 没有减少 harm，或者只靠删信息；
4. correct sender artifact 几乎没有 useful transfer；
5. quarantine 或 unrelated control 也大量出错；
6. 结果主要由少数 case 支配，leave-one-case-out 后消失。
```

## 分片策略

receiver packet 预计约 `1800` rows，建议分成 4 个 shard，每个约 `450` rows。

本地已准备通用分片脚本：

```bash
python scripts/split_jsonl_shards.py \
  --packet experiments/<local-typecast-math200-receiver-packet>/typecast_math_receiver_packet.jsonl \
  --out-dir experiments/<local-typecast-math200-receiver-packet>/shards \
  --rows-per-shard 450 \
  --prefix typecast_math200_receiver
```

每个 shard 后续可以作为独立短 GPU 任务：

```bash
PACKET=/data/xuhaoming/yfy/research_workspace/experiments/<receiver-packet>/shards/typecast_math200_receiver.shard001.jsonl \
RUN_ID=<stamp>-a8002-typecast-math200-receiver-shard001-qwen25-14b \
MODEL_PATH=/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct \
SERVED_MODEL=qwen2.5-14b-typecast-receiver \
GPU_ID=<free-gpu> \
PORT=<free-port> \
MAX_TOKENS=768 \
RUN_TIMEOUT=3600 \
EVALUATE=1 \
scripts/run_typecast_arena_packet_a8002.sh
```

原则：

- 单卡；
- 分片；
- 每次短跑；
- 跑前报备；
- 有人要卡就停；
- 不 overnight；
- 不多卡。

## 已完成的本地改动

新增：

```text
scripts/build_typecast_math200_source_rows.py
scripts/split_jsonl_shards.py
reports/20260616-decisive-typecast-gpu-plan.md
```

修改：

```text
scripts/materialize_typecast_math_live_receiver_packet.py
```

修改点：

```text
materializer 新增 --channels 参数，支持只生成决定性 cast 条件。
```

本地生成：

```text
experiments/20260616-local-typecast-arena-math200-decisive-source/source_rows.jsonl
experiments/20260616-local-typecast-arena-math200-decisive-source/typecast_math200_sender_stage_packet.jsonl
experiments/20260616-local-typecast-arena-math200-decisive-source/summary.json
experiments/20260616-local-typecast-arena-math200-decisive-source/README.md
```

本轮没有启动远程或 GPU。
