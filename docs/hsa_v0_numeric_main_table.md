# HSA-v0 数字主表

Snapshot date: `2026-06-19`.

机器可筛选版本见 `docs/hsa_v0_numeric_rows.csv`。

## 核心判断

`HSA-v0` 是 HiddenBench 信号进入 SSEAC / State Admission 主线的桥。它当前已经有 packet、compiler、scorer、transparent controls、A800_2 runner、四条 Qwen2.5-14B 完整 9 行模型诊断结果、一条本地后置补全诊断结果、15 行扩展包和真跑结果、33 行 P0/P1 远程真跑结果，以及一条纳入 P2 长档案种子的 36 行远程真跑结果。

透明条件说明这张小表能测两个关键点：一是通信必要性，`shared_only_verified` 在 9 行 base rows 上是 `0/3`，在 15 行 base rows 上是 `0/5`，在 33 行 base rows 上是 `0/11`，在 36 行 base rows 上是 `0/12`；二是过度准入风险，`all_scoped_verified` 在 36 行上 strict 是 `36/36`，但 extra final cards 是 `195`。三十六行真跑显示硬准入能把模型直出的 `16/36` 推到 `34/36`，阻断补全后到 `35/36`，支撑型窄补全后到 `36/36`，extra final cards 是 `42`。

## 主数字表

