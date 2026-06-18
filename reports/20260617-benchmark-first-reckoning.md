# 主线清算与 benchmark-first 重置

## 核心判断

旧的 authority / typecast 主线不能继续作为论文主故事推进。它在 MATH 和 TypeCastArena 上主要揭示了模型会受可见错误文本、final-answer surface、operator 片段、parser 和 prompt contract 影响；这些现象适合作为机制显微镜，不能支撑多智能体通信可靠性的主 claim。

现在应把主线重置为 benchmark-first：先让外部 benchmark 证明任务确实需要信息在 agent 之间移动，再讨论 public-state protocol、typed fact card、admission check 或 constraint merge 是否改善通信失败。没有通信必要性的任务，不能继续承担主证据。

## 清算对象

MATH authority genesis、epistemic type erasure、sender-receiver micro-protocol、operator lifecycle 等实验，保留为 operator-level invalid cast 诊断。它们的价值是暴露 receiver 如何继承错误 equation、numeric role、relation skeleton 或 final-answer artifact。它们的边界也很清楚：样本是人工或半人工选出的 re-answer packet，单模型、零温、case concentration 明显，任务本身没有证明 agent 间通信是必要条件。

TypeCastArena live receiver 线停止扩大。`315` 行和 repaired `117` 行都说明当前设计还不能隔离 lifecycle admission：baseline 不稳，content-visible inert control 与 target channels 出现同级失败，typed partial / typed rederive 仍能保留可复原错误答案的 operator state。继续扩大只会增加噪声。

PACT 旧的 saved-field / re-answer stress 结果不能当 benchmark 结果。PACT 方法本身是 protocol，不是 benchmark；能进入新主线的是 PACT-style split-evidence setting，例如 HotpotQA / 2Wiki 中每个 agent 只拿 partial evidence、最终答案依赖证据交换的设置。

早期 MAD-MM、DAR、MOC、MATH50/MMLU-Pro 小 sweep 都只保留为 reproduction contact 和背景经验。它们帮助我们看到通信、memory、retention 和 token cost 的坑，但没有形成可发表主问题。

## 证据链

TypeCastArena `315` 行 run 已经失败在控制门：`baseline_previous_solution` 只有 `16/35` 正确，paired authority violations 在 self、unrelated、inert、peer、workspace、verifier、quarantine、typed rederive 间接近同级。对应记录是 `reports/20260617-typecast-math200-inert-receiver315-qwen25-14b.md` 和 E-116。

Repaired `117` 行 run 仍没有把 lifecycle admission 分离出来：baseline 只有 `11/13` 正确；在这 `11` 个 baseline-correct cases 上，inert visible scratch、direct peer、shared workspace、verifier admitted 都是 `2/11`，typed rederive 是 `1/11`。这个结果只能算更清楚的 control-gate failure。对应记录是 `reports/20260617-typecast-repaired-controlstable117-qwen25-14b.md` 和 E-118。

MATH operator lifecycle v1 给了局部正信号，但它仍是显微镜信号。hard controls 稳定，typed partial 出现 `3/16` operator candidates，shared workspace 和 verifier admitted 各出现 `1/16` direct uptake；但五个 semantic failures 只来自 `math96` 和 `math121` 两个 cases。对应记录是 `reports/20260617-math-operator-lifecycle-v1-qwen25-14b.md`。

HiddenBench 给出更强外部压力：`shared_only` 只有 `1/65`，`oracle_public_facts` 是 `56/65`，`full_info` 是 `59/65`，而当前生成式 `exchange_then_decide` 只有 `24/65`。这个 gap 说明任务确实依赖 hidden information，也说明失败点在私有事实如何变成可靠 public state。对应记录是 `reports/20260617-hiddenbench-communication-necessity-qwen25-14b.md`。

TeamBench 是更硬的工程级通信必要 benchmark，但当前 A800_2 缺 Docker / Podman / Singularity / Apptainer，也没有免密 sudo；官方 OS-enforced role separation 结果暂时不可做。对应记录是 `reports/20260617-a8002-docker-feasibility.md`。

模型设置也需要清算。Qwen2.5-14B 适合 cheap diagnostic 和 packet debugging，但单独承载不了最终 claim。强结果至少需要一个 open stronger model 和一个 closed frontier model 的同方向检查。对应记录是 `reports/20260617-model-family-and-experiment-setting-gap.md`。

## 退役判定

退役的主 claim 是：仅凭 MATH / TypeCast re-answer pressure 证明多智能体通信中的 authority genesis 或 type erasure 是一个可发表主问题。当前证据支撑不到这个层级。

保留的诊断 handle 是：可见 communication object 可能被 receiver cast 成可继承 operator state，尤其是 equation surface、numeric role、relation skeleton 和 final-answer artifact。这个 handle 可以帮助解释未来 benchmark 上的失败 case，但它不能自己决定 benchmark 选择。

退役的实验动作是：继续扩展 MATH/TypeCast packet、继续为 inert/typed controls 打补丁、继续跑更多 Qwen2.5-14B re-answer variants。除非新 benchmark 暴露出明确相同机制，否则这些动作都不再优先。

## 新门槛

下一阶段任何主实验都必须先过 benchmark-first 门：

- benchmark 自身有信息不对称、角色隔离、partial observability 或通信必要性；
- 有 partial/no-comm、oracle-public-facts/full-info、protocol condition 之间的硬对照；
- gold 和 evaluator 足够明确，不能主要依赖选例解释；
- 不需要管理员权限，或明确标记为 blocked 而不伪装成可复现结果；
- 至少保留跨模型压力的路径，Qwen2.5-14B 只作为 debug backbone；
- 失败分析必须能回到 benchmark task，而不是回到我们手工构造的 artifact。

## 下一步压力

第一优先级是 HiddenBench protocol v2。它应比较 `shared_only`、`full_info`、`oracle_public_facts`、普通 exchange、fact-only exchange、typed fact card、constraint merge 和 admission check。若 typed fact / admission protocol 不能把 `exchange_then_decide` 拉近 oracle-public-facts，它应被退役或重写。

第二优先级是 PACT-style HotpotQA / 2Wiki split-evidence。它的使用方式必须是 benchmark setting，而不是旧的 saved-field re-answer stress。关键读数是 partial evidence 下是否需要交换 supporting facts，以及 public-state protocol 是否减少遗漏、污染或错误引用。

第三优先级是 SOTOPIA-TOM 或类似 private facts / channel policy benchmark 的小规模 contact。它适合测试谁知道什么、该公开还是私聊、哪些信息不能泄露，但要先确认本地可运行性和 judge 风险。

TeamBench 保留为管理员权限到位后的 P0 工程压力。当前只能读代码、跑 mock 或记录 feasibility，不能报告官方隔离结果。

## 一句话结论

旧主线已经清算：它留下一个机制词汇表，但不再指挥实验。新主线从外部 benchmark 开始，让通信必要性、角色隔离和信息公开失败先成立，再决定协议或方法是否值得写。
