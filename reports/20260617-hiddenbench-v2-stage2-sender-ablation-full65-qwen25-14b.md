# HiddenBench V2 Stage 2 Sender Ablation Full65

## 核心判断

Stage 2 full65 明确支持继续把 idea 收束到 sender-side public-state discipline。单独禁止推荐、单独禁止共享信息复述都有恢复作用，但恢复幅度远低于 fact-only；在 clean subset 上，fact-only 达到 `55/55`，禁推荐只有 `28/55`，禁共享复述只有 `31/55`。

这说明 Stage 1 的提升不能用一个简单禁令解释。旧 sender context 同时带来三类问题：过早偏好压缩、共享优势重放、私有事实搬运不精确。fact-only 的强信号来自这三类问题一起被压住。

## 运行信息

- Run id: `20260617-1807-a8002-hiddenbench-v2-stage2-sender-ablation-full65-qwen25-14b`
- Remote path: `/data/xuhaoming/yfy/research_workspace/experiments/20260617-1807-a8002-hiddenbench-v2-stage2-sender-ablation-full65-qwen25-14b/`
- Local path: `experiments/20260617-1807-a8002-hiddenbench-v2-stage2-sender-ablation-full65-qwen25-14b/`
- Model: `Qwen2.5-14B-Instruct`
- GPU / port: `A800_2` GPU `7`, port `8047`
- Limit: `65`
- Records: `585`
- Failures: `0`
- Unparsed: `0`
- Prompts saved: `false`

Run completed cleanly. The vLLM service exited through the launcher cleanup path; GPU7 and port `8047` were free after completion.

## Raw 和 Corrected 结果

Corrected scoring produced `0` rescoring changes.

| Condition | Correct / 65 |
| --- | ---: |
| `shared_only` | `1` |
| `exchange_then_decide` | `24` |
| `no_recommendation_exchange` | `30` |
| `no_shared_repeat_exchange` | `33` |
| `oracle_public_facts` | `56` |
| `fact_only_constraint_decide` | `56` |
| `fact_only_with_options_exchange` | `56` |
| `fact_only_exchange` | `57` |
| `full_info` | `59` |

Raw result already shows the split：局部 sender ban 比旧 exchange 好一点，但远低于 fact-only。`fact_only_exchange` 仍接近 `full_info` 和 `oracle_public_facts`。

## Clean Subset

主读数是 clean subset：`full_info` 和 `oracle_public_facts` 都正确的 `55` 个任务。

| Condition | Correct / 55 |
| --- | ---: |
| `shared_only` | `0` |
| `exchange_then_decide` | `23` |
| `no_recommendation_exchange` | `28` |
| `no_shared_repeat_exchange` | `31` |
| `fact_only_with_options_exchange` | `53` |
| `fact_only_exchange` | `55` |
| `fact_only_constraint_decide` | `55` |

clean subset 上，`fact_only_exchange` 相比旧 exchange 多救 `32` 个任务，没有 regression。相比 `no_recommendation_exchange` 多救 `27` 个任务，没有 regression。相比 `no_shared_repeat_exchange` 多救 `24` 个任务，也没有 regression。

局部禁令本身不稳定。`no_recommendation_exchange` 比旧 exchange 多救 `11` 个 clean tasks，但也让 `6` 个旧 exchange 正确任务变错。`no_shared_repeat_exchange` 多救 `10` 个 clean tasks，同时有 `2` 个 regression。这个现象说明“禁推荐”或“禁共享复述”单独作为方法都不干净。

## Message Audit

自动 message audit 给出机制解释。

| Condition | Rec leakage | Shared overtalk | Private exact | Avg private overlap |
| --- | ---: | ---: | ---: | ---: |
| `exchange_then_decide` | `225/253` | `134/253` | `6/253` | `0.656` |
| `no_recommendation_exchange` | `12/253` | `176/253` | `2/253` | `0.628` |
| `no_shared_repeat_exchange` | `191/253` | `28/253` | `6/253` | `0.715` |
| `fact_only_exchange` | `0/253` | `4/253` | `198/253` | `0.951` |
| `fact_only_with_options_exchange` | `0/253` | `4/253` | `199/253` | `0.947` |

