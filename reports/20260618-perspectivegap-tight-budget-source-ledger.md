# PerspectiveGap tight-budget source-ledger 诊断

## 核心判断

这轮结果把问题往前推了一步：source-ledger 加预算编译确实能把“多发、错发、超预算”压成可行输出，但当前 tight-budget V0 还太浅。最危险的信号是 utility-density greedy 已经达到 `0.982` utility ratio 和 `25/40` strict，14B 新 prompt 加 compiler 只有 `0.846` utility ratio 和 `10/40` strict。

## 我们做了什么

我从 rotated source/scope packet 构造了一个紧预算版本：40 行，160 个 role，其中 134 个 role 的预算低于完整候选成本；平均预算比例是 `0.589`，每个 role 平均有 `3.375` 个候选源，oracle 在预算内平均只能选 `2.1125` 个。新的 scorer 同时保留 hard-routing strict 指标，并增加 `utility_ratio`、`raw_utility_ratio`、`exact_target_role_rate` 和 `budget_feasible_role_rate`。

## 本地基线说明了什么

oracle 满分，说明 gold 和 scorer 基本闭合。`eligible_all` 的 coverage 是 `1.000`，raw utility ratio 是 `1.444`，但 budget pass 是 `0.000`，feasible utility ratio 掉到 `0.100`，说明 scorer 没有把超预算乱发误判成好结果。

更关键的是简单启发式太强：`eligible_cheapest` 有 `14/40` strict、`0.893` utility ratio；`utility_density_greedy` 有 `25/40` strict、`0.982` utility ratio。这说明 V0 的 utility 设计主要在测“按性价比挑源”，复杂度还不够。

## 模型结果

旧 full-budget source-ledger 输出离线重编译到 tight-budget packet 后，7B 是 `2/40` strict、`0.603` utility ratio；14B 是 `11/40` strict、`0.871` utility ratio。这只算诊断，因为旧 prompt 没有告诉模型 tight-budget utility 目标。

我又跑了 Qwen2.5-14B 的 utility-aware source-ledger prompt。raw 输出 `0/40` strict，budget pass 只有 `0.025`，raw utility ratio 是 `1.205`，feasible utility ratio 只有 `0.147`。预算编译后变成 `10/40` strict，budget pass `1.000`，precision `0.919`，utility ratio `0.846`。

## 机制解释

这支持一个比较朴素但重要的机制判断：LLM 能读 source ledger，却很难稳定执行“按角色预算做取舍”的组合约束；把边界执行交给 deterministic compiler 能稳定修掉预算和错收件人问题。问题在于，这个 V0 benchmark 的 utility 形状太容易被贪心启发式解决，所以它还不能证明我们有一个足够深的多智能体通信机制。

## 对研究方向的影响

我的判断是，方向没有被证伪，但“source routing + budget compiler”单独撑不住 A 会故事。它现在更像一个工程上有效、研究上偏浅的组件。真正可能变有趣的位置要继续往后压：通信状态里的证据不只要分发给谁，还要处理稀缺带宽、依赖闭包、跨角色耦合、以及错误公共状态对私有证据价值的污染。

## 下一步压力测试

下一步不该扩大这个 V0。更好的动作是做 tight-budget V1：让 utility 不再被简单 density greedy 吃掉，引入 dependency closure 或 role-coupled constraints。目标应当放在区分三件事：读懂 source/scope、选择高价值证据、执行预算和依赖约束。只有这三件事分开后，source-ledger compiler 才可能从“直觉工程补丁”变成可讲的机制。