| Family | Condition | Rows | Strict | Base strict | Perturb strict | Slot recall | Extra final cards | Forced commitment | 角色 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| oracle | oracle_admissible_facts | 9 | 9/9 | 1.0000 | 1.0000 | 0.8333 | 0 | 0.0000 | 上界 |
| lower bound | shared_only_verified | 9 | 6/9 | 0.0000 | 1.0000 | 0.1759 | 24 | 0.3333 | 通信必要性下界 |
| over-admission | all_scoped_verified | 9 | 9/9 | 1.0000 | 1.0000 | 0.8333 | 24 | 0.0000 | 过度准入对照 |
| model | structured_model_only_qwen25_14b_full9 | 9 | 3/9 | 0.6667 | 0.1667 | 0.8148 | 8 | 0.5556 | 模型直出对照 |
| model | sseac_qwen25_14b_compiler_full9 | 9 | 7/9 | 0.3333 | 1.0000 | 0.7130 | 8 | 0.7778 | 诊断模型行 |
| model | recall_sweep_model_only_qwen25_14b_full9 | 9 | 5/9 | 0.6667 | 0.5000 | 0.9259 | 19 | 0.0000 | 召回增强对照 |
| model | recall_sweep_sseac_qwen25_14b_compiler_full9 | 9 | 8/9 | 0.6667 | 1.0000 | 0.7963 | 19 | 0.3333 | 召回增强诊断行 |
| model | focused_recall_model_only_qwen25_14b_full9 | 9 | 5/9 | 1.0000 | 0.3333 | 0.9167 | 12 | 0.2222 | focused model-only |
| model | focused_recall_sseac_qwen25_14b_compiler_full9 | 9 | 8/9 | 0.6667 | 1.0000 | 0.8148 | 12 | 0.5556 | focused 诊断行 |
| model | constraint_recall_model_only_qwen25_14b_full9 | 9 | 5/9 | 1.0000 | 0.3333 | 0.8981 | 10 | 0.2222 | constraint model-only |
| model | constraint_recall_sseac_qwen25_14b_compiler_full9 | 9 | 8/9 | 0.6667 | 1.0000 | 0.7963 | 10 | 0.5556 | 当前最强纯提示诊断行 |
| postfilter | constraint_completion_model_only_full9 | 9 | 5/9 | 1.0000 | 0.3333 | 0.9352 | 10 | 0.1111 | 后置补全 model-only |
| postfilter | constraint_completion_sseac_compiler_full9 | 9 | 9/9 | 1.0000 | 1.0000 | 0.8333 | 10 | 0.4444 | 当前最强 HSA 诊断行 |
| oracle | oracle_admissible_facts_extended15 | 15 | 15/15 | 1.0000 | 1.0000 | 0.8400 | 0 | 0.0000 | 15 行上界 |
| lower bound | shared_only_verified_extended15 | 15 | 10/15 | 0.0000 | 1.0000 | 0.1956 | 39 | 0.3333 | 15 行通信必要性下界 |
| over-admission | all_scoped_verified_extended15 | 15 | 15/15 | 1.0000 | 1.0000 | 0.8400 | 39 | 0.0000 | 15 行过度准入对照 |
| model | constraint_recall_model_only_qwen25_14b_extended15 | 15 | 7/15 | 1.0000 | 0.2000 | 0.9389 | 13 | 0.1333 | 15 行模型直出 |
| model | constraint_recall_sseac_qwen25_14b_compiler_extended15 | 15 | 14/15 | 0.8000 | 1.0000 | 0.8178 | 10 | 0.6000 | 15 行硬准入模型行 |
| postfilter | constraint_completion_model_only_qwen25_14b_extended15 | 15 | 7/15 | 1.0000 | 0.2000 | 0.9611 | 13 | 0.0667 | 15 行补全 model-only |
| postfilter | constraint_completion_sseac_qwen25_14b_compiler_extended15 | 15 | 15/15 | 1.0000 | 1.0000 | 0.8400 | 10 | 0.5333 | 15 行最强模型链路 |
| oracle | oracle_admissible_facts_p0p1_33 | 33 | 33/33 | 1.0000 | 1.0000 | 0.8394 | 0 | 0.0000 | 33 行上界 |
| lower bound | shared_only_verified_p0p1_33 | 33 | 22/33 | 0.0000 | 1.0000 | 0.0818 | 111 | 0.3333 | 33 行通信必要性下界 |
| over-admission | all_scoped_verified_p0p1_33 | 33 | 33/33 | 1.0000 | 1.0000 | 0.8394 | 111 | 0.0000 | 33 行过度准入对照 |
| model | constraint_recall_model_only_qwen25_14b_p0p1_33 | 33 | 15/33 | 0.9091 | 0.2273 | 0.9591 | 40 | 0.0909 | 33 行模型直出 |
| model | constraint_recall_sseac_qwen25_14b_compiler_p0p1_33 | 33 | 32/33 | 0.9091 | 1.0000 | 0.8273 | 37 | 0.5455 | 33 行硬准入模型行 |
| postfilter | constraint_completion_model_only_qwen25_14b_p0p1_33 | 33 | 15/33 | 0.9091 | 0.2273 | 0.9712 | 40 | 0.0606 | 33 行补全 model-only |
| postfilter | constraint_completion_sseac_qwen25_14b_compiler_p0p1_33 | 33 | 33/33 | 1.0000 | 1.0000 | 0.8394 | 37 | 0.5152 | 33 行最强模型链路 |
| oracle | oracle_admissible_facts_p0p1p2_36 | 36 | 36/36 | 1.0000 | 1.0000 | 0.8477 | 0 | 0.0000 | 36 行上界 |
| lower bound | shared_only_verified_p0p1p2_36 | 36 | 24/36 | 0.0000 | 1.0000 | 0.0750 | 129 | 0.3333 | 36 行通信必要性下界 |
| over-admission | all_scoped_verified_p0p1p2_36 | 36 | 36/36 | 1.0000 | 1.0000 | 0.8477 | 195 | 0.0000 | 36 行过度准入对照 |
| model | constraint_recall_model_only_qwen25_14b_p0p1p2_36 | 36 | 16/36 | 0.9167 | 0.2083 | 0.9271 | 43 | 0.1667 | 36 行模型直出 |
| model | constraint_recall_sseac_qwen25_14b_compiler_p0p1p2_36 | 36 | 34/36 | 0.8333 | 1.0000 | 0.8038 | 40 | 0.5833 | 36 行硬准入模型行 |
| postfilter | constraint_completion_model_only_qwen25_14b_p0p1p2_36 | 36 | 16/36 | 0.9167 | 0.2083 | 0.9458 | 43 | 0.1389 | 36 行补全 model-only |
| postfilter | constraint_completion_sseac_qwen25_14b_compiler_p0p1p2_36 | 36 | 35/36 | 0.9167 | 1.0000 | 0.8225 | 40 | 0.5556 | 36 行阻断补全链路 |
| postfilter | constraint_support_completion_model_only_qwen25_14b_p0p1p2_36 | 36 | 16/36 | 0.9167 | 0.2083 | 0.9711 | 45 | 0.0833 | 36 行支撑补全 model-only |
| postfilter | constraint_support_completion_sseac_qwen25_14b_compiler_p0p1p2_36 | 36 | 36/36 | 1.0000 | 1.0000 | 0.8477 | 42 | 0.5278 | 当前最强 HSA 模型链路 |

