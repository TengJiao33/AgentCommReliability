# HiddenBench V2 Stage 4 Sender Visibility Smoke12

## 核心判断

这轮 smoke 跑通了，而且给了一个值得继续压的信号：在 clean subset 上，旧 exchange 仍然很差，blind/minimal 和 fact-only 仍然很强。更细的 sender visibility matrix 暂时只抓到一个可解释分裂点，样本太小，结论等级只能是 diagnostic。

## 我们做了什么

这次运行的是 HiddenBench V2 Stage 4 sender visibility matrix。固定 final decision prompt 和 minimal sender 输出格式后，只改变 sender 能看到的上下文：只看 private observation、额外看 task、额外看 options、额外看 shared facts、以及 full visibility。运行路径是 `experiments/20260617-2125-a8002-hiddenbench-v2-stage4-sender-visibility-smoke12-qwen25-14b/`，远端路径是 `/data/xuhaoming/yfy/research_workspace/experiments/20260617-2125-a8002-hiddenbench-v2-stage4-sender-visibility-smoke12-qwen25-14b/`。

运行配置：A800_2，GPU 7，port 8053，Qwen2.5-14B-Instruct，temperature 0.0，12 个任务，10 个条件，总计 120 条 final records。`runner.stderr.log` 为空，records 数量完整，分析后 rescoring changes 为 0。完成后远端 runner、vLLM 进程和 8053 端口都清理干净。

## 发生了什么

全样本 12 题里，`blind_minimal_exchange` 是 9/12，`fact_only_exchange` 是 9/12，`exchange_then_decide` 是 2/12。`private_plus_task_minimal_exchange` 是 8/12，`private_plus_options_minimal_exchange`、`private_plus_shared_minimal_exchange`、`full_visibility_minimal_exchange` 都是 7/12。`full_info` 是 9/12，`oracle_public_facts` 是 8/12，所以不能直接拿全样本当机制证据。

更该看的 clean subset 是 `full_info` 和 `oracle_public_facts` 都正确的 8 个任务。在这 8 题里，`blind_minimal_exchange`、`fact_only_exchange`、`private_plus_task_minimal_exchange` 都是 8/8；`private_plus_options_minimal_exchange`、`private_plus_shared_minimal_exchange`、`full_visibility_minimal_exchange` 都是 7/8；旧 `exchange_then_decide` 是 2/8。

## 机制解释

最稳的信号仍然是输出 contract：旧 exchange 的 sender 很容易写 recommendation 和共享事实复述，message audit 中 recommendation leakage 是 41/45，shared overtalk 是 25/45；而 blind/minimal、fact-only 和 visibility-minimal 条件的 recommendation leakage 都是 0/45。这支持我们继续把问题压在“公共消息如何形成可整合事实状态”上。

这轮新增的 visibility 信号较弱，但有具体例子。在 `baker_2010` 里，gold 是 `Roberts`。`blind_minimal_exchange`、`fact_only_exchange`、`private_plus_task_minimal_exchange` 都选 `Roberts`；当 sender 额外看到 options、shared facts 或 full context 时，final 变成 `Jones`。case inspection 显示，shared/full visibility 下部分 sender 只保留 Stevens 或表面候选相关信息，final 又被 Jones 的 board/campaign/teaching 等共享优势吸走。这个例子提示：更多 sender context 可能诱发选择性压缩或候选锚定。

## 为什么还不能这么说

目前只有 12 题 smoke，clean subset 只有 8 题。visibility-minimal 条件之间真正分开的 clean case 只有 `baker_2010` 一个，所以不能说已经证明 sender visibility 本身会系统性伤害通信。更稳妥的判断是：这个 smoke 通过了 plumbing，并给 full65 一个明确压力点。

另一个 caveat 是 HiddenBench 的部分任务本身不稳定。`clean_info_unstable` 有 4 题，连 full-info 或 oracle-public-facts 控制都不能稳定答对，这些题不能用来解释 sender 机制。

## 下一步压力

下一步应该跑 full65 Stage 4，并强制输出 case atlas：所有 `blind_minimal_exchange` 与任一 visibility-minimal 条件不同的任务，都要抽 sender messages、final answer 和 message audit。只有 full65 里继续出现 `options/shared/full visibility` 低于 blind/private+task，sender-visibility hypothesis 才能升级。若 full65 里这些 minimal visibility 条件全部贴近 blind/minimal，主线应回到 output contract 和 fact-state admission。
