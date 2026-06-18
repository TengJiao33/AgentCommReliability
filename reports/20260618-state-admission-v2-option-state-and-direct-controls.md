# State Admission V2 Option-State And Direct Controls

日期：2026-06-18

## 审稿裁决

当前系列更值得保留的对象已经收窄：模型在显式 source/scope/verification 条件下，能否保持 option-state、admission units、rejections 和 final_decider state 的一致性。这个对象比宽泛的通信协议叙事更硬，也更容易和 DeLM、CICL、PerspectiveGap、ProvenanceGuard 等邻域拉开边界。

## GPU Evidence

| Run | Model / prompt | Main result |
| --- | --- | --- |
| `20260618-1650-a8002-state-admission-v2-smoke9-qwen25-7b` | 7B `unit_first` | `strict=0.0000`, `unit_recall=0.2222`, `downstream_ok=0.0000` |
| `20260618-1710-a8002-state-admission-v2-option-state-smoke9-qwen25-7b` | 7B `option_state_first` | `strict=0.0000`, `option_state_recall=0.6111`, `downstream_ok=0.2222` |
| `20260618-1724-a8002-state-admission-v2-option-state-smoke9-qwen25-14b` | 14B `option_state_first` | `strict=0.1111`, `option_state_recall=0.9259`, `unit_recall=0.5926`, `downstream_ok=0.4444` |
| `20260618-1732-a8002-state-admission-v2-direct-allfacts-smoke9-qwen25-14b` | 14B direct all facts | `gold_answer_ok=0.6667`; supply-drop 三个 variant 都选 Warehouse B |
| `20260618-1738-a8002-state-admission-v2-direct-admissible-smoke9-qwen25-14b` | 14B direct oracle-admitted facts | `admissible_downstream_ok=0.3333`; perturbation rows 为 `0.0000` |

## 读法

`option_state_first` 不是空转。7B 的 `option_state_recall` 到 `0.6111`，14B 到 `0.9259`。这说明第一版 `unit_first` 的失败确实混入了 schema 影响。

14B 的低 strict 仍然有研究价值。它多数时候会列对 option states，却仍会漏 rejection、输出 absent unit，或在 admissible evidence 不足时继续给出原始 gold answer。失败对象从“选项极性”进一步收窄到 certificate consistency 和 admissible abstention。

direct controls 把 reviewer objection 变清楚。All-facts direct answer 在 supply-drop 上被 Warehouse B 的 shared-context 诱导，说明直接把所有事实塞给 final decider 不是强 baseline。Admissible-facts direct answer 在所有 perturbation 上都没有输出 insufficient，说明最终决策层存在强制选择倾向。

## Out-of-box 调整

主实验不要继续扩大同款 9-row prompt。下一步应该先改 benchmark shape：每行显式落盘 `expected_option_states`，并把 direct all-facts、direct admissible-facts 作为每个 packet 的标准 controls。

Supply-drop 不能无审计扩样。它在 direct all-facts 下三行全错，说明 shared-context distractor 太强。它可以保留为“tempting context suppresses hazard blocker”的压力案例，但不适合单独代表 task understanding。

Perturbation rows 需要单独标注 final_decider abstention target。现在 gold answer 仍保留原始 HiddenBench gold，而 `expected_downstream_state` 要求 insufficient。这个设计合理，但报告和 scorer 必须把 `gold_answer_ok` 与 `admissible_downstream_ok` 分开，否则很容易被审稿人读成自相矛盾。

下一包应加入 privacy/RBAC-style rejection。AgentLeak 和 OrgAccess/RBAC 类外部压力会问内部通道、权限、角色可见性是否真正被执行。当前 option-choice rows 已经有 scope perturbation，但还缺更自然的权限拒绝任务。

## Go / No-Go Update

Go 条件被改写：不要求 14B 在 option-state 层继续大错。更有价值的 go 条件是，14B 在 option-state 已高的情况下仍然稳定失败于 rejections、absent units、final_decider abstention，且 direct controls 能定位这些失败。

No-go 条件也更清楚：如果加入 abstention-specific prompt 后 perturbation rows 接近 oracle，State Admission V2 应降级为 schema/control note，主线转向更自然的 RBAC/privacy admission。

## External Pressure

DeLM 和 CICL 压 shared substrate 与 evidence packing，所以我们需要把 claim 固定在 role-scoped admissibility consistency，而不是共享上下文优化。来源：https://arxiv.org/html/2606.10662v1 和 https://arxiv.org/abs/2606.08151

PerspectiveGap 压 role-fragment assignment，ProvenanceGuard 压 answer 后 source verification。我们当前更接近答前 admissibility certificate，但必须保留 direct-answer controls，避免被看成普通任务求解失败。来源：https://arxiv.org/html/2606.08878v1 和 https://arxiv.org/abs/2606.18037

AgentLeak 与 OrgAccess/RBAC 提醒下一包要覆盖内部通道和权限拒绝。来源：https://arxiv.org/html/2602.11510v3 和 https://openreview.net/forum?id=oyjdyS7hBZ

## Immediate Next Step

冻结这组 9-row 作为 diagnostic slice。下一轮不扩样，先做一个 `abstention_explicit` schema ablation：在 prompt 中强制 final_decider 先判断是否存在 exactly one enabled admissible option，再允许输出 answer。若 14B 仍然在 perturbation 中强制选择，扩到 30-50 rows 才值得。
