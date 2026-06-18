# HiddenBench V2 Stage 4 Sender Visibility Full65

## 核心判断

这轮 full65 把主线推清楚了：最强证据指向 public-message output contract，也就是公共消息应该被约束成可整合的事实状态。sender visibility hiding 还有一个活例子，但整体效果很弱，不能作为主机制。

## 我们做了什么

这轮实验固定 HiddenBench 任务、模型和 final decision prompt，比较 10 个条件：`shared_only`、`full_info`、`oracle_public_facts`、旧 `exchange_then_decide`、`blind_minimal_exchange`、`fact_only_exchange`，以及四个 visibility-minimal 条件。运行路径是 `experiments/20260617-2159-a8002-hiddenbench-v2-stage4-sender-visibility-full65-qwen25-14b/`。

运行配置：A800_2，GPU 7，port 8053，Qwen2.5-14B-Instruct，temperature 0.0，65 个任务，10 个条件，总计 650 条 records。`runner.stderr.log` 为空，corrected rescoring changes 为 0。完成后远端 runner、vLLM 和 8053 端口都已清理，GPU 7 回到 4 MiB、0% utilization。

## 发生了什么

全样本上，`shared_only` 是 1/65，`full_info` 是 59/65，`oracle_public_facts` 是 56/65。这说明 HiddenBench 在这组任务上确实提供了通信必要性压力：没有私有信息几乎答不对，公开所有事实后大多数题可解。

旧 `exchange_then_decide` 是 24/65，明显低于 `blind_minimal_exchange` 和 `fact_only_exchange` 的 57/65。message audit 也很一致：旧 exchange 的 recommendation leakage 是 225/253，shared overtalk 是 134/253；而 blind/fact-only/visibility-minimal 条件的 recommendation leakage 都是 0/253，shared overtalk 都只有 4/253。

最关键的是 clean subset。`full_info` 和 `oracle_public_facts` 都正确的 55 个任务里，`blind_minimal_exchange`、`fact_only_exchange`、`private_plus_task_minimal_exchange` 全部是 55/55；`private_plus_options_minimal_exchange`、`private_plus_shared_minimal_exchange`、`full_visibility_minimal_exchange` 是 54/55；旧 `exchange_then_decide` 是 23/55。

## 机制解释

这轮结果说明，旧 exchange 的失败主要来自公共消息形态。sender 在 helpful exchange 里会把局部事实加工成候选推荐、共享信息复述、表面优势摘要，final receiver 接收到的已经不是干净事实状态。clean subset 里有 32 个任务满足旧 exchange 错、blind/minimal 对；这些任务的旧 exchange 消息合计出现 113 次 recommendation leakage、59 次 shared overtalk、120 次 answer mention，覆盖 125 条 public messages。

visibility hiding 的解释被削弱。clean subset 里真正区分 visibility-minimal 条件的只有 `baker_2010` 一个样本：blind/fact/private+task 选 Roberts，options/shared/full visibility 掉到 Jones。这个样本仍然重要，因为它显示候选或共享上下文可能诱发 candidate anchoring；但 1/55 的规模不足以支撑一个主机制故事。

## 对 idea 的影响

目前最稳的 idea 应该叫 fact-state admission 或 public fact-state protocol：多 agent 通信不能只要求 agent “helpfully discuss”，而要约束 sender 先提交可审计的局部观察，receiver 再从这些事实重新推导。这个故事比单纯隐藏 sender 上下文更可靠，因为 full-visibility minimal 也能在 clean subset 做到 54/55。

论文味道来自这里：通信失败不只是信息不足，也不是模型单体推理差；在完整信息可解、共享信息不可解的任务里，错误来自公共消息生成阶段把私有事实转写成了带候选偏见的公共状态。我们的机制设计应当直接控制这一步。

## 边界

HiddenBench runner 是本地协议，不是官方多人交互 harness。message audit 是自动代理指标，具体机制仍要靠 case inspection 和下一轮协议 ablation。`clean_info_unstable` 有 10 个任务，full-info 或 oracle-public-facts 控制不稳，这些任务不应该用于机制判断。

还有一个重要边界：fact-only 和 blind-minimal 在 clean subset 已经到 55/55，天花板很高。下一轮不能只追求准确率提升，必须展示更一般的协议原则、跨模型复现，或者在更难的构造 benchmark 上保持优势。

## 下一步压力

下一步应做 `fact_state_admission` 协议：sender 只能提交 typed local observations，禁止推荐、排序、候选总结；receiver 必须把 observations 当作待整合事实，并显式 re-derive final answer。对照组保留旧 exchange、blind minimal、full-visibility minimal。成功标准应设为：在更多模型或更强干扰条件下稳定压住旧 exchange，同时保留可解释的 message audit。

同时要保留 `baker_2010` 作为 candidate anchoring case。它可以帮助我们设计更强压力：给 sender 可见 options/shared facts，但要求 fact-state admission，观察是否能消除 Jones anchoring。
