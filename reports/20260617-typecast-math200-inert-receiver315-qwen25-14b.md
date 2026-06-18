# TypeCastArena Inert Receiver315 结果

## 核心判断

这次 A800_2 run 给出了一个可靠但偏负面的进展：新 TypeCastArena 315-row packet 跑通了，评估和 boundary triage 也完整跑通了，但它没有通过 control gate。当前结果不能支持“admitted/verifier lifecycle 比 inert/control 更容易诱发 invalid cast”这个正向说法；它更像是在告诉我们，下一版 packet 必须先修 baseline 稳定性和 final-answer 输出。

更准确地说，这不是对研究想法的 true negative。它压力到的是实验设计：receiver baseline 只有 `16/35` case 是正确的，而且 `missing_answer` 很高；在这种底盘上，self-revision、unrelated control、inert visible scratch、quarantine、typed rederive 和 admitted/peer 条件都出现了可比的 right-to-wrong 压力。

## 证据链

运行记录在 `experiments/20260617-0033-a8002-typecast-math200-inert-receiver315-qwen25-14b/`。远端使用 A800_2 GPU 7、Qwen2.5-14B-Instruct、temperature `0`、max tokens `768`，完成 `315/315` 行，失败 `0` 行。跑完后 vLLM 服务已清理，GPU 7 回到空闲状态。

本地重评后的 `evaluation/summary.json` 显示：`315` 行里 semantic correct `124`、semantic wrong `109`、semantic unknown `82`，known semantic accuracy `0.532`。远端原始 evaluator stdout 是 `125` correct，本地重评少 `1` 行，属于 parser/版本噪声，不影响判断。

最关键的 paired readout 只覆盖 `16` 个 baseline-correct case。在这些 case 上，authority violations 分布为：self-revision `1/16`，unrelated control `2/16`，inert visible scratch `2/16`，peer direct `2/16`，shared workspace `2/16`，verifier admitted `3/16`，quarantine `3/16`，typed rederive `2/16`。这个形状不支持生命周期分离。

boundary triage 也显示控制没有守住：总 concern cards 为 `22/315`，其中 inert visible scratch `9`，typed rederive `7`，quarantine `4`，unrelated visible control `2`。admitted/erased 行没有被标成 boundary concern，是因为这些通道按协议允许看到 artifact；但它们的 raw wrong-answer uptake 也高，peer/shared/verifier 都是 `10/35`，inert visible scratch 是 `9/35`，差不出来。

## 机制解释

这次 run 暴露出的主要机制不是“准入状态增强了权威”，而是“可见错误内容和 receiver 自身不稳定已经足够强”。`sender_private_scratch_visible_inert` 明确标成未交付、未准入，但仍然产生 `9` 张 concern card，说明当前 prompt 下模型并没有可靠地区分“看见一段 sender scratch”和“可继承通信对象”。

case-level 也支持这个判断。`17` 张 paired authority-violation row 中，`math200_case112` 和 `math200_case127` 各占 `5` 张；它们在多个条件下同时失败，包括控制或非准入条件。这种 case concentration 更像局部 re-solve / prompt sensitivity，而不是一个干净的 lifecycle 梯度。

## 失败和边界

这个实验未能回答原问题，因为控制条件出现了与目标条件相近的失败率。按 `research-experiment-gate`，这应归类为 control-gate / design failure，而不是行为机制结论。

还有一个评估边界：semantic unknown 有 `82` 行，baseline 自身有 `9/35` missing-answer。这说明当前 receiver prompt 对 final answer 格式约束不够硬，或者这批 source case 对 Qwen2.5-14B 太不稳。后续不能用这个 run 的总体 accuracy 或 raw wrong-answer uptake 当强证据。

## 下一步压力测试

下一步不应继续扩大 GPU。更小更尖的动作是本地构造 v2 receiver packet：只保留本次 run 中 receiver baseline-correct 的 case，或者先单独跑/筛 baseline-only；同时把 prompt 改成强 final-answer contract，降低 missing-answer。然后再保留 inert visible scratch、unrelated control、quarantine、typed rederive 作为硬 gate。

如果下一版仍然出现 inert/quarantine/typed 与 admitted/verifier 同样失败，就应把 TypeCastArena 当前 MATH 形态标成不适合承载 lifecycle claim，转向更受控的人工 artifact 或更稳定的任务切片。如果 repaired packet 里 admitted/verifier 才明显分离，才值得升级为行为证据。
