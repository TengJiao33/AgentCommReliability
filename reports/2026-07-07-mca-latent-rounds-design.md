# MCA 潜状态多轮交换设计

日期：2026-07-07

## 目标

这版实现更接近原始想法：

```text
agent 在答案收敛前交换思考状态；
不交换最终答案；
不读取 peer 文本；
多轮 latent round 之后才生成最终答案。
```

之前几条线都提供了诊断，但偏离了这个核心想法：

- `question_only` Pre-KV 主要传的是题目编码，不是思考状态；
- `early_plan` Pre-KV 传 live KV，容易变成接着别人半截回答往下写；
- `micro-commitment` 引入显式人工字段，变成 prompt protocol 工程。

## 运行入口

```text
scripts/run_mca_latent_rounds.py
```

每道题跑两个 paired condition。

## A. 基线私有轮次

每个 agent 做同样轮数的私有 pre-answer thought：

```text
Round 0: private natural thought
Round 1: private natural thought
...
Final: output answer
```

不使用 peer state。

## B. 潜状态交换轮次

latent 条件下，agent 从第 1 轮之后接收上一轮 peer states 的 latent message：

```text
Round 0:
  每个 agent 私下思考；
  捕获各自的 latent vector。

Round r > 0:
  每个 agent 接收 peer latent message；
  用 activation steering 注入；
  agent 继续私下思考；
  捕获新的 latent vector。

Final:
  agent 使用自己的 private thought trajectory；
  默认不再注入 peer vector；
  只在这里输出最终答案。
```

不展示同伴文本：

```text
visible_peer_text = false
```

交换对象是由私有思考得到的激活向量：

```text
state_fusion = mean_peer_activation
```

这样避开 raw KV 的主要问题：接收方不需要接着另一个 agent 的半截 assistant completion 写。

## 为什么它更贴近 MCA 想法

这里的辩论不是文本反驳，而是多轮状态更新：

```text
private state -> latent message -> private state update -> latent message -> final answer
```

轮数由参数控制：

```bash
--latent-rounds 2
```

## 记录指标

主要转移类型：

```text
BaC_to_C: baseline correct, latent correct
BaC_to_W: baseline correct, latent wrong
BaW_to_C: baseline wrong, latent correct
BaW_to_W: baseline wrong, latent wrong
```

主指标：

```text
latent_delta_vs_baseline = latent_correct - baseline_correct
```

诊断指标：

```text
thought_answer_marker_count
thought_gold_suspect_count
```

这两个用于检查私有思考是否提前出现显式最终答案标记，或被解析器怀疑包含标准答案。

## 初始安全参数

先跑分歧子集：

```bash
--split mca_disagreement_v1
--latent-rounds 2
--thought-tokens-per-round 96
--private-thought-style natural
--steering-layer 16
--steering-scale 0.05
--normalize-steering
--peer-message-max-norm 1.0
--same-seed-conditions
--no-apply-peer-on-final
```

先看分歧子集上是否能多救错、少伤对，再考虑扩大。

## 第一次远程停止后的修正

第一次远程尝试用了未归一化 peer vector 和：

```text
--steering-scale 1.0
```

观测到同伴向量范数大约 60-80。跑完 6 条后停止。

修正后的 runner 做了这些事：

- 思考状态差量默认归一化；
- 融合后的同伴消息用 `--peer-message-max-norm` 截断；
- 默认 steering scale 降到 `0.05`；
- 私有思考提示词默认 `natural`；
- 更强的 critique/refinement 提示词只通过 `--private-thought-style deliberative` 显式打开；
- 基线条件和潜状态条件默认使用匹配种子；
- 最终答案默认不接收同伴 steering；
- records 写入同伴消息元数据，包括 raw norm、effective norm、是否 clipped、fusion mode、source count。

## 最终阶段注入小样本测试

6 条 smoke 的 effective peer-message norm：

```text
effective peer-message norm ≈ 0.87 - 0.97
```

但是最终阶段继续注入最后一轮同伴向量，会伤一题基线正确样本：

```text
apply_peer_on_final=true:
  baseline_correct = 2/6
  latent_correct = 1/6
  transitions = 4 BaW_to_W, 1 BaC_to_C, 1 BaC_to_W
```

变化样例：

```text
gold = pi
baseline majority = pi
latent majority with final steering = 3*pi/2
```

匹配小样本测试关闭最终阶段同伴 steering：

```text
apply_peer_on_final=false:
  baseline_correct = 2/6
  latent_correct = 2/6
  transitions = 4 BaW_to_W, 2 BaC_to_C
```

默认协议：

```text
潜状态通信只影响私有轮次；
最终解码使用 agent 自己的私有轨迹；
最终阶段 steering 只作为显式诊断开关。
```
