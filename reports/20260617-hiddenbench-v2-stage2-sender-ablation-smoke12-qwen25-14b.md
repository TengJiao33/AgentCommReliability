# HiddenBench V2 Stage 2 Sender Ablation Smoke12

## 核心判断

Stage 2 smoke12 支持继续追 sender-side 机制，但把 story 压窄了：单独禁止推荐或单独禁止共享信息复述只能救一部分旧 exchange 失败，完整 fact-only 仍然明显更强。更准确地说，当前信号指向“sender 是否把私有事实精确搬进公共状态”，而不只是“sender 是否过早表态”。

这个结果还不能直接变成方法结论。它是一个拆因子诊断：在前 12 个 HiddenBench 任务上，旧 exchange 的失败可以被两个局部约束部分缓解，但只有强 fact-only surface 接近 clean-information upper bound。

## 运行信息

- Run id: `20260617-1752-a8002-hiddenbench-v2-stage2-sender-ablation-smoke12-qwen25-14b`
- Remote path: `/data/xuhaoming/yfy/research_workspace/experiments/20260617-1752-a8002-hiddenbench-v2-stage2-sender-ablation-smoke12-qwen25-14b/`
- Local path: `experiments/20260617-1752-a8002-hiddenbench-v2-stage2-sender-ablation-smoke12-qwen25-14b/`
- Model: `Qwen2.5-14B-Instruct`
- GPU / port: `A800_2` GPU `7`, port `8047`
- Limit: `12`
- Conditions: `shared_only`, `full_info`, `oracle_public_facts`, `exchange_then_decide`, `no_recommendation_exchange`, `no_shared_repeat_exchange`, `fact_only_with_options_exchange`, `fact_only_exchange`, `fact_only_constraint_decide`
- Records: `108`
- Failures: `0`
- Unparsed: `0`

Execution note: an earlier background launch with run id prefix `20260617-1745` failed before model loading because a PowerShell-generated temporary shell wrapper hit a CRLF/path parsing issue. It produced no model calls and is not behavior evidence. The successful run used direct `nohup env ... bash scripts/run_hiddenbench_probe_a8002.sh`.

## 结果

Corrected scoring produced no changes from raw scoring.

| Condition | Correct / 12 |
| --- | ---: |
| `shared_only` | `1` |
| `exchange_then_decide` | `2` |
| `no_recommendation_exchange` | `5` |
| `no_shared_repeat_exchange` | `5` |
| `fact_only_with_options_exchange` | `8` |
| `oracle_public_facts` | `8` |
| `full_info` | `9` |
| `fact_only_exchange` | `9` |
| `fact_only_constraint_decide` | `9` |

Clean subset 更关键。只看 `full_info` 和 `oracle_public_facts` 都正确的 `8` 个任务，旧 exchange 是 `2/8`，禁推荐是 `4/8`，禁共享复述是 `4/8`，fact-only-with-options 是 `7/8`，fact-only 是 `8/8`。这说明两个局部禁令都有用，但各自只修到一半。

Paired contrast 的方向也一致。在 clean subset 上，`no_recommendation_exchange` 相比旧 exchange 只多救 `2` 个任务，`no_shared_repeat_exchange` 也只多救 `2` 个任务；`fact_only_exchange` 相比这两个局部条件各自还多救 `4` 个任务。`fact_only_constraint_decide` 和 `fact_only_exchange` 完全一致，继续削弱“final-decider prompt 是主瓶颈”的解释。

## Message Audit

自动 message audit 给出的机制切面很清楚。

| Condition | Rec leakage | Shared overtalk | Private exact | Avg private overlap |
| --- | ---: | ---: | ---: | ---: |
| `exchange_then_decide` | `41/45` | `25/45` | `6/45` | `0.714` |
| `no_recommendation_exchange` | `0/45` | `28/45` | `2/45` | `0.621` |
| `no_shared_repeat_exchange` | `31/45` | `5/45` | `3/45` | `0.740` |
| `fact_only_exchange` | `0/45` | `4/45` | `28/45` | `0.896` |
| `fact_only_with_options_exchange` | `0/45` | `4/45` | `28/45` | `0.876` |

`no_recommendation_exchange` 的推荐泄漏降到 `0/45`，但共享信息复述反而到 `28/45`，私有事实 exact 只有 `2/45`。`no_shared_repeat_exchange` 的共享复述降到 `5/45`，但推荐泄漏仍有 `31/45`。fact-only 同时压低推荐和共享复述，并显著提高私有事实 exact count。

## Case Triage

clean subset 的 case-level 翻转支持上面的解释。

- Task `11` 和 `12`：禁推荐能从旧 exchange 的错误中恢复，禁共享复述不能恢复。
- Task `7` 和 `10`：禁共享复述能恢复，禁推荐不能恢复。
- Task `3` 和 `5`：两个局部禁令都不能恢复，fact-only 恢复。
- Task `5`：`fact_only_with_options_exchange` 仍错，`fact_only_exchange` 对，提示 possible-answer visibility 可能在少数任务上仍会诱发表述压缩或选项锚定。

这些 case 说明单一规则无法完全解释 Stage 1 的 fact-only 增益。当前更合理的诊断是：旧 sender context 同时诱发偏好压缩、共享优势重放、以及私有事实搬运不精确；fact-only surface 把这三件事一起压住了。

## 边界

这是 smoke12，只能决定是否值得 full65，不能给稳定率估计。clean subset 只有 `8` 个任务，且 message-audit 是自动 proxy；`no_shared_repeat_exchange` 的 shared-overtalk proxy 在个别任务上可能把私有事实和共享事实的词面重叠算进来，所以后续 full65 仍需要 case inspection。

Prompt 约束也可能过强。尤其 fact-only 条件更接近“强格式化信息搬运”，它证明了当前协议切口可工作，但还没有证明一个自然多智能体对话方法。

## 下一步

我建议跑 Stage 2 full65。理由是 smoke12 已经把三种因素拉开：局部禁令部分恢复，fact-only 仍然明显更强，fact-only-with-options 出现轻微掉点。full65 应该回答这些方向是否稳定，尤其是 clean subset 上 `fact_only_exchange` 相比 `no_recommendation_exchange` 和 `no_shared_repeat_exchange` 的剩余增益是否仍然大。

Full65 前不需要改条件。需要保留 corrected scoring、clean subset、message audit，并额外抽查：

- `fact_only_exchange` over `no_recommendation_exchange` 的 rescue cases；
- `fact_only_exchange` over `no_shared_repeat_exchange` 的 rescue cases；
- `fact_only_with_options_exchange` 掉点 cases；
- proxy 可疑的 shared-overtalk cases。
