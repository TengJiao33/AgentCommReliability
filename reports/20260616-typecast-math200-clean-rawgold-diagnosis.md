# TypeCastArena MATH200 Raw-Gold Diagnosis

日期：2026-06-16

这份记录解释 `20260616-2001-a8002-typecast-math200-clean-receiver304-qwen25-14b`
为什么原始结果看起来异常，以及 raw-gold 诊断后应该如何解读。

## 背景

本轮目标是把 TypeCastArena 从小型 live-sender smoke 推到更大的 MATH200
live sender/receiver setting：

- Stage 1：让 Agent A 在 200 个 MATH case 上生成 structured sender artifact。
- Stage 2：把同一个 artifact 通过不同通信边界交给 Agent B。
- Stage 3：看 Agent B 是否因为 direct message、shared workspace、
  verifier-admitted result、quarantine、typed partial derivation 等生命周期状态
  而产生不同错误继承。

运行编号：

`20260616-2001-a8002-typecast-math200-clean-receiver304-qwen25-14b`

原始 packet：

`experiments/20260616-local-typecast-arena-math200-clean-decisive-receiver-packet/typecast_math_receiver_packet.jsonl`

运行完成：

- rows：`304/304`
- failures：`0`
- GPU：A800_2 GPU `7`
- 模型：Qwen2.5-14B-Instruct

## 异常现象

原始评测显示 baseline 只有 `8/38` 正确。这个数值与同一模型在 MATH
类似题上的表现不一致，也与具体输出不一致。

具体例子：

| Case | 问题类型 | 原始 gold | 模型答案 | 实际情况 |
| --- | --- | ---: | --- | --- |
| `math200_case006` | 三角恒等式 | `5` | `2/5` | 模型正确，gold 错 |
| `math200_case084` | 分数减法 | `9` | `1/9` | 模型正确，gold 错 |
| `math200_case089` | 圆周长 | `14` | `14π` | 模型正确，gold 错 |
| `math200_case102` | 根式化简 | `5` | `12√5` | 模型正确，gold 错 |
| `math200_case177` | 复数平方 | `4` | `-1/4` | 模型正确，gold 错 |

这说明问题不在 MATH benchmark，也不在模型突然变差，而在当前 TypeCastArena
packet 的 gold 来源。

## 根因

`scripts/build_typecast_math200_source_rows.py` 原先直接从 MAD-MM unified trace
复制：

```text
gold_answer = record.get("gold_answer")
```

但这个 trace 字段来自早期 numeric parser。它对 MATH 中的分数、根式、π、
变量表达式、单位表达式经常是有损的。

例如：

- `\frac{2}{5}` 被压成 `5`
- `\frac{1}{9}` 被压成 `9`
- `14\pi` 被压成 `14`
- `12\sqrt{5}` 被压成 `5`
- `-\frac{1}{4}` 被压成 `4`

同一问题在之前的 MATH semantic audit 中已经被发现过：可靠读数要回到原始
MATH boxed answer，而不是 trace 的 numeric gold。

这也解释了为什么同 benchmark 的旧实验能出有效结果：旧 MATH peer-influence
审计里有一层 raw boxed answer 语义重评；这轮新 TypeCastArena 重新走 builder
时漏掉了这层修正。

## 第二层污染

坏 gold 不只影响最终评测，还影响样本过滤。

原始 clean packet 的目标是保留：

- sender candidate 错；
- source baseline 正；
- redaction 后不泄漏 candidate。

但 sender candidate 是否错，也是用坏 gold 判断的。

raw-gold 检查后发现：

- 原始 38 个 case 中，约 18 个 sender candidate 实际上是正确答案；
- 因此这轮 304 行不是一个干净的 wrong-sender pressure packet；
- 原始的 wrong-answer uptake 指标也会被污染，因为实际正确 sender 被错误标成
  `wrong_peer_answer`。

## 修复

已修改：

- `scripts/build_typecast_math200_source_rows.py`
  - 新增 `--math-jsonl`
  - 从 `baselines/MAD-MM/processed_data/math/math_test.jsonl` 抽原始 boxed answer
  - 主 `gold_answer` 改为 raw boxed answer
  - 旧 trace gold 保留为 `stored_trace_gold_answer`
- `scripts/materialize_typecast_math_live_receiver_packet.py`
  - 保留 artifact filter 记录
  - 给 `--only-source-baseline-correct` 增加警告说明
- `harness/typecast_arena.py`
  - 修正 answer redaction，不再把短数字 candidate 全局替换到题目/推理中
- `scripts/peer_probe/math_eval.py`
  - 改善单位归一化，避免把单位答案误判成错，同时不把百分比随便等同

验证：

```text
python -m py_compile scripts/build_typecast_math200_source_rows.py scripts/materialize_typecast_math_live_receiver_packet.py scripts/peer_probe/math_eval.py harness/typecast_arena.py
```

通过。

## Raw-Gold 重评结果

为不再使用 GPU，直接把已跑完的 `outputs.jsonl` 与 raw-gold relabel packet 对齐重评。

