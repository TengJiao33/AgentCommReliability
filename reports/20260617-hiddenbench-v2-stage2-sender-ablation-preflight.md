# HiddenBench V2 Stage 2 Sender Ablation Preflight

## 核心判断

下一步最该压的是 Stage 1 增益的来源。Stage 1 已经显示 `fact_only_exchange` 在 clean subset 上达到 `55/55`，旧 `exchange_then_decide` 只有 `23/55`；但这个差异同时改变了推荐行为、共享信息复述、私有事实精确度、选项可见性。Stage 2 只回答拆因子问题，还不能直接升级成方法结论。

## 目的和实验单位

目的：判断 HiddenBench Stage 1 的提升主要来自禁止 sender 过早给推荐，还是来自更强的私有事实上报和公共状态清洁。

实验单位：

- HiddenBench task；
- 每个 condition 的最终回答记录；
- 每个 agent 的 public message，用于 message-audit proxy。

模型和环境：

- model: `Qwen2.5-14B-Instruct`;
- remote: `A800_2:/data/xuhaoming/yfy/research_workspace`;
- GPU: `7`;
- port: `8047`;
- temperature: `0`;
- max tokens: `320`;
- benchmark: `data/external/hiddenbench/benchmark.json`.

## 条件

| Condition | 作用 |
| --- | --- |
| `shared_only` | 检查共享信息诱导的默认错误强度。 |
| `full_info` | 检查任务在全信息下是否可由模型解决。 |
| `oracle_public_facts` | 检查所有隐藏事实公开后是否可由模型解决。 |
| `exchange_then_decide` | Stage 1 旧 exchange baseline。 |
| `no_recommendation_exchange` | 保留旧 sender context、共享信息、私有事实和选项列表，但禁止推荐、排序、比较、排除答案。 |
| `no_shared_repeat_exchange` | 保留推荐能力，但禁止复述共享信息或把共享信息作为推荐理由。 |
| `fact_only_with_options_exchange` | 使用 fact-only 私有事实报告规则，但显式展示 possible answers。 |
| `fact_only_exchange` | Stage 1 强条件：只报告私有事实，不展示共享信息和选项。 |
| `fact_only_constraint_decide` | 便宜的 continuity control；复用 fact-only messages，只换 final decider prompt。 |

## 主对照

第一主对照：`no_recommendation_exchange` vs `exchange_then_decide`。

如果它接近 `fact_only_exchange`，说明 Stage 1 的大部分增益来自 premature recommendation / preference compression。这个结果会把下一步推向更简单的 sender contract 和 recommendation-delay protocol。

第二主对照：`fact_only_exchange` vs `no_recommendation_exchange`。

如果 `fact_only_exchange` 仍明显更强，说明只禁推荐还不够，机制更可能包含私有事实精确上报、共享事实去噪、或选项不可见带来的表述差异。

## 次级对照

`no_shared_repeat_exchange` vs `exchange_then_decide`：检查共享事实复述和共享优势重放是否足以解释旧 exchange 失败。

`fact_only_exchange` vs `no_shared_repeat_exchange`：检查禁止共享复述之后，私有事实精确化还有多少增益。

`fact_only_exchange` vs `fact_only_with_options_exchange`：检查 possible-answer visibility 是否会诱发 sender 把事实压缩成偏好或排除。

`fact_only_constraint_decide` vs `fact_only_exchange`：确认 Stage 1 的 final-decider 结论没有被新 run 打翻。

## 成功、失败和转向条件

支持继续推进的信号：

- `no_recommendation_exchange` 大幅高于旧 exchange，且 message audit 的 recommendation leakage 明显下降；
- `fact_only_exchange` 相比 `no_recommendation_exchange` 还有剩余增益，并能被 private-fact overlap / shared-overtalk / option-mention proxies 解释；
- clean subset 上的方向和 raw 方向一致。

削弱当前机制切口的信号：

- 三个新 sender 条件都接近旧 exchange，说明 Stage 1 的 fact-only 强信号可能依赖更窄的 prompt 形式；
- 三个新 sender 条件都接近 `fact_only_exchange`，说明宽泛的 recommendation ban 已经足够，typed/admission/public-state 方向的新意会变弱；
- `full_info` 或 `oracle_public_facts` 在 smoke 中不稳，导致行为差异无法和信息可解性分开。

## 失效条件

- parser 或 final-answer extraction 出现 unparsed；
- clean-information controls 不稳，尤其 `full_info` 和 `oracle_public_facts` 同时错的任务过多；
- prompt 过度警告，直接把模型推成规则遵守测试，而不再是 communication failure 测试；
- condition order 或 repeated calls 造成任务间不公平；
- message-audit proxies 把合理提及选项误判为 recommendation leakage；
- 远端已有服务占用目标端口或 GPU，导致结果混入执行不稳定。

## 本地和远端准备状态

本地检查已过：

```text
python -m py_compile scripts/run_hiddenbench_communication_probe.py scripts/analyze_hiddenbench_records.py scripts/analyze_hiddenbench_subsets.py
python scripts/analyze_hiddenbench_subsets.py --records experiments/20260617-163732-a8002-hiddenbench-v2-stage1-full65-qwen25-14b/analysis_corrected/corrected_records.jsonl --out-dir experiments/20260617-163732-a8002-hiddenbench-v2-stage1-full65-qwen25-14b/analysis_subsets_script_check
```

subset analyzer 复现 Stage 1 clean subset：`full_info_and_oracle_public_facts_correct=55`，`fact_only_exchange` 相比旧 exchange 有 `32` 个 clean left-only rescue，`0` 个 clean right-only regression。

远端检查已过：

- Python 脚本远端 `py_compile` 通过；
- `scripts/run_hiddenbench_probe_a8002.sh` 远端 `bash -n` 通过；
- GPU7: `4 MiB used`, `81149 MiB free`, `0% util`;
- port `8047` 未占用；
- port `8012` 和 `8014` 已有监听，保持不动；
- `/data` 可用约 `1.4T`，`/mnt/quarkfs` 可用约 `4.4T`;
- 本地和远端四个脚本 SHA256 一致。

## 下一步命令

推荐先跑 smoke12，不直接 full65。

PowerShell 入口：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_hiddenbench_stage2_sender_ablation_a8002.ps1 -Limit 12 -IncludePrompts
```

只检查将要发到远端的脚本，不启动 GPU：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_hiddenbench_stage2_sender_ablation_a8002.ps1 -Limit 12 -IncludePrompts -DryRun
```

预期输出目录：

```text
/data/xuhaoming/yfy/research_workspace/experiments/<run-id>/
```

如果 smoke12 的 clean subset 和 message audit 能把三个因素分开，再跑 full65。full65 命令只改 `-Limit 65`，并关闭 prompts 以减少输出体积：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_hiddenbench_stage2_sender_ablation_a8002.ps1 -Limit 65
```
