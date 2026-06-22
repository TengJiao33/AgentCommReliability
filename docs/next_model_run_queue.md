# 下一批模型真跑队列

Snapshot date: `2026-06-20`.

## 核心判断

当前已经从“内部机制开发”切到“对外报告准备”。如果目标是 A 会论文，P0 队列必须回到同一模型、同一预算的公开基准比较；PerspectiveGap official full-grid route 已经补出 Qwen2.5-14B direct baseline：combined strict `2/440`。`PG40 tight-budget` 已完成 true prompt、card-unit、role-plan 三轮 limit5，结果显示 compiler 能修预算，card-level unit 能改善 coverage 和 utility，但解释型 role-plan contract 没有继续改善。2026-06-20 的 scope-projection rerank 预检显示，若能使用 PG40 `recipient_scope`，五行可到 `5/5`，full40 旧 source-ledger 14B 可到 `17/40`、utility `0.8845`。同日 no-scope 规则 selector 预检是负结果：full40 model-only `0/40`、utility `0.5243-0.5467`。随后 GPU7 五行 pairwise role-card selector 也为负：parse clean，model-only/compiler 都是 `0/5`、utility `0.0000`，compiler 拦下 `14` 个 out-of-scope assignment。下一步不扩 pairwise full40，先修 role/recipient interface 或转回 official role-assignment arms。

P0 的目标是判断一个不读 gold 的 system route 能否在同模型表中超过 direct prompt、source-ledger、transparent heuristic 和 oracle/control gap 所定义的 baseline ladder。公开 leaderboard 当前 `273/440` combined pass target 只作为 frontier ceiling 记录；近期目标集中在 PG40 / PerspectiveGap 公开切片，先把公开主表补齐，再谈方法优势。

## P0：论文主表公平比较队列

| 项 | 内容 |
| --- | --- |
| primary comparison | same backbone / same budget / same released grid or same public slice |
| official grid | `110` scenarios x seeds `1,42` x tasks `role_assignment,prompt_writing` = `440` requests |
| 公开参考 | `openai/gpt-5.5`：`273/440` combined，仅作为 frontier ceiling / optional leaderboard target |
| official repo | `baselines/PerspectiveGap/upstream`, commit `60b1dcaaeeb40619075f6cd8779c47fa4b344391` |
| 官方测试 | local venv 重跑 `18 passed` |
| 新组件 | `scripts/perspectivegap_assignment_to_prompt_predictions.py` |
| ensemble 组件 | `scripts/perspectivegap_ensemble_role_assignments.py` |
| PAL 式 ablation | `scripts/compile_sseac_v0.py --mode model_only|compiler`，队列同时产出 `structured_no_compiler` 与 `compiled` |
| 本地 smoke | oracle role assignment -> deterministic prompt writing = `220/220` prompt-writing strict |
| full-grid direct baseline | `20260619-a8002-perspectivegap-official-fullgrid-direct-qwen25-14b`: combined `2/440` |
| full-grid direct role-to-prompt control | direct role assignment deterministic prompt writer: combined `0/440` |
| ensemble smoke | 7B/14B union coverage `0.6648` 但 strict `0/40`; intersection precision `0.9680` 但 strict `0/40` |
| 禁区 | prediction-time 不读 `reference_need_sets`、SSEAC `required_slots`、PG40 `recipient_scope` 或任何 derived oracle fields |

### P0A：同一模型服务 direct baseline

状态：已完成 full grid。Qwen2.5-14B official runner direct baseline 是 `2/440` combined strict，role assignment `0/220`，prompt writing `2/220`。

复现入口：

```powershell
cd baselines\PerspectiveGap\upstream
$env:OPENAI_API_KEY='<key-or-empty-compatible-key>'
$env:PYTHONPATH='src'
python scripts\run_model_predictions.py `
  --provider openai-compatible `
  --base-url <base-url> `
  --api-key-env OPENAI_API_KEY `
  --model <served-model-name> `
  --shuffle-seed 1 `
  --shuffle-seed 42 `
  --tasks both `
  --out D:\develop\AgentCommReliability\experiments\<run-id>\predictions_direct.jsonl
python scripts\score_predictions.py `
  --predictions D:\develop\AgentCommReliability\experiments\<run-id>\predictions_direct.jsonl `
  --out D:\develop\AgentCommReliability\experiments\<run-id>\scores_direct.jsonl
```

