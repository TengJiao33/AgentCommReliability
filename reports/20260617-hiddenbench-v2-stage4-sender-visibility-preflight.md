# HiddenBench V2 Stage 4 Sender Visibility Matrix Preflight

## 核心判断

这轮实验要杀的假设很具体：HiddenBench 里 blind/minimal sender 的强结果，究竟来自减少 sender 任务可见信息，还是来自严格最小格式带来的私有事实复制。

如果同样使用最小 `Local observation` 输出格式时，额外给 sender 任务、选项、共享信息或全部上下文会让 clean subset 明显掉分，sender visibility hypothesis 才继续升级。若这些条件都接近 `blind_minimal_exchange`，blind result 应降级为格式和事实搬运结果。

## 实验目的

Purpose: 拆分 sender 端可见信息来源，判断哪类额外上下文会破坏公共事实状态。

Unit: HiddenBench task-level condition record。核心 paired unit 是同一 task 在不同 sender visibility condition 下的 final decision。

Primary contrast:

- `blind_minimal_exchange` vs `private_plus_task_minimal_exchange`
- `blind_minimal_exchange` vs `private_plus_options_minimal_exchange`
- `blind_minimal_exchange` vs `private_plus_shared_minimal_exchange`
- `blind_minimal_exchange` vs `full_visibility_minimal_exchange`
- `full_visibility_minimal_exchange` vs `exchange_then_decide`

Secondary controls:

- `shared_only`: no-private-information floor
- `full_info`: all-facts direct upper check
- `oracle_public_facts`: clean public private-fact upper check
- `fact_only_exchange`: previous strongest strict sender reference
- `exchange_then_decide`: old helpful sender failure reference

## 条件定义

`blind_minimal_exchange`: sender 只看 private observation，不看 task、shared facts、options，并用 `Local observation` 最小格式输出。

`private_plus_task_minimal_exchange`: sender 看 option-redacted task description 和 private observation，不看 shared facts 或具体 option names，并用同一最小格式输出。

`private_plus_options_minimal_exchange`: sender 看 possible answers 和 private observation，不看 task 或 shared facts，并用同一最小格式输出。

`private_plus_shared_minimal_exchange`: sender 看 shared facts 和 private observation，不看 task 或 options，并用同一最小格式输出。

`full_visibility_minimal_exchange`: sender 看 task、shared facts、options 和 private observation，但仍只能用最小格式输出。

`exchange_then_decide`: sender 看完整上下文并可写 helpful public message，包括 tentative recommendation。

`fact_only_exchange`: sender 看 task 和 private fact，但被要求只报告 private fact。它是历史 strongest reference；由于 HiddenBench raw description 本身常包含 options，这个条件不能当严格 no-options 控制。

## 成功信号

强成功信号：clean subset 上 `blind_minimal_exchange` 明显高于某个 visibility-minimal 条件，且该条件 message audit 出现 private overlap 下降、recommendation leakage 或 shared overtalk 上升。

机制定位：

- `private_plus_task_minimal_exchange` 掉分：task goal 会诱发过早解释。
- `private_plus_options_minimal_exchange` 掉分：answer option visibility 会诱发候选锚定。
- `private_plus_shared_minimal_exchange` 掉分：shared facts 会诱发共享优势复述或稀释私有事实。
- `full_visibility_minimal_exchange` 接近 blind，但 `exchange_then_decide` 仍低：主要问题是 sender 输出权限和 helpful recommendation。
- `full_visibility_minimal_exchange` 也低：可见上下文本身会破坏最小事实搬运。

## 失败信号

若所有 visibility-minimal 条件都接近 `blind_minimal_exchange` 和 `fact_only_exchange`，则 Stage 3 的 strong result 更像最小格式和私有事实搬运收益。

若只有 `exchange_then_decide` 低，visibility hypothesis 降级，下一步应研究 public-message output contract，而非 sender context hiding。

若 `full_info` 或 `oracle_public_facts` 在 smoke 中不稳定，整轮只算 contact，不能解释 sender visibility。

## 无效条件

- parser 出现大量 unparsed；
- 新 condition 未被 runner 接受或 paired analyzer 漏掉条件；
- sender minimal prompt 泄露不该出现的上下文到输出；
- `blind_minimal_exchange` 在 smoke 中无法复现 Stage 3 方向；
- 远端脚本版本和本地脚本版本不同步；
- vLLM 端口冲突、服务提前退出或部分任务失败。

## 预期 Artifacts

Smoke run:

- run id pattern: `*-a8002-hiddenbench-v2-stage4-sender-visibility-smoke12-qwen25-14b`
- remote path: `/data/xuhaoming/yfy/research_workspace/experiments/<run-id>/`
- local mirror: `experiments/<run-id>/`
- corrected analysis: `experiments/<run-id>/analysis_corrected/`
- subset analysis: `experiments/<run-id>/analysis_subsets/`

Full run, only after smoke 通过:

- run id pattern: `*-a8002-hiddenbench-v2-stage4-sender-visibility-full65-qwen25-14b`
- same artifact layout as smoke.

## Launch Commands

Smoke:

```powershell
.\scripts\run_hiddenbench_stage4_sender_visibility_a8002.ps1 -Limit 12 -Port 8053
```

Full:

```powershell
.\scripts\run_hiddenbench_stage4_sender_visibility_a8002.ps1 -Limit 65 -Port 8053 -RunTimeout 24000
```

Dry run:

```powershell
.\scripts\run_hiddenbench_stage4_sender_visibility_a8002.ps1 -DryRun
```

## Claim Status

This experiment is diagnostic. It can promote or weaken the sender-visibility hypothesis, but it cannot by itself support a paper claim until a second split-evidence benchmark or another model repeats the direction.
