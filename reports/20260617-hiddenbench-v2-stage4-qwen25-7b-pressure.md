# HiddenBench V2 Stage 4 Qwen2.5-7B Pressure

## 核心判断

7B 这轮是有效外部压力。它把 14B 的天花板降下来，但主方向没有变：旧式 helpful exchange 明显差，最小事实消息稳定得多。sender visibility 仍然只是弱信号。

## 为什么要跑 7B

14B full65 的 clean subset 里，`blind_minimal_exchange`、`fact_only_exchange`、`private_plus_task_minimal_exchange` 全部是 55/55，`full_visibility_minimal_exchange` 也有 54/55。这个结果支持 fact-state 方向，但也带来一个 caveat：模型可能太强，只要消息稍微干净，它就能把答案合出来。

7B 的目的就是压这个 caveat。我们想知道：换成更弱但仍可用的 instruction model 后，旧 exchange 的失败是否还存在，minimal fact-state 条件是否还稳。

## Smoke 结果

7B smoke12 没有崩。全样本中，`shared_only` 是 1/12，`full_info` 是 9/12，`oracle_public_facts` 是 8/12，旧 `exchange_then_decide` 是 3/12，`blind_minimal_exchange` 是 8/12，`fact_only_exchange` 是 7/12。

clean subset 有 8 题。旧 exchange 是 3/8；blind、fact-only 和 visibility-minimal 条件基本都在 7/8。这个 smoke 说明 7B 还能理解任务，也保留了旧 exchange 明显更差的方向，因此可以继续 full65。

## Full65 结果

7B full65 完整完成：650/650 records，stderr 为空，corrected rescoring changes 为 0，远端 vLLM 自动清理。

全样本里，`shared_only` 是 2/65，`full_info` 是 55/65，`oracle_public_facts` 是 51/65。这说明 benchmark 对 7B 仍有通信必要性压力，也说明 7B 控制没有塌掉。旧 `exchange_then_decide` 是 18/65，`blind_minimal_exchange` 和 `fact_only_exchange` 都是 51/65。

clean subset 有 50 题。这里的关键结果是：旧 exchange 只有 16/50；`blind_minimal_exchange`、`fact_only_exchange`、`private_plus_task_minimal_exchange`、`private_plus_options_minimal_exchange`、`private_plus_shared_minimal_exchange` 都是 47/50；`full_visibility_minimal_exchange` 是 46/50。

## 机制解释

7B 结果支持同一个机制：旧 exchange 的问题来自公共消息污染。旧 exchange 的 public messages 里有大量候选提及、共享信息复述和推荐倾向。全样本 audit 中，旧 exchange 的 recommendation leakage 是 104/253，shared overtalk 是 150/253，answer mentions 是 244/253。minimal 条件的 recommendation leakage 全部是 0。

case atlas 也支持这个判断。clean subset 里，blind 正确但旧 exchange 错的任务有 32 个。旧 exchange 在这些任务中累计出现 55 次 recommendation leakage、73 次 shared overtalk、115 次 answer mention，覆盖 124 条 public messages。

## 对 14B 结论的影响

7B 让 14B 结果更可信。14B 的 clean subset 中 minimal 条件太接近满分，容易被质疑为模型太强。7B 把 clean minimal 条件降到 47/50 左右，但旧 exchange 仍只有 16/50。这说明旧交流污染公共事实状态的现象不依赖 14B 天花板。

sender visibility 这条线继续降级。7B clean subset 中真正的 visibility split case 只有 1 个，和 14B 一样少。不同 visibility-minimal 条件高度聚集，说明“看了任务/候选/共享信息就坏”不是主要解释。

## 下一步

下一步应直接实现 `fact_state_admission`：sender 只能提交 typed local observations，禁止推荐、候选排序和全局判断；receiver 必须基于这些 observations 重新推导答案。这个协议需要同时在 7B 和 14B 上跑，和旧 exchange、blind minimal、full-visibility minimal 对比。

成功标准应设为：在 7B 这种较弱模型上仍能明显压过旧 exchange，同时 message audit 显示推荐泄漏、共享复述和候选锚定被控制住。
