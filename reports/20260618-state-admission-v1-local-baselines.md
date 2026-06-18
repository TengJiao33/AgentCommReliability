# State Admission V1.1 本地基线压力

## 核心判断

V1.1 把问题从“按单条证据做预算选择”推进到了“证据要成组进入某个 role 的上下文，并且跨 role pair 组合受全局预算约束”。这一步有实际价值：V0 里 `utility_density_greedy` 已经接近 oracle；V1.1 里单片段全局贪心只剩 `0.041` utility ratio，bundle-level greedy 也只有 `0.449`。

这个结果还不能支撑方法 claim。它目前证明的是 benchmark 形状更锋利，同时也暴露出一个边界：能直接读取 group utility 的 `group_density_global` 仍然很强，达到 `32/40` strict 和 `0.967` utility ratio。所以这版更适合先问“LLM 能不能跟上简单符号 admission planner”，暂时不适合讲复杂优化算法。

## 设计

V1.1 复用 rotated PerspectiveGap tight-budget packet 里的 source/scope 扰动和候选片段，然后额外加了四层结构：

1. 每个 role 有一个 evidence bundle，bundle 内片段必须一起准入才有 utility。
2. 每个片段还有 standalone hint score，制造“单片段看起来很有用”的诱饵。
3. 每行有 global budget，oracle 需要选择哪些 role group 值得服务。
4. Pair-group utility 加入 density-trap decoy：某些 pair 的局部性价比更高，但会挡住更高总价值的 target pair。

输出仍然是同一个 hard-routing JSON 形状：每个 role 接收若干 cards，card 包含 `fragment_id`、`source_id`、`visibility`。新的 scorer 在旧 strict/coverage/precision/budget/source/visibility 指标外，增加 `utility_ratio`、`global_budget_pass`、`closure_violations` 和 `completed_role_rate`。

sanity audit 显示，`32/40` 行使用 pair-group oracle；剩下 `8/40` 个 2-role 行因为全局预算放不下整组，回退成单 role oracle。当前 packet 里有 `32` 个 target pair 和 `127` 个 overlap decoy pair。因此 V1.1 是混合压力：3 到 6 role 行主要测 pair-group coupling，2 role 行主要测 bundle closure 和全局稀缺。

## 结果

| Condition | Strict | Coverage | Precision | Utility ratio | Global budget pass | Closure violations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| oracle | 40/40 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| eligible_all | 0/40 | 1.000 | 0.302 | 0.000 | 0.000 | 0.000 |
| item_density_per_role | 0/40 | 0.816 | 0.383 | 0.000 | 0.000 | 1.150 |
| item_density_global | 0/40 | 0.564 | 0.327 | 0.041 | 1.000 | 2.000 |
| bundle_density_global | 14/40 | 0.509 | 0.374 | 0.449 | 1.000 | 0.000 |
| cheapest_bundle_global | 14/40 | 0.485 | 0.350 | 0.424 | 1.000 | 0.000 |
| group_density_global | 32/40 | 0.902 | 1.000 | 0.967 | 1.000 | 0.000 |

关键对比是 V0 到 V1.1 的变化。V0 里 `utility_density_greedy` 有 `25/40` strict 和 `0.982` utility ratio；V1.1 里 `bundle_density_global` 只有 `14/40` strict 和 `0.449` utility ratio。这个变化说明 V1.1 已经开始摆脱简单背包题。

## 机制解释

单片段贪心失败得很彻底，因为它会优先拿 standalone hint 高的片段，但这些片段无法单独释放 bundle utility。它在全局预算约束下可行，utility 仍然只有 `0.041`，说明问题已经从“别超预算”推进到“要完整满足一个 role 的证据依赖”。

bundle 贪心还有 `0.45` 左右 utility，说明它理解 bundle 后能吃到一部分结构。但它仍然无法处理 pair-group 的组合取舍：它会局部选择看起来性价比高的 bundle，错过更高价值的跨 role 组合。这贴近我们想要的 admission 故事：准入层要控制证据集合进入哪些 agent，并在系统预算下形成有效局部上下文。

`group_density_global` 很强，说明只要把 group utility 显式交给一个符号贪心 planner，许多行已经能解。这让故事更清楚：下一轮 LLM smoke 的意义在于观察模型面对同样显式 schema 时，会不会出现结构化准入失败；它暂时不承担算法难度证明。

## 边界

这个 V1.1 是合成压力，距离自然 benchmark 还有距离。bundle、standalone hint、density-trap group utility 都是 builder 加进去的结构，因此它只说明“可以构造出更像研究问题的压力形状”。它还没有证明真实多 agent 任务存在同样结构，也没有证明 LLM 会在这个结构上失败。

当前也没有模型输出。我们只跑了 deterministic baselines。下一步必须先做 packet audit，看具体行能否被人理解、目标是否自然、诱饵是否太刻意。通过后再跑小模型 smoke。

## Prompt Audit

我加了 `scripts/run_state_admission_v1_openai_compatible.py`，它可以把模型输出的 role-to-source 列表编译成 scorer 需要的 hard-routing cards。先用 dry-run 物化了 5 条分层 prompt，覆盖 2 到 6 role。

prompt 长度在 `5611` 到 `15065` chars 之间。每条 prompt 都显式给出 role budgets、global budget、role bundles、pair groups、source eligibility、standalone hints 和 payload previews；prompt 文件只带审计 metadata，正文没有给模型 `oracle_roles`、`oracle_groups` 或 target recipients。这个长度应该还能进 8k token 级上下文，但 6-role 行已经不算短，GPU smoke 需要限制 `max_model_len` 和 `max_tokens` 时留意。

我也加了 `scripts/run_state_admission_v1_a8002.sh`，默认用 Qwen2.5-14B 跑同一组 stratified5，`MAX_MODEL_LEN=16384`、`MAX_TOKENS=1536`。本地做过 `py_compile` 和 `bash -n` 静态检查；还没有实际启动 GPU。

## 下一步

下一步我会先写一个 strict JSON prompt，让 7B/14B 各跑一个小 smoke。判断标准很直接：如果模型完全读不懂 bundle/group schema，问题在 benchmark 表达；如果能读懂但系统性输给 `group_density_global` 或 exact oracle，才有继续讲 model-vs-symbolic admission 的空间。

## Artifacts

- Packet and run record: `experiments/20260618-local-state-admission-v1/README.md`
- Builder: `scripts/build_state_admission_v1_packet.py`
- Baselines: `scripts/generate_state_admission_v1_baselines.py`
- Scorer: `scripts/score_state_admission_v1.py`
- Runner/prompt builder: `scripts/run_state_admission_v1_openai_compatible.py`
- A800 launch wrapper: `scripts/run_state_admission_v1_a8002.sh`
- Packet: `experiments/20260618-local-state-admission-v1/state_admission_v1_rotated20.jsonl`
- Summaries: `experiments/20260618-local-state-admission-v1/summary_<baseline>.md`
- Prompt audit: `experiments/20260618-local-state-admission-v1/prompt_audit_stratified5.jsonl`