## 怎么读

第一，oracle 行闭合。`oracle_admissible_facts` 是 `9/9`，说明 HSA-v0 packet、SSEAC compiler 和 scorer 可以共同工作。base rows 能由 admissible facts 支持答案；perturbation rows 能落到 `insufficient_evidence`。

第二，shared-only 行证明 base rows 需要通信。`shared_only_verified` 的 base strict 是 `0/3`，slot recall 只有 `0.1759`。它在 perturbation rows 上是 `6/6`，因为这些行的目标是证据不足。

第三，all-scoped 行暴露了评价风险。`all_scoped_verified` 的 strict 是 `9/9`，slot recall 和 oracle 一样是 `0.8333`，但 extra final cards 是 `24`。这意味着只看最终 strict 会奖励“全塞进去”的策略；主表必须把 evidence discipline 放到 strict 旁边。

第四，模型行显示硬准入的收益集中在扰动行。`sseac_qwen25_14b_compiler_full9` 的 perturb strict 是 `1.0000`，而 `structured_model_only_qwen25_14b_full9` 是 `0.1667`。这说明硬准入规则能挡住范围越界、隔离证据和未验证证据导致的错误承诺。

第五，baseline 模型行暴露了候选证据召回瓶颈。硬准入的 base strict 是 `0.3333`，低于模型直出的 `0.6667`。两个失败 base 行中，模型答案本身正确，但少提了必需证据卡片；compiler 因充分性不满足退回 `insufficient_evidence`。

第六，`recall_sweep` 说明召回瓶颈可以被提示契约部分修复。compiler strict 到 `8/9`，base strict 到 `0.6667`，perturbation strict 保持 `1.0000`。但 extra final cards 到 `19`，明显高于 baseline 的 `8`，已经接近 all-scoped 的 `24`。

第七，`focused_recall` 和 `constraint_recall` 说明过度准入可以被压低。两者都保持 compiler `8/9`，其中 `constraint_recall` 把 extra final cards 降到 `10`。唯一未解的问题是 `hiddenbench_evacuation_west_city` base 仍漏 `hb01_hidden_2`。本地 `constraint_completion` 只补预测时可见、已验证、面向最终决策者的阻断卡，补上这张卡后 compiler 到 `9/9`，extra final cards 保持 `10`。

第八，`constraint_completion` 仍然只是诊断行。它复用了 `constraint_recall` 的模型输出，没有新增模型生成；它说明补全器能修当前小表漏卡，下一步必须扩到 HiddenBench seed shortlist 检查规则精度。

第九，15 行扩展包已经通过透明控制门禁。理想准入是 `15/15`；只给共享信息时基础行是 `0/5`；全范围信息也是 `15/15`，但 extra final cards 到 `39`。这让下一次模型真跑有清楚边界：高严格正确必须同时伴随较低多余卡片，才算机制信号。

