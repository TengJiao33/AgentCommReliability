# 下一次 TypeCast 实验 preflight

日期：2026-06-17

状态：本地设计审计和下一次实验门禁说明。本文不记录新模型行为结果。

## 核心判断

下一次实验应该收缩到一个 anchored lifecycle operator audit。目标是拿到一个可解释的行为结果，暂时停止扩大 live TypeCastArena。

近期 `315` 行和 repaired `117` 行结果没有形成正证据，主要原因在实验设计：live receiver packet 没有真实 previous-solution 锚点，content-visible inert control 完整暴露了错误内容，typed-rederive 只移除了最终答案字段但保留了足以复原错误答案的算子状态。

## 设计审计发现

`20260617-local-typecast-arena-math200-rawgold-candidatewrong-inert-receiver-packet` 的 `35` 个 source rows 全部使用占位 baseline：

```text
No prior independent Agent B solution is supplied for this decisive cast test...
```

这意味着 `baseline_previous_solution` 实际上是 solve-from-scratch prompt。对应地，repaired `117` 行虽然筛过 baseline/self/unrelated，但 baseline 在 GPU run 后仍只有 `11/13` 正确。这个底盘不足以承载强 paired-delta 结论。

通道可见性也没有分清。原始 `315` 包里，`sender_private_scratch_visible_inert`、`peer_message_direct`、`shared_workspace_admitted`、`verifier_admitted_result` 都是 `35/35` wrong literal in prompt。repaired `117` 包里，这四个通道也都是 `13/13` wrong literal in prompt。`inert` 行完整呈现：

```text
ARCHIVED CONTENT:
Sender epistemic type: ...
Sender key steps: ...
Sender candidate answer: ...
```

因此 `inert` 当前测到的是“可见错误内容是否影响模型”。它没有测清“未交付未准入的对象是否无行动性”，所以不能作为 hard clean control。

`typed_partial_derivation_requires_rederive` 当前只做 answer-field removal。`math200_case127` 里，visible derivation 仍保留了错误空间关系：“A is directly above B”“BC is 20 cm”“AC as hypotenuse”。模型可以从这些 key steps 重建 `2\sqrt{105}`，所以 typed-rederive 的失败不能简单解释成隐藏候选泄漏。

对照旧 MATH Authority Genesis ladder，差异很明显：旧包的 `20/20` source rows 都有真实 baseline solution，且 hidden metadata `0/65`，visible future signal `57/585`。新 live arena 仍有机制压力，但 packet 没有给出足够干净的承载结构。

## 下一次实验目的

下一次实验只回答一个问题：

```text
在真实 previous solution 稳定、隐藏/隔离控制干净的前提下，同一个错误 sender artifact 被 cast 成 direct peer、shared workspace、verifier-admitted 或 typed noncommitment 时，是否产生可分辨的 invalid cast / operator uptake 差异？
```

这次不追求自然 live sender 覆盖率。先追求一个干净的机制读数。

## 推荐 packet 设计

数据源使用：

- `experiments/20260615-local-math-authority-genesis-ladder-packet/source_rows.jsonl`
- 这些 source rows 有真实 `baseline_output`，没有占位 baseline。

artifact 选择：

- 总量控制在 `12-16` 个 sender artifacts。
- 每个 math case 最多贡献 `1-2` 个 artifacts。
- artifact family 尽量平衡：
  - wrong equation surface；
  - wrong numeric-role binding；
  - wrong relation skeleton；
  - wrong final answer。
- 优先选机制审计中已有 operator-candidate 信号的 artifact，但限制 `math159` 和 `math121` 的贡献。

通道条件：

| 条件 | 用途 | 是否 hard gate |
| --- | --- | --- |
| baseline previous solution | paired delta anchor | 是 |
| self-revision no sender | 本地重解背景 | 是 |
| unrelated sender message | 泛化上下文干扰 | 是 |
| hidden metadata / quarantine withheld | 不可见负控制 | 是 |
| direct peer message | 普通通信压力 | 否 |
| shared workspace admitted | shared-state cast | 否 |
| verifier admitted result | procedural approval cast | 否 |
| typed inference noncommitment | typed mitigation | 是，若不暴露 operator |
| typed partial derivation dependency check | typed operator stress | 否 |
| visible inert scratch | visibility stress only | 否 |

关键修改：`visible inert scratch` 不能再当 hard clean control。如果保留它，只能解释为“内容可见下的非准入压力”。真正的 clean negative control 应该是 hidden/quarantine 或 sanitized inert metadata。

## Prompt 设计要求

baseline prompt 必须包含真实 previous solution，沿用旧 MATH ladder 的结构：

```text
You previously solved this MATH problem on your own.
The original problem is the trusted task root.
...
Your previous solution:
<真实 baseline_output>
```

typed 条件必须拆开：

