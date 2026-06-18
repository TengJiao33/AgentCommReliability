# HiddenBench 通信必要性外部压力结果

## 核心判断

HiddenBench 是目前更合适的外部压力对象。它天然把信息拆成 shared information 和 hidden information，单个 agent 在 shared-only 或单条私有信息下很难完成任务；当所有私有事实被干净公开后，Qwen2.5-14B 的准确率大幅上升。

这次 full 65 结果给出明确方向：benchmark 本身有通信必要性，朴素生成式 exchange 远没有把私有信息可靠转成可用公共状态。下一步应围绕“私有事实如何被公开、校验、压缩、禁止被推荐语污染”做协议，而不再继续扩展 MATH peer-influence 变体。

## 实验设计

外部数据来自 HiddenBench：

- dataset: `data/external/hiddenbench/benchmark.json`
- source: `https://huggingface.co/datasets/YuxuanLi1225/HiddenBench`
- paper: `https://arxiv.org/abs/2505.11556`

本次 runner 使用项目内协议，未使用官方交互 harness。每个任务构造五类条件：

- `shared_only`: 只给 shared information。
- `single_private_agent`: 每个 agent 只拿一条 hidden information，独立作答。
- `oracle_public_facts`: 把所有 hidden facts 作为干净公共消息给最终决策者。
- `full_info`: 直接给最终决策者 shared + all hidden information。
- `exchange_then_decide`: 每个局部 agent 先生成 public message，最终决策者只看 shared information + public messages。

运行配置：

- remote: `A800_2`
- model: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- served name: `qwen2.5-14b-hiddenbench`
- temperature: `0`
- max tokens: `180`
- run id: `20260617-20260617-102311-a8002-hiddenbench-full65-answerfirst-qwen25-14b`
- local run dir: `experiments/20260617-20260617-102311-a8002-hiddenbench-full65-answerfirst-qwen25-14b/`
- corrected analysis: `experiments/20260617-20260617-102311-a8002-hiddenbench-full65-answerfirst-qwen25-14b/analysis_corrected/`

## 结果

corrected summary 只修正了一条 parser case：task 62 输出 `Answer: Option C`，对应选项 `Option C: Logistics software company`。修正后无 exchange unparsed。

| Condition | Records | Correct | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| `shared_only` | 65 | 1 | 0.015 | 0 |
| `single_private_agent` | 253 | 62 | 0.245 | 1 |
| `single_private_task_majority` | 65 | 16 | 0.246 | 0 |
| `single_private_task_any` | 65 | 37 | 0.569 | 0 |
| `exchange_then_decide` | 65 | 24 | 0.369 | 0 |
| `oracle_public_facts` | 65 | 56 | 0.862 | 0 |
| `full_info` | 65 | 59 | 0.908 | 0 |

paired contrasts：

- `full_info` 正确而 `shared_only` 错：59/65。
- `oracle_public_facts` 正确而 `shared_only` 错：56/65。
- `oracle_public_facts` 正确而 `exchange_then_decide` 错：33/65。
- `full_info` 正确而 `exchange_then_decide` 错：35/65。
- `exchange_then_decide` 正确而 `shared_only` 错：24/65。
- `exchange_then_decide` 正确而 `oracle_public_facts` 错：1/65。

## 解释

第一层信号很强：`shared_only` 只有 1/65，`full_info` 到 59/65，`oracle_public_facts` 到 56/65。这个 gap 说明任务确实依赖 hidden information，单 agent 拿 shared context 基本无法完成。

第二层信号更关键：干净公共事实能达到 56/65，但生成式 exchange 只有 24/65。也就是说，失败点主要在通信表面；最终模型在 clean fact 条件下有能力整合事实。当前 public message 常把私有事实和推荐语混在一起，最终决策者会被显眼但已被否定的选项吸走。

第三层信号说明单个局部 agent 也不够。`single_private_task_any` 有 37/65，表示不少任务里至少一个局部 agent 能猜到或看到关键线索；但 majority 只有 16/65，说明靠局部 agent 投票会严重失真。通信协议需要保留每条 hidden fact 的 provenance、否决关系和适用范围。

## 典型失败

Task 10 `emergency_supply_drop`：gold 是 `Warehouse C`。Agent 4 明确报告 Warehouse B 有 noxious gas risk，但其他 public messages 大量重复 Warehouse B 的道路优势和响应中心优势，最终 exchange 仍选 `Warehouse B`。

Task 11 `emergency_conference_relocation`：gold 是 `School Gym`。Agent 1 报告 City Library generator 只能撑 2 小时且无法加油，Agent 2 报告 School Gym restroom 会在一小时内恢复；最终 exchange 仍选 `City Library`，说明负面约束和修复性事实都没有稳定进入最终决策。

Task 12 `evacuate_park_dilemma`：gold 是 `Green Valley`。Agent 2 报告 Red Lake road closed，Agent 1 报告 Green Valley pest closure 只影响 tourists；最终 exchange 仍选 `Red Lake`。这类错误非常贴近我们要研究的 field authority：事实出现了，但消息的可用性和最终承诺没有被正确约束。

## 边界

这次是项目内协议，不等同于 HiddenBench 官方 group-interaction harness。它足以作为外部压力 preflight 和协议诊断，暂时还不能声明官方 benchmark SOTA 或完整多 agent 复现。

TeamBench 仍然是更强的工程隔离目标，但当前 A800_2 没有 Docker、Podman、Singularity、Apptainer，也没有免密 sudo；严格 OS-level role separation 需要管理员介入。当前可执行路线先用 HiddenBench 建立通信必要性和协议失败面。

## 下一步

优先做一个 HiddenBench protocol v2，暂停继续跑 MATH：

1. `fact_only_exchange`: agent public message 只能输出私有事实，不允许推荐答案。
2. `typed_fact_card`: 每条 fact 带 `source_agent`, `option_affected`, `polarity`, `scope`, `confidence`, `verbatim_fact`。
3. `constraint_merge`: 最终决策前先合并每个 option 的 blocking facts 和 enabling facts。
4. `admission_check`: 最终答案只能引用已经进入 typed fact card 的事实。

判断标准很直接：如果 v2 能把 `exchange_then_decide` 从 24/65 拉近 `oracle_public_facts` 的 56/65，同时保持 shared-only floor 不变，这才是有说服力的通信协议结果。