当前记录：

```text
experiments/20260619-a8002-perspectivegap-official-fullgrid-direct-qwen25-14b/
reports/20260619-perspectivegap-official-fullgrid-direct-baseline.md
```

### P0B：assignment-to-prompt system route

先生成更强的 role-assignment predictions，再转 prompt-writing rows。已验证 direct role assignment 直接转 prompt-writing 不能救结果：`0/440`，所以 P0B 的核心在 no-gold role assignment route，writer 不是主要瓶颈。

```powershell
python D:\develop\AgentCommReliability\scripts\perspectivegap_assignment_to_prompt_predictions.py `
  --assignments D:\develop\AgentCommReliability\experiments\<run-id>\predictions_role_assignment_system.jsonl `
  --out D:\develop\AgentCommReliability\experiments\<run-id>\predictions_prompt_from_assignment.jsonl
```

然后把 role-assignment rows 和 prompt-writing rows 拼成配对 rows，用官方 scorer 计分。若后续要走 optional leaderboard route，full grid 需要补齐到 `440` rows；若 prompt-writing 完全由 assignment 派生，role-assignment strict 需要超过 `137/220` 才有机会单路超过 `273/440`。这个数字只是公开 ceiling 参考，当前论文主表不以它作为 gate。

已有 7B/14B no-gold union/intersection smoke 说明简单 set voting 不够。下一轮 system wrapper 应优先产生更多样的 role-assignment prompt arms，或使用强模型做 candidate generation，再用 no-gold validation/repair 只处理 JSON、role names、fragment ids 和 duplicated fragments。

### P0C：paper-facing baseline ladder

主表优先比较这些行：

| 行 | 作用 |
| --- | --- |
| official direct prompt | 同模型直接基线 |
| recall-heavy / precision-guarded prompt arms | prompt surface control |
| source-ledger / role-list route | 机制前身 |
| deterministic assignment-to-prompt writer | 把 prompt-writing 从自由生成中分离 |
| no-gold repair / ensemble router | system decomposition ablation |
| transparent heuristic / oracle | 强 baseline 和上界 |
| SSEAC-style route | 当前 Ours 候选 |

扩 full grid 的门槛是同模型 pilot 里出现可解释增益，并且增益没有来自泄漏、oracle-derived field 或 scorer artifact。

## P1：SSEAC 方法开发队列

远程运行默认使用 GPU 7。GPU 0 到 6 尽量不用；如果 GPU 7 忙，先暂停并汇报。

## 一键队列入口

通用脚本：

```powershell
scripts\run_sseac_smoke_queue_openai_compatible.ps1
```

先 dry-run 看命令队列：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_sseac_smoke_queue_openai_compatible.ps1 -BaseUrl http://127.0.0.1:8000/v1 -Model <served-model-name> -RunId <run-id> -DryRun
```

如果已经有通用模型服务地址，可以真跑：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_sseac_smoke_queue_openai_compatible.ps1 -BaseUrl <openai-compatible-base-url> -Model <served-model-name> -RunId <run-id>
```