禁推荐确实压低 recommendation leakage，但共享事实复述变得更重，私有事实 exact count 还更低。禁共享复述确实压低 shared overtalk，但 recommendation leakage 仍然很高。fact-only 同时压低两类污染，并显著提高私有事实搬运精度。

## Case Triage

case-level triage 和 aggregate 一致。

- `no_recommendation_exchange` 在 clean subset 中救了 `11` 个旧 exchange 错误任务，但回退了 `6` 个旧 exchange 正确任务。
- `no_shared_repeat_exchange` 救了 `10` 个旧 exchange 错误任务，但回退了 `2` 个旧 exchange 正确任务。
- `fact_only_exchange` 相比 `no_recommendation_exchange` 额外救 `27` 个 clean tasks，且没有 clean regression。
- `fact_only_exchange` 相比 `no_shared_repeat_exchange` 额外救 `24` 个 clean tasks，且没有 clean regression。
- `fact_only_exchange` 相比 `fact_only_with_options_exchange` 额外救 `2` 个 clean tasks：`baker_2010` 和 `secure_meeting_room_decision`。

具体 case list 见 `experiments/20260617-1807-a8002-hiddenbench-v2-stage2-sender-ablation-full65-qwen25-14b/case_triage_summary.md`。

## 解释

目前最稳的机制表述是：HiddenBench 这类 hidden-profile 任务里，LLM sender 在默认对话式 exchange 中倾向把私有事实转成偏好、推荐、共享优势重放，导致公共状态没有干净承载隐藏事实。final decider 看到的是被偏好污染和共享信息稀释过的消息流，所以即使所有私有事实理论上都被各 agent 看到，最终仍选错。

fact-only protocol 的价值不在复杂 final integration。`fact_only_constraint_decide` 没有超过 `fact_only_exchange`，full65 clean subset 上二者都是 `55/55`。当前更值得做的是 sender public-state contract：要求 agent 把私有事实作为事实进入公共状态，并延迟推荐/排序/排除。

## 边界

这个结果强于 smoke12，但仍是 project-local HiddenBench protocol、单模型 Qwen2.5-14B、temperature `0`。message audit 是 proxy，尤其 shared-overtalk 和 exact-private-fact 受词面匹配影响，后续需要人工 case card 或更稳的 semantic audit。

`fact_only_with_options_exchange` 只比 fact-only 少 `2` 个 clean tasks，所以 option visibility 只是边界因素。故事重心不应放在“是否展示选项”。

## 对 Idea 的影响

旧的宽泛说法“让 agent 不要过早推荐”太弱。full65 显示仅禁推荐只有 `28/55` clean accuracy，还会制造 `6` 个 clean regression。更好的 idea 是：在 hidden-profile multi-agent tasks 中，sender public messages 需要先形成事实型公共状态，再允许偏好或最终选择进入协议。

这个 idea 的外部新颖性仍然要继续被压。hidden profile 的共享信息偏置是已知心理学现象；我们这里较有价值的切口是 LLM agent 版本的 sender-side decomposition：推荐泄漏、共享复述、私有事实搬运精度可以被分开测，并且单独禁令无法达到 clean fact-state 的效果。

## 下一步

我建议不要马上继续堆 HiddenBench prompt variant。下一步应该做一个更像方法的最小 protocol：

- sender phase: fact-state admission，只允许私有事实和来源；
- verifier/admission phase: 检查是否复述共享信息、是否给推荐、是否遗漏私有事实；
- decision phase: 在 admitted public facts 上选择答案。

然后把同一思想转到一个外部不同形态的 communication-necessary benchmark，例如 PACT-style split evidence 或 SOTOPIA-TOM contact。HiddenBench full65 现在足够支撑机制方向，但还不能独自支撑完整 paper story。