第十，15 行真跑给出十五行最强模型链路。模型直出 `7/15`，硬准入 `14/15`，补全后硬准入 `15/15`。关键点是扰动行：模型直出只有 `2/10`，硬准入后是 `10/10`。补全新增两个 `hb01_hidden_2` 单元，修掉唯一基础行漏卡，extra final cards 没有从 `10` 上升。

第十一，强制作答仍是活风险。补全后硬准入的 forced commitment rate 是 `0.5333`，说明模型本体仍倾向在证据不足时给具体答案；当前成绩主要来自准入规则把错误承诺挡回去。

第十二，33 行扩展把十五行信号推到更高压力。透明控制显示 shared-only 基础行是 `0/11`，all-scoped 是 `33/33` 但 extra final cards 是 `111`。模型直出是 `15/33`，硬准入是 `32/33`，补全后硬准入是 `33/33`，extra final cards 是 `37`。这说明硬准入仍主要修扰动行错误承诺，同时没有靠全范围收证据拿分。

第十三，33 行补全只新增两个 `hb03_hidden_2` 单元。真正改变最终正确性的行是 `hiddenbench_evacuation_east_town__hb03_base_verified_role_scoped__hsa_v0`；另一个扰动行只提高召回，最终仍保持 `insufficient_evidence`。这让补全器目前更像窄修复规则，也解释了为什么需要再用长档案任务压支撑卡召回。

第十四，36 行扩展纳入了 P2 长档案种子。透明控制显示 shared-only 基础行是 `0/12`，all-scoped 是 `36/36` 但 extra final cards 是 `195`。模型直出是 `16/36`，硬准入是 `34/36`，阻断补全后硬准入是 `35/36`，支撑型窄补全后硬准入是 `36/36`。扰动行在硬准入和两种补全后都保持 `24/24`，说明来源、验证和最终决策者范围规则仍然稳。

第十五，36 行阻断补全后的唯一剩余失败来自 `baker_2010` 基础行。补全后仍缺 Roberts 的 `collaborative`、`diversity`、`excellent_teacher`、`federal_grant`、`research_productivity` 五张正向支撑卡。这说明长档案压力主要落在支持型证据召回。

第十六，支撑型窄补全能修掉这个缺口。该规则只在模型已经给出具体最终答案时，补可见、已验证、面向最终决策者、且与模型答案匹配的支撑卡。它把补全后硬准入从 `35/36` 推到 `36/36`，extra final cards 从 `40` 到 `42`，仍远低于 all-scoped 的 `195`。这个结果目前是诊断后处理行，需要在后续报告中和纯模型生成区分开。

第十七，旧包重放暂时没有发现过度补卡。支撑型窄补全在 33 行包上保持 `33/33`、extra final cards `37`，在 15 行包上保持 `15/15`、extra final cards `10`。新增支撑卡主要集中在 task 5 的 Roberts 档案行。

## Runner Preflight

| 项 | 结果 |
| --- | --- |
| runner | `scripts/run_hsa_v0_sseac_openai_compatible.py` |
| packet | `experiments/20260618-local-hsa-v0-sseac-adapter/hsa_v0_packet.jsonl` |
| dry-run rows | `9` |
| prompt length | `5499` 到 `5994` 字符，平均 `5691.56` |
| source cards | 每行 `7` 到 `8`，平均 `7.67` |
| evaluator-only fields leak check | 未命中 `required_slots`、`acceptable_card_ids`、`slot_id`、`expected_final_decision`、`gold_answer`、`oracle_unit_ids`、`downstream_scoring_obligations` |

## 证据路径