可单独跑：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_sseac_smoke_queue_openai_compatible.ps1 -Scope PG40 -BaseUrl <openai-compatible-base-url> -Model <served-model-name> -RunId <run-id>
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_sseac_smoke_queue_openai_compatible.ps1 -Scope HSA -BaseUrl <openai-compatible-base-url> -Model <served-model-name> -RunId <run-id>
```

项目惯用的 A800_2 小样本入口：

```bash
cd /data/xuhaoming/yfy/research_workspace
GPU_ID=7 bash scripts/run_sseac_v0_pg40_a8002.sh
PROMPT_CONTRACT=constraint_recall GPU_ID=7 LIMIT=0 PACKET=/data/xuhaoming/yfy/research_workspace/experiments/20260619-local-hsa-v0-p0p1-seed-expansion33-draft/packet/hsa_v0_packet.jsonl bash scripts/run_hsa_v0_sseac_a8002.sh
```

默认输出目录：

```text
experiments\<run-id>\pg40\
experiments\<run-id>\hsa_v0\
```

每个 scope 会产出两条 paper-facing ablation 路径：

| Artifact | Condition | 用途 |
| --- | --- | --- |
| `structured_no_compiler_limit<N>.jsonl` | `structured_no_compiler` | 模型直接写 admission state，compiler/gate 只做诊断。 |
| `compiled_limit<N>.jsonl` | `ours_sseac_v0` | 模型提 candidate units，deterministic compiler 执行 hard constraints 和 sufficiency gate。 |
| `scores_structured_no_compiler_limit<N>.jsonl` | no-compiler score | PAL 式去 executor 对照。 |
| `scores_limit<N>.jsonl` | compiled score | 主方法候选行。 |
| `paired_delta_limit<N>.json/md` | compiled - no-compiler | 跑后主读数，直接服务论文表。 |

读数时必须做 paired delta：`compiled - structured_no_compiler`。最终 strict 只是一列，优先同时看 budget pass、leakage、extra final cards、forced commitment、slot recall、utility 和 admitted-card/cost 指标。

## 队列 1：PG40 true SSEAC prompt

| 项 | 内容 |
| --- | --- |
| packet | `experiments/20260618-local-sseac-v0-pg40-adapter/sseac_pg40_packet.jsonl` |
| 当前状态 | role-plan limit5 已完成并退休；scope-projection rerank 本地预检已完成；no-scope 规则 selector 已负；pairwise selector 五行已负 |
| 当前最好运行 | `experiments/20260619-a8002-sseac-v0-pg40-limit5-cardunit-qwen25-14b/` |
| 当前最好读数 | compiled `1/5`，coverage `0.6667`，budget pass `1.0000`，utility `0.8155` |
| 最新诊断运行 | `experiments/20260619-a8002-sseac-v0-pg40-limit5-roleplan-qwen25-14b/` |
| 最新诊断读数 | compiled `1/5`，coverage `0.6667`，budget pass `1.0000`，utility `0.7811` |
| 最新本地后处理 | `experiments/20260620-local-pg40-scope-rerank-preflight/` |
| 后处理读数 | card-unit 五行 scope-project `5/5`；full40 source-ledger 14B scope-project `17/40`，utility `0.8845` |
| 最新 no-scope 规则预检 | `experiments/20260620-local-pg40-no-scope-role-affinity-preflight/` |
| no-scope 规则读数 | hybrid model-only `0/40`、utility `0.5243`；cost model-only `0/40`、utility `0.5467`；hybrid + compiler `1/40`、utility `0.5243` |
| pairwise selector 预飞行 | `experiments/20260620-local-pg40-pairwise-selector-preflight/` |
| pairwise selector 真跑 | `experiments/20260620-a8002-pg40-pairwise-selector-limit5-qwen25-14b/` |
| pairwise selector 读数 | model-only/compiler `0/5`，utility `0.0000`；parse ok `5/5`；prompt leak `0`；raw assignments `22`；compiler prevented out-of-scope `14`；admitted units `0` |
| direct baseline | `experiments/20260619-a8002-pg40-direct-routing-limit5-qwen25-14b/`；strict `0/5`，utility `0.0987` |
| 复跑规模 | 下一轮 pairwise selector 先跑同 5 行 |
| runner | `scripts/run_sseac_v0_pg40_openai_compatible.py` |
| direct runner | `scripts/run_pg40_direct_routing_openai_compatible.py` |
| pairwise runner | `scripts/run_pg40_pairwise_role_card_selector_openai_compatible.py` |
| pairwise A800_2 wrapper | `scripts/run_pg40_pairwise_role_card_selector_a8002.sh` |
| compiler | `scripts/compile_sseac_v0.py` |
| scorer | `scripts/score_sseac_pg40_compiled.py` |
| 当前强 baseline | `utility_density_greedy`：`25/40` strict，utility `0.9825` |
| 旧模型参考 | source-ledger 14B compiled：`11/40` strict，utility `0.8707` |
| PAL ablation | `structured_no_compiler_limit5` vs `compiled_limit5` |

### 读数

pairwise selector 五行复现入口：

```bash
cd /data/xuhaoming/yfy/research_workspace
GPU_ID=7 PORT=<free-port> RUN_ID=20260620-a8002-pg40-pairwise-selector-limit5-qwen25-14b LIMIT=5 GPU_MEMORY_UTILIZATION=0.75 MAX_MODEL_LEN=8192 MAX_TOKENS=3072 bash scripts/run_pg40_pairwise_role_card_selector_a8002.sh
```

| 指标 | 用途 |
| --- | --- |
| schema compile rate | 判断模型能否按 SSEAC contract 输出 |
| strict | 判断 exact slot / budget / answer 是否同时满足 |
| coverage | 看是否漏掉必要 evidence |
| precision | 看是否乱收 source card |
| budget pass | 检查是否还在重复旧 source-ledger 的过预算失败 |
| utility | 对齐 PG40 tight-budget 主压力 |
| exact role | 判断 source role 是否被模型真正用上 |
| paired delta | 判断 compiler 是否带来 PAL 式方法增量 |

### 下一步动作

| 条件 | 动作 |
| --- | --- |
| role-plan contract 已低于 card-unit | 退休该提示契约 |
| direct routing 基线 | 已完成；不扩 direct |
| 若继续 PG40 | 先修 role/recipient interface；当前 pairwise prompt 不扩 full40 |
| 新 public recipient-context prompt 五行超过 `1/5` 且 utility 超过 `0.8155` | 再考虑扩到 `20` 行 |
| strict 或 utility 明显靠近 `utility_density_greedy` | 开始写主表 model row |
| 新接口仍低于 card-unit 或 source-ledger 14B compiled | PG40 继续作为失败分析和强压力表 |

## 队列 2：HSA-v0 true SSEAC prompt

| 项 | 内容 |
| --- | --- |
| packet | `experiments/20260619-local-hsa-v0-p0p1p2-seed-expansion36-draft/packet/hsa_v0_packet.jsonl` |
| 默认规模 | `--limit 3` |
| runner | `scripts/run_hsa_v0_sseac_openai_compatible.py` |
| compiler | `scripts/compile_sseac_v0.py` |
| scorer | `scripts/score_hsa_v0_compiled.py` |
| lower bound | shared-only verified p0p1p2_36：`24/36` strict，base strict `0/12` |
| over-admission 对照 | all-scoped verified p0p1p2_36：`36/36` strict，extra final cards `195` |
| baseline model row | compiler `7/9`，base strict `1/3`，extra final cards `8` |
| current best prompt-only extended row | constraint_recall compiler `14/15`，base strict `4/5`，extra final cards `10` |
| current best diagnostic row | constraint_support_completion p0p1p2_36 compiler `36/36`，base strict `12/12`，perturb strict `24/24`，extra final cards `42` |
| current next action | 暂停扩包；公开基准主表优先 |
| PAL ablation | `structured_no_compiler_limit3` vs `compiled_limit3` |

### 读数

| 指标 | 用途 |
| --- | --- |
| strict | 最终答案是否对 |
| base strict | 通信是否帮助 base rows |
| perturb strict | 是否能保持 insufficient-evidence |
| slot recall | 是否找到了必要 evidence slots |
| extra final cards | 是否出现全收 evidence 的投机策略 |
| forced commitment | 是否在证据不足时硬答 |
| paired delta | 判断 compiler/gate 是否减少全收、硬答或无效支撑 |

### 扩跑条件

| 结果 | 动作 |
| --- | --- |
| constraint_completion 已到 `9/9` 且 extra final cards `10` | 已完成；作为 9 行诊断上界 |
| HB12/HB31 draft 完成且 transparent controls 闭合 | 已完成；15 行包已生成 |
| 15 行 transparent controls 闭合 | 已完成 |
| 15 行 constraint_recall + completion | 已完成；补全后硬准入 `15/15`，extra final cards `10` |
| 33 行 P0/P1 transparent controls 闭合 | 已完成；理想准入 `33/33`，shared-only 基础行 `0/11`，all-scoped extra final cards `111` |
| 33 行 constraint_recall + completion | 已完成；补全后硬准入 `33/33`，extra final cards `37` |
| P2 长档案种子补齐并通过透明控制 | 已完成；理想准入 `36/36`，shared-only 基础行 `0/12`，all-scoped extra final cards `195` |
| 36 行 constraint_recall + blocker completion | 已完成；阻断补全后硬准入 `35/36`，extra final cards `40` |
| task 5 Roberts 支撑卡召回修复 | 已完成；支撑型窄补全后硬准入 `36/36`，extra final cards `42` |
| 支撑型窄补全在旧包复核干净 | 已完成；33 行保持 `33/33`，15 行保持 `15/15` |
| 支撑型窄补全方法组件文档 | 已完成；规则、禁区和升级门槛见 `docs/hsa_support_completion_method_component.md` |
| HSA 主表草稿完成 | 已完成；三十六行主表和论文骨架已接入支撑型窄补全 |
| 更大 HSA 派生包预飞行 | 已启动；候选筛选标准和第一批候选见 `docs/hsa_larger_derived_packet_preflight.md` |
| 更大 HSA 派生包人工复核 | 已完成；`18/22/32/41/52` 通过，`59` 暂缓，见 `docs/hsa_larger_derived_candidate_review.md` |
| 更大 HSA 派生包草稿构造 | 暂停；对外报告主线先补公开基准主表 |
| strict 到 `9/9` 但 extra final cards 接近 all-scoped | 只保留诊断，不写方法优势 |
| perturb rows 大量 forced commitment | 暂停扩跑，改 insufficient-evidence contract |

## 运行前 gate

真跑前必须确认：

| 检查项 | 要求 |
| --- | --- |
| 模型调用路径 | A800_2 包装脚本或通用模型服务地址已确认可访问 |
| model name | `-Model` 与服务端 served model name 一致 |
| API key | 无真实 key 需求时用 `EMPTY`；需要 key 时设 `OPENAI_API_KEY` |
| dry-run | 命令队列完整打印 runner、compiler、scorer |
| output dir | `experiments/<run-id>/` 采用唯一 run id |
| prompt leak | launch gate 已通过 evaluator-only field exact leak check |
| paired artifacts | `structured_no_compiler` 和 `compiled` 两路都必须存在 |
| paired delta | `paired_delta_limit<N>.md` 自动生成 |

## 跑完后必须更新

| 产物 | 更新位置 |
| --- | --- |
| run record | `experiments/<run-id>/README.md` |
| 解释报告 | `reports/<date>-<topic>.md` |
| PG40 数字表 | `docs/pg40_tight_budget_numeric_main_table.md` 和 CSV |
| HSA 数字表 | `docs/hsa_v0_numeric_main_table.md` 和 CSV |
| 总索引 | `docs/owned_results_table_index.md` |
| 论文骨架 | `docs/sseac_paper_skeleton_v0.md` |

## 当前结论

下一步转到对外报告主线：PG40 / PerspectiveGap 公开切片优先。HSA-v0 三十六行真跑已经足够支持机制解释，继续扩 HSA 对证明方法有效性的帮助有限。PG40 role-plan 已退休，scope projection 已证明 role-card 投影是关键诊断变量；规则式 no-scope selector 已负；pairwise selector 五行真跑也已负。当前不扩 pairwise full40，先修 role/recipient interface，或回到 PerspectiveGap official role-assignment arms。

公开主表必须同时放 direct、source-ledger、structured no compiler、compiled、transparent greedy 和 oracle。HSA 主表保留为机制分析表，用来解释来源、范围、验证、证据不足和支撑型窄补全。
