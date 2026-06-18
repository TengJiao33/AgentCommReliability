# HiddenBench V2 Stage 3 Blind Sender Preflight

## 核心判断

这轮实验只检验一个反直觉候选：减少 sender 的任务可见信息，是否会提升团队最终决策。它要压力测试的说法是：在 hidden-profile 协作里，sender 知道任务和选项后会过早解释本地事实，降低公共消息质量。

## 实验目的

Purpose: 比较 helpful sender、fact-only sender、blind sender 在同一 HiddenBench task 上的最终决策表现。

Unit: HiddenBench task-level condition record。核心 paired unit 是同一 task 在不同 communication condition 下的 final decision。

Primary contrast:

- `blind_exchange` vs `exchange_then_decide`
- `blind_minimal_exchange` vs `exchange_then_decide`
- `fact_only_exchange` vs `blind_exchange`
- `fact_only_exchange` vs `blind_minimal_exchange`
- `blind_minimal_exchange` vs `blind_exchange`

Secondary controls:

- `shared_only`: no-private-information floor
- `full_info`: all-facts direct upper check
- `oracle_public_facts`: clean public private-fact upper check
- `fact_only_with_options_exchange`: fact-only with answer options visible to sender

## 条件定义

`exchange_then_decide` 是 helpful sender：sender 看任务、shared facts、private fact 和 possible answers，可以给 tentative recommendation。

`fact_only_exchange` 是 strict sender：sender 看任务和 private fact，不能推荐、排序、复述 shared facts 或推理。

`blind_exchange` 是 blind free-form sender：sender 只看一条 local observation，看不到任务、shared facts 或 possible answers，自由写短消息。

`blind_minimal_exchange` 是 blind minimal sender：可见信息同 `blind_exchange`，但必须用 `Local observation` 格式报告。

## 成功信号

强信号：在 clean subset 上，`blind_exchange` 或 `blind_minimal_exchange` 明显高于 `exchange_then_decide`，并接近 `fact_only_exchange`。

更强信号：`blind_exchange` 接近 `fact_only_exchange`，说明关键可能是 sender task visibility，而不只是强格式约束。

反直觉信号：`blind_exchange` 高于 `fact_only_with_options_exchange`，说明给 sender 更多任务信息会伤害通信。

## 失败信号

若 blind 条件只接近旧 `exchange_then_decide`，Blind Sender Hypothesis 降级。

若只有 `blind_minimal_exchange` 接近 fact-only，而 `blind_exchange` 仍低，机制更可能是格式约束或精确复制，不宜写成 task-visibility 效应。

若 `full_info` 或 `oracle_public_facts` 在 smoke 中不稳定，这轮只能算 plumbing/contact，不能解读 blind sender 机制。

## 无效条件

- parser 出现大量 unparsed；
- sender blind prompt 泄露 task、option 或 shared facts；
- runner 条件数量不成对；
- 远端 benchmark/data/scripts 与本地版本不同步；
- vLLM 服务提前退出或部分任务失败。

## 预期 artifacts

Smoke run:

- run id pattern: `*-a8002-hiddenbench-v2-stage3-blind-sender-smoke12-qwen25-14b`
- remote path: `/data/xuhaoming/yfy/research_workspace/experiments/<run-id>/`
- local mirror: `experiments/<run-id>/`
- corrected analysis: `experiments/<run-id>/analysis_corrected/`

Full run, only after smoke 通过:

- run id pattern: `*-a8002-hiddenbench-v2-stage3-blind-sender-full65-qwen25-14b`
- same artifact layout as smoke.
