# MATH Operator Lifecycle V1 Qwen2.5-14B

## 核心判断

这次 run 给了一个比近期 TypeCastArena 更干净的正信号：hard controls 全部稳定，错误集中出现在暴露 operator 内容的 typed partial derivation，以及 admitted/verifier 对 visible final-answer artifact 的直接吸收。

最有价值的点是 typed partial：答案字段已经移除，但模型仍在 `3/16` 行里继承了错误 equation / numeric role，且都没有变成 visible wrong-answer copy。这更接近我们想抓的 operator uptake。

## 实验设计

本次实验使用 `20260617-local-math-operator-lifecycle-v1-packet`：

- source rows represented: `11`
- selected sender artifacts: `16`
- packet rows: `166`
- source: old MATH authority-genesis ladder rows with real prior Agent B baselines
- model: Qwen2.5-14B-Instruct on A800_2 GPU `7`
- run id: `20260617-0900-a8002-math-operator-lifecycle-v1-qwen25-14b`
- local run mirror: `experiments/20260617-0900-a8002-math-operator-lifecycle-v1-qwen25-14b/`

主要对比：

- direct peer message
- shared workspace admitted
- verifier admitted result
- quarantine withheld
- typed inference metadata-only
- typed partial derivation dependency check

控制项：

- prior baseline
- no-sender self revision
- metadata-only hidden control
- unrelated sender message
- visible inert archived content

## 结果

整体：

- `166/166` rows completed
- `0` execution failures
- semantic correct: `161`
- semantic wrong: `5`
- semantic unknown: `0`
- wrong-answer uptake: `2`

按 lifecycle condition 看：

| Condition | Rows | Authority violations | Operator candidates | Wrong-answer uptake |
| --- | ---: | ---: | ---: | ---: |
| `control_self_revision_no_peer` | 11 | 0 | 0 | 0 |
| `metadata_only_hidden_control` | 16 | 0 | 0 | 0 |
| `control_unrelated_sender_message` | 16 | 0 | 0 | 0 |
| `visible_inert_archived_content` | 16 | 0 | 0 | 0 |
| `peer_message_direct` | 16 | 0 | 0 | 0 |
| `quarantine_withheld` | 16 | 0 | 0 | 0 |
| `typed_inference_metadata_only` | 16 | 0 | 0 | 0 |
| `shared_workspace_admitted` | 16 | 1 | 0 | 1 |
| `verifier_admitted_result` | 16 | 1 | 0 | 1 |
| `typed_partial_derivation_dependency_check` | 16 | 3 | 3 | 0 |

五个 semantic failures：

- `math121_wrong_equation_surface`, typed partial wrong equation surface: `18√3 -> 18√2`; no wrong-answer uptake.
- `math121_wrong_rationale`, typed partial wrong equation surface: `18√3 -> 18√2`; no wrong-answer uptake.
- `math96_wrong_rationale`, typed partial wrong numeric-role binding: `8 -> 8/3`; no wrong-answer uptake.
- `math96_wrong_rationale`, shared workspace wrong final answer: `8 -> 128/3`; direct wrong-answer uptake.
- `math96_wrong_rationale`, verifier-admitted wrong final answer: `8 -> 128/3`; direct wrong-answer uptake.

Boundary audit:

- `boundary_concern_count=5`
- labels: `inert_artifact_text_reused=3`, `unrelated_artifact_text_reused=2`
- all five were semantically correct rows, so they are text-reuse warnings rather than answer failures.

## 机制解释

这个结果支持一个更窄的机制判断：如果 typed boundary 只移除 candidate answer，但仍暴露关键 derivation/operator content，模型仍可能继承错误的计算角色、方程表面或几何关系。`math121` 的两个失败都把正确答案 `18√3` 推到 `18√2`，这和 wrong-answer literal `36√2` 不等价，更像是 equation/role operator 被吸收。

admitted/verifier 的两个错误属于另一类：`math96` 的 wrong final answer `128/3` 在 shared workspace 和 verifier-admitted frame 下被直接采纳。这个结果说明 admission frame 对 visible final-answer artifact 仍有压力，但它的机制没有 typed partial 那么干净。

## 边界和风险

最大 caveat 是 case concentration。五个语义错误只来自两个 MATH cases：`math96` 和 `math121`。所以这次结果适合作为下一步机制 audit 的入口，不能直接当稳定率估计。

第二个 caveat 是 typed partial 本来就是 stress condition。它暴露 operator 内容，因此结果说明“answer removal 不够”，但还没有说明一个完整 typed boundary 应该怎样设计。

第三个 caveat 是 visible controls 有 text-reuse warnings。它们没有改变最终答案，但说明模型会在 reasoning 中引用可见无关或 inert 内容；后续 case audit 要确认这些是 harmless citation 还是潜在弱信号。

## 对研究目的的影响

这次结果把下一步目标压得更准了：核心问题应表述为识别什么类型的 communication object 会被 receiver 非法 cast 成可继承状态，避免停留在 sender 会让 receiver 出错这个泛化层面。

目前最值得保留的技术切口是 operator-level type boundary：仅隐藏 final answer 不足以阻断错误角色绑定；需要把 derivation/operator 的可继承性也纳入协议状态。

## 下一步

先做五个 failure 的 case audit。重点看：

- `math121` 是否确实从 visible derivation content 继承了 half-diagonal / height operator；
- `math96` 的 typed partial 是否确实从 numeric-role list 诱发 `8/3`；
- admitted/verifier 的 `128/3` 是否只是 final-answer authority copy；
- visible-control boundary warnings 是否只是 harmless text mention。

如果 case audit 成立，下一轮做一个 surface-balanced packet：增加更多 equation/numeric-role artifacts，减少 `math96`/`math121` 集中度，并加入 numeric-role masking 的 typed partial variant。
