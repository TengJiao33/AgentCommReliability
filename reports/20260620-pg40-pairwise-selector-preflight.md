# PG40 Pairwise Selector 预飞行

## 核心判断

pairwise role-card selector 已经从想法推进成可跑入口。当前没有模型分数，但 full40 prompt、禁用字段审计、schema smoke 和 A800_2 包装脚本都已经就绪。

这个预飞行承接 no-scope 规则 selector 的负结果：手写 lexical / cost 规则 full40 model-only 是 `0/40`，utility 只有 `0.5243-0.5467`。下一步需要让模型逐对判断 role-card assignment，再用 deterministic budget prune 和 SSEAC compiler 读数。

## 做了什么

新增两个脚本。`scripts/run_pg40_pairwise_role_card_selector_openai_compatible.py` 构造 no-scope pairwise prompt，调用 OpenAI-compatible API，解析模型的 sparse assignments，并转成 SSEAC `candidate_units`。`scripts/run_pg40_pairwise_role_card_selector_a8002.sh` 是 A800_2 包装入口，会启动 vLLM、跑 selector、compile model-only / compiler 两路，并用 PG40 scorer 打分。

prompt 只给模型 `packet_id`、`roles`、`role_budgets`、`card_id`、`cost` 和 card text。它不给 `recipient_scope`、required slots、need sets、utility gold 或任何 target role 标注。

## 本地门禁

full40 dry-run prompt 已材料化到 `experiments/20260620-local-pg40-pairwise-selector-preflight/dry_run_prompts_full40.jsonl`。共有 `40` 行，角色数 `2-6`，卡片数 `7-13`，prompt 长度 `3570-9876` 字符。

禁用字段扫描是 `0/40` 命中。扫描词包括 `recipient_scope`、`required_slots`、`acceptable_card_ids`、`expected_final_decision`、`reference_need_sets`、`candidate_need_sets`、`role_utilities`、`needed_by`、`eligible_by`、`target_needed_by`、`utility_by_recipient`、`visibility_gold`、`source_scope_ledger`、`oracle`、`gold` 和 `distractor`。

schema smoke 已通过。一个不含金标信息的假 assignment 可以写成 SSEAC prediction，并通过 `compile_sseac_v0.py --mode model_only`、`compile_sseac_v0.py --mode compiler` 和 `score_sseac_pg40_compiled.py`。这只证明接口兼容，不提供行为证据。

## 失败和边界

本机 `bash -n` 超时，原因和此前本地 bash / WSL 初始化卡住一致。远程 GPU 前必须在 A800_2 上重新跑 `bash -n scripts/run_pg40_pairwise_role_card_selector_a8002.sh`。

这次还没有模型输出，所以不能把它写成 PG40 结果行。它只是把下一轮 GPU run 的门槛补齐。

## 后续更新

GPU7 五行真跑已完成，见 `reports/20260620-pg40-pairwise-selector-limit5.md` 和 `experiments/20260620-a8002-pg40-pairwise-selector-limit5-qwen25-14b/README.md`。结果是 model-only/compiler `0/5`、utility `0.0000`、parse clean；compiler 拦下 `14` 个 out-of-scope assignment，admitted units 为 `0`。

这说明当前 no-scope pairwise prompt 缺少 role/recipient 转换上下文。当前不扩 full40，下一步转为修任务接口或回到 PerspectiveGap official role-assignment arms。

## 下一步压力测试

下一步不跑当前 pairwise prompt 的 full40。更小压力点是设计 public recipient-context prompt，或使用 PerspectiveGap official scenario context 重新做 role assignment。