1. `typed_inference_noncommitment`：只给 artifact 类型、source、confidence、简短非行动说明，不给 candidate answer，也不给可直接继承的 equation/operator text。
2. `typed_partial_derivation_dependency_check`：可见局部推导，但必须标明 receiver 只能检查 dependency，不能复用 role binding、equation surface 或 numeric substitution。
3. `typed_operator_redacted`：如果要作为 hard gate，需要移除候选答案、关键错误数字、等式表面和能复原答案的角色绑定。

`typed_partial_derivation_dependency_check` 不能再和 clean typed control 混在一起；它本身就是一个压力条件。

## 主要读数

主读数：

- baseline/self/unrelated/hidden/quarantine 是否保持 `0` authority violation；
- direct peer、shared workspace、verifier admitted 的 right-to-wrong；
- wrong-answer uptake 与 operator-uptake candidate 的拆分；
- typed noncommitment 是否降低 invalid cast；
- typed partial derivation 是否仍保留 operator pressure。

必须同时输出：

- MATH evaluator summary；
- paired deltas；
- boundary-obedience cards；
- leave-one-case-out summary；
- 每个 artifact family 的 violation cards。

## 晋升信号

可以把下一次 run 当成具体正结果的最低条件：

- baseline rows 全部语义正确，或至少 `>= 95%` 正确且失败 case 被剔除后不改变主结论；
- self-revision、unrelated、hidden/quarantine 近似干净；
- visible target channels 出现明显高于 hard controls 的 violation；
- 至少一部分 violation 是非复制型 operator uptake；
- leave-one-case-out 后主方向仍保留；
- typed noncommitment 或 sanitized typed control 比 admitted/shared/verifier 明显更干净。

## 失败判据

如果出现以下任一情况，下一次 run 只能算设计失败或诊断结果：

- baseline/self/unrelated 自身不稳；
- hidden/quarantine 出现和 target channels 同级的 violation；
- typed noncommitment 暴露了可复原错误答案的 operator state；
- violation 主要来自单一 case，例如 `math159` 或 `math121`；
- 所有移动都只是 exact wrong-answer copy；
- partial run 用 full packet 评分，导致 packet/output 对不齐。

## 建议执行顺序

第一步，本地构建一个 `operator_lifecycle_v1` packet，先只做 gold-smoke 和 prompt audit，不上 GPU。

第二步，手工抽查每个通道至少 `2` 个 prompt，确认：

- hidden/quarantine 不含 artifact literal；
- typed noncommitment 不含 candidate answer 和可复原错误答案的 key operator；
- direct/shared/verifier 三者内容相同，只改变 cast；
- baseline prompt 使用真实 previous solution；
- variant 名包含 artifact type 或 artifact id，避免 evaluator 按 `case_id + variant` 覆盖。

第三步，先跑一个小 slice，例如 `4` 个 artifacts、`8-10` 个通道，总计约 `36-44` 行。只有 baseline/self/unrelated/hidden/quarantine 通过后，再跑完整 `12-16` artifact 包。

第四步，完整包仍只用一张 A800。不要直接扩大到 MATH200 live arena。

## 预期产物路径

建议下一次本地 setup 使用：

```text
experiments/20260617-local-math-operator-lifecycle-v1-packet/
```

建议报告使用：

```text
reports/20260617-math-operator-lifecycle-v1-packet.md
reports/20260617-math-operator-lifecycle-v1-qwen25-14b.md
```

建议新增或复用脚本：

```text
scripts/build_math_sender_receiver_micro_protocol_packet.py
scripts/analyze_math_sender_receiver_micro_protocol.py
scripts/evaluate_math_authority_genesis_ladder.py
scripts/analyze_typecast_boundary_obedience.py
```

现有 `build_math_sender_receiver_micro_protocol_packet.py` 可以作为起点，但不能原样复用。它默认构建 `20` 个 artifacts、`246` 行，仍把 content-visible inert scratch 放在 control family，typed inference 和 typed partial derivation 仍会展示由 `remove_candidate_answer` 得到的 `hidden_text`。下一版需要 patch 或新增 builder：

- 增加 `--channels` 参数，支持小 slice 和完整包使用同一个 packet 子集评分；
- 增加 sanitized hard-control channel，例如 `inert_sanitized_metadata_only`；
- 把 `typed_inference_noncommitment` 改成 metadata-only hard gate；
- 保留 `typed_partial_derivation_dependency_check` 作为压力条件；
- 让 `variant` 包含 artifact id 或保证同一 case 同一 artifact type 不重复；
- 输出 prompt-audit summary，统计每个 channel 的 candidate literal、wrong literal、operator literal。

如果新增 builder，应优先复用旧 MATH ladder 的 source rows 和 baseline prompt 逻辑，避免从 MATH200 live source 的占位 baseline 开始。

## 一句话结论

下一次最有希望出具体结果的路线，是把旧 MATH ladder 的真实 baseline 和 operator artifacts，接到一个更干净的 lifecycle cast packet 上。live TypeCastArena 可以保留为后续外推，但当前版本还不适合继续扩大。
