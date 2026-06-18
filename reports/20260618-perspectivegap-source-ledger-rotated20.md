# PerspectiveGap Source Ledger Rotated20：结果判断

## 核心判断

这一步终于摸到了更有意思的机制形状。把同一批 fragment 文本的 recipient scope 旋转后，旧 role-list 预测几乎崩掉；给模型显式 source access ledger 后，14B 能把 coverage 拉到 `0.854`，并出现 `3/40` strict pass。说明 source/scope 状态确实能成为一个有效控制面。

但这还没有变成完整方法。source ledger 解决了“按内容猜路由”的问题，新的瓶颈变成 budgeted delivery：模型能读 ledger，却仍然倾向于多发，导致预算失败。

## 证据

本地 rotated20 packet 保持 fragment 文本不变，把非 reject fragment 的 recipient roles 旋转一位。oracle 是 `40/40` strict。旧 role-list 预测在 rotated gold 上明显崩：7B coverage `0.076`、precision `0.135`；14B coverage `0.150`、precision `0.197`。

source-ledger router 显著恢复。7B 达到 coverage `0.574`、precision `0.745`、reject_recall `1.000`，但 strict 仍是 `0/40`，budget_pass `0.350`。14B 达到 coverage `0.854`、precision `0.779`、reject_recall `1.000`，strict `3/40`，但 budget_pass 只有 `0.225`，mean budget_overrun `13.150`。

两次 source-ledger run 都是 `40/40` status ok，parse-error rows 都是 `0`。格式问题解释不了这个结果；失败主要来自预算过发和少量 extra delivery。

## 机制解释

这个结果把前面几轮拆清楚了。原始 PerspectiveGap role assignment 里，模型主要在靠内容语义猜“谁需要什么”。当 source/scope 被旋转，内容语义和通信状态冲突，旧预测立刻失效。

显式 ledger 让模型重新抓住通信状态，尤其 14B 恢复得很明显。这说明“source/scope 作为外部状态”比“让模型自己从文本推断 scope”更稳。可是模型仍然没有自然内化 budget：它知道谁该收，但经常把太多 source 一起发出去。

## 对 idea 的影响

这条线比单纯 multi-agent communication prompt 更像可讲的故事：LLM 能读内容，也能在显式 ledger 下跟随通信状态；但当通信状态同时带有 source/scope/budget 约束时，模型缺少稳定的执行层。

下一步的机制可以更明确：把 multi-agent communication 改写成“communication state control”问题。核心张力从“大家要不要说话”推进到“系统如何让模型可靠地操作 source、scope、budget、reject 这些通信状态”。

## 下一步

我建议继续做 budget-aware source ledger，暂停回到 general hard prompt：

1. 给 source ledger 增加 per-role remaining budget，并要求模型按 budget 排序截断。
2. 加一个 deterministic budget compiler：模型只给优先级，系统负责截断，比较 model-budget 和 compiler-budget。
3. 保留 rotated source/scope，让内容语义无法直接救场。

如果 compiler-budget 能把 14B 的 coverage 保在高位、同时把 budget_pass 拉上去，这就会变成一个像样的机制故事：模型负责识别通信状态，系统负责执行预算约束。
