# PerspectiveGap Budget-Compiled Source Ledger：结果判断

## 核心判断

这一步把 source-ledger 线推进成一个可工作的 protocol 雏形：模型负责读 ledger 和给 source 顺序，系统 compiler 负责 recipient validation、reject、source/scope 填充和预算执行。14B 在 rotated20 上从 raw source-ledger 的 `3/40` strict 提升到 `12/40`，coverage 保持 `0.854`，precision、budget_pass、reject_recall 都到 `1.000`。

这说明我们终于有了一个像样的机制切口：模型可以识别通信状态，但执行边界和预算更适合交给确定性系统层。

## 证据

7B raw source-ledger 是 coverage `0.574`、precision `0.745`、budget_pass `0.350`、reject_recall `1.000`。budget compiler 后 coverage 保持 `0.574`，precision 到 `1.000`，budget_pass 到 `1.000`，leak 到 `0.000`，visibility_accuracy 从 `0.700` 到 `0.819`。

14B raw source-ledger 是 strict `3/40`、coverage `0.854`、precision `0.779`、budget_pass `0.225`、mean budget_overrun `13.150`。budget compiler 后 strict 到 `12/40`，coverage 仍是 `0.854`，precision `1.000`，budget_pass `1.000`，budget_overrun `0.000`，visibility_accuracy 到 `0.952`。

compiler 诊断显示，7B 跳过 `106` 个 wrong-recipient source 和 `13` 个重复项；14B 跳过 `131` 个 wrong-recipient source 和 `1` 个重复项。没有 over-budget valid source 被跳过。

## 机制解释

前几轮的问题现在拆成三层了。第一层，内容语义会误导路由；rotated scope 让旧 role-list coverage 掉到 `0.076/0.150`。第二层，显式 ledger 能恢复 source/scope 跟随；14B raw source-ledger coverage 到 `0.854`。第三层，模型自己执行边界会多发；compiler 过滤 wrong-recipient 和重复项后，预算和 precision 直接恢复。

这个结果把 paper story 往“communication state control”推了一步。重点从“让 agent 多交流或少交流”推进到“把 source、scope、budget、reject 分成模型可读状态和系统可执行约束”。

## Caveat

当前 compiler 还没有证明 tight-budget priority。因为 rotated20 的每个 role budget 等于所有 gold needed source 的总成本，compiler 的收益主要来自过滤 wrong-recipient extra，而非在 gold source 之间做艰难取舍。

所以这一步支持“确定性执行层有价值”，还没支持“模型能在稀缺预算下给出最优优先级”。

## 下一步

下一步要做 tight-budget source ledger：把每个 role 的预算压到 gold cost 的一部分，让 oracle 也必须选子集。然后比较三种条件：

1. model-only source-ledger；
2. model priority + deterministic budget compiler；
3. oracle priority + deterministic budget compiler。

如果 14B 在 model priority + compiler 下接近 oracle priority，这条线就有机会从 benchmark trick 变成方法故事。
