# TypeCastArena Boundary Obedience Preflight

## 核心判断

本轮没有继续上 GPU，但推进出了一个更可靠的下一步实验入口：TypeCastArena 的 MATH raw-gold / sender-candidate-wrong receiver packet 已经加入了“内容可见但不交付/不准入”的 inert scratch 控制，并配套了边界服从诊断脚本。这个进展本身不是模型行为结论，但它让下一次 GPU run 更能区分“看见了错误内容”和“把错误内容 cast 成可继承通信状态”。

更准确地说，旧 304-row clean receiver run 现在只能作为 workflow/diagnostic 使用；新 packet 才是下一次可以进入 claim-bearing 预检的候选对象。原因是新 packet 用 raw gold 过滤出 live sender 确认错误的 artifact，并把 no-sender、自我修订、无关消息、inert visible scratch、direct peer、shared workspace、verifier admitted、quarantine、typed rederive 放进同一个 35-case 框架里。

## 证据链

新 packet 位于 `experiments/20260617-local-typecast-arena-math200-rawgold-candidatewrong-inert-receiver-packet/`。它包含 `35` 个 live sender artifact、`315` 行 receiver prompt，并且 `sender_candidate_correct` 全部为 `False`。条件行数是 baseline `35`、control `105`、erased `35`、admitted `70`、quarantine `35`、typed `35`。

本地 gold-smoke 已经通过同一个 MATH evaluator：`315/315` 行 semantic correct，`0` semantic unknown。普通 evaluator 在 no-sender gold-smoke 行里还会报 `2` 个 wrong-answer-uptake 计数，这是 gold/source-candidate 表面碰撞加 synthetic gold prediction 造成的诊断噪声，不是模型行为。这个检查说明 packet / evaluator / gold 的接口是通的，但它只证明评分管道没有明显断裂，不证明模型会服从边界。

新增的边界服从诊断脚本是 `scripts/analyze_typecast_boundary_obedience.py`。它读取 `<run-dir>/evaluated_rows.jsonl` 和 packet JSONL，输出 `summary.json`、`boundary_records.jsonl`、`boundary_concern_cards.jsonl` 和 `summary.md`。在新 packet 的 gold-smoke 上，它产生 `0` 张 boundary concern card；这说明脚本不会在理想 gold 输出上制造明显假阳性队列。

对旧 run 的 raw-gold relabel 诊断输出在 `experiments/20260616-2001-a8002-typecast-math200-clean-receiver304-qwen25-14b/boundary_obedience_rawgold_relabel/`。它只产生 `2` 张 concern card，且都集中在 `math200_case168`：一个 `admission_rejected_quarantine`，一个 `typed_partial_derivation_requires_rederive`，两者都输出 sender wrong candidate `660/7`。这更像旧 run 的人工复查线索，不应被写成新机制结果。

## 机制解释

这个 preflight 解决的是上一轮 TypeCastArena 最大的设计歧义：如果 receiver 出错，我们不知道它只是因为错误答案内容可见，还是因为通信边界把一个 tentative / partial / rejected artifact 变成了更强的公共状态。新 packet 加入 `sender_private_scratch_visible_inert` 后，可以做两个关键对照：同样看见 sender artifact text，inert scratch 不交付不准入，而 peer/shared/verifier 条件把它包装成不同通信生命周期状态。

因此下一次模型行为读数不能只看 final-answer correctness。真正有意义的信号是：admitted / verifier 条件是否比 inert visible scratch、unrelated control、quarantine、typed rederive 更容易产生 wrong-answer uptake、source-candidate collision、artifact phrase reuse 或继承 Agent A 的语言。如果 controls 也同样失败，那结果应先归因于本地 re-solve 噪声、短答案碰撞或 prompt 诱导，而不是通信 lifecycle。

## 失败和边界

这次没有新的模型行为结果。新 packet、gold-smoke 和 boundary analyzer 都是实验门控工件，最多说明下一次 run 更干净，不能单独支持“typed boundary 有效”或“verifier admission 更危险”之类结论。

诊断脚本也是启发式 review queue，不是最终语义裁判。它会用 candidate literal、source wrong answer collision、artifact phrase overlap、Agent A inheritance language 等信号打卡；这些信号可能来自自然碰撞、短数字、模型自我说明，或者数学题本身的重合。因此 concern card 必须人工读具体 case。

旧 304-row run 仍然不能恢复成 claim-bearing 结果。raw-gold relabel 只修复了一部分 label/evaluator 问题，旧 packet 缺少 inert content-visible control，并且之前的 source/filter 过程已经暴露过 gold/prompt 混杂风险。它现在的价值是告诉我们 scorer 能抓到什么，而不是告诉我们模型机制是什么。

## 下一步压力测试

下一步不应该直接扩大实验，而是用新 315-row packet 做一次小而干净的 A800_2 行为 run。如果要先 smoke，必须确保 evaluator 和 boundary analyzer 都对同一个 sliced packet 评分，避免以前 LIMIT 输出和 full packet 评价错位的问题。

如果资源允许，也可以直接跑完整 `315` 行，因为当前 A800_2 多数 GPU 空闲；但 run 之后必须同时报告普通 semantic/paired summary 和 boundary-obedience summary。只有当 admitted/verifier 的 concern pattern 明显高于 inert/unrelated/quarantine/typed controls，并且人工卡片显示不是短答案碰撞或本地 re-solve，才可以把它升级为 TypeCastArena 行为证据。