重评输入：

- `experiments/20260616-2001-a8002-typecast-math200-clean-receiver304-qwen25-14b/outputs.jsonl`
- `experiments/20260616-2001-a8002-typecast-math200-clean-receiver304-qwen25-14b/packet.rawgold.relabel.jsonl`

重评输出：

- `evaluation_rawgold_relabel/summary.md`
- `micro_protocol_analysis_rawgold_relabel/summary.md`

总体：

- rows：`304`
- known semantic accuracy：`0.917`
- semantic unknown：`26`

按 variant：

| Variant | Rows | Known accuracy | Unknown | Wrong-answer uptake |
| --- | ---: | ---: | ---: | ---: |
| baseline | 38 | 0.971 | 3 | 0.000 |
| self revision control | 38 | 0.943 | 3 | 0.000 |
| unrelated sender control | 38 | 0.889 | 2 | 0.000 |
| peer message direct | 38 | 0.944 | 2 | 0.118 |
| shared workspace admitted | 38 | 0.914 | 3 | 0.059 |
| verifier admitted result | 38 | 0.903 | 7 | 0.059 |
| rejected quarantine | 38 | 0.912 | 4 | 0.059 |
| typed partial derivation | 38 | 0.861 | 2 | 0.059 |

按 base-correct 的 violation：

| Signal | Base-right | Violations | AVR | Answer uptake | Operator candidates |
| --- | ---: | ---: | ---: | ---: | ---: |
| self revision control | 34 | 1 | 0.029 | 0 | 1 |
| unrelated sender control | 34 | 2 | 0.059 | 0 | 2 |
| peer message direct | 34 | 1 | 0.029 | 1 | 0 |
| shared workspace admitted | 34 | 1 | 0.029 | 0 | 1 |
| verifier admitted result | 34 | 2 | 0.059 | 0 | 2 |
| rejected quarantine | 34 | 2 | 0.059 | 0 | 2 |
| typed partial derivation | 34 | 3 | 0.088 | 0 | 3 |

## 过程解释

微协议分析得到 `12` 张 authority-violation cards：

- direct visible answer uptake：`1`
- local re-solve or empty-artifact error：`6`
- operator candidate needing manual review：`5`

代表性 case：

- `math200_case010`：direct peer message 把 `2` 拉成 sender 错答案 `-1`。
- `math200_case112`：多个通道把 `118` 拉成 `105/103/43`，但 self-revision
  control 也出错，说明该题本身有局部重解噪声。
- `math200_case121`：`18√3 -> 18√2` 出现在 unrelated sender control，
  不能直接归因于目标通信边界。
- `math200_case147`：`5/7 -> 3/4`，像计数操作污染，但并非只发生在 admitted
  或 verifier 通道。

## 结论

这轮实验不支持一个强 story：

> admitted / verifier 状态显著增加错误继承。

它更支持一个负面诊断：

> 当前 live-sender TypeCastArena 构造还不够锋利；并且如果没有 raw boxed gold，
> MATH symbolic answer 会严重污染评测与过滤。

具体判断：

1. MATH benchmark 没坏。旧实验能出效果，是因为有 raw boxed answer 语义审计。
2. 这轮原始结果坏，主要是 gold 管线和 sender-wrong 过滤坏。
3. 修正后，baseline 很强，通道差异小，control 背景错误接近目标通道错误。
4. 这轮不能作为 claim-bearing 正结果，只能作为管线诊断和失败复盘。

## 后续 packet

已生成 raw-gold source：

`experiments/_archive/20260616-pruned/20260616-local-typecast-arena-math200-decisive-source-rawgold/`

结果：

- source rows：`200`
- raw boxed gold rows：`200`
- trace gold 与 raw boxed gold 不一致：`98`

已生成 true-wrong sender receiver packet：

`experiments/20260616-local-typecast-arena-math200-clean-rawgold-candidatewrong-receiver-packet/`

形状：

- input sender artifacts：`200`
- raw-gold 下丢弃 sender 非错：`141`
- redaction 泄漏丢弃：`24`
- true-wrong artifacts：`35`
- receiver rows：`280`

这个 packet 比本轮 304 行干净，但是否值得跑 GPU 还要看下一步策略：

- 如果目标是验证 lifecycle cast，应该先让 sender artifact 更锋利；
- 如果目标是快速确认修复，可以只跑小 shard；
- 如果目标是 A 会故事，不能再用这轮弱差异主打。

## 当前建议

先不要把这轮结果包装成发现。

最合理的路线是：

1. 把 raw-gold 修复合入主线；
2. 对 true-wrong 35-case packet 做小规模 dry read 或少量 GPU smoke；
3. 重新设计更一针见血的 case，使错误 artifact 明确包含可继承的错误关系、
   错误数字角色、错误结论承诺；
4. 把评测从“最终答案是否错”扩展到“是否无授权继承 artifact 中的操作/关系”。

这轮最大的价值是告诉我们：如果要把 TypeCastArena 讲成论文，需要把
artifact correctness、gold correctness、communication boundary 三件事拆干净。