| 证据 | 路径 |
| --- | --- |
| adapter smoke report | `reports/20260618-hsa-v0-sseac-adapter.md` |
| runner preflight report | `reports/20260618-hsa-v0-sseac-runner-preflight.md` |
| packet and transparent predictions | `experiments/20260618-local-hsa-v0-sseac-adapter/` |
| dry-run prompts | `experiments/20260618-local-hsa-v0-sseac-runner-preflight/dry_run_prompts_full9.jsonl` |
| limit3 launch gate | `reports/20260618-hsa-v0-sseac-launch-gate.md`; `experiments/20260618-local-hsa-v0-sseac-launch-gate/README.md` |
| full9 model run | `reports/20260619-hsa-v0-full9-a8002.md`; `experiments/20260619-a8002-hsa-v0-sseac-full9-qwen25-14b/README.md` |
| recall_sweep full9 model run | `reports/20260619-hsa-v0-recall-sweep-full9-a8002.md`; `experiments/20260619-a8002-hsa-v0-recall-sweep-full9-qwen25-14b/README.md` |
| focused / constraint full9 runs | `reports/20260619-hsa-v0-focused-constraint-full9-a8002.md`; `experiments/20260619-a8002-hsa-v0-focused-recall-full9-qwen25-14b/README.md`; `experiments/20260619-a8002-hsa-v0-constraint-recall-full9-qwen25-14b/README.md` |
| constraint completion postfilter | `reports/20260619-hsa-v0-constraint-completion-postfilter.md`; `experiments/20260619-local-hsa-v0-constraint-completion-postfilter/README.md` |
| extended15 transparent gate | `reports/20260619-hsa-v0-extended15-packet-gate.md`; `experiments/20260619-local-hsa-v0-extended15-packet/README.md` |
| extended15 model run | `reports/20260619-hsa-v0-constraint-recall-extended15-a8002.md`; `experiments/20260619-a8002-hsa-v0-constraint-recall-extended15-qwen25-14b/README.md` |
| P0/P1 33-row transparent gate | `reports/20260619-hsa-v0-p0p1-seed-expansion33-gate.md`; `experiments/20260619-local-hsa-v0-p0p1-seed-expansion33-draft/README.md` |
| P0/P1 33-row model run | `reports/20260619-hsa-v0-constraint-recall-p0p1-33-a8002.md`; `experiments/20260619-a8002-hsa-v0-constraint-recall-p0p1-33-qwen25-14b/README.md` |
| P0/P1/P2 36-row transparent gate | `experiments/20260619-local-hsa-v0-p0p1p2-seed-expansion36-draft/README.md` |
| P0/P1/P2 36-row model run | `reports/20260619-hsa-v0-constraint-recall-p0p1p2-36-a8002.md`; `experiments/20260619-a8002-hsa-v0-constraint-recall-p0p1p2-36-qwen25-14b/README.md` |
| builder / scorer / runner | `scripts/build_hsa_v0_sseac_packet.py`; `scripts/score_hsa_v0_compiled.py`; `scripts/run_hsa_v0_sseac_openai_compatible.py` |

## 论文表位置

| 放置位置 | 内容 |
| --- | --- |
| Main table candidate | shared-only、oracle-admissible、all-scoped、SSEAC model diagnostic row |
| Metric table | answer strict、base strict、perturb strict、slot recall、extra final cards、forced commitment |
| Appendix | prompt leak check、dry-run prompt stats、seed shortlist provenance |

## 下一步压力

1. `Profile support recall`：把支撑型窄补全从本地诊断整理成明确方法组件，写清楚字段可见性和禁区。
2. `Same-readout discipline`：继续同时报告模型直出、硬准入、补全后硬准入、共享信息下界和全范围信息对照。
3. `Success signal`：36 行支撑补全保持 `36/36`，extra final cards 仍明显低于 `195`；perturbation rows 继续维持 insufficient-evidence。
4. `Main-table gate`：把 HSA 写成主表候选，并决定是否进入更大基准评测。

这张表的意义是把 HiddenBench 的“fact-state discipline”变成可评分的 admission packet。它已经给出诊断模型信号：硬准入在防错上有效，候选证据召回可以改善，过度准入也能被压低；剩余瓶颈是间接约束卡的稳定补全。
